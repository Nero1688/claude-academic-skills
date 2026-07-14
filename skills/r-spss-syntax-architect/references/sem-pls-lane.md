# SEM 第四軌:CB-SEM(lavaan)與 PLS-SEM(seminr)(2026-07 新增)

問卷研究的結構模型軌。**選型先於語法**:

| | CB-SEM(lavaan) | PLS-SEM(seminr/SmartPLS) |
|---|---|---|
| 目的 | 理論檢定(共變數導向) | 預測導向、探索性 |
| 構念 | 反映性為主 | 形成性構念友善 |
| 樣本 | 較大(參數×5–10) | 較小可行(但別拿此當偷懶藉口) |
| 主場 | OB/HRM、心理 | 資管(MISQ 系)、行銷 |
| 配適 | χ²、CFI/TLI、RMSEA、SRMR | 無全域配適,重 R²/Q²/路徑 |

期刊語言注意:資管與行銷對 PLS 接受度高;財金與 OB 頂刊偏 CB-SEM。
投哪裡,說哪裡的話。

## CB-SEM(lavaan)

```r
library(lavaan)
model <- '
  # 測量模型(先單獨跑 CFA 通過再進結構)
  TRUST =~ t1 + t2 + t3 + t4
  SAT   =~ s1 + s2 + s3
  LOY   =~ l1 + l2 + l3
  # 結構模型
  SAT ~ a*TRUST
  LOY ~ b*SAT + c*TRUST
  # 中介效果(bootstrap)
  ind := a*b
'
fit <- sem(model, data = df, estimator = "MLR",   # 非常態用穩健 MLR
           se = "bootstrap", bootstrap = 5000)
summary(fit, fit.measures = TRUE, standardized = TRUE)
parameterEstimates(fit, boot.ci.type = "bca.simple")  # 中介 CI 用 BCa
```

- 配適慣例(報告用,並附「慣例非鐵律」意識):CFI/TLI ≥ .90(佳 .95)、
  RMSEA ≤ .08(佳 .06)、SRMR ≤ .08。切點出自模擬研究,勿當司法判決。
- 信效度:CR ≥ .70、AVE ≥ .50、區辨效度 Fornell-Larcker **加報 HTMT**(見下)。
- 測量恆等性(跨群比較前必做)→ 轉 ob-hrm-scale-adaptor 的 MI 三階流程。

## PLS-SEM(seminr)

```r
library(seminr)
mm <- constructs(
  composite("TRUST", multi_items("t", 1:4)),
  composite("PERF",  multi_items("p", 1:3), weights = mode_B),  # 形成性用 mode_B
  composite("LOY",   multi_items("l", 1:3))
)
sm <- relationships(
  paths(from = "TRUST", to = c("PERF", "LOY")),
  paths(from = "PERF",  to = "LOY")
)
pls  <- estimate_pls(data = df, measurement_model = mm, structural_model = sm)
boot <- bootstrap_model(pls, nboot = 5000, seed = 20260715)
summary(boot)
```

- 測量評估:反映性——loading ≥ .708、CR、AVE;**HTMT < .85(嚴)/.90(寬)**
  且 bootstrap CI 不含 1;形成性——權重顯著性+VIF < 3(共線)。
- 結構評估:路徑係數 bootstrap CI、R²、f²、Q²(預測相關);報告格式對齊
  目標期刊慣例(MISQ/JM 系的表格語言)。
- 誠實紀律:「小樣本所以用 PLS」不是理由——樣本小是檢定力問題,換方法不會
  變出檢定力;選 PLS 要用「預測導向/形成性構念」等正當理由。

## 共同紀律(兩軌通用)

1. 測量模型先過,結構模型才有意義;CFA/測量評估失敗就回量表層(ob-hrm)。
2. 問卷資料先過 survey-research-architect 的品質放行與 CMV 檢驗再進 SEM。
3. bootstrap 一律 5000 起、設 seed、寫進再現性聲明。
4. 模型比較(競爭模型)比單一模型的完美配適更有說服力。
