"""
Date           : 2023-05-04
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video:
https://www.youtube.com/watch?v=ylPJoD25zhE&list=PL3Jd92exRxKTGkeWFT4V-z8Gu3svBJ6ap&index=18

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 
"""


import logging
import numpy as np
import os
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go 


from backtesting import Backtest, Strategy
from progress.bar import Bar
from typing import List 

# Own modules
from entry.entry import SimpleStrategy
from exits.exits import *
from utils.utils import plot_ohlc, get_trading_strategy, read_data, run_backtest



def plot_ohlc_pivots(ohlc: pd.DataFrame, filename: str = ""):
    """
    Plot the OHLC data and the Pivot points

    :params ohlc dataframe
    :type :pd.DataFrame

    :params filename for the saved image
    :type :str

    """

    ohlc_plot = ohlc.iloc[1000:1250,:]
    ohlc_plot.reset_index(drop=True, inplace=True)

    fig = go.Figure(data=[
          go.Candlestick(x=ohlc_plot.index,
          open = ohlc_plot["Open"],
          high = ohlc_plot["High"],
          low  = ohlc_plot["Low"],
          close= ohlc_plot["Close"],
          name = "OHLC")  
    ])

    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False, color="white"), yaxis=dict(showgrid=False, side="right", color="white"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01))


    fig.add_trace(go.Scatter(
        x=ohlc_plot.index,
        y=ohlc_plot.PP,
        marker=dict(color="orange", size=4),
        mode="markers",
        name ="PP"
    ))

    fig.add_trace(go.Scatter(
        x=ohlc_plot.index,
        y=ohlc_plot.S1,
        marker=dict(color="red", size=4),
        mode="markers",
        name ="S1"
    ))    

    fig.add_trace(go.Scatter(
        x=ohlc_plot.index,
        y=ohlc_plot.S2,
        marker=dict(color="red", size=4),
        mode="markers",
        name ="S2"
    )) 


    fig.add_trace(go.Scatter(
        x=ohlc_plot.index,
        y=ohlc_plot.R1,
        marker=dict(color="green", size=4),
        mode="markers",
        name ="R1"
    )) 

    fig.add_trace(go.Scatter(
        x=ohlc_plot.index,
        y=ohlc_plot.R2,
        marker=dict(color="green", size=4),
        mode="markers",
        name ="R2"
    ))     

    # fig.show()

    # Also save it in the docs folder (if its there)
    try:
        dir_book     = os.path.realpath('').split("code")[0]
        file_path    = os.path.join(dir_book,"book", "100-strategies", "_static","images", f"{filename}.png")
        fig.write_image(file_path)
    except Exception as e:
        pass


def main(show_plot=True):
    """
    This is the main function to run the analysis
    """

    strategy_name = "pivot-extension"
    # Read in the data
    ohlc_subset  = read_data()


    # Set the index 
    ohlc_subset["datetime"] = ohlc_subset["date"]
    ohlc_subset.set_index("datetime", inplace=True)
    ohlc_subset.sort_index(inplace=True)
    
    # Create a Date column that will be used in the merging
    intra_date = ohlc_subset.index.strftime('%Y-%m-%d')
    ohlc_subset["MDate"] = intra_date

    # Resample to daily data
    open_daily       = ohlc_subset["Open"].resample("D").first()
    close_daily      = ohlc_subset["Close"].resample("D").last()
    high_daily       = ohlc_subset["High"].resample("D").max()
    low_daily        = ohlc_subset["Low"].resample("D").min()

    daily_index =  ohlc_subset["Open"].resample("D").first().index.strftime('%Y-%m-%d')

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
    ohlc = ohlc_subset.merge(ohlc_daily, left_on="MDate", right_on="MDate")
    ohlc.set_index(ohlc_subset.index, inplace=True)

    # Drop missing info
    ohlc.dropna(inplace=True)
  
    # Plot the ohlc and the pivot points
    plot_ohlc_pivots(ohlc, filename=strategy_name)


    # Signal conditions
    buy_conditions = (ohlc["Low"] <  ohlc["S2"])
    sell_conditions = (ohlc["High"] >  ohlc["R2"]) 


    # # Signal Points
    ohlc.loc[:,"buy"] = np.where(buy_conditions,1,0)
    ohlc.loc[:,"sell"] = np.where(sell_conditions,1,0)  


    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name) 



if __name__ == "__main__":
    main()