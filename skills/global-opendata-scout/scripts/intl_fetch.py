#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
intl_fetch.py — 跨國官方統計資料撈取工具（World Bank + SDMX 家族）

【設計理路】
多數國際組織與各國統計機構採用 **SDMX** 這個統計交換標準,因此本工具走兩軌:
  軌一 `wb`    World Bank Indicators API——自成一格的 REST,最適合做跨國追蹤資料
  軌二 `sdmx`  通用 SDMX 客戶端——一支打通 Eurostat / ILOSTAT / IMF / UN 等

【端點驗證狀態(2026-07-26 實測)】
  ✅ 已實測可用:
     World Bank  https://api.worldbank.org/v2          免金鑰
     Eurostat    https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0
     ILOSTAT     https://sdmx.ilo.org/rest             (舊的 www.ilo.org/sdmx/rest 已失效)
     IMF         https://sdmxcentral.imf.org/ws/public/sdmxapi/rest
     UN Data     http://data.un.org/WS/rest            (注意是 http 非 https)
  ⚠️ 待確認,本工具不內建:
     OECD        sdmx.oecd.org 的 v2 路徑實測 404;stats.oecd.org 有回應但兩個不同
                 URL 回傳位元組完全相同的回應,疑似 catch-all。請查官方文件確認正確
                 路徑後再用 --base 自行指定,勿假設本檔記載的形式正確。
     FRED        需申請 API key,本工具未內建(見 SKILL.md 的金鑰紀律)

【金鑰紀律】任何 API key 一律走環境變數,絕不硬編碼、絕不寫進產出檔。

【用法】
    python intl_fetch.py wb   --indicator NY.GDP.MKTP.CD --countries TW,US,JP --start 2015 --end 2022 -o gdp.csv
    python intl_fetch.py wb   --search "gdp per capita"
    python intl_fetch.py sdmx --provider ilostat --resource dataflow -o flows.xml
    python intl_fetch.py sdmx --provider eurostat --dataset DEMO_R_D3DENS --params "geo=EU27_2020&time=2022" -o pop.json

last_verified: 2026-07-26
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import ssl
import sys

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.poolmanager import PoolManager
except ImportError:
    print("錯誤：需要 requests 套件。請執行：pip install requests", file=sys.stderr)
    sys.exit(1)


class _RelaxedStrictAdapter(HTTPAdapter):
    """解除 VERIFY_X509_STRICT，仍完整保留憑證鏈與主機名驗證。

    部分官方統計站的憑證鏈不符 Python 3.13+ 預設的 RFC 嚴格檢查。
    採憑證鏈驗證的 TLS 相容作法——**絕不使用 verify=False**。
    """

    def _ctx(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context()
        ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
        return ctx

    def init_poolmanager(self, connections, maxsize, block=False, **kw):
        kw["ssl_context"] = self._ctx()
        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, **kw
        )


def session() -> requests.Session:
    s = requests.Session()
    s.mount("https://", _RelaxedStrictAdapter())
    mail = os.environ.get("CONTACT_MAILTO", "").strip()
    s.headers.update(
        {"User-Agent": "global-opendata-scout/1.0 (academic research)"
                       + (f" mailto:{mail}" if mail else "")}
    )
    return s


# ── 軌一：World Bank ──────────────────────────────────────────────────
WB_BASE = "https://api.worldbank.org/v2"


def wb_fetch(indicator: str, countries: str, start: int, end: int, timeout: int = 40):
    """取回 World Bank 指標資料。countries 用分號或逗號分隔的 ISO 代碼，或 'all'。"""
    cc = countries.replace(",", ";")
    url = f"{WB_BASE}/country/{cc}/indicator/{indicator}"
    params = {"format": "json", "per_page": 20000, "date": f"{start}:{end}"}
    r = session().get(url, params=params, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"World Bank 回應 HTTP {r.status_code}")
    j = r.json()
    if not isinstance(j, list) or len(j) < 2:
        msg = j[0].get("message") if isinstance(j, list) and j else j
        raise RuntimeError(f"World Bank 未回傳資料：{msg}")
    return j[0], j[1] or []


def wb_search(q: str, timeout: int = 40):
    """在 World Bank 指標清單中搜尋（用關鍵字找 indicator 代碼）。"""
    r = session().get(
        f"{WB_BASE}/indicator",
        params={"format": "json", "per_page": 20000},
        timeout=timeout,
    )
    r.raise_for_status()
    j = r.json()
    if len(j) < 2:
        return []
    ql = q.lower()
    return [
        (d["id"], d["name"])
        for d in j[1]
        if ql in (d.get("name") or "").lower()
    ]


def cmd_wb(a) -> int:
    if a.search:
        hits = wb_search(a.search)
        print(f"找到 {len(hits)} 個指標（顯示前 40 個）：")
        for i, (code, name) in enumerate(hits[:40]):
            print(f"  {code:32s} {name[:75]}")
        if len(hits) > 40:
            print(f"  …另有 {len(hits)-40} 個，請用更精確的關鍵字")
        return 0

    if not a.indicator:
        print("錯誤：請給 --indicator，或用 --search 先找指標代碼", file=sys.stderr)
        return 1

    meta, rows = wb_fetch(a.indicator, a.countries, a.start, a.end)
    if not rows:
        print("查無資料：可能是該國家／年份組合無此指標的觀測值。", file=sys.stderr)
        return 1

    out = a.output or f"{a.indicator.replace('.', '_')}.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["country_id", "country", "indicator_id", "indicator", "year", "value", "unit"])
        for d in rows:
            w.writerow([
                (d.get("country") or {}).get("id", ""),
                (d.get("country") or {}).get("value", ""),
                (d.get("indicator") or {}).get("id", ""),
                (d.get("indicator") or {}).get("value", ""),
                d.get("date", ""),
                d.get("value", ""),
                d.get("unit", ""),
            ])
    nonnull = sum(1 for d in rows if d.get("value") is not None)
    print(f"成功：{len(rows)} 筆已存至 {out}（其中 {nonnull} 筆有值，{len(rows)-nonnull} 筆為空）")
    print(f"　總筆數(伺服器回報)：{meta.get('total')}　頁數：{meta.get('pages')}")
    if len(rows) - nonnull > len(rows) * 0.3:
        print("　⚠️ 空值比例偏高——該指標對部分國家/年份可能無涵蓋，做面板前先檢查涵蓋率。")
    return 0


# ── 軌二：通用 SDMX ───────────────────────────────────────────────────
SDMX_PROVIDERS = {
    "eurostat": {
        "base": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0",
        "note": "資料路徑為 /data/{datasetCode}；已實測可用，免金鑰。",
        "verified": "2026-07-26",
    },
    "ilostat": {
        "base": "https://sdmx.ilo.org/rest",
        "note": "國際勞工組織。舊 base www.ilo.org/sdmx/rest 已失效。已實測可用。",
        "verified": "2026-07-26",
    },
    "imf": {
        "base": "https://sdmxcentral.imf.org/ws/public/sdmxapi/rest",
        "note": "已實測可用。注意：dataservices.imf.org 已失效、data.imf.org 回 403。",
        "verified": "2026-07-26",
    },
    "undata": {
        "base": "http://data.un.org/WS/rest",
        "note": "聯合國。**是 http 非 https**（官方如此）。已實測可用。",
        "verified": "2026-07-26",
    },
}


def cmd_sdmx(a) -> int:
    if a.list_providers:
        print("內建 SDMX 提供者（皆為 2026-07-26 實測可用）：")
        for k, v in SDMX_PROVIDERS.items():
            print(f"\n  {k}")
            print(f"    base : {v['base']}")
            print(f"    說明 : {v['note']}")
        print("\n  OECD／FRED 未內建——OECD 端點待確認、FRED 需 API key，見 SKILL.md。")
        return 0

    base = a.base or (SDMX_PROVIDERS.get(a.provider) or {}).get("base")
    if not base:
        print(f"錯誤：未知的 provider「{a.provider}」。用 --list-providers 看可用清單，"
              f"或用 --base 自行指定。", file=sys.stderr)
        return 1

    if a.dataset:
        url = f"{base}/data/{a.dataset}"
    elif a.resource:
        url = f"{base}/{a.resource}"
    else:
        print("錯誤：請給 --dataset 或 --resource", file=sys.stderr)
        return 1

    params = {}
    if a.params:
        for kv in a.params.split("&"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                params[k] = v

    try:
        r = session().get(url, params=params, timeout=a.timeout)
    except Exception as e:  # noqa: BLE001
        print(f"錯誤：連線失敗（{type(e).__name__}: {e}）", file=sys.stderr)
        return 1

    if r.status_code != 200:
        print(f"錯誤：HTTP {r.status_code}\n  URL: {r.url}\n  回應: {r.text[:220]}",
              file=sys.stderr)
        print("\n提示：SDMX 各提供者的資源路徑與查詢語法不完全相同，"
              "失敗時請查該組織的官方 API 文件確認路徑形式。", file=sys.stderr)
        return 1

    ct = r.headers.get("content-type", "")
    ext = ".json" if "json" in ct.lower() else (".xml" if "xml" in ct.lower() else ".txt")
    out = a.output or f"sdmx_{a.provider or 'custom'}{ext}"
    with open(out, "wb") as f:
        f.write(r.content)
    print(f"成功：已存 {len(r.content):,} bytes 至 {out}")
    print(f"　URL        : {r.url}")
    print(f"　Content-Type: {ct}")
    if "xml" in ct.lower():
        print("　（SDMX 結構檔為 XML；要轉成表格請用 pandasdmx 之類的套件解析）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="跨國官方統計資料撈取（World Bank + SDMX 家族）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  # 找指標代碼
  python intl_fetch.py wb --search "gdp per capita"
  # 撈跨國追蹤資料
  python intl_fetch.py wb --indicator NY.GDP.MKTP.CD --countries TW,US,JP --start 2015 --end 2022 -o gdp.csv
  # SDMX
  python intl_fetch.py sdmx --list-providers
  python intl_fetch.py sdmx --provider ilostat --resource dataflow -o flows.xml

金鑰紀律：任何 API key 一律走環境變數，本工具不硬編碼、不寫進產出檔。
""",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("wb", help="World Bank Indicators API（免金鑰）")
    p.add_argument("--indicator", help="指標代碼，如 NY.GDP.MKTP.CD")
    p.add_argument("--countries", default="all", help="ISO 代碼，逗號分隔，如 TW,US,JP（預設 all）")
    p.add_argument("--start", type=int, default=2000)
    p.add_argument("--end", type=int, default=2023)
    p.add_argument("--search", help="用關鍵字搜尋指標代碼")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_wb)

    p = sub.add_parser("sdmx", help="通用 SDMX 客戶端")
    p.add_argument("--provider", help="eurostat / ilostat / imf / undata")
    p.add_argument("--base", help="自訂 base URL（provider 未內建時用）")
    p.add_argument("--dataset", help="資料集代碼（會組成 {base}/data/{dataset}）")
    p.add_argument("--resource", help="資源路徑，如 dataflow")
    p.add_argument("--params", help='查詢參數，如 "geo=EU27_2020&time=2022"')
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--list-providers", action="store_true")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_sdmx)

    a = ap.parse_args()
    try:
        return a.func(a)
    except RuntimeError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
