"""
Scalping with RSI, EMA and ADX 

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=29

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


def main(show_plot=False):
    """
    
    """
    
    strategy_name = "adx-rsi-ema"
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)
    
    # Calculate the technical indicators 
    ohlc["ema_200"] = ohlc.ta.ema(length=200)
    ohlc            = find_ema_signal(ohlc, backcandles=BACK_CANDLES)
    ohlc["rsi"]     = ohlc.ta.rsi(length=3)
    adx             = ta.adx(ohlc.High, ohlc.Low, ohlc.Close, length=7)
    ohlc['adx']     = adx['ADX_7']
    
    
    # Find the signal 
    ohlc["lag_close"] = ohlc["Close"].shift(1)
    ohlc["lag_open"]  = ohlc["Open"].shift(1)
    first_condition  = (ohlc["ema_signal"] == 1) & (ohlc["rsi"] <= 20) & (ohlc["adx"] >= 30) & (ohlc["Open"] < ohlc["Close"]) & \
                       (ohlc["Close"] > ohlc[["lag_open","lag_close"]].max(axis=1) )

    second_condition = (ohlc["ema_signal"] == 2) & (ohlc["rsi"] >= 80) & (ohlc["adx"] >= 30) & (ohlc["Open"] < ohlc["Close"]) & \
                        (ohlc["Close"] < ohlc[["lag_open","lag_close"]].min(axis=1) )
                        
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
    