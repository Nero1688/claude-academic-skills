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
