# spatial-data-architect / scripts

## spatial_aggregate.py — 點資料 → H3 六角網格聚合

把帶經緯度(WGS84)的點資料聚合到 Uber H3 六角網格。內建 WGS84 範圍檢查
(擋下未轉換的 TWD97 投影座標)、隱私提示(小樣本網格)、筆數對帳。

```bash
pip install h3 pandas
python spatial_aggregate.py deals.csv --lat 緯度 --lng 經度 --value 成交價 --agg median --res 8
python spatial_aggregate.py            # 無參數=跑內建自我測試(500 合成點)
```

參數:`--lat/--lng` 座標欄名、`--value` 聚合的數值欄、`--agg` mean/median/sum/max/min/count、
`--res` H3 解析度(台灣不動產建議 7-9)、`-o` 輸出路徑。

實測(2026-08,h3 4.5.0):自我測試 500 點→325 網格、筆數對帳 500=500、TWD97 誤用防線正確擋下。

配方與進階(空間權重、多尺度、出圖)見 `../references/` 下各檔。
座標若為 TWD97,先用 pyproj 轉 WGS84(見 taiwan-spatial-notes.md)再進來。
