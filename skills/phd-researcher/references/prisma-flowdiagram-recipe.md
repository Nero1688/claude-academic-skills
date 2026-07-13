# PRISMA 2020 流程圖一鍵產出配方(2026-07 新增)

篩選數字對帳通過後(四階段加減平衡),流程圖不必手畫。官方認可工具:
[prisma-flowdiagram/PRISMA2020](https://github.com/prisma-flowdiagram/PRISMA2020)
(R 套件+Shiny 網頁版,出處:Haddaway et al., 2022, *Campbell Systematic Reviews*)。

## 路線一:零安裝網頁版(推薦初次使用)

https://estech.shinyapps.io/prisma_flowdiagram/
填四階段數字 → 即時預覽 → 下載 PDF/PNG/SVG。適合一次性使用;
缺點:數字打錯要重填,不留可重現紀錄。

## 路線二:R 套件(可重現,建議正式論文用)

```r
# install.packages("PRISMA2020")
library(PRISMA2020)

# 官方 CSV 模板填數字(欄位:box 名稱、n、排除理由明細)
data <- read.csv("prisma_data.csv")   # 模板: PRISMA_data(檔內附範例)
data <- PRISMA_data(data)

plot <- PRISMA_flowdiagram(data,
  interactive   = FALSE,
  previous      = FALSE,    # 有前版回顧(更新型 SLR)才開
  other         = TRUE,     # 含資料庫外來源(引用追溯、灰色文獻)
  fontsize      = 11)

PRISMA_save(plot, filename = "prisma_flowdiagram.pdf", filetype = "PDF")
```

## 與本 skill 的對帳銜接(硬規則不變)

1. **先對帳後畫圖**:SKILL.md 的 PRISMA 流程對帳(識別=去重後+重複、
   篩選後=全文評讀+標題摘要排除、納入=全文評讀−全文排除)通過後,
   數字才進 CSV;圖只是對帳結果的視覺化,絕不反過來為了圖湊數字。
2. 排除理由明細(Screening 與 Eligibility 階段)要與 literature_matrix 的
   排除紀錄逐筆可對應。
3. 中文論文:PRISMA2020 套件支援自訂 box 文字,可把標籤換成中文
   (辨識/篩選/資格評讀/納入);期刊有指定語言就照期刊。
