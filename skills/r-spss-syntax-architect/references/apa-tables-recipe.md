# 迴歸表直出 Word(APA 格式)配方(2026-07 新增)

手抄係數進 Word 表是 L-003(數字對不上)的最大來源。能程式直出就直出,
人只負責核對不負責抄寫。

## R 路線(推薦):modelsummary / flextable → .docx

```r
# install.packages(c("modelsummary", "flextable"))
library(modelsummary)

models <- list("模型一 (ROA)" = m1, "模型二 (Tobin's Q)" = m2)
modelsummary(models,
  output   = "regression_table.docx",       # 直接輸出 Word
  stars    = c("*" = .1, "**" = .05, "***" = .01),   # 星號慣例依目標期刊調整
  coef_map = c("tnfd" = "TNFD 揭露", "esg_e" = "環境構面績效",
               "size" = "公司規模", "lev" = "負債比率"),   # 變數中文名對照
  gof_map  = c("nobs", "r.squared", "adj.r.squared"),
  fmt      = 3,                              # 小數三位
  notes    = "註:括號內為叢集穩健標準誤;含公司與年度固定效果。")
```

- 相關矩陣與敘述統計:`datasummary_correlation(df)`、`datasummary_skim(df)` 同樣可 output docx。
- 純 APA 心理學格式(t 檢定/ANOVA/迴歸):apaTables 套件 `apa.reg.table(m1, filename="t1.doc")`。

## Python 路線:Stargazer 風格 + python-docx

```python
# pip install stargazer  (Python 版 stargazer,吃 statsmodels 結果)
from stargazer.stargazer import Stargazer
html = Stargazer([m1, m2]).render_html()     # linearmodels 結果需先轉 statsmodels 或手工表
```
linearmodels 結果建議手工組表:`params/std_errors/pvalues` 三個 Series 拼 DataFrame
→ python-docx 寫表(格式控制最精準,參考 thesis-consistency-audit 的表格慣例)。

## SPSS 路線

OUTPUT EXPORT 直出 Word:
```spss
OUTPUT EXPORT /DOC DOCUMENTFILE='C:\output\tables.docx'.
```
SPSS 表格樣式先在 編輯→選項→樞紐分析表 選 APA 樣板,再輸出。

## 三條紀律

1. 星號慣例(10%/5%/1% 或 5%/1%/0.1%)以**目標期刊**為準,表註寫明。
2. 變數順序:自變數→調節→交乘→控制→固定效果聲明→N/R²,全文所有表一致。
3. 直出後仍要跑 thesis-consistency-audit 對帳——直出防抄錯,不防模型跑錯。
