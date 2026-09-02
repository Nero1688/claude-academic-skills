#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spatial_aggregate.py — 點資料 → H3 六角網格聚合(空間分析的地基工具)

用途:把「帶經緯度的點觀測值」(如每筆不動產成交、每家公司總部)聚合到 Uber H3
六角網格,產出可分析、可畫圖、隱私較安全的網格層資料。為什麼用 H3 而非行政區:
  - 六角網格面積相等、鄰居距離一致(行政區大小懸殊,會扭曲密度比較)
  - 解析度可調(res 5~10),同一份點資料可看不同尺度
  - 天然去識別:個別地址被歸併到網格,降低可識別性(隱私紅線)

用法:
  python spatial_aggregate.py points.csv --lat lat --lng lng --value price --res 8
  python spatial_aggregate.py points.csv --lat 緯度 --lng 經度 --agg count --res 7 -o out.csv

輸出:每個 H3 網格一列(h3, 中心 lat/lng, n 筆數, 聚合值),可直接餵 choropleth/hexbin 出圖。

依賴:h3 (pip install h3)、pandas。座標務必為 WGS84(EPSG:4326);
若你的資料是 TWD97(EPSG:3826,台灣官方常用),先轉換再進來(見 references/taiwan-spatial-notes.md)。
"""
from __future__ import annotations

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import h3
    import pandas as pd
except ImportError:
    sys.exit("[錯誤] 需要 h3 與 pandas:pip install h3 pandas")


def aggregate(df, lat_col, lng_col, res, value_col=None, agg="mean"):
    """把點聚合到 H3 網格。回傳每格一列的 DataFrame。"""
    # WGS84 合理範圍檢查(抓到 TWD97 投影座標這種明顯錯誤)
    if not (df[lat_col].between(-90, 90).all() and df[lng_col].between(-180, 180).all()):
        raise ValueError(
            "經緯度超出 WGS84 範圍——你的座標可能是 TWD97 投影(公尺),"
            "請先轉成 WGS84(見 taiwan-spatial-notes.md),不要硬聚合。")

    df = df.dropna(subset=[lat_col, lng_col]).copy()
    df["h3"] = [h3.latlng_to_cell(la, lo, res)
                for la, lo in zip(df[lat_col], df[lng_col])]

    grp = df.groupby("h3")
    out = grp.size().rename("n").reset_index()
    if value_col:
        if agg == "count":
            pass
        else:
            v = getattr(grp[value_col], agg)().rename(value_col)
            out = out.merge(v.reset_index(), on="h3")

    # 網格中心座標(畫圖與標註用)
    centers = [h3.cell_to_latlng(c) for c in out["h3"]]
    out["center_lat"] = [c[0] for c in centers]
    out["center_lng"] = [c[1] for c in centers]
    return out


def main():
    ap = argparse.ArgumentParser(description="點資料 → H3 六角網格聚合")
    ap.add_argument("csv", nargs="?", help="輸入 CSV(省略則跑內建自我測試)")
    ap.add_argument("--lat", default="lat", help="緯度欄名")
    ap.add_argument("--lng", default="lng", help="經度欄名")
    ap.add_argument("--value", default=None, help="要聚合的數值欄(如成交價);省略只算筆數")
    ap.add_argument("--agg", default="mean", help="聚合方式:mean/median/sum/max/min/count")
    ap.add_argument("--res", type=int, default=8, help="H3 解析度 0-15(台灣不動產建議 7-9)")
    ap.add_argument("-o", "--output", default=None)
    args = ap.parse_args()

    if not args.csv:
        return self_test()

    df = pd.read_csv(args.csv)
    for c in (args.lat, args.lng):
        if c not in df.columns:
            sys.exit(f"[錯誤] 找不到欄位 {c};現有欄位:{list(df.columns)}")
    out = aggregate(df, args.lat, args.lng, args.res, args.value, args.agg)
    out = out.sort_values("n", ascending=False)

    dst = args.output or (args.csv.rsplit(".", 1)[0] + f"_h3res{args.res}.csv")
    out.to_csv(dst, index=False, encoding="utf-8-sig")
    print(f"[完成] {len(df)} 點 → {len(out)} 個 H3 網格(res{args.res}) → {dst}")
    print(f"[提示] 隱私:每格至少 {out['n'].min()} 筆;n 過小的格(如 <3)畫圖前建議遮罩")
    print(out.head(8).to_string(index=False))


def self_test() -> int:
    """無輸入時跑:合成台北/新北不動產點,驗證聚合正確與 TWD97 誤用防線。"""
    import random
    random.seed(20260808)
    rows = []
    for _ in range(500):
        la = 25.03 + random.uniform(-0.08, 0.08)
        lo = 121.55 + random.uniform(-0.10, 0.10)
        rows.append({"緯度": la, "經度": lo, "price": random.uniform(15, 90)})
    df = pd.DataFrame(rows)
    out = aggregate(df, "緯度", "經度", 8, "price", "median")
    print(f"[自我測試] 500 點 → {len(out)} 個 res8 網格;總筆數對帳 {out['n'].sum()}=500 → "
          f"{'✓' if out['n'].sum() == 500 else '✗'}")
    print(out.sort_values("n", ascending=False).head(5).to_string(index=False))

    # TWD97 誤用防線
    bad = pd.DataFrame({"緯度": [2748000.0], "經度": [302000.0], "price": [50]})  # 公尺投影座標
    try:
        aggregate(bad, "緯度", "經度", 8)
        print("[自我測試] TWD97 防線:✗ 未擋下")
        return 1
    except ValueError:
        print("[自我測試] TWD97 投影座標誤用防線:✓ 正確擋下")
    return 0


if __name__ == "__main__":
    sys.exit(main())
