# 文字時間戳對交易日的對齊守則＋情緒對報酬的檢驗設計（2026-10 新增）

**何時讀**：文字變數帶發布時間（新聞、社群貼文、法說會逐字稿、自建情緒指數），且要與股價報酬
同日合併或做預測檢定。這一步做錯，後面所有係數都不能用：前視偏誤不會讓程式報錯，只會讓結果
「好得不合理」。

| 這一步 | 歸誰 |
|---|---|
| 公開資訊觀測站重大訊息的事件日（發言日期＋13:30 後順延） | `public-disclosure-scout` Step 2（官方揭露已有現成規則） |
| 新聞、社群、逐字稿的時間戳對齊；情緒指數建構；情緒對報酬的檢驗設計 | 本檔 |
| 預測迴歸、HAC、樣本外 R² 的語法 | `r-spss-syntax-architect` 的 `references/finance-timeseries-lane.md` §4 |
| 事件研究的識別與稽核（文字事件當事件日時） | `causal-inference-architect` |

---

## §1 對齊守則（七條，依執行順序）

1. **時區先統一。** 全部轉成 Asia/Taipei（UTC+8，無夏令時間）再比對收盤時間。外電與 RSS 常以
   UTC 或帶時區偏移字串發布；沒有時區資訊的欄位，先用幾則已知發布時間的新聞核對來源慣例，
   不要直接假設是台北時間。
2. **13:30 切點。** 台股 13:30 收盤。交易日 13:30 以前發布者歸當日（與當日收盤報酬為同期），
   13:30 以後、週末、國定假日、颱風停市日發布者，歸**下一個實際交易日**。切點附近的新聞影響
   最難判定，穩健性把切點前移（例如 13:00）重跑一次。
3. **只有日期、沒有時分：一律保守順延。** 許多資料源的部分紀錄只有日期，讀進來會被補成
   00:00:00。若照第 2 條機械判斷，00:00 早於 13:30 而被歸入當日，但這則文字可能是當晚才發布，
   等於讓情緒變數提前知道收盤後的消息（見 §4 教訓 1）。處理：00:00:00 精確值一律視為「時分未知」，
   順延到下一交易日；報告這類紀錄的比例；並以「歸當日」與「順延」兩版做敏感度。偵測方法：畫發布
   時分的分布，00:00:00 若出現尖峰，就是補值不是真實發布時間。
4. **交易日曆用實際交易日。** 以 TEJ 匯出日期或證交所休市表為準，不用營業日曆函式。春節封關、
   颱風停市後的第一個交易日會累積多日文字，量與語調都異常：控制星期效果，穩健性剔除長假後首日。
5. **轉載去重要在對齊之前做。** 同一則新聞被多家媒體轉載，時間有先後。若先對齊再「同股同日」去重，
   13:00 的原稿與 15:00 的轉載會落在不同交易日、兩則都留下，轉載被當成隔日的新資訊。正確順序：
   同股、正規化標題（去標點與空白）、短時間窗（例如 3 日）內視為同一則，**保留最早發布者**
   （它的時間才是資訊到達時點），再做第 2 條。措辭微調的近似轉載，穩健性改用文字相似度門檻去重；
   窗長與門檻是設計選擇，要揭露。
6. **價格觸發稿要剔除或另列。** 「盤中速報」「漲停」「股價重挫」這類由價格變動觸發的機器稿或標題，
   描述的是報酬本身，納入會人為製造情緒與同期報酬的正相關（反向因果）。用來源或標題規則分類，
   研究版剔除，並保留分類規則與逐源歸類表供稽核。
7. **語料要 point-in-time。** 記錄每筆文字的抓取時間，原文永久保存；媒體事後修改或下架、資料商
   回溯補資料或改方法，都會讓同一天的情緒值隨抓取時間而變。序列若在某日出現水準跳動，先查是否
   換了來源組成或模型版本，再談經濟意義。

```python
import pandas as pd
cal = pd.DatetimeIndex(sorted(trading_days))                          # 實際交易日
ts = pd.to_datetime(news["published"], format="ISO8601")
ts = ts.dt.tz_localize("Asia/Taipei") if ts.dt.tz is None else ts.dt.tz_convert("Asia/Taipei")
news["ts"] = ts                                                        # 無時區者已確認為台北時間才可 localize
# 第 5 條：先去重（同股、正規化標題、3 日窗內保留最早）
news["key"] = news["title"].str.replace(r"[\W_]+", "", regex=True).str.lower()
news = news.sort_values("ts")
gap = news.groupby(["stock_id", "key"])["ts"].diff() > pd.Timedelta(days=3)
news["story"] = gap.groupby([news["stock_id"], news["key"]]).cumsum()
news = news.drop_duplicates(["stock_id", "key", "story"], keep="first").copy()
# 第 2、3 條：13:30 切點；00:00:00 視為時分未知、保守順延
day = news["ts"].dt.tz_localize(None).dt.normalize()
date_only = news["ts"].dt.strftime("%H:%M:%S").eq("00:00:00")
intraday = day.isin(cal) & news["ts"].dt.strftime("%H:%M").le("13:30") & ~date_only
k = cal.searchsorted(day, side="right")                                # 嚴格晚於當日的第一個交易日
nxt = pd.Series([cal[i] if i < len(cal) else pd.NaT for i in k], index=news.index)
news["trade_date"] = day.where(intraday, nxt)
print("時分未知比例", date_only.mean())                               # 進資料節
```
（以上片段 2026-10-04 以 pandas 3.0.6 合成資料實跑：13:31 發布、週末發布、00:00:00 紀錄皆順延到
下一交易日；15:20 的同標題轉載被去重。）

---

## §2 情緒對報酬的檢驗設計

1. **先分清楚同期與預測。** 「t 日情緒 ↔ t 日報酬」是同期共動，多半反映新聞在報導價格；
   「t 日情緒 → t+1 日報酬」才是預測檢定。兩者都可以報，但結論的動詞不同（見第 7 條）。
2. **控制落後報酬。** 報酬有短期反轉與動能，情緒又追隨過去報酬；不控制落後報酬，情緒係數會吸收
   報酬自身的動態。Tetlock（2007）的 VAR 式設計以五期落後報酬與其他控制並列，是常見起點；
   另控制成交量、市場波動與星期效果。
3. **標準誤用 Newey–West。** 日資料殘差有序列相關與異質變異；預測期 h > 1 且觀測重疊時，
   HAC 落後期數至少 h−1。
4. **反向 Granger 一定要測。** 文獻常見「報酬領先情緒」：Tetlock（2007）發現低市場報酬之後
   媒體悲觀度上升；網路留言的語調對報酬的預測力微弱，訊息量對波動的預測較穩（Antweiler & Frank,
   2004）。只報「情緒 → 報酬」不報「報酬 → 情緒」，審稿人會直接問。VAR 兩個方向的
   Granger 檢定並陳。
5. **樣本外證據。** 擴張窗估計、逐期預測，報 Campbell–Thompson 樣本外 R²（基準為歷史均值），
   巢狀比較用 Clark–West 檢定（語法見 `finance-timeseries-lane.md` §4）。樣本內顯著、樣本外 R² 為負，
   正文就只能寫「樣本內相關」。
6. **情緒指數通常高度持續。** 持續的預測變數在小樣本預測迴歸中有 Stambaugh（1999）偏誤，t 值偏大；
   報持續性（一階自相關）並以樣本外結果為主要證據。Garcia（2013）發現情緒的預測力集中在
   景氣衰退期，分期報告比全期平均更有資訊。
7. **結論語言。** 同期相關強、預測力弱，是情緒指數最常見的結果；這時應寫「情緒指數描述市場氛圍」，
   不寫「情緒預測報酬」。一個只會反映當下的指標，是溫度計，不是預測器；兩種用途的驗證標準不同，
   論文開頭就要說清楚要用哪一種。

```python
import statsmodels.api as sm
X = pd.concat({"sent": s, **{f"r_l{k}": ret.shift(k - 1) for k in range(1, 6)}}, axis=1)   # t 日已知
fit = sm.OLS(ret.shift(-1), sm.add_constant(X), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 5})
from statsmodels.tsa.api import VAR
v = VAR(pd.DataFrame({"ret": ret, "sent": s}).dropna()).fit(maxlags=5)
v.test_causality("ret", ["sent"], kind="f").pvalue    # 情緒 → 報酬
v.test_causality("sent", ["ret"], kind="f").pvalue    # 報酬 → 情緒（反向，必報）
```

---

## §3 多股合成指數的加權偏誤

把多檔股票的新聞混在一起算「(正面數 − 負面數)／總則數」，等於**以新聞則數加權**。新聞量高度
集中在少數超大型權值股，合成指數會被一兩檔股票主導，實際上量的是那幾檔的情緒（見 §4 教訓 2）。

- **先公司、後市場**：每檔每日先算自己的情緒，再以明確權重合成。
- **權重要與報酬端一致**：對市值加權指數報酬，用前一日市值加權；對等權報酬，用公司等權。
  新聞則數加權只有在理論上主張「新聞量本身就是資訊強度」時才用，且要寫出理由。
- **報集中度**：每日最大單一公司新聞占比、新聞則數的 HHI；穩健性剔除新聞量最大的公司重算。
- **零新聞日**：淨情緒比率分母為 0，是缺值不是中性，不得補 0；新聞極少的日子雜訊大，
  設最低則數門檻或以則數做精確度權重，並揭露。
- **股票池的存活偏誤**：以「現在」的權值股回推歷史，是事後選樣；用歷史成分股清單重建。

```python
firm_day = scored.groupby(["trade_date", "stock_id"]).agg(net=("net", "mean"), n=("net", "size"))
pooled = scored.groupby("trade_date")["net"].mean()                       # 則數加權（要避免的做法）
ew = firm_day.groupby(level="trade_date")["net"].mean()                   # 公司等權
vw = (firm_day.join(mcap_lag)               # mcap_lag：索引同為 (trade_date, stock_id)、欄 mcap＝前一交易日市值
        .groupby(level="trade_date").apply(lambda g: np.average(g["net"], weights=g["mcap"])))
top1 = firm_day.groupby(level="trade_date")["n"].apply(lambda s: s.max() / s.sum())   # 單一公司占比
```
三個版本並陳，若 `pooled` 與 `ew`、`vw` 的走勢差很多，表示合成指數其實被少數公司主導。

---

## §4 實測教訓（已去識別，來自一個中文新聞情緒指數的建置經驗）

1. **00:00 補值造成前視。** 部分新聞紀錄只有日期、被補成 00:00，依「≤13:30 歸當日」規則被提前
   歸入當日，同期相關因此被灌水。修法見 §1 第 3 條；修正後同期相關變小是預期中的事，不要回頭找理由。
2. **多股混合指數被新聞量最大的權值股主導。** 單一超大型權值股的新聞則數遠高於其他成分股，
   則數加權的混合指數幾乎等於該股的情緒。修法見 §3。
3. **標題級推論＋領域外模型＋人工驗證未完成＝只能稱探索性。** 拿訓練語料與目標語料（繁體財經
   新聞標題）不同的中文金融情緒模型做推論，屬領域外使用（SKILL.md 方法階梯 3b）；分層抽樣的人工驗證樣本標完、
   κ 達標之前，情緒變數不得當主要解釋變數。
4. **文件自己承認「情緒是溫度計，不是報酬預測器」。** 這是誠實的定位：同期共動穩定、預測力薄弱。
   論文若主張預測，就必須拿出 §2 第 5 條的樣本外證據；拿不出來，就把研究問題改寫成「情緒如何反映、
   放大或延遲反映市場事件」。

---

## §5 審稿人會怎麼問

| 問題 | 本檔對應 |
|---|---|
| 新聞發布時間的時區與收盤切點怎麼處理？只有日期的紀錄有幾成、怎麼歸日？ | §1 第 1–3 條 |
| 轉載有沒有去重？去重在對齊之前還是之後？ | §1 第 5 條 |
| 由價格觸發的新聞是否剔除？情緒與報酬的相關是不是新聞在報導價格？ | §1 第 6 條、§2 第 4 條 |
| 有控制落後報酬嗎？反向 Granger 呢？ | §2 第 2、4 條 |
| 樣本外 R² 是多少？情緒指數的持續性多高？ | §2 第 5、6 條 |
| 合成指數的權重是什麼？會不會被一兩檔股票主導？ | §3 |
| 情緒模型在你的語料上的準確率與 κ？是否領域外使用？ | SKILL.md Step 2 的 3b、Step 3 |

---

## 文獻

- Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. *Journal of Finance*, 59(3), 1259–1294.
- Araci, D. (2019). FinBERT: Financial sentiment analysis with pre-trained language models. arXiv:1908.10063（預印本，非期刊）.
- Campbell, J. Y., & Thompson, S. B. (2008). Predicting excess stock returns out of sample: Can anything beat the historical average? *Review of Financial Studies*, 21(4), 1509–1531.
- Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics*, 138(1), 291–311.
- Garcia, D. (2013). Sentiment during recessions. *Journal of Finance*, 68(3), 1267–1300.
- Granger, C. W. J. (1969). Investigating causal relations by econometric models and cross-spectral methods. *Econometrica*, 37(3), 424–438.
- Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. *Contemporary Accounting Research*, 40(2), 806–841.
- Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. *Journal of Accounting Research*, 54(4), 1187–1230.
- Malo, P., Sinha, A., Korhonen, P., Wallenius, J., & Takala, P. (2014). Good debt or bad debt: Detecting semantic orientations in economic texts. *Journal of the Association for Information Science and Technology*, 65(4), 782–796.（Financial PhraseBank 出處）
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Stambaugh, R. F. (1999). Predictive regressions. *Journal of Financial Economics*, 54(3), 375–421.
- Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *Journal of Finance*, 62(3), 1139–1168.
