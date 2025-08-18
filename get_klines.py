import os
import time
import requests
import pandas as pd
import datetime as dt
from tqdm import tqdm
import urllib.request
from joblib import Parallel, delayed
from concurrent.futures import ThreadPoolExecutor

start_date = "2020-1-1"
file_interval = 'monthly'
bar_interval = '1h'
data_need = 0

"""
source: data.binance.vision

start_date: Specify the start date of the data. For example, "2023-1-1".

file_interval: Define the file interval of the data; it can be either 'daily' or 'monthly'. 
If the period is set to 'monthly', you should run 'get_lacked_klines.py'.

bar_interval: Set the interval of the bars for the data. 
Possible values are: '1m' (1 minute), '1h' (1 hour), '1d' (1 day), '15m' (15 minutes).
Note: before setting this, a file named 'raw_klines_{bar_interval}' should be created first; and put it in .gitignore

data_need: Determine the type of data needed. 
0 means both futures and spot data are required.
1 means only futures data is required.
2 means only spot data is required.

Run again if the error : "<urlopen error [Errno 8] nodename nor servname provided, or not known>" occurs.
"""

### get data list ###

def get_symbols_list(type_):

    """
    This function should be used to update the 'symbols_list_4' when the number of spot symbols exceeds 3000.

    source of um symbol list
    https://data.binance.vision/?prefix=data/futures/um/monthly/klines/

    source of spot symbol list
    https://data.binance.vision/?prefix=data/spot/monthly/klines/
    """

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


binance_ufutures = get_symbols_list(type_='ufutures')
binance_ufutures = [i for i in binance_ufutures if (i[-4:] == 'USDT') & ("_" not in i)]
# binance_ufutures = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

# binance_spot = get_symbols_list(type_='spot')
binance_spot = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']

if len(binance_spot) > 3000:
    print("update crawler link")


# only customize 1000xxxx and save USDT spot
spots = []
if data_need != 1:
    for s in binance_ufutures:
        if s[-4:] == 'USDT':
            if s[:4] == '1000':
                symbol = s[4:]
            else:
                symbol = s
                
            if symbol in binance_spot:
                spots.append(symbol)

if  data_need != 2:
    ufutures = [i for i in binance_ufutures if i[-4:] != 'BUSD']
else:
    ufutures = []


### prepare date range and file ###

if file_interval == 'monthly':
    end_date = dt.datetime.now().date() + dt.timedelta(days=30)
    date_range = pd.date_range(start_date, end_date, freq="M")
    date_range = [str(i.date()).split('-')[0]+'-'+str(i.date()).split('-')[1] for i in date_range]
elif file_interval == 'daily':
    end_date = dt.datetime.now().date() + dt.timedelta(days=2)
    date_range = pd.date_range(start_date, end_date, freq="D").date

parent_dir = f"raw_klines_{bar_interval}"

# Remember to put it in .gitignore
if not os.path.exists(parent_dir):
    print(f"Remember to put {parent_dir}/ in .gitignore")
    os.mkdir(parent_dir)


### speeded-up function  ###

def download_data(typeName, ticker, date, parent_dir, file_interval, bar_interval):
    
    if typeName == "ufutures":
        base_url = f"https://data.binance.vision/data/futures/um/{file_interval}/klines"
    elif typeName == "spot":
        base_url = f"https://data.binance.vision/data/spot/{file_interval}/klines"

    path = f"{parent_dir}/{ticker}_{typeName}"
    if not os.path.exists(path):
        os.mkdir(path)

    url = f"{base_url}/{ticker}/{bar_interval}/{ticker}-{bar_interval}-{date}.zip"
    file_path = f"{path}/{ticker}-{typeName}-{date}.zip"
    file_path = file_path.replace("-", "_")

    if not os.path.exists(file_path):
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                urllib.request.urlretrieve(url, file_path)
                break  # 成功下載就跳出重試迴圈
            except Exception as e:
                # 若為 404 Not Found，直接放棄不再重試
                if "Not Found" in str(e):
                    # 若需要除錯也可在這裡印出訊息
                    # print(f"Not Found: {url}")
                    break
                # 最後一次仍失敗就印出錯誤；否則等待 1 秒再重試
                if attempt == max_attempts - 1:
                    print(f"Failed to download {ticker} {typeName} data for {date}: {e} ({file_path})")
                else:
                    time.sleep(1)  # 間隔 1 秒後重試

def download_data_func(typeName, ticker, date_range, parent_dir, file_interval, bar_interval, max_workers):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(lambda date: download_data(typeName, ticker, date, parent_dir, file_interval, bar_interval), date_range)


### get klines ###

def gernerate_tasks(func, symbols, typeName, max_workers):
    for symbol in symbols:
        yield delayed(func)(typeName, symbol, date_range, parent_dir, file_interval, bar_interval, max_workers)

if data_need != 2:
    tasks = gernerate_tasks(download_data_func, ufutures, "ufutures", max_workers=10)
    result = Parallel(n_jobs=-1)(tqdm(tasks, "download ufutures data", total=len(ufutures)))

if data_need != 1:
    tasks = gernerate_tasks(download_data_func, spots, "spot", max_workers=10)
    result = Parallel(n_jobs=-1)(tqdm(tasks, "download spot data", total=len(spots)))
