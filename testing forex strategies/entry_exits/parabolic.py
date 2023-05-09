"""
Date           : 2023-05-02
Author         : Zetra Team
YouTube Channel: https://www.youtube.com/@zetratrading/featured
Github Link    : https://github.com/zeta-zetra/code

This is a strategy from the following Youtube video:
https://www.youtube.com/watch?v=gfRO2_QS6gM


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




logging.getLogger().addHandler(logging.StreamHandler())
logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s')



def main(show_plot=False, save_plot=True):
    """
    This is the main function to run the analysis
    """

    strategy_name = "parabolic"
    # Read in the data
    ohlc = read_data()

    # Calculate the Parabolic SAR
    psar = ohlc.ta.psar()

  
    ohlc.loc[:,"psar_long"]  = psar.loc[:,"PSARl_0.02_0.2"]
    ohlc.loc[:,"psar_short"] = psar.loc[:,"PSARs_0.02_0.2"]

    # Signal position points (i.e. for plotting)
    ohlc.loc[:,"buy_position"] = np.where(ohlc["High"] >  ohlc["psar_long"],ohlc["High"],np.nan)
    ohlc.loc[:,"sell_position"] = np.where(ohlc["Low"] <  ohlc["psar_short"],ohlc["Low"],np.nan)


    # Signal Points
    ohlc.loc[:,"buy"] = np.where(ohlc["High"] >  ohlc["psar_long"],1,0)
    ohlc.loc[:,"sell"] = np.where(ohlc["Low"] <  ohlc["psar_short"],1,0)  

    if save_plot:
        plot_ohlc(ohlc, filename=strategy_name)


    # ===============
    # Run backtest 
    #================

    run_backtest(ohlc, SimpleStrategy, strategy_name=strategy_name) 



if __name__ == "__main__":
    main()