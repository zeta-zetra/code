
from backtesting import Strategy
import numpy as np
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go 


class FixedPIPExitStrategy(Strategy):
    """
    Exit based on fixed pips
    """

    stop_loss   = 45e-4
    take_profit = 45e-4

    def init(self):
        super().init()

        self.tp = self.take_profit
        self.sl = self.stop_loss

    def set_pips(self, tp: float = 45e-4, sl: float = 45e-4):
        """
        Set the pips for the take profit and stoploss
        """

        self.tp = tp
        self.sl = sl

    def next(self):
        super().next()
        
        for trade in self.trades:

            if trade.sl == None and trade.tp == None:

                if trade.is_long:
                   trade.sl = self.data.Close[-1] - self.sl
                   trade.tp = self.data.Close[-1] + self.tp

                elif trade.is_short:
                   trade.sl = self.data.Close[-1] + self.sl
                   trade.tp = self.data.Close[-1] - self.tp  


class DayOfTheWeekExitStrategy(Strategy):
    """
    Exit based on the day of the week
    
    0 - Monday
    1 - Tuesday
    2 - Wednesday
    3 - Thursday
    4 - Friday
    """

    _dow      = 4
    _dow_dict = {0:"Monday", 1: "Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday"}
    _day      = _dow_dict[_dow]

    def init(self):
        super().init()

    def set_dow(self, dow: int = 4):
        """
        Set the day of the week using an integer
        {0:"Monday", 1: "Tuesday", 2:"Wednesday", 3:"Thursday", 4:"Friday"}
        """
        self._dow = dow 
        self._day      = self._dow_dict[self._dow]

    def next(self):
        super().next()

        

        for trade in self.trades:
           
            if trade.is_long and self.data.date[-1].strftime('%A') == self._day:
               trade.close()

            elif trade.is_short and self.data.date[-1].strftime('%A') == self._day:
               trade.close()        


class NBarExitStrategy(Strategy):
    """" N bar timed exit  """

    __n_bars = 5 

    def init(self):
        super().init()
    

    def set_n_bars(self, n_bars: float = 5):
        """
        Set the N bars to exit after
        """
        self.__n_bars = n_bars

    def next(self):
        super().next()

        current_bar = len(self.data)     
        for trade in self.trades:
            if trade.is_long and trade.entry_bar + self.__n_bars < current_bar:
                trade.close()

            elif trade.is_short and trade.entry_bar + self.__n_bars < current_bar:
                trade.close()


class PercentileExitStrategy(Strategy):
    """
    Exit based on price being less or greater than recent prices 
    """

    percentile = 50
    lookback   = 10

    def init(self):
        super().init()
        self._percentile = self.percentile
        self._lookback   = self.lookback

    def set_percentile(self, q: float = 50):
        """
        Set the percentile
        """
        self._percentile = q

    def set_lookback(self, lookback: int = 10):
        """
        Set the lookback period for the recent prices
        """
        self._lookback = lookback

    def next(self):
        super().next()

        for trade in self.trades:
            if (len(self.data) - 1) > (self._lookback + 1):
                recent_prices    = [self.data.Close[i] for i in range(-1*self._lookback,-1)]
                percentile_price = np.percentile(recent_prices, 50)

                if trade.is_long and self.data.Close[-1] < percentile_price:                
                    trade.close()

                elif trade.is_short and self.data.Close[-1] > percentile_price:
                    trade.close()


class LineStrikeExitStrategy(Strategy):
    """
    Exit based on n consecutive bars up/down 
    """

    _n_bars = 3

    def init(self):
        super().init()
        self.__n_bars = self._n_bars

    def set_bars(self, bars:int = 3):
        """
        Look at n bars 
        """
        self.__n_bars = bars 

    def next(self):    
        super().next()

        for trade in self.trades:
            if (len(self.data) - 1) > self.__n_bars+1:

                if trade.is_long:                
                    higher_closes = [self.data.Close[i+1] > self.data.Close[i]  for i in range(-1*(self.__n_bars +1),-1)]
                    if all(higher_closes):
                        trade.close()

                elif trade.is_short:
                      lower_closes = [self.data.Close[i+1] < self.data.Close[i]  for i in range(-1*(self.__n_bars +1),-1)]
                      if all(lower_closes):
                       trade.close()


class SwingExitStrategy(Strategy):
    """
    Exit based on swing low and highs 
    """

    _profit_bars = 10
    _loss_bars   = 7 


    def init(self):
        super().init()

        self._profit_lookback = -2 + (-1*self._profit_bars)
        self._loss_lookback   = -2 + (-1*self._loss_bars)

    def set_swing_bars(self, profit_bars: int = 10, loss_bars: int = 7):
        """
        Set the swing bars
        """ 

        self._profit_bars = profit_bars
        self._loss_bars   = loss_bars 
    

    def next(self):
        super().next()

        for trade in self.trades:
    
            long_profit_exit = max(self.data.High[self._profit_lookback:-2])
            long_loss_exit   = min(self.data.Low[self._loss_lookback:-2])

            short_profit_exit = min(self.data.Low[self._profit_lookback:-2])
            short_loss_exit   = max(self.data.High[self._loss_lookback:-2])



            
            if trade.is_long:     
                if (self.data.Close[-1] > long_profit_exit) or (self.data.Close[-1] < long_loss_exit):
                     trade.close()

            elif trade.is_short:
                if (self.data.Close[-1] > short_loss_exit) or (self.data.Close[-1] < short_profit_exit):
                    trade.close()       


class FirstProfitExitStrategy(Strategy):
    """
    Exit on the first opportunity of profit
    """

    def init(self):
        super().init()
        self._current_trade = -1 

    def next(self):
        super().next()


        for trade in self.trades:

            if self._current_trade == -1:
                    self._current_trade  = trade.entry_bar

                 
            if self._current_trade  == trade.entry_bar and  trade.pl > 0: 
                    trade.close()
                    self._current_trade  = -1
