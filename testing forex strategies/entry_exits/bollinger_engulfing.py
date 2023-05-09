"""
Date           : 2023-05-07
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video: https://www.youtube.com/watch?v=LNQUvN7_NUQ

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
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest



def main(show_plot=True):
    """
    This is the main function to run the analysis
    """

    strategy_name = "bollinger-engulfing"
    # Read in the data
    ohlc = read_data()

    # Calculate the bollinger bands
    bb = ta.bbands(ohlc.Close, length=30, std=1.5)
    ohlc["BBL_30_1_5"] = bb["BBL_30_1.5"]
    ohlc["BBU_30_1_5"] = bb["BBU_30_1.5"]

    ohlc["L_BBL_30_1_5"] = bb["BBL_30_1.5"].shift(1)
    ohlc["L_BBU_30_1_5"] = bb["BBU_30_1.5"].shift(1)

    
    # Lag the Open and Close 
    ohlc["Close_1"]   = ohlc["Close"].shift(1)
    ohlc["Close_2"]   = ohlc["Close"].shift(2)
    ohlc["Close_3"]   = ohlc["Close"].shift(3)

    ohlc["Open_1"]   = ohlc["Open"].shift(1)
    ohlc["Open_2"]   = ohlc["Open"].shift(2)
    ohlc["Open_3"]   = ohlc["Open"].shift(3)

    # Buy and sell conditions
    buy_conditions = (ohlc["Close"] < ohlc["BBL_30_1_5"]) & (ohlc["Close"] > ohlc["Open"]) & \
                     (ohlc["Close_1"] < ohlc["Open_1"]) & (ohlc["Open"] < ohlc["Close_1"]) & \
                     (ohlc["Close"] > ohlc["Open_1"])

    sell_conditions = (ohlc["Close"] > ohlc["BBL_30_1_5"]) & (ohlc["Close"] < ohlc["Open"]) & \
                      (ohlc["Close_1"] > ohlc["Open_1"]) & (ohlc["Open"] > ohlc["Close_1"]) & (ohlc["Close"] < ohlc["Open_1"])

    ohlc.loc[:,"buy_position"] = np.where(buy_conditions, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(sell_conditions, ohlc["Low"],np.nan)

    # Signal Points
    ohlc.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc.loc[:,"sell"] = np.where(sell_conditions,1,0)  


    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name)    


    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name) 

if __name__ == "__main__":
    main()