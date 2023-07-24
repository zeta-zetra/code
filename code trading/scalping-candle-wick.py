"""
Scalping with Candle wick conditions

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=30

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



WICK_LIMIT = 2e-5

def main(show_plot=False):
    """
    
    """
    
    strategy_name = "scalping-candle-wick"
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)
    
    # Calculate the EMAs
    ohlc["ema_50"]  = ohlc.ta.ema(length=50)
    ohlc["ema_100"] = ohlc.ta.ema(length=100)
    ohlc["ema_150"] = ohlc.ta.ema(length=150)
        
    # Calculate the rolling averages
    backrollingN = 10
    ohlc['slope_ema_50'] = ohlc['ema_50'].diff(periods=1)
    ohlc['slope_ema_50'] = ohlc['slope_ema_50'].rolling(window=backrollingN).mean()

    ohlc['slope_ema_100'] = ohlc['ema_100'].diff(periods=1)
    ohlc['slope_ema_100'] = ohlc['slope_ema_100'].rolling(window=backrollingN).mean()

    ohlc['slope_ema_150'] = ohlc['ema_150'].diff(periods=1)
    ohlc['slope_ema_150'] = ohlc['slope_ema_150'].rolling(window=backrollingN).mean()   
        
    # Find the EMA signal    
    conditions = [
    ( (ohlc['ema_50'] < ohlc['ema_100']) & (ohlc['ema_100']<ohlc['ema_150']) & (ohlc['slope_ema_50']<0) & (ohlc['slope_ema_100']<0) & (ohlc['slope_ema_150']<0)),
    ( (ohlc['ema_50'] > ohlc['ema_100']) & (ohlc['ema_100']>ohlc['ema_150']) & (ohlc['slope_ema_50']>0) & (ohlc['slope_ema_100']>0) & (ohlc['slope_ema_150']>0))]
   
    choices = [2,1]
    ohlc['ema_signal'] = np.select(conditions, choices, default=0)

    # Find the signal 
    first_condition  = (ohlc["ema_signal"] == 1) & (ohlc["Open"] < ohlc["ema_50"]) & (ohlc["Close"] > ohlc["ema_50"]) & ((ohlc["Open"] - ohlc["Low"]) <= WICK_LIMIT)
    second_condition = (ohlc["ema_signal"] == 2) & (ohlc["Open"] > ohlc["ema_50"]) & (ohlc["Close"] < ohlc["ema_50"]) & ((ohlc["High"] - ohlc["Open"]) <= WICK_LIMIT )
    
    ohlc["signal"]   = np.select([first_condition, second_condition], [1,2],0)
    
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