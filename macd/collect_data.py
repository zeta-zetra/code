"""
Date: 2023-02-23

Visit our YouTube Channel: https://www.youtube.com/@zetratrading

License    : MIT
Disclaimer : This program is not an investment advice and is for educational and entertainment purposes only!  

@author Zetra Team
"""

import os
import MetaTrader5 as mt5
import pytz
import datetime
import pandas as pd
import time


pairs   = ['AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD', 'AUDUSD', 'CADCHF', 'CADJPY', 'CHFJPY', 'EURAUD', 'EURCAD', 'EURCHF', 'EURDKK', 'EURGBP', 'EURJPY', 'EURNOK', 'EURNZD', 'EURRUB', 'EURSEK', 'EURTRY', 'EURUSD', 'EURZAR', 'GBPAUD', 'GBPCAD', 'NZDCAD', 'NZDCHF', 'NZDJPY', 'NZDSGD', 'NZDUSD', 'SGDJPY', 'USDCAD', 'USDCHF', 'USDDKK', 'USDHKD', 'USDJPY', 'USDMXN', 'USDNOK', 'USDPLN', 'USDRUB', 'USDSEK', 'USDSGD', 'USDTRY', 'USDZAR']

time_frames_mt5 = {"15min":mt5.TIMEFRAME_M15, "30min":mt5.TIMEFRAME_M30, "1h": mt5.TIMEFRAME_H1,
                    "4h": mt5.TIMEFRAME_H4, "1d": mt5.TIMEFRAME_D1}


START     = "2003-01-01"
END_DT    = "2022-12-31"
YEAR_MT5  = 2021
MONTH_MT5 = 1
DAY_MT5   = 1
TIME_DELTA= 3300

dir_ = os.path.realpath('')

# Collect data from MetaTrader5. Make sure that the MT5 is open
if source == "mt5":
    if not mt5.initialize():
        
        print("initialize() failed, error code =", mt5.last_error())

        quit()


    for pair in pairs:
        for tf in tf_arr:
            if tf == "30min":
                TIME_DELTA = 1650
                YEAR_MT5   = 2022
            if tf == "1h":
                TIME_DELTA = 3300
                YEAR_MT5   = 2021

            timezone   = pytz.timezone("Africa/Johannesburg")
            time_frame = time_frames_mt5[tf]

            if tf != "1d" or tf != "4h":
                time_from = datetime.datetime(YEAR_MT5, MONTH_MT5, DAY_MT5, tzinfo = timezone)

                time_to = datetime.datetime.now(timezone) + datetime.timedelta(days=TIME_DELTA)


            else:
                time_from = datetime.datetime.strptime(START,"%Y-%m-%d" ,tzinfo = timezone)  
                time_to = datetime.datetime.strptime(END,"%Y-%m-%d" , tzinfo = timezone)

            print("Coping rates from MT5...")
            rates = mt5.copy_rates_range(pair, time_frame, time_from, time_to)

            print("Loading the data in a DF....")
            rates_frame = pd.DataFrame(rates)
        
            if rates_frame.shape[0] > 0:
                # Save the data
                print("Saving the data to a csv file...")
            
                if os.path.exists(os.path.join( dir_,'data',tf)):
                    rates_frame.to_csv(os.path.join( dir_,'data', tf ,f'mt5-{pair.lower()}-{tf}.csv'), index=True)
                else:
                    os.mkdir(os.path.join( dir_,'data',tf))
                    rates_frame.to_csv(os.path.join( dir_,'data',tf,f'mt5-{pair.lower()}-{tf}.csv'), index=True)
                print(f"Completed for {pair} {tf}") 
            else:
                print(f"No data found for {pair} {tf}")   

        time.sleep(5)