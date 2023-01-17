"""
Date 20230107

This progam implements the Flag Chart Patterns
"""

from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mpdates
import matplotlib.pyplot as plt 
import numpy as np
import os
import pandas as pd
from scipy.stats import linregress

plt.style.use('seaborn-darkgrid')

def pivot_id(ohlc, l, n1, n2):
    """
    Get the pivot id 

    :params ohlc is a dataframe
    :params l is the l'th row
    :params n1 is the number of candles to the left
    :params n2 is the number of candles to the right
    :return int  
    """

    # Check if the length conditions met
    if l-n1 < 0 or l+n2 >= len(ohlc):
        return 0
    
    pivot_low  = 1
    pivot_high = 1

    for i in range(l-n1, l+n2+1):
        if(ohlc.loc[l,"Low"] > ohlc.loc[i, "Low"]):
            pivot_low = 0

        if(ohlc.loc[l, "High"] < ohlc.loc[i, "High"]):
            pivot_high = 0

    if pivot_low and pivot_high:
        return 3

    elif pivot_low:
        return 1

    elif pivot_high:
        return 2
    else:
        return 0


def pivot_point_position(row):
    """
    Get the Pivot Point position and assign the Low or High value

    :params row -> row of the ohlc dataframe
    :return float
    """
   
    if row['Pivot']==1:
        return row['Low']-1e-3
    elif row['Pivot']==2:
        return row['High']+1e-3
    else:
        return np.nan


def find_flag_points(ohlc, back_candles):
    """
    Find flag points

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
                minim = np.append(minim, ohlc.loc[i, "Low"])
                xxmin = np.append(xxmin, i) 
            if ohlc.loc[i,"Pivot"] == 2:
                maxim = np.append(maxim, ohlc.loc[i,"High"])
                xxmax = np.append(xxmax, i)

        
        if (xxmax.size <3 and xxmin.size <3) or xxmax.size==0 or xxmin.size==0:
        
            continue

           
        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)
  
        # Check if the lines are parallel 
        if abs(rmax)>=0.9 and abs(rmin)>=0.9 and (slmin>=1e-3 and slmax>=1e-3 ) or (slmin<=-1e-3 and slmax<=-1e-3):
                        if (slmin/slmax > 0.9 and slmin/slmax < 1.05): # The slopes are almost equal to each other

                            all_points.append(candle_idx)
                            

    return all_points


def save_plot(ohlc, all_points, back_candles):
    """
    Save all the flag graphs

    :params ohlc         -> dataframe that has OHLC data
    :params all_points   -> flag points
    :params back_candles -> number of periods to lookback
    :return 
    """

    total = len(all_points)
    for j, point in enumerate(all_points):

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])

       
        for i in range(point-back_candles, point+1):
            if ohlc.loc[i,"Pivot"] == 1:
                minim = np.append(minim, ohlc.loc[i, "Low"])
                xxmin = np.append(xxmin, i) 
                
            if ohlc.loc[i,"Pivot"] == 2:
                maxim = np.append(maxim, ohlc.loc[i,"High"])
                xxmax = np.append(xxmax, i)

        idx     = range(point-back_candles-5,point-back_candles)
        xslope  = np.array([])
        values  = np.array([])

        for i in idx:
            xslope = np.append(xslope,i)
            values = np.append(values, ohlc.loc[i,"Close"])


        # Linear regressions
        sl, interm, r, p, se = linregress(xslope, values)
        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)

        xxmin = np.append(xxmin, xxmin[-1]) 
        xxmax = np.append(xxmax, xxmax[-1])



        ohlc_subset = ohlc[point-back_candles-5:point+back_candles+5]
        ohlc_subset_copy = ohlc_subset.copy()
        ohlc_subset_copy.loc[:,"Index"] = ohlc_subset_copy.index
        
 

        xxmin = np.append(xxmin, xxmin[-1]+15)
        xxmax = np.append(xxmax, xxmax[-1]+15)


    
        # Make the plot
        fig, ax = plt.subplots(figsize=(15,7))

        
        candlestick_ohlc(ax, ohlc_subset_copy.loc[:, ["Index","Open", "High", "Low", "Close"] ].values, width=0.6, colorup='green', colordown='red', alpha=0.8)

       
        ax.plot(xxmin, xxmin*slmin + intercmin)
        ax.plot(xxmax, xxmax*slmax + intercmax)
        ax.plot(xslope, sl*xslope + interm, color="magenta", linewidth=3)
        ax.annotate(' ', xy=(point,ohlc_subset_copy.loc[point,"High"]), arrowprops=dict(width=9, headlength = 14, headwidth=14, facecolor='purple', color='purple') )

        ax.grid(True)
        ax.set_xlabel('Index')
        ax.set_ylabel('Price')

        
        if sl < 0 and slmin > 0 and slmax > 0:
            name= f"potential-bearish-{point}"
        elif sl >0 and slmin <0 and slmax <0:
            name= f"potential-bullish-{point}"
        else:
            name = f"{point}"
       
        fn = f"flag-{name}.png"
        file = os.path.join( dir_,'images','analysis',fn)
        plt.savefig(file, format="png")
        print(f"Completed {round((j+1)/total,2)*100}%")

    return

if __name__ == "__main__":
    dir_ = os.path.realpath('').split("research")[0]
    file = os.path.join( dir_,'data','eurusd-4h.csv') 
    df   = pd.read_csv(file)

    # Remove all non-trading periods
    df = df[df['Volume']!=0]
    df.reset_index(drop=True, inplace=True)

    ohlc         = df.loc[:, ["Date", "Open", "High", "Low", "Close"] ]
    format       = '%d.%m.%Y %H:%M:%S.%f' 
    ohlc["Date"] = pd.to_datetime(ohlc["Date"], format=format)
    ohlc["Date"] = ohlc["Date"].map(mpdates.date2num)

    ohlc["Pivot"] = 0


    # Get the minimas and maximas 
    ohlc["Pivot"]    = ohlc.apply(lambda x: pivot_id(ohlc, x.name, 3, 3), axis=1)
    ohlc['PointPos'] = ohlc.apply(lambda row: pivot_point_position(row), axis=1)


    # Find all flag pattern points
    back_candles = 20
    all_points = find_flag_points(ohlc, back_candles)

    # Plot the flag pattern graphs
    save_plot(ohlc, all_points, back_candles)
