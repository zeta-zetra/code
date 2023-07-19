
from backtesting import Strategy, Backtest

class SimpleStrategy(Strategy):
    initsize   = 0.3
    mysize     = initsize
    strat_name = ""
    def init(self):
        super().init()


    def next(self):
        super().next()
        # if not self.position:
        if self.data.sell == 1 and len(self.trades) == 0:
            self.sell(size=self.mysize)

        elif self.data.buy == 1 and len(self.trades) == 0:
            self.buy(size=self.mysize) 
