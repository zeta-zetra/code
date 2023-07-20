"""
This file programs different ways of capturing a retracement 

Source: https://www.youtube.com/watch?v=3rmw0UFgYmQ  
Date  : 2023-07-19
"""

import glob
import numpy as np 
import os 
import pandas as pd 
import pandas_ta as ta 
import plotly.graph_objects as go

from progress.bar import Bar
from scipy.signal import argrelextrema
from typing import List,Tuple, Union



def find_pips(data: np.array, n_pips: int, dist_measure: int) -> Tuple[List[int],List[float]]:
    """
    Find the Perceptual Important Points
    
    :params data is the price array 
    :type :np.array
    
    :params n_pips is the number of points that needed to be extracted
    :type :int 
    
    :params dist_measure is the type of distance measure to use. Options: [1 = Euclidean Distance, 2 = Perpindicular Distance, 3 = Vertical Distance]
    :type :int
    
    :return: (Tuple[List[int],List[float]])
    """
    
    pips_x = [0, len(data) - 1]  # Index
    pips_y = [data[0], data[-1]] # Price

    for curr_point in range(2, n_pips):

        md = 0.0 # Max distance
        md_i = -1 # Max distance index
        insert_index = -1

        for k in range(0, curr_point - 1):

            # Left adjacent, right adjacent indices
            left_adj = k
            right_adj = k + 1

            time_diff = pips_x[right_adj] - pips_x[left_adj]
            price_diff = pips_y[right_adj] - pips_y[left_adj]
            slope = price_diff / time_diff
            intercept = pips_y[left_adj] - pips_x[left_adj] * slope;

            for i in range(pips_x[left_adj] + 1, pips_x[right_adj]):
                
                d = 0.0 # Distance
                if dist_measure == 1: # Euclidean distance
                    d =  ( (pips_x[left_adj] - i) ** 2 + (pips_y[left_adj] - data[i]) ** 2 ) ** 0.5
                    d += ( (pips_x[right_adj] - i) ** 2 + (pips_y[right_adj] - data[i]) ** 2 ) ** 0.5
                elif dist_measure == 2: # Perpindicular distance
                    d = abs( (slope * i + intercept) - data[i] ) / (slope ** 2 + 1) ** 0.5
                else: # Vertical distance    
                    d = abs( (slope * i + intercept) - data[i] )

                if d > md:
                    md = d
                    md_i = i
                    insert_index = right_adj

        pips_x.insert(insert_index, md_i)
        pips_y.insert(insert_index, data[md_i])

    return pips_x, pips_y


def get_level_bounds(df: pd.DataFrame, zone_threshold: float) -> pd.DataFrame:
    """
    Get the upper and lower bounds of S1 and R1
    
    :params df is the OHLC dataframe
    :type :pd.DataFrame
    
    :params zone_threshold is used for the pivot point retracement condition
    :type :float 
    
    :return: (pd.DataFrame)
    """
    
    df["s1_lower"] = df["s1"] - zone_threshold
    df["s1_upper"] = df["s1"] + zone_threshold

    df["r1_lower"] = df["r1"] - zone_threshold
    df["r1_upper"] = df["r1"] + zone_threshold

    return df 

def pivot_point_retracement_conditions(df: pd.DataFrame, zone_threshold: float, price_diff_threshold: float, gap_bars: int) -> np.array:
    """
    Get the conditions of the Pivot Point type condition.
    
    This is used for Fibonacci, DM, Camarilla and Traditional
    
    :params df is the dataframe with the data 
    :type :pd.DataFrame
    
    :params zone_threshold is used for the pivot point retracement condition
    :type :float 
    
    :params price_diff_threshold is used for the pivot point retracement condition
    :type :float
    
    :params gap_bars is the minimum number of bars between the retracement point and the pivot high/low 
    :type :int
    
    :return: (np.array)
    """
    conditions = [ (abs(df.index_close - df.pivot_index_high ) >= gap_bars) & (df["pivot_diff"] >  price_diff_threshold) & (df.pivot_index_high > df.pivot_index_low) & ( abs(df.current_close - df["s1"]) < zone_threshold ),
                    (abs(df.index_close - df.pivot_index_low ) >= gap_bars) & ( df["pivot_diff"] >  price_diff_threshold) & (df.pivot_index_high < df.pivot_index_low) & ( abs(df.current_close - df["r1"]) < zone_threshold )] 
    
    return conditions 
    
def retracement_conditions(df: pd.DataFrame, condition: str="distance", zone_threshold: float=0.0002, price_diff_threshold: float=0.001, gap_bars: int = 5, ma_length: int=20) -> pd.DataFrame:
    """
    Set the conditions for what one considers a `true` retracement
    
    :params df is the OHLC data plus the pivot columns
    :type :pd.DataFrame
    
    :params condition is the type of conditions to use to mark a retracement. Options ["distance", "fibonacci", "camarilla", "dm", "ma"]
    :type :str 
    
    :params zone_threshold is used for the pivot point retracement condition
    :type :float 
    
    :params price_diff_threshold is used for the pivot point retracement condition
    :type :float
    
    :params gap_bars is the minimum number of bars between the retracement point and the pivot high/low 
    :type :int
    
    :return: (pd.DataFrame)
    """

    if condition == "distance":
    
        conditions = [ (abs(df.index_close - df.pivot_index_high ) >= gap_bars) & (df.pivot_index_high > df.pivot_index_low) & (df.current_close < df.pivot_high) & (df.current_close > df.pivot_low) & 0.5*abs(df.pivot_index_high - df.pivot_index_low) >= abs(df.pivot_high - df.current_close), 
                    (abs(df.index_close - df.pivot_index_low ) >= gap_bars) & (df.pivot_index_high < df.pivot_index_low) & (df.current_close > df.pivot_low) & (df.current_close < df.pivot_high) & 0.5*abs(df.pivot_index_high - df.pivot_index_low) >= abs(df.pivot_low - df.current_close)]
    elif condition == "fibonacci":
        
        df["s1"] = df.pivot_high - 0.62*(df.pivot_high - df.pivot_low) 
        df["r1"] = df.pivot_low  + 0.62*(df.pivot_high - df.pivot_low) 
        df["pivot_diff"] = df.pivot_high - df.pivot_low 
        df         = get_level_bounds(df, zone_threshold)
        conditions = pivot_point_retracement_conditions(df, zone_threshold, price_diff_threshold, gap_bars)
    
    elif condition == "dm":
        df["dm"] = 2*df.low +df.high +df.low 
        df["s1"] = df["dm"]/2 - df.pivot_high
        df["r1"] = df["dm"]/2 - df.pivot_low 
        
        df["pivot_diff"] = df.pivot_high - df.pivot_low 
        df         = get_level_bounds(df, zone_threshold)
        conditions = pivot_point_retracement_conditions(df, zone_threshold, price_diff_threshold, gap_bars) 
    elif condition == "camarilla":
        df["s1"]         = df.pivot_high - (df.pivot_high - df.pivot_low)*1.1/12
        df["r1"]         = df.pivot_low  + (df.pivot_high - df.pivot_low)*1.1/12
        df["pivot_diff"] = df.pivot_high - df.pivot_low
        df               = get_level_bounds(df, zone_threshold)
        conditions       = pivot_point_retracement_conditions(df, zone_threshold, price_diff_threshold, gap_bars)
    
    elif condition == "ma":
        df["r1"]         = ta.ema(df.close, length=ma_length)
        df["s1"]         = ta.ema(df.close, length=ma_length)
        df               = get_level_bounds(df, zone_threshold)
        df["pivot_diff"] = df.pivot_high - df.pivot_low 
        conditions       = pivot_point_retracement_conditions(df, zone_threshold, price_diff_threshold, gap_bars) 
        
    choices           = [-1, 1]
    df["retracement"] = np.select(conditions, choices, np.nan)
    
    return df 


def calculate_pivot_points(df: pd.DataFrame, lookback: int, method: str = "one", fractal_length:int = 5, pips_measure: int = 1, n_pips: int = 5) -> pd.DataFrame:
    """
    Calculate the Pivot Points 
    
    :params df is the OHLC data 
    :type :pd.DataFrame
    
    :params lookback is the number of bars to use to calculate the pivot points
    :type :int 
    
    :params method is how to calculate the pivot points. Options: ["hilo", "arg", "frc", "pips"]
    :type :str 
    
    :params fractal_length is the number of periods to calculate the fractals
    :type :int
    
    :params pips_measure is the pips measure method to use. Options: [1 = Euclidean Distance, 2 = Perpindicular Distance, 3 = Vertical Distance]
    :type :int 
    
    :params n_pips is the number of pips to extract.
    :type :int
    
    :return: (pd.DataFrame)
    """
    
    df["pivot_high"]   = np.nan 
    df["pivot_low"]    = np.nan 
    bar = Bar("Calculating the pivot points...", max=len(df))
    for idx in range(lookback, len(df)):
        if method == "hilo":
            df.loc[idx,"pivot_high"]       = df.loc[idx-lookback:idx, "high"].max()
            df.loc[idx,"pivot_index_high"] = df.loc[idx-lookback:idx, "high"].idxmax()

            df.loc[idx,"pivot_low"]         = df.loc[idx-lookback:idx, "low"].min()
            df.loc[idx,"pivot_index_low"]   = df.loc[idx-lookback:idx, "low"].idxmin()
            df.loc[idx, "current_close"]    = df.loc[idx,"close"] 
            df.loc[idx, "index_close"]        = idx 
        
        elif method == "arg":
            
            max_indexes = argrelextrema(df.loc[idx-lookback:idx, "high"].values, np.greater)[0]
            min_indexes = argrelextrema(df.loc[idx-lookback:idx, "low"].values, np.less)[0]
            
            df.loc[idx, "pivot_high"]       = df.loc[max_indexes,"high"].max()
            df.loc[idx, "pivot_index_high"] = df.loc[max_indexes,"high"].idxmax()
            df.loc[idx, "pivot_low"]        = df.loc[min_indexes,"low"].min()
            df.loc[idx, "pivot_index_low"]  = df.loc[min_indexes,"low"].idxmin()
            df.loc[idx, "current_close"]    = df.loc[idx,"close"] 
            df.loc[idx, "index_close"]      = idx 
                    
        elif method == "frc":
             df_subset = df.iloc[idx-lookback:idx]
             fractal_highs  = df.loc[idx-lookback:idx,"high"] == df.loc[idx-lookback:idx,"high"].rolling(fractal_length, center=True).max()
             fractal_lows   = df.loc[idx-lookback:idx,"low"] == df.loc[idx-lookback:idx,"low"].rolling(fractal_length, center=True).min()
            
             df.loc[idx, "pivot_high"]       = df_subset.loc[fractal_highs,"high"].max()
             df.loc[idx, "pivot_index_high"] = df_subset.loc[fractal_highs,"high"].idxmax()                
               
             df.loc[idx, "pivot_low"]        =  df_subset.loc[fractal_lows,"low"].min()
             df.loc[idx, "pivot_index_low"]  =  df_subset.loc[fractal_lows,"low"].idxmin()
 
             df.loc[idx, "current_close"]    = df.loc[idx,"close"] 
             df.loc[idx, "index_close"]      = idx 
                
        elif method == "pips":
                idx_range = list(range(idx-lookback,idx+1))
                
                high_array = df.loc[idx-lookback:idx, "close"].to_numpy()
                low_array  = df.loc[idx-lookback:idx, "close"].to_numpy()
                
                high_indexes, high_values  = find_pips(high_array,n_pips, pips_measure)
                low_indexes,  low_values   = find_pips(low_array,n_pips, pips_measure)
                
                df.loc[idx, "pivot_high"]       = np.array(high_values).max()
                df.loc[idx, "pivot_index_high"] = idx_range[np.array(high_values).argmax()] 
                
                df.loc[idx, "pivot_low"]        = np.array(low_values).min()
                df.loc[idx, "pivot_index_low"]  = idx_range[np.array(low_values).argmin()] 
                
                df.loc[idx, "current_close"]    = df.loc[idx,"close"] 
                df.loc[idx, "index_close"]      = idx 
                
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
        y=[df.loc[point,"current_close"]],
        mode="markers", marker=dict(size=20, color="purple"), name="Retracement Point"
    )
    
    
    try:
    # Add the region, if available or set
        fig.add_hline(y=df.iloc[-1].s1, line_color="red")
        fig.add_hline(y=df.iloc[-1].r1, line_color="green")
        
        fig.add_hline(y=df.iloc[-1].r1_lower, line_color="green", line_dash="dash")
        fig.add_hline(y=df.iloc[-1].r1_upper, line_color="green", line_dash="dash")
        
        fig.add_hline(y=df.iloc[-1].s1_lower, line_color="red", line_dash="dash")
        fig.add_hline(y=df.iloc[-1].s1_upper, line_color="red", line_dash="dash")
    except:
        pass 
        
    if df.iloc[-1].pivot_index_high > df.iloc[-1].pivot_index_low:
        fig.add_scatter(
            x = [df.iloc[-1].pivot_index_low, df.iloc[-1].pivot_index_high , point],
            y = [df.iloc[-1].pivot_low, df.iloc[-1].pivot_high, df.loc[point,"current_close"]],
            marker = dict(size=10, symbol="arrow-bar-up", angleref="previous", color="blue"), showlegend=False
        )
    else:
         fig.add_scatter(
            x = [df.iloc[-1].pivot_index_high, df.iloc[-1].pivot_index_low , point],
            y = [df.iloc[-1].pivot_high, df.iloc[-1].pivot_low, df.loc[point,"current_close"]],
            marker = dict(size=10, symbol="arrow-bar-up", angleref="previous", color="blue"), showlegend=False
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
                        if idx_high == 1 or idx_high == 0:
                            df_copy = df.iloc[idx_high:row[0]+1]
                        else:
                            df_copy = df.iloc[idx_high-2:row[0]+1]
                    else:
                        if idx_low ==1 or idx_low ==0:
                            df_copy = df.iloc[idx_low:row[0]+1]
                        else:
                           df_copy = df.iloc[idx_low-2:row[0]+1]

                    display_plot(df_copy, row[0], save=True)
                bar.next()
            bar.finish()    
                    
    except Exception as e:
        print(f"Error: {e}")


def save_signal_graphs(df: pd.DataFrame, lookback:int):
    """
    Save the signal graphs 
    
    :params df is the dataframe
    :type :pd.DataFrame
    
    :params lookback is the number of periods for the plotting window
    :type :int
    
    """

    bar = Bar("Saving the signal graphs...", max=len(df))
    for row in df.iterrows():
        if row[1]["signal"] == -1 or row[1]["signal"] == 1:
            
            end   = row[0] + lookback
            start = row[0] - lookback 
            if end <= len(df):
                df_copy = df.iloc[start:end]
            else:
                df_copy = df.iloc[start:len(df)]
            
            
            fig = go.Figure(data=[go.Candlestick(
                        x    = df_copy.index,
                        open  = df_copy.close,
                        high  = df_copy.high,
                        low   = df_copy.low,
                        close = df_copy.close, name="OHLC"    
                )])
            
            if row[1]["signal"] == 1:
                fig.add_scatter(
                    x=[row[0]],
                    y=[df.iloc[row[0]].close],
                    mode="markers", marker=dict(size=20, color="purple", symbol="arrow-up"), name="BUY"
                )
            else:
                fig.add_scatter(
                    x=[row[0]],
                    y=[df.iloc[row[0]].close],
                    mode="markers", marker=dict(size=20, color="purple", symbol="arrow-down"), name="SELL"
                )                

            fig.add_scatter(
                x=[df.iloc[row[0]].pivot_index_high],
                y=[df.iloc[row[0]].pivot_high],
                mode="markers", marker=dict(size=20, color="green"), name="Pivot High"
            )

            fig.add_scatter(
                x=[df.iloc[row[0]].pivot_index_low],
                y=[df.iloc[row[0]].pivot_low],
                mode="markers", marker=dict(size=20, color="red"), name="Pivot Low"
            )
        
            if df.iloc[row[0]].pivot_index_high > df.iloc[row[0]].pivot_index_low:
                fig.add_scatter(
                x = [df.iloc[row[0]].pivot_index_low, df.iloc[row[0]].pivot_index_high , row[0]],
                y = [df.iloc[row[0]].pivot_low, df.iloc[row[0]].pivot_high, df.loc[row[0],"current_close"]],
                marker = dict(size=10, symbol="arrow-bar-up", angleref="previous", color="blue"), showlegend=False)
            else:
                fig.add_scatter(
                x = [df.iloc[row[0]].pivot_index_high, df.iloc[row[0]].pivot_index_low , row[0]],
                y = [df.iloc[row[0]].pivot_high, df.iloc[row[0]].pivot_low, df.loc[row[0],"current_close"]],
                marker = dict(size=10, symbol="arrow-bar-up", angleref="previous", color="blue"), showlegend=False)       
        
        
            fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                            xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, side="right"), legend_font_color="white",
                            legend=dict(yanchor="bottom", y=0.99, xanchor="left", x=0.01) )

            fig.update_traces(increasing_fillcolor="#3D9970", selector=dict(type='candlestick'))
            fig.update_traces(decreasing_fillcolor="#FF4136", selector=dict(type='candlestick'))

            fig.update_xaxes(color='white') 
            fig.update_yaxes(color='white')   
        
            fig.add_hline(y=df.iloc[row[0]].s1, line_color="red")
            fig.add_hline(y=df.iloc[row[0]].r1, line_color="green")
            
            fig.add_hline(y=df.iloc[row[0]].r1_lower, line_color="green", line_dash="dash")
            fig.add_hline(y=df.iloc[row[0]].r1_upper, line_color="green", line_dash="dash")
            
            fig.add_hline(y=df.iloc[row[0]].s1_lower, line_color="red", line_dash="dash")
            fig.add_hline(y=df.iloc[row[0]].s1_upper, line_color="red", line_dash="dash")
                        
            file_image =os.path.join("results",f"signal-{row[0]}.png")
        
            fig.write_image(file_image)

        bar.next()
    bar.finish()

if __name__ == "__main__":
    df = pd.read_csv("data/sample.csv")

    lookback          = 50
    idx               = 100
    df = calculate_pivot_points(df, lookback, method="hilo", pips_measure=2, n_pips=10)


    condition_options = ["distance", "fibonacci", "camarilla", "dm", "ma"]
    for c in condition_options:
        if c == "ma":
            df = retracement_conditions(df, condition=c)


    # Plot/Save the 'potential' retracement points
    plot_retracement_point(df,all_points=True)
   
    # ==============================================================
    # An example - Define your own measure of trend up and down
    #================================================================
    
    # Define a trend using the EMA
    df["ema_signal"] = np.select([df.ta.ema() < df.close, df.ta.ema() > df.close ], [1,-1], np.nan)
    
    # Find the signal retracements
    df["signal"]     = np.select([(df.ema_signal == 1) & (df.retracement == -1), (df.ema_signal == -1) & (df.retracement == 1)   ], [1,-1], np.nan)
    
    # Save the signal graphs
    save_signal_graphs(df, lookback)
    
