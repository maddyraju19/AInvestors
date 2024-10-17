import backtrader as bt
import yfinance as yf
import pandas as pd
import numpy as np
import datetime

class MovingAverageStrategy(bt.Strategy):
    def __init__(self, params):
        self.dataclose = self.datas[0].close
        period = params[0] * 21
        stratype = params[1]     
        if stratype == "sma":
            self.ma = bt.indicators.SMA(self.dataclose, period=period)
            self.shortma = bt.indicators.SMA(self.dataclose, period=10)
        elif stratype == "ema":
            self.ma = bt.indicators.EMA(self.dataclose, period=period)
            self.shortma = bt.indicators.EMA(self.dataclose, period=10)
        elif stratype == "dema":
            self.ma = bt.indicators.DoubleExponentialMovingAverage(self.dataclose, period=period)
            self.shortma = bt.indicators.DoubleExponentialMovingAverage(self.dataclose, period=10)  
        elif stratype == "tema":
            self.ma = bt.indicators.TripleExponentialMovingAverage(self.dataclose, period=period)
            self.shortma = bt.indicators.TripleExponentialMovingAverage(self.dataclose, period=10)
        else:
            raise ValueError("Unknown strategy type")
        self.posize = params[2]
        self.stop_loss = params[3]

        
    def next(self):
        if self.shortma >= self.ma:
            if self.position.size < self.posize:
                self.buy()
        else:
            if self.position.size * -1 < self.posize:
                self.sell()
        
        if self.broker.getvalue() < self.broker.get_cash() * (1 - (self.stop_loss / 100)):
            self.close()
                
def runStrategy(params):
    cerebro = bt.Cerebro()
    

    cerebro.broker.set_cash(1000)
    data = yf.download("SPY")
    bt_data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(bt_data)
    cerebro.addstrategy(MovingAverageStrategy(params))
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='mysharpe')
    cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name='myret')
    cerebro.addanalyzer(bt.analyzers.SQN, _name='mysqn')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='mydd')
    strat = cerebro.run()[0]
    
    final_portfolio_value = cerebro.broker.getvalue()
    final_cash = cerebro.broker.get_cash()
    annual_return = strat.analyzers.myret.get_analysis()
    sharpe_ratio = strat.analyzers.mysharpe.get_analysis()["sharperatio"]
    sqn = strat.analyzers.mysqn.get_analysis()["sqn"]
    drawdown = strat.analyzers.mydd.get_analysis()["drawdown"]

    # Return as a formatted string
    return f"""
    Final Portfolio Value: {final_portfolio_value:.2f}
    Final Cash: {final_cash:.2f}

    Annual Return: {annual_return}

    Sharpe Ratio: {sharpe_ratio}
    SQN: {sqn}
    DrawDown: {drawdown}
    """

