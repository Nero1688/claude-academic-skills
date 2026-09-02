# H3 六角網格聚合配方(h3-py 4.x)

Uber H3 是全球階層式六角網格系統。核心優點:面積近似相等、任兩鄰居距離一致、
解析度階層可調、去識別友善。本檔配方對應 h3-py **4.x**(函式名與 3.x 不同)。

## 解析度對照(台灣不動產研究常用)

| res | 平均邊長 | 尺度 | 適用 |
|---|---|---|---|
| 6 | ~3.2 km | 鄉鎮 | 全國概覽 |
| 7 | ~1.2 km | 區域 | 縣市內分區、通勤圈 |
| 8 | ~0.53 km | 里級 | 房價熱區、社區尺度(不動產最常用) |
| 9 | ~0.20 km | 街廓 | 街道級密度(資料量大時) |
| 10 | ~0.075 km | 建物群 | 極細,樣本要夠多否則太稀疏 |

選 res 的判準:每格至少要有足夠觀測值(隱私+統計),又要細到能看出空間變異。
房價研究從 res 8 起手,視樣本密度上下調。

## 核心 API(h3 4.x)

```python
import h3
# 點 → 網格(注意 4.x 是 latlng,不是 3.x 的 geo_to_h3)
cell = h3.latlng_to_cell(lat, lng, res)      # 經緯度(WGS84)→ H3 index
lat2, lng2 = h3.cell_to_latlng(cell)          # 網格 → 中心座標
boundary = h3.cell_to_boundary(cell)          # 六個頂點(畫圖用)
neighbors = h3.grid_disk(cell, k=1)           # k 環鄰居(空間權重、平滑用)
edge_km = h3.average_hexagon_edge_length(res, unit='km')
# 階層:粗細轉換(多尺度分析)
parent = h3.cell_to_parent(cell, res-1)
children = h3.cell_to_children(cell, res+1)
```

## 聚合骨架(直接用 scripts/spatial_aggregate.py,或自寫)

```python
import pandas as pd, h3
df = pd.read_csv("deals.csv")                 # 需有 lat/lng(WGS84)與數值欄
df["h3"] = [h3.latlng_to_cell(a, o, 8) for a, o in zip(df.lat, df.lng)]
grid = (df.groupby("h3")
          .agg(n=("price","size"), price_med=("price","median"))
          .reset_index())
grid[["clat","clng"]] = [h3.cell_to_latlng(c) for c in grid.h3]
# 隱私:小樣本格遮罩
grid.loc[grid.n < 3, "price_med"] = None       # n<3 不揭露,避免反推個別交易
```

## H3 當空間權重(交棒空間迴歸前)

H3 的 `grid_disk(cell, k)` 給出鄰接關係,可直接建鄰接型空間權重 W:
- k=1:共邊六鄰(queen 類比);k=2:更大鄰域。
- 產出「格 i 的鄰居清單」→ 交 r-spss 的 spdep 建 listw 跑 Moran's I 與空間迴歸。
- 注意:H3 鄰接是「網格鄰接」,若研究的空間互動是「距離帶」或「行政區鄰接」,
  用對應的 W 定義,不要因為 H3 方便就套錯理論。

## 陷阱

1. **res 混用**:不同 res 的 H3 index 不可混在同一份分析;固定一個 res。
2. **邊界效應**:研究區邊緣的網格鄰居在區外會缺,Moran's I 要處理(如只保留內部格)。
3. **空網格**:沒有觀測的網格不會出現在 groupby 結果;若分析需要完整網格(如密度平滑),
   要另外補齊 res 範圍內全部網格再左連結。
