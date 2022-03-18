from gevent import config
from numpy import append
import pandas_ta as ta
import pandas as pd
#import numpy as np
import yfinance as yf
import vectorbt as vbt
#from datetime import datetime
from tvDatafeed import TvDatafeed, Interval
import config_api
import matplotlib.pyplot as plt

config
symbol = 'BTCUSDT'
exchange = 'BINANCE'
bars = 5000
interval = Interval.in_daily
symbols = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'ADAUSDT']

rsi_bm = 50
obv_fast = 5
obv_slow = 35
ma_type = 'ema'
ma_fast = 5
ma_slow = 15

def tv_plugin():
    user = config_api.tradingview_user  
    password = config_api.tradingview_password
    tv = TvDatafeed(user, password, chromedriver_path= None)

    return tv

def tv_import():
    df = tv_plugin().get_hist(
        symbol= symbol,
        exchange= exchange, 
        interval= interval, 
        n_bars= bars
    )
    df = pd.DataFrame(df)
    return df

def indicator():
    rsi_name = tv_import().ta.rsi(length= 14, append= True).name
    ma_obv = tv_import().ta.ma_obv(fast= obv_fast, slow= obv_slow, ma_type= 'ema', append= True).name
    ma_cross = tv_import().ta.ma_cross(fast= ma_fast, slow= ma_slow, ma_type= 'ema', append= True).name

    return ma_cross, ma_obv, rsi_name#, tv_import

    #df.ta.rsi(length= 14)

def strategyname():
    symbol_str = f'{tv_import().symbol}'.split()[3].split(':')[1]
    #strat = symbol_str + '_' + indicator().ma_obv + '_' + indicator().
    strat = symbol_str
    for i in indicator():
        strat = strat + i
    strat = symbol_str + indicator()
    return  strat, symbol_str