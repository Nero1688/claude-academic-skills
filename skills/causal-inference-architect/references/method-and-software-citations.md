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

## 其他識別方法

- **Imbens & Lemieux (2008)** / **Calonico, Cattaneo & Titiunik (2014)** — RDD
  (`rdrobust` 的穩健偏誤校正 CI)。
- **Abadie, Diamond & Hainmueller (2010)** — 合成控制(`Synth`)。
- **弱工具**:Stock & Yogo (2005);Montiel Olea & Pflueger (2013) 的 effective F。

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
