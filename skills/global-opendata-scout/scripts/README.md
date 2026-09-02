# scripts — 跨國統計資料撈取

## intl_fetch.py

### 安裝
```bash
pip install requests
```

### 兩軌設計

| 子指令 | 對象 | 說明 |
|---|---|---|
| `wb` | World Bank | 自成一格的 REST，最適合做跨國追蹤資料 |
| `sdmx` | Eurostat / ILOSTAT / IMF / UN | 通用 SDMX 客戶端，一支打通多家 |

### 用法
```bash
python intl_fetch.py wb --search "gdp per capita"
python intl_fetch.py wb --indicator NY.GDP.MKTP.CD --countries US,JP,DE --start 2015 --end 2022 -o gdp.csv
python intl_fetch.py sdmx --list-providers
python intl_fetch.py sdmx --provider ilostat --resource dataflow -o flows.xml
python intl_fetch.py sdmx --provider eurostat --dataset DEMO_R_D3DENS --params "geo=EU27_2020&time=2022" -o pop.json
python intl_fetch.py sdmx --base https://your.custom/sdmx --resource dataflow    # 自訂來源
```

### 端點狀態（2026-07-26 實測）

✅ 已實測可用、免金鑰：World Bank、Eurostat、ILOSTAT、IMF(sdmxcentral)、UN Data(http)

⚠️ 待確認、**刻意不內建**：
- **OECD**：`sdmx.oecd.org` 的 v2 路徑實測 404；`stats.oecd.org` 有回 200
  但兩個語意不同的 URL 回傳位元組完全相同的內容，疑似 catch-all。
  請查官方文件確認後用 `--base` 自行指定。
- **FRED**：需 API key。要用請以環境變數提供，**勿寫進程式碼或產出檔**。

### 重要提醒

- ⚠️ **World Bank 沒有台灣資料**（實測確認）。台灣走 `tw-opendata-scout`。
- 空值比例超過 30% 時腳本會警告——**遺漏若與應變數相關是選擇偏誤，不是資料清理**。
- 總體統計會被回溯修訂，**務必記錄抓取日期**。
- SDMX 回傳多為 XML 結構檔；要轉成分析表格建議用 `pandasdmx` 解析。
- 可設 `CONTACT_MAILTO` 環境變數在 User-Agent 帶聯絡信箱（部分機構據此提供較佳服務）。
