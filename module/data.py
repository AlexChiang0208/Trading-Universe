import numpy as np
import pandas as pd
import datetime as dt

import talib
from talib import abstract


def get_tidyData(file_name, _type):
    df_ = pd.read_csv(f'tidy_data/{file_name}.csv', parse_dates=True, index_col='openTime')
    df_.index = [i+dt.timedelta(minutes=1) for i in df_.index]

    if _type == 'single':
        df_ = df_.drop('closeTime', axis=1)
    elif _type == 'pair':
        pass

    return df_


def resample_symbol(df_symbol, rule='1H'):

    df_ = pd.DataFrame()

    df_['Open'] = df_symbol.resample(rule=rule, closed='right', label='right').first()['Open']
    df_['High'] = df_symbol.resample(rule=rule, closed='right', label='right').max()['High']
    df_['Low'] = df_symbol.resample(rule=rule, closed='right', label='right').min()['Low']
    df_['Close'] = df_symbol.resample(rule=rule, closed='right', label='right').last()['Close']

    summ = df_symbol.resample(rule=rule, closed='right', label='right').sum()

    df_['Volume'] = summ['Volume']
    df_['quoteVolume'] = summ['quoteVolume']
    df_['numTrade'] = summ['numTrade']
    df_['takerBuyVolume'] = summ['takerBuyVolume']
    df_['takerBuyQuoteVolume'] = summ['takerBuyQuoteVolume']
    df_['takerSellVolume'] = summ['takerSellVolume']
    df_['takerSellQuoteVolume'] = summ['takerSellQuoteVolume']
    df_['avgTradeVolume'] = df_['quoteVolume'] / df_['numTrade']

    return df_


class Data:

    def __init__(self, df_symbol, rule, startTime=None, endTime=None):
        self.df = resample_symbol(df_symbol=df_symbol, rule=rule)
        
        if startTime == None:
            startTime = self.df.index[0]

        if endTime == None:
            endTime = self.df.index[-1]
        
        self.startTime = startTime
        self.endTime = endTime
        self.idx = self.df.loc[startTime:endTime].index

    def type_setting(self, df_ohlc, entryLong, entrySellShort, exitShort, exitBuyToCover, vol_type='ATR', vol_length=22):
        self.open_arr = np.array(df_ohlc['Open'].loc[self.startTime:self.endTime])
        self.high_arr = np.array(df_ohlc['High'].loc[self.startTime:self.endTime])
        self.low_arr = np.array(df_ohlc['Low'].loc[self.startTime:self.endTime])
        self.close_arr = np.array(df_ohlc['Close'].loc[self.startTime:self.endTime])
        self.entryLong_arr = np.array(entryLong.loc[self.startTime:self.endTime])
        self.entrySellShort_arr = np.array(entrySellShort.loc[self.startTime:self.endTime])
        self.exitShort_arr = np.array(exitShort.loc[self.startTime:self.endTime])
        self.exitBuyToCover_arr = np.array(exitBuyToCover.loc[self.startTime:self.endTime])

        if vol_type == 'STD':
            std_df = df_ohlc['Close'].rolling(vol_length).std()
            self.vol_arr = np.array(std_df.loc[self.startTime:self.endTime])
        elif vol_type == 'ATR':
            atr_df = talib.ATR(df_ohlc['High'], df_ohlc['Low'], df_ohlc['Close'], vol_length)
            self.vol_arr = np.array(atr_df.loc[self.startTime:self.endTime])

        self.input_arr = np.array([self.open_arr, self.high_arr, self.low_arr, self.close_arr, 
                                   self.entryLong_arr, self.entrySellShort_arr, 
                                   self.exitShort_arr, self.exitBuyToCover_arr, 
                                   self.vol_arr])


