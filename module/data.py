import glob
import numpy as np
import pandas as pd
import datetime as dt
from tqdm import tqdm

import talib
from talib import abstract


def get_tidyData(symbol='BTCUSDT', data_type='ufutures'):

    columns_name = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'closeTime', 'quoteVolume', 'numTrade', 'takerBuyVolume', 'takerBuyQuoteVolume', 'ignore']
    ticker_path = glob.glob(f"raw_klines/{symbol}_{data_type}/*.zip")
    ticker_path = sorted(ticker_path)

    combine_list = []
    for path in tqdm(ticker_path):
        temp = pd.read_csv(path, header=None, index_col=None)
        if temp.iloc[0,0] == "open_time":
            temp = temp.iloc[1:]
        combine_list.append(temp)

    df_ = pd.concat(combine_list, axis=0)
    df_.columns = columns_name
    df_['openTime']= pd.to_datetime(df_['openTime'], unit='ms')
    df_ = df_.drop(['ignore', 'closeTime'], axis=1)
    df_ = df_.sort_values('openTime', ascending=True)
    df_ = df_.set_index('openTime')
    df_ = df_.astype(float)
    df_['takerSellVolume'] = df_['Volume'] - df_['takerBuyVolume']
    df_['takerSellQuoteVolume'] = df_['quoteVolume'] - df_['takerBuyQuoteVolume']
    df_['avgTradeVolume'] = df_['quoteVolume'] / df_['numTrade']

    return df_


def resample_symbol(df_symbol, rule='1H'):

    df_ = pd.DataFrame()

    df_['Open'] = df_symbol.resample(rule=rule, closed='left', label='left').first()['Open']
    df_['High'] = df_symbol.resample(rule=rule, closed='left', label='left').max()['High']
    df_['Low'] = df_symbol.resample(rule=rule, closed='left', label='left').min()['Low']
    df_['Close'] = df_symbol.resample(rule=rule, closed='left', label='left').last()['Close']

    summ = df_symbol.resample(rule=rule, closed='left', label='left').sum()

    df_['Volume'] = summ['Volume']
    df_['quoteVolume'] = summ['quoteVolume']
    df_['numTrade'] = summ['numTrade']
    df_['takerBuyVolume'] = summ['takerBuyVolume']
    df_['takerBuyQuoteVolume'] = summ['takerBuyQuoteVolume']
    df_['takerSellVolume'] = summ['takerSellVolume']
    df_['takerSellQuoteVolume'] = summ['takerSellQuoteVolume']
    df_['avgTradeVolume'] = df_['quoteVolume'] / df_['numTrade']

    return df_


def resample_pair(df_symbolA, df_symbolB, rule='1H'):

    '''you can add more if you need, such as quantile(0.5) of diff of takerBuyQuoteVolume'''

    df_spread_open = df_symbolA['Open'] / df_symbolB['Open']
    df_spread_close = df_symbolA['Close'] / df_symbolB['Close']
    df_spread_volume = df_symbolA['quoteVolume'] + df_symbolB['quoteVolume']

    df_pair_ = pd.DataFrame()

    df_pair_['Open'] = df_spread_open.resample(rule=rule, closed='left', label='left').first()
    df_pair_['High'] = df_spread_close.resample(rule=rule, closed='left', label='left').max()
    df_pair_['Low'] = df_spread_close.resample(rule=rule, closed='left', label='left').min()
    df_pair_['Close'] = df_spread_close.resample(rule=rule, closed='left', label='left').last()
    df_pair_['Volume'] = df_spread_volume.resample(rule=rule, closed='left', label='left').sum()
    df_pair_['Mean'] = df_spread_close.resample(rule=rule, closed='left', label='left').mean()
    df_pair_['Volatility'] = df_spread_close.resample(rule=rule, closed='left', label='left').std()
    df_pair_['Qt1'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.1)
    df_pair_['Qt2'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.2)
    df_pair_['Qt3'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.3)
    df_pair_['Qt4'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.4)
    df_pair_['Qt5'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.5)
    df_pair_['Qt6'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.6)
    df_pair_['Qt7'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.7)
    df_pair_['Qt8'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.8)
    df_pair_['Qt9'] = df_spread_close.resample(rule=rule, closed='left', label='left').quantile(0.9)

    dfA_ = resample_symbol(df_symbolA, rule=rule)
    dfB_ = resample_symbol(df_symbolB, rule=rule)

    idx = df_pair_.dropna().index
    df_pair_ = df_pair_.loc[idx]
    dfA_ = dfA_.loc[idx]
    dfB_ = dfB_.loc[idx]

    return df_pair_, dfA_, dfB_


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

    def type_setting(self, entryLong, entrySellShort, exitShort, exitBuyToCover, 
                     vol_type='ATR', vol_length=22, longOnly=False, shortOnly=False):
        self.open_arr = np.array(self.df['Open'].loc[self.startTime:self.endTime])
        self.high_arr = np.array(self.df['High'].loc[self.startTime:self.endTime])
        self.low_arr = np.array(self.df['Low'].loc[self.startTime:self.endTime])
        self.close_arr = np.array(self.df['Close'].loc[self.startTime:self.endTime])
        self.entryLong_arr = np.array(entryLong.loc[self.startTime:self.endTime])
        self.entrySellShort_arr = np.array(entrySellShort.loc[self.startTime:self.endTime])
        self.exitShort_arr = np.array(exitShort.loc[self.startTime:self.endTime])
        self.exitBuyToCover_arr = np.array(exitBuyToCover.loc[self.startTime:self.endTime])

        if longOnly == True:
            noSignal = pd.Series([False]*len(self.df.index), index=self.df.index)
            self.entrySellShort_arr = np.array(noSignal.loc[self.startTime:self.endTime])
            self.exitBuyToCover_arr = np.array(noSignal.loc[self.startTime:self.endTime])

        if shortOnly == True:
            noSignal = pd.Series([False]*len(self.df.index), index=self.df.index)
            self.entryLong_arr = np.array(noSignal.loc[self.startTime:self.endTime])
            self.exitShort_arr = np.array(noSignal.loc[self.startTime:self.endTime])

        if vol_type == 'STD':
            std_df = self.df['Close'].rolling(vol_length).std()
            self.vol_arr = np.array(std_df.loc[self.startTime:self.endTime])
        elif vol_type == 'ATR':
            atr_df = talib.ATR(self.df['High'], self.df['Low'], self.df['Close'], vol_length)
            self.vol_arr = np.array(atr_df.loc[self.startTime:self.endTime])

        self.input_arr = np.array([self.open_arr, self.high_arr, self.low_arr, self.close_arr, 
                                   self.entryLong_arr, self.entrySellShort_arr, 
                                   self.exitShort_arr, self.exitBuyToCover_arr, 
                                   self.vol_arr])


class DataPair:

    def __init__(self, df_symbolA, df_symbolB, rule, startTime=None, endTime=None):

        self.df_pair, self.dfA, self.dfB = resample_pair(df_symbolA, df_symbolB, rule=rule)

        if startTime == None:
            startTime = self.df_pair.index[0]

        if endTime == None:
            endTime = self.df_pair.index[-1]
        
        self.startTime = startTime
        self.endTime = endTime
        self.idx = self.df_pair.loc[startTime:endTime].index

    def type_setting(self, entryLong, entrySellShort, exitShort, exitBuyToCover, spread_value='Close',
                     vol_type='STD', vol_value='Qt5', vol_length=22, longOnly=False, shortOnly=False):

        '''spread_arr use "Close" is same with single backtesting situation'''

        self.spreadOpen_arr = np.array(self.df_pair['Open'].loc[self.startTime:self.endTime])
        self.spread_arr = np.array(self.df_pair[spread_value].loc[self.startTime:self.endTime])
        self.openA_arr = np.array(self.dfA['Open'].loc[self.startTime:self.endTime])
        self.openB_arr = np.array(self.dfB['Open'].loc[self.startTime:self.endTime])
        self.closeA_arr = np.array(self.dfA['Close'].loc[self.startTime:self.endTime])
        self.closeB_arr = np.array(self.dfB['Close'].loc[self.startTime:self.endTime])
        self.entryLong_arr = np.array(entryLong.loc[self.startTime:self.endTime])
        self.entrySellShort_arr = np.array(entrySellShort.loc[self.startTime:self.endTime])
        self.exitShort_arr = np.array(exitShort.loc[self.startTime:self.endTime])
        self.exitBuyToCover_arr = np.array(exitBuyToCover.loc[self.startTime:self.endTime])

        if longOnly == True:
            noSignal = pd.Series([False]*len(self.df.index), index=self.df.index)
            self.entrySellShort_arr = np.array(noSignal.loc[self.startTime:self.endTime])
            self.exitBuyToCover_arr = np.array(noSignal.loc[self.startTime:self.endTime])

        if shortOnly == True:
            noSignal = pd.Series([False]*len(self.df.index), index=self.df.index)
            self.entryLong_arr = np.array(noSignal.loc[self.startTime:self.endTime])
            self.exitShort_arr = np.array(noSignal.loc[self.startTime:self.endTime])

        if vol_type == 'STD':
            std_df = self.df_pair[vol_value].rolling(vol_length).std()
            self.vol_arr = np.array(std_df.loc[self.startTime:self.endTime])
        elif vol_type == 'ATR':
            atr_df = talib.ATR(self.df_pair['High'], self.df_pair['Low'], self.df_pair['Close'], vol_length)
            self.vol_arr = np.array(atr_df.loc[self.startTime:self.endTime])

        self.input_arr = np.array([self.spreadOpen_arr, self.spread_arr, 
                                   self.openA_arr, self.openB_arr, 
                                   self.closeA_arr, self.closeB_arr, 
                                   self.entryLong_arr, self.entrySellShort_arr, 
                                   self.exitShort_arr, self.exitBuyToCover_arr, 
                                   self.vol_arr])

