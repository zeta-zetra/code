
import logging
import os 
import pandas as pd
import plotly.graph_objects as go 


from backtesting import Strategy, Backtest
from progress.bar import Bar
from typing import List


# Own modules
from exits.exits import *


DATA_FILENAME= "eurusd-15m.csv"

def read_data():
    """
    Read in the data 
    """
    # Read in the data 
    
    dir_     = os.path.realpath('')
    csv_file = os.path.join(dir_,"data",DATA_FILENAME)


    # Read in the data
    ohlc = pd.read_csv(csv_file)   

    # Remove non-trading periods (i.e. weekends)
    ohlc = ohlc[ohlc['Volume']!=0]
    ohlc.reset_index(drop=True, inplace=True)

    # Set index
    ohlc["datetime"] = pd.to_datetime(ohlc["Local time"], dayfirst=True)
    ohlc.set_index("datetime", inplace=True)

    # Set the date 
    ohlc["date"] = pd.to_datetime(ohlc["Local time"], dayfirst=True)

    


    return ohlc

def plot_ohlc(ohlc_subset: pd.DataFrame, filename: str, save_plot: bool = True, show_plot: bool = True ):
    """
    Plot the ohlc data with the buy and sell signals

    :params ohlc data 
    :type :pd.DataFrame 

    :params filename that will save the image
    :type :str

    :params save_plot 
    :type :bool 

    :params show_plot
    :type :bool

    """

    

    ohlc_plot         = ohlc_subset.iloc[250:1500,:]
    ohlc_plot.reset_index(drop=True, inplace=True)


    fig = go.Figure(data=[go.Candlestick(x=ohlc_plot.index,
                    open=ohlc_plot['Open'],
                    high=ohlc_plot['High'],
                    low=ohlc_plot['Low'],
                    close=ohlc_plot['Close'], name="OHLC")])

    fig.add_scatter(x=ohlc_plot.index, y=ohlc_plot['buy_position'], mode="markers",
                    marker=dict(size=20, color="green"), marker_symbol="triangle-up",
                    name="Buy")

    fig.add_scatter(x=ohlc_plot.index, y=ohlc_plot['sell_position'], mode="markers",
                    marker=dict(size=20, color="red"), marker_symbol="triangle-down",
                    name="Sell")                  

    fig.update_layout(xaxis_rangeslider_visible=False, plot_bgcolor='black', paper_bgcolor="black",
                     xaxis=dict(showgrid=False, color="white"), yaxis=dict(showgrid=False, side="right", color="white"), legend_font_color="white",
                     legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01) )

    if show_plot:
      fig.show()

    if save_plot:
        dir_     = os.path.realpath('')
        fig.write_image(os.path.join(dir_,"results", f"{filename}.png"))



def get_trading_strategy(base: List[Strategy]):
    """
    Get the Strategy class for the Exit and Entry 
    """

    class EntryExitStrategy(*base):

        def init(self):
            super().init()

        def next(self):
            super().next()

    return EntryExitStrategy


def run_backtest(ohlc_subset: pd.DataFrame, strategy: Strategy, strategy_name: str = "" ) -> None:
    """
    Run backtest 

    :params ohlc_subset is OHLC data 
    :type :pd.DataFrame

    :params strategy is the backtesting Strategy class 
    :type :Strategy

    :params strategy_name is the strategy name 
    :type :str 
    """

    # Different exits
    exits      = [FixedPIPExitStrategy, NBarExitStrategy, DayOfTheWeekExitStrategy, SwingExitStrategy, LineStrikeExitStrategy, PercentileExitStrategy, FirstProfitExitStrategy ]
    exit_names = ["Fixed PIP Exit","N Bar Exit", "Day of the Week Exit", "Swing High/Low Exit", "Line Strike Exit", "Percentile Exit", "First Profit Exit"]


    # Save directory
    dir_     = os.path.realpath('')

    # Placeholder for all the backtest results
    all_stats     = pd.DataFrame()
    limited_stats = pd.DataFrame()

    bar = Bar("Processing strategy...", max=len(exits))

    
    for i, item  in enumerate(zip(exits, exit_names)):
        
        # Exit strategy to use and its name
        exit = item[0]
        name = item[1]

        # Get the strategy class
        NewStrat = get_trading_strategy([strategy, exit])
        
        # Run the backtest
        bt = Backtest(ohlc_subset, NewStrat, cash=10_000, commission=.00, margin=1/100)
        stats = bt.run()

        # Get the stats results
        keys   = list(stats.keys())[:-3]
        values =  [round(stats[k],2) if isinstance(stats[k], float) else stats[k]  for k in keys]
        
        limited_res = ["Equity Final [$]", "Equity Peak [$]","Return [%]",
                        "Buy & Hold Return [%]","Return (Ann.) [%]", 
                        "Max. Drawdown [%]", "# Trades","Win Rate [%]" ]
        limited_keys   = [key  for key in keys if key in limited_res ]
        limited_values = [round(stats[k],2) if isinstance(stats[k], float) else stats[k]  for k in limited_keys]

        # Prepend the exit type
        keys   = ["Exit Type"] + keys
        values = [name]  + values 

        limited_keys = ["Exit Type"] + limited_keys
        limited_values = [name] + limited_values

        # Prepend the strategy name
        keys   = ["Strategy Name"]  + keys 
        values = [NewStrat.strat_name] + values 

        # Save the results to the all_stats dataframe
        series         = pd.DataFrame(columns=keys ,data=[values])
        series_limited = pd.DataFrame(columns=limited_keys ,data=[limited_values])
        all_stats      = pd.concat([all_stats, series])
        limited_stats  = pd.concat([limited_stats, series_limited])
        bar.next()

    bar.finish()

   # all_stats.to_csv(os.path.join(dir_,"results", f"result-{strategy_name}.csv"), index=False)    
    limited_stats.to_csv(os.path.join(dir_,"results", "csv",f"result-limited-{strategy_name}.csv"), index=False)

    save_backtest_stats(limited_stats, strategy_name)


def save_backtest_stats(df: pd.DataFrame, filename: str = "") -> None:
    """
    Save a table of the backtest statistics

    :params df that contains the stats 
    :type :pd.DataFrame

    :params filename is the strategy name
    :type :str
    """

    # keys   = list(stats.keys())[:-3]
    # values = [stats[k] for k in keys]

    # df     = pd.DataFrame({"stat":keys, "value": values})

   
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df['Exit Type'], df["Equity Final [$]"], df["Equity Peak [$]"], df["Return [%]"],
                           df["Buy & Hold Return [%]"], df["Return (Ann.) [%]"], df["Max. Drawdown [%]"],
                           df["# Trades"], df["Win Rate [%]"]],
                fill_color='lavender',
                align='left'))
    ])

    fig.update_layout(width=1080, height=600)
    # Also save it in the docs folder (if its there)
    try:
        dir_book     = os.path.realpath('')
        file_path    = os.path.join(dir_book,"results", "reports" ,f"{filename}.png")
        fig.write_image(file_path)
    except Exception as e:
        pass


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


def plot_ohlc_pivots_dm(ohlc: pd.DataFrame, filename: str = ""):
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
        y=ohlc_plot.R1,
        marker=dict(color="green", size=4),
        mode="markers",
        name ="R1"
    )) 


    # fig.show()

    # Also save it in the docs folder (if its there)
    try:
        dir_book     = os.path.realpath('').split("code")[0]
        file_path    = os.path.join(dir_book,"book", "100-strategies", "_static","images", f"{filename}.png")
        fig.write_image(file_path)
    except Exception as e:
        pass