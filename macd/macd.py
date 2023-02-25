"""
Date: 2023-02-23

Visit our YouTube Channel: https://www.youtube.com/@zetratrading

License    : MIT
Disclaimer : This program is not an investment advice and is for educational and entertainment purposes only!  

@author Zetra Team
"""

import glob
import os 
import pandas as pd 
import pandas_ta as ta
from backtesting import Strategy, Backtest




class MacdStrategy(Strategy):

    def init(self):
        pass 

    def next(self):
        super().next()

        if not self.position:
            if self.data.signal == 1:
                    self.buy(sl=self.data.Close*0.85 , tp=self.data.Close*1.25, size=1000)
                        
            elif self.data.signal == -1:
                    self.sell(sl=self.data.Close*1.25 , tp=self.data.Close*0.85, size=1000)

        else:

            if self.data.signal == 1:
                self.position.close()
                self.buy(sl=self.data.Close*0.85 , tp=self.data.Close*1.25, size=1000)
        
            elif self.data.signal == -1:
                 self.position.close()
                 self.sell(sl=self.data.Close*1.25 , tp=self.data.Close*0.85, size=1000)


if __name__ == "__main__":

    folders     = ["30min","1h","4h"] 
    
    for folder in folders:
        files       = glob.glob(f".//data//{folder}//*.csv") # Assumes you are in a windows machine

        symbols_arr        = []
        trades_arr         = []
        return_arr         = []
        win_rate_arr       = []
        for file in files:
            df          = pd.read_csv(file) 
            symbol      = os.path.basename(file).split("-")[1]
                        

            df.rename(columns={"open":"Open", "high":"High","low":"Low","close":"Close"}, inplace=True)
            df              = df.loc[:,["Open","High","Low", "Close"]]


            # Calculate the MACD    
            macd_results    = df.ta.macd()
            df["macd"]      = macd_results["MACD_12_26_9"]
            df["macdh"]     = macd_results["MACDh_12_26_9"]
            df["macds"]     = macd_results["MACDs_12_26_9"]
            df["lag_macd"]  =  df["macd"].shift()
            df["lag_macds"] =  df["macds"].shift()

            # Calculate the ema 
            df["ema"]       = df.ta.ema(200)


            # Find the buy and sell signal points
            df["signal"] = 0 
            buy_signal  = (df["macd"] < 0) & (df["macds"] < 0) & (df["macd"] > df["macds"]) & (df["lag_macd"] < df["lag_macds"]) & (df["Close"] > df["ema"])
            sell_signal = (df["macd"] > 0) & (df["macds"] > 0) & (df["macd"] < df["macds"]) & (df["lag_macd"] > df["lag_macds"]) & (df["Close"] < df["ema"])
            df.loc[buy_signal,"signal"]  = 1
            df.loc[sell_signal,"signal"] = -1

            # Set the stoploss and takeprofit
            stoploss  = 0.85
            takeprofit= 1.25

            # ===============
            # Run the backtest
            # ==============
            bt = Backtest(df, MacdStrategy,
                        cash=1000000, commission=.002)



            output = bt.run()

            number_of_trades = output["# Trades"]
            return_          = output["Return [%]"]
            win_rate         = output["Win Rate [%]"]

            symbols_arr.append(symbol)
            trades_arr.append(number_of_trades)
            return_arr.append(return_)
            win_rate_arr.append(win_rate)

            
            print(f"Completed for {symbol} {folder}")

        # Make a dataframe of the results
        data = {"symbols":symbols_arr,"trades":trades_arr,"returns":return_arr,"winrate":win_rate_arr}
        results_df = pd.DataFrame(data)
        # Save the results
        if os.path.exists(".//results"):
            
            results_df.to_csv(os.path.join(f".//results//result-{folder}.csv"), index=False)
        else:
            os.mkdir(".//results")
            results_df.to_csv(os.path.join(f".//results//result-{folder}.csv"), index=False)

            