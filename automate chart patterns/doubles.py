"""
Date 20230105

This progam implements the Doubles Chart Patterns

Source: https://alpaca.markets/learn/algorithmic-trading-chart-pattern-python/
        https://github.com/samchaaa/alpaca_tech_screener/blob/master/tech_screener_notebook.ipynb
"""

from mplfinance.original_flavor import candlestick_ohlc
from scipy.signal import argrelextrema

import matplotlib.dates as mpdates
import matplotlib.pyplot as plt 
import numpy as np
import os
import pandas as pd


plt.style.use('seaborn-darkgrid')

from collections import defaultdict


def save_plots(ohlc, patterns, max_min, filename):
    """
    Save the plots of the analysis

    :params ohlc -> dataframe holding the ohlc data

    :params paterns -> all the indices where the patterns exist

    :params max_min -> the maximas and minimas

    :params filename -> prefix for the graph names 
    """
    for i, pattern in enumerate(patterns):
        fig, ax  = plt.subplots(figsize=(15,7)) 
        start_   = pattern[0]
        end_     = pattern[1]
        idx      = max_min.loc[start_-100:end_+100].index.values.tolist()
        ohlc_copy = ohlc.copy()
        ohlc_copy.loc[:,"Index"] = ohlc_copy.index

        max_min_idx = max_min.loc[start_:end_].index.tolist()

        candlestick_ohlc(ax, ohlc_copy.loc[idx, ["Index","Open", "High", "Low", "Close"] ].values, width=0.1, colorup='green', colordown='red', alpha=0.8)   
        ax.plot(max_min_idx, max_min.loc[start_:end_].values[:,1],color='orange')


        ax.grid(True)
        ax.set_xlabel('Index')
        ax.set_ylabel('Price')

        # Create the save folder if it does not exist
        if not os.path.exists(os.path.join(dir_,"images","analysis")):

                os.mkdir(os.path.join(dir_,"images","analysis"))


        fn = f"{filename}-{i}.png"
        file = os.path.join( dir_,'images','analysis',fn)
        plt.savefig(file, format="png")

        
        print(f"Completed {round((i+1)/len(patterns),2)*100}%")

    return 


def find_doubles_patterns(max_min):
    """
    Find the the double tops and bottoms patterns

    :params max_min -> the maximas and minimas

    :return patterns_tops, patterns_bottoms
    """
    
    # Placeholders for the Double Tops and Bottoms indices
    patterns_tops = []
    patterns_bottoms = []

    # Window range is 5 units
    for i in range(5, len(max_min)):  
        window = max_min.iloc[i-5:i]
        
        
        # Pattern must play out in less than n units
        if window.index[-1] - window.index[0] > 50:      
            continue   
            
        a, b, c, d, e = window.iloc[0:5,1]
        # Double Tops
        if a<b and a<d and c<b and c<d and e<b and e<d and b>d :
               patterns_tops.append((window.index[0], window.index[-1]))

        # Double Bottoms
        if a>b and a>d and c>b and c>d and e>b and e>d and b<d:
                patterns_bottoms.append((window.index[0], window.index[-1]))

    return patterns_tops, patterns_bottoms


def find_local_maximas_minimas(ohlc, window_range, smooth=False, smoothing_period=10):
    """
    Find all the local maximas and minimas

    :params ohlc         -> dataframe holding the ohlc data
    :params window_range -> range to find min and max
    :params smooth       -> should the prices be smoothed
    :params smoothing_period -> the smoothing period

    :return max_min
    """
    local_max_arr = []
    local_min_arr = []

    if smooth:
        smooth_close = ohlc["Close"].rolling(window=smoothing_period).mean().dropna()
        local_max = argrelextrema(smooth_close.values, np.greater)[0]
        local_min = argrelextrema(smooth_close.values, np.less)[0]   
    else:
        local_max = argrelextrema(ohlc["Close"].values, np.greater)[0]
        local_min = argrelextrema(ohlc["Close"].values, np.less)[0]   

    for i in local_max:
        if (i>window_range) and (i<len(ohlc)-window_range):
            local_max_arr.append(ohlc.iloc[i-window_range:i+window_range]['Close'].idxmax())
   
    for i in local_min:
        if (i>window_range) and (i<len(ohlc)-window_range):
            local_min_arr.append(ohlc.iloc[i-window_range:i+window_range]['Close'].idxmin())  


    maxima  = pd.DataFrame(ohlc.loc[local_max_arr])
    minima  = pd.DataFrame(ohlc.loc[local_min_arr])
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min = max_min[~max_min.index.duplicated()]

    return max_min


if __name__ == "__main__":
    dir_ = os.path.realpath('').split("research")[0]
    file = os.path.join( dir_,'data','eurusd-4h.csv') 
    df = pd.read_csv(file)

    ohlc = df.loc[:, ["Date", "Open", "High", "Low", "Close"] ]
    
    ohlc["Date"] = pd.to_datetime(ohlc["Date"], format="%d.%m.%Y %H:%M:%S.%f")
    ohlc["Date"] = ohlc["Date"].map(mpdates.date2num)
      
    
    # Find all the local minimas and maximas
    window_range = 10 # Defining the local range where min and max will be found
    max_min = find_local_maximas_minimas(ohlc, window_range, smooth=True)

    # Find the tops and bottoms
    patterns_tops, patterns_bottoms = find_doubles_patterns(max_min)
   
    # Plots for Double Tops
    print("Plotting the Double Tops")
    save_plots(ohlc, patterns_tops, max_min, "double-tops")


    # Plots for Double Bottoms
    print("Plotting the Double Bottoms")
    save_plots(ohlc, patterns_bottoms, max_min, "double-bottoms")



 

        

