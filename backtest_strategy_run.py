import pandas_ta as ta
import pandas as pd
#import numpy as np
import yfinance as yf
import vectorbt as vbt
#from datetime import datetime
from tvDatafeed import TvDatafeed, Interval
import config_api
import matplotlib.pyplot as plt




user = config_api.tradingview_user
password = config_api.tradingview_password
tv = TvDatafeed(user, password, chromedriver_path= None)

########## input strategy and symbol #################

#symbol = 'BNBUSDT'
symbols = ['BNBUSDT', 'BTCUSDT', 'ETHUSDT', 'XRPUSDT', 'ADAUSDT']
rsi_bm = 50
obv_fast = 5
obv_slow = 35
ma_type = 'ema'
ma_fast = 5
ma_slow = 15



#data = tv.get_hist(symbol= symbol, exchange= 'BINANCE', interval= Interval.in_daily, n_bars= 5000)

#df = data.copy()

for i in symbols:
    data = tv.get_hist(symbol= i, exchange= 'BINANCE', interval= Interval.in_daily, n_bars= 5000)
    df = data.copy()
    df['rsi'] = df.ta.rsi(length=14)
    ma_obv = df.ta.ma_obv(fast= obv_fast, slow= obv_slow, ma_type= 'ema', append= True)
    ma_cross = df.ta.ma_cross(fast= ma_fast, slow= ma_slow, ma_type= 'ema', append= True)

    symbol_str = f'{df.symbol}'.split()[3].split(':')[1]
    strat = symbol_str + '_' + ma_obv.name + '_rsi50' + '_' + ma_cross.name

    df.loc[df['rsi'] >= rsi_bm, 'strength'] = 1
    df.loc[df['rsi'] < rsi_bm, 'strength'] = -1
    df.loc[df[f'{ma_obv.name}'] > 0, 'vol_in'] = 1
    df.loc[df[f'{ma_obv.name}'] < 0, 'vol_in'] = -1
    df.loc[df[f'{ma_cross.name}'] > 0, 'ma_cross'] = 1
    df.loc[df[f'{ma_cross.name}'] < 0, 'ma_cross'] = -1

    df['signal'] = (df['vol_in'] == 1) & (df['strength'] == 1) & (df['ma_cross'] == 1)

    df_signal = df[['open', 'close', 'rsi', f'{ma_obv.name}', 'vol_in', 'strength', 'ma_cross', 'signal']] # 'vol_in'

    df_signal['next_open'] = df_signal['open'].shift(-1)
    signal_vectorbt = df.ta.tsignals(df_signal['signal'], asbool= True)

    port = vbt.Portfolio.from_signals(
        df_signal['next_open'],
        entries= signal_vectorbt['TS_Entries'],
        exits= signal_vectorbt['TS_Exits'],
        freq= '1D',
        init_cash= 100,
        fees= 0.0025,
        slippage= 0.0050
    )

    port.plot().show()
    port.plot().write_image(file= f'../trading_signal_backtest/port_plot/{strat}.png', format= 'png', scale= 2.0)

    port.stats()
    return_adjust_vol = port.annualized_return() / port.annualized_volatility()
    ret_adj_risk = ['Annualized Return Adjust Vol', return_adjust_vol]
    print(ret_adj_risk)

    port_df = pd.DataFrame(port.stats()).rename(columns={0: strat})
    port_df = port_df.reset_index()
    series = pd.Series(ret_adj_risk, index= port_df.columns)
    port_df = port_df.append(series, ignore_index= True)
    port_df = port_df.set_index('index')

    #### if csv file is exist use this script
    port_csv = pd.read_csv('./crypto_tf1d_backtest.csv', index_col=0)
    port_csv[f'{strat}'] = port_df
    port_csv.to_csv('crypto_tf1d_backtest.csv', index= True)
    #### save portfolio records to cache in the same name as column in csv
    port.save(f'{strat}')


