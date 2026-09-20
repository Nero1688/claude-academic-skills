# 抓取工具盤點：通用網頁抓取、合規、與現成工具的定位

本 skill 的主流程優先走已實測的官方 API（World Bank、SDMX 家族，見
`intl_fetch.py`）。但跨國研究常遇到目標國家的統計機構**沒有 API，只有網頁**——
這時需要通用網頁抓取，而不是每個國家硬刻一支客戶端。本檔給抓取工具的選型判準、
合規紀律，以及兩個常被提及但**僅供參考、不建議直接引入**的外部專案的定位說明。

## 一、預設選擇：requests + BeautifulSoup

對絕大多數靜態 HTML 頁面（各國統計局的資料表格頁、開放資料入口的資料集列表），
`requests` 抓 HTML、`BeautifulSoup` 解析,是最輕量、最少依賴、最容易讓其他研究者
複現的組合，優先於任何重量級無頭瀏覽器方案。判斷是否夠用：

1. 用瀏覽器「檢視原始碼」（非開發者工具的 Elements 面板，那個是渲染後的 DOM）
   確認要的資料是否已經在原始 HTML 裡。在原始 HTML 裡 → `requests` 就夠。
2. 若原始 HTML 是空殼、資料由 JavaScript 動態載入，先找頁面背後打的 API/AJAX
   端點（瀏覽器開發者工具 → Network，找回傳 JSON 的請求），直接打那個端點——
   往往比上無頭瀏覽器更乾淨、更穩定、對站方負擔更小。這個「找背後 API」的
   升級階梯與 `public-disclosure-scout` 的 `references/dynamic-scraping-escalation.md`
   完全同構，差別只在本 skill 面對的是各國統計機構而非台灣 MOPS。
3. 只有在真的需要 JS 渲染、且找不到背後 API 時，才考慮無頭瀏覽器（見第三節
   對 crawl4ai 的定位說明）——這是成本最高的選項，能不用就不用。

## 二、速率限制、禮貌間隔、合規

跨國抓取比台灣本地抓取多一層複雜度：**各國站方的服務條款、機器人政策、
資料授權條款可能完全不同**，不能假設「台灣這樣做可以，其他國家也一樣」。

1. **請求間隔**：預設至少 1-3 秒一次請求，站方文件另有規定者從其規定；
   大量頁面（如逐頁翻爬某國開放資料入口）務必離峰執行、分批進行,不要
   短時間內對同一站台發大量並行請求。
2. **`robots.txt` 是第一步，不是唯一一步**：抓取前先讀目標站的 `robots.txt`
   確認允許的路徑與抓取頻率建議（`Crawl-delay`），但 `robots.txt` 只是
   站方對機器人的最低限度聲明，**服務條款（ToS）可能有更嚴格的限制**（如
   禁止商業使用、要求註冊、限制批次下載量），學術用途仍需自行確認 ToS 是否
   允許研究性抓取與資料再散布。
3. **識別碼**：User-Agent 帶專案名與聯絡方式（如 `mailto:` 資訊），讓站方
   在異常流量時能聯繫到你而非直接封鎖——`intl_fetch.py` 已示範此作法
   （`CONTACT_MAILTO` 環境變數）,新腳本延續同一慣例。
4. **🚫 反偵測與隱身功能一律不用**：與 `dynamic-scraping-escalation.md` 的
   合規紅線相同——遇到 CAPTCHA、遇到站方明確的反爬蟲機制,代表站方要求人工
   或不歡迎自動化存取，尊重之、改走官方批次/申請管道，**不繞過**。
5. **資料授權**：確認該國開放資料的授權條款（如是否類似台灣的政府資料開放
   授權條款、CC BY、或需要註明來源），研究使用與論文中的資料可用性聲明
   （data availability statement）要對應寫清楚。

## 三、gov.tw 情境的 TLS 慣例（跨國研究混台灣資料時適用）

本 skill 的核心定位是台灣以外的資料（台灣一律轉台灣官方來源），
但跨國比較研究常常**同時**要撈台灣資料與撈他國資料，此時若研究者自己另外寫
腳本去打 .gov.tw 網域，務必沿用家族既有慣例，不要另創一套：

- 部分 .gov.tw 憑證缺 Subject Key Identifier 擴充欄位，Python 3.13+ 預設的
  `VERIFY_X509_STRICT` 嚴格檢查會導致連線失敗（`SSLCertVerificationError`）。
- 解法統一沿用本技能 `scripts/_gov_tls.py`（家族單一正本，`from _gov_tls import
  make_session`）：**只解除** `VERIFY_X509_STRICT` 這一個旗標，**完整保留**
  憑證鏈驗證（`CERT_REQUIRED`）與主機名驗證（`check_hostname=True`）。
- **絕不使用 `verify=False`**——那會完全放棄憑證驗證，是資安掃描會攔的作法，
  也違反本家族一貫的紀律。`intl_fetch.py` 直接匯入 `_gov_tls.py`（見腳本檔頭
  註解），任何新寫的跨網域腳本都應比照。

## 四、crawl4ai：存在、授權、已知漏洞史、定位（REFERENCE-ONLY）

[unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)（Apache-2.0）是一套
成熟的 LLM 導向網頁抓取工具，底層用 Playwright 做無頭瀏覽器渲染，能把網頁轉成
乾淨的 markdown、支援 CSS/XPath 抽取——`public-disclosure-scout` 的
`dynamic-scraping-escalation.md` 第 4 級（無頭瀏覽器）已提過此工具作為成熟選項。

**本檔要額外提醒的是它的資安狀況**：crawl4ai 專案自身的說明文件揭露，
0.7.7 版之前的版本存在包括**遠端程式碼執行（RCE）、伺服器端請求偽造（SSRF）、
硬編碼 JWT 金鑰**等嚴重漏洞。這些漏洞的攻擊面主要與其**自架 API 服務**
（把 crawl4ai 包成一個對外開放的 Docker 服務,讓其他系統呼叫）有關。

**本 skill 家族的立場**：
1. **不建議自架 crawl4ai 的 Docker API 對外服務**——上述漏洞史顯示這條路線
   的攻擊面較大，且維運（版本更新、金鑰輪替）成本不小,對一個學術研究專案
   不划算。
2. 若真的需要 JS 渲染（第一、二節的方法都不夠用），優先考慮**本機直接跑
   Playwright**（不包成對外服務、不暴露網路埠、跑完即關），把攻擊面限制在
   本機單次執行的範圍內。
3. 本檔（與 `dynamic-scraping-escalation.md`）對 crawl4ai 的定位是
   **REFERENCE-ONLY**：只借鏡其「把網頁轉成 LLM 可讀結構」的概念與工具存在
   的事實，**不在本 skill 家族的任何腳本中引入其程式碼或依賴**。

## 五、public-apis：起點清單、驗活紀律、時效警語（REFERENCE-ONLY）

[public-apis/public-apis](https://github.com/public-apis/public-apis)（MIT）是一份
按領域分類、社群維護的公開 API 清單（含金融、政府、教育等分類），適合當
「這個領域有沒有現成 API」的**起點搜尋**，但有三個使用上的紀律：

1. **每一條都要自己驗活**：這是社群眾包維護的清單，端點過時、下線、改版
   是常態（本 skill 自己在建置 `intl_fetch.py` 時就實測推翻了三個網路流傳的
   國際組織端點——OECD 舊路徑 404、ILOSTAT 舊 base 失效、IMF dataservices
   已死）。清單上列出的任何端點，使用前都要比照本 skill 第五步的紀律
   （✅已實測／⚠️待確認）自己打一次確認,不能因為清單上有列就當作可用。
2. **時效警語**：清單快照的時間點與你使用的時間點之間可能差數月至數年，
   API 的免費額度、認證方式、甚至是否還存在都可能已經改變。
3. **定位是 REFERENCE-ONLY**：本 skill 家族**不直接引入**此清單的內容當作
   自己的資料源目錄——本 skill 已實測並維護的 `catalog-*.md` 系列才是可信賴
   來源；public-apis 只在「本 skill 沒收錄的領域,不知道有沒有現成 API」時，
   當作起點去搜尋，找到後仍須完整走一遍驗活與可比性檢查（`cross-country-cautions.md`）
   才能真正使用。

## 六、決策速查

| 情境 | 建議路徑 |
|---|---|
| 資料在原始 HTML 裡 | `requests` + `BeautifulSoup`，直接抽 |
| 資料由 JS 動態載入，但有背後 API | 找到該 API，直接打（優先於無頭瀏覽器） |
| 真的需要 JS 渲染且無 API 可用 | 本機跑 Playwright（不自架對外服務） |
| 不知道某領域有沒有現成 API | public-apis 當起點搜尋，找到後自行驗活 |
| 混台灣與他國資料，要連 .gov.tw | 沿用 `_gov_tls.py` 慣例，不用 `verify=False` |
| 站方明示禁止自動抓取／有 CAPTCHA | 停止自動化，改官方申請管道或人工 |

## 七、接回主流程

找到適合的抓取方式後，回到 SKILL.md 的 Step 3（撈取）與 Step 4（可比性檢查）；
台灣資料一律轉台灣官方來源；多源資料整合交棒
`anthropic-skills:multi-source-data-integrator`。
