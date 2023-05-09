"""
Date           : 2023-04-22
Author         : Zetra Team 
YouTube Channel: https://www.youtube.com/@zetratrading/featured

This is a script that implements a strategy for the 20pips challenge. 
The challenge is a way to grow your small Forex account.

Here is the source of the strategy from the CodeTrading YouTube Channel: https://www.youtube.com/watch?v=ybmep_u5MeU

Here is the link to the Youtube video about growing your small account:

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

    strategy_name = "ema-scalping"
    # Read in the data
    ohlc  = read_data()

    # Calculate the EMAs 
    ohlc["ema50"]   = ta.ema(ohlc.Close, length=50)
    ohlc["ema100"]  = ta.ema(ohlc.Close, length=100)
    ohlc["ema150"]  = ta.ema(ohlc.Close, length=150)


    # Calculate the slopes of the EMAs 
    rolling_period = 10

    ohlc["slope_ema50"] = ohlc["ema50"].diff(periods=1)
    ohlc["slope_ema100"] = ohlc["ema100"].diff(periods=1)
    ohlc["slope_ema150"] = ohlc["ema150"].diff(periods=1)

    ohlc["slope_ema50"] = ohlc["slope_ema50"].rolling(window=rolling_period).mean()
    ohlc["slope_ema100"] = ohlc["slope_ema100"].rolling(window=rolling_period).mean()
    ohlc["slope_ema150"] = ohlc["slope_ema150"].rolling(window=rolling_period).mean()


    # Set the wick limit 
    wick_limit = 2e-5 

    # Generate the ema signal
    conditions = [
        ( (ohlc['ema50']<ohlc['ema100']) & (ohlc['ema100']<ohlc['ema150']) & (ohlc['slope_ema50']<0) & (ohlc['slope_ema100']<0) & (ohlc['slope_ema150']<0)),
        ( (ohlc['ema50']>ohlc['ema100']) & (ohlc['ema100']>ohlc['ema150']) & (ohlc['slope_ema50']>0) & (ohlc['slope_ema100']>0) & (ohlc['slope_ema150']>0))
            ]
    choices = [1, 2]
    ohlc['ema_signal'] = np.select(conditions, choices, default=0)

    # Buy and sell conditions
    sell_conditions = (ohlc.ema_signal==1) & (ohlc.Open > ohlc.ema50) & (ohlc.Close <ohlc.ema50) & ( (ohlc.High-ohlc.Open)<=wick_limit)
    buy_conditions  = (ohlc.ema_signal==2) & (ohlc.Open < ohlc.ema50) & (ohlc.Close > ohlc.ema50) & ( (ohlc.Open-ohlc.Low)<=wick_limit)

    # Signal Points for plotting
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