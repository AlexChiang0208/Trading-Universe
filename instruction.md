# 出場條件參數說明

* 固定時間出場 (exit_timeOut)
  * exParam1 根後平倉
  * 相關參數
    * from_exit_condition = False (True : exit_condition 後才開始計時)
* 停利出場 (exit_profitOut)
  * 固定 exParam2% 停利
* 停損出場 (exit_lossOut)
  * lossOut_condition
    * (1) 固定 exParam3% 停損
    * (2) 高點滑落 exParam3% 停損 (**註** : 高點滑落的停利法，建議加入**賺 xx% 才開啟**的條件)
    * (3) 高點滑落 exParam3 個 VOL 停損 (VOL 由外部提供 ; 可以 input ATR or STD)
    * (4) 跌破近 exParam3 根的低點出場
  * 相關參數
    * risk_control = True : 碰停損後的下次以 rc_percent 比例進場，直到獲利交易為止
    * price_trigger3 = "HL" or "C" (從何啟動停損條件, 以下舉例)
      * 2,3 => 曾經的高點滑落，拿 H 當高點還是 C 當高點
      * 4 => 跌破的歷史低點，要拿 L 還是 C 當低點
* 開啟出場條件 (exit_condition)
  * exit_condition
    * (1) 進場 exParam0 根後開啟 (預設0, 進場即開啟)
    * (2) 賺 exParam0% 後
    * (3) 賺 exParam0 個 VOL 後
    * (4) 賠 exParam0% 後
    * (5) 賠 exParam0 個 VOL 後
    * (6) VOL 轉為進場後的 exParam0 倍
  * 相關參數
    * price_trigger0 = "HL" or "C" (如何觸發出場條件, 以下舉例)
      * 2,3 => 賺xx後開啟條件, 是曾經賺(H) 還是收盤賺(C)
      * 4,5 => 賠xx後開啟條件, 是曾經賠(L) 還是收盤賠(C)

> ## 備註

* 暫時不做多重條件出場 (例如 : exit_condition = [2,4])，避免參數過多混亂
* 延遲進場、延遲出場，暫時沒有需求，所以先不做
