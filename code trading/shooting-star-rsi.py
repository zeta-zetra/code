"""
Shooting Star strategy

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored

Date: 2023-07-23
Source: https://www.youtube.com/watch?v=eN4zh3PEH6c&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=47

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 
"""

import numpy as np 
import pandas as pd 
import pandas_ta as ta 


# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest



def main(show_plot=False):
    """
    """
    
    strategy_name = "shooting-star-rsi"

    # Read in the data
    ohlc  = read_data()
    
    # Calculate indicators
    ohlc['ATR'] = ohlc.ta.atr(length=10)
    ohlc['RSI'] = ohlc.ta.rsi()
    
    # Calculate the reversal 
    ohlc["high_diff"] = ohlc["High"] - ohlc[["Open","Close"]].max(axis=1)
    ohlc["body_diff"] = (ohlc["Open"] - ohlc["Close"]).abs()
   
     
    ohlc["low_diff"] = ohlc[["Open","Close"]].min(axis=1) - ohlc["Low"]
    ohlc["ratio1"]   = ohlc["high_diff"]/ohlc["body_diff"]
    ohlc["ratio2"]   = ohlc["low_diff"]/ohlc["body_diff"]
    
    first_condition  = (ohlc["ratio1"] > 2.5) & (ohlc["low_diff"] < 0.3*ohlc["high_diff"]) & (ohlc["body_diff"] > 0.00003) & (ohlc["RSI"] > 50) & (ohlc["RSI"] > 70)
    second_condition = (ohlc["ratio2"] > 2.5) & (ohlc["high_diff"] < 0.23*ohlc["low_diff"]) & (ohlc["body_diff"] > 0.00003) & (ohlc["RSI"] < 55) & (ohlc["RSI"] < 30)
    
    ohlc["signal"]  = np.select([first_condition, second_condition], [1,2], 0 )
    
    
    ohlc.loc[:,"buy_position"] = np.where(ohlc["signal"]==1, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(ohlc["signal"]==2, ohlc["Low"],np.nan)


    # Signal Points 
    ohlc.loc[:,"buy"] = np.where(ohlc["signal"]==2,1,0)
    ohlc.loc[:,"sell"] = np.where(ohlc["signal"]==1,1,0) 
       
    # Plot 
    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name)  
 
 
    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name)       
     
if __name__ == "__main__":
    main()
    