
import plotly.graph_objects as go 
import pandas as pd 

from typing import List

def plot_density(x: List[float], y: List[float]):
        """
        Plot the density given the x and y values
        """
        fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines')) 
    
        fig.show()

def plot_ohlc_pivots_dm(ohlc: pd.DataFrame, title: str = ""):
    """
    Plot the OHLC data and the Pivot points

    :params ohlc dataframe
    :type :pd.DataFrame

    :params title of the chart
    :type :str

    """

    ohlc_plot = ohlc
    ohlc_plot.reset_index(drop=True, inplace=True)

    fig = go.Figure(data=[
          go.Candlestick(x=ohlc_plot.index,
          open = ohlc_plot["open"],
          high = ohlc_plot["high"],
          low  = ohlc_plot["low"],
          close= ohlc_plot["close"],
          name = "OHLC")  
    ])

    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False, color="white"), yaxis=dict(showgrid=False, side="right", color="white"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), title=title, font_color="#FFFFFF")


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
        y=ohlc_plot.R1,
        marker=dict(color="green", size=4),
        mode="markers",
        name ="R1"
    )) 


    fig.show()

def plot(df: pd.DataFrame, title:str = ""):
    """
    Plot 
    """
    


    fig = go.Figure(
        data=[
            go.Candlestick(
            x    = df.index,
            open = df["open"],
            high = df["high"],
            low  = df["low"],
            close= df["close"], showlegend=False,
            name="OHLC"
            )
        ]
    )


    fig.add_trace(go.Scatter(
            x = df.index,
            y = df["support"],
            name="Support",
    ))

    fig.add_trace(go.Scatter(
            x = df.index,
            y = df["resistance"],
            name="Resistance",
    ))


    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, side="right"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01), title=title, font_color="#FFFFFF")

    fig.update_traces(increasing_fillcolor="#3D9970", selector=dict(type='candlestick'))
    fig.update_traces(decreasing_fillcolor="#FF4136", selector=dict(type='candlestick'))

    fig.update_xaxes(color='white') 
    fig.update_yaxes(color='white') 

    fig.show()
