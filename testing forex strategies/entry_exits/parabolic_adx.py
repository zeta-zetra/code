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

    strategy_name = "parabolic-adx"

    # Read in the data
    ohlc  = read_data()

    # Calculate the Parabolic SAR
    psar = ohlc.ta.psar()

    ohlc.loc[:,"psar_long"]  = psar.loc[:,"PSARl_0.02_0.2"]
    ohlc.loc[:,"psar_short"] = psar.loc[:,"PSARs_0.02_0.2"]

    # Calculate the ADX
    adx_  = ohlc.ta.adx(high = ohlc["High"], low = ohlc["Low"], close = ohlc["Close"],
                                length=14)

    ohlc.loc[:,"ADX"] = adx_.loc[:,"ADX_14"]


    # Signal position points (i.e. for plotting)
    buy_conditions  = ohlc["High"] >  ohlc["psar_long"]
    sell_conditions = ohlc["Low"] <  ohlc["psar_short"]

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