#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
archive_url.py — 引用網頁的存檔／驗證工具（Wayback Machine，純標準庫）

【動機】
頂刊審稿人與資料編輯會點開論文引用的網頁連結；MOPS 重訊、公司 IR 頁、政府統計頁
數年後常已改版或下架（404）。本工具讓「引用網頁」在投稿當下就留一份可驗證的存檔
快照，並把每次查核寫進 CSV 供方法節與複製包引用（呼應
`references/disclosure-monitoring.md` 的「引用永久性」設計）。

【依賴】
只用標準庫：urllib、json、csv、hashlib、argparse、ssl、time、datetime、pathlib。
不裝 requests、不裝任何第三方套件。

【網路範圍（硬規則）】
本腳本的 HTTP 用戶端只連線到 archive.org / web.archive.org 這兩個網域
（已列於家族 scripts/egress_allowlist.txt）。子指令的 <url> 參數是「被存檔／被查詢
的目標網址」，一律只以查詢參數的形式交給 archive.org 的端點，本腳本不會直接對
該目標網址發連線——連到目標網站是 archive.org 伺服器端的事,不是本腳本的事。
因此 `hash` 子指令雜湊的是「已被 Wayback 收錄的快照內容」而非即時抓即時頁面；
即時頁面的雜湊比對（變更監測）屬於各站台專用抓取腳本的工作（如
台灣官方統計的撈取腳本 或使用者私有的 MOPS 工具，那些腳本有自己核准的
outbound 網域），本工具與其分工、以「存檔」與「回溯驗證」銜接。

【端點驗測狀態】
下列狀態由本專案主對話於 2026-09-20 實測（詳見
`references/disclosure-monitoring.md` 的「Wayback 端點實測」一節，此處只留摘要,
數字與現象若有出入以該檔為準）：

  - CDX 查詢 `https://web.archive.org/cdx/search/cdx`：✅ 可用（HTTP 200,
    回傳快照清單 JSON）。**補充**：本檔實作與測試過程中（同日、稍晚時段）另外
    觀察到間歇性 503「Internet Archive: Temporarily Offline」——服務本身會短暫
    整站離線，重試數次後仍可拿到 200。故本腳本內建重試＋退避,不假設單次請求
    一定成功,也不把單次 503 誤判為「CDX 端點失效」。

  【H4 修復：「最新快照」查詢方式實測（2026-09-20，本次審查修復時）】
  舊版用 `limit=2000`（預設升冪、無 sort 參數）取前 2000 筆再 `max(rows, key=ts)`，
  對快照數 <2000 的網址沒事,但只要總筆數更多,拿到的就是「最舊 2000 筆裡最新的」
  ——已實測命中：`archive_log.csv` 曾把 tpex.org.tw 的「最新快照」記成 2020-06-01。
  逐一實測兩種候選修法（`curl`,目標 `https://www.tpex.org.tw/`,同日多次因間歇性
  503 重試後取得 200）：
    1. `curl "https://web.archive.org/cdx/search/cdx?url=https://www.tpex.org.tw/&output=json&limit=-3"`
       → 回傳「末尾 3 筆」,但筆內仍是**升冪**排列（最新一筆在陣列最後）：
       2026-07-23 09:12:09、2026-08-28 14:26:26、2026-09-12 14:20:34（時間戳格式
       化寫法避免與本檔 sanitize_check.sh 的台灣手機號樣式誤判——連續 14 位數字
       字串可能巧合命中 09 開頭的 10 位數樣式）。負數 limit 確實會從尾端取,
       但排序語意未在回應中明講,仍需事後找 max。
    2. `curl "https://web.archive.org/cdx/search/cdx?url=https://www.tpex.org.tw/&output=json&sort=reverse&limit=3"`
       → 回傳**降冪**排列，第一筆就是最新：2026-09-12 14:20:34、2026-08-28 14:26:26、
       2026-07-23 09:12:09。
    兩者都能正確定位到同一筆最新快照（2026-09-12 14:20:34,即本次修復當下的真實最新值）,
    但 `sort=reverse` 讓「陣列第一筆＝最新」這件事**由伺服器保證、不必再猜排序**，
    且與既有 `--limit` 參數語意（要幾筆）不衝突（負數 limit 是否所有 CDX 部署都支援
    未經正式文件保證）。因此本檔採用 `sort=reverse`，`cdx_latest_snapshot()` 直接取
    第一筆為最新，不再對整批做 `max()`。
  - `https://archive.org/wayback/available`：429 Too Many Requests（帶 UA 重試仍
    429，本工具**不使用**此端點）。
  - 匿名 Save Page Now `https://web.archive.org/save/<url>`：429／500。
  - SPN2 認證端點（帶使用者自備 S3 金鑰）：**待確認，本次未實測**。本工具在偵測
    到環境變數存在時會嘗試呼叫，但明確標示「未經驗證、盡力嘗試」，失敗即老實
    印出錯誤，不假裝成功。

【金鑰紀律】
SPN2 認證只讀環境變數 `IA_ACCESS_KEY` / `IA_SECRET_KEY`（於
https://archive.org/account/s3.php 取得），絕不寫死在程式碼、絕不印出或寫入
CSV 記錄檔。未設定時一律走匿名請求。

【子指令】
    python archive_url.py lookup <url> [--limit N] [--retries N] [--timeout S]
    python archive_url.py save   <url> [--dry-run] [--retries N] [--timeout S]
    python archive_url.py hash   <url> [--timestamp TS] [--retries N]
    python archive_url.py log    [--tail N] [--csv-path PATH]

CSV 記錄檔欄位（固定五欄）：url, checked_at, snapshot_url, method, status
預設路徑：`./output/archive_log.csv`（自動建目錄；可用 --csv-path 或環境變數
ARCHIVE_LOG_CSV 覆寫，M4 修復：不再直接寫 cwd）。

User-Agent 一律帶專案名與聯絡方式（若設定 CONTACT_MAILTO 環境變數）。

last_verified: 2026-09-20
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Windows 主控台預設 cp950，中文/符號輸出遇到編碼不到的字元會整支崩掉。
# 查核結果比主控台美觀重要，這裡讓輸出失敗時降級顯示而不是讓程式中止（同 L-029）。
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

PROJECT_UA_BASE = "academic-claude-skills/public-disclosure-scout archive_url.py (academic research)"
ALLOWED_HOSTS = {"archive.org", "web.archive.org"}
CDX_ENDPOINT = "https://web.archive.org/cdx/search/cdx"
SAVE_ENDPOINT_ANON = "https://web.archive.org/save/"
SAVE_ENDPOINT_SPN2 = "https://web.archive.org/save"
CSV_FIELDS = ["url", "checked_at", "snapshot_url", "method", "status"]

SAVE_RATE_LIMIT_ADVICE = """\
⚠️ 存檔請求被限流或伺服器忙碌（HTTP {code}）。三條替代路徑：
  1. 稍後（數分鐘至數小時）重試，Internet Archive 的匿名存檔限流會隨時間解除。
  2. 瀏覽器手動存檔：開啟 https://web.archive.org/save/{url} 並人工完成（不受本工具的
     程式化限流影響，且可肉眼確認存檔內容正確）。
  3. 使用者自備 archive.org 帳號的 S3 金鑰，走 SPN2 認證端點：
     於 https://archive.org/account/s3.php 取得 access/secret key，
     設定環境變數 IA_ACCESS_KEY / IA_SECRET_KEY 後重跑本指令。
     ⚠️ 本工具的 SPN2 呼叫路徑「待確認」（本專案尚未實測過認證端點是否真能繞過限流），
     此路徑僅供嘗試，不保證成功。
"""


def _user_agent() -> str:
    mail = os.environ.get("CONTACT_MAILTO", "").strip()
    return PROJECT_UA_BASE + (f" mailto:{mail}" if mail else "")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _assert_allowed_host(url: str) -> None:
    """硬性檢查：本腳本即將連線的 host 必須在 archive.org / web.archive.org 之內。"""
    host = urllib.parse.urlparse(url).netloc.split(":")[0].lower()
    if host not in ALLOWED_HOSTS:
        raise RuntimeError(
            f"拒絕連線：{host} 不在本腳本允許的網域範圍（{sorted(ALLOWED_HOSTS)}）。"
            "本工具只查詢/存檔 Wayback Machine，不直接抓取任意站台。"
        )


class _HostCheckRedirectHandler(urllib.request.HTTPRedirectHandler):
    """跟隨重導向前，對新位址重新套用 _assert_allowed_host（M11 修復）。

    urllib 的預設 HTTPRedirectHandler 會照單全收任何 3xx 的 Location，
    即使新網域不在允許清單內也會照連——本腳本的賣點就是「只連
    archive.org / web.archive.org」，這裡把它做實：若 web.archive.org
    出現開放重導向（或連線被 DNS 劫持），在建立重導向請求前就擋下，
    不讓 User-Agent／Authorization 等 headers 有機會被帶去未知網域。
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        _assert_allowed_host(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_HostCheckRedirectHandler())


def _http_get(url: str, timeout: int, retries: int, backoff: float = 3.0):
    """對 archive.org 系網域發 GET，對 503／逾時做重試退避；其餘錯誤原樣拋出。"""
    _assert_allowed_host(url)
    req = urllib.request.Request(url, headers={"User-Agent": _user_agent()})
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            with _OPENER.open(req, timeout=timeout) as r:
                return r.status, r.read(), dict(r.headers)
        except urllib.error.HTTPError as e:
            body = e.read()
            if e.code == 503 and attempt < retries:
                print(f"  [重試 {attempt}/{retries}] HTTP 503（Internet Archive 可能暫時離線），"
                      f"{backoff:.0f} 秒後重試…", file=sys.stderr)
                last_err = e
                time.sleep(backoff)
                backoff *= 1.5
                continue
            return e.code, body, dict(e.headers or {})
        except (TimeoutError, urllib.error.URLError) as e:
            last_err = e
            if attempt < retries:
                print(f"  [重試 {attempt}/{retries}] 連線逾時/失敗（{e}），"
                      f"{backoff:.0f} 秒後重試…", file=sys.stderr)
                time.sleep(backoff)
                backoff *= 1.5
                continue
            raise
    if last_err:
        raise last_err
    raise RuntimeError("未知錯誤：重試邏輯未正常結束")


def append_log(csv_path: Path, url: str, snapshot_url: str, method: str, status: str) -> None:
    """把一次 lookup/save/hash 的結果追加到 CSV；檔案不存在就先寫表頭。"""
    is_new = not csv_path.exists()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(CSV_FIELDS)
        w.writerow([url, _now_iso(), snapshot_url, method, status])


def _csv_path(args) -> Path:
    """決定記錄檔路徑:使用者指定就用使用者的;否則預設寫到 ./output/(建目錄、印路徑),
    不直接寫 cwd(M4 修復——cwd 常是 repo 根目錄,`~/.claude/skills` 是指回 repo 的
    junction,散落的 CSV 會被誤帶進 repo)。
    """
    p = getattr(args, "csv_path", None) or os.environ.get("ARCHIVE_LOG_CSV")
    if p:
        return Path(p)
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)
    default_path = out_dir / "archive_log.csv"
    print(f"[提醒] 未指定 --csv-path,記錄檔預設寫到 {default_path}", file=sys.stderr)
    return default_path


# ── lookup ──────────────────────────────────────────────────────────────

def cdx_latest_snapshot(url: str, limit: int, timeout: int, retries: int):
    """查 CDX、回傳 (timestamp, original, 找到的筆數, truncated) 的最新一筆；查無回 (None, None, 0, False)。

    H4 修復：改用 `sort=reverse`，讓伺服器直接以時間降冪回傳，陣列第一筆保證是
    「本次查詢範圍內最新」，不再對 `limit` 筆內的資料做 `max()`（那只在總筆數
    ≤ limit 時才等於真正的最新一筆；超過時會取到「最舊 limit 筆裡最新的」——
    這正是 archive_log.csv 曾把 tpex.org.tw 記成 2020 年快照的成因，見檔頭
    「H4 修復」一節的 curl 實測）。
    `truncated`：回傳筆數已達 limit，代表本次查詢範圍內可能還有更早的快照未列出
    （但最新一筆本身不受影響，因為是降冪排列的第一筆）；呼叫端據此決定 status。
    """
    q = urllib.parse.urlencode({"url": url, "limit": limit, "output": "json", "sort": "reverse"})
    status, body, _ = _http_get(f"{CDX_ENDPOINT}?{q}", timeout=timeout, retries=retries)
    if status != 200:
        raise RuntimeError(f"CDX 回應 HTTP {status}：{body[:200]!r}")
    data = json.loads(body.decode("utf-8") or "[]")
    rows = data[1:] if len(data) > 1 else []
    if not rows:
        return None, None, 0, False
    latest = rows[0]  # sort=reverse：伺服器已降冪排序，第一筆即最新
    truncated = len(rows) >= limit
    return latest[1], latest[2], len(rows), truncated


def cmd_lookup(args) -> int:
    url = args.url
    print(f"查詢 CDX：{url}（limit={args.limit}，sort=reverse）…")
    try:
        ts, original, n, truncated = cdx_latest_snapshot(url, args.limit, args.timeout, args.retries)
    except Exception as e:  # noqa: BLE001 — 對外一律誠實回報，不吞例外
        print(f"錯誤：{e}", file=sys.stderr)
        append_log(_csv_path(args), url, "", "lookup", f"error:{e}")
        return 1

    if ts is None:
        print("查無快照（Wayback 尚未收錄此網址，或本次 limit 範圍內查不到）。")
        append_log(_csv_path(args), url, "", "lookup", "not_found")
        return 1

    snapshot_url = f"https://web.archive.org/web/{ts}/{original}"
    print(f"找到 {n} 筆快照（本次查詢範圍內，降冪排列），最新一筆：")
    print(f"  快照時間：{ts}")
    print(f"  快照網址：{snapshot_url}")
    if truncated:
        print(f"  提醒：回傳筆數已達 --limit（{args.limit}），本次查詢範圍內可能還有"
              "更早的快照未列出（最新一筆本身不受影響）；如需完整歷史請調高 --limit。")
        append_log(_csv_path(args), url, snapshot_url, "lookup", "truncated")
        return 2
    append_log(_csv_path(args), url, snapshot_url, "lookup", "ok")
    return 0


# ── save ────────────────────────────────────────────────────────────────

def cmd_save(args) -> int:
    url = args.url
    csv_path = _csv_path(args)

    if args.dry_run:
        access = os.environ.get("IA_ACCESS_KEY", "")
        secret_set = bool(os.environ.get("IA_SECRET_KEY", ""))
        print("【--dry-run，不會送出任何網路請求】")
        if access and secret_set:
            print(f"  將嘗試（未經驗證、盡力嘗試）：POST {SAVE_ENDPOINT_SPN2}")
            print(f"    headers: Authorization: LOW ***:***（金鑰已完全遮蔽，M11 修復——"
                  f"舊版印出前 4 碼，即使部分遮蔽仍是不必要的洩漏）")
            print(f"    body   : url={url}")
        else:
            print(f"  將嘗試：GET {SAVE_ENDPOINT_ANON}{url}")
            print("    （未偵測到 IA_ACCESS_KEY / IA_SECRET_KEY，走匿名請求）")
        print(f"  User-Agent: {_user_agent()}")
        append_log(csv_path, url, "", "save", "dry-run")
        return 0

    access = os.environ.get("IA_ACCESS_KEY", "")
    secret = os.environ.get("IA_SECRET_KEY", "")
    status_code = None
    body = b""
    used = ""

    if access and secret:
        print("偵測到 IA_ACCESS_KEY / IA_SECRET_KEY，嘗試 SPN2 認證端點"
              "（⚠️ 本專案未實測過此路徑，僅盡力嘗試）…")
        try:
            data = urllib.parse.urlencode({"url": url}).encode("ascii")
            req = urllib.request.Request(
                SAVE_ENDPOINT_SPN2, data=data, method="POST",
                headers={"User-Agent": _user_agent()},
            )
            # M11 修復：Authorization 用 add_unredirected_header，不放進一般
            # headers——urllib 建立重導向請求時只會複製一般 headers，
            # unredirected_hdrs 不會被帶到新位址，金鑰因此不會跟著重導向出站。
            # 加上 _OPENER 的網域檢查是第二道防線（雙重保障）。
            req.add_unredirected_header("Authorization", f"LOW {access}:{secret}")
            _assert_allowed_host(SAVE_ENDPOINT_SPN2)
            with _OPENER.open(req, timeout=args.timeout) as r:
                status_code, body = r.status, r.read()
            used = "spn2"
        except urllib.error.HTTPError as e:
            status_code, body = e.code, e.read()
            used = "spn2"
        except Exception as e:  # noqa: BLE001
            print(f"  SPN2 嘗試失敗（{type(e).__name__}: {e}），改走匿名請求。", file=sys.stderr)

    if status_code is None:
        print(f"送出匿名 Save Page Now：GET {SAVE_ENDPOINT_ANON}{url}")
        try:
            status_code, body, _ = _http_get(
                f"{SAVE_ENDPOINT_ANON}{url}", timeout=args.timeout, retries=1
            )
            used = "anonymous"
        except Exception as e:  # noqa: BLE001
            print(f"錯誤：連線失敗（{type(e).__name__}: {e}）", file=sys.stderr)
            append_log(csv_path, url, "", "save", f"error:{e}")
            return 1

    if status_code and 200 <= status_code < 300:
        print(f"成功（HTTP {status_code}，方式={used}）。")
        append_log(csv_path, url, "", "save", f"ok:{status_code}:{used}")
        return 0

    if status_code in (429, 500, 502, 503):
        print(SAVE_RATE_LIMIT_ADVICE.format(code=status_code, url=url))
        append_log(csv_path, url, "", "save", f"rate_limited:{status_code}:{used}")
        return 1

    print(f"未預期的回應：HTTP {status_code}（方式={used}）\n{body[:300]!r}", file=sys.stderr)
    append_log(csv_path, url, "", "save", f"unexpected:{status_code}:{used}")
    return 1


# ── hash ────────────────────────────────────────────────────────────────

def cmd_hash(args) -> int:
    url = args.url
    csv_path = _csv_path(args)
    ts = args.timestamp

    if not ts:
        print(f"未指定 --timestamp，先查 CDX 取最新快照時間…")
        try:
            ts, original, _n, _truncated = cdx_latest_snapshot(url, args.limit, args.timeout, args.retries)
        except Exception as e:  # noqa: BLE001
            print(f"錯誤：{e}", file=sys.stderr)
            append_log(csv_path, url, "", "hash", f"error:{e}")
            return 1
        if ts is None:
            print("查無快照，無法雜湊（請先用 save 建立快照）。")
            append_log(csv_path, url, "", "hash", "not_found")
            return 1
    else:
        original = url

    # id_ 後綴＝取原始未改寫內容（不含 Wayback 工具列與連結改寫），適合做內容雜湊比對。
    raw_snapshot_url = f"https://web.archive.org/web/{ts}id_/{original}"
    print(f"抓取快照原始內容：{raw_snapshot_url}")
    try:
        status, body, _ = _http_get(raw_snapshot_url, timeout=args.timeout, retries=args.retries)
    except Exception as e:  # noqa: BLE001
        print(f"錯誤：{e}", file=sys.stderr)
        append_log(csv_path, url, raw_snapshot_url, "hash", f"error:{e}")
        return 1

    if status != 200:
        print(f"錯誤：HTTP {status}", file=sys.stderr)
        append_log(csv_path, url, raw_snapshot_url, "hash", f"http_{status}")
        return 1

    digest = hashlib.sha256(body).hexdigest()
    print(f"快照時間：{ts}")
    print(f"內容長度：{len(body):,} bytes")
    print(f"SHA-256 ：{digest}")
    append_log(csv_path, url, raw_snapshot_url, "hash", f"sha256:{digest}")
    return 0


# ── log ─────────────────────────────────────────────────────────────────

def cmd_log(args) -> int:
    csv_path = _csv_path(args)
    if not csv_path.exists():
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            csv.writer(f).writerow(CSV_FIELDS)
        print(f"尚無記錄，已建立空白記錄檔：{csv_path}")
        return 0

    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header, data = (rows[0], rows[1:]) if rows else ([], [])
    tail = data[-args.tail:] if args.tail > 0 else data
    print(f"記錄檔：{csv_path}（共 {len(data)} 筆，顯示最後 {len(tail)} 筆）")
    print("  " + " | ".join(header))
    for row in tail:
        print("  " + " | ".join(row))
    return 0


# ── main ────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="引用網頁的存檔／驗證工具（Wayback Machine，純標準庫）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  python archive_url.py lookup https://www.twse.com.tw/
  python archive_url.py save   https://mops.twse.com.tw/mops/... --dry-run
  python archive_url.py hash   https://www.twse.com.tw/
  python archive_url.py log    --tail 10

金鑰紀律：IA_ACCESS_KEY / IA_SECRET_KEY 只讀環境變數，絕不寫死、絕不寫入 CSV。
""",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("lookup", help="查 CDX，印出最新一筆 Wayback 快照網址")
    p.add_argument("url")
    p.add_argument("--limit", type=int, default=2000, help="CDX 查詢筆數上限（預設 2000）")
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--csv-path", default=None)
    p.set_defaults(func=cmd_lookup)

    p = sub.add_parser("save", help="請求 Wayback 存檔（Save Page Now）")
    p.add_argument("url")
    p.add_argument("--dry-run", action="store_true", help="只印將送出的請求，不連網")
    p.add_argument("--retries", type=int, default=1)
    p.add_argument("--timeout", type=int, default=45)
    p.add_argument("--csv-path", default=None)
    p.set_defaults(func=cmd_save)

    p = sub.add_parser("hash", help="雜湊已存檔快照的內容（供變更監測比對）")
    p.add_argument("url")
    p.add_argument("--timestamp", default=None, help="指定快照時間戳（YYYYMMDDhhmmss）；不給則查最新一筆")
    p.add_argument("--limit", type=int, default=2000)
    p.add_argument("--retries", type=int, default=3)
    p.add_argument("--timeout", type=int, default=30)
    p.add_argument("--csv-path", default=None)
    p.set_defaults(func=cmd_hash)

    p = sub.add_parser("log", help="顯示（或建立）本機的查核記錄 CSV")
    p.add_argument("--tail", type=int, default=20)
    p.add_argument("--csv-path", default=None)
    p.set_defaults(func=cmd_log)

    args = ap.parse_args()
    try:
        return args.func(args)
    except RuntimeError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
