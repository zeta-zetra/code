import numpy as np
import pandas as pd
import pandas_ta as ta


# Own Modules
from entry.entry import SimpleStrategy
from utils.utils import  read_data, run_backtest


CANDLESTICK = "harami"

def candlestick_pivot_point_1():
    """
    This uses a candlestick and the traditional
    """
    strategy_name = f"{CANDLESTICK}-candlestick-and-pivot-point-version-1"

    # Read in the data
    ohlc  = read_data()

    # Create a Date column that will be used in the merging
    intra_date    = ohlc.index.strftime('%Y-%m-%d')
    ohlc["MDate"] = intra_date

    # Resample to daily data
    open_daily       = ohlc["Open"].resample("D").first()
    close_daily      = ohlc["Close"].resample("D").last()
    high_daily       = ohlc["High"].resample("D").max()
    low_daily        = ohlc["Low"].resample("D").min()

    daily_index =  ohlc["Open"].resample("D").first().index.strftime('%Y-%m-%d')

    ohlc_daily = pd.DataFrame({
                "Open": open_daily,
                "High": high_daily,
                "Low" : low_daily,
                "Close": close_daily,
                "MDate": daily_index 
    })

    # Calculate the pivot points on the daily 
    ohlc_daily["PP"] = (ohlc_daily["High"] + ohlc_daily["Low"] + ohlc_daily["Close"])/3

    ohlc_daily["R1"] = ohlc_daily["PP"]*2 - ohlc_daily["Low"]
    ohlc_daily["S1"] = ohlc_daily["PP"]*2 - ohlc_daily["High"]
    
    ohlc_daily["R2"] = ohlc_daily["PP"] + (ohlc_daily["High"] - ohlc_daily["Low"])
    ohlc_daily["S2"] = ohlc_daily["PP"] - (ohlc_daily["High"] - ohlc_daily["Low"])

    # Shift the Pivot Points
    ohlc_daily["PP"] = ohlc_daily["PP"].shift(1)
    ohlc_daily["R1"] = ohlc_daily["R1"].shift(1)
    ohlc_daily["S1"] = ohlc_daily["S1"].shift(1)
    ohlc_daily["R2"] = ohlc_daily["R2"].shift(1)
    ohlc_daily["S2"] = ohlc_daily["S2"].shift(1)

    # Subset and get the Pivot points
    ohlc_daily = ohlc_daily[["MDate", "PP", "S1", "S2", "R1", "R2"]]

    # Merge the intra day and daily pivot point data
    ohlc_merged = ohlc.merge(ohlc_daily, left_on="MDate", right_on="MDate")
    ohlc_merged.set_index(ohlc.index, inplace=True)
    
    # Drop missing info
    ohlc_merged.dropna(inplace=True)
  
    # Calculate the patterns
    patterns  = ohlc_merged.ta.cdl_pattern(name=["harami"])

    ohlc_merged["harami"] = patterns["CDL_HARAMI"] 

    ohlc_merged.loc[:,"bullish_close"] = np.where(ohlc_merged["harami"]==100,ohlc_merged["Close"],np.nan) 
    ohlc_merged.loc[:,"bearish_close"] = np.where(ohlc_merged["harami"]==-100,ohlc_merged["Close"],np.nan)

    # Signal conditions
    buy_conditions  = (ohlc_merged["bullish_close"] >  ohlc_merged["R2"]) & (ohlc_merged["harami"]==100)
    sell_conditions = (ohlc_merged["bearish_close"] <  ohlc_merged["S2"]) & (ohlc_merged["harami"]==-100)

    # Signal Points
    ohlc_merged.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc_merged.loc[:,"sell"] = np.where(sell_conditions,1,0)  

    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc_merged, SimpleStrategy, strategy_name=strategy_name) 


def candlestick_pivot_point_2():
    """
    This uses a candlestick and the traditional
    """
    strategy_name = f"{CANDLESTICK}-candlestick-and-pivot-point-version-2"

    # Read in the data
    ohlc  = read_data()

    # Create a Date column that will be used in the merging
    intra_date    = ohlc.index.strftime('%Y-%m-%d')
    ohlc["MDate"] = intra_date

    # Resample to daily data
    open_daily       = ohlc["Open"].resample("D").first()
    close_daily      = ohlc["Close"].resample("D").last()
    high_daily       = ohlc["High"].resample("D").max()
    low_daily        = ohlc["Low"].resample("D").min()

    daily_index =  ohlc["Open"].resample("D").first().index.strftime('%Y-%m-%d')

    ohlc_daily = pd.DataFrame({
                "Open": open_daily,
                "High": high_daily,
                "Low" : low_daily,
                "Close": close_daily,
                "MDate": daily_index 
    })

    # Calculate the pivot points on the daily 
    ohlc_daily["PP"] = (ohlc_daily["High"] + ohlc_daily["Low"] + ohlc_daily["Close"])/3

    ohlc_daily["R1"] = ohlc_daily["PP"]*2 - ohlc_daily["Low"]
    ohlc_daily["S1"] = ohlc_daily["PP"]*2 - ohlc_daily["High"]
    
    ohlc_daily["R2"] = ohlc_daily["PP"] + (ohlc_daily["High"] - ohlc_daily["Low"])
    ohlc_daily["S2"] = ohlc_daily["PP"] - (ohlc_daily["High"] - ohlc_daily["Low"])

    # Shift the Pivot Points
    ohlc_daily["PP"] = ohlc_daily["PP"].shift(1)
    ohlc_daily["R1"] = ohlc_daily["R1"].shift(1)
    ohlc_daily["S1"] = ohlc_daily["S1"].shift(1)
    ohlc_daily["R2"] = ohlc_daily["R2"].shift(1)
    ohlc_daily["S2"] = ohlc_daily["S2"].shift(1)

    # Subset and get the Pivot points
    ohlc_daily = ohlc_daily[["MDate", "PP", "S1", "S2", "R1", "R2"]]

    # Merge the intra day and daily pivot point data
    ohlc_merged = ohlc.merge(ohlc_daily, left_on="MDate", right_on="MDate")
    ohlc_merged.set_index(ohlc.index, inplace=True)
    
    # Drop missing info
    ohlc_merged.dropna(inplace=True)
  
    # Calculate the patterns
    patterns  = ohlc_merged.ta.cdl_pattern(name=["harami"])

    ohlc_merged["harami"] = patterns["CDL_HARAMI"] 

    ohlc_merged.loc[:,"bullish_close"] = np.where(ohlc_merged["harami"]==100,ohlc_merged["Close"],np.nan) 
    ohlc_merged.loc[:,"bearish_close"] = np.where(ohlc_merged["harami"]==-100,ohlc_merged["Close"],np.nan)

    # Signal conditions
    buy_conditions  = (ohlc_merged["bullish_close"] <  ohlc_merged["S2"]) & (ohlc_merged["harami"]==100)
    sell_conditions = (ohlc_merged["bearish_close"] >  ohlc_merged["R2"]) & (ohlc_merged["harami"]==-100)

    # Signal Points
    ohlc_merged.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc_merged.loc[:,"sell"] = np.where(sell_conditions,1,0)  

    # ===============
    # Run backtest 
    #================

    # Simple candlestick backtest
    run_backtest(ohlc_merged, SimpleStrategy, strategy_name=strategy_name) 




def main():
    """
    Main function
    """

    strategy_name = f"{CANDLESTICK}-candlestick"

    # Read in the data
    ohlc  = read_data()

    # Calculate the patterns
    patterns  = ohlc.ta.cdl_pattern(name=["harami"])

    # Signal position points (i.e. for plotting)
    buy_conditions  = (patterns["CDL_HARAMI"]==100)
    sell_conditions = (patterns["CDL_HARAMI"]==-100)

    # Signal Points
    ohlc.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc.loc[:,"sell"] = np.where(sell_conditions,1,0)  


    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name) 

    # Version 1 with pivot point
    candlestick_pivot_point_1()

    # Version 2 with pivot point
    candlestick_pivot_point_2()

if __name__ == "__main__":
    main()
    
    