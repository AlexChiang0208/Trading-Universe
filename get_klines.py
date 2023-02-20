import pandas as pd
import datetime as dt
import zipfile
import urllib.request
import requests
import time
import os

## um symbol list copy from this link
## https://data.binance.vision/?prefix=data/futures/um/monthly/klines/

## spot symbol list copy from this link
## https://data.binance.vision/?prefix=data/spot/monthly/klines/


update_period = 'monthly' # daily / monthly (monthly should run get_lacked_klines.py)
start_date = "2020-4-1"


# %%

# 等 spot symbols > 3000 個，get_symbols_list function 要更新 symbols_list_4
def get_symbols_list(type_):
    if type_ == 'ufutures':
        r = requests.get(f'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/futures/um/daily/klines/')
        return list(map(lambda x:x.split('/')[1],r.text.split('klines')[2:]))
    elif type_ == 'spot':
        r = requests.get(f'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/')
        symbols_list_1 = list(map(lambda x:x.split('/')[1],r.text.split('klines')[2:]))
        r = requests.get('https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/&marker=data%2Fspot%2Fdaily%2Fklines%2FHOTETH%2F')
        symbols_list_2 = list(map(lambda x:x.split('/')[1],r.text.split('klines')[2:]))
        r = requests.get('https://s3-ap-northeast-1.amazonaws.com/data.binance.vision?delimiter=/&prefix=data/spot/daily/klines/&marker=data%2Fspot%2Fdaily%2Fklines%2FWAVESPAX%2F')
        symbols_list_3 = list(map(lambda x:x.split('/')[1],r.text.split('klines')[2:]))
        return list(set(symbols_list_1+symbols_list_2+symbols_list_3))

### update ###

binance_ufutures = get_symbols_list(type_='ufutures')
binance_spot = get_symbols_list(type_='spot')

# binance_ufutures = pd.read_csv('symbol_list/binance_ufutures_20230203.csv', header=None)[0]
# binance_ufutures = list(binance_ufutures)
# binance_ufutures = [i.split('/')[0] for i in binance_ufutures]

# binance_spot = pd.read_csv('symbol_list/binance_spot_20230203.csv', header=None)[0]
# binance_spot = list(binance_spot)
# binance_spot = [i.split('/')[0] for i in binance_spot]

## only customize 1000xxxx and save USDT spot

spots = []

for s in binance_ufutures:
    if s[-4:] == 'USDT':
        if s[:4] == '1000':
            symbol = s[4:]
        else:
            symbol = s
            
        if symbol in binance_spot:
            spots.append(symbol)

ufutures = [i for i in binance_ufutures if i[-4:] != 'BUSD']

# %%

## prepare date range and file

if update_period == 'monthly':
    end_date = dt.datetime.now().date() + dt.timedelta(days=30)
    date_range = pd.date_range(start_date, end_date, freq="M")
    date_range = [str(i.date()).split('-')[0]+'-'+str(i.date()).split('-')[1] for i in date_range]
elif update_period == 'daily':
    end_date = dt.datetime.now().date() + dt.timedelta(days=2)
    date_range = pd.date_range(start_date, end_date, freq="D").date

parent_dir = "raw_klines/"


## get klines

for dataType, typeName in zip([ufutures, spots], ["ufutures", "spot"]):

    if typeName == "ufutures":
        base_url = f"https://data.binance.vision/data/futures/um/{update_period}/klines"
    elif typeName == "spot":
        base_url = f"https://data.binance.vision/data/spot/{update_period}/klines"

    for ticker in dataType:
        print(ticker)
        path = os.path.join(parent_dir, f"{ticker}_{typeName}")

        if not os.path.exists(path):
            os.mkdir(path)

        for date in date_range:
            url = f"{base_url}/{ticker}/1m/{ticker}-1m-{date}.zip"
            file_path = os.path.join(path, f"{ticker}-{typeName}-{date}.zip")
            file_path = file_path.replace("-", "_")

            if not os.path.exists(file_path):
                try:
                    urllib.request.urlretrieve(url, file_path)
                    # print(f"success : {ticker} {date}")
                except:
                    # print(f"failed : {ticker} {date}")
                    continue

        # time.sleep(1)
