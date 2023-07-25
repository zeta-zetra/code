"""
Bollinger and Doji

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-25
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=6

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


CANDLESTICK = "engulfing" # "doji"

def main(show_plot=False):
    """
    """
    
    
    strategy_name = "bollinger-candlestick-"+CANDLESTICK
    
    # Read in the data
    ohlc  = read_data()
    
    # reset index
    ohlc.reset_index(inplace=True) 
    
    # Calculate Bollinger 
    bbands  = ohlc.ta.bbands(length=30, std=1.5)
    ohlc    = pd.concat([ohlc, bbands], axis=1) 
    
    # Lags
    ohlc["lag_close_1"] = ohlc["Close"].shift(1)  
    ohlc["lag_close_2"] = ohlc["Close"].shift(2)
    ohlc["lag_close_3"] = ohlc["Close"].shift(3)
    ohlc["lag_open_1"]  = ohlc["Open"].shift(1)  
    ohlc["lag_open_2"]  = ohlc["Open"].shift(2)
    ohlc["lag_open_3"]  = ohlc["Open"].shift(3)
    ohlc['lag_bbl']     = ohlc['BBL_30_1.5'].shift(1)
    ohlc['lag_bbu']     = ohlc['BBU_30_1.5'].shift(1)
    
    
    # Create signal based on candlestick selected 
    if CANDLESTICK == "doji":
        first_condition = (ohlc["lag_close_1"] < ohlc["lag_bbl"]) & (ohlc["lag_close_1"] > ohlc["lag_open_1"]) & (ohlc["lag_close_2"] == ohlc["lag_open_2"] ) & \
            (ohlc["lag_close_3"] < ohlc["lag_open_3"])
        second_condition = (ohlc["lag_close_1"] > ohlc["lag_bbu"]) & (ohlc["lag_close_1"] < ohlc["lag_open_1"]) & (ohlc["lag_close_2"] == ohlc["lag_open_2"] ) & \
            (ohlc["lag_close_3"] > ohlc["lag_open_3"])
        
        ohlc["signal"] = np.select([first_condition, second_condition],[1,2],0)
        
    elif CANDLESTICK == "engulfing":
         first_condition = (ohlc["lag_close_1"] < ohlc["lag_bbl"]) & (ohlc["lag_close_1"] > ohlc["lag_open_1"]) & (ohlc["lag_close_2"] < ohlc["lag_open_2"] ) & \
            (ohlc["lag_open_1"] < ohlc["lag_close_2"])  & (ohlc["lag_close_1"] > ohlc["lag_open_2"])
            
         second_condition = (ohlc["lag_close_1"] > ohlc["lag_bbu"]) & (ohlc["lag_close_1"] < ohlc["lag_open_1"]) & (ohlc["lag_close_2"] > ohlc["lag_open_2"] ) & \
            (ohlc["lag_open_1"] > ohlc["lag_close_2"])  & (ohlc["lag_close_1"] < ohlc["lag_open_2"])  
            
         ohlc["signal"] = np.select([first_condition, second_condition],[1,2],0)
         
                    
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