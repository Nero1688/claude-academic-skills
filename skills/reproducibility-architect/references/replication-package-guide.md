# 複製包實務指南(模板與檢查清單)

## Master script 骨架(R)

```r
# run_all.R — 一鍵從 raw 跑到 output。在專案根目錄執行:Rscript run_all.R
# 環境:R 4.3.x;先 renv::restore() 還原套件
set.seed(20260723)                         # 全域種子(各腳本內 bootstrap 另設)
library(here)                              # 相對路徑,絕不硬編本機家目錄的絕對路徑

source(here("code","01_clean.R"))          # raw → derived(清理)
source(here("code","02_integrate.R"))      # 多源整合(見 multi-source-data-integrator)
source(here("code","03_analysis.R"))       # 建模(見 r-spss / causal-inference)
source(here("code","04_tables_figures.R")) # 產出 output/tables 與 output/figures
message("完成:所有表圖已重建於 output/")
```

Python 版同理:`python run_all.py`,各步驟 import 或 subprocess 串接,
`np.random.seed`/`random.seed` 開頭設定。

## 資料可用性聲明模板(逐源交代)

```
Data Availability Statement
本研究使用之資料來源與取得方式如下:
1. TEJ 台灣經濟新報(付費授權):因授權條款不可公開散布。取得方式為向 TEJ
   訂閱(www.tej.com.tw);本研究使用之資料表、欄位與期間清單見複製包 /docs/tej_variables.csv。
2. 公開資訊觀測站 MOPS 重大訊息(官方公開):完整事件資料已附於複製包 /data/raw/mops/。
3. 政府開放資料(政府資料開放授權條款第 1 版):已附於複製包並註明擷取日期。
所有分析程式碼公開於 [OSF/Zenodo DOI]。有 TEJ 授權者可依 /docs 清單重建完整資料集。
```

## AI 使用揭露聲明模板(2026)

```
AI Use Disclosure
本研究於下列環節使用生成式 AI 輔助,均經作者審查與負責:
- 文獻整理與初步歸納:[工具名]
- 分析程式碼撰寫與除錯輔助:[工具名]
- 語言潤飾:[工具名]
資料分析之判斷、結果詮釋與學術主張均由作者做出;AI 未用於代造資料或結果。
```
(依目標期刊的 AI 政策微調;有些期刊有指定表格或位置。)

## 合成資料做法(受限資料的程式驗證)

```r
# 產生結構相同、數值為合成的假資料,讓程式碼可跑通(驗證程式邏輯,非重現數字)
# 保留:欄位名、型別、大致分布、面板結構;不保留:真實數值、可識別資訊
synth <- data.frame(
  coid = sprintf("%04d", sample(1000:9999, N, replace=TRUE)),
  year = sample(2016:2024, N, replace=TRUE),
  roa  = rnorm(N, 0.05, 0.08),  # 分布近似真實但為亂數
  tnfd = rbinom(N, 1, 0.15)
)
# README 註明:此為合成資料,僅供驗證程式可執行;真實結果需授權資料重跑
```

## 封存平台選擇

| 平台 | 特點 | 適用 |
|---|---|---|
| Zenodo | 免費、給 DOI、可綁 GitHub release | 通用首選 |
| OSF | 開放科學生態、可含預先註冊 | 含 preregistration 的研究 |
| Harvard Dataverse | 社科標準、版本管理 | 社科資料集 |
GitHub 本身不算長期封存(會變動、可刪);要 DOI 快照才算數。

## 複製包最終檢查清單

- [ ] raw/ 唯讀,所有清理輸出到 derived/
- [ ] master script 一鍵從 raw 跑到全部 output,中途無需手動
- [ ] 環境鎖定檔(renv.lock / requirements.txt)在,版本已聲明
- [ ] 全域與各步驟 seed 已設
- [ ] 全部相對路徑,無本機絕對路徑
- [ ] 輸出檔名對應論文表號/圖號
- [ ] 三份聲明(資料可用性/程式碼可用性/AI 使用)已備
- [ ] 受限資料:程式碼公開+存取指引+(可選)合成資料
- [ ] 在乾淨環境(或請同事)實跑通過
- [ ] 封存到 Zenodo/OSF 取得 DOI,寫進論文
- [ ] 打包前跑 thesis-consistency-audit,確認輸出數字與稿件一致
