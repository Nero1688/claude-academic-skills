# 來源標示 (Attribution)

本技能為融合式原創作品;所有程式碼均自行撰寫,未複製任何外部 repo 的程式碼。

## 概念來源

1. **ianlkl11234s/mini-taiwan-pulse**(https://github.com/ianlkl11234s/mini-taiwan-pulse,MIT)
   啟發本技能的兩個方法概念:
   - **LLM 輔助地理編碼 + 驗證退路**:該專案以「行政區白名單 + 中心點回退」約束 LLM
     地理編碼、抓出離群(368 鄉鎮白名單、centroid fallback)。本技能將此提煉為
     `references/geocoding-validation.md` 的驗證紀律,並接上家族既有的 LLM 標註信效度精神。
   - **H3 六角網格空間聚合**:該專案用 H3 做人口流動與空間指標的網格聚合。本技能將
     「H3 聚合 + 隱私去識別 + 空間權重」重新實作為研究方法工具(scripts/spatial_aggregate.py
     為自行撰寫)。
   說明:未採用該專案的核心(即時交通 3D 視覺化、Three.js/Mapbox/Supabase 前端棧),
   那屬前端工程,與本技能的「研究方法」定位不同。僅汲取上述兩個可轉移的方法概念。

2. **h3-py / Uber H3**(https://github.com/uber/h3-py,Apache 2.0)
   本技能的網格聚合以 Uber 的 H3 函式庫實作;使用時請依 Apache 2.0 保留其版權聲明。
   H3 index 系統為 Uber 之著作,本技能只是應用其公開 API。

3. **pyproj / PROJ**(座標轉換)、**geopandas / matplotlib**(出圖):
   均為開源標準工具,本技能引用其公開 API,未修改或散布其程式碼。

本技能供學術研究使用。
