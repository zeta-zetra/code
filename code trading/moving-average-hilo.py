"""
Moving average and High, Low 

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=36

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 
"""

import numpy as np 
import pandas as pd 
import pandas_ta as ta 

from tqdm  import tqdm

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest


BACK_CANDLES = 30

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


def main(show_plot=False):
    """
    
    """
    
    strategy_name = "moving-average-hilo"
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)
    
    # Calculate the EMA
    ohlc["ema"] = ohlc.ta.ema(length=100)


    # Find the ema signal 
    ohlc["ema_signal"] = 0
    
    pbar = tqdm(range(BACK_CANDLES, len(ohlc)))
    for row in pbar :
        ohlc.loc[row, "ema_signal"] = find_ema_signal(ohlc, row, back_candles=BACK_CANDLES)
        pbar.set_description("Finding EMA signals...")
        
    # High and Low points        
    HLBackCandles = 8

    ohlc['mins'] = ohlc['Low'].rolling(window=HLBackCandles).min()
    ohlc['maxs'] = ohlc['High'].rolling(window=HLBackCandles).max()
    
    
    # Find the signal
    first_condition  = (ohlc["ema_signal"] == 1) & (ohlc["Low"] <= ohlc["mins"])
    second_condition = (ohlc["ema_signal"] == -1) & (ohlc["High"]>= ohlc["maxs"])
    ohlc["signal"]   = np.select([first_condition, second_condition], [1,2], 0)
    
    
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
