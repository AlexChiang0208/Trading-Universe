import pandas as pd
import datetime as dt
import zipfile
import urllib.request
import time
import os

## um symbol list copy from this link
## https://data.binance.vision/?prefix=data/futures/um/monthly/klines/

## spot symbol list copy from this link
## https://data.binance.vision/?prefix=data/spot/monthly/klines/


binance_ufutures = pd.read_csv('symbol_list/binance_ufutures_20230117.csv', header=None)[0]
binance_ufutures = list(binance_ufutures)
binance_ufutures = [i.split('/')[0] for i in binance_ufutures]

binance_spot = pd.read_csv('symbol_list/binance_spot_20230117.csv', header=None)[0]
binance_spot = list(binance_spot)
binance_spot = [i.split('/')[0] for i in binance_spot]


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


## prepare date range and file

start_date = "2020-11-1"
end_date = dt.datetime.now().date() + dt.timedelta(days=30)

date_range = pd.date_range(start_date, end_date, freq="M")
date_range = [str(i.date()).split('-')[0]+'-'+str(i.date()).split('-')[1] for i in date_range]

parent_dir = "raw_klines/"


## get klines

for dataType, typeName in zip([ufutures, spots], ["ufutures", "spot"]):

    if typeName == "ufutures":
        base_url = "https://data.binance.vision/data/futures/um/monthly/klines"
    elif typeName == "spot":
        base_url = "https://data.binance.vision/data/spot/monthly/klines"

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
                except:
                    print(f"failed : {ticker} {date}")
                    continue

        time.sleep(2)

