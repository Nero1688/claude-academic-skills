# 方法與軟體引用清單(投稿時務必正確引用)

本 skill 教你使用的估計量與 R 套件,都是學者的實質貢獻。頂刊要求方法與軟體都要引用;
正確引用既是學術規範,也是對這些作者最恰當的致謝。下列為建議引用(以各論文/套件
官方 citation 為準,投稿前核對最新版本與頁碼)。

## 現代 DiD 方法

- **Goodman-Bacon (2021)**, "Difference-in-differences with variation in treatment
  timing," *Journal of Econometrics* — TWFE 分解。
- **Callaway & Sant'Anna (2021)**, "Difference-in-differences with multiple time
  periods," *Journal of Econometrics* — 組別×時期 ATT 估計量(`did` 套件)。
- **Sun & Abraham (2021)**, "Estimating dynamic treatment effects in event studies
  with heterogeneous treatment effects," *Journal of Econometrics* — 交互加權事件研究。
- **de Chaisemartin & D'Haultfœuille (2020)**, *American Economic Review* — 異質處理效應 DiD。
- **Rambachan & Roth (2023)**, "A more credible approach to parallel trends,"
  *Review of Economic Studies* — 誠實區間(`HonestDiD`)。
- **Baker, Larcker & Wang (2022)**, "How much should we trust staggered
  difference-in-differences estimates?" *Journal of Financial Economics* — 財務審稿人
  引用交錯 DiD 問題的標準文獻;財務家族稿件用交錯 DiD 時必引。
- **Roth, Sant'Anna, Bilinski & Poe (2023)**, "What's trending in difference-in-differences?
  A synthesis of the recent econometrics literature," *Journal of Econometrics* — 現代 DiD
  總覽;識別策略節引它說明「為何選這個估計量」。
- **Callaway, Goodman-Bacon & Sant'Anna**, "Difference-in-differences with a continuous
  treatment" — 連續處理/劑量設計的強平行趨勢假設(R `contdid`)。已查證 2026-09-20:
  仍為 NBER 工作論文 w32117 / arXiv 2107.02637(最近版本 2025),未見期刊版;投稿前
  **建議查證**刊出狀態,以當時最新版本引用。
- **Arkhangelsky, Athey, Hirshberg, Imbens & Wager (2021)**, "Synthetic
  difference-in-differences," *American Economic Review* — 合成 DiD(R `synthdid`)。

## 衝擊品質與自然實驗的可信度(財務家族第一輪必問)

- **Atanasov & Black (2016)**, "Shock-based causal inference in corporate finance and
  accounting research," *Critical Finance Review* — 衝擊品質清單(強度、外生性、
  only-through、如同隨機、共變數平衡、無預期);robustness-battery 第七節「衝擊品質六問」
  的依據。
- **Abadie, Athey, Imbens & Wooldridge (2023)**, "When should you adjust standard errors
  for clustering?" *Quarterly Journal of Economics* — 叢集層級由抽樣設計與處理指派層級
  決定;表註引它說明叢集選擇。
- **Simonsohn, Simmons & Nelson (2020)**, "Specification curve analysis,"
  *Nature Human Behaviour* — 設定曲線(R `specr`)。

## 其他識別方法

- **Imbens & Lemieux (2008)** / **Calonico, Cattaneo & Titiunik (2014)** — RDD
  (`rdrobust` 的穩健偏誤校正 CI)。
- **Abadie, Diamond & Hainmueller (2010)** — 合成控制(`Synth`)。
- **弱工具**:Stock & Yogo (2005);Montiel Olea & Pflueger (2013) 的 effective F;
  **Lee, McCrary, Moreira & Porter (2022)**, "Valid t-ratio inference for IV,"
  *American Economic Review* — tF 程序,單一工具時依第一階段 t 值調整臨界值;
  「F > 10 經驗法則已不被接受」的依據。
- **Jiang (2017)**, "Have instrumental variables brought us closer to the truth,"
  *Review of Corporate Finance Studies* 6(2), 127–140(已查證 2026-09-20)— IV 估計值
  普遍大於 OLS 的系統性檢討;解釋 IV vs OLS 方向時引。
- **Cinelli, Forney & Pearl (2024)**, "A crash course in good and bad controls,"
  *Sociological Methods & Research* 53(3), 1071–1104(線上首發 2022;已查證 2026-09-20)—
  壞控制變數的速查;robustness-battery 通用層「壞控制變數」列的依據。

## 事件研究估計(完整清單與卷期頁見 `event-study-estimation.md` 第九節)

- **Boehmer, Musumeci & Poulsen (1991)**, *Journal of Financial Economics* — 標準化橫斷面檢定(BMP),
  處理事件誘發的變異;短窗市場反應的預設主檢定。
- **Kolari & Pynnönen (2010)**, *Review of Financial Studies* — 異常報酬橫斷面相關的調整;事件日叢集時必引。
- **Corrado (1989)**, *Journal of Financial Economics*;**Corrado & Zivney (1992)**, *Journal of Financial
  and Quantitative Analysis* — 等級檢定與標準化等級。
- **Patell (1976)**, *Journal of Accounting Research*;**Cowan (1992)**, *Review of Quantitative Finance and
  Accounting* — 標準化檢定與廣義符號檢定。
- **Barber & Lyon (1997)**、**Kothari & Warner (1997)**,皆 *Journal of Financial Economics*;**Fama (1998)**,
  *Journal of Financial Economics*;**Mitchell & Stafford (2000)**, *Journal of Business* — 長期事件的
  BHAR 偏誤與 calendar-time 組合。

## 樣本外預測評估與資料窺探(robustness-battery 第九節)

- **López de Prado (2018)**, *Advances in Financial Machine Learning*, Wiley — purged k-fold 與 embargo(第 7 章)。
- **Diebold & Mariano (1995)**, "Comparing predictive accuracy," *Journal of Business & Economic Statistics*,
  13(3), 253–263;**Harvey, Leybourne & Newbold (1997)**, *International Journal of Forecasting*, 13(2),
  281–291 — 預測準確度比較與小樣本修正。
- **Clark & West (2007)**, "Approximately normal tests for equal predictive accuracy in nested models,"
  *Journal of Econometrics*, 138(1), 291–311。
- **Campbell & Thompson (2008)**, "Predicting excess stock returns out of sample: Can anything beat the
  historical average?" *Review of Financial Studies*, 21(4), 1509–1531;**Welch & Goyal (2008)**,
  *Review of Financial Studies*, 21(4), 1455–1508。
- **Newey & West (1987)**, *Econometrica*, 55(3), 703–708;**Hodrick (1992)**, *Review of Financial
  Studies*, 5(3), 357–386;**Driscoll & Kraay (1998)**, *Review of Economics and Statistics*, 80(4),
  549–560 — 重疊標籤與面板的 HAC 標準誤。
- **Bailey & López de Prado (2014)**, "The deflated Sharpe ratio," *Journal of Portfolio Management*,
  40(5), 94–107;**Bailey, Borwein, López de Prado & Zhu (2017)**, "The probability of backtest
  overfitting," *Journal of Computational Finance*, 20(4)(頁碼建議查證)。
- **Harvey, Liu & Zhu (2016)**, "… and the cross-section of expected returns," *Review of Financial
  Studies*, 29(1), 5–68;**Harvey (2017)**, "The scientific outlook in financial economics," *Journal of
  Finance*, 72(4), 1399–1440;**Lo & MacKinlay (1990)**, "Data-snooping biases in tests of financial asset
  pricing models," *Review of Financial Studies*, 3(3), 431–467。
- **Benjamini & Yekutieli (2001)**, *Annals of Statistics*, 29(4), 1165–1188;**White (2000)**, "A reality
  check for data snooping," *Econometrica*, 68(5), 1097–1126;**Hansen (2005)**, "A test for superior
  predictive ability," *Journal of Business & Economic Statistics*, 23(4), 365–380;**Romano & Wolf (2005)**,
  "Stepwise multiple testing as formalized data snooping," *Econometrica*, 73(4), 1237–1282。
- **Gu, Kelly & Xiu (2020)**, "Empirical asset pricing via machine learning," *Review of Financial Studies*,
  33(5), 2223–2273;**McLean & Pontiff (2016)**, "Does academic research destroy stock return
  predictability?" *Journal of Finance*, 71(1), 5–32;**Shumway (1997)**, "The delisting bias in CRSP
  data," *Journal of Finance*, 52(1), 327–340。
- **Glasserman & Lin (2023)**, 以 GPT 情緒分析預測股票報酬的前視偏誤評估,arXiv 工作論文;
  期刊版刊名與卷期**建議查證**。

## R 套件(軟體引用,用 `citation("套件名")` 取官方格式)

- `did` — Callaway & Sant'Anna。
- `fixest` — Laurent Bergé (2018), "Efficient estimation of maximum likelihood
  models with multiple fixed effects."
- `bacondecomp` — Goodman-Bacon, Goldring & Nichols。
- `HonestDiD` — Rambachan & Roth。
- `rdrobust` — Calonico, Cattaneo, Titiunik 等。
- `Synth` — Abadie, Diamond & Hainmueller。

## SEM/PLS(見 r-spss-syntax-architect 的 sem-pls-lane)

- `lavaan` — Rosseel (2012), *Journal of Statistical Software*。
- `seminr` — Ray, Danks & Calero Valdez。

## 使用紀律

1. 用了哪個估計量/套件就引用哪個;不要只寫「用 DiD」而不指明估計量與出處。
2. 套件版本寫進再現性聲明(reproducibility-architect 的環境鎖定)——
   計量套件更新可能改變結果,版本本身是可重現的一部分。
3. `citation("套件名")` 在 R 裡直接產出官方引用格式,別自己編。
