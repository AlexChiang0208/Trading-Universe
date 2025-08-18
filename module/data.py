import time
import glob
import requests
import numpy as np
import pandas as pd
import datetime as dt
from tqdm import tqdm
from joblib import Parallel, delayed
from concurrent.futures import ThreadPoolExecutor

import talib
from talib import abstract

from .operators import ts_continuous_atr

def get_data(error_path: list, combine_list: list, path: str):

    try:
        temp = pd.read_csv(path, header=None, index_col=None)
        if temp.iloc[0,0] == "open_time":
            temp = temp.iloc[1:]
        combine_list.append(temp)
    except Exception as e:
        print(f'error : {e} ; path : {path}')
        error_path.append(path)
        pass

    return


def convert_mixed_timestamp(df: pd.DataFrame, col: str = 'openTime') -> pd.DataFrame:

    is_us = df[col].map(lambda x: len(str(int(x))) >= 16)
    df_us = df[is_us].copy()
    df_ms = df[~is_us].copy()

    df_us[col] = pd.to_datetime(df_us[col], unit='us')
    df_ms[col] = pd.to_datetime(df_ms[col], unit='ms')

    df_out = pd.concat([df_us, df_ms])
    df_out = df_out.sort_values(col, ascending=True)

    return df_out


def get_tidyData_v2(symbol='BTCUSDT', data_type='ufutures', bar_interval='5m', max_workers=5):

    '''using thread pool to get data'''

    def get_data_func(error_path, combine_list, ticker_path, max_workers):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(lambda path: get_data(error_path, combine_list, path), ticker_path)

    columns_name = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'closeTime', 'quoteVolume', 'numTrade', 'takerBuyVolume', 'takerBuyQuoteVolume', 'ignore']
    ticker_path = glob.glob(f"raw_klines_{bar_interval}/{symbol}_{data_type}/*.zip")
    ticker_path = sorted(ticker_path)
    
    error_path = []
    combine_list = []
    get_data_func(error_path, combine_list, ticker_path, max_workers)

    if len(error_path) != 0:
        print(f'{symbol}_{data_type} return error_path; download again!')
        return error_path
    
    else:
        df_ = pd.concat(combine_list, axis=0)
        df_.columns = columns_name
        df_ = convert_mixed_timestamp(df_, 'openTime')
        df_ = df_.drop(['ignore', 'closeTime'], axis=1)
        # df_ = df_.sort_values('openTime', ascending=True)
        df_ = df_.set_index('openTime')
        df_ = df_.astype(float)
        df_['takerSellVolume'] = df_['Volume'] - df_['takerBuyVolume']
        df_['takerSellQuoteVolume'] = df_['quoteVolume'] - df_['takerBuyQuoteVolume']
        df_['avgTradeVolume'] = df_['quoteVolume'] / df_['numTrade']
        df_ = df_[~df_.index.duplicated(keep='first')]
        return df_


def get_tidyData(symbol='BTCUSDT', data_type='ufutures', bar_interval='5m'):

    columns_name = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'closeTime', 'quoteVolume', 'numTrade', 'takerBuyVolume', 'takerBuyQuoteVolume', 'ignore']
    ticker_path = glob.glob(f"raw_klines_{bar_interval}/{symbol}_{data_type}/*.zip")
    ticker_path = sorted(ticker_path)
    
    error_path = []
    combine_list = []
    for path in ticker_path:
        get_data(error_path, combine_list, path)

    if len(error_path) != 0:
        print(f'{symbol}_{data_type} return error_path; download again!')
        return error_path
    
    else:
        df_ = pd.concat(combine_list, axis=0)
        df_.columns = columns_name
        df_ = convert_mixed_timestamp(df_, 'openTime')
        df_ = df_.drop(['ignore', 'closeTime'], axis=1)
        # df_ = df_.sort_values('openTime', ascending=True)
        df_ = df_.set_index('openTime')
        df_ = df_.astype(float)
        df_['takerSellVolume'] = df_['Volume'] - df_['takerBuyVolume']
        df_['takerSellQuoteVolume'] = df_['quoteVolume'] - df_['takerBuyQuoteVolume']
        df_['avgTradeVolume'] = df_['quoteVolume'] / df_['numTrade']
        df_ = df_[~df_.index.duplicated(keep='first')]
        return df_


def update_newData(df_origin, symbol='BTCUSDT', data_type='ufutures', bar_interval='5m'):
    
    if data_type == 'ufutures':
        base_url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={bar_interval}&limit=1500'
    elif data_type == 'spot':
        base_url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={bar_interval}&limit=1000'

    if bar_interval == '1m':
        add_period = 60000
    elif bar_interval == '3m':
        add_period = int(60000 * 3)
    elif bar_interval == '5m':
        add_period = int(60000 * 5)
    elif bar_interval == '15m':
        add_period = int(60000 * 15)
    elif bar_interval == '30m':
        add_period = int(60000 * 30)
    elif bar_interval == '1h':
        add_period = int(60000 * 60)
    elif bar_interval == '4h':
        add_period = int(60000 * 240)
    elif bar_interval == '1d':
        add_period = int(60000 * 1440)

    data_list = []
    start_time = int(df_origin.index[-1].timestamp() * 1000)
    endTime = int((dt.datetime.now().timestamp()) * 1000)
    
    while start_time < endTime:
        url = f'{base_url}&startTime={start_time}&endTime={endTime}'
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                break
            else:
                error_json = response.json()
                print(f"{symbol} crawl error: {error_json}")

                if symbol == 'BTCSTUSDT': # temporarily solution
                    return df_origin

        data = response.json()

        if len(data) == 0:
            break
        else:
            data_list.extend(data)
            start_time = int(data[-1][0]) + add_period

    columns_name = ['openTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'closeTime', 'quoteVolume', 'numTrade', 'takerBuyVolume', 'takerBuyQuoteVolume', 'ignore']
    df_new = pd.DataFrame(data_list, columns=columns_name)
    df_new = df_new.astype(float)
    df_new = convert_mixed_timestamp(df_new, 'openTime')
    # df_new['openTime'] = pd.to_datetime(df_new['openTime'], unit='ms')
    df_new = df_new.drop(['ignore', 'closeTime'], axis=1)
    # df_new = df_new.sort_values('openTime', ascending=True)
    df_new = df_new.set_index('openTime')
    df_new['takerSellVolume'] = df_new['Volume'] - df_new['takerBuyVolume']
    df_new['takerSellQuoteVolume'] = df_new['quoteVolume'] - df_new['takerBuyQuoteVolume']
    df_new['avgTradeVolume'] = df_new['quoteVolume'] / df_new['numTrade']
    
    df_ = pd.concat([df_origin, df_new])
    df_ = df_[~df_.index.duplicated(keep='first')]

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
    # df_pair_['Volatility'] = df_spread_close.resample(rule=rule, closed='left', label='left').std()
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
        self.df = self.df[~self.df['Close'].isnull()] #run re-sample will have missing data
        
        if startTime == None:
            startTime = self.df.index[0]

        if endTime == None:
            endTime = self.df.index[-1]
        
        self.startTime = startTime
        self.endTime = endTime
        self.idx = self.df.loc[startTime:endTime].index

    def type_setting(self, entryLong, entrySellShort, exitShort, exitBuyToCover, 
                     vol_type='STD', vol_length=22, longOnly=False, shortOnly=False):
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
        elif vol_type == 'continuous_atr':
            atr_df = ts_continuous_atr(high=self.df['High'], low=self.df['Low'], window=vol_length)
            self.vol_arr = np.array(atr_df.loc[self.startTime:self.endTime])

        self.input_arr = np.array([self.open_arr, self.high_arr, self.low_arr, self.close_arr, 
                                   self.entryLong_arr, self.entrySellShort_arr, 
                                   self.exitShort_arr, self.exitBuyToCover_arr, 
                                   self.vol_arr])


class DataPair:

    def __init__(self, df_symbolA, df_symbolB, rule, startTime=None, endTime=None):

        self.df_pair, self.dfA, self.dfB = resample_pair(df_symbolA, df_symbolB, rule=rule)

        self.dfA = self.dfA[~self.dfA['Close'].isnull()]
        self.dfB = self.dfB[~self.dfB['Close'].isnull()]
        intersection = self.dfA.index.intersection(self.dfB.index)
        self.dfA = self.dfA.loc[intersection]
        self.dfB = self.dfB.loc[intersection]
        self.df_pair = self.df_pair.loc[intersection]

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


def get_symbol_df(typeName, symbol, bar_interval, version):

    '''example of symbol: BTC'''

    if typeName == 'spot' and symbol[:4] == '1000':
        adjust_1000 = True
        adj_symbol = symbol[4:]
    else:
        adjust_1000 = False
        adj_symbol = symbol

    try:
        if version == 1:
            df = get_tidyData(symbol=f"{adj_symbol}USDT", data_type=typeName, bar_interval=bar_interval)
        elif version == 2:
            df = get_tidyData_v2(symbol=f"{adj_symbol}USDT", data_type=typeName, bar_interval=bar_interval, max_workers=5)
        state_bool = 1

    except:
        df = None
        state_bool = 0

    return typeName, symbol, df, state_bool, adjust_1000


def get_symbol_name(typeName='ufutures', bar_interval='1h'):

    '''exclude delivery'''
    _ufutures = glob.glob(f"raw_klines_{bar_interval}/*_ufutures")
    ufutures_list = [i.split('/')[1].split('_ufutures')[0] for i in _ufutures]
    ufutures_list = [i[:-4] for i in ufutures_list if i[-4:]=='USDT']

    if typeName == 'spot':
        _spot = glob.glob(f"raw_klines_{bar_interval}/*_spot")
        spot_list_ = [i.split('/')[1].split('_spot')[0] for i in _spot]
        spot_list_ = [i[:-4] for i in spot_list_ if i[-4:]=='USDT']

        spot_list = []
        for s in spot_list_:
            '''adjust to same name of ufutures'''
            if '1000'+s in ufutures_list:
                spot_list.append('1000'+s)
            else:
                spot_list.append(s)
    
    if typeName == 'ufutures':
        symbol_list = ufutures_list
    elif typeName == 'spot':
        symbol_list = spot_list

    return symbol_list


def get_symbol_dict(df_dict, typeName, symbol_list, empty_list=[], bar_interval='1h', version=1, update=False, n_jobs=2, crawl_sleep=0.5):

    '''
    - spot also uses the symbol name of futures
    - Crawler cannot be too fast or it'll be banned :(
    '''

    def gernerate_tasks(func, symbol_list, typeName, bar_interval, version):
        for symbol in symbol_list:
            yield delayed(func)(typeName, symbol, bar_interval, version)

    tasks = gernerate_tasks(get_symbol_df, symbol_list, typeName, bar_interval, version)
    result = Parallel(n_jobs=-1)(tqdm(tasks, f"loading {typeName} {bar_interval} klines from local db", total=len(symbol_list)))
    
    for output_list in result:
        if output_list[3] == 0:
            empty_list.append(output_list[1])
            symbol_list.remove(output_list[1])
        else:
            if update == False and output_list[4] == True:
                df_ = output_list[2]
                df_['Open'] = df_['Open'] * 1000
                df_['High'] = df_['High'] * 1000
                df_['Low'] = df_['Low'] * 1000
                df_['Close'] = df_['Close'] * 1000
                df_['Volume'] = df_['Volume'] / 1000
                df_['takerBuyVolume'] = df_['takerBuyVolume'] / 1000
                df_['takerSellVolume'] = df_['takerSellVolume'] / 1000
                df_dict[f"{output_list[1]}_{output_list[0]}"] = df_
            else:
                df_dict[f"{output_list[1]}_{output_list[0]}"] = output_list[2]

    # check again
    while True:
        typeName_key = [i for i in list(df_dict.keys()) if i.split('_')[1] == typeName]
        dict_symbols = [i.split(f'_{typeName}')[0] for i in typeName_key]
        load_again = list(set(dict_symbols) ^ set(symbol_list))

        if len(load_again) == 0:
            break
        else:
            print(f'load again: {load_again}')
            for symbol in load_again:
                typeName_, symbol_, df_, state_bool_, adjust_1000_ = get_symbol_df(typeName, symbol, bar_interval, version)

                if state_bool_ == 0:
                    empty_list.append(symbol_)
                    symbol_list.remove(symbol_)
                else:
                    if update == False and adjust_1000_ == True:
                        df_['Open'] = df_['Open'] * 1000
                        df_['High'] = df_['High'] * 1000
                        df_['Low'] = df_['Low'] * 1000
                        df_['Close'] = df_['Close'] * 1000
                        df_['Volume'] = df_['Volume'] / 1000
                        df_['takerBuyVolume'] = df_['takerBuyVolume'] / 1000
                        df_['takerSellVolume'] = df_['takerSellVolume'] / 1000
                    else:
                        df_dict[f"{symbol_}_{typeName_}"] = df_

    # update new data
    if update == True:
        
        def update_func(df_old, symbol, typeName, bar_interval):

            '''Binance will block IP if running too many requests'''

            if typeName == 'spot' and symbol[:4] == '1000':
                adjust_1000 = True
                adj_symbol = f"{symbol[4:]}USDT"
            else:
                adjust_1000 = False
                adj_symbol = f"{symbol}USDT"

            adj_symbol = adj_symbol.upper()
            df_new = update_newData(df_old, adj_symbol, typeName, bar_interval)

            if adjust_1000 == True:
                df_new['Open'] = df_new['Open'] * 1000
                df_new['High'] = df_new['High'] * 1000
                df_new['Low'] = df_new['Low'] * 1000
                df_new['Close'] = df_new['Close'] * 1000
                df_new['Volume'] = df_new['Volume'] / 1000
                df_new['takerBuyVolume'] = df_new['takerBuyVolume'] / 1000
                df_new['takerSellVolume'] = df_new['takerSellVolume'] / 1000

            time.sleep(crawl_sleep)

            return typeName, symbol, df_new
        
        def gernerate_tasks2(func, symbol_list, typeName, bar_interval):
            for symbol in symbol_list:
                df_old = df_dict[f"{symbol}_{typeName}"]
                yield delayed(func)(df_old, symbol, typeName, bar_interval)

        tasks = gernerate_tasks2(update_func, symbol_list, typeName, bar_interval)
        result2 = Parallel(n_jobs=n_jobs)(tqdm(tasks, f"update {typeName} {bar_interval} new klines from binance", total=len(symbol_list)))
        
        for output_list in result2:
            df_dict[f"{output_list[1]}_{output_list[0]}"] = output_list[2]

    result_dict = {'df_dict': df_dict, 'empty_list': empty_list, 'symbol_list': symbol_list}

    return result_dict
