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

from module.data import get_tidyData, Data
from module.backtest import backtesting, dictType_output
from module.visualize import Performance, PercentageReturnPlot

# %%

df_btc_origin = get_tidyData(symbol='BTCUSDT', data_type='ufutures')
df_eth_origin = get_tidyData(symbol='ETHUSDT', data_type='ufutures')

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
output_dict = dictType_output(backtesting(data.input_arr, exit_profitOut=True, exParam2=0.015, end_trigger2='C', fund=fund))

# plot & result
result = Performance(data.df['Open'], output_dict, data.idx, fund=fund, Name='RSI Strategy')
result.calculate_result()
result.show_performance()
result.draw_unrealized_profit()
result.draw_realized_profit()
result.draw_equity_curve(text_position='2022-01-01')
result.draw_monthly_equity(text_position='2022-01-01')
result.draw_daily_distribution(bins=40)
result.draw_hold_position()


#%%

### example of multi-result ###

pnl_list = []
pnl_fee_list = []
time_list = []
fund = 100

for len1, len2 in zip(range(12,25), range(24,49)):
    for rule in ['30T', '1H']:
  
        data = Data(df_symbol=df_btc_origin, rule=rule)

        data.df['rsi'] = talib.RSI(data.df['Close'], len1)
        data.df['rsi_r1'] = data.df['rsi'].rolling(len1).mean()
        data.df['rsi_r2'] = data.df['rsi'].rolling(len2).mean()

        ## entry condition
        entryLong = (data.df['rsi_r1'] > data.df['rsi_r2']) & (data.df['rsi_r1'] > 70)
        entrySellShort =  (data.df['rsi_r1'] < data.df['rsi_r2']) & (data.df['rsi_r1'] < 30)

        ## exit condition
        exitShort = data.df['rsi_r1'] < 30
        exitBuyToCover = data.df['rsi_r1'] > 70

        data.type_setting(data.df, entryLong, entrySellShort, exitShort, exitBuyToCover)
        output_dict = dictType_output(backtesting(data.input_arr, exit_profitOut=True, exParam2=0.015, end_trigger2='C', fund=fund))
        
        pnl_list.append(output_dict['profit_list'])
        pnl_fee_list.append(output_dict['profit_fee_list'])
        time_list.append(data.idx)

df_combine_noFee = pd.DataFrame()
df_combine = pd.DataFrame()

for pnl, pnl_fee, time_ in zip(pnl_list, pnl_fee_list, time_list):
    df_temp1 = pd.DataFrame({'equity': np.cumsum(pnl)}, index=time_)
    df_temp2 = pd.DataFrame({'equity_fee': np.cumsum(pnl_fee)}, index=time_)

    df_combine_noFee = pd.concat([df_combine_noFee, df_temp1], axis=1)
    df_combine = pd.concat([df_combine, df_temp2], axis=1)
    
df_combine_noFee = df_combine_noFee.fillna(method='ffill').fillna(0)
df_combine = df_combine.fillna(method='ffill').fillna(0)

# Multi-Plot
ax = df_combine.plot(alpha=0.4, legend=False)
mn = df_combine.mean(axis=1)
mn.name = 'mean'
mn.plot(ax=ax, legend=True, grid=True, figsize=(12, 5), title='Profit and Loss', c='r')
plt.show();

# Single-Plot
return_series = ((mn + fund) / fund) * 100
percent_return_series = return_series - return_series.shift(1)

daily_plot = PercentageReturnPlot(percent_return_series)
daily_plot.equity_plot("My Strategy", "2022-01-01") 
# daily_plot.Month_equity_plot("My Strategy", "2022-09")
# daily_plot.Daily_Distribution_plot("My Strategy", bins=60)


# %%



