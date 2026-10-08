# 事件研究估計層：窗口、正常報酬模型、AR／CAR／BHAR 與跨事件檢定（含 Python／R 實作）

本檔是事件研究的**估計層**，補上「事件日有了、稽核清單有了，但中間怎麼算」那一段。
事件研究在本技能家族分四層，各層只做自己的事：

| 層 | 回答的問題 | 在哪裡 |
|---|---|---|
| 事件日層 | t = 0 是哪一天？發言時間 13:30 後怎麼辦？事實發生日怎麼處理？ | `public-disclosure-scout` Step 2 |
| 資料層 | 報酬、市場指數、Fama-French 因子、下市公司在 TEJ 哪裡？ | `tej-data-scout` 的 `references/tej-catalog.md` Part C、Part D |
| **估計層（本檔）** | 窗口怎麼切、正常報酬用哪個模型、AR／CAR／BHAR 與檢定統計量怎麼算、台灣市場的制度特徵怎麼處理 | 本檔 |
| 稽核層 | 審稿人會逐項要哪些穩健性？ | `references/robustness-battery.md` 第六節 |

出圖交 `management-figure`：短窗市場反應的平均累積異常報酬曲線用 `car_plot()`；
交錯 DiD 的動態係數圖用 `event_study_plot()`。兩者在英文裡都叫 event study，但一個是
**短窗市場反應**（本檔），一個是**面板 DiD 的動態效果**（`estimator-playbook.md`），
估計量、標準誤與圖的讀法都不同，稿件中要用不同名稱區分（例：「市場反應事件研究」與
「事件研究式 DiD」），避免審稿人誤會識別來源。

格式沿用 `robustness-battery.md`：**必做**＝沒有就是 Major；**加分**＝攻防表多一列；
**情境觸發**＝符合條件才做。每項附「審稿人會怎麼問」與套件函式。Python 以
`statsmodels`／`scipy` 為主（台灣研究者多用 Python 串 TEJ API），R 為備援；函式名以
官方文件為準，版本寫進再現性聲明。

---

## 一、窗口設計

| 等級 | 項目 | 審稿人會怎麼問 | 做法 | 報告方式 |
|---|---|---|---|---|
| 必做 | 估計窗 | "Why this estimation window, and is it long enough?" | 常見為 (−250, −11)，約一年交易日；常見替代為 (−250, −30)、(−120, −11)（樣本期短或公司上市未滿一年時）。TEJ 事件研究模組（EVENT）的預設估計窗以你訂閱版本的設定畫面為準，常見說法為 −250 至 −10 個交易日（**建議查證**：開設定畫面截圖存證，並寫進資料節）。估計窗有效交易日不足 100 日者剔除（慣例門檻，不是定理；剔除數要報） | 資料節一句＋剔除數 |
| 必做 | 緩衝期：估計窗與事件窗不重疊 | "Does the estimation window overlap with the event window, or with pre-announcement leakage?" | 估計窗終點必須早於事件窗起點，建議至少留 10 個交易日緩衝；有**事實發生日**（`fact_date`）早於發言日期者，估計窗終點再往前推到事實發生日之前；同公司前一次事件的事件窗落進本次估計窗者，剔除該段或改用更早期間 | 資料節一句 |
| 必做 | 事件窗：事前決定、多窗調整 | "Why (−1, +1)? Did you pick the window after seeing the results?" | 主窗 (−1, +1) 或 (0, +1)；敏感度 (0, 0)、(−3, +3)、(−5, +5)；事前窗 (−10, −2) 檢查資訊外洩、事後窗 (+2, +10) 檢查漂移。主窗寫進研究設計（最好預先登記）；同時報多個窗時，各檢定的 p 值跨窗做 Holm (1979) 調整，或明說哪一窗是主檢定 | 主表一欄主窗、附錄全部窗 |
| 情境觸發 | 漲跌停延伸窗 | 見第六節第 2 列 | 事件窗延伸到連續漲跌停結束後一日 | 附錄表 |
| 情境觸發 | 長期窗（12～36 個月） | 見第五節 | 改用 BHAR 或 calendar-time 組合，不要把日 CAR 累加到一年 | 正文另一節 |

---

## 二、正常報酬模型

| 等級 | 模型 | 審稿人會怎麼問 | 做法與套件函式 | 報告方式 |
|---|---|---|---|---|
| 必做 | **市場模型**（主設定）：R_it = α_i + β_i·R_mt + ε_it | "Which benchmark model do you use for expected returns?" | 每個事件在估計窗各跑一條 OLS。Python：`statsmodels.api.OLS(r_est, sm.add_constant(rm_est)).fit()`；R：`lm(r ~ rm)`，或 `estudy2::apply_market_model()`（函式名以 `?estudy2` 為準，**建議查證**）。日資料下市場模型的檢定規格良好（Brown & Warner, 1985） | 資料節一句 |
| 必做 | **市場報酬的口徑** | "Is your market index a price index while your stock returns include dividends?" | 個股用 TEJ 還原（含息）報酬時，市場端也要用**含息報酬指數**，不要用加權股價指數這類價格指數（第六節第 4 列） | 資料節一句寫明兩端口徑 |
| 必做（財務期刊） | **因子模型**：Fama & French (1993) 三因子、Carhart (1997) 四因子 | "Market model vs. factor model: are results robust?" | y = R_it − R_ft，自變數為 MKT−RF、SMB、HML（Carhart 再加 UMD）。台灣用 TEJ 現成 Fama-French 因子，不必自建：路由見 `tej-data-scout` 的 `references/tej-catalog.md` Part C「因子投資／動能／三因子五因子」列與「事件研究法（CAR/AR）」列。TEJ 因子常以 % 為單位，匯入時統一換成小數，無風險利率的期別（日、月）要對齊 | 附錄表：市場模型與因子模型並陳 |
| 加分 | 市場調整模型：AR_it = R_it − R_mt | "Your estimation window is short; are the betas reliable?" | 不需估計參數，適合剛上市、估計窗資料不足的事件；Brown & Warner (1985) 指出短窗下與市場模型差異不大 | 附錄表 |
| 情境觸發 | 薄交易 beta | "Thin trading biases beta toward zero." | Scholes & Williams (1977)：β_SW = (β₋₁ + β₀ + β₊₁)／(1 + 2ρ_m)，β_k 為 R_it 對 R_m,t+k 的簡單迴歸斜率，ρ_m 為市場報酬一階自我相關；Dimson (1979)：R_it 對 R_m,t−1、R_mt、R_m,t+1 同時迴歸，β_D 取三係數加總。兩者皆需手刻（約 10 行） | 附錄表：OLS beta 與調整後 beta 兩欄 |
| 情境觸發 | 配對組合或產業指數 | "Firm characteristics, not the event, may drive the returns." | 長期事件才必要（第五節）；短窗一般不需要 | 附錄表 |

---

## 三、AR、CAR、BHAR 與預測誤差變異

```
AR_it        = R_it − (α̂_i + β̂_i·R_mt)                       事件窗內各日（因子模型同理，以 x_t′b̂ 取代）
CAR_i(τ1,τ2) = Σ_{t=τ1..τ2} AR_it                             L = τ2 − τ1 + 1
CAAR         = (1/N) Σ_i CAR_i                                 N 個事件的平均
BHAR_i(τ1,τ2)= Π_t (1 + R_it) − Π_t (1 + R_bench,t)           長期用；基準為配對組合或含息報酬指數

s_i²         = Σ_{估計窗} ε̂_it² ／(M_i − k)                     M_i：估計窗有效日；k：參數個數（市場模型 2）
Var(CAR_i)   = s_i² · [ L + ι′ X_w (X′X)⁻¹ X_w′ ι ]              X：估計窗設計矩陣；X_w：事件窗設計矩陣；
                                                               第二項是參數估計誤差（預測誤差修正）
  市場模型單日特例：s_i² · [ 1 + 1/M_i + (R_mt − R̄_m)² ／ Σ_{估計窗}(R_mτ − R̄_m)² ]
SCAR_i       = CAR_i ／ √Var(CAR_i)                            標準化累積異常報酬
```

讀法提醒：
1. CAR 是報酬的**加總**，BHAR 是**複利**；短窗兩者幾乎相同，長窗會分歧，且 BHAR 右偏
   （第五節）。
2. 預測誤差修正項在估計窗 250 日時很小，但估計窗短（如 120 日）或事件窗長時不可省；
   省略會使標準化檢定略為偏向拒絕。
3. 單位一律用小數報酬計算，報告時才換成 %；正文同時報基點與以市值換算的金額
   （`robustness-battery.md` 第七節落差 3）。

---

## 四、跨事件檢定（六種，依假設選用）

| 檢定 | 統計量 | 假設與適用 | 審稿人會怎麼問 | Python／R |
|---|---|---|---|---|
| 橫斷面 t（Brown & Warner, 1980, 1985） | t = CAAR ／ (sd(CAR)／√N)，自由度 N − 1 | 只假設事件互相獨立；對事件誘發的變異增加是穩健的；**事件日叢集時過度拒絕** | "Your events cluster in calendar time; the cross-sectional t assumes independence." | `scipy.stats.ttest_1samp(car, 0)`；R `t.test(car)` |
| Patell (1976) 標準化檢定 | Z = Σ_i SCAR_i ／ √Σ_i [(M_i − k)／(M_i − k − 2)] | 以各事件的估計窗變異加權，檢定力高；但**事件使報酬變異上升時過度拒絕**（BMP 1991 的模擬證據） | "Event-induced variance inflates the Patell statistic." | 手刻（SCAR 已算好時一行）；R `estudy2::patell()`（**建議查證**） |
| **BMP**（Boehmer, Musumeci & Poulsen, 1991） | t = mean(SCAR)·√N ／ sd(SCAR)，自由度 N − 1 | 先標準化再用橫斷面變異，同時處理異質變異與事件誘發的變異；**仍假設事件獨立**。短窗市場反應的預設主檢定 | "Report a test that is robust to event-induced variance." | 手刻；R `estudy2::boehmer()`（**建議查證**） |
| **Kolari–Pynnönen (2010) 調整 BMP** | t_KP = t_BMP · √[(1 − r̄)／(1 + (N − 1)·r̄)] | r̄ 為事件期異常報酬的平均橫斷面相關，實務上以估計窗殘差的平均相關估計；**事件日叢集時必報**。原式假設所有事件同一天；事件窗只部分重疊時，常見做法是不重疊的事件對相關設為 0、部分重疊者依重疊比例加權（屬實作選擇，論文要寫明） | "Even a small average correlation (e.g., 0.02) severely inflates test statistics when N is large." | 手刻（r̄ 用 `numpy.corrcoef` 算成對相關後平均） |
| Corrado (1989) 等級檢定 | 每個事件把估計窗＋事件窗的 AR 排名，U_it = K_it ／(T_i + 1)（Corrado & Zivney, 1992 的標準化）；Z = Σ_{t∈窗}(Ū_t − 0.5) ／(√L · S_U)，S_U 為全期 Ū_t − 0.5 的標準差；多日窗的累加形式見 Campbell & Wasley (1993) | 無母數，對報酬的厚尾與偏態穩健；全體同日時，S_U 取自時間序列，對橫斷面相關也較不敏感；有叢集疑慮時另見 Kolari & Pynnönen (2011) 的等級檢定（**建議查證**卷期頁） | "Returns are non-normal; report a rank test." | `scipy.stats.rankdata()` 手刻；R `estudy2::rank_test()`、`modified_rank_test()`（**建議查證**） |
| 符號檢定（廣義符號，Cowan, 1992） | Z = (w − N·p̂) ／ √[N·p̂(1 − p̂)]；w 為 CAR > 0 的事件數，p̂ 為估計窗內 AR > 0 的平均比例 | 日 AR 右偏、中位數略小於 0，以 0.5 為期望值的簡單符號檢定會偏誤；廣義版以估計窗的實際正比例為期望值 | "Is the result driven by a few large observations?" | 手刻；R `estudy2::generalized_sign_test()`（**建議查證**） |

選用紀律：
1. **主檢定只選一個並事前寫明**（建議 BMP；事件日叢集時改 KP 調整 BMP），其餘列在同表
   作為穩健性；不要六個檢定挑最顯著的報。
2. p 值：橫斷面 t、BMP、KP 用 t(N − 1)；Patell、Corrado、符號用標準常態。多窗時每種
   檢定跨窗做 Holm 調整（Python `statsmodels.stats.multitest.multipletests(p, method="holm")`；
   R `p.adjust(p, "holm")`）。
3. 小樣本（N < 30）時，常態近似與 t 近似的差異不可忽略；不要沿用 1.96。
4. CAR 的橫斷面迴歸（CAR 對公司特徵）是另一件事：標準誤以事件日叢集
   （`robustness-battery.md` 第六節最後一列）。

---

## 五、長期事件研究（12～36 個月）

| 等級 | 項目 | 審稿人會怎麼問 | 做法 | 報告方式 |
|---|---|---|---|---|
| 必做 | BHAR 的三種偏誤 | "BHARs relative to a market index are severely misspecified." | Barber & Lyon (1997)、Kothari & Warner (1997)：新上市偏誤（指數納入新股）、再平衡偏誤（指數定期再平衡、個股買進持有）、偏態偏誤（BHAR 右偏，t 檢定在左尾過度拒絕）。對策：以規模×淨值市價比配對的參考組合或控制公司為基準；檢定用偏態調整的 bootstrap t（Lyon, Barber & Tsai, 1999） | 附錄表：指數基準與配對基準並陳 |
| 必做 | **Calendar-time 組合**（主設定） | "Long-run returns of overlapping events are cross-sectionally dependent." | Fama (1998)、Mitchell & Stafford (2000)：每月把過去 h 個月內有事件的公司組成組合（等權與市值加權各一），組合超額報酬對 FF3／Carhart 因子做時間序列迴歸，截距 α 即月平均異常報酬；成員少於 10 家的月份剔除或以成員數加權（慣例，要報）；標準誤用 Newey–West | 正文表：α、t、月數、平均成員數 |
| 加分 | 檢定力的誠實說明 | "Insignificant α may simply reflect low power." | Loughran & Ritter (2000)：calendar-time 法對「異常報酬集中在事件密集期」的情況檢定力偏低；正文明寫 | 正文一句 |
| 情境觸發 | 下市公司的報酬 | "Do you drop firms that delist during the holding period?" | 不可剔除：持有期內下市者保留至下市日，下市後以基準報酬補齊並報敏感度；資料取得見 `tej-data-scout` Part D 第 1 點（下市檔必合併）；美國文獻的下市報酬偏誤見 Shumway (1997) | 資料節一句＋附錄敏感度 |

---

## 六、台灣情境（國外教科書不會寫，審稿人卻會問）

| # | 情境 | 機制 | 做法 | 審稿人會怎麼問 |
|---|---|---|---|---|
| 1 | **發言時間 13:30 後順延** | 台股一般交易於 13:30 收盤；收盤後的盤後定價交易以當日收盤價成交，不產生新價格，故收盤後公告的價格反應落在次一交易日 | 規則與 `public-disclosure-scout` Step 2 完全一致：發言時間在 13:30（含）之後者 t = 0 順延至次一交易日；週末、國定假日、颱風假發言者順延至次一交易日（週末晚間發言只順延到週一，不重複順延）。事件檔保留原始 `announce_time` 供稽核，正文報順延事件數 | "Announcements after market close should be assigned to the next trading day." |
| 2 | **漲跌幅限制造成的延遲反應** | 2015 年 6 月 1 日起個股漲跌幅由 7% 放寬為 10%（以證交所公告為準）。觸及漲跌停時當日價格被截斷，反應延續到後續交易日；價格限制延遲價格發現的論證見 Kim & Rhee (1997) | (a) 報 t = 0 觸及漲跌停的事件比例與連續漲跌停日數；(b) 事件窗延伸到連續漲跌停結束後一日，或報 (0, +k) 系列；(c) 剔除觸及者的穩健性；(d) 樣本跨 2015 年制度變更時分期報告。漲跌停判定以「\|報酬\| ≥ 0.95 × 當期限制」近似，除權息日的參考價調整會使報酬計算口徑略有差異 | "With daily price limits, a (−1, +1) window may truncate the reaction." |
| 3 | **薄交易、停牌與處置股** | 小型股零報酬日多、beta 偏向 0；暫停交易日沒有報酬；處置股（分盤撮合）與全額交割股交易頻率下降；興櫃股票沒有漲跌幅限制且交易稀疏，不宜與上市櫃混成同一樣本 | 報估計窗零報酬比例；超過 20%（經驗門檻）者加跑 Scholes–Williams 或 Dimson beta。停牌日**不可補 0**：補 0 會在停牌期間製造假的零異常報酬，再於復牌日一次跳躍；應剔除事件窗內停牌的事件並報剔除數，或把停牌期間的累積報酬歸到復牌日並延伸事件窗 | "Thinly traded stocks bias beta and the test statistics." |
| 4 | **價格指數 vs 報酬指數的口徑不一** | 加權股價指數（及 Yahoo 的 ^TWII）是**價格指數**、不含息；個股若用 TEJ 還原股價計算報酬則**含息**。除權息集中於 6～9 月（7、8 月最密集），價格指數報酬在這段期間系統性偏低，AR 因而系統性偏高；股東常會、股利公告也集中在這段期間，偏誤與事件日高度重疊 | 市場端改用含息報酬指數（例：臺灣證券交易所發行量加權股價報酬指數，或 TEJ 股價庫的市場報酬欄位；確切表名與起始日**建議查證**），或改用 TEJ Fama-French 因子檔的市場報酬（MKT−RF 加 RF）。資料節寫明兩端口徑 | "Are your market returns and stock returns measured on the same basis (with or without dividends)?" |
| 5 | **同日叢集** | 上市櫃公司年度財報 3 月底前、第一至三季財報分別於 5/15、8/14、11/14 前公告；月營收於次月 10 日前公告；股東常會集中於 5、6 月；主管機關對整個產業的同日公告。叢集使異常報酬橫斷面相關，橫斷面 t、Patell、BMP 都會過度拒絕 | 報「與其他事件同日的事件比例」；比例高時以 KP 調整 BMP 為主檢定，並報 r̄；全體同一天（如法規宣布）時改用 portfolio 法（等權組合的時間序列標準差）或第五節 calendar-time；CAR 橫斷面迴歸以事件日叢集 | "Events cluster around filing deadlines; how do you handle cross-sectional correlation?" |
| 6 | 民國日期、代號變更、同公司同日多則公告 | 民國年未轉換會被解析成西元 1 至 2 世紀；轉板、更名使代號變動 | 依 `public-disclosure-scout` Step 2–3 處理；程式讀日期後檢查年份，早於 1900 年即停 | "How did you construct the event file?" |
| 7 | 評等與 TESG 的回溯值 | 市場在公布當時看不到回溯重算的分數 | 回溯值不得當市場反應的事件，見 `tej-data-scout` Part D 第 2、3 點 | "Was this score available to investors at the event date?" |

---

## 七、Python 實作骨架（statsmodels）

以下是可直接改寫的最小骨架（單一事件市場模型＋跨事件 BMP 與 KP）。r、rm 為以**同一交易
日曆**對齊的 numpy 陣列（口徑一致的含息報酬），t0 為事件日在陣列中的位置：

```python
import numpy as np
import statsmodels.api as sm
from scipy import stats

def market_model_scar(r, rm, t0, est=(-250, -11), win=(-1, 1)):
    """回傳 (CAR, SCAR, 估計窗有效日 M, 估計窗殘差);預測誤差修正見第三節公式。"""
    e = np.arange(t0 + est[0], t0 + est[1] + 1)
    w = np.arange(t0 + win[0], t0 + win[1] + 1)
    ok = np.isfinite(r[e]) & np.isfinite(rm[e])
    X = sm.add_constant(rm[e][ok])
    fit = sm.OLS(r[e][ok], X).fit()
    Xw = sm.add_constant(rm[w], has_constant="add")
    ar = r[w] - Xw @ fit.params                      # 事件窗 AR
    xs = Xw.sum(axis=0)
    var_car = fit.scale * (len(w) + xs @ np.linalg.inv(X.T @ X) @ xs)   # fit.scale = SSR/(M-k)
    return ar.sum(), ar.sum() / np.sqrt(var_car), int(ok.sum()), fit.resid

def bmp_kp(scar, rbar=0.0):
    """BMP 與 Kolari–Pynnönen 調整;rbar 為估計窗殘差的平均成對相關(事件窗不重疊的事件對記 0)。"""
    n = len(scar)
    t_bmp = scar.mean() * np.sqrt(n) / scar.std(ddof=1)
    t_kp = t_bmp * np.sqrt((1 - rbar) / (1 + (n - 1) * rbar))
    p = lambda t: 2 * stats.t.sf(abs(t), n - 1)
    return dict(t_bmp=t_bmp, p_bmp=p(t_bmp), t_kp=t_kp, p_kp=p(t_kp))
```

Calendar-time 組合的骨架（月資料；`panel` 每列為公司×月，`months_since_event` 為距事件月數）：

```python
mask = (panel["months_since_event"] >= 1) & (panel["months_since_event"] <= 36)
port = panel[mask].groupby("month").agg(ret=("ret", "mean"), n=("ret", "size"))
port = port[port["n"] >= 10].join(ff, how="inner")          # ff:TEJ Fama-French 月因子
y = port["ret"] - port["rf"]
fit = sm.OLS(y, sm.add_constant(port[["mkt_rf", "smb", "hml"]])).fit(
    cov_type="HAC", cov_kwds={"maxlags": 3})
print(fit.params["const"], fit.tvalues["const"])             # α:月平均異常報酬
```

R 的對應：單一事件用 `lm()`；整批可用 `estudy2`（Rudnytskyi；`apply_market_model()` 後接
`parametric_tests()`／`nonparametric_tests()`，涵蓋 Patell、BMP、Corrado、廣義符號等；
函式名與參數以 `?estudy2` 為準，**建議查證**）。KP 調整目前需手刻。


---

## 八、報告方式

正文主表欄位建議：窗口｜N｜CAAR（%）｜中位數 CAR｜正比例｜BMP t｜KP 調整 p｜Corrado z｜
廣義符號 z；表註寫明估計窗、模型、順延規則、多窗調整方法與 r̄。

> "We estimate market-model parameters over trading days [−250, −11] relative to the
> announcement date, requiring at least 100 valid daily returns. Announcements released after
> the 13:30 market close are assigned to the next trading day. Because stock returns are
> dividend-adjusted, market returns are taken from the [total-return index]. We test abnormal
> returns with the standardized cross-sectional test of Boehmer, Musumeci, and Poulsen (1991);
> because [x]% of events share an announcement date with at least one other event, we also report
> the Kolari and Pynnönen (2010) adjustment (average residual cross-correlation r̄ = [value]) and
> the Corrado (1989) rank test. P-values across the [k] event windows are adjusted with Holm's
> (1979) step-down procedure."

| 放正文 | 放附錄 |
|---|---|
| 主窗 CAAR 與主檢定、CAAR 曲線圖（`car_plot()`，主窗淡色標示） | 全部窗口 × 六種檢定表 |
| 順延、漲跌停、叢集三項的事件數 | 因子模型、Scholes–Williams／Dimson beta、市場調整模型的重估表 |
| 經濟量級（基點與市值換算金額） | 剔除清單與理由（停牌、估計窗不足、混淆事件） |

---

## 九、文獻（作者、年份、刊名；卷期頁不確定者標「建議查證」）

- Barber, B. M., & Lyon, J. D. (1997). Detecting long-run abnormal stock returns: The empirical power and specification of test statistics. *Journal of Financial Economics*, 43(3), 341–372.
- Boehmer, E., Musumeci, J., & Poulsen, A. B. (1991). Event-study methodology under conditions of event-induced variance. *Journal of Financial Economics*, 30(2), 253–272.
- Brown, S. J., & Warner, J. B. (1980). Measuring security price performance. *Journal of Financial Economics*, 8(3), 205–258.
- Brown, S. J., & Warner, J. B. (1985). Using daily stock returns: The case of event studies. *Journal of Financial Economics*, 14(1), 3–31.
- Campbell, C. J., & Wasley, C. E. (1993). Measuring security price performance using daily NASDAQ returns. *Journal of Financial Economics*（卷期頁建議查證）。
- Campbell, J. Y., Lo, A. W., & MacKinlay, A. C. (1997). *The econometrics of financial markets*（第 4 章）. Princeton University Press.
- Carhart, M. M. (1997). On persistence in mutual fund performance. *Journal of Finance*, 52(1), 57–82.
- Corrado, C. J. (1989). A nonparametric test for abnormal security-price performance in event studies. *Journal of Financial Economics*, 23(2), 385–395.
- Corrado, C. J., & Zivney, T. L. (1992). The specification and power of the sign test in event study hypothesis tests using daily stock returns. *Journal of Financial and Quantitative Analysis*, 27(3), 465–478.
- Cowan, A. R. (1992). Nonparametric event study tests. *Review of Quantitative Finance and Accounting*（卷期頁建議查證）。
- Dimson, E. (1979). Risk measurement when shares are subject to infrequent trading. *Journal of Financial Economics*, 7(2), 197–226.
- Fama, E. F. (1998). Market efficiency, long-term returns, and behavioral finance. *Journal of Financial Economics*, 49(3), 283–306.
- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3–56.
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70.
- Kim, K. A., & Rhee, S. G. (1997). Price limit performance: Evidence from the Tokyo Stock Exchange. *Journal of Finance*, 52(2), 885–901.
- Kolari, J. W., & Pynnönen, S. (2010). Event study testing with cross-sectional correlation of abnormal returns. *Review of Financial Studies*, 23(11), 3996–4025.
- Kolari, J. W., & Pynnönen, S. (2011). Nonparametric rank tests for event studies. *Journal of Empirical Finance*（卷期頁建議查證）。
- Kothari, S. P., & Warner, J. B. (1997). Measuring long-horizon security price performance. *Journal of Financial Economics*, 43(3), 301–339.
- Kothari, S. P., & Warner, J. B. (2007). Econometrics of event studies. In B. E. Eckbo (Ed.), *Handbook of corporate finance: Empirical corporate finance*（Vol. 1；頁碼建議查證）. Elsevier／North-Holland.
- Loughran, T., & Ritter, J. R. (2000). Uniformly least powerful tests of market efficiency. *Journal of Financial Economics*, 55(3), 361–389.
- Lyon, J. D., Barber, B. M., & Tsai, C.-L. (1999). Improved methods for tests of long-run abnormal stock returns. *Journal of Finance*, 54(1), 165–201.
- MacKinlay, A. C. (1997). Event studies in economics and finance. *Journal of Economic Literature*, 35(1), 13–39.
- Mitchell, M. L., & Stafford, E. (2000). Managerial decisions and long-term stock price performance. *Journal of Business*, 73(3), 287–329.
- Patell, J. M. (1976). Corporate forecasts of earnings per share and stock price behavior: Empirical tests. *Journal of Accounting Research*, 14(2), 246–276.
- Scholes, M., & Williams, J. (1977). Estimating betas from nonsynchronous data. *Journal of Financial Economics*, 5(3), 309–327.
- Shumway, T. (1997). The delisting bias in CRSP data. *Journal of Finance*, 52(1), 327–340.

軟體：`estudy2`（R，Rudnytskyi；引用以 `citation("estudy2")` 為準）、`statsmodels`（Seabold & Perktold, 2010, *Proceedings of the 9th Python in Science Conference*）。

延伸閱讀（只借方法模式，未搬程式碼）：Lewinson (2022), *Python for finance cookbook*（2nd ed.）, Packt，第 8 章示範 CAPM 與 Fama-French 因子迴歸的 statsmodels 寫法，可套到本檔第二節；該書沒有事件研究的 AR／CAR 與檢定，估計層仍以本檔為準。
