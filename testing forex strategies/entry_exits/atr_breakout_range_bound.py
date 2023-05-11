"""
Date           : 2023-05-10
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
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest





def main(show_plot=True):
    """
    This is the main function to run the analysis
    """

    strategy_name = "atr-breakout-range-bound"

    # Read in the data
    ohlc  = read_data()

    # ATR 
    ohlc['atr'] = ohlc.ta.atr(length=14)

    # Upper and lower atr 
    ohlc["upper_band"] = ohlc["Close"] + ohlc["atr"]
    ohlc["lower_band"] = ohlc["Close"] - ohlc["atr"]

    # Calculate the patterns
    patterns  = ohlc.ta.cdl_pattern(name=["engulfing","harami","dragonflydoji","invertedhammer","morningstar"])

    # Buy and Sell conditions
    buy_conditions   = (ohlc["High"] > ohlc["upper_band"]) & ((patterns["CDL_ENGULFING"]==100) | (patterns["CDL_HARAMI"]==100) )
    sell_conditions  = (ohlc["Low"] < ohlc["lower_band"]) & ((patterns["CDL_ENGULFING"]==-100) | (patterns["CDL_HARAMI"]==-100) )

    ohlc.loc[:,"buy_position"]  = np.where(buy_conditions, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(sell_conditions, ohlc["Low"],np.nan)


    # Signal Points 
    ohlc.loc[:,"buy"]  = np.where(buy_conditions,1,0)
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
