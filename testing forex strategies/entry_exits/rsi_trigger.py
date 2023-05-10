"""
Date           : 2023-05-10
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following book: https://www.amazon.com/Entry-Exit-Confessions-Champion-Trader/dp/1095328557


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

    strategy_name = "rsi-trigger"

    # Read in the data
    ohlc  = read_data()

    # Calculate the RSI 
    ohlc["rsi"] = ta.rsi(ohlc.Close, length=5)

    # Calculate the Average Close
    rolling_period = 5
    ohlc["avg_close"] = ohlc["Close"].rolling(window=rolling_period).mean()


    # Buy and Sell conditions
    buy_conditions   = (ohlc["rsi"] < 80) & (ohlc["avg_close"] < ohlc["Close"])
    sell_conditions  = (ohlc["rsi"] > 20) & (ohlc["avg_close"] > ohlc["Close"])

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