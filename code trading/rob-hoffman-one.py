"""
Rob Hoffman strategy

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=22

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
BACK_CANDLES = 5

def find_ema_signal(df: pd.DataFrame, l:int, back_candles:int = 30) -> int:
    """
    Find the ema signal based on the back candles
    
    :params df is the OHLC data 
    :type :pd.DataFrame
    
    :params l is the row index
    :type :int 
    
    :params back_candles is the look back number of candles
    :type :int 
    
    
    :return: (int)
    """
    sigup = 1
    sigdn = -1
    for i in range(l-back_candles, l+1):
        if df.Low[i]<=df.ema[i]:
            sigup = 0
            
        if df.High[i]>=df.ema[i]:
            sigdn = 0
    if sigup:
        return sigup
    elif sigdn:
        return sigdn
    else:
        return 0



def find_rob_hoffman_signal(df: pd.DataFrame, left_bars: int, right_bars:int) -> pd.DataFrame:
    """
    Find the Rob Hoffman's signal
    
    :params df is OHLC is dataframe
    :type :pd.DataFrame
    
    :params left_bars is the number of bars to the left of the current candle to be considered
    :type :int 
    
    :params righ_bars is the number of bars to the righ of the current candle to be considered
    :type :int    
    
    :return: (pd.DataFrame)
    """
    
    df["rh_signal"] = 0
    df["min_close_open"] = df[["Open","Close"]].min(axis=1)
    df["max_close_open"] = df[["Open","Close"]].max(axis=1)
    
    pbar = tqdm(range(left_bars, len(df)))
    for row in pbar:
      try:  
          div = (df.loc[row-right_bars, "High"]-df.loc[row-right_bars, "Low"])
      except:
          continue 
      
      if df.loc[row-right_bars, "slope_ema"] < -SLOPE_LIMIT and (((df.loc[row-right_bars,"min_close_open"] - df.loc[row-right_bars, "Low"])/(df.loc[row-right_bars, "High"] - df.loc[row-right_bars, "Low"]))) >PERCENT_LIMIT and \
           df.loc[row-right_bars,"Low"] <= df.loc[row-left_bars:row,"Low"].min() :
             df.loc[row-right_bars,"rh_signal"] = 2
        
      if df.loc[row-right_bars, "slope_ema"] > SLOPE_LIMIT and (df.loc[row-right_bars, "High"] - df.loc[row-right_bars,"max_close_open"])/(df.loc[row-right_bars, "High"]-df.loc[row-right_bars, "Low"]) > PERCENT_LIMIT and \
            df.loc[row-right_bars, "High"] >= df.loc[row-left_bars:row, "High"].max():
            df.loc[row-right_bars,"rh_signal"]=1
            
      pbar.set_description("Finding Rob Hoffman signal points...")
            
    return df  


def find_hoffman_break_signal(df: pd.DataFrame, l: int, backcandles: int) -> int:
    """
    Find the Hoffman break signal
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params l is the current candle bar index 
    :type :int 
    
    :params backcandles is the number of look back candles 
    :type :int 
    
    :return: (int)
    """
    
 
    for r in range(l-backcandles, l):
        if df.loc[l, "ema_signal"] == 1 and df.loc[r, "rh_signal"] == 1 and df.loc[l, "Close"] >= df.loc[r, "High"]:
            return 1
        elif df.loc[l, "ema_signal"] == -1 and df.loc[r, "rh_signal"] == 2 and df.loc[l, "Close"] <= df.loc[r, "Low"]:
            return 2

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
    
    # Find the EMA signal
    ohlc["ema_signal"] = 0
    
    pbar = tqdm(range(BACK_CANDLES, len(ohlc)))
    for row in pbar :
        ohlc.loc[row, "ema_signal"] = find_ema_signal(ohlc, row, back_candles=BACK_CANDLES)
        pbar.set_description("Finding EMA signals...")
        
        
    # Find the Hoffman Signal
    rh_backcandles_left = 7
    rh_backcandles_right = 5
    
    ohlc = find_rob_hoffman_signal(ohlc, rh_backcandles_left, rh_backcandles_right)
    
    # Find the Hoffman break signal
    backcandles = 1 
    pbar        = tqdm(range(backcandles, len(ohlc)))
    for row in pbar: 
         ohlc.loc[row, "signal"]  = find_hoffman_break_signal(ohlc, row, backcandles=backcandles)
         pbar.set_description("Finding Hoffman Break Signal points...")
    

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
        
