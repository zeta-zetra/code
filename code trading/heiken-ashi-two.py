"""
Heiken Ashi Two

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=14

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



def find_heiken_ashi_signal(df: pd.DataFrame, ratio: float = 1.5) -> pd.DataFrame:
    """
    Find the Heiken Ashi signal
    
    :params df is the OHLC dataframe 
    :type :pd.DataFrame
    
    :params ratio 
    :type :float 
    
    :return: (pd.DataFrame)
    """
    
    df["prev_heiken_open"]  = df['heiken_open'].shift(1)
    df["prev_heiken_close"] = df['heiken_close'].shift(1)
    df["prev_heiken_low"]   = df['heiken_low'].shift(1)
    df["prev_heiken_high"]  = df['heiken_high'].shift(1)
    df["prev_heiken_body"]  = (df["prev_heiken_open"] - df["prev_heiken_close"]).abs()

    
  
    df["max_heiken_open_close"] = df[["prev_heiken_open", "prev_heiken_close"]].max(axis=1)
    df["min_heiken_open_close"] = df[["prev_heiken_open", "prev_heiken_close"]].min(axis=1)
    
    first_condition = ((df["prev_heiken_high"] - df["max_heiken_open_close"])/df["prev_heiken_body"] > ratio) & \
                      ( (df["min_heiken_open_close"] - df["min_heiken_open_close"])/df["prev_heiken_body"] > ratio ) & \
                      ( df['heiken_open'] < df['heiken_close']) & (df['heiken_low'] >= df['heiken_open'])
                      
                      
    
    second_condition = ((df["prev_heiken_high"] - df["max_heiken_open_close"])/df["prev_heiken_body"] > ratio) & \
                      ( (df["min_heiken_open_close"] - df["min_heiken_open_close"])/df["prev_heiken_body"] > ratio ) & \
                      ( df['heiken_open'] >= df['heiken_close']) & (df['heiken_high'] <= df['heiken_open'])


    df["ha_signal"] = np.select([first_condition, second_condition], [1,2], 0)
    
    return df 

def main(show_plot=False):
    """
    """
    strategy_name = "heiken-ashi-two"
    
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)    

    # Calculate the EMAs 
    ohlc["ema_10"] = ohlc.ta.ema(length=10)
    ohlc["ema_30"] = ohlc.ta.ema(length=30)

    # Calculate Heiken Ashi candlesticks
    ohlc['heiken_close'] = (ohlc.Open + ohlc.Close + ohlc.High + ohlc.Low)/4
    ohlc['heiken_open']  = ohlc['Open']
    ohlc['heiken_open']  = (ohlc.heiken_open.shift(1) + ohlc.heiken_close.shift(1))/2
    ohlc['heiken_high']  = ohlc[['High', 'heiken_open', 'heiken_close']].max(axis=1)
    ohlc['heiken_low']   = ohlc[['Low', 'heiken_open', 'heiken_close']].min(axis=1)
    
    
    # Find HA signal
    ohlc = find_heiken_ashi_signal(ohlc)
    
    # Find the signal            
    first_condition  = (ohlc["ema_10"] > ohlc["ema_30"]) & (ohlc["heiken_open"] < ohlc["ema_10"]) & (ohlc["heiken_close"] > ohlc["ema_10"]) & (ohlc["ha_signal"] == 1)
    second_condition = (ohlc["ema_10"] < ohlc["ema_30"]) & (ohlc["heiken_open"] > ohlc["ema_10"]) & (ohlc["heiken_close"] < ohlc["ema_10"]) & (ohlc["ha_signal"] == 2)
    
    ohlc["signal"]    = np.select([first_condition, second_condition], [1,2], 0)
        
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