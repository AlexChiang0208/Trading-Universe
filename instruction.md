# 新增出場條件

* 固定時間出場 (time_out)
  * exParam1 根後平倉
    * from_exit_condition = False (True : exit_condition 後才執行此條件)
* 停利出場 (profit_out)
  * 固定 exParam2% 停利
    * end_trigger2 = "HL" or "C"
* 停損出場 (loss_out)
  * (1) 固定 exParam3% 停損
  * (2) 高點滑落 exParam3% 停損 (**註** : 高點滑落的停利法，建議加入**賺 xx% 才開啟**的條件)
  * (3) 高點滑落 exParam3 個 VOL 停損 (VOL 由外部提供 ; 可以 input ATR or STD)
  * (4) 跌破近 exParam3 根的低點出場
    * start_trigger3 = "HL" or "C" (如 : 高點滑落的高點 ; 近幾根低點)
    * end_trigger3 = "HL" or "C" (如 : 跌破是 close 跌破還是 low 跌破)
* 開啟出場條件 (exit_condition)
  * (1) 進場 exParam0 根後開啟 (預設0, 進場即開啟)
  * (2) 賺 exParam0% 後
  * (3) 賺 exParam0 個 VOL 後
  * (4) 賠 exParam0% 後
  * (5) 賠 exParam0 個 VOL 後
  * (6) VOL 轉為進場後的 exParam0 倍
    * end_trigger0 = "HL" or "C"

> ## 備註

* 暫時不做多重條件出場 (例如 : exit_condition = [2,4])，避免參數過多混亂
* 延遲進場、延遲出場，暫時沒有需求，所以先不做
