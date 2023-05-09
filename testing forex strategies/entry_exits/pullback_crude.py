"""
Date           : 2023-05-04
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video:
https://www.youtube.com/watch?v=bdi6zQ7g-r4


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

    strategy_name = "pullback-crude"

    # Read in the data
    ohlc_subset  = read_data()

    # Calculate the shift periods
    ohlc_subset.loc[:,"Close_200"] = ohlc_subset.loc[:,"Close"].shift(200)
    ohlc_subset.loc[:,"Close_20"] = ohlc_subset.loc[:,"Close"].shift(20)
    ohlc_subset.loc[:,"Close_10"] = ohlc_subset.loc[:,"Close"].shift(10)

    # Signal position points (i.e. for plotting)
    buy_conditions = (ohlc_subset["Close"] >  ohlc_subset["Open"]) & (ohlc_subset["Close"] < ohlc_subset["Close_200"]) & \
                     (ohlc_subset["Close"] > ohlc_subset["Close_20"]) & (ohlc_subset["Close"] < ohlc_subset["Close_10"])

    sell_conditions = (ohlc_subset["Close"] <  ohlc_subset["Open"]) & (ohlc_subset["Close"] > ohlc_subset["Close_200"]) & \
                     (ohlc_subset["Close"] < ohlc_subset["Close_20"]) & (ohlc_subset["Close"] > ohlc_subset["Close_10"])

    ohlc_subset.loc[:,"buy_position"] = np.where(buy_conditions, ohlc_subset["High"],np.nan)

    ohlc_subset.loc[:,"sell_position"] = np.where(sell_conditions, ohlc_subset["Low"],np.nan)

    # Signal Points
    ohlc_subset.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc_subset.loc[:,"sell"] = np.where(sell_conditions,1,0)  

    if show_plot:
        plot_ohlc(ohlc_subset, filename=strategy_name)

    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc_subset, SimpleStrategy, strategy_name=strategy_name) 



if __name__ == "__main__":
    main()