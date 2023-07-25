"""
Breakout Strategy

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-25
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=7

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 
"""

import numpy as np 
import pandas as pd 
import pandas_ta as ta 

from scipy import stats
from tqdm import tqdm 
from typing import Tuple

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest


def find_pivot(df: pd.DataFrame, candle: int, window:int ) -> int:
    """
    Function that detects if a candle is a pivot/fractal point
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params candle is the current candle bar
    :type :int
    
    :params window is the number of candles before and after the current candle bar
    :type :int 
    
    :return: (int)
    """

    if candle-window < 0 or candle+window >= len(df):
        return 0
    
    pivot_high = 1
    pivot_low  = 2
    
    for i in range(candle - window, candle + window + 1):
        if df.iloc[candle].Low > df.iloc[i].Low:
            pivot_low = 0
            
        if df.iloc[candle].High < df.iloc[i].High:
            pivot_high = 0
            
    if (pivot_high and pivot_low):
        return 3
    elif pivot_high:
        return pivot_high
    elif pivot_low:
        return pivot_low
    else:
        return 0


def find_channel(df: pd.DataFrame, candle:int , backcandles:int , window:int ) -> Tuple[float, float, float, float, float, float]:
    """
    Find the channels 
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params candle is the current candle bar
    :type :int 
    
    :params backcandles is the number of candle bars to lookback
    :type :int
    
    :params window is the number of candles before and after the current bar
    :type :int 
    
    :return: (Tuple[float, float, float, float, float, float])
    """
    localdf  = df[candle-backcandles-window:candle-window]
   
    highs    = localdf[localdf['pivot']==1].High.values
    idxhighs = localdf[localdf['pivot']==1].High.index
    
    lows     = localdf[localdf['pivot']==2].Low.values
    idxlows  = localdf[localdf['pivot']==2].Low.index
    
    if len(lows) >= 3 and len(highs) >= 3:
        
        sl_lows, interc_lows, r_value_l, _, _ = stats.linregress(idxlows,lows)
        sl_highs, interc_highs, r_value_h, _, _ = stats.linregress(idxhighs,highs)
    
        return(sl_lows, interc_lows, sl_highs, interc_highs, r_value_l**2, r_value_h**2)
    else:
        return(0,0,0,0,0,0)



def find_breakout_signal(df: pd.DataFrame, candle:int, backcandles:int, window:int) -> int:
    """
    Find the breakout signal
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params candle is the current candle bar
    :type :int 
    
    :params backcandles is the number of look back candles
    :type :int 
    
    :params window is the 
    :type :int
    
    :return: (int) 
    """
    
    if (candle-backcandles-window) < 0:
        return 0
    
    sl_lows, interc_lows, sl_highs, interc_highs, r_sq_l, r_sq_h = df.iloc[candle].channel
    
    prev_idx   = candle-1
    prev_high  = df.iloc[candle-1].High
    prev_low   = df.iloc[candle-1].Low
    prev_close = df.iloc[candle-1].Close
    
    curr_idx   = candle
    curr_high  = df.iloc[candle].High
    curr_low   = df.iloc[candle].Low
    curr_close = df.iloc[candle].Close
    curr_open  = df.iloc[candle].Open

    if ( prev_high > (sl_lows*prev_idx + interc_lows) and
        prev_close < (sl_lows*prev_idx + interc_lows) and
        curr_open < (sl_lows*curr_idx + interc_lows) and
        curr_close < (sl_lows*prev_idx + interc_lows)): #and r_sq_l > 0.9
        return 2
    
    elif ( prev_low < (sl_highs*prev_idx + interc_highs) and
        prev_close > (sl_highs*prev_idx + interc_highs) and
        curr_open > (sl_highs*curr_idx + interc_highs) and
        curr_close > (sl_highs*prev_idx + interc_highs)): #and r_sq_h > 0.9
        return 1
    
    else:
        return 0


def main(show_plot=False):
    """
    """
    
    backcandles = 45
    strategy_name = "breakout"
    
    # Read in the data
    ohlc  = read_data()
    
    # reset index
    ohlc.reset_index(inplace=True)    
    
    # Find pivot
    window = 3
    tqdm.pandas(desc='Finding Pivot Points...')
    ohlc['pivot']   = ohlc.progress_apply(lambda x: find_pivot(ohlc, x.name, window), axis=1)
    
    # Get the channels
    pbar            = tqdm(ohlc.index, desc="Finding the channels...")
    ohlc['channel'] = [find_channel(ohlc, candle, backcandles, window) for candle in pbar]
    
        
    # Find the signals
    ohlc["signal"] = [find_breakout_signal(ohlc, candle, backcandles, window) for candle in ohlc.index]
    
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