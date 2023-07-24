"""
RSI and Divergence 

This is a strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-24
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=39

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT
"""

import numpy as np 
import pandas as pd 
import pandas_ta as ta 

from tqdm.auto import tqdm

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest


DIVERGENCE_SLOPES = False

def find_pivot_id(df: pd.DataFrame, l:int , n1:int, n2:int, rsi:bool = False) -> int: 
    """
    Find if the given point is a pivot point
    
    :params df is the OHLC data
    :type :pd.DataFrame
    
    :params l is the point to check
    :type :int
    
    :params n1 is the number of candles to consider to the left
    :type :int
    
    :params n2 is the number of candles to consider on the right
    :type :int 
    
    :params rsi is to get the pivot for the rsi indicator
    :type :bool
    
    :return: (int)
    """
    
    if l-n1 < 0 or l+n2 >= len(df):
        return 0
    
    pivot_id_low=1
    pivot_id_high=1
    
    for i in range(l-n1, l+n2+1):
        if ((df.Low[l] > df.Low[i]) and not rsi) or ((df.RSI[l] > df.RSI[i]) and rsi) :
            pivot_id_low = 0
            
        if(df.High[l] < df.High[i]) and not rsi or ((df.RSI[l]<df.RSI[i]) and rsi):
            pivot_id_high = 0
            
    if pivot_id_low and pivot_id_high:
        return 3
    elif pivot_id_low:
        return 1
    elif pivot_id_high:
        return 2
    else:
        return 0


def find_point_position(row: pd.Series, name: str = "pivot") -> float:
    """
    Annotate the pivot point position 
    
    :params row is the pandas Series (row)
    :type :pd.Series
    
    :params name of the column to check 
    :type :str 
    
    :return: (float)
    """
    if row[name]==1:
        return row['Low']-1e-3
    elif row[name]==2:
        return row['High']+1e-3
    else:
        return np.nan


def find_divergence_signal(ohlc: pd.DataFrame, row: pd.Series , back_candles: int = 30, slopes: bool = True) ->  int:
    """
    Find the divergence signal 
    
    :params ohlc is the OHLC dataframe
    :type :pd.DataFrame
    
    :params row is the pd.Series 
    :type  :pd.Series
    
    :params back_candles is the number of look back periods
    :type :int 
    
    :params slopes to be used for divergence or use points instead? 
    :type :bool 
    
    :return: (int)
    """
    candleid = int(row.name)
    
    if candleid < back_candles:
        return 0

    # Placeholders for price information
    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])

    # Placeholders for RSI information
    maximRSI = np.array([])
    minimRSI = np.array([])
    xxminRSI = np.array([])
    xxmaxRSI = np.array([])
    
    if not slopes:
        closp = np.array([])
        xxclos = np.array([])

    for i in range(candleid-back_candles, candleid+1):
        
        if not slopes:
            closp = np.append(closp, ohlc.iloc[i].Close)
            xxclos = np.append(xxclos, i)
        
        if ohlc.iloc[i].pivot == 1:
            minim = np.append(minim, ohlc.iloc[i].Low)
            xxmin = np.append(xxmin, i) 
        if ohlc.iloc[i].pivot == 2:
            maxim = np.append(maxim, ohlc.iloc[i].High)
            xxmax = np.append(xxmax, i) 
        if ohlc.iloc[i].rsi_pivot == 1:
            minimRSI = np.append(minimRSI, ohlc.iloc[i].RSI)
            xxminRSI = np.append(xxminRSI, ohlc.iloc[i].name)
        if ohlc.iloc[i].rsi_pivot == 2:
            maximRSI = np.append(maximRSI, ohlc.iloc[i].RSI)
            xxmaxRSI = np.append(xxmaxRSI, ohlc.iloc[i].name)

    if slopes:
            if maxim.size<2 or minim.size<2 or maximRSI.size<2 or minimRSI.size<2:
                return 0
            
            slmin, intercmin = np.polyfit(xxmin, minim,1)
            slmax, intercmax = np.polyfit(xxmax, maxim,1)
            slminRSI, intercminRSI = np.polyfit(xxminRSI, minimRSI,1)
            slmaxRSI, intercmaxRSI = np.polyfit(xxmaxRSI, maximRSI,1)
            
            
            if slmin > 1e-4 and slmax > 1e-4 and slmaxRSI <-0.1:
                return 1
            elif slmin < -1e-4 and slmax < -1e-4 and slminRSI > 0.1:
                return 2
            else:
                return 0
    else:
            slclos, interclos = np.polyfit(xxclos, closp,1)
    
            if slclos > 1e-4 and (maximRSI.size<2 or maxim.size<2):
                return 0
            if slclos < -1e-4 and (minimRSI.size<2 or minim.size<2):
                return 0
            
            # signal decisions here
            if slclos > 1e-4:
                if maximRSI[-1]<maximRSI[-2] and maxim[-1]>maxim[-2]:
                    return 1
            elif slclos < -1e-4:
                if minimRSI[-1]>minimRSI[-2] and minim[-1]<minim[-2]:
                    return 2
            else:
                return 0




def main(show_plot=False):
    """
    
    """
    


    if DIVERGENCE_SLOPES:
        strategy_name = "rsi-divergence-slopes"
    else:
        strategy_name = "rsi-divergence-points"
    # Read in the data
    ohlc  = read_data() 
    
    # reset index
    ohlc.reset_index(inplace=True)
        
    
    # Calculate the RSI 
    ohlc['RSI'] = ohlc.ta.rsi(length=14) 
    
    # Find the pivot points
    tqdm.pandas(desc='Finding Pivot Points...')
    ohlc['pivot']     = ohlc.progress_apply(lambda x: find_pivot_id(ohlc, x.name,5,5), axis=1)   
    
    tqdm.pandas(desc='Finding RSI Pivot Points...')
    ohlc['rsi_pivot'] = ohlc.progress_apply(lambda x: find_pivot_id(ohlc, x.name, 5, 5, rsi=True), axis=1)
    
    # Annotate the pivot point positions
    # ohlc['pivot_position']     = ohlc.apply(lambda x: find_point_position(x), axis=1)   
    # ohlc['rsi_pivot_position'] = ohlc.apply(lambda x: find_point_position(x, name='rsi_pivot'), axis=1)    

    # Find the divergence signal
    tqdm.pandas(desc='Finding the Signal Points...')
    if DIVERGENCE_SLOPES:
         ohlc['signal'] = ohlc.progress_apply(lambda row: find_divergence_signal(ohlc, row, 30), axis=1)  
    else: 
          ohlc['signal'] = ohlc.progress_apply(lambda row: find_divergence_signal(ohlc, row, 30, slopes=False), axis=1)  


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