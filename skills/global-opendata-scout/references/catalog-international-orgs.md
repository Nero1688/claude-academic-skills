# 國際組織資料庫目錄

> **端點狀態一律標註實測日期。標「待確認」者請勿當成可用端點寫進程式。**

## ✅ 已實測可用（2026-07-26）

### World Bank — Indicators API
- **標註**：【官方，免金鑰】
- **涵蓋**：GDP、人口、教育、貿易、治理指標（WGI）等數千個指標，多數回溯至 1960
- **base**：`https://api.worldbank.org/v2`
- **取資料**：`/country/{ISO碼;逗號分隔}/indicator/{指標碼}?format=json&date=2015:2022`
- **查指標**：`/indicator?format=json&per_page=20000`
- **⚠️ 無台灣資料**（實測確認，見 `cross-country-cautions.md` 第零節）
- **腳本**：`scripts/intl_fetch.py wb`
- **引用**：World Bank (年份). *World Development Indicators*. 指標代碼. 擷取日期.

### Eurostat
- **標註**：【官方，免金鑰】
- **涵蓋**：歐盟會員國的人口、勞動、企業、區域統計（NUTS 分區極細）
- **base**：`https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0`
- **取資料**：`/data/{datasetCode}?geo=EU27_2020&time=2022`
- **腳本**：`scripts/intl_fetch.py sdmx --provider eurostat`

### ILOSTAT（國際勞工組織）
- **標註**：【官方，免金鑰】
- **涵蓋**：就業、失業、工時、薪資、勞動關係——**對人資／勞動研究最重要的跨國源**
- **base**：`https://sdmx.ilo.org/rest`
- **⚠️ 舊 base `https://www.ilo.org/sdmx/rest` 已失效**，網路上舊教學多半還在用它
- **腳本**：`scripts/intl_fetch.py sdmx --provider ilostat`

### IMF
- **標註**：【官方，免金鑰】
- **涵蓋**：國際收支、政府財政、金融穩定指標
- **base**：`https://sdmxcentral.imf.org/ws/public/sdmxapi/rest`
- **⚠️ 實測發現**：`dataservices.imf.org` 已無法連線、`data.imf.org` 回 HTTP 403。
  網路上多數教學引用的是這兩個失效端點——**以本檔記載的 sdmxcentral 為準**。
- **腳本**：`scripts/intl_fetch.py sdmx --provider imf`

### UN Data
- **標註**：【官方，免金鑰】
- **base**：`http://data.un.org/WS/rest`
- **⚠️ 是 http 不是 https**（官方即如此）
- **腳本**：`scripts/intl_fetch.py sdmx --provider undata`

---

## ⚠️ 待確認（本工具刻意不內建）

### OECD
- **實測結果**：`https://sdmx.oecd.org/public/rest/v2/...` 多個路徑皆回 **HTTP 404
  「Could not find requested structures」**（主機存活但路徑形式不對）。
  另 `https://stats.oecd.org/...` 有回 200，但**兩個語意完全不同的 URL
  回傳位元組數完全相同（7,804,327 B）的內容**，疑似 catch-all 或轉址，
  無法確認其正確語意。
- **結論**：**不寫進內建 provider**。要用請先查 OECD 官方 API 文件確認當期路徑形式，
  再用 `intl_fetch.py sdmx --base <你查到的 base>` 自行指定。
- **不要照抄網路教學的 OECD 端點**——本次實測證明流傳的形式多已過時。

### FRED（美國聯準會聖路易分行）
- **標註**：【官方，**需申請 API key**】
- **端點**：`https://api.stlouisfed.org/fred/series/observations`（需 `api_key` 參數）
- **本工具未內建**：因為需要金鑰。若要使用，**金鑰一律走環境變數**，
  絕不寫進程式碼或產出檔（台灣官方統計來源 的金鑰紀律）。
- 涵蓋美國總體與金融時間序列，深度極佳，但**只有美國**。

---

## 付費／需訂閱（列出供對照，非開放資料）

| 名稱 | 說明 |
|---|---|
| Compustat Global / CRSP | 跨國公司財務與股價，多數商學院有訂 |
| Refinitiv（原 Thomson Reuters）| 跨國公司、ESG 評分 |
| CEIC | 亞洲總體資料涵蓋較佳，**可能含台灣**（未實測，請自行查證） |
| Penn World Table | 學術用跨國生產力資料，**免費**但需自行下載檔案（非 API） |

## 選源判準

| 你要的東西 | 建議源 |
|---|---|
| 跨國總體（GDP、人口、貿易） | World Bank |
| 跨國勞動／薪資／就業 | ILOSTAT |
| 歐盟細部區域統計 | Eurostat |
| 國際收支、政府財政 | IMF |
| 美國深度時間序列 | FRED（需 key） |
| **台灣** | 台灣官方來源:主計總處／央行／勞動部（國際庫多半沒有） |
| 跨國公司層級財務 | Compustat Global（付費） |
