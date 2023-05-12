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

    strategy_name = "triple-ma-macd"

    # Read in the data
    ohlc  = read_data()

    # Calculate EMAs 
    ohlc["ema50"]   = ta.ema(ohlc.Close, length=50)
    ohlc["ema21"]   = ta.ema(ohlc.Close, length=21)
    ohlc["ema200"]  = ta.ema(ohlc.Close, length=200)


    # Calculate the slopes of the EMAs 
    rolling_period = 10

    ohlc["slope_ema21"] = ohlc["ema21"].diff(periods=1)
    ohlc["slope_ema50"] = ohlc["ema50"].diff(periods=1)
    ohlc["slope_ema200"] = ohlc["ema200"].diff(periods=1)

    ohlc["slope_ema21"] = ohlc["slope_ema21"].rolling(window=rolling_period).mean()
    ohlc["slope_ema50"] = ohlc["slope_ema50"].rolling(window=rolling_period).mean()
    ohlc["slope_ema200"] = ohlc["slope_ema200"].rolling(window=rolling_period).mean()


    # Generate the ema signal
    conditions = [
        ( (ohlc['ema21']<ohlc['ema50']) & (ohlc['ema50']<ohlc['ema200']) & (ohlc['slope_ema21']<0) & (ohlc['slope_ema50']<0) & (ohlc['slope_ema200']<0) ),
        ( (ohlc['ema21']>ohlc['ema50']) & (ohlc['ema50']>ohlc['ema200']) & (ohlc['slope_ema21']>0) & (ohlc['slope_ema50']>0) & (ohlc['slope_ema200']>0) )
            ]
    choices = [1, 2]
    ohlc['ema_signal'] = np.select(conditions, choices, default=0)    


    # Calculate MACD
    macd_  = ohlc.ta.macd()

    ohlc["macd_signal"] = macd_["MACDs_12_26_9"]
    ohlc["macd"]        = macd_["MACD_12_26_9"]

  # Buy and sell conditions
    sell_conditions = (ohlc.ema_signal==1) & (ohlc.macd < ohlc.macd_signal) & (ohlc.macd_signal > 0) & (ohlc.macd > 0)
    buy_conditions  = (ohlc.ema_signal==2) & (ohlc.macd > ohlc.macd_signal) & (ohlc.macd_signal < 0) & (ohlc.macd < 0)

    # Signal Points for plotting
    ohlc.loc[:,"buy_position"] = np.where(buy_conditions, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(sell_conditions, ohlc["Low"],np.nan)

    # Signal Points
    ohlc.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc.loc[:,"sell"] = np.where(sell_conditions,1,0)  

    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name)

    # ================
    # Run backtest 
    # ================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name) 



if __name__ == "__main__":
    main()