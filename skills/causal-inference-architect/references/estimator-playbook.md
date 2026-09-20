# 估計量手冊(R 語法,套件以 CRAN 現行版為準)

再現性聲明模板:`sessionInfo()` 輸出+估計量名稱+控制組定義,一律寫進附錄。

## 1. 現代 DiD

```r
# install.packages(c("did", "fixest", "bacondecomp"))

## (a) Goodman-Bacon 分解:先看 TWFE 的比較組成有多少「壞比較」
library(bacondecomp)
bacon(y ~ treat, data = df, id_var = "firm", time_var = "year")

## (b) Callaway & Sant'Anna:組別×時期 ATT(預設首選)
library(did)
## 共變數:處理前一期固定值,不放時變值(壞控制變數警語)
## did::att_gt 以基期值處理共變數;時變且可能受處理影響的變數(ROA、外資持股、
## 環境績效)進 xformla 會引入處理後偏誤。先把每家公司 first_treat-1 年的值展開成
## 不隨時間變動的欄(never-treated 取樣本期第一年,並在論文明寫):
library(dplyr)
df <- df %>%
  group_by(firm) %>%
  mutate(base_year = ifelse(first_treat > 0, first_treat - 1, min(year)),
         size_pre  = size[match(base_year, year)],
         lev_pre   = lev[match(base_year, year)]) %>%
  ungroup()
cs <- att_gt(yname = "y", tname = "year", idname = "firm",
             gname = "first_treat",        # 首次處理年;never-treated 設 0(did 慣例)
             control_group = "notyettreated",  # 或 "nevertreated",論文要明說
             xformla = ~ size_pre + lev_pre,   # 條件平行趨勢的共變數:處理前一期固定值
             data = df, clustervars = "firm")
aggte(cs, type = "dynamic", na.rm = TRUE)  # 事件研究聚合(畫圖用);$Wpval = 前期聯合檢定 p
aggte(cs, type = "simple")                 # 整體 ATT

## (c) Sun & Abraham:fixest 內建,動態路徑
## never-treated 編碼與 did 不同:sunab 把「cohort 值不在 period 範圍內」的單位當 never-treated
## (fixest 文件 base_stagg 範例用 10000;已查證 2026-09-20)。不要與 did 共用同一欄位。
library(fixest)
df$first_treat_sa <- ifelse(df$first_treat == 0, 10000, df$first_treat)
stopifnot(sum(df$first_treat == 0) == sum(df$first_treat_sa > max(df$year)))  # 編碼核對
sa <- feols(y ~ sunab(first_treat_sa, year) + size_pre + lev_pre | firm + year,
            data = df, cluster = ~firm)
iplot(sa)                                  # 事件研究圖(草圖;投稿圖交 management-figure 的 event_study_plot)

## (d) 古典 TWFE(僅作對照,交錯場景不可單獨報告)
twfe <- feols(y ~ treat + size_pre + lev_pre | firm + year, data = df, cluster = ~firm)
```

控制組選擇的論文語言:not-yet-treated 假設「尚未採用者未預期調整」;
never-treated 假設「永不採用者與採用者可比」。兩者都跑=穩健性——但先過
robustness-battery 第二節的「對照組情境表」四個情境(全體終將受處理／門檻分批／
自願提前者／套件編碼),對上號的情境主設定要照表改,不能只寫「兩種都跑」。

## 2. 事件研究的誠實區間(前期不完美平行時)

```r
# install.packages("HonestDiD")
library(HonestDiD)
# 以事件研究係數與 VCV 輸入,回答:「允許前趨勢偏離至 M 倍,效果仍顯著嗎?」
# 報告 M 的臨界值,讓審稿人自行判斷穩健程度
```

## 3. IV / 2SLS

```r
library(fixest)
iv <- feols(y ~ size + lev | firm + year | treat ~ instrument,
            data = df, cluster = ~firm)
summary(iv, stage = 1)     # 第一階段:報 F(fixest 給 Kleibergen-Paap)
# 弱工具紅線:effective F < 10 級別要用弱工具穩健推論(AR 信賴區間),不硬報 2SLS
```

排除限制沒有統計檢定——攻防表寫制度論證+「工具不影響 Y 的其他管道」逐一排除。

## 4. RDD

```r
# install.packages(c("rdrobust", "rddensity"))
library(rdrobust); library(rddensity)
rdplot(df$y, df$running, c = cutoff)                    # 視覺化先行
rd <- rdrobust(df$y, df$running, c = cutoff)             # 局部多項式+穩健 CI
summary(rd)
rddensity(df$running, c = cutoff)                        # McCrary 操縱檢定
# 標配穩健性:頻寬×2/÷2、多項式階數、甜甜圈 RDD(剔除門檻極近點)
```

## 5. 合成控制

```r
# install.packages("Synth")  # 或 tidysynth
# 單一處理單位:供體池選擇要理論化(同產業/規模帶),前期 RMSPE 要好
# 推論用 permutation:每個供體輪流當假處理,畫 gap 圖比較
```

## 6. 估計量適用速查

| 場景 | 用 | 不要用 |
|---|---|---|
| 交錯採用+可能異質效果 | CS / SA / stacked | 單獨 TWFE |
| 同時點處理 | TWFE 可(它此時無病) | — |
| 前期趨勢可疑 | HonestDiD 敏感度 | 假裝沒看見 |
| 處理單位極少(≤5) | SCM + permutation | 大樣本漸近推論 |
| 面板短(T<4) | 謹慎;動態設定不可行 | 長事件窗 |
