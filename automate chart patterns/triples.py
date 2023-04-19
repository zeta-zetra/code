"""
Date 20230119

This scripts get the Triple Top and Bottom Chart Patterns
Source: https://www.youtube.com/watch?v=Mxk8PP3vbuA
"""

import mplfinance as mpf 
import glob
import matplotlib.pyplot as plt 
import numpy as np
import os
import pandas as pd

from progress.bar import Bar
from scipy.stats import linregress


plt.style.use('seaborn-darkgrid')



def pivot_id(ohlc, l, n1, n2):
    """
    Get the pivot id 

    :params ohlc is a dataframe

    :params l is the l'th row

    :params n1 is the number of candles to the left

    :params n2 is the number of candles to the right

    :return boolean  
    """
    
    # Check if the length conditions met
    if l-n1 < 0 or l+n2 >= len(ohlc):
        return 0
    
    pivot_low  = 1
    pivot_high = 1

    bar = Bar(f'Processing pivot for n1:{n1} and n2:{n2}', max=len(range(l-n1, l+n2+1)))
   
    for i in range(l-n1, l+n2+1):
        if(ohlc.loc[l,"Low"] > ohlc.loc[i, "Low"]):
            pivot_low = 0

        if(ohlc.loc[l, "High"] < ohlc.loc[i, "High"]):
            pivot_high = 0
            
        bar.next()

    bar.finish()
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
    Get the Pivot Point position

    :params row of the ohlc dataframe
    """
   
    if row['Pivot']==1:
        return row['Low']-1e-3
    elif row['Pivot']==2:
        return row['Low']+1e-3
    else:
        return np.nan


def _find_points(df, candle_id, back_candles):
    """
    Find points provides all the necessary arrays and data of interest

    :params df        -> DataFrame with OHLC data
    :params candle_id -> current candle
    :params back_candles -> lookback period
    :return maxim, minim, xxmax, xxmin, maxacount, minacount, maxbcount, minbcount
    """

    maxim = np.array([])
    minim = np.array([])
    xxmin = np.array([])
    xxmax = np.array([])
    minbcount=0 #minimas before head
    maxbcount=0 #maximas before head
    minacount=0 #minimas after head
    maxacount=0 #maximas after head
    
    for i in range(candle_id-back_candles, candle_id+back_candles):
        if df.loc[i,"ShortPivot"] == 1:
            minim = np.append(minim, df.loc[i, "Low"])
            xxmin = np.append(xxmin, i)        
            if i < candle_id:
                minbcount=+1
            elif i>candle_id:
                minacount+=1
        if df.loc[i, "ShortPivot"] == 2:
            maxim = np.append(maxim, df.loc[i, "High"])
            xxmax = np.append(xxmax, i)
            if i < candle_id:
                maxbcount+=1
            elif i>candle_id:
                maxacount+=1
    


    return maxim, minim, xxmax, xxmin, maxacount, minacount, maxbcount, minbcount

def find_triple_bottoms(df, back_candles=14):
    """
    Find all triple bottom chart patterns
    
    :params df -> an ohlc dataframe that has "ShortPivot" and "Pivot" as columns
    :params back_candles -> Look-back and look-forward period
    :returns all_points    
    """
    all_points = []
    bar = Bar(f'Finding Triple Bottoms', max=len(range(back_candles+20, len(df)-back_candles)))
    for candle_id in range(back_candles+20, len(df)-back_candles):



        maxim, minim, xxmax, xxmin, maxacount, minacount, maxbcount, minbcount = _find_points(df,candle_id, back_candles)

        if minbcount<1 or minacount<1 or maxbcount<1 or maxacount<1:
                continue

        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)
        headidx     = np.argmin(minim, axis=0)  
       
        try:
            if xxmax[0]>xxmin[headidx-1] and xxmax[1]>xxmin[headidx] and xxmax[1]<xxmin[headidx+1] \
                and xxmax[2] > xxmin[headidx+1]  and abs(minim[headidx-1] - minim[headidx]) <1e-3 \
                and abs(minim[headidx+1]-minim[headidx])<1e-3 and abs(slmin)>0 and abs(slmin)<=1e-4  : 

                        all_points.append(candle_id)       
        except:
            pass    
        
        bar.next()
    bar.finish()
    return all_points


def find_triple_top(df, back_candles=14):
    """
    Find all Triple top chart patterns

    :params df -> an ohlc dataframe that has "ShortPivot" and "Pivot" as columns
    :params back_candles -> Look-back and look-forward period
    :returns all_points
    """
    all_points = []

    bar = Bar(f'Finding Triple Tops', max=len(range(back_candles+20, len(df)-back_candles)))
    for candle_id in range(back_candles+20, len(df)-back_candles):

        
        
        maxim, minim, xxmax, xxmin, maxacount, minacount, maxbcount, minbcount = _find_points(df,candle_id, back_candles)

        if minbcount<1 or minacount<1 or maxbcount<1 or maxacount<1:
            continue

        slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
        slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)
        headidx                             = np.argmax(maxim, axis=0)          
       
        try:
            if xxmin[0]>xxmax[headidx-1] and xxmin[1]>xxmax[headidx] and xxmin[1]>xxmax[headidx+1] \
               and abs(maxim[headidx-1] - maxim[headidx]) <1e-3 and abs(maxim[headidx+1]-maxim[headidx])<1e-3 and abs(slmax)>0 and abs(slmax)<=1e-4  : 

                        all_points.append(candle_id)


                 
        except:
            pass   
         
        bar.next()
    bar.finish()
    return all_points



def save_plot(ohlc, all_points, back_candles, fname="triple_tops", tt=True):
    """
    Save all the graphs

    :params ohlc         -> dataframe that has OHLC data
    :params all_points   -> points
    :params back_candles -> number of periods to lookback
    :params fname -> filename
    :params tt -> Is it a Triple Top?
    :return 
    """

    total = len(all_points)
    bar = Bar(f'Processing {fname} images', max=total)

    for j, point in enumerate(all_points):

        maxim = np.array([])
        minim = np.array([])
        xxmin = np.array([])
        xxmax = np.array([])
        ohlc["TR"] = np.nan
        try:
            for i in range(point-back_candles, point+back_candles):
                if ohlc.loc[i,"ShortPivot"] == 1:
                    minim = np.append(minim, ohlc.loc[i, "Low"])
                    xxmin = np.append(xxmin, i)        
                if ohlc.loc[i, "ShortPivot"] == 2:
                    maxim = np.append(maxim, ohlc.loc[i, "High"])
                    xxmax = np.append(xxmax, i)


            slmin, intercmin, rmin, pmin, semin = linregress(xxmin, minim)
            slmax, intercmax, rmax, pmax, semax = linregress(xxmax, maxim)
            
            if tt:
                headidx     = np.argmax(maxim, axis=0)  
                hsx = ohlc.loc[[xxmax[headidx-1],xxmin[0],xxmax[headidx],xxmin[1],xxmax[headidx+1] ],"Date"]
                hsy = [maxim[headidx-1], minim[0], maxim[headidx], minim[1], maxim[headidx+1]]
            else:
                headidx     = np.argmin(minim, axis=0)  
                hsx = ohlc.loc[[xxmin[headidx-1],xxmax[0],xxmin[headidx],xxmax[1],xxmin[headidx+1] ],"Date"]
                hsy = [minim[headidx-1], maxim[0], minim[headidx], maxim[1], minim[headidx+1]]          

            ohlc_copy = ohlc.copy()
            ohlc_copy.set_index("Date", inplace=True)
            levels = [(x,y) for x,y in zip(hsx,hsy)]

            for l in levels:
                ohlc_copy.loc[l[0].strftime("%Y-%m-%dT%H:%M:%S.%f"),"TR"] = l[1]



            ohlc_hs  = ohlc_copy.iloc[point-(back_candles+6):point+back_candles+6, : ]
            hs_l       = mpf.make_addplot(ohlc_hs["TR"], type="scatter", color='r', marker="v", markersize=200)
            fn       = f"{fname}-{point}.png"
            save_   = os.path.join( dir_,'images','analysis',fn)
            mpf.plot(ohlc_hs,
                    type='candle',
                    style='charles',
                    addplot=[hs_l],
                    alines=dict(alines=levels,colors=['purple'], alpha=0.5,linewidths=20),
                    savefig=f"{save_}"
                    )
        except:
            pass
        bar.next()
    
    bar.finish()
    return


if __name__ == "__main__":
    dir_ = os.path.realpath('').split("research")[0]
    file = os.path.join( dir_,'data','eurusd-4h.csv') 

    df = pd.read_csv(file)

    ohlc = df.loc[:, ["Date", "Open", "High", "Low", "Close"] ]
    ohlc["Date"] = pd.DatetimeIndex(ohlc["Date"]) 
  
    back_candles = 14
    ohlc["Pivot"] = ohlc.apply(lambda x: pivot_id(ohlc, x.name, 15, 15), axis=1)
    ohlc['ShortPivot'] = ohlc.apply(lambda x: pivot_id(df, x.name,5,5), axis=1)

    all_points = find_triple_top(ohlc, back_candles=14)
    # all_points_ = find_triple_bottoms(ohlc, back_candles=14)
    save_plot(ohlc, all_points, back_candles)
    # save_plot(ohlc, all_points_, back_candles, fname="triple_bottoms", tt=False)