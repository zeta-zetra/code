"""
Date           : 2023-05-04
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video: https://www.youtube.com/watch?v=MzEX4XumtEE


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

    strategy_name = "rsi-ema-scalping"
    # Read in the data
    ohlc  = read_data()

    # Calculate the EMA
    ohlc["EMA200"] = ta.ema(ohlc.Close, length=200)
    
    # Calculate the RSI 
    ohlc["RSI"] = ta.rsi(ohlc.Close, length=3)

    # Buy and Sell conditions
    buy_conditions   = (ohlc["High"] > ohlc["EMA200"]) & (ohlc["RSI"] < 10)
    sell_conditions  = (ohlc["Low"] < ohlc["EMA200"]) & (ohlc["RSI"] > 90)

    ohlc.loc[:,"buy_position"] = np.where(buy_conditions, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(sell_conditions, ohlc["Low"],np.nan)


    # Signal Points 
    ohlc.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc.loc[:,"sell"] = np.where(sell_conditions,1,0) 


    # Plot 
    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name)    


    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name)


if __name__ == "__main__":
    main()
    
