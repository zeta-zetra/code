"""
This file programs different ways of capturing a retracement 

Source: https://www.youtube.com/watch?v=3rmw0UFgYmQ  
Date  : 2023-07-19
"""

import glob
import numpy as np 
import os 
import pandas as pd 
import plotly.graph_objects as go

from progress.bar import Bar
from typing import Union

def retracement_conditions(df: pd.DataFrame, condition: str="distance", zone_threshold: float=0.001, price_diff_threshold: float=0.001) -> pd.DataFrame:
    """
    Set the conditions for what one considers a `true` retracement
    
    :params df is the OHLC data plus the pivot columns
    :type :pd.DataFrame
    
    :params condition is the type of conditions to use to mark a retracement. Options ["distance", "fibonacci"]
    :type :str 
    
    :params zone_threshold is used for the Fibonacci retracement condition
    :type :float 
    
    :params price_diff_threshold is used for the Fibonacci retracement condition
    :type :float
    
    :return: (pd.DataFrame)
    """

    if condition == "distance":
        conditions = [(df.pivot_index_high > df.pivot_index_low) & (df.index_close < df.pivot_high) & (df.index_close > df.pivot_low) & 0.5*abs(df.pivot_index_high - df.pivot_index_low) >= abs(df.pivot_high - df.index_close), 
                (df.pivot_index_high < df.pivot_index_low) & (df.index_close > df.pivot_low) & (df.index_close < df.pivot_high) & 0.5*abs(df.pivot_index_high - df.pivot_index_low) >= abs(df.pivot_low - df.index_close)]
    elif condition == "fibonacci":
        
        df["s1"] = df.pivot_high - 0.62*(df.pivot_high - df.pivot_low) 
        df["r1"] = df.pivot_low  + 0.62*(df.pivot_high - df.pivot_low) 
        df["pivot_diff"] = df.pivot_high - df.pivot_low 

        conditions = [( df["pivot_diff"] >  price_diff_threshold) & (df.pivot_index_high > df.pivot_index_low) & ( abs(df.index_close - df["s1"]) < zone_threshold ),
                      ( df["pivot_diff"] >  price_diff_threshold) & (df.pivot_index_high < df.pivot_index_low) & ( abs(df.index_close - df["r1"]) < zone_threshold )] 
    
    choices    = [-1, 1]
    df["retracement"] = np.select(conditions, choices, np.nan)
    
    return df 

def calculate_pivot_points(df: pd.DataFrame, lookback: int) -> pd.DataFrame:
    """
    Calculate the Pivot Points 
    
    :params df is the OHLC data 
    :type :pd.DataFrame
    
    :params lookback is the number of bars to use to calculate the pivot points
    :type :int 
    
    :return: (pd.DataFrame)
    """
    
    df["pivot_high"]   = np.nan 
    df["pivot_low"]    = np.nan 
    bar = Bar("Calculating the pivot points...", max=len(df))
    for idx in range(lookback, len(df)):
        df.loc[idx,"pivot_high"]       = df.loc[idx-lookback:idx, "high"].max()
        df.loc[idx,"pivot_index_high"] = df.loc[idx-lookback:idx, "high"].idxmax()

        df.loc[idx,"pivot_low"]       = df.loc[idx-lookback:idx, "low"].min()
        df.loc[idx,"pivot_index_low"] = df.loc[idx-lookback:idx, "low"].idxmin()
        df.loc[idx, "index_close"]    = df.loc[idx,"close"] 
        bar.next()
        
    bar.finish()
    return df 


def display_plot(df: pd.DataFrame, point: int, save: bool=False):
    """
    Display or save the retracement point
    
    :params df is the data
    :type :pd.DataFrame
    
    :params point is the retracement point 
    :type :int 
    
    :params save is to save the plot as a png file
    :type :bool 
    """
    fig = go.Figure(data=[go.Candlestick(
                x    = df.index,
                open  = df.close,
                high  = df.high,
                low   = df.low,
                close = df.close, name="OHLC"    
        )])

    fig.add_scatter(
        x=[df.iloc[-1].pivot_index_high],
        y=[df.iloc[-1].pivot_high],
        mode="markers", marker=dict(size=20, color="green"), name="Pivot High"
    )

    fig.add_scatter(
        x=[df.iloc[-1].pivot_index_low],
        y=[df.iloc[-1].pivot_low],
        mode="markers", marker=dict(size=20, color="red"), name="Pivot Low"
    )

    fig.add_scatter(
        x=[point],
        y=[df.loc[point,"index_close"]],
        mode="markers", marker=dict(size=20, color="purple"), name="Retracement Point"
    )
        
    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                    xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, side="right"), legend_font_color="white",
                    legend=dict(yanchor="bottom", y=0.99, xanchor="left", x=0.01) )

    fig.update_traces(increasing_fillcolor="#3D9970", selector=dict(type='candlestick'))
    fig.update_traces(decreasing_fillcolor="#FF4136", selector=dict(type='candlestick'))

    fig.update_xaxes(color='white') 
    fig.update_yaxes(color='white')        
    
    if save:
        file_image =os.path.join("results",f"{point}.png")
        
        fig.write_image(file_image)
    else:
        fig.show()

def plot_retracement_point(df: pd.DataFrame, point_of_interest: Union[int, None] = None, all_points: bool = False):
    """
    Plot the retracement for the given point, if it is one
    
    :params df is the OHLC data with the retracement data
    :type :pd.DataFrame
    
    :params point_of_interest is the retracement point
    :type :int 
    
    :params all_points of retracements have to be plotted and saved? 
    :type :bool
    """
    
    try:
        
        if point_of_interest and not all_points:
            # Get the indices of the pivot high and low
            idx_high = int(df.iloc[point_of_interest].pivot_index_high)
            idx_low  = int(df.iloc[point_of_interest].pivot_index_low)
            
            # Subset the data based on the lowest index between the pivot high and low
            if idx_high < idx_low:
                df = df.iloc[idx_high-2:point_of_interest+1]
            else:
                df = df.iloc[idx_low-2:point_of_interest+1]


            display_plot(df, point_of_interest)

        elif all_points:
            
            # Create the results folder
            if not os.path.exists("results"):
                os.mkdir("results")
            else:
                # Remove previous results if any found!
                pngs = glob.glob(os.path.join("results","*.png"))
                for png in pngs:
                    os.remove(png)
                print("Removed all previous results")
                
            bar = Bar("Saving the images...", max=len(df))
            for row in df.iterrows():
                if row[1]["retracement"] == 1 or row[1]["retracement"] == -1:
                                # Get the indices of the pivot high and low
                    idx_high = int(df.iloc[row[0]].pivot_index_high)
                    idx_low  = int(df.iloc[row[0]].pivot_index_low)
                    
                    # Subset the data based on the lowest index between the pivot high and low
                    if idx_high < idx_low:
                        df_copy = df.iloc[idx_high-2:row[0]+1]
                    else:
                        df_copy = df.iloc[idx_low-2:row[0]+1]

                    display_plot(df_copy, row[0], save=True)
                bar.next()
            bar.finish()    
                    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    df = pd.read_csv("data/sample.csv")

    lookback          = 25
    df = calculate_pivot_points(df, lookback)
   
    df = retracement_conditions(df, condition="distance")
    
    plot_retracement_point(df, all_points=True)