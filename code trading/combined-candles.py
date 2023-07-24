"""
Combined Candles 

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-23
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=45

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


BODY_DIFF_MIN = 0.00002
WITH_RSI = False



def main(show_plot=False):
    """
    
    """
    
    if WITH_RSI:
        strategy_name = "combined-candles-rsi"
    else:
        strategy_name = "combined-candles"

    # Read in the data
    ohlc  = read_data()
    
    # Calculate RSI 
    ohlc['RSI'] = ohlc.ta.rsi()
    
  
    ohlc["body_diff"] = (ohlc["Open"] - ohlc["Close"]).abs()     
    ohlc["body_diff"] = np.where(ohlc["body_diff"] < 0.000001,0.000001, ohlc["body_diff"])
    
    # Get engulfing pattern        
    engulfing_1 = (ohlc["body_diff"] > BODY_DIFF_MIN) & (ohlc["body_diff"].shift(1) > BODY_DIFF_MIN) & (ohlc["Open"].shift(1) < ohlc["Close"].shift(1)) & \
                  (ohlc["Open"] > ohlc["Close"]) & ( (ohlc["Open"] - ohlc["Close"].shift(1)) > 0) & (ohlc["Close"] < ohlc["Open"].shift(1))
           
    engulfing_2 = (ohlc["body_diff"] > BODY_DIFF_MIN) & (ohlc["body_diff"].shift(1) > BODY_DIFF_MIN) & (ohlc["Open"].shift(1) > ohlc["Close"].shift(1)) & \
                     ( ohlc["Open"] < ohlc["Close"]) & ( (ohlc["Open"] - ohlc["Close"].shift(1)) < 0) & (ohlc["Close"] > ohlc["Open"].shift(1))
                  
    ohlc["engulfing"] = np.select([engulfing_1, engulfing_2], [1,2], 0)
               
    
    # Get star pattern 
    ohlc["high_diff"] = ohlc["High"] - ohlc[["Open","Close"]].max(axis=1)
    ohlc["low_diff"]  = ohlc[["Open","Close"]].min(axis=1) - ohlc["Low"] 
    
    ohlc["ratio1"] = ohlc["high_diff"]/ohlc["body_diff"]
    ohlc["ratio2"] = ohlc["low_diff"]/ohlc["body_diff"]
    
    
    star_1  = (ohlc["ratio1"] > 1) & (ohlc["low_diff"] < 0.2*ohlc["high_diff"]) & (ohlc["body_diff"] > BODY_DIFF_MIN)
    star_2  = (ohlc["ratio2"] > 1) & (ohlc["high_diff"] < 0.2*ohlc["low_diff"]) & (ohlc["body_diff"] > BODY_DIFF_MIN)
    
    ohlc["star"] = np.select([star_1, star_2], [1,2], 0)
    
    # Get the condtitions for the signal
    if WITH_RSI:
        first_condition  = (ohlc["engulfing"]==1) & (ohlc["star"] == 1) & (ohlc["RSI"] < 30 )
        second_condition = (ohlc["engulfing"]==2) & (ohlc["star"] == 2) & (ohlc["RSI"] > 70 )
    else:
        first_condition = (ohlc["engulfing"]==1) & (ohlc["star"] == 1)
        second_condition = (ohlc["engulfing"]==2) & (ohlc["star"] == 2)
        
    # Get the signal
    ohlc["signal"]  = np.select([first_condition, second_condition], [1,2], 0 )
    
    ohlc.loc[:,"buy_position"] = np.where(ohlc["signal"]==1, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(ohlc["signal"]==2, ohlc["Low"],np.nan)
    
    # Signal Points 
    ohlc.loc[:,"buy"] = np.where(ohlc["signal"]==1,1,0)
    ohlc.loc[:,"sell"] = np.where(ohlc["signal"]==2,1,0)     
    
    
    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name) 
        
    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name)       
    
if __name__ == "__main__":
    main()