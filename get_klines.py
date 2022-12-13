import pandas as pd
import zipfile
import urllib.request
import time
import os

# u-futures klines

tickers = ["BTCUSDT", "BTCUSDT_210326", "BTCUSDT_210625", "BTCUSDT_210924", "BTCUSDT_211231", "BTCUSDT_220325", "BTCUSDT_220624", "BTCUSDT_220930", "BTCUSDT_221230", 
           "ETHUSDT", "ETHUSDT_210326", "ETHUSDT_210625", "ETHUSDT_210924", "ETHUSDT_211231", "ETHUSDT_220325", "ETHUSDT_220624", "ETHUSDT_220930", "ETHUSDT_221230"]

start_date = "2020-12-30"
end_date = "2022-12-04"

date_range = pd.date_range(start_date, end_date, freq="D")
parent_dir = "raw_klines/"

for ticker in tickers:
    print(ticker)
    path = os.path.join(parent_dir, ticker+'_ufutures')

    if not os.path.exists(path):
        os.mkdir(path)

    for date in date_range:
        base_url = f"https://data.binance.vision/data/futures/um/daily/klines/{ticker}/1m/"
        url = base_url + ticker + "-1m-" + date.date().isoformat() + ".zip"
        print(url)
        file_path = os.path.join(path, ticker + '-ufutures-' + date.date().isoformat() + ".zip")
        file_path = file_path.replace("-", "_")

        if not os.path.exists(file_path):
            try:
                urllib.request.urlretrieve(url, file_path)
            except:
                print(f"failed : {date}")
                continue

        time.sleep(0.3)
