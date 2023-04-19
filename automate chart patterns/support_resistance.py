"""
Date: 2023-04-14

Support and resistance

This code is based on the following Youtube video: https://www.youtube.com/watch?v=Mxk8PP3vbuA
"""

from mplfinance.original_flavor import candlestick_ohlc

import glob
import pandas as pd
import os
import sys

import matplotlib.pyplot as plt 
import matplotlib.dates as mpdates

plt.style.use('seaborn-darkgrid')

def support(ohlc, l, n1, n2):
    """
    Calculate the support level

    :params ohlc is a dataframe

    :params l is the l'th row

    :params n1 is the number of candles to the left

    :params n2 is the number of candles to the right

    :return boolean  
    """
    
    for i in range(l-n1+1, l+1):
        try:
            if(ohlc.loc[i,"Low"] > ohlc.loc[i-1,"Low"]):
                return 0
        except:
            return 0
    for i in range(l+1,l+n2+1):
        try:
            if(ohlc.loc[i,"Low"] < ohlc.loc[i-1,"Low"]):
                return 0
        except:
            return 0
    return 1



def resistance(ohlc, l, n1, n2):
    """
    Calculate the resistance level

    :params ohlc is a dataframe

    :params l is the l'th row

    :params n1 is the number of candles to the left

    :params n2 is the number of candles to the right

    :return boolean  
    """

    for i in range(l-n1+1, l+1):
        try:
            if(ohlc.loc[i, "High"] < ohlc.loc[i-1, "High"] ):
                return 0
        except:
            return 0 

    for i in range(l+1,l+n2+1):
        try:
            if(ohlc.loc[i, "High"] > ohlc.loc[i-1, "High"]):
                return 0
        except:
            return 0
    return 1

def find_support_and_resistance(ohlc: pd.DataFrame,n1: int, n2: int, skip_next: int = 10) -> pd.DataFrame:
    """
    Find the index points of both the support and resistance lines

    :params ohlc is a dataframe
    :type :pd.DataFrame

    :params n1 is the number of candles to the left
    :type :int

    :params n2 is the number of candles to the right
    :type :int

    :params skip_next - Number of bars to skip after finding a resistance or support point. Default = 10.
    :type :int 

    :returns ohlc
    """

    l=0
    while l < len(ohlc):
        if l > n1+n2 and l < len(ohlc) - n1 -n2:
            if support(ohlc, l, n1, n2):
                ohlc.loc[l, "Support"] = round(ohlc.loc[l, "Low"],4)
                ohlc.loc[l, "SupportIndex"] = l 
                # print(f"Found support at {ohlc['Date'][l]} which is index {l}") #debugging
                l+=skip_next
                continue   

            if resistance(ohlc, l, n1, n2):
                ohlc.loc[l, "Resistance"] = round(ohlc.loc[l, "High"],4)
                ohlc.loc[l, "ResistanceIndex"] = l 
                # print(f"Found resistance at {ohlc['Date'][l]} which is index {l}")
                l+=skip_next
                continue 
        l+=1

    return ohlc 


def find_best_pair(ohlc: pd.DataFrame):
    """
    Find the best support and resistance pair based on the least distance on index position

    :params ohlc is a dataframe
    :type :pd.DataFrame


    """

    sup_arr = ohlc["SupportIndex"].unique()
    res_arr = ohlc["ResistanceIndex"].unique()

    res_idx = 0
    sup_idx = 0
    
    old_dis = 9999

    for i in sup_arr:
        if i ==0:
            continue

        for j in res_arr:
            if j ==0:
                continue

            min_dis=abs(i-j)
            if min_dis< old_dis:
                old_dis=min_dis
                res_idx = j
                sup_idx = i 

    return res_idx, sup_idx


def plot(ohlc: pd.DataFrame):
    """
    Plot the support and resistance lines
    
    :params ohlc is a dataframe
    :type :pd.DataFrame

    """

    n = len(ohlc) - 5

    fig, ax = plt.subplots(figsize=(15,7))

    candlestick_ohlc(ax, ohlc.loc[:, ["Date","Open", "High", "Low", "Close"] ].values, width=0.8, colorup='green', colordown='red', alpha=0.8)

    # Draw the support levels
    ax.hlines(xmin=ohlc['Date'][sup_idx], y=ohlc.loc[sup_idx, "Support"], xmax= ohlc['Date'][n], color="purple")

    # Draw the resistance levels
    ax.hlines(xmin=ohlc['Date'][res_idx], y=ohlc.loc[res_idx, "Resistance"], xmax= ohlc['Date'][n], color='purple')



    ax.grid(True)
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')

    date_format  = mpdates.DateFormatter('%Y-%m-%d')
    ax.xaxis.set_major_formatter(date_format)


    plt.show()


def save_plot(ohlc: pd.DataFrame, point: int) -> None:
    """
    Save the plot 

    :params ohlc is a dataframe
    :type :pd.DataFrame

    :params point - Save point
    :type :int
    """

    dir_ = os.path.realpath('').split("research")[0]

    # Prepare the data
    ohlc = ohlc.copy()
    ohlc.loc[:,"Index"] = ohlc.index
    n = len(ohlc) - 5


    # Move the y-axis to the right hand side. 
    plt.rcParams['ytick.right'] = plt.rcParams['ytick.labelright'] = True
    plt.rcParams['ytick.left'] = plt.rcParams['ytick.labelleft'] = False



    fig, ax = plt.subplots(figsize=(15,7), facecolor='#000000')
  
    candlestick_ohlc(ax, ohlc.loc[:, ["Index","Open", "High", "Low", "Close"] ].values, colorup='green', colordown='red', alpha=0.8)



    # Draw the support levels
    ax.hlines(xmin=ohlc['Index'][sup_idx], y=ohlc.loc[sup_idx, "Support"], xmax= ohlc['Index'][n], color="purple", linewidth=12)

    # Draw the resistance levels
    ax.hlines(xmin=ohlc['Index'][res_idx], y=ohlc.loc[res_idx, "Resistance"], xmax= ohlc['Index'][n], color='purple', linewidth=12)

    # Color the ticks white
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    

    ax.set_facecolor('#000000')

    ax.grid(False)
    ax.set_xlabel('Index')
    # ax.set_ylabel('Price')

    # date_format  = mpdates.DateFormatter('%Y-%m-%d')
    # ax.xaxis.set_major_formatter(date_format)

    fn   = f"rectangle-{point}.png"
    file = os.path.join( dir_,'images','analysis',fn)
    plt.savefig(file, format="png")



if __name__ == "__main__":
    
    dir_ = os.path.realpath('').split("research")[0]
    file = os.path.join( dir_,'data', 'eurusd-4h.csv') 
    df = pd.read_csv(file)

    # Remove all non-trading periods
    df = df[df['Volume']!=0]
    df.reset_index(drop=True, inplace=True)

    ohlc         = df.loc[:, ["Date", "Open", "High", "Low", "Close"] ]
    ohlc["Date"] = pd.to_datetime(ohlc["Date"])
    ohlc["Date"] = ohlc["Date"].map(mpdates.date2num)

    ohlc["Support"]    = 0
    ohlc["Resistance"] = 0

    ohlc["SupportIndex"]  = 0
    ohlc["ResistanceIndex"] = 0

    # Skip the next bars once support or resistance line is found
    skip_next = 10

    # Overlapping, non-overlapping, all
    # print(len(ohlc))



    batch = 500
    start = 0
    end   = batch
    type_ = "non-rolling"
    while end < len(ohlc):
        
        ohlc_sub  = ohlc.loc[start:end,:]
        ohlc_sub.reset_index(inplace=True)

        n1    = 3
        n2    = 2

        # Find the support and resistance points
        ohlc_sub = find_support_and_resistance(ohlc_sub, n1, n2)

        # Support and resistance pairing with the least distance
        res_idx, sup_idx = find_best_pair(ohlc_sub)

        # Check if best pair was found
        if res_idx == 0 and sup_idx == 0:
            print(f"No support and resistance found. Increase the sample size or change n1 and/or n2 ")
        else:
            # Plot the OHLC data with the support and resistance
            #plot(ohlc)

            # Save the plot 
            save_plot(ohlc_sub, end)

        if type_ == "rolling":
            start +=1
            end   =start + batch 
        elif type_ == "non-rolling":
            start +=batch
            end   +=batch 
    
