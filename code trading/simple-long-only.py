"""
Long Only RSI Strategy

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=15

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT
"""

import numpy as np 
import pandas as pd 
import pandas_ta as ta 

from tqdm import tqdm 

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest


def main(show_plot=False):
    """
    """
    
    strategy_name = "simple-long-only"
    
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True) 
    
    # Calculate the indicators
    ohlc['ema'] = ohlc.ta.sma(length=200)
    ohlc["rsi"] = ohlc.ta.rsi(length=2)
    adx         = ohlc.ta.adx()
    ohlc["adx"] = adx["ADX_14"]    
    
    # Find the EMA signal
    backcandles = 6
    pbar   = tqdm(ohlc.rolling(backcandles), desc="Finding EMA signal points...")
    ohlc["ema_signal"] =  [ 1 if (window.High > window.ema).all() else (-1 if (window.Low < window.ema).all() else 0) for window in pbar]       
    
    
    # Find the signal
    first_condition = (ohlc["ema_signal"] == 1) & (ohlc["rsi"] <= 25) & (ohlc["adx"] >= 20)
    ohlc["signal"] = np.where(first_condition, 1, 0)
    
    # Set the index 
    ohlc.set_index("datetime", inplace=True)
    
    print("Setting the buy and sell positions...")
    ohlc.loc[:,"buy_position"] = np.where(ohlc["signal"]==1, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(ohlc["signal"]==2, ohlc["Low"],np.nan)
    
    # Signal Points 
    ohlc.loc[:,"buy"] = np.where(ohlc["signal"]==1,1,0)
    ohlc.loc[:,"sell"] = np.where(ohlc["signal"]==2,1,0)     
    print("Completed setting the buy and sell positions...")
    
    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name) 
        
    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name)     
    
if __name__ == "__main__":
    main()