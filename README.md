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
  * run get_klines.py (update_period = 'monthly')
  * run get_lacked_klines.py
* Create your own strategies
  * Create your strategy into "Strategy File"


## Example

* RSI Strategy in [singleTrade_example.py](Strategy/singleTrade_example.py)
	* The data.df is a resampled DataFrame object, which can be utilized effectively.
	* entryLong / entrySellShort are the entry condition.
	* exitShort / exitBuyToCover are the exit condition.
	* For more details on the backtesting functions, please refer to "[Exit Parameters Instruction](instruction.md)".

```python
data = Data(df_symbol=df_btc_origin, rule='30T')

data.df['rsi'] = talib.RSI(data.df['Close'], 12)
data.df['rsi_r1'] = data.df['rsi'].rolling(12).mean()
data.df['rsi_r2'] = data.df['rsi'].rolling(24).mean()

## entry condition
entryLong = (data.df['rsi_r1'] > data.df['rsi_r2']) & (data.df['rsi_r1'] > 70)
entrySellShort =  (data.df['rsi_r1'] < data.df['rsi_r2']) & (data.df['rsi_r1'] < 30)

## exit condition
exitShort = data.df['rsi_r1'] < 30
exitBuyToCover = data.df['rsi_r1'] > 70

data.type_setting(entryLong, entrySellShort, exitShort, exitBuyToCover, longOnly=False, shortOnly=False)
output_dict = dictType_output(backtesting(data.input_arr, exit_profitOut=True, exParam2=0.02, fund=100)) # 2% stop profit
```

```python
result.draw_equity_curve(text_position='2022-01-01')
```

![output3](https://user-images.githubusercontent.com/77842290/207234980-5e53caf3-3ca3-4eac-9e87-fd9cf8a0ae9d.png)

```python
result.draw_monthly_equity(text_position='2022-01-01')
```

![output4](https://user-images.githubusercontent.com/77842290/207234996-c8af9f18-1f26-4104-88b4-0a60711930cf.png)

## 支援
1. 考慮翻單的獲利情況 (假如出場時滿足對邊進場條件)
2. Numba @jit 加速運算
3. 內建超過 30 種停利停損出場方式
4. 配對交易回測 - 等資金下注
5. 補充幣安月資料的缺漏天數

## 不支援 (歡迎協作)
1. 加減碼邏輯
2. 永續合約之資金費率
3. 配對交易非等資金下注
4. 台指期或其他市場
5. tick data 回測

## 備注
1. resample 使用 (left, left) 為開盤時間 K 棒 ; resample 加一分鐘再使用 (right, right) 為收盤時間 K 棒
    * 為了與幣安統一使用前者, 之後使用外部資料需小心 forward looking 問題
2. timestamp 轉 datetime 用 pd.to_datetime() 才不會自動轉換為 UTC+8
3. 回測限制 : 如果同一根 K 棒同時碰到停損及停利, 視為停損
4. 盤中停損另加滑價 (stopLoss_slippageAdd)
5. 對外使用請註明出處 (**Please indicate the source for external use.**)
6. 有空的話會再把 Document 和程式註解寫豐富一點
7. 聯絡方式
	* email : yuhung.career@gmail.com
	* linkedin : https://www.linkedin.com/in/alex-chiang-0208/
