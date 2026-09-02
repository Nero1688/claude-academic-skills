# TEJ 資料取得管道(2026-07 新增)

可行性報告確認「TEJ 有這筆資料」之後,下一個問題是「怎麼拿到手」。三條管道:

## 管道對照表

| 管道 | 形式 | 適合 | 前提 |
|---|---|---|---|
| ① TEJ Pro 桌面端 | GUI 點選→匯出 Excel/CSV | 一次性抓定範圍的面板資料;學術論文主流做法 | 學校授權帳號(依所屬學校之授權範圍) |
| ② TEJ API(tejapi) | Python 程式化撈取 | 需要重複更新、多表串接、可重現腳本 | 另行申請 API 金鑰(**與 TEJ Pro 帳號是兩套系統,不通用**) |
| ③ TQuant-Lab / zipline-tej | 回測框架含資料 bundle | 交易策略回測 | TQuant 授權;屬投資應用,學術面板研究通常用不到 |

## ① TEJ Pro 匯出流程(依官方手冊)

1. 主選單選資料庫(分類見 tej-catalog.md)→ 檢視方式(個股/多股/單項目比較)。
2. 條件設定:自訂**公司群組**(全上市櫃/產業別)、**欄位群組**(照 tej-variable-mapper 的採購清單勾選)、**進階日期**(研究期間,注意年季/年月頻率)。
3. 「匯出儲存資料」→ Excel/CSV → 交給 tej-data-wrangler 清理。
4. 加值功能:TEJ Pro 內建**事件研究**模組(檢定事件日異常報酬),做事件研究法時可先用它跑初步結果,再決定是否自建。
5. 智能搜尋:不確定欄位在哪個資料庫時,直接搜欄位名或 #表格。

## ② TEJ API 程式化撈取

- 申請:api.tej.com.tw 有**試用金鑰**線上申請;正式使用需購買或確認學校是否有 API 授權(TEJ Pro 校園帳號不含 API)。
- 官方 Python 套件:`pip install tejapi`
- 標準用法(金鑰一律走環境變數,絕不寫死在程式或 notebook 裡):

```python
import os
import tejapi

tejapi.ApiConfig.api_key = os.environ["TEJAPI_KEY"]  # 金鑰放環境變數
tejapi.ApiConfig.ignoretz = True

df = tejapi.get(
    "TWN/<資料表代碼>",          # 表代碼查 api.tej.com.tw 的資料表文件,勿憑記憶填
    coid=["2330", "2317"],       # 公司代碼
    mdate={"gte": "2016-01-01", "lte": "2024-12-31"},
    paginate=True,               # 大量資料必加,自動翻頁
)
```

- 資料表代碼與欄位定義以 api.tej.com.tw 官方文件為準——**表代碼絕不編造**,查
  不到就標「需向 TEJ 確認」,原則同 tej-variable-mapper。
- 撈回的 DataFrame 直接進 tej-data-wrangler 的清理流程(欄名標準化、頻率解析同樣適用)。

## ③ TEJ 官方 GitHub 資源(github.com/tejtw)

| Repo | 內容 |
|---|---|
| TQuant-Lab | 量化回測框架主倉(Jupyter 範例,MIT) |
| zipline-tej | zipline 回測引擎的 TEJ 資料改版 |
| TEJ_TOOL_API | API 工具集 |
| WelcomeToTejApi | API 新手教學 notebook |
| TEJAPI_Python_Medium_Rookies / _DataAnalysis / _Application | 由淺入深三套教學 |

教學 repo 的 notebook 是「表代碼實例」的可靠來源,查表代碼時可先看這裡的實際呼叫。

## 金鑰與帳號安全紀律

1. API 金鑰、TEJ Pro 帳密,永不寫進任何 skill、repo、notebook 或對話——金鑰只放
   環境變數(TEJAPI_KEY)或本機 .env(且 .env 必在 .gitignore)。
2. sanitize_check 清單應包含:`tejapi.ApiConfig.api_key\s*=\s*["']`(硬編碼金鑰紅旗)。
3. 助手(Claude)不代輸入帳號與登入憑證;登入動作由使用者本人完成,登入後的匯出檔或
   API 金鑰環境變數才是助手的工作介面。

## 與家族其他成員的銜接

- 發想期:本 skill 判斷「有沒有、在哪、走哪條管道」。
- 對應期:tej-variable-mapper 產出精確欄位採購清單(GUI 勾選用)或表代碼查證任務(API 用)。
- 清理期:tej-data-wrangler 接手 RAW Excel 或 API DataFrame。
- 回測需求(選股策略、報酬回測)→ 屬個人投資應用,不在本學術技能家族範圍。
