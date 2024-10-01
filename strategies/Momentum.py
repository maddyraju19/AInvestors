import backtrader as bt
import yfinance as yf

class trendFollowingStrategy(bt.Strategy):
    def __init__(self):
        while True:
            try:
                bools = []
                bools.append(bool(input("Enter 'True' or 'False' to add the RSI indicator: ")))
                bools.append(bool(input("Enter 'True' or 'False' to add the MACD indicator: ")))
                break
            except ValueError:
                print("Invalid input. Please enter 'True' or 'False'.")
                continue
        
        stoploss = int(input("Enter the stop loss: "))
        short_period = int(input("Enter the short moving average period: "))
        long_period = int(input("Enter the long moving average period: "))
        threshigh = int(input("Enter the upper threshold: "))
        threshlow = int(input("Enter the lower threshold: "))
        
        self.RSItest = bools[0]
        self.MACDtest = bools[1]
        self.stoploss = stoploss
        self.threshigh = threshigh
        self.threshlow = threshlow
        self.dataclose = self.datas[0].close
        self.short_period = short_period
        self.long_period = long_period
        self.positionsize = int(input("Max position size: "))
        
        # Trend-following indicators (Moving Averages)
        self.short_ma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.short_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.dataclose, period=self.long_period)

        if self.RSItest == True:
            self.rsi = bt.indicators.RSI(self.dataclose, period=self.short_period)
        if self.MACDtest == True:
            self.macd = bt.indicators.MACD(self.dataclose, period_me1=int(input("Fast period: ")), 
                                           period_me2=int(input("Long Period: ")), 
                                           period_signal=int(input("Signal period: ")))

    def next(self):
        rsi_value = self.rsi[0] if self.RSItest else None
        macd_value = self.macd[0] if self.MACDtest else None
        macd_signal = self.macd.signal[0] if self.MACDtest else None

        # Trend-following buy signal: short MA crosses above long MA
        if self.short_ma > self.long_ma:
            if self.position.size < self.positionsize:
                self.buy()

        # Trend-following sell signal: short MA crosses below long MA
        elif self.short_ma < self.long_ma:
            if self.position.size * -1 < self.positionsize:
                self.sell()

        # Optional indicators (RSI/MACD)
        if self.RSItest and rsi_value is not None:
            if rsi_value > self.threshigh:
                self.sell()
            elif rsi_value < self.threshlow:
                self.buy()

        if self.MACDtest and macd_value is not None and macd_signal is not None:
            if macd_value > macd_signal:
                self.buy()
            elif macd_value < macd_signal:
                self.sell()

        # Global stop-loss check
        if self.broker.getvalue() < self.broker.get_cash() * (1 - (self.stoploss / 100)):
            self.close()
            print('Stop loss triggered, closing all positions.')

def runStrategy():
    cerebro = bt.Cerebro()
    cerebro.broker.set_cash(1000)

    data = yf.download("SPY")
    bt_data = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(bt_data)
    
    cerebro.addstrategy(trendFollowingStrategy)
    
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

