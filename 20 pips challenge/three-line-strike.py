"""
Date           : 2023-04-22
Author         : Zetra Team 
YouTube Channel: https://www.youtube.com/@zetratrading/featured

This is a script that implements a strategy for the 20pips challenge. 
The challenge is a way to grow your small Forex account.

Here is the YouTube channel for the source of the strategy: https://www.youtube.com/@TheMovingAverage

Here is the link to the Youtube video about growing your small account:

Disclaimer: We want to emphasize that this is purely for educational purposes only. We do not offer any financial advice, recommendations, or make any guarantees of profit or success. 
Trading carries a risk of loss, and it is important to always consult with a qualified professional before making any trading decisions.

License: MIT 

"""

import numpy as np
import os
import pandas as pd 
import pandas_ta as ta 
import plotly.graph_objects as go 

from backtesting import Backtest, Strategy
from typing import Union


class ThreeLineStrikeScaplingStrategy(Strategy):
    initsize = 0.3
    mysize   = initsize

    def init(self):
        super().init()

    def next(self):
        super().next()
        
        if self.data.signal==2 and len(self.trades)==0:   
            sl1 = self.data.Close[-1] - 45e-4
            tp1 = self.data.Close[-1] + 45e-4 
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        elif self.data.signal==1 and len(self.trades)==0:         
            sl1 = self.data.Close[-1] + 45e-4
            tp1 = self.data.Close[-1] - 45e-4 
            self.sell(sl=sl1, tp=tp1, size=self.mysize)


class ThreeLineStrikeScaplingATRStopStrategy(Strategy):
    initsize = 0.3
    mysize = initsize
    def init(self):
        super().init()

    def next(self):
        super().next()
        slatr = 2*self.data.atr[-1]
        TPSLRatio = 1.2

        if self.data.signal==2 and len(self.trades)==0:   
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr*TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        elif self.data.signal==1 and len(self.trades)==0:         
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr*TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)


class ThreeLineStrikeScaplingATRStopLossStrategy(Strategy):
    
    def init(self):
        super().init()

    def next(self):
        super().next()
        sltr = 1*self.data.atr[-1]
        for trade in self.trades: 
            if trade.is_long: 
                trade.sl = max(trade.sl or -np.inf, self.data.Close[-1] - sltr)
                if self.data.signal==1:
                    trade.close()
            else:
                trade.sl = min(trade.sl or np.inf, self.data.Close[-1] + sltr) 
                if self.data.signal==2:
                    trade.close()
                    
        if self.data.signal==2 and len(self.trades)==0:
            sl1 = self.data.Close[-1] - sltr
            self.buy(sl=sl1)
        elif self.data.signal==1 and len(self.trades)==0:
            sl1 = self.data.Close[-1] + sltr
            self.sell(sl=sl1)



def plot_ohlc(ohlc: pd.DataFrame) -> None:
    """
    Plot the ohlc data

    :params ohlc - A DataFrame that has ohlc data 
    :type  :pd.DataFrame 

    :returns None 
    """

    ohlc = ohlc.loc[250:1000,:]
    fig = go.Figure(data=[
        go.Candlestick(
            x     = ohlc.index,
            open  = ohlc["Open"],
            high  = ohlc["High"],
            low   = ohlc["Low"],
            close = ohlc["Close"]
        )
    ])

   

    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False, color="white"), yaxis=dict(showgrid=False, side="right", color="white"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01) )

    fig.show()


def plot_ohlc_animation(ohlc: pd.DataFrame, start: int = 0 ,increment: int = 15) -> None:
    """
    Plot the ohlc as an animation

    :params ohlc - OHLC dataframe 
    :type :pd.DataFrame

    :params start - index to start the plotting
    :type :int 

    :params increment - By how many bars should the plot be slided to the right?
    :type :int 


    :returns None 
    """

    # Make Figure
    fig_dict = {
        "data"    : [],
        "layout"  : {},
        "frames"  : []
    }

    # Fill in most of the layout
    fig_dict["layout"]["xaxis_rangeslider_visible"]  = False
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 100, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 100,
                                                                        "easing": "quadratic-in-out"}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 100, "redraw": True},
                                    "mode": "immediate",
                                    "transition": {"duration": 100}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]


    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Index:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {"duration": 100, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }


    start_ohlc = ohlc.loc[0:250,:]
    data_dict = go.Candlestick(
            x     = start_ohlc.index,
            open  = start_ohlc["Open"],
            high  = start_ohlc["High"],
            low   = start_ohlc["Low"],
            close = start_ohlc["Close"]
        )

    fig_dict["data"].append(data_dict)   


    end_ = 250 +increment
    for i in range(0, len(ohlc)-increment, increment):

        if  end_ < len(ohlc) - increment:  

            frame = {"data": [], "name": str(end_)}
            
            ohlc_subset = ohlc.loc[i+increment:end_,:]
            data_ = go.Candlestick(
                    x     = ohlc_subset.index,
                    open  = ohlc_subset["Open"],
                    high  = ohlc_subset["High"],
                    low   = ohlc_subset["Low"],
                    close = ohlc_subset["Close"]
                )

            frame["data"].append(data_)

            fig_dict["frames"].append(frame)
            slider_step = {"args": [
                [end_],
                {"frame": {"duration": 100, "redraw": True},
                "mode": "immediate",
                "transition": {"duration": 100}}
            ],
                "label": end_,
                "method": "animate"}
            sliders_dict["steps"].append(slider_step)

            end_+=increment

    fig_dict["layout"]["sliders"] = [sliders_dict]

    fig = go.Figure(fig_dict)

    fig.show()


def signal_point_position(row: pd.Series) -> Union[float, None]:
    """
    Set the buy to the Low and set the sell to the High

    :params row - A row of the ohlc dataframe
    :type :pd.Series 

    :return float or np.nan
    """
    if row['signal']==1:
        return row['High']
    elif row['signal']==2:
        return row['Low'] 
    else:
        return np.nan



def plot_ohlc_plus_signal(ohlc: pd.DataFrame) -> None:
    """
    Plot ohlc data with the signal points
    
    :params ohlc - A DataFrame that has ohlc data 
    :type  :pd.DataFrame 

    :params with_emas - Should EMAs be included in the plot 
    :type :bool 

    :returns None     
    """

    ohlc_subset = ohlc.loc[250:1000,:]


    fig = go.Figure(data=[go.Candlestick(x=ohlc_subset.index,
                    open=ohlc_subset['Open'],
                    high=ohlc_subset['High'],
                    low=ohlc_subset['Low'],
                    close=ohlc_subset['Close'], name="OHLC")])




    fig.add_scatter(x=ohlc_subset.index, y=ohlc_subset['signal_point'], mode="markers",
                    marker=dict(size=10, color="MediumPurple"),
                    name="Signal")



    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False, color="white"), yaxis=dict(showgrid=False, side="right", color="white"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01) )

    fig.show()


def generate_signal(ohlc: pd.DataFrame) -> pd.DataFrame:
    """
    Generate the signal

    :parmas ohlc - OHLC DataFrame
    :type  :pd.DataFrame
    

    :return pd.DataFrame

    """

    # Calculate the engulfing candles 
    ohlc["engulf"] = ohlc.ta.cdl_pattern(name="engulfing")
    
    # Calculate ATR 
    ohlc["atr"] = ohlc.ta.atr()

    # Calculate OHLC lags
    high_t   = ohlc["High"]             # high(t)
    high_t_1 = ohlc["High"].shift(1)    # high(t-1)
    high_t_2 = ohlc["High"].shift(2)    # high(t-2)
    high_t_3 = ohlc["High"].shift(3)    # high(t-3)

    low_t    = ohlc["Low"]              # low(t)
    low_t_1  = ohlc["Low"].shift(1)     # low(t-1)
    low_t_2  = ohlc["Low"].shift(2)     # low(t-2)   
    low_t_3  = ohlc["Low"].shift(3)     # low(t-3)

  
    close_t_1  = ohlc["Close"].shift(1)     # close(t-1)
    close_t_2  = ohlc["Close"].shift(2)     # close(t-2)   
    close_t_3  = ohlc["Close"].shift(3)     # close(t-3)

    open_t_1  = ohlc["Open"].shift(1)     # open(t-1)
    open_t_2  = ohlc["Open"].shift(2)     # open(t-2)   
    open_t_3  = ohlc["Open"].shift(3)     # open(t-3)


    # Generate signal 
    conditions = [
        ( (high_t_1 > high_t_2) & (high_t_2 > high_t_3) & (low_t_1 > low_t_2) & (low_t_2 > low_t_3) & (close_t_1 > open_t_1) & (close_t_2 > open_t_2) & (close_t_3 > open_t_3)  ),
        ( (low_t_1 < low_t_2) & (low_t_2 < low_t_3) & (high_t_1 < high_t_2) & (high_t_2 < high_t_3) & (close_t_1 < open_t_1) & (close_t_2 < open_t_2) & (close_t_3 < open_t_3)  )
            ]
    choices = [1, 2]

    ohlc['hi_lo'] = np.select(conditions, choices, default=0)

    
    signal = [0]*len(ohlc)
   
    for row in range(0, len(ohlc)):
        
        # signal[row] = 0

        if ohlc.engulf[row] == -100 and ohlc['hi_lo'][row] == 1:
            signal[row] = 1

        if ohlc.engulf[row] == 100 and ohlc['hi_lo'][row] == 2:
            signal[row] = 2


    ohlc['signal'] = signal

    return ohlc


def plot_backtest_stats(stats) -> None:
    """
    Plot a table of the backtest statistics
    """

    keys   = list(stats.keys())[:-3]
    values = [stats[k] for k in keys]

    df     = pd.DataFrame({"stat":keys, "value": values})

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.stat, df.value],
                fill_color='lavender',
                align='left'))
    ])

    fig.show()   



def plot_equity_curve(equity_curve: pd.DataFrame) -> None:
    """
    Plot the equity curve

    :params equity_curve - dataframe that has Equity, DrawdownPct and DrawdownDuration
    :type :pd.DataFrame
    
    """

    fig = go.Figure(
            go.Scatter(x=equity_curve.index, y=equity_curve.Equity, line=dict(color="blue", width=2), name="Equity Curve")
    )

    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False, color="white"), yaxis=dict(showgrid=False, side="right", color="white"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01) )

    fig.show()     


def main(animation: bool = False, static_plot: bool = False, signal_plot: bool = True, backtest: bool = True) -> None:
    """
    Main function to do the analysis and backtest
    
    :params animation - Run animation plot?
    :type :bool

    :params static_plot - plot ohlc data? Note this will include first 250 candlebars. See plot_ohlc function
    :type :bool
    

    :params signal_plot - plot the ohlc data and the signal points? Note this will include  250 until 1000 candlebars. See plot_ohlc_plus_signal function
    :type :bool 

    :params backtest - Run a backtest
    :type :bool     

    """

    dir_     = os.path.realpath('')
    csv_file = os.path.join(dir_,"data","EURUSD_Candlestick_15_M_BID_01.01.2020-31.12.2022.csv")

    # Read in the data
    ohlc = pd.read_csv(csv_file)

    # Remove non-trading periods (i.e. weekends)
    ohlc = ohlc[ohlc['Volume']!=0]
    ohlc.reset_index(drop=True, inplace=True)


    # Plot the ohlc data
    if static_plot:
        plot_ohlc(ohlc)


    # Look at the data as an animation 
    if animation:
        plot_ohlc_animation(ohlc)


    # Generate Signal 
    ohlc = generate_signal(ohlc)

    # Create the signal points
    ohlc['signal_point'] = ohlc.apply(lambda row: signal_point_position(row), axis=1)

    # # Plot with signals 
    if signal_plot:
      plot_ohlc_plus_signal(ohlc)

    # Run backtest
    if backtest:
        strategies = [ThreeLineStrikeScaplingATRStopStrategy, ThreeLineStrikeScaplingStrategy, ThreeLineStrikeScaplingATRStopLossStrategy]

        for strategy in strategies:
            bt    = Backtest(ohlc, strategy, cash=100, margin=1/100, commission=.00)
            stats = bt.run()

            # Plot the stats 
            plot_backtest_stats(stats)


            # Original backtesting.py plot
            bt.plot()

            # Plot equity curve 
            plot_equity_curve(stats["_equity_curve"])



if __name__ == "__main__":
    main()