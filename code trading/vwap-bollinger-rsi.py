"""
VWAP Bollinger RSI 

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=13

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


def find_vwap_signal(df: pd.DataFrame, backcandles:int) -> pd.DataFrame:
    """
    Find the VWAP signal 
    
    :params df is the OHLC dataframe 
    :type :pd.DataFrame
    
    :params backcandles is the number of look back candles 
    :type :int 
    
    :return: (int)
    """ 
    
    df["vwap_signal"] = 0
    
    pbar   = tqdm(range(backcandles, len(df)))
    for row in pbar:
        upt = 1
        dnt = 1
        for i in range(row-backcandles, row+1):
            if df.High[i]>=df.vwap[i]:
                dnt=0
            if df.Low[i]<=df.vwap[i]:
                upt=0
        if upt==1 and dnt==1:
            df.loc[row, "vwap_signal"] = 3
            
        elif upt==1:
            df.loc[row, "vwap_signal"] = 1
        elif dnt==1:
            df.loc[row, "vwap_signal"] = 2

        pbar.set_description("Finding the VWAP signal points...")

    return df 



def main(show_plot=False):
    """
    
    """

    strategy_name = "vwap-bollinger-rsi"
    
    # Read in the data
    ohlc  = read_data() 
    
    # Calculate the indicators
    ohlc["vwap"] = ohlc.ta.vwap()
    
    # reset index
    ohlc.reset_index(inplace=True)    
    ohlc["rsi"]  = ohlc.ta.rsi(length=16)
    bbands       = ohlc.ta.bbands(length=14, std=2.0)
    
    ohlc = pd.concat([ohlc, bbands], axis=1)
    
    # Find the VWAP signal
    ohlc = find_vwap_signal(ohlc, backcandles=3)   
    
    # Find signal        
    first_condition  = (ohlc["vwap_signal"] == 1) & (ohlc["Close"] <= ohlc["BBL_14_2.0"]) & (ohlc["rsi"] < 45)
    second_condition = (ohlc["vwap_signal"] == 2) & (ohlc["Close"] >= ohlc["BBL_14_2.0"]) & (ohlc["rsi"] > 55)
    
    ohlc["signal"]    = np.select([first_condition, second_condition],[1,2],0)
    
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
    