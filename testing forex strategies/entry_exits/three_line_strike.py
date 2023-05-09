"""
Date           : 2023-05-04
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video: https://www.youtube.com/@TheMovingAverage

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

    strategy_name = "three-line-strike"

    # Read in the data
    ohlc = read_data()


    # Calculate the engulfing candles 
    ohlc["engulf"] = ohlc.ta.cdl_pattern(name="engulfing")
    
    # Calculate ATR 
    ohlc["atr"] = ohlc.ta.atr()

    # Calculate OHLC lags
    high_t   = ohlc["High"]             # high(t)
    high_t_1 = ohlc["High"].shift(1)    # high(t-1)
    high_t_2 = ohlc["High"].shift(2)    # high(t-2)
    high_t_3 = ohlc["High"].shift(3)    # high(t-3)

    low_t    = ohlc["Low"]              # low(t)
    low_t_1  = ohlc["Low"].shift(1)     # low(t-1)
    low_t_2  = ohlc["Low"].shift(2)     # low(t-2)   
    low_t_3  = ohlc["Low"].shift(3)     # low(t-3)

  
    close_t_1  = ohlc["Close"].shift(1)     # close(t-1)
    close_t_2  = ohlc["Close"].shift(2)     # close(t-2)   
    close_t_3  = ohlc["Close"].shift(3)     # close(t-3)

    open_t_1  = ohlc["Open"].shift(1)     # open(t-1)
    open_t_2  = ohlc["Open"].shift(2)     # open(t-2)   
    open_t_3  = ohlc["Open"].shift(3)     # open(t-3)


    # Generate signal 
    conditions = [
        ( (high_t_1 > high_t_2) & (high_t_2 > high_t_3) & (low_t_1 > low_t_2) & (low_t_2 > low_t_3) & (close_t_1 > open_t_1) & (close_t_2 > open_t_2) & (close_t_3 > open_t_3)  ),
        ( (low_t_1 < low_t_2) & (low_t_2 < low_t_3) & (high_t_1 < high_t_2) & (high_t_2 < high_t_3) & (close_t_1 < open_t_1) & (close_t_2 < open_t_2) & (close_t_3 < open_t_3)  )
            ]
    choices = [1, 2]

    ohlc['hi_lo'] = np.select(conditions, choices, default=0)

    # Buy and sell conditions
    sell_conditions = (ohlc.engulf == -100) & (ohlc['hi_lo'] == 1)
    buy_conditions  = (ohlc.engulf == 100) &  (ohlc['hi_lo'] == 2)


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