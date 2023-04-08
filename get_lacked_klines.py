import os
import glob
import time
import pandas as pd
import urllib.request
from tqdm import tqdm

from module.data import get_tidyData

df_dict = {}
parent_dir = "raw_klines/"

# load ufutures_symbols
_ufutures = glob.glob(f"raw_klines/*_ufutures")
ufutures_symbols = [i.split('/')[1].split('_ufutures')[0] for i in _ufutures]
ufutures_broken_list = []

for j in tqdm(ufutures_symbols):
    try:
        df_dict[f'{j}_ufutures'] = get_tidyData(symbol=j, data_type='ufutures')
        if type(df_dict[f'{j}_ufutures']) == list:
            ufutures_broken_list.append(j)
    except Exception as e:
        print(f'other error: {e} ; symbol : {j}')
        ufutures_symbols.remove(j)
        continue


# load spot_symbols
_spot = glob.glob(f"raw_klines/*_spot")
spot_symbols = [i.split('/')[1].split('_spot')[0] for i in _spot]
spot_broken_list = []

for i in tqdm(spot_symbols):
    try:
        df_dict[f'{i}_spot'] = get_tidyData(symbol=i, data_type='spot')
        if type(df_dict[f'{i}_spot']) == list:
            spot_broken_list.append(i)
    except Exception as e:
        print(f'other error: {e} ; symbol : {i}')
        spot_symbols.remove(i)
        continue


# %%

# re-download ufutures broken file
print(f'ufutures_broken_list : {ufutures_broken_list}')

if len(ufutures_broken_list) != 0:
    for j in ufutures_broken_list:
        base_url_daily = "https://data.binance.vision/data/futures/um/daily/klines"
        base_url_monthly = "https://data.binance.vision/data/futures/um/monthly/klines"

        for broken_path in df_dict[f'{j}_ufutures']:
            info = broken_path.split('/')[-1].replace('_','-').split('-ufutures-')
            if len(info[1].split('-')) == 2:
                base_url = base_url_monthly
            elif len(info[1].split('-')) == 3:
                base_url = base_url_daily

            url = f"{base_url}/{info[0]}/1m/{info[0]}-1m-{info[1]}"
            print(url)

            path = os.path.join(parent_dir, f"{info[0]}_ufutures")
            file_path = os.path.join(path, f"{info[0]}-ufutures-{info[1]}")
            file_path = file_path.replace("-", "_")
            os.remove(file_path)
            time.sleep(1)
            urllib.request.urlretrieve(url, file_path)

        df_dict[f'{j}_ufutures'] = get_tidyData(symbol=j, data_type='ufutures')


# re-download spot broken file
print(f'spot_broken_list : {spot_broken_list}')

if len(spot_broken_list) != 0:
    for i in spot_broken_list:
        base_url_daily = "https://data.binance.vision/data/spot/daily/klines"
        base_url_monthly = "https://data.binance.vision/data/spot/monthly/klines"

        for broken_path in df_dict[f'{i}_spot']:
            info = broken_path.split('/')[-1].replace('_','-').split('-spot-')
            if len(info[1].split('-')) == 2:
                base_url = base_url_monthly
            elif len(info[1].split('-')) == 3:
                base_url = base_url_daily

            url = f"{base_url}/{info[0]}/1m/{info[0]}-1m-{info[1]}"
            print(url)

            path = os.path.join(parent_dir, f"{info[0]}_spot")
            file_path = os.path.join(path, f"{info[0]}-spot-{info[1]}")
            file_path = file_path.replace("-", "_")
            os.remove(file_path)
            time.sleep(1)
            urllib.request.urlretrieve(url, file_path)

        df_dict[f'{i}_spot'] = get_tidyData(symbol=i, data_type='spot')


# %%

### run error-symbol only ###
## sometimes get_tidyData cannot success to build a dataframe for some of symbol
## check those independently
# df_dict[f'INJUSDT_ufutures'] = get_tidyData(symbol='INJUSDT', data_type='ufutures')
# df_dict[f'XLMUSDT_spot'] = get_tidyData(symbol='XLMUSDT', data_type='spot')
# ufutures_symbols = ['INJUSDT']
# spot_symbols = ['XLMUSDT']
# spot_symbols = []


for dataList, typeName in zip([ufutures_symbols, spot_symbols], ["ufutures", "spot"]):

    if typeName == "ufutures":
        base_url = "https://data.binance.vision/data/futures/um/daily/klines"
    elif typeName == "spot":
        base_url = "https://data.binance.vision/data/spot/daily/klines"

    for data in tqdm(dataList):
        try:
            df = df_dict[f'{data}_{typeName}']

            start_date = df.index[0].date()
            end_date = df.index[-1].date()
            date_range = pd.date_range(start_date, end_date, freq="D").date
            real_index = df.index.date

            lacked_day = (list(set(date_range)^set(real_index)))

            if len(lacked_day) >= 10:
                print(f'too much lacked_day in monthly data : {data} {len(lacked_day)}')
                # continue
        
            if len(lacked_day) != 0:

                path = os.path.join(parent_dir, f"{data}_{typeName}")

                for date in tqdm(lacked_day):

                    date = str(date)
                    url = f"{base_url}/{data}/1m/{data}-1m-{date}.zip"

                    file_path = os.path.join(path, f"{data}-{typeName}-{date}.zip")
                    file_path = file_path.replace("-", "_")

                    if not os.path.exists(file_path):
                        try:
                            urllib.request.urlretrieve(url, file_path)
                            print(f"add : {data} {date}")
                        except:
                            continue

        except Exception as e:
            print(f'{data}_{typeName} error : {e}') ## hand check each error-symbol
            continue

