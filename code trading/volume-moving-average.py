"""
Volume and Moving Average Strategy

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=28

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


BACK_CANDLES = 8
VOLUME_BACK_CANDLES = 1
PRICE_BACK_CANDLES = 4

def find_ema_signal(df: pd.DataFrame, backcandles:int = 20) -> pd.DataFrame:
    """
    Find EMA signal based on back candles
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params backcandles is the number of look back candles to use 
    :type :int 
    
    
    :return: (int)
    """

    df["ema_signal"] = np.nan 
    pbar = tqdm(range(backcandles -1, len(df)))
    for row in pbar:
        upt = 1
        dnt = 1
        for i in range(row-backcandles, row+1):
            if df.High[row]>=df.ema_200[row]:
                dnt=0
            if df.Low[row]<=df.ema_200[row]:
                upt=0
        if upt==1 and dnt==1:
            #print("!!!!! check trend loop !!!!")
            
            df.loc[row,"ema_signal"] = 3
        elif upt==1:
            df.loc[row,"ema_signal"] = 1
        elif dnt==1:
            df.loc[row,"ema_signal"] = 2
         
        pbar.set_description("Finding the EMA signals..")            
    return df 


def find_volume_signal(df: pd.DataFrame, backcandles:int = 1) -> pd.DataFrame:
    """
    Find the volumen signal
    
    :params df is the OHLC 
    :type :pd.DataFrame
    
    :params backcandles is the number of candles to lookback 
    :type :int 
    
    :return: (pd.DataFrame)
    """

    df["volume_signal"] = 1
    pbar = tqdm(range(backcandles+1, len(df)))
    for row in pbar:

        for i in range(row-backcandles, row):
            if df.Volume[row] < df.Volume[i] and df.Volume[row-1] < df.Volume[row-2]:
                df.loc[row, "volume_signal"] = 0
        pbar.set_description("Finding the volume signal...") 
                
    return df 


def find_price_signal(df: pd.DataFrame, backcandles:int = 4) -> pd.DataFrame:
    """
    Find the price signal 
    
    
    :params df is the OHLC 
    :type :pd.DataFrame
    
    :params backcandles is the number of candles to lookback 
    :type :int 
    
    :return: (pd.DataFrame)    
    """

    df["price_signal"] = 1
    pbar               = tqdm(range(backcandles, len(df)))
    
    for row in pbar:
        
        for i in range(row-backcandles, row):
            if df.ema_signal[row] == 2: #downtrend
                if df.Open[row]<=df.Close[row]: #downcandle row
                    df.loc[row,"price_signal"]=0
                elif df.Open[i] > df.Close[i]: #downcandle i we are looking for 4 upcandles
                    df.loc[row,"price_signal"]=0
                    
            if df.ema_signal[row] == 1: #uptrend
                if df.Open[row] >= df.Close[row]: #upcandle row
                    df.loc[row,"price_signal"]=0
                elif df.Open[i] < df.Close[i]: #upcandle i we are looking for 4 dowcandles
                    df.loc[row,"price_signal"]=0
            else:
                df.loc[row,"price_signal"] = 0

        pbar.set_description("Finding the price signal...")
        
    return df 

def main(show_plot=False):
    """
    
    """
    
    strategy_name = "volume-moving-average"
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)
    
    # Calculate the technical indicators 
    ohlc["ema_200"] = ohlc.ta.ema(length=200)   

    # Find the ema signal 
    ohlc = find_ema_signal(ohlc, backcandles=BACK_CANDLES)
    
    # Find volume signal 
    ohlc = find_volume_signal(ohlc, backcandles=VOLUME_BACK_CANDLES)
    
    # Find the price signal
    ohlc = find_price_signal(ohlc, backcandles=PRICE_BACK_CANDLES)
    
    
    # Find the total signal
    first_condition  = (ohlc["ema_signal"] == 1) & (ohlc["volume_signal"] == 1) & (ohlc["price_signal"] == 1)
    second_condition = (ohlc["ema_signal"] == 2) & (ohlc["volume_signal"] == 1) & (ohlc["price_signal"] == 1)
    
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
    