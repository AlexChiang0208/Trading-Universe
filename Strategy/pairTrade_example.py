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

from module.data import get_tidyData, DataPair
from module.backtest import backtestingPair, dictType_output
from module.visualize import Performance, PercentageReturnPlot

# %%

df_btc_origin = get_tidyData(symbol='BTCUSDT', data_type='ufutures')
df_eth_origin = get_tidyData(symbol='ETHUSDT', data_type='ufutures')

# %%

fund = 100
data = DataPair(df_symbolA=df_btc_origin, df_symbolB=df_eth_origin, rule='1H')

# %%

len1 = 12
len2 = 2*len1

data.df_pair['rsi'] = talib.RSI(data.df_pair['Close'], len1)
data.df_pair['rsi_r1'] = data.df_pair['rsi'].rolling(len1).mean()
data.df_pair['rsi_r2'] = data.df_pair['rsi'].rolling(len2).mean()

## entry condition
entryLong = (data.df_pair['rsi_r1'] > data.df_pair['rsi_r2']) & (data.df_pair['rsi_r1'] > 70)
entrySellShort = (data.df_pair['rsi_r1'] < data.df_pair['rsi_r2']) & (data.df_pair['rsi_r1'] < 30)

## exit condition
exitShort = data.df_pair['rsi_r1'] < 30
exitBuyToCover = data.df_pair['rsi_r1'] > 70

data.type_setting(entryLong, entrySellShort, exitShort, exitBuyToCover)
output_dict = dictType_output(backtestingPair(data.input_arr, exit_profitOut=True, exParam2=0.03, fund=fund))

# plot & result
result = Performance(data.df_pair['Open'], output_dict, data.idx, fund=fund, Name='Pair Trading')
result.calculate_result()
result.show_performance()
result.draw_realized_profit()
result.draw_equity_curve(text_position='2022-04-10')


# %%
