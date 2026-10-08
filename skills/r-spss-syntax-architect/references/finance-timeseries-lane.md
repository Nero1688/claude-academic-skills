# 金融時序第五軌：資產定價、波動度、預測評估、體制（2026-10 新增）

面板 FE 之外的第五條軌道。**何時走**：依變數是報酬或風險（股價報酬率、超額報酬、beta、波動度、
VaR），或研究問題是「某變數能否在樣本外預測報酬／波動」。**何時不走**：Y 是會計績效的
公司-年面板（回 SKILL.md 主軌或 `python-panel-lane.md`）；事件研究 CAR 的識別與稽核
（歸 `causal-inference-architect` 的 `references/robustness-battery.md` 第六節）。
SPSS 無 GARCH、Fama–MacBeth、Markov-switching 原生程序，本軌只有 R 與 Python 雙軌。

| 這一步 | 歸誰 |
|---|---|
| 報酬序列紅旗（除權息、漲跌停、停牌、日曆、分割、口徑混用） | `tej-data-wrangler` Step 4（先過再進本軌） |
| 報酬、Beta、Fama-French 因子在 TEJ 哪裡 | `tej-data-scout` 的 `references/tej-catalog.md` Part C「股票報酬／風險／Beta」與「因子投資／動能／三因子五因子」兩列 |
| 本軌：估計語法（時序因子迴歸、FM、GARCH、預測評估、斷點偵測） | 本檔 |
| 事件是否外生、制度變革的因果識別 | `causal-inference-architect`（本軌的斷點是「偵測」不是「識別」，見 §6） |
| 文字情緒變數對報酬的檢驗 | `text-analytics-architect` 的 `references/text-timestamp-alignment.md` |
| 樣本外評估的資料窺探檢核表 | `causal-inference-architect` 的 `references/robustness-battery.md`「樣本外預測評估與資料窺探」一節 |

**實測紀錄（2026-10-04）**：本檔所有 Python 名稱已在 Python 3.14 環境實測 import 與合成資料冒煙
測試（arch 8.0.0、statsmodels 0.15.0、linearmodels 7.0、scikit-learn 1.9.1、pandas 3.0.6）。
R 端在 R 4.6.0 實測可呼叫：sandwich 3.1.1、lmtest 0.9.40、forecast 9.0.2、urca 1.3.4、
zoo 1.8.15、PerformanceAnalytics 2.1.0。**rugarch、strucchange、MSwM、plm 本機未安裝，凡出自
這幾個套件的函式名一律標「建議查證」**，使用前以 `?函式名` 或套件 vignette 核對。
版本號寫進再現性聲明（SKILL.md output_contract 第 4 件），套件改版後重測一次。

---

## §0 前置：台灣報酬資料的口徑（原創注入，審稿人第一輪就問）

1. **報酬指數 vs 價格指數。** Yahoo 的 `^TWII`（發行量加權股價指數）是**價格指數**，不含現金股利；
   證交所另編「發行量加權股價報酬指數」（含股利再投資，起編日建議查證）。台股現金股利率高、
   除息集中在年中（約 6–9 月），拿價格指數當市場報酬會系統性低估市場報酬，且在除息季製造季節性
   假跌。**個股用含息報酬、市場用價格指數**是最常見的口徑錯配：迴歸會吐出一個「正 alpha」，
   其實只是股利。規則：個股、市場、因子三者同為含息口徑，欄名加後綴 `_tr`／`_px` 防混用。
2. **TEJ 現成因子。** Fama-French 三／五因子與 TEJ 自編多因子有日週月年頻率（見上表 Part C 列），
   不必自建。但因子的建構細節（分組 breakpoint 用哪個母體、市值加權或等權、每年幾月重組、
   是否含上櫃、無風險利率用哪一檔）以 TEJ 官方文件為準並寫進資料節；**因子檔是否附無風險利率欄
   建議查證**，自建時常見選擇是一年期定存利率換算成月或日利率，選哪一個要寫明。
3. **漲跌幅截斷。** 2015-06-01 起由 ±7% 放寬為 ±10%（證交所公告）。觸及漲跌停日的報酬被截尾，
   當日波動被低估、未消化的資訊延到次日（Kim & Rhee, 1997 稱為波動外溢與價格發現延遲）。
   後果：(a) 跨 2015 年的長樣本有一個**制度造成的**波動斷點；(b) 小型股觸及漲跌停的比例遠高於
   權值股，GARCH 參數在兩群之間不可比。最低要求：報告漲跌停日占比，跨 2015 樣本分段估計或加
   制度虛擬變數。
4. **交易日曆。** 以實際交易日為準（TEJ 匯出的日期或證交所休市表）。颱風停市、春節封關、補行
   上班日是否開市（早年曾開市，建議以證交所歷年休市表查證）都會讓 `pd.bdate_range` 之類的
   營業日曆出錯：多出來的日子若被補成 0 報酬，GARCH 低估波動、自相關被人為製造。
   與美國因子或總經資料合併時，美國 t 日收盤對應台灣 t+1 日開盤，日期要錯開一天再談同期。
5. **頻率選擇。** 資產定價檢定多用月報酬；波動度建模用日報酬；日內資料（已實現波動）的個股
   可得性建議向資料商查證，不要假設有。

**審稿人會怎麼問**：「市場報酬含息嗎？」「因子是自建還是 TEJ 現成？breakpoint 母體是什麼？」
「2015 年漲跌幅放寬前後是否分段？」「非交易日怎麼處理？」——四題都要在資料節一句話答完。

---

## §1 典型事實檢查（資料品質閘門，建模前跑）

報酬序列先過四項典型事實（Cont, 2001），過不了通常代表資料有問題，而不是發現了新現象：

| 檢查 | 預期 | 不符時先懷疑 |
|---|---|---|
| 厚尾：超額峰態 > 0、Jarque–Bera 拒絕常態 | 日報酬幾乎必然厚尾 → 分配用 t 或偏 t | 報酬被平滑或縮尾過頭 |
| 報酬本身自相關弱 | 一階自相關接近 0 | 大量 0 報酬（停牌補零、薄交易）、日曆錯位 |
| 平方報酬自相關強（波動群聚） | Ljung–Box、ARCH-LM 拒絕 | 頻率太低（月資料群聚弱是正常的） |
| 槓桿效果：今日報酬與未來波動負相關 | 負相關 → 考慮 GJR／EGARCH | 只看單一股票時可能不顯著，不必強求 |

```python
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox, het_arch
print(stats.skew(r), stats.kurtosis(r), stats.jarque_bera(r).pvalue)   # kurtosis 回傳超額峰態
print(acorr_ljungbox(r**2, lags=[5, 10, 22]))                           # 平方報酬 → 波動群聚
print(het_arch(r, nlags=5)[1])                                          # ARCH-LM 的 p 值
lev = r.corr((r**2).shift(-1))                                          # 描述用；負值＝槓桿效果
lim = np.where(r.index < "2015-06-01", 0.07, 0.10)                      # 台股漲跌幅制度
print((r.abs() >= lim - 0.0005).mean())                                 # 漲跌停日占比（近似，見下）
```
```r
Box.test(r^2, lag = 10, type = "Ljung-Box")   # base R；ARCH-LM 可用 FinTS::ArchTest（未安裝，建議查證）
```
漲跌停判定以參考價為基準、價格需落在升降單位上，用報酬門檻只是近似；資料商若有漲跌停旗標欄，
以旗標為準（TEJ 是否提供建議查證）。

**審稿人會怎麼問**：「為何選 t 分配？峰態多少？」「報酬有不尋常的自相關嗎？（通常是薄交易或補零）」
「漲跌停日占多少？對結果有影響嗎？」

---

## §2 資產定價

### 2.1 時序因子迴歸（CAPM／FF3／FF5／Carhart）＋ HAC 標準誤

r_ex,t = α + β′f_t + ε_t，f 為 MKT−RF、SMB、HML（FF5 加 RMW、CMA；Carhart 加 MOM）。
α 是「因子解釋不了的平均超額報酬」，**它的顯著性取決於因子集**：同一個 α 在 CAPM 下顯著、
在 FF5 下消失很常見，正文要報所有因子模型的 α 並排。標準誤用 Newey–West（1987）HAC，
落後期數 L 用 Newey–West（1994）的經驗法則並做 L 的敏感度。

```python
import numpy as np, statsmodels.api as sm
L  = int(np.floor(4 * (len(r_ex) / 100) ** (2 / 9)))     # 正文報 L，附錄報 L±2
ff = sm.OLS(r_ex, sm.add_constant(F)).fit(cov_type="HAC", cov_kwds={"maxlags": L})
# 多個投組的 alpha 聯合為零（GRS 精神的漸近 Wald 檢定）：
from linearmodels.asset_pricing import TradedFactorModel
jt = TradedFactorModel(ports, F).fit(cov_type="kernel").j_statistic   # .stat / .pval
```
```r
library(sandwich); library(lmtest)
m <- lm(r_ex ~ mkt_rf + smb + hml, data = d)
L <- floor(4 * (nrow(d) / 100)^(2/9))
coeftest(m, vcov. = NeweyWest(m, lag = L, prewhite = FALSE))   # 不預白化，與 statsmodels HAC 同口徑
```
GRS（Gibbons, Ross & Shanken, 1989）的有限樣本 F 版本 linearmodels 未直接提供，需要時自寫
或用 R 的 GRS 檢定套件（套件名建議查證）。

### 2.2 滾動 beta

```python
from statsmodels.regression.rolling import RollingOLS
rb = RollingOLS(r_ex, sm.add_constant(F[["mkt_rf"]]), window=60, min_nobs=36).fit()
beta_t = rb.params["mkt_rf"].shift(1)   # ★下一步若當解釋變數，只能用 t−1 以前估出的 beta
```
```r
b <- zoo::rollapply(zoo::zoo(as.matrix(d)), width = 60, by.column = FALSE, align = "right",
                    FUN = function(z) coef(lm(z[, "r_ex"] ~ z[, "mkt_rf"]))[2])
```
窗長（月資料 36–60 個月、日資料約一年）是設計選擇，要揭露並做敏感度。忘了 `shift(1)` 是最常見的前視。

### 2.3 Fama–MacBeth 兩階段＋ Newey–West

第一階段每期做一次橫斷面迴歸，第二階段對斜率的時間序列取平均，標準誤用斜率序列的 Newey–West。
**特徵要在 t 期期末已知**：財報變數要加公告時滯（台灣年度財報的申報期限與適用年度建議查證），
報酬用 t+1 期。

```python
from linearmodels.panel import FamaMacBeth
# panel：MultiIndex(firm, month)；ret_lead＝t+1 月報酬
# month 層須為 Timestamp（如月底日期），用 pandas Period 索引 linearmodels 會報錯
fm = FamaMacBeth.from_formula("ret_lead ~ 1 + beta + log_size + bm + gov", data=panel)
res = fm.fit(cov_type="kernel", bandwidth=L)        # 斜率序列的 Bartlett 核 HAC
```
```r
# 手寫版（base R＋sandwich，透明、可逐期檢查）
g  <- t(sapply(split(pan, pan$month), function(s) coef(lm(ret_lead ~ beta + log_size + bm, data = s))))
fm <- lm(g[, "bm"] ~ 1)                                         # 第二階段：斜率序列對常數
coeftest(fm, vcov. = NeweyWest(fm, lag = L, prewhite = FALSE))
# 套件版 plm::pmg（以時間為群）亦可，函式行為建議查證
```
兩個常被審稿人抓的點：(a) beta 若是估計值，第二階段有變數誤差，報 Shanken（1992）修正；
`LinearFactorModel` 的標準誤是否已含此修正以官方文件為準（建議查證）。(b) Petersen（2009）：
FM 標準誤處理橫斷面相關，但**不處理公司效果的持續性**；治理變數高度持續時，並陳公司叢集
標準誤的 pooled 迴歸。

### 2.4 Portfolio sorts

```python
panel["q"] = panel.groupby(level="month")["signal"].transform(
    lambda s: pd.qcut(s, 5, labels=False, duplicates="drop"))          # t 月底分組
port = panel.groupby([panel.index.get_level_values("month"), "q"]).apply(
    lambda g: np.average(g["ret_lead"], weights=g["mcap"]))            # 市值加權；等權另報
spread = port.xs(4, level="q") - port.xs(0, level="q")                  # 高減低
sm.OLS(spread, np.ones(len(spread))).fit(cov_type="HAC", cov_kwds={"maxlags": L})
```
設計選擇逐項揭露：breakpoint 母體（全體或只用上市股，台灣上櫃小型股多，母體不同結果可差很多）、
等權 vs 市值加權、重組月份、下市股最後一期報酬怎麼算（存活偏誤見 `tej-data-scout` Part D）、
雙重排序是獨立還是條件排序。單調性用 Patton & Timmermann（2010）的檢定，不要只看「高減低」。

**審稿人會怎麼問（§2 全節）**：「alpha 對因子集穩健嗎？」「HAC 落後期數怎麼選？」
「FM 的 beta 有 EIV 修正嗎？」「排序結果是不是只來自小型股與低流動性股？」「扣交易成本後還在嗎？」
「你試過幾種排序與因子組合？」（t 門檻與多重檢定的審稿期待見 `q1-journal-reviewer` 的
`references/top-journal-standards.md` 財務家族子類。）

---

## §3 波動度

**管理研究最常見的用法先講**：治理或 ESG 對「公司風險」的研究，多半把**年度報酬標準差**或
**特質波動度**（FF3 殘差標準差；Ang, Hodrick, Xing & Zhang, 2006）算成公司-年變數，再回主軌跑面板 FE。
這時不需要 GARCH。GARCH 與 HAR 適用的是「條件波動的時間序列」問題：事件前後波動是否改變、
波動預測、風險管理。

### 3.1 GARCH(1,1)、GJR、EGARCH 與 t 分配

```python
from arch import arch_model
am  = arch_model(100 * r, mean="Constant", vol="GARCH", p=1, o=1, q=1, dist="t")  # o=1 即 GJR；×100 助收斂
res = am.fit(disp="off")
a, g, b = res.params["alpha[1]"], res.params["gamma[1]"], res.params["beta[1]"]
persist   = a + b + g / 2                      # 對稱分配下 GJR 的持續性，需 < 1
half_life = np.log(0.5) / np.log(persist)      # 衝擊衰減一半的天數，比參數本身好解釋
# EGARCH：vol="EGARCH"；偏 t：dist="skewt"；條件波動序列：res.conditional_volatility
```
```r
library(rugarch)   # 本機未安裝：以下函式與參數名建議查證
spec <- ugarchspec(variance.model = list(model = "gjrGARCH", garchOrder = c(1, 1)),
                   mean.model = list(armaOrder = c(0, 0)), distribution.model = "std")
fit  <- ugarchfit(spec, data = r)
```
紀律：均值與變異方程式同時估計，不要先跑 ARIMA 再拿殘差跑 GARCH；報 α+β（或 GJR 持續性）
與半衰期；t 分配自由度 ν 很大時與常態無異，可據以簡化。台灣小型股：漲跌停日占比高時，
GARCH 估出的持續性偏高，分群（權值股 vs 小型股）估計並揭露（§0 第 3 點）。

### 3.2 HAR-RV（Corsi, 2009）

RV_{t+1} = b0 + b_d·RV_t + b_w·RV_t^(週) + b_m·RV_t^(月)，以日、週（5 日）、月（22 日）平均捕捉長記憶。
```python
har = arch_model(rv, mean="HAR", lags=[1, 5, 22], vol="Constant").fit(disp="off")
# 等價做法：自建三個落後平均，sm.OLS(...).fit(cov_type="HAC", ...)；log-HAR 對右偏較穩
```
```r
rv_w <- stats::filter(rv, rep(1/5, 5), sides = 1)     # 週平均（含當日往回 5 日）
rv_m <- stats::filter(rv, rep(1/22, 22), sides = 1)   # 月平均
n <- length(rv)
h <- lm(rv[-1] ~ rv[-n] + rv_w[-n] + rv_m[-n])        # 以 t 期資訊預測 t+1
coeftest(h, vcov. = NeweyWest(h, lag = 5, prewhite = FALSE))
```
RV 本應來自日內報酬；只有日資料時以 r² 或高低價區間代理，雜訊大，正文要揭露代理方式。

### 3.3 波動預測評估：QLIKE、MSE、Diebold–Mariano

只看樣本外。參數只用預測起點之前的資料估計（`fit(last_obs=...)`），每隔固定期間重估，
擴張窗與滾動窗都報。基準至少三個：滾動 21 日變異、EWMA（RiskMetrics 的 λ=0.94，
`(r**2).ewm(alpha=0.06).mean()`）、GARCH(1,1)。Hansen & Lunde（2005）比較數百個 ARCH 類模型：
匯率資料中沒有模型顯著勝過 GARCH(1,1)，股票報酬則是含槓桿效果的模型較佳；所以 GARCH(1,1)
與 GJR 都要列為基準，新模型輸給它們要誠實寫。

```python
res = am.fit(last_obs=split_date, disp="off")
fc  = res.forecast(horizon=1, start=split_date, reindex=False)   # 參數固定的一步預測；重估要自寫迴圈
def qlike(proxy, h):                       # Patton (2011)：代理變數有雜訊時，MSE 與 QLIKE 仍能正確排序
    return proxy / h - np.log(proxy / h) - 1
d  = qlike(proxy, h_a) - qlike(proxy, h_b)                          # 損失差
dm = sm.OLS(d, np.ones(len(d))).fit(cov_type="HAC", cov_kwds={"maxlags": max(h_step - 1, 0)})
from arch.bootstrap import MCS                                      # 多模型：Model Confidence Set
mcs = MCS(loss_df, size=0.10, reps=5000, seed=20261004); mcs.compute(); mcs.included
```
```r
forecast::dm.test(e1, e2, h = 1, power = 2)   # 已實測可呼叫；小樣本修正的預設行為以 ?dm.test 為準
```

**審稿人會怎麼問（§3）**：「你的 RV 代理是什麼？」「用 MSE 還是 QLIKE？為何？」
「對 GARCH(1,1) 與 EWMA 有贏嗎？DM 或 MCS 結果？」「參數多久重估一次？」「漲跌停截斷怎麼處理？」

---

## §4 時序預測評估（報酬、情緒、總經序列通用）

1. **平穩性：ADF 與 KPSS 併用**（虛無假設相反）。

   | ADF（H0 單根） | KPSS（H0 平穩） | 判讀 |
   |---|---|---|
   | 拒絕 | 不拒絕 | 平穩，可直接建模 |
   | 不拒絕 | 拒絕 | 單根，差分或改用報酬 |
   | 都拒絕／都不拒絕 | — | 證據衝突：看檢定力、結構斷點（ZivotAndrews） |
   ```python
   from statsmodels.tsa.stattools import adfuller, kpss
   p_adf, p_kpss = adfuller(x, autolag="AIC")[1], kpss(x, regression="c", nlags="auto")[1]
   from arch.unitroot import ZivotAndrews      # 允許一個內生斷點的單根檢定
   ```
   ```r
   urca::ur.df(x, type = "drift", selectlags = "AIC"); urca::ur.kpss(x, type = "mu")
   ```
   KPSS 的 p 值有查表上下限，超出會出警告且回傳邊界值，報告時寫「p > 0.10」而非精確值。
2. **ARIMA 只當基準**（`statsmodels.tsa.arima.model.ARIMA`；R `forecast::Arima`／`auto.arima`），
   不當主角。報酬的基準至少要有：隨機漫步／最後值、**歷史均值（擴張窗）**。
3. **Campbell–Thompson 樣本外 R²** 與 **Clark–West 檢定**（巢狀模型）：
   ```python
   hist = r.expanding().mean().shift(1)                       # 歷史均值基準，只用 t−1 以前
   oos  = pd.concat({"r": r, "f": r_hat, "b": hist}, axis=1).loc[oos_start:].dropna()
   r2_os = 1 - ((oos.r - oos.f) ** 2).sum() / ((oos.r - oos.b) ** 2).sum()
   f_cw  = (oos.r - oos.b) ** 2 - ((oos.r - oos.f) ** 2 - (oos.b - oos.f) ** 2)
   sm.OLS(f_cw, np.ones(len(f_cw))).fit(cov_type="HAC", cov_kwds={"maxlags": L})  # 單尾 t 檢定
   ```
   Welch & Goyal（2008）顯示多數預測變數的 R²_OS 為負；Campbell & Thompson（2008）指出月頻的
   小幅正值對均值變異投資人就可能有經濟意義。兩篇一起引，結論才平衡。
4. **切分**：擴張窗或滾動窗，`sklearn.model_selection.TimeSeriesSplit(n_splits, test_size, gap)`；
   標籤跨期重疊時要 gap。**記錄試過幾種設定**，資料窺探的檢核走 `causal-inference-architect`
   的 `robustness-battery.md`「樣本外預測評估與資料窺探」一節。
5. **Granger 因果**只是「領先」，不是因果：`statsmodels.tsa.stattools.grangercausalitytests`、
   `statsmodels.tsa.api.VAR(...).fit(p).test_causality(...)`；R `lmtest::grangertest`。
   兩個方向都要測（反向常常更顯著，見 `text-timestamp-alignment.md` §2）。
6. **預測變數高度持續**（股利率、情緒指數）時，預測迴歸係數有 Stambaugh（1999）偏誤，
   小樣本 t 值偏大；報偏誤修正或以樣本外證據為主。

**審稿人會怎麼問（§4）**：「基準是什麼？」「R²_OS 是多少、顯著嗎？」「切分點怎麼選、換了會怎樣？」
「試了幾個模型？」「預測變數持續性多高？」

---

## §5 VaR／ES 與回測（公司治理、ESG 研究較少用到，一小節為限）

治理、ESG、家族企業研究很少需要 VaR；若審稿人要求「下方風險」，多半用下方標準差或
最大回撤等公司-年變數即可。真要做 VaR 時：

- 模型：歷史模擬、GARCH-t 參數法、過濾歷史模擬（FHS）。R `PerformanceAnalytics::VaR`／`ES`
  （`method = "historical"` 等，已實測可呼叫）；`rugarch::VaRTest`（建議查證）。
- **Kupiec（1995）無條件覆蓋**：例外次數 x、樣本 T、名目 p，LR_uc ~ χ²(1)。
  **Christoffersen（1998）**：例外是否群聚（獨立性 LR_ind ~ χ²(1)），合併為條件覆蓋
  LR_cc = LR_uc + LR_ind ~ χ²(2)。Python 無標準函式，用 `scipy.stats.chi2.sf` 自寫：
  ```python
  def kupiec(hits, p):                       # hits：損失超過 VaR 的 0/1 序列；x=0 時另處理
      T, x = len(hits), int(hits.sum()); pi = x / T
      lr = -2 * ((T - x) * np.log(1 - p) + x * np.log(p) - (T - x) * np.log(1 - pi) - x * np.log(pi))
      return lr, stats.chi2.sf(lr, 1)
  ```
- 台灣：單日跌幅被 −10% 截斷，個股 1 日 99% VaR 的歷史模擬會被制度上限壓住，尾部被低估；
  多日 VaR 不能用 √h 放大來迴避這件事。

**審稿人會怎麼問（§5）**：「例外次數與名目水準一致嗎（Kupiec）？例外有沒有群聚（Christoffersen）？」
「回測期是否完全在估計期之外？」「為什麼你的研究問題需要 VaR，而不是較簡單的下方風險變數？」

---

## §6 體制與結構斷點（偵測，不是識別）

**劃界**：本節回答「序列在何時改變了行為」。**不回答「為什麼改變」**。把資料偵測出的斷點
當成處理時點，再跑 DiD 或事件研究，等於讓資料自己挑處理日，是資料窺探；制度變革的因果識別
歸 `causal-inference-architect`（宣布日、生效日、首次適用年由法規決定，不由演算法決定）。

### 6.1 Markov-switching（Hamilton, 1989）
```python
from statsmodels.tsa.regime_switching.markov_regression import MarkovRegression
ms = MarkovRegression(r, k_regimes=2, trend="c", switching_variance=True).fit()
p_filt = ms.filtered_marginal_probabilities    # 只用 t 以前資訊：可當即時變數
p_smth = ms.smoothed_marginal_probabilities    # 用到全樣本：只能描述，當預測變數＝前視
ms.expected_durations                           # 各體制平均持續期，先看合不合理
# 自我迴歸版：statsmodels.tsa.regime_switching.markov_autoregression.MarkovAutoregression(r, k_regimes=2, order=1)
```
R 端 `MSwM::msmFit`（本機未安裝，建議查證）。參數仍是全樣本估計，嚴格的樣本外要擴張窗重估。
「體制」的命名（多頭／空頭、高／低波動）是研究者的詮釋，要用持續期與各體制的均值變異佐證。

### 6.2 Bai–Perron 多重斷點
```r
library(strucchange)   # 本機未安裝：函式名建議查證
bp <- breakpoints(vol_m ~ 1, h = 0.15)   # 最小區段占樣本 15%
summary(bp); confint(bp)                 # 以 BIC 選斷點數；斷點日期的信賴區間
```
Python 無附推論的 Bai–Perron 官方實作：參數穩定性可用
`statsmodels.stats.diagnostic.breaks_cusumolsresid`（只檢定、不定位），單根加一個斷點用
`arch.unitroot.ZivotAndrews`；第三方偵測套件多無推論，進論文前以 R strucchange 覆核。
**台灣已知斷點先列出來**：2015-06 漲跌幅放寬、2008 金融危機、2020 疫情。若 Bai–Perron 找到
2015-06，那是制度，不是經濟發現；先排除已知制度斷點再談新發現。

**審稿人會怎麼問（§6）**：「斷點數怎麼選？信賴區間多寬？」「體制機率是 filtered 還是 smoothed？」
「偵測到的斷點與已知制度變革重疊嗎？」「你用偵測出的日期當處理時點了嗎？」

---

## §7 對帳與再現性（同 SKILL.md Step 4）

- 每張表註明：報酬口徑（含息／價格）、頻率、樣本起訖、HAC 落後期數、因子來源與版本、
  估計窗與預測窗起訖、重估頻率。
- bootstrap 類（MCS、SPA、FHS）一律設 seed；`arch` 與 `linearmodels` 版本寫進再現性聲明。
- 「試過的設定清單」另存附錄檔：模型數、窗長數、切分點數，供資料窺探檢核用。
- N 對帳：時序迴歸的 T＝樣本期數減落後期與遺漏；FM 的期數與平均每期公司數都要報。

---

## 文獻（本檔引用；皆為期刊論文，另註明者除外）

- Ang, A., Hodrick, R. J., Xing, Y., & Zhang, X. (2006). The cross-section of volatility and expected returns. *Journal of Finance*, 61(1), 259–299.
- Bai, J., & Perron, P. (1998). Estimating and testing linear models with multiple structural changes. *Econometrica*, 66(1), 47–78.
- Bai, J., & Perron, P. (2003). Computation and analysis of multiple structural change models. *Journal of Applied Econometrics*, 18(1), 1–22.
- Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. *Journal of Econometrics*, 31(3), 307–327.
- Campbell, J. Y., & Thompson, S. B. (2008). Predicting excess stock returns out of sample: Can anything beat the historical average? *Review of Financial Studies*, 21(4), 1509–1531.
- Carhart, M. M. (1997). On persistence in mutual fund performance. *Journal of Finance*, 52(1), 57–82.
- Christoffersen, P. F. (1998). Evaluating interval forecasts. *International Economic Review*, 39(4), 841–862.
- Clark, T. E., & West, K. D. (2007). Approximately normal tests for equal predictive accuracy in nested models. *Journal of Econometrics*, 138(1), 291–311.
- Cont, R. (2001). Empirical properties of asset returns: Stylized facts and statistical issues. *Quantitative Finance*, 1(2), 223–236.
- Corsi, F. (2009). A simple approximate long-memory model of realized volatility. *Journal of Financial Econometrics*, 7(2), 174–196.
- Diebold, F. X., & Mariano, R. S. (1995). Comparing predictive accuracy. *Journal of Business & Economic Statistics*, 13(3), 253–263.
- Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. *Journal of the American Statistical Association*, 74(366), 427–431.
- Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. *Econometrica*, 50(4), 987–1007.
- Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. *Journal of Financial Economics*, 33(1), 3–56.
- Fama, E. F., & French, K. R. (2015). A five-factor asset pricing model. *Journal of Financial Economics*, 116(1), 1–22.
- Fama, E. F., & MacBeth, J. D. (1973). Risk, return, and equilibrium: Empirical tests. *Journal of Political Economy*, 81(3), 607–636.
- Gibbons, M. R., Ross, S. A., & Shanken, J. (1989). A test of the efficiency of a given portfolio. *Econometrica*, 57(5), 1121–1152.
- Glosten, L. R., Jagannathan, R., & Runkle, D. E. (1993). On the relation between the expected value and the volatility of the nominal excess return on stocks. *Journal of Finance*, 48(5), 1779–1801.
- Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business cycle. *Econometrica*, 57(2), 357–384.
- Hansen, P. R., & Lunde, A. (2005). A forecast comparison of volatility models: Does anything beat a GARCH(1,1)? *Journal of Applied Econometrics*, 20(7), 873–889.
- Hansen, P. R., Lunde, A., & Nason, J. M. (2011). The model confidence set. *Econometrica*, 79(2), 453–497.
- Kim, K. A., & Rhee, S. G. (1997). Price limit performance: Evidence from the Tokyo Stock Exchange. *Journal of Finance*, 52(2), 885–901.
- Kupiec, P. H. (1995). Techniques for verifying the accuracy of risk measurement models. *Journal of Derivatives*, 3(2), 73–84.
- Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. *Journal of Econometrics*, 54(1–3), 159–178.
- Nelson, D. B. (1991). Conditional heteroskedasticity in asset returns: A new approach. *Econometrica*, 59(2), 347–370.
- Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. *Econometrica*, 55(3), 703–708.
- Newey, W. K., & West, K. D. (1994). Automatic lag selection in covariance matrix estimation. *Review of Economic Studies*, 61(4), 631–653.
- Patton, A. J. (2011). Volatility forecast comparison using imperfect volatility proxies. *Journal of Econometrics*, 160(1), 246–256.
- Patton, A. J., & Timmermann, A. (2010). Monotonicity in asset returns: New tests with applications to the term structure, the CAPM, and portfolio sorts. *Journal of Financial Economics*, 98(3), 605–625.
- Petersen, M. A. (2009). Estimating standard errors in finance panel data sets: Comparing approaches. *Review of Financial Studies*, 22(1), 435–480.
- Shanken, J. (1992). On the estimation of beta-pricing models. *Review of Financial Studies*, 5(1), 1–33.
- Sharpe, W. F. (1964). Capital asset prices: A theory of market equilibrium under conditions of risk. *Journal of Finance*, 19(3), 425–442.
- Stambaugh, R. F. (1999). Predictive regressions. *Journal of Financial Economics*, 54(3), 375–421.
- Welch, I., & Goyal, A. (2008). A comprehensive look at the empirical performance of equity premium prediction. *Review of Financial Studies*, 21(4), 1455–1508.
- Zivot, E., & Andrews, D. W. K. (1992). Further evidence on the great crash, the oil-price shock, and the unit-root hypothesis. *Journal of Business & Economic Statistics*, 10(3), 251–270.
- 技術文件：J.P. Morgan/Reuters (1996). *RiskMetrics—Technical Document* (4th ed.)。EWMA λ=0.94 出處；版次與年份建議查證。
