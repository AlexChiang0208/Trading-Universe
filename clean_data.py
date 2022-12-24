import os
import glob
import numpy as np
import pandas as pd
import datetime as dt

BTCUSDT_ufutures_path = glob.glob("raw_klines/BTCUSDT_ufutures/*.zip")
BTCUSDT_ufutures_path = sorted(BTCUSDT_ufutures_path)

columns_name = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'closeTime', 'quoteVolume', 'numTrade', 'takerBuyVolume', 'takerBuyQuoteVolume', 'ignore']
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
