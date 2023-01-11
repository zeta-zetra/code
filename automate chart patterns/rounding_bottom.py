"""
Date 20230105

This program implements the Rounding Bottom Chart Patterns

"""

from mplfinance.original_flavor import candlestick_ohlc
from scipy.signal import argrelextrema

import matplotlib.dates as mpdates
import matplotlib.pyplot as plt 
import numpy as np
import os
import pandas as pd


plt.style.use('seaborn-darkgrid')


def find_rounding_bottom_points(ohlc, back_candles):
    """
    Find all the rounding bottom points

    :params ohlc         -> dataframe that has OHLC data
    :params back_candles -> number of periods to lookback
    :return all_points 
    """
    all_points = []
    for candle_idx in range(back_candles+10, len(ohlc)):

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

        for i in range(candle_idx-back_candles, candle_idx+1):
            if ohlc.loc[i,"Pivot"] == 1:
                minim = np.append(minim, ohlc.loc[i, "Close"])
                xxmin = np.append(xxmin, i) 
            if ohlc.loc[i,"Pivot"] == 2:
                maxim = np.append(maxim, ohlc.loc[i,"Close"])
                xxmax = np.append(xxmax, i)

        
        if (xxmax.size <3 and xxmin.size <3) or xxmax.size==0 or xxmin.size==0:
            continue

        # Fit a nonlinear line: ax^2 + bx + c        
        z = np.polyfit(xxmin, minim, 2)

        # Check if the first and second derivatives are for a parabolic function
        if 2*xxmin[0]*z[0] + z[1]*xxmin[0] < 0 and 2*z[0] > 0:
             if z[0] >=2.19388889e-04 and z[1]<=-3.52871667e-02:          
                    all_points.append(candle_idx)
                                    

    return all_points


def save_plot(ohlc, all_points, back_candles):
    """
    Save all the rounding bottoms graphs

    :params ohlc         -> dataframe that has OHLC data
    :params all_points   -> rounding bottom points
    :params back_candles -> number of periods to lookback
    :return 
    """
    total = len(all_points)
    for j, point in enumerate(all_points):
        candleid = point

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

        for i in range(point-back_candles, point+1):
            if ohlc.loc[i,"Pivot"] == 1:
                minim = np.append(minim, ohlc.loc[i, "Close"])
                xxmin = np.append(xxmin, i) 
            if ohlc.loc[i,"Pivot"] == 2:
                maxim = np.append(maxim, ohlc.loc[i,"Close"])
                xxmax = np.append(xxmax, i)
                

        z = np.polyfit(xxmin, minim, 2)
        f = np.poly1d(z)
        
        ohlc_subset = ohlc[point-back_candles-10:point+back_candles+10]
        
        xxmin = np.insert(xxmin,0,xxmin[0]-3)    
        xxmin = np.append(xxmin, xxmin[-1]+3)
        minim_new = f(xxmin)
      
        ohlc_subset_copy = ohlc_subset.copy()
        ohlc_subset_copy.loc[:,"Index"] = ohlc_subset_copy.index

        fig, ax = plt.subplots(figsize=(15,7))

        candlestick_ohlc(ax, ohlc_subset_copy.loc[:, ["Index","Open", "High", "Low", "Close"] ].values, width=0.6, colorup='green', colordown='red', alpha=0.8)
        ax.plot(xxmin, minim_new)

        ax.grid(True)
        ax.set_xlabel('Index')
        ax.set_ylabel('Price')


        fn = f"rounding-bottom-{point}.png"
        file = os.path.join( dir_,'images','analysis',fn)
        plt.savefig(file, format="png")
        
        print(f"Completed {round((j+1)/total,2)*100}%")

    return

if __name__ == "__main__":
    dir_ = os.path.realpath('').split("research")[0]
    file = os.path.join( dir_,'data','eurusd-4h.csv') 
    df = pd.read_csv(file)

    # Remove all non-trading periods
    df=df[df['Volume']!=0]
    df.reset_index(drop=True, inplace=True)


    ohlc = df.loc[:, ["Date", "Open", "High", "Low", "Close"] ]
    ohlc["Date"] = pd.to_datetime(ohlc["Date"])
    ohlc["Date"] = ohlc["Date"].map(mpdates.date2num)

    ohlc["Pivot"] = 0


    # Get the minimas and maximas 
    local_max = argrelextrema(ohlc["Close"].values, np.greater)[0]
    local_min = argrelextrema(ohlc["Close"].values, np.less)[0]   

    # Set max points to `2` 
    for m in local_max:
        ohlc.loc[m, "Pivot"] = 2
        
    # Set min points to `1`
    for m in local_min:
        ohlc.loc[m, "Pivot"] = 1

    
    # Find all the rounding bottom points
    back_candles = 20
    all_points = find_rounding_bottom_points(ohlc, back_candles)


    # Save all the plots
    save_plot(ohlc, all_points,back_candles)


        

