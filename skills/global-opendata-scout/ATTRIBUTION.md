# 來源標示 (Attribution)

## 借用的程式碼

**無。** `scripts/intl_fetch.py` 為自行撰寫，未複製任何外部專案的程式碼。

### 關於 pandaSDMX / sdmx1（原本預計借用，實際未採用）

建置前盤點時，曾規劃採用 `pandaSDMX` / `sdmx1`（Apache-2.0）——它以一個套件
封裝多個官方統計機構的 SDMX 存取，是這個領域最成熟的方案。

**未採用的理由**：本技能的定位是「偵察與確認端點可用性」，需要看到**原始 HTTP
回應與 content-type** 才能判斷端點是否真的活著（本次實測就靠這個推翻了三個
流傳中的過時端點）。套件的抽象層會把這些訊號吃掉。
且本技能不做 SDMX 結構解析——那正是 `pandasdmx` 該上場的地方。

**因此本技能的定位是互補而非取代**：用 `intl_fetch.py` 確認端點可用並取回原始檔，
要把 SDMX XML 轉成分析用的表格時，**建議改用 `pandasdmx`**（技能文件中已如此指引）。

## 相依套件

| 套件 | 授權 | 用途 |
|---|---|---|
| `requests` | Apache-2.0 | HTTP 呼叫，以 pip 正常安裝使用，未修改原始碼 |

`scripts/intl_fetch.py` 的 TLS 相容層（解除 `VERIFY_X509_STRICT`、
保留憑證鏈與主機名驗證）直接匯入同資料夾的 `scripts/_gov_tls.py`——本技能家族
的單一正本（M2 修復，2026-09-20：原本三份各自維護已漂移，現整併於此）——
**同一使用者的自有程式碼**，非外部借用。

## 使用的資料服務

以下皆為官方免金鑰公開 API，2026-07-26 實測可用：
World Bank、Eurostat、ILOSTAT、IMF（sdmxcentral）、UN Data。
各組織的資料授權與引用格式請依其官網規定；學術使用通常需標示機構、
資料集代碼與**擷取日期**（總體統計會被回溯修訂）。

本技能供學術研究使用。

## 補充概念來源(2026-09-20 新增)

- **public-apis/public-apis**
  (https://github.com/public-apis/public-apis,MIT,
  2026-09-20 實抓 LICENSE:`/blob/master/LICENSE`)
  `references/scraper-tooling.md` 第五節提及此清單作為「找不到現成 API 時的
  起點搜尋」。**定位為 REFERENCE-ONLY**:僅當找源起點,未複製其清單內容進本技能
  的任何 catalog 檔,清單上的端點使用前一律要求自行驗活(見該節紀律)。

- **unclecode/crawl4ai**
  (https://github.com/unclecode/crawl4ai,Apache-2.0,
  2026-09-20 實抓 LICENSE:`/blob/main/LICENSE`)
  `references/scraper-tooling.md` 第四節提及此工具作為無頭瀏覽器渲染的成熟選項,
  並記錄其專案自述 0.7.7 版前存在 RCE/SSRF/硬編碼 JWT 等嚴重漏洞。**定位為
  REFERENCE-ONLY**:僅供概念參考與風險提醒,**未引入其程式碼或依賴**,且明確
  建議不自架其 Docker API 對外服務。
