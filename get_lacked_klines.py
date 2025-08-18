import os
import glob
import time
import pandas as pd
import urllib.request
from tqdm import tqdm

from module.data import get_tidyData

# Revise file
bar_interval = '5m' # 5m / 1h

df_dict = {}
parent_dir = f"raw_klines_{bar_interval}"
print(f'start {bar_interval}')

### load ufutures_symbols ###

_ufutures = glob.glob(f"raw_klines_{bar_interval}/*_ufutures")
ufutures_symbols = [i.split('/')[1].split('_ufutures')[0] for i in _ufutures]
ufutures_broken_list = []

while True:
    data_type = 'ufutures'
    load_again = list(set(ufutures_symbols) ^ set([i.split(f'_{data_type}')[0] for i in df_dict.keys() if i.split('_')[-1] == data_type]))
    if len(load_again) == 0:
        break
    else:
        for symbol in tqdm(load_again):
            try:
                df_dict[f'{symbol}_{data_type}'] = get_tidyData(symbol=symbol, data_type=data_type, bar_interval=bar_interval)
                if type(df_dict[f'{symbol}_{data_type}']) == list:
                    ufutures_broken_list.append(symbol)
            except Exception as e:
                print(f'other error: {e} ; symbol : {symbol}')
                ufutures_symbols.remove(symbol)
                continue


### load spot_symbols ###
_spot = glob.glob(f"raw_klines_{bar_interval}/*_spot")
spot_symbols = [i.split('/')[1].split('_spot')[0] for i in _spot]
spot_broken_list = []

while True:
    data_type = 'spot'
    load_again = list(set(spot_symbols) ^ set([i.split(f'_{data_type}')[0] for i in df_dict.keys() if i.split('_')[-1] == data_type]))
    if len(load_again) == 0:
        break
    else:
        for symbol in tqdm(load_again):
            try:
                df_dict[f'{symbol}_{data_type}'] = get_tidyData(symbol=symbol, data_type=data_type, bar_interval=bar_interval)
                if type(df_dict[f'{symbol}_{data_type}']) == list:
                    spot_broken_list.append(symbol)
            except Exception as e:
                print(f'other error: {e} ; symbol : {symbol}')
                spot_symbols.remove(symbol)
                continue


### re-download broken file ###

print(f'ufutures_broken_list : {ufutures_broken_list}')
print(f'spot_broken_list : {spot_broken_list}')

def urlretrieve_retry(url, file_path, max_attempts=5, delay=1):

    last_err = None

    for i in range(max_attempts):
        try:
            return urllib.request.urlretrieve(url, file_path)
        except Exception as e:
            if "Not Found" in str(e):
                return None
            last_err = e
            if i < max_attempts - 1:
                time.sleep(delay)

    print(f"Failed to download after {max_attempts} attempts: {url} -> {file_path}: {last_err}")
    
    return None

def redownload_data(df_dict, broken_list, data_type):

    if len(broken_list) != 0:

        if data_type == 'ufutures':
            base_url_daily = "https://data.binance.vision/data/futures/um/daily/klines"
            base_url_monthly = "https://data.binance.vision/data/futures/um/monthly/klines"

        elif data_type == 'spot':
            base_url_daily = "https://data.binance.vision/data/spot/daily/klines"
            base_url_monthly = "https://data.binance.vision/data/spot/monthly/klines"

        for symbol in broken_list:
            for broken_path in df_dict[f'{symbol}_{data_type}']:
                info = broken_path.split('/')[-1].replace('_','-').split(f'-{data_type}-')
                if len(info[1].split('-')) == 2:
                    base_url = base_url_monthly
                elif len(info[1].split('-')) == 3:
                    base_url = base_url_daily

                url = f"{base_url}/{info[0]}/{bar_interval}/{info[0]}-{bar_interval}-{info[1]}"
                print(url)

                path = f"{parent_dir}/{info[0]}_{data_type}"
                file_path = f"{path}/{info[0]}-{data_type}-{info[1]}"
                file_path = file_path.replace("-", "_")
                os.remove(file_path)
                time.sleep(1)
                r = urlretrieve_retry(url, file_path)

            df_dict[f'{symbol}_{data_type}'] = get_tidyData(symbol=symbol, data_type=data_type, bar_interval=bar_interval)

    return df_dict

df_dict = redownload_data(df_dict, ufutures_broken_list, 'ufutures')
df_dict = redownload_data(df_dict, spot_broken_list, 'spot')


### download lacked data ###

for dataList, typeName in zip([ufutures_symbols, spot_symbols], ["ufutures", "spot"]):

    if typeName == "ufutures":
        base_url = "https://data.binance.vision/data/futures/um/daily/klines"
    elif typeName == "spot":
        base_url = "https://data.binance.vision/data/spot/daily/klines"

    for data in tqdm(dataList):

        try:
            df = df_dict[f"{data}_{typeName}"]
            start_date = df.index[0].date()
            end_date = df.index[-1].date()
            date_range = pd.date_range(start_date, end_date, freq="D").date
            real_index = df.index.date

            lacked_day = (list(set(date_range)^set(real_index)))

            if len(lacked_day) >= 20:
                print(f'too much lacked_day in monthly data : {data} {len(lacked_day)}')
        
            if len(lacked_day) != 0:
                path = f"{parent_dir}/{data}_{typeName}"

                for date in tqdm(lacked_day):
                    date = str(date)
                    url = f"{base_url}/{data}/{bar_interval}/{data}-{bar_interval}-{date}.zip"
                    file_path = f"{path}/{data}-{typeName}-{date}.zip"
                    file_path = file_path.replace("-", "_")

                    if not os.path.exists(file_path):
                        r = urlretrieve_retry(url, file_path)

                        if r is not None:
                            print(f"add : {data} {date}")

        except Exception as e:
            print(f'[hand check] {data}_{typeName} error : {e}') ## hand check error-symbol
            continue
