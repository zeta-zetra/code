"""
Support and resistance candles 

This is s strategy from the CodingTrading Youtube Channel. It has only been refactored.

Date: 2023-07-23
Source: https://www.youtube.com/watch?v=TiWjTpuL21w&list=PLwEOixRFAUxZmM26EYI1uYtJG39HDW1zm&index=43

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 
"""

import numpy as np 
import pandas as pd 
import pandas_ta as ta 

from progress.bar import Bar
from typing import List

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest

WITH_RSI = True
BODY_DIFF_MIN = 0.00002
n1=2
n2=2
back_candles=45



def support(df: pd.DataFrame, l:int, n1:int , n2:int) -> int:
    """
    Get the support point
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params l is current row
    :type :int 
    
    :params n1 is the number of bars to the left of l 
    :type :int 
    
    :params n2 is the number of bars to the right of l 
    :type :int 
    
    :return: (int)
    """ 
    for i in range(l-n1+1, l+1):
        if(df.Low[i]>df.Low[i-1]):
            return 0
    for i in range(l+1,l+n2+1):
        if(df.Low[i]<df.Low[i-1]):
            return 0
    return 1

def resistance(df: pd.DataFrame, l: int, n1: int, n2: int) -> int:  
    """
    Get the resistance point
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params l is current row
    :type :int 
    
    :params n1 is the number of bars to the left of l 
    :type :int 
    
    :params n2 is the number of bars to the right of l 
    :type :int 
    
    :return: (int)    
    """
    for i in range(l-n1+1, l+1):
        if(df.High[i] < df.High[i-1]):
            return 0
        
    for i in range(l+1,l+n2+1):
        if(df.High[i] > df.High[i-1]):
            return 0
    return 1


def close_resistance(df: pd.DataFrame, l: int, levels: List[float], limit: float) -> int:
    """
    Find if the point is near the resistance level
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame    
    
    :params l is the current row 
    :type :int 
    
    :params levels is the identified resistance points 
    :type :list 
    
    :params limit is the distance between the levels and the current candle 
    :type :float 
    
    :return: (int)
    """
    if len(levels)==0:
        return 0
    c1 = abs(df.High[l]-min(levels, key=lambda x:abs(x-df.High[l]))) <= limit
    c2 = abs(max(df.Open[l],df.Close[l])-min(levels, key=lambda x:abs(x-df.High[l]))) <=limit
    c3 = min(df.Open[l],df.Close[l]) < min(levels, key=lambda x:abs(x-df.High[l]))
    c4 = df.Low[l] < min(levels, key=lambda x:abs(x-df.High[l]))
    if( (c1 or c2) and c3 and c4 ):
        return 1
    else:
        return 0
    
def close_support(df: pd.DataFrame, l: int, levels: List[float], limit: float) -> int:
    """
    Find if the point is near the support level
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame    
    
    :params l is the current row 
    :type :int 
    
    :params levels is the identified support points 
    :type :list 
    
    :params limit is the distance between the levels and the current candle 
    :type :float 
    
    :return: (int)   
    """
    
    if len(levels)==0:
        return 0
    c1 = abs(df.Low[l]-min(levels, key=lambda x:abs(x-df.Low[l])))<=limit
    c2 = abs(min(df.Open[l], df.Close[l])-min(levels, key=lambda x:abs(x-df.Low[l])))<=limit
    c3 = max(df.Open[l],df.Close[l])>min(levels, key=lambda x:abs(x-df.Low[l]))
    c4 = df.High[l]>min(levels, key=lambda x:abs(x-df.Low[l]))
    if( (c1 or c2) and c3 and c4 ):
        return 1
    else:
        return 0


def main(show_plot=False):
    """
    
    """
    if not WITH_RSI: 
        strategy_name = "support-and-resistance-candles"
    else:
        strategy_name = "support-and-resistance-rsi-candles"

    # Read in the data
    ohlc  = read_data()    

    # Calculate the RSI
    ohlc["RSI"] = ohlc.ta.rsi()
   
   
    # Calculate the body diff
    ohlc["body_diff"] = (ohlc["Open"] - ohlc["Close"]).abs()     
    ohlc["body_diff"] = np.where(ohlc["body_diff"] < 0.000001,0.000001, ohlc["body_diff"])
    
    # Get engulfing pattern        
    engulfing_1 = (ohlc["body_diff"] > BODY_DIFF_MIN) & (ohlc["body_diff"].shift(1) > BODY_DIFF_MIN) & (ohlc["Open"].shift(1) < ohlc["Close"].shift(1)) & \
                  (ohlc["Open"] > ohlc["Close"]) & ( (ohlc["Open"] - ohlc["Close"].shift(1)) > 0) & (ohlc["Close"] < ohlc["Open"].shift(1))
           
    engulfing_2 = (ohlc["body_diff"] > BODY_DIFF_MIN) & (ohlc["body_diff"].shift(1) > BODY_DIFF_MIN) & (ohlc["Open"].shift(1) > ohlc["Close"].shift(1)) & \
                     ( ohlc["Open"] < ohlc["Close"]) & ( (ohlc["Open"] - ohlc["Close"].shift(1)) < 0) & (ohlc["Close"] > ohlc["Open"].shift(1))
                  
    ohlc["engulfing"] = np.select([engulfing_1, engulfing_2], [1,2], 0)
               
    
    # Get star pattern 
    ohlc["high_diff"] = ohlc["High"] - ohlc[["Open","Close"]].max(axis=1)
    ohlc["low_diff"]  = ohlc[["Open","Close"]].min(axis=1) - ohlc["Low"] 
    
    ohlc["ratio1"] = ohlc["high_diff"]/ohlc["body_diff"]
    ohlc["ratio2"] = ohlc["low_diff"]/ohlc["body_diff"]
    
    
    star_1  = (ohlc["ratio1"] > 1) & (ohlc["low_diff"] < 0.2*ohlc["high_diff"]) & (ohlc["body_diff"] > BODY_DIFF_MIN)
    star_2  = (ohlc["ratio2"] > 1) & (ohlc["high_diff"] < 0.2*ohlc["low_diff"]) & (ohlc["body_diff"] > BODY_DIFF_MIN)
    
    ohlc["star"] = np.select([star_1, star_2], [1,2], 0)
    
    
    # Find the signal points
    ohlc["signal"] = 0
    
    ohlc.reset_index(inplace=True)
    
    bar = Bar("Finding signal points...", max=len(range(back_candles, len(ohlc)-n2)))
    for row in range(back_candles, len(ohlc)-n2):
        ss = []
        rr = []
        
        for subrow in range(row-back_candles+n1, row+1):
            if support(ohlc, subrow, n1, n2):
                ss.append(ohlc.Low[subrow])
            if resistance(ohlc, subrow, n1, n2):
                rr.append(ohlc.High[subrow])
                
        if not WITH_RSI:
            if ((ohlc.loc[row,"engulfing"]==1 or ohlc.loc[row,"star"]==1) and close_resistance(ohlc,row, rr, 150e-5) ):#and df.RSI[row]<30
                ohlc.loc[row,"signal"] = 1
            elif((ohlc.loc[row,"engulfing"]==2 or ohlc.loc[row,"star"]==2) and close_support(ohlc, row, ss, 150e-5)):#and df.RSI[row]>70
                ohlc.loc[row,"signal"] = 2
        else:
            if ((ohlc.loc[row,"engulfing"]==1 or ohlc.loc[row,"star"]==1) and close_resistance(ohlc,row, rr, 150e-5) and ohlc.RSI[row]<30 ):
                ohlc.loc[row,"signal"] = 1
            elif((ohlc.loc[row,"engulfing"]==2 or ohlc.loc[row,"star"]==2) and close_support(ohlc, row, ss, 150e-5) and ohlc.RSI[row]>70):
                ohlc.loc[row,"signal"] = 2

        bar.next()
    bar.finish()
    
    
    # Set the index 
    ohlc.set_index("datetime", inplace=True)
 
    ohlc.loc[:,"buy_position"] = np.where(ohlc["signal"]==1, ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(ohlc["signal"]==2, ohlc["Low"],np.nan)
    
    # Signal Points 
    ohlc.loc[:,"buy"] = np.where(ohlc["signal"]==1,1,0)
    ohlc.loc[:,"sell"] = np.where(ohlc["signal"]==2,1,0)     
    
    
    if show_plot:
        plot_ohlc(ohlc, filename=strategy_name) 
        
    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name)  
    
if __name__ == "__main__":
    main()
