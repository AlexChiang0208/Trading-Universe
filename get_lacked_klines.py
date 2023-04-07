import os
import glob
import time
import pandas as pd
import urllib.request

from module.data import get_tidyData

df_dict = {}
parent_dir = "raw_klines/"

_ufutures = glob.glob(f"raw_klines/*_ufutures")
ufutures_symbols = [i.split('/')[1].split('_ufutures')[0] for i in _ufutures]

for j in ufutures_symbols:
    try:
        df_dict[f'{j}_ufutures'] = get_tidyData(symbol=j, data_type='ufutures')
    except:
        print(f'error: no ufutures_symbols : {j}')
        ufutures_symbols.remove(j)

_spot = glob.glob(f"raw_klines/*_spot")
spot_symbols = [i.split('/')[1].split('_spot')[0] for i in _spot]

for i in spot_symbols:
    try:
        df_dict[f'{i}_spot'] = get_tidyData(symbol=i, data_type='spot')
    except:
        print(f'error: no spot_symbols : {i}')
        spot_symbols.remove(i)    


# run error-symbol only
# df_dict[f'ENJUSDT_ufutures'] = get_tidyData(symbol='ENJUSDT', data_type='ufutures')
# df_dict[f'XLMUSDT_spot'] = get_tidyData(symbol='XLMUSDT', data_type='spot')
# ufutures_symbols = ['ENJUSDT']
# spot_symbols = ['XLMUSDT']


for dataList, typeName in zip([ufutures_symbols, spot_symbols], ["ufutures", "spot"]):

    if typeName == "ufutures":
        base_url = "https://data.binance.vision/data/futures/um/daily/klines"
    elif typeName == "spot":
        base_url = "https://data.binance.vision/data/spot/daily/klines"

    for data in dataList:
        try:
            df = df_dict[f'{data}_{typeName}']

            start_date = df.index[0].date()
            end_date = df.index[-1].date()
            date_range = pd.date_range(start_date, end_date, freq="D").date
            real_index = df.index.date

            lacked_day = (list(set(date_range)^set(real_index)))

            if len(lacked_day) != 0:

                path = os.path.join(parent_dir, f"{data}_{typeName}")

                for date in lacked_day:

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
