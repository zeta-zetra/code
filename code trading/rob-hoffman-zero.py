"""
Rob Hoffman strategy

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=24

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


SLOPE_LIMIT   = 5e-5
PERCENT_LIMIT = 0.45

def main(show_plot=False):
    """
    
    """
    
    strategy_name = "rob-hoffman-zero"
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)
    
    # Calculate the ema
    ohlc["ema"] = ohlc.ta.ema(length=20)
    
    # Calculate the rolling ema 
    backrollingN = 20
    ohlc['slope_ema'] = ohlc['ema'].diff(periods=1)
    ohlc['slope_ema'] = ohlc['slope_ema'].rolling(window=backrollingN).mean()
    
    # Find the signal 
    ohlc["min_close_open"] = ohlc[["Open","Close"]].min(axis=1)
    ohlc["max_close_open"] = ohlc[["Open","Close"]].max(axis=1)
    first_condition  = (ohlc["slope_ema"] > SLOPE_LIMIT) & (((ohlc["High"] - ohlc["max_close_open"])/(ohlc["High"] - ohlc["Low"])) > PERCENT_LIMIT) 
    second_condition = (ohlc["slope_ema"] < -SLOPE_LIMIT) & (((ohlc["min_close_open"] - ohlc["Low"])/(ohlc["High"] - ohlc["Low"])) > PERCENT_LIMIT)
    
    
    ohlc["signal"]  = np.select([first_condition, second_condition],[1,2],0)
    
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
