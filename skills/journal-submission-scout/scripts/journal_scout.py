#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
journal_scout.py — 投稿期刊候選搜尋與比對（免金鑰）

從公開資料源查期刊的客觀指標，供投稿前建立候選名單。

【資料源，全部免金鑰、2026-08-20 實測可用】
  OpenAlex  https://api.openalex.org/sources   — h-index、被引、APC、DOAJ 收錄狀態
  DOAJ      https://doaj.org/api/search/journals — 開放取用期刊的 APC 與**審查制度**
  Crossref  https://api.crossref.org/journals   — 期刊基本資料、ISSN 對接

【🚫 本工具絕對不做的事（很重要）】
  1. **不提供 Journal Impact Factor**。JIF 是 Clarivate 專有指標，
     公開 API 取不到。OpenAlex 的 `2yr_mean_citedness`（兩年平均被引）
     是**概念相近但演算法不同**的開放指標，**兩者不可互相代替、不可混稱**。
     本工具一律標示為「2年平均被引(OpenAlex)」，絕不寫成 IF 或影響係數。
  2. **不提供接受率**。多數期刊不公開，任何宣稱的數字都不可信。
  3. **不判定 ABS/FT50/SCImago 分級**。那些是專有清單，需自行查詢或憑機構訂閱。
  4. **不判定某期刊是否為掠奪性期刊**。工具只給訊號（是否在 DOAJ、
     審查制度是否揭露、APC 是否透明），**判定必須由你依 Think.Check.Submit
     逐項人工核對**——見 ../references/predatory-screening.md。

【用法】
    python journal_scout.py search "family firm governance" --top 10
    python journal_scout.py lookup 0143-2095
    python journal_scout.py compare 0143-2095,0149-2063,1467-8551
    python journal_scout.py search "ESG disclosure" --top 8 --csv out.csv

last_verified: 2026-08-20
"""

from __future__ import annotations

import argparse
import csv
import ssl
import sys
import time

OPENALEX = "https://api.openalex.org/sources"
DOAJ = "https://doaj.org/api/search/journals"
CROSSREF = "https://api.crossref.org/journals"


def _session():
    try:
        import requests
        from requests.adapters import HTTPAdapter
        from urllib3.poolmanager import PoolManager
    except ImportError:
        raise SystemExit("錯誤：需要 requests 套件。請執行：pip install requests")

    class _Adapter(HTTPAdapter):
        # 部分學術站台憑證在 Python 3.13+ 的嚴格模式下會失敗；
        # 只解除 RFC 嚴格旗標，仍完整保留憑證鏈與主機名驗證（絕不 verify=False）
        def init_poolmanager(self, c, m, block=False, **kw):
            ctx = ssl.create_default_context()
            ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
            kw["ssl_context"] = ctx
            self.poolmanager = PoolManager(num_pools=c, maxsize=m, block=block, **kw)

    import os

    s = requests.Session()
    s.mount("https://", _Adapter())
    mail = os.environ.get("CROSSREF_MAILTO", "").strip()
    s.headers.update({
        "User-Agent": "journal-submission-scout/1.0 (academic use)"
                      + (f" mailto:{mail}" if mail else "")
    })
    return s


def _get(s, url, params=None, retries=2, timeout=45):
    """帶重試與非 JSON 防護的 GET。失敗回 None（不當成空結果）。"""
    for i in range(retries + 1):
        try:
            r = s.get(url, params=params, timeout=timeout)
            if r.status_code == 200:
                try:
                    return r.json()
                except ValueError:
                    if i < retries:
                        time.sleep(3)
                        continue
                    return None
            if r.status_code in (429, 503):
                time.sleep(5)
                continue
            return None
        except Exception:  # noqa: BLE001
            if i < retries:
                time.sleep(3)
                continue
            return None
    return None


def _fmt(v, dash="—"):
    return dash if v in (None, "", []) else v


# 非期刊來源：預印本平台、機構典藏、資料庫。天真搜尋會把這些排在最前面,
# 但它們不是投稿標的——不濾掉會給出有害建議。
NON_JOURNAL_HINT = (
    "ssrn", "research square", "preprints", "zenodo", "arxiv", "biorxiv",
    "repositor", "referencia", "figshare", "osf", "hal", "dspace",
    "institutional", "working paper", "conference", "proceedings",
)
# Mega-journal:收稿量極大、跨領域,對頂刊投稿者通常不是目標,但仍標出供判斷
MEGA_HINT = ("sustainability", "plos one", "scientific reports",
             "heliyon", "cureus", "ieee access", "frontiers in")


def openalex_search(s, query: str, top: int, since: str | None = None) -> list:
    """先搜該主題的論文,再統計它們發表在哪些期刊——這才是「誰會登我這種研究」。

    ⚠️ 設計要點(實測發現):直接用 sources?search= 是搜**期刊名稱**,
       主題查詢一律查無。必須改成 works + group_by。
    ⚠️ 但主題聚合的原始結果會被預印本平台與 mega-journal 洗版
       (實測某主題前 10 名有 SSRN／Research Square／Preprints.org／Sustainability),
       故必須過濾與標記,否則會給出有害建議。
    """
    flt = ["type:article"]
    if since:
        flt.append(f"from_publication_date:{since}-01-01")
    g = _get(s, "https://api.openalex.org/works", {
        "search": query, "filter": ",".join(flt),
        "group_by": "primary_location.source.id", "per-page": 200})
    if not g:
        return []

    cand = []
    for x in g.get("group_by", []):
        name = x.get("key_display_name") or ""
        low = name.lower()
        if not name or name == "unknown":
            continue
        if any(h in low for h in NON_JOURNAL_HINT):
            continue                      # 濾掉預印本／典藏
        cand.append((name, x.get("key"), x.get("count", 0)))
        if len(cand) >= top * 3:          # 多取一些,補完 metadata 後再截斷
            break

    out = []
    for name, src_id, cnt in cand:
        # ⚠️ group_by 的 key 是**實體 URI**（https://openalex.org/S10134376），
        #    不是 API 端點。直接 GET 會打到網站首頁拿回 HTML、解析失敗而被靜默濾掉
        #    （實測踩過：搜尋結果一律變成 0 筆）。必須抽出 ID 再組 API URL。
        sid = str(src_id or "").rstrip("/").split("/")[-1]
        j = _get(s, f"{OPENALEX}/{sid}") if sid.startswith("S") else None
        if not j or j.get("type") != "journal":
            continue                      # 再用 OpenAlex 的 type 欄位確認是期刊
        ss = j.get("summary_stats", {}) or {}
        out.append({
            "name": j.get("display_name") or name,
            "topic_works": cnt,
            "issn_l": j.get("issn_l"),
            "publisher": j.get("host_organization_name"),
            "works": j.get("works_count"),
            "cited": j.get("cited_by_count"),
            "h_index": ss.get("h_index"),
            "mean_cited_2y": round(ss.get("2yr_mean_citedness"), 2)
                             if ss.get("2yr_mean_citedness") is not None else None,
            "is_oa": j.get("is_oa"),
            "in_doaj": j.get("is_in_doaj"),
            "apc_usd": j.get("apc_usd"),
            "homepage": j.get("homepage_url"),
            "mega": any(h in (j.get("display_name") or "").lower() for h in MEGA_HINT),
        })
        time.sleep(0.25)
        if len(out) >= top:
            break
    return out


def doaj_review_process(s, issn: str) -> tuple:
    """回傳 (審查制度, APC說明)。DOAJ 只收開放取用期刊，非 OA 期刊查無屬正常。"""
    j = _get(s, f"{DOAJ}/issn:{issn}", {"pageSize": 1})
    if not j or not j.get("results"):
        return None, None
    b = j["results"][0].get("bibjson", {})
    rev = (b.get("editorial") or {}).get("review_process")
    apc = b.get("apc") or {}
    apc_txt = "無 APC" if apc.get("has_apc") is False else (
        "有 APC" if apc.get("has_apc") else None)
    return (", ".join(rev) if isinstance(rev, list) else rev), apc_txt


def enrich(s, rows: list) -> list:
    for r in rows:
        if r.get("issn_l"):
            rev, apc = doaj_review_process(s, r["issn_l"])
            r["review_process"] = rev
            r["doaj_apc"] = apc
            time.sleep(0.5)   # 對 DOAJ 保持禮貌間隔
    return rows


def risk_flag(r: dict) -> str:
    """掠奪性期刊的**風險訊號**（不是判定）。

    🚫 本函式**不判定**任何期刊是不是掠奪性期刊——那必須由人依
       Think.Check.Submit 逐項核對，見 ../references/predatory-screening.md。
       這裡只把幾個客觀可查的訊號濃縮成提示，讓你知道**哪幾本要優先細查**。

    訊號（任一成立計一分）：
      · 收 APC 但不在 DOAJ —— 收費卻未通過 DOAJ 審查門檻，值得追問
      · h-index < 20 但收稿量 > 3000 —— 量大而影響力低的典型樣態
      · APC > 3000 USD 且 h-index < 50 —— 收費與品質不相稱

    ⚠️ **訊號 ≠ 證據。** 老牌訂閱制頂刊本來就不在 DOAJ（如 SMJ），
       會被計一分，這完全正常。分數只用來排你的查證順序，不能拿來下結論。
    """
    n = 0
    h = r.get("h_index") or 0
    apc = r.get("apc_usd") or 0
    works = r.get("works") or 0
    if apc and not r.get("in_doaj"):
        n += 1
    if h < 20 and works > 3000:
        n += 1
    if apc > 3000 and h < 50:
        n += 1
    return ("·", "!", "!!", "!!!")[min(n, 3)]


def print_table(rows: list) -> None:
    if not rows:
        print("查無結果。試著換關鍵字，或確認網路連線。")
        return
    print(f"\n{'期刊':40s} {'本主題':>5s} {'h-idx':>6s} {'2年均引':>7s} {'APC':>7s} {'風險':>5s}")
    print("─" * 76)
    for r in rows:
        tag = " [MEGA]" if r.get("mega") else ""
        print(f"{(str(_fmt(r['name']))[:34] + tag):40s} "
              f"{str(_fmt(r.get('topic_works'))):>5s} "
              f"{str(_fmt(r['h_index'])):>6s} "
              f"{str(_fmt(r['mean_cited_2y'])):>7s} "
              f"{str(_fmt(r['apc_usd'])):>7s} "
              f"{risk_flag(r):>5s}")
    print("""
⚠️ 指標說明（請勿誤用）
   h-index／2年均引 皆來自 **OpenAlex 開放資料**。
   「2年均引」**不是** Journal Impact Factor——JIF 是 Clarivate 專有指標、
   演算法與收錄範圍都不同，兩者不可互換，也不可在論文中互稱。
   本工具**不提供** JIF、接受率、ABS／FT50／SCImago 分級（皆需另行查詢）。

⚠️ 「風險」欄是**查證優先序，不是判定**：· 無訊號／! 一項／!! 兩項／!!! 三項。
   老牌訂閱制頂刊本來就不在 DOAJ（如 SMJ），會被計一分，這完全正常。
   **要不要投，最終必須依 ../references/predatory-screening.md 逐項人工核對。**
⚠️ 已自動濾除：預印本平台與機構典藏（SSRN／Research Square／Preprints.org／
   Zenodo／典藏庫等）——它們常在主題聚合中排前面，但不是投稿標的。
⚠️ 標 MEGA 者為收稿量極大的跨領域期刊（如 Sustainability、PLoS ONE）。
   不是說不好，但**對要投 ABS 3*/4* 的人通常不是目標**，請自行判斷。""")


def cmd_search(a) -> int:
    s = _session()
    rows = openalex_search(s, a.query, a.top, a.since)
    if not rows:
        print("查無結果或查詢失敗（注意：查詢失敗 ≠ 沒有符合的期刊）", file=sys.stderr)
        return 1
    rows = enrich(s, rows)
    print_table(rows)

    print("\n【審查制度（DOAJ，僅開放取用期刊有資料）】")
    any_rev = False
    for r in rows:
        if r.get("review_process"):
            any_rev = True
            print(f"  {str(r['name'])[:40]:42s} {r['review_process']}")
    if not any_rev:
        print("  （本批皆非 DOAJ 收錄，多為訂閱制期刊——這不代表有問題）")

    if a.csv:
        cols = ["name", "issn_l", "publisher", "h_index", "mean_cited_2y", "works",
                "cited", "apc_usd", "is_oa", "in_doaj", "review_process", "homepage"]
        with open(a.csv, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\n已存出 {a.csv}")

    print("\n📌 下一步（工具做不到、必須你自己做的）：")
    print("   1. 查 ABS／FT50／SCImago 分級——決定投稿層級")
    print("   2. 讀該刊近兩年目次，確認你的題目真的在它的守備範圍")
    print("   3. 依 ../references/predatory-screening.md 逐項篩掠奪性期刊")
    return 0


def cmd_lookup(a) -> int:
    s = _session()
    j = _get(s, f"{OPENALEX}/issn:{a.issn}")
    if not j:
        print(f"查詢失敗或查無 ISSN {a.issn}", file=sys.stderr)
        return 1
    ss = j.get("summary_stats", {}) or {}
    print(f"\n期刊　　　：{j.get('display_name')}")
    print(f"ISSN　　　：{', '.join(j.get('issn') or [])}")
    print(f"出版商　　：{_fmt(j.get('host_organization_name'))}")
    print(f"h-index　 ：{_fmt(ss.get('h_index'))}")
    print(f"2年均引　 ：{_fmt(round(ss.get('2yr_mean_citedness'),2) if ss.get('2yr_mean_citedness') else None)}"
          f"　（非 JIF，見說明）")
    print(f"總篇數　　：{_fmt(j.get('works_count'))}　總被引：{_fmt(j.get('cited_by_count'))}")
    print(f"開放取用　：{'是' if j.get('is_oa') else '否'}　DOAJ 收錄：{'是' if j.get('is_in_doaj') else '否'}")
    print(f"APC(USD)　：{_fmt(j.get('apc_usd'))}")
    print(f"官網　　　：{_fmt(j.get('homepage_url'))}")
    rev, apc = doaj_review_process(s, a.issn)
    if rev:
        print(f"審查制度　：{rev}　(DOAJ)")
    return 0


def cmd_compare(a) -> int:
    s = _session()
    rows = []
    for issn in [x.strip() for x in a.issns.split(",") if x.strip()]:
        j = _get(s, f"{OPENALEX}/issn:{issn}")
        if not j:
            print(f"  ⚠️ {issn} 查詢失敗，略過（不代表該刊不存在）", file=sys.stderr)
            continue
        ss = j.get("summary_stats", {}) or {}
        rows.append({
            "name": j.get("display_name"), "issn_l": j.get("issn_l"),
            "h_index": ss.get("h_index"),
            "mean_cited_2y": round(ss.get("2yr_mean_citedness"), 2)
                             if ss.get("2yr_mean_citedness") else None,
            "works": j.get("works_count"), "apc_usd": j.get("apc_usd"),
            "in_doaj": j.get("is_in_doaj"),
        })
        time.sleep(0.4)
    print_table(rows)
    return 0 if rows else 1


def main() -> int:
    ap = argparse.ArgumentParser(
        description="投稿期刊候選搜尋與比對（免金鑰；資料源 OpenAlex／DOAJ／Crossref）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  python journal_scout.py search "family firm governance" --top 10
  python journal_scout.py lookup 0143-2095
  python journal_scout.py compare 0143-2095,0149-2063

🚫 本工具不提供 JIF、接受率、ABS／FT50／SCImago 分級——那些需另行查詢，
   工具不會憑印象生成任何一個。「2年均引」是 OpenAlex 開放指標，非 JIF。
""")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("search", help="依主題搜尋候選期刊")
    p.add_argument("query")
    p.add_argument("--top", type=int, default=10)
    p.add_argument("--since", help="只看該年之後的論文（如 2021），反映當前趨勢")
    p.add_argument("--csv", help="另存 CSV")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("lookup", help="查單一期刊（用 ISSN）")
    p.add_argument("issn")
    p.set_defaults(func=cmd_lookup)

    p = sub.add_parser("compare", help="比較多本期刊（ISSN 逗號分隔）")
    p.add_argument("issns")
    p.set_defaults(func=cmd_compare)

    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
