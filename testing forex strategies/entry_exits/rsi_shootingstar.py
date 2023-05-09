"""
Date           : 2023-05-04
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video: https://www.youtube.com/watch?v=eN4zh3PEH6c&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=44

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

    strategy_name = "rsi-shooting-star"
    # Read in the data
    ohlc = read_data()
    
    # Calculate the RSI
    ohlc["rsi"] = ohlc.ta.rsi()

    # Calculate the shooting star
    ohlc["high_diff"] = ohlc["High"] - ohlc[["Open","Close"]].max(axis=1)
    ohlc["body_diff"] = abs(ohlc["Open"] - ohlc["Close"])
    ohlc["body_diff"] = np.where( ohlc["body_diff"] < 0.002, 0.002, ohlc["body_diff"])
    ohlc["low_diff"]  = ohlc[["Open","Close"]].min(axis=1) - ohlc["Low"] 
    ohlc["ratio_1"]   = ohlc["high_diff"]/ohlc["body_diff"]
    ohlc["ratio_2"]   = ohlc["low_diff"]/ohlc["body_diff"]

    # Buy and sell conditions

    sell_conditions = (ohlc["ratio_1"] > 1.5) & (ohlc["low_diff"] < 0.3*ohlc["high_diff"]) & \
                      (ohlc["body_diff"] > 0.03) & (ohlc["rsi"] > 50) & (ohlc["rsi"] < 70)

    buy_conditions  = (ohlc["ratio_2"] > 1.5) & (ohlc["high_diff"] < 0.23*ohlc["low_diff"]) & \
                      (ohlc["body_diff"] > 0.03) & (ohlc["rsi"] < 55) & (ohlc["rsi"] > 30)


    ohlc.loc[:,"buy_position"] = np.where(buy_conditions, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(sell_conditions, ohlc["Low"],np.nan)

    # Signal Points
    ohlc.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc.loc[:,"sell"] = np.where(sell_conditions,1,0)  


    # if show_plot:
    #     plot_ohlc(ohlc, filename=strategy_name)    


if __name__ == "__main__":
    main()