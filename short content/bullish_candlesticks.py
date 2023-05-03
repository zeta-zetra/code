"""
Date 20230129

This file calculates bullish candlestick patterns. This is done for the following candlestick patterns:
 - "engulfing",
 - "harami"
 - "dragonflydoji"
 - "invertedhammer"
 - "morningstar"

@author Zetra Team
License   : MIT
Disclaimer: Any program we provide does not constitute financial advice.  
"""

import pandas as pd
import pandas_ta as ta 
import mplfinance as mpf
import numpy as np
import yfinance as yf



# Get the Data
df = pd.DataFrame()
df = df.ta.ticker("aapl", period="1y")


patterns  = df.ta.cdl_pattern(name=["engulfing","harami","dragonflydoji","invertedhammer","morningstar"])

# Bullish engulfing
df["ENGULFING"]                                = patterns["CDL_ENGULFING"]
df.loc[df["ENGULFING"]<100,"ENGULFING"]        = np.nan 
df.loc[df["ENGULFING"]==100,"HIGH_ENGULFING"]  = df.loc[df["ENGULFING"]==100,"High"] + 3e-5 


# Bullish Harami
df["HARAMI"]                              = patterns["CDL_HARAMI"]
df.loc[df["HARAMI"]<100,"HARAMI"]         = np.nan 
df.loc[df["HARAMI"]==100,"HIGH_HARAMI"]   = df.loc[df["HARAMI"]==100,"High"] + 3e-5 


# Dragonfly Doji
df["DRAGONFLYDOJI"]                                    = patterns["CDL_DRAGONFLYDOJI"]
df.loc[df["DRAGONFLYDOJI"]<100,"DRAGONFLYDOJI"]        = np.nan 
df.loc[df["DRAGONFLYDOJI"]==100,"HIGH_DRAGONFLYDOJI"]  = df.loc[df["DRAGONFLYDOJI"]==100,"High"] + 3e-5 


# Inverted Hammer
df["INVERTEDHAMMER"]                                     = patterns["CDL_INVERTEDHAMMER"]
df.loc[df["INVERTEDHAMMER"]<100,"INVERTEDHAMMER"]        = np.nan 
df.loc[df["INVERTEDHAMMER"]==100,"HIGH_INVERTEDHAMMER"]  = df.loc[df["INVERTEDHAMMER"]==100,"High"] + 3e-5 



# Morning star
df["MORNINGSTAR"]                                  = patterns["CDL_MORNINGSTAR"]
df.loc[df["MORNINGSTAR"]<100,"MORNINGSTAR"]        = np.nan 
df.loc[df["MORNINGSTAR"]==100,"HIGH_MORNINGSTAR"]  = df.loc[df["MORNINGSTAR"]==100,"High"] + 3e-5 


# Save the plot as images. The images will be saved in the same folder where you run the program
for candle_pattern in ["ENGULFING","HARAMI","DRAGONFLYDOJI","INVERTEDHAMMER","MORNINGSTAR"]:
    bullish_pattern = mpf.make_addplot(df[f"HIGH_{candle_pattern}"], type="scatter", color='g', marker="v", markersize=200)
    mpf.plot(df, style="charles", type="candle", addplot=[bullish_pattern], 
    savefig=f"bullish_{candle_pattern.lower()}.png")
