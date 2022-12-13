import pandas as pd
import zipfile
import urllib.request
import time
import os

# tick aggTrades

names = ["BTC", "ETH"]

start_date = "2020-12-31"
end_date = "2022-12-04"

date_range = pd.date_range(start_date, end_date, freq="D")
parent_dir = "raw_tick/"

for name in names:
    print(name)
    ticker = name + "USDT"
    path = os.path.join(parent_dir, ticker)

    if not os.path.exists(path):
        os.mkdir(path)

    for date in date_range:
        base_url = "https://data.binance.vision/data/futures/um/daily/aggTrades/"
        url = base_url + ticker + "/" + ticker + "-aggTrades-" + date.date().isoformat() + ".zip"
        print(url)
        file_path = os.path.join(path, ticker + "-aggTrades-" + date.date().isoformat() + ".zip")
        file_path = file_path.replace("-", "_")

        if not os.path.exists(file_path):
            try:
                urllib.request.urlretrieve(url, file_path)
            except:
                print(f"failed : {date}")
                continue

        time.sleep(0.1)
