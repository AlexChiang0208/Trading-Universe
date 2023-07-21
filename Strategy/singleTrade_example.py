# %%
import os
import time
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt

import talib
from talib import abstract

# file path should under level first
os.chdir("..")
print(os.getcwd())

from module.data import get_tidyData, update_newData, Data
from module.backtest import backtesting, dictType_output
from module.visualize import Performance, PercentageReturnPlot

# %%

df_btc_origin = get_tidyData(symbol='BTCUSDT', data_type='ufutures')
df_btc_spot = get_tidyData(symbol='BTCUSDT', data_type='spot')
df_eth_origin = get_tidyData(symbol='ETHUSDT', data_type='ufutures')

# %%

df_btc_origin = update_newData(df_btc_origin, symbol ='BTCUSDT', data_type='ufutures')
df_btc_spot = update_newData(df_btc_spot, symbol ='BTCUSDT', data_type='spot')
df_eth_origin = update_newData(df_eth_origin, symbol ='ETHUSDT', data_type='ufutures')

# %%

fund = 100
data = Data(df_symbol=df_btc_origin, rule='30T')

len1 = 12
len2 = 2*len1

data.df['rsi'] = talib.RSI(data.df['Close'], len1)
data.df['rsi_r1'] = data.df['rsi'].rolling(len1).mean()
data.df['rsi_r2'] = data.df['rsi'].rolling(len2).mean()

## entry condition
entryLong = (data.df['rsi_r1'] > data.df['rsi_r2']) & (data.df['rsi_r1'] > 70)
entrySellShort =  (data.df['rsi_r1'] < data.df['rsi_r2']) & (data.df['rsi_r1'] < 30)

## exit condition
exitShort = data.df['rsi_r1'] < 30
exitBuyToCover = data.df['rsi_r1'] > 70

data.type_setting(entryLong, entrySellShort, exitShort, exitBuyToCover)
output_dict = dictType_output(backtesting(data.input_arr, exit_profitOut=True, 
                                          exParam2=0.02, fund=fund))

# %%

# plot & result
result = Performance(data.df['Open'], output_dict, data.idx, fund=fund, Name='RSI Strategy')
result.calculate_result()
result.show_performance()
# result.draw_unrealized_profit()
result.draw_realized_profit()
result.draw_equity_curve(text_position='2022-01-01')
# result.draw_monthly_equity(text_position='2022-01-01')
# result.draw_daily_distribution(bins=40)
# result.draw_hold_position()

# %%
