"""
Date           : 2023-05-11
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from ChatGPT. See the following for the rules: 
https://zeta-zetra.github.io/docs-forex-strategies-python/

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 
"""

import logging
import numpy as np
import os
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go 


from backtesting import Backtest, Strategy
from progress.bar import Bar
from typing import List 

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest, plot_ohlc_pivots, plot_ohlc_pivots_dm



def main(show_plot=True):
    """
    This is the main function to run the analysis
    """

    strategy_name = "range-bound-4"

    # Read in the data
    ohlc  = read_data()

    # Create a Date column that will be used in the merging
    intra_date    = ohlc.index.strftime('%Y-%m-%d')
    ohlc["MDate"] = intra_date

    # Resample to daily data
    open_daily       = ohlc["Open"].resample("D").first()
    close_daily      = ohlc["Close"].resample("D").last()
    high_daily       = ohlc["High"].resample("D").max()
    low_daily        = ohlc["Low"].resample("D").min()

    daily_index =  ohlc["Open"].resample("D").first().index.strftime('%Y-%m-%d')

    ohlc_daily = pd.DataFrame({
                "Open": open_daily,
                "High": high_daily,
                "Low" : low_daily,
                "Close": close_daily,
                "MDate": daily_index 
    })


    # print(ohlc_daily[ohlc_daily["Open"]==ohlc_daily["Close"]])
    ohlc_daily.loc[ohlc_daily["Open"]== ohlc_daily["Close"],"DM"] = ohlc_daily.loc[ohlc_daily["Open"]==ohlc_daily["Close"],"High"] + ohlc_daily.loc[ohlc_daily["Open"]==ohlc_daily["Close"],"Low"] + 2*ohlc_daily.loc[ohlc_daily["Open"]==ohlc_daily["Close"],"Close"]
    ohlc_daily.loc[ohlc_daily["Open"] < ohlc_daily["Close"],"DM"] = 2*ohlc_daily.loc[ohlc_daily["Open"] < ohlc_daily["Close"], "High"] + ohlc_daily.loc[ohlc_daily["Open"] < ohlc_daily["Close"], "Low"] + ohlc_daily.loc[ohlc_daily["Open"] < ohlc_daily["Close"], "Close"]
    
    condition_1 = ohlc_daily["Open"] != ohlc_daily["Close"]
    condition_2 = ohlc_daily["Open"] > ohlc_daily["Close"]
    # ohlc_daily["DM"]    = ohlc_daily["DM"].fillna()

    ohlc_daily.loc[ (condition_1) & (condition_2) ,"DM"] = 2*ohlc_daily.loc[ (condition_1) & (condition_2) ,"Low"] + ohlc_daily.loc[ (condition_1) & (condition_2) ,"High"] + ohlc_daily.loc[ (condition_1) & (condition_2) ,"Close"]

    ohlc_daily["PP"] = ohlc_daily["DM"]/4
    ohlc_daily["R1"] = ohlc_daily["DM"]/2 - ohlc_daily["Low"]
    ohlc_daily["S1"] = ohlc_daily["DM"]/2 - ohlc_daily["High"]

    # Shift the Pivot Points
    ohlc_daily["PP"] = ohlc_daily["PP"].shift(1)
    ohlc_daily["R1"] = ohlc_daily["R1"].shift(1)
    ohlc_daily["S1"] = ohlc_daily["S1"].shift(1)


    # Subset and get the Pivot points
    ohlc_daily = ohlc_daily[["MDate", "PP", "S1", "R1"]]

    # Merge the intra day and daily pivot point data
    ohlc_merged = ohlc.merge(ohlc_daily, left_on="MDate", right_on="MDate")
    ohlc_merged.set_index(ohlc.index, inplace=True)
    
    # Drop missing info
    ohlc_merged.dropna(inplace=True)
  
    # Calculate the patterns
    patterns  = ohlc_merged.ta.cdl_pattern(name=["engulfing","harami","dragonflydoji","invertedhammer","morningstar"])

    # Signal conditions
    buy_conditions = (ohlc_merged["Low"] <  ohlc_merged["S1"]) & ((patterns["CDL_ENGULFING"]==100) | (patterns["CDL_HARAMI"]==100))
    sell_conditions = (ohlc_merged["High"] >  ohlc_merged["R1"]) & ((patterns["CDL_ENGULFING"]==-100) | (patterns["CDL_HARAMI"]==-100))


    ohlc_merged.loc[:,"buy_position"]  = np.where(buy_conditions, ohlc_merged["High"],np.nan)
    ohlc_merged.loc[:,"sell_position"] = np.where(sell_conditions, ohlc_merged["Low"],np.nan)


    # Signal Points 
    ohlc_merged.loc[:,"buy"]  = np.where(buy_conditions,1,0)
    ohlc_merged.loc[:,"sell"] = np.where(sell_conditions,1,0) 

    # Plot the ohlc and the pivot points
    plot_ohlc_pivots_dm(ohlc_merged, filename=strategy_name)

    # ===============
    # Run backtest 
    #================
    run_backtest(ohlc_merged, SimpleStrategy, strategy_name=strategy_name)

if __name__ == "__main__":
    main()
