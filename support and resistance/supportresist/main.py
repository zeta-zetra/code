"""
This file gets the support and resistance levels

Date  : 2023-07-04
Author: Zetra Team
"""
import numpy as np 
import pandas as pd 
import plotly.graph_objects as go
import warnings


# Own modules
from density import density_method
from fractal import fractal_method
from pivots import (clustering_methods, pivot_point_methods, scoring_methods)
from plotting import plot, plot_ohlc_pivots_dm


warnings.filterwarnings("ignore")



def find_levels(df: pd.DataFrame, method: str ="kmeans", pivot_method:str="argrel", levels:str="l"):
    """
    Find the support and resistance levels

    :params df is the OHLC data
    :type :str 

    :params method is how to calculate the levels: 
    :type  :str

    :params pivot_method is the way the pivot points should be calculated 
    :type :str
    """

    if method=="kmeans" or method=="agglomerative":
        df = clustering_methods(df, method, pivot_method)
        plot(df, method)
    elif method == "dm" or method == "traditional" or method =="camarilla" or method=="fibonacci" :
        df = pivot_point_methods(df, method)
        plot_ohlc_pivots_dm(df, title=f"Method: {method.title()}")

    elif method in ["scoring_1","scoring_2"]:
        df = scoring_methods(df, method)
        plot(df, method)
    elif method == "density_1" or method == "density_2":
        df = density_method(df, method)
        plot(df)
    elif method == "fractal":
        df = fractal_method(df)
        plot(df)





if __name__ == "__main__":
    df      = pd.read_csv("../data/sample-15m.csv")
    
    find_levels(df, method="fractal")

    


