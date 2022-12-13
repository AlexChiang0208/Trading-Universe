import os
import glob
import numpy as np
import pandas as pd
import datetime as dt

BTCUSDT_ufutures_path = glob.glob("raw_klines/BTCUSDT_ufutures/*.zip")
ETHUSDT_ufutures_path = glob.glob("raw_klines/ETHUSDT_ufutures/*.zip")

BTCUSDT_ufutures_path = sorted(BTCUSDT_ufutures_path)
ETHUSDT_ufutures_path = sorted(ETHUSDT_ufutures_path)

columns_name = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'closeTime', 'quoteVolume', 'numTrade', 'takerBuyVolume', 'takerBuyQuoteVolume', 'ignore']

# %%

df_btc = pd.DataFrame()

for path in BTCUSDT_ufutures_path:

    temp = pd.read_csv(path)
    temp.columns = columns_name
    temp['openTime'] = [pd.to_datetime(dt.datetime.fromtimestamp(int(i/1000))) for i in temp['openTime']]
    temp['closeTime'] = [pd.to_datetime(dt.datetime.fromtimestamp(int(i/1000))) for i in temp['closeTime']]
    temp = temp.drop('ignore', axis=1)
    temp = temp.sort_values('openTime', ascending=True)
    temp['takerSellVolume'] = temp['Volume'] - temp['takerBuyVolume']
    temp['takerSellQuoteVolume'] = temp['quoteVolume'] - temp['takerBuyQuoteVolume']
    temp['avgTradeVolume'] = temp['quoteVolume'] / temp['numTrade']

    df_btc = pd.concat([df_btc, temp], axis=0)

df_btc = df_btc.sort_values('openTime', ascending=True)
df_btc = df_btc.set_index('openTime')
df_btc.to_csv('tidy_data/binance_um_1m_btcusdt.csv')

# %%

df_eth = pd.DataFrame()

for path in ETHUSDT_ufutures_path:

    temp = pd.read_csv(path)
    temp.columns = columns_name
    temp['openTime'] = [pd.to_datetime(dt.datetime.fromtimestamp(int(i/1000))) for i in temp['openTime']]
    temp['closeTime'] = [pd.to_datetime(dt.datetime.fromtimestamp(int(i/1000))) for i in temp['closeTime']]
    temp = temp.drop('ignore', axis=1)
    temp = temp.sort_values('openTime', ascending=True)
    temp['takerSellVolume'] = temp['Volume'] - temp['takerBuyVolume']
    temp['takerSellQuoteVolume'] = temp['quoteVolume'] - temp['takerBuyQuoteVolume']
    temp['avgTradeVolume'] = temp['quoteVolume'] / temp['numTrade']

    df_eth = pd.concat([df_eth, temp], axis=0)

df_eth = df_eth.sort_values('openTime', ascending=True)
df_eth = df_eth.set_index('openTime')
df_eth.to_csv('tidy_data/binance_um_1m_ethusdt.csv')


# %%

import pandas as pd

df_btc = pd.read_csv('tidy_data/binance_um_1m_btcusdt.csv', parse_dates=True, index_col='openTime')
df_btc = df_btc.drop('closeTime', axis=1)

df_eth = pd.read_csv('tidy_data/binance_um_1m_ethusdt.csv', parse_dates=True, index_col='openTime')
df_eth = df_eth.drop('closeTime', axis=1)

df_ethbtc = pd.DataFrame()

df_ethbtc['Open'] = df_eth['Open'] / df_btc['Open']
df_ethbtc['High'] = df_eth['High'] / df_btc['High']
df_ethbtc['Low'] = df_eth['Low'] / df_btc['Low']
df_ethbtc['Close'] = df_eth['Close'] / df_btc['Close']
df_ethbtc['btc_volume'] = df_btc['quoteVolume']
df_ethbtc['btc_numTrade'] = df_btc['numTrade']
df_ethbtc['btc_buyVolume'] = df_btc['takerBuyQuoteVolume']
df_ethbtc['btc_sellVolume'] = df_btc['takerSellQuoteVolume']
df_ethbtc['btc_avgTradeVolume'] = df_btc['avgTradeVolume']
df_ethbtc['eth_volume'] = df_eth['quoteVolume']
df_ethbtc['eth_numTrade'] = df_eth['numTrade']
df_ethbtc['eth_buyVolume'] = df_eth['takerBuyQuoteVolume']
df_ethbtc['eth_sellVolume'] = df_eth['takerSellQuoteVolume']
df_ethbtc['eth_avgTradeVolume'] = df_eth['avgTradeVolume']
df_ethbtc['Volume'] = df_ethbtc['btc_volume'] + df_ethbtc['eth_volume']

df_ethbtc.to_csv('tidy_data/binance_um_1m_ethbtc_combine.csv')



