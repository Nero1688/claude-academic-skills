# 如何找到「任一國家」的官方統計

國際組織只涵蓋主要指標。要細到「某國某產業的受僱員工薪資」，就得找**該國自己的統計機構**。
這是一套可重複的方法，不是清單——因為世界上有 200 個國家，清單一定不完整也一定會過時。

## 五步法

### Step 1｜找該國的國家統計局（NSO）

每個國家都有一個中央統計機關，名稱各異：

| 類型 | 例子 |
|---|---|
| Statistics + 國名 | Statistics Canada、Statistics Korea、Statistics Netherlands |
| National Institute of Statistics | INSEE（法）、ISTAT（義）、INE（西/葡語系） |
| Bureau/Office of Statistics | 美國 BLS/BEA/Census（**美國沒有單一 NSO，分散多機關**） |
| 內含於財政或經濟部 | 部分開發中國家 |

**最可靠的入口**：聯合國統計司維護各國 NSO 的官方連結清單；
另 World Bank、IMF 的國別頁通常也連到該國統計機關。
搜尋語法：`"national statistics office" <國名>` 或 `<國名> 統計局 official`。

⚠️ **台灣**：主計總處（DGBAS）是統計主管機關，但**不在多數國際 NSO 清單裡**
（會籍問題）。台灣資料走官方來源（主計總處／央行／勞動部）。

### Step 2｜判斷它是否支援 SDMX

SDMX 是統計交換的國際標準。**支援 SDMX 的機構可以用同一支客戶端打通**，
不必為每個國家手刻 wrapper。判斷方法：

1. 在該機構網站找 "API"、"Web services"、"SDMX"、"開發者" 字樣
2. 試 `https://<統計局網域>/sdmx` 或 `.../rest/dataflow` 這類慣用路徑
3. 回傳 `application/vnd.sdmx.structure+xml` 就是支援

支援 → 用 `scripts/intl_fetch.py sdmx --base <base URL>`
不支援 → 進 Step 3

### Step 3｜找該國的開放資料入口

多數國家有中央開放資料平台，網域慣例：
`data.gov.<國碼>`（如 data.gov.uk、data.gov.sg、data.gov.au）
或 `<國名>.opendata...`。歐盟另有 `data.europa.eu` 彙整各會員國。

⚠️ 開放資料平台上的統計常是**快照或子集**，不一定與統計局官網同步。
研究用途應**以統計局官方數字為準**，開放資料平台當作方便的取得管道。

### Step 4｜確認四件事再投入

找到源之後，投入清洗前先確認（任一不符就要調整研究設計）：

1. **涵蓋期間**是否覆蓋你的研究期間
2. **頻率**（年／季／月）是否符合你的分析單位
3. **定義**是否與其他國家可比（見 `cross-country-cautions.md`）
4. **授權**是否允許學術使用與再散布（多數官方統計允許，但**要查**）

### Step 5｜記錄來源譜系

每一個抓下來的數列都要記：機構全名、資料集代碼、**抓取日期**、指標定義連結。
總體統計會被回溯修訂，沒記日期就無法重現。
交棒 `anthropic-skills:reproducibility-architect` 做複製包時會用到。

## 主要國家的統計入口（快速起點，非完整清單）

> 以下為**方向指引**，本檔未逐一實測其 API 端點。
> 使用前務必自行確認當期路徑——各國統計局改版頻繁。

| 國家／地區 | 主要機構 | 備註 |
|---|---|---|
| 美國 | BLS（勞動）、BEA（國民所得）、Census（普查）、FRED（彙整，需 key） | 無單一 NSO，依主題分流 |
| 英國 | ONS（Office for National Statistics） | 開放資料成熟 |
| 歐盟整體 | Eurostat | 已實測，見目錄檔 |
| 日本 | 総務省統計局 / e-Stat | e-Stat 有 API（需註冊） |
| 韓國 | Statistics Korea (KOSIS) | |
| 中國 | 國家統計局 | |
| 新加坡 | SingStat | |
| 澳洲 | ABS | |
| 加拿大 | Statistics Canada | 有成熟 API |
| **台灣** | 主計總處、央行、勞動部 | **直接走官方來源**，國際庫多無涵蓋 |

## 找不到怎麼辦（誠實路徑）

依序考慮，**不要編造來源**：

1. **改用國際組織的估計值**——World Bank／ILOSTAT 常有各國估計值，
   雖不如該國原始統計細緻，但至少可比。
2. **改變分析單位**——找不到細產業別，就退到大產業別。
3. **縮小樣本國家範圍**——只納入資料齊備的國家，
   但**必須揭露這造成的選擇偏誤**（見 cautions 第五節）。
4. **誠實回報「查無」**——並說明查過哪些地方、缺口在哪。
   這比生一個看似合理但錯誤的來源有價值得多。
