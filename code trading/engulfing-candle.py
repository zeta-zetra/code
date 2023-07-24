"""
Engulfing candlestick 

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-23
Source: https://www.youtube.com/watch?v=eN4zh3PEH6c&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=46

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


BODY_DIFF_MIN = 0.00003

def main(show_plot=False):
    """
    
    """
    
    strategy_name = "engulfing-candle"

    # Read in the data
    ohlc  = read_data()
    
    # Calculate the engulfing pattern signal
    ohlc["body_diff"] = (ohlc["Open"] - ohlc["Close"]).abs()
    
    
    first_condition = (ohlc["body_diff"] > BODY_DIFF_MIN) & ( ohlc["body_diff"].shift(1) > BODY_DIFF_MIN) & (ohlc["Open"].shift(1) < ohlc["Close"].shift(1)) & \
                      (ohlc["Open"] > ohlc["Close"]) & ( (ohlc["Open"] - ohlc["Close"]) > 0) & (ohlc["Close"] < ohlc["Open"].shift(1))
                      
    second_condition = (ohlc["body_diff"] > BODY_DIFF_MIN)  & ( ohlc["body_diff"].shift(1) > BODY_DIFF_MIN) & (ohlc["Open"].shift(1) > ohlc["Close"].shift(1)) & \
                        (ohlc["Open"] < ohlc["Close"]) & ( (ohlc["Open"] - ohlc["Close"]) < 0) & (ohlc["Close"] > ohlc["Open"].shift(1))
    
    ohlc["signal"]  = np.select([first_condition, second_condition], [1,2], 0 )
    
    
    ohlc.loc[:,"buy_position"] = np.where(ohlc["signal"]==1, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(ohlc["signal"]==2, ohlc["Low"],np.nan)
    
    # Signal Points 
    ohlc.loc[:,"buy"] = np.where(ohlc["signal"]==2,1,0)
    ohlc.loc[:,"sell"] = np.where(ohlc["signal"]==1,1,0)     
    
    
    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name) 
        
    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name)   
                
if __name__ == "__main__":
    main()