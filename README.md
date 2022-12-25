# Trading-Universe
Modular backtesting tools (Python)

## Start

* git clone
* Create venv

```
1.    virtualenv venv
2.    enter venv
	  	(a) windows: venv\Scripts\activate
	  	(b) linux & MAC OS: source venv/bin/activate
3.    pip install -r requirements.txt
```

* Get Data
  * run get_klines.py
  * run clean_data.py
* Create your own strategies
  * Create your strategy into "Strategy File"


## Example

RSI Strategy in singleTrade_example.py

#### result.show_performance()
![Screen Shot 2022-12-13 at 1 35 11 PM](https://user-images.githubusercontent.com/77842290/207235117-bf705239-d101-44aa-a62b-d364501baa66.png)

#### result.draw_unrealized_profit()
![output1](https://user-images.githubusercontent.com/77842290/207234958-5a4c72ed-925a-4253-95f2-86c17aae310d.png)

#### result.draw_realized_profit()
![output2](https://user-images.githubusercontent.com/77842290/207234967-f695aa21-2a8c-479b-900e-656c4ff49c87.png)

#### result.draw_equity_curve(text_position='2022-01-01')
![output3](https://user-images.githubusercontent.com/77842290/207234980-5e53caf3-3ca3-4eac-9e87-fd9cf8a0ae9d.png)

#### result.draw_monthly_equity(text_position='2022-01-01')
![output4](https://user-images.githubusercontent.com/77842290/207234996-c8af9f18-1f26-4104-88b4-0a60711930cf.png)

#### result.draw_daily_distribution(bins=40)
![output5](https://user-images.githubusercontent.com/77842290/207235000-a5e37a5b-bb11-4d92-8329-ee21570dec3b.png)

#### result.draw_hold_position()
![output6](https://user-images.githubusercontent.com/77842290/207235017-22acd140-9a23-4dc1-980a-afc2dc4d832f.png)

## 支援
1. 考慮翻單的獲利情況
2. Numba @jit 加速運算
3. 內建超過 36 種停利停損出場方式
4. 配對交易回測 - 等資金下注
5. 因子強度統計檢定 (未公開)

