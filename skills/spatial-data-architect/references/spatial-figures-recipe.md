# 出版級空間地圖配方(靜態,論文/簡報用)

本 skill 畫「有地理底圖的空間圖」;純統計圖(森林圖/交互作用)歸 management-figure。
輸出目標:300dpi、色盲友善、可放期刊與口試簡報的**靜態**地圖。
(即時 3D/WebGL 互動不在此範圍。)

依賴:geopandas + matplotlib(+ mapclassify 做分級)。
注意:geopandas 依賴 GDAL/shapely/pyproj,安裝較重;`pip install geopandas mapclassify matplotlib`。

## 1. Choropleth 面量圖(行政區著色)

```python
import geopandas as gpd
import matplotlib.pyplot as plt

# 讀行政區界(TWD97 shapefile,來自 台灣官方統計來源)
gdf = gpd.read_file("towns_twd97.shp")
gdf = gdf.merge(stats, on="town_code")          # 併入每區的數值(如中位房價)

fig, ax = plt.subplots(figsize=(7, 8))
gdf.plot(column="price_med", scheme="quantiles", k=5,   # 分位數分級,避免離群壓縮色階
         cmap="YlOrRd", legend=True, edgecolor="white", linewidth=0.3, ax=ax,
         legend_kwds={"title": "中位成交價(萬/坪)"},
         missing_kwds={"color": "lightgrey", "label": "無資料"})
ax.set_axis_off(); ax.set_title("各行政區房價分布", fontproperties=...)  # 中文字型見下
fig.savefig("choropleth.png", dpi=300, bbox_inches="tight")
```

分級法(scheme)選擇:資料右偏(房價常態)用 `quantiles` 或 `fisher_jenks`,
不要用等距 `equal_interval`(會被極端值壓成一片同色)。

## 2. Hexbin 六角密度圖(H3 聚合結果上色)

```python
from shapely.geometry import Polygon
import geopandas as gpd, h3

grid = pd.read_csv("deals_h3res8.csv")          # spatial_aggregate.py 產出
grid["geometry"] = [Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(c)])
                    for c in grid["h3"]]
gg = gpd.GeoDataFrame(grid, geometry="geometry", crs="EPSG:4326")
gg = gg[gg["n"] >= 3]                            # 隱私:遮罩小樣本格
gg.plot(column="price", cmap="viridis", legend=True, figsize=(7, 8))
```

## 3. 中文字型(沿用家族 management-figure 紀律)

matplotlib 預設無中文,標楷體/黑體要指定;字型缺就誠實 fallback,不假裝已套用:
```python
from matplotlib.font_manager import FontProperties
import matplotlib
for f in ["Microsoft JhengHei", "DFKai-SB", "PMingLiU"]:
    try:
        fp = FontProperties(fname=None, family=f); matplotlib.rcParams["font.sans-serif"]=[f]
        matplotlib.rcParams["axes.unicode_minus"]=False; break
    except Exception: continue
# 找不到中文字型時,標題改英文並在圖說註明,不要出現豆腐方塊
```

## 4. 出版紀律

- 一定要有:比例尺或明確範圍、圖例含單位、資料來源與擷取日期、色盲友善色盤。
- choropleth 的視覺陷阱:大面積行政區在視覺上「更重要」,但可能人口/交易量很少——
  必要時併附密度圖或人口加權,避免誤導(這與 global-opendata-scout 的涵蓋偏誤同精神)。
- 底圖與資料的 CRS 要一致(都轉 WGS84 或都 TWD97),否則會錯位。
