#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
litmatrix.py — 文獻語料庫與文獻比較矩陣建置工具

把一堆 PDF 變成:(1) 有結構的文獻資料夾、(2) 一份 JSON 文獻庫、
(3) 一張可比較的 Excel 文獻矩陣(含 APA7 引用、DOI、摘要、跨文獻比較欄)。

【子指令】
  init    建立文獻資料夾結構與空的 library.json
  add     加入一篇文獻:抽 PDF metadata → 查 CrossRef → 寫入 library.json
  lookup  只查 DOI 的 metadata 與 APA7,不寫入(用來驗證)
  build   從 library.json 產出 Excel 文獻矩陣
  list    列出目前文獻庫內容

【依賴】
  requests  必要(CrossRef 查詢)
  openpyxl  產 Excel 時必要
  pypdf     從 PDF 抽 metadata/文字時必要(可省略,改用 --doi 手動指定)

【資料來源與授權】
  CrossRef REST API — https://api.crossref.org/ — 免金鑰、免費。
  依 CrossRef 禮貌池(polite pool)慣例,建議在 User-Agent 帶聯絡信箱以取得較佳服務:
  設定環境變數 CROSSREF_MAILTO=you@example.com 即可,**本腳本不硬編碼任何信箱**。
  CrossRef metadata 依其條款多為開放,但**摘要(abstract)著作權通常仍屬出版社**——
  僅供個人研究閱讀,勿公開重製散布(見 SKILL.md 的著作權紀律)。

last_verified: 2026-07-26
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

CROSSREF_API = "https://api.crossref.org/works"
DEFAULT_UA = "literature-matrix-builder/1.0 (academic research use)"

# 文獻矩陣欄位:前段為書目,後段為「比較/綜整」欄——後者才是矩陣的學術價值所在
MATRIX_COLUMNS = [
    ("key", "引用代碼"),
    ("apa7", "APA7 參考文獻"),
    ("authors_short", "作者(簡)"),
    ("year", "年份"),
    ("title", "題名"),
    ("journal", "期刊"),
    ("doi", "DOI"),
    ("theory", "理論視角"),
    ("context", "研究情境/樣本"),
    ("method", "研究方法"),
    ("iv", "自變數"),
    ("dv", "應變數"),
    ("mediator_moderator", "中介/調節"),
    ("key_findings", "主要發現"),
    ("gap_or_limitation", "限制/未解問題"),
    ("relevance", "與本研究的關聯"),
    ("quote", "可引用金句(附頁碼)"),
    ("abstract", "摘要"),
    ("pdf_path", "PDF 路徑"),
    ("added_on", "加入日期"),
]

# 需要人工填寫的綜整欄(工具抓不到,必須研究者自己讀完填)
MANUAL_FIELDS = [
    "theory",
    "context",
    "method",
    "iv",
    "dv",
    "mediator_moderator",
    "key_findings",
    "gap_or_limitation",
    "relevance",
    "quote",
]


def _session():
    try:
        import requests
    except ImportError:
        raise SystemExit("錯誤：需要 requests 套件。請執行：pip install requests")
    s = requests.Session()
    mailto = os.environ.get("CROSSREF_MAILTO", "").strip()
    ua = DEFAULT_UA + (f" mailto:{mailto}" if mailto else "")
    s.headers.update({"User-Agent": ua})
    return s


# ── CrossRef 查詢與 APA7 產生 ──────────────────────────────────────────
def fetch_crossref(doi: str, timeout: int = 30) -> dict[str, Any]:
    """以 DOI 取回 CrossRef metadata。查無或失敗時丟出 RuntimeError。"""
    doi = doi.strip().replace("https://doi.org/", "").replace("doi:", "").strip()
    s = _session()
    try:
        r = s.get(f"{CROSSREF_API}/{doi}", timeout=timeout)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"連線 CrossRef 失敗：{type(e).__name__}: {e}")
    if r.status_code == 404:
        raise RuntimeError(f"CrossRef 查無此 DOI：{doi}（請確認 DOI 是否正確）")
    if r.status_code != 200:
        raise RuntimeError(f"CrossRef 回應 HTTP {r.status_code}")
    return r.json()["message"]


def _authors(msg: dict) -> list[tuple[str, str]]:
    out = []
    for a in msg.get("author", []) or []:
        fam = (a.get("family") or "").strip()
        giv = (a.get("given") or "").strip()
        if fam or giv:
            out.append((fam, giv))
    return out


def _initials(given: str) -> str:
    parts = re.split(r"[\s\-]+", given.strip())
    return " ".join(f"{p[0]}." for p in parts if p)


def to_apa7(msg: dict) -> str:
    """依 APA 7 期刊論文格式組出參考文獻字串。

    格式：Author, A. A., & Author, B. B. (Year). Title. *Journal*, *Vol*(Issue), pages.
          https://doi.org/xxx
    ⚠️ 只處理期刊論文(journal-article)。書籍/章節/會議論文格式不同,
       本函式會在前面加註「[需人工確認格式]」,由使用者依 APA7 手冊調整。
    """
    auths = _authors(msg)
    n = len(auths)
    if n == 0:
        a_str = "(No author)"
    elif n == 1:
        a_str = f"{auths[0][0]}, {_initials(auths[0][1])}"
    elif n <= 20:
        parts = [f"{f}, {_initials(g)}" for f, g in auths]
        a_str = ", ".join(parts[:-1]) + ", & " + parts[-1]
    else:
        parts = [f"{f}, {_initials(g)}" for f, g in auths]
        a_str = ", ".join(parts[:19]) + ", ... " + parts[-1]

    year = "n.d."
    for k in ("issued", "published-print", "published-online"):
        dp = (msg.get(k) or {}).get("date-parts") or []
        if dp and dp[0] and dp[0][0]:
            year = str(dp[0][0])
            break

    title = (msg.get("title") or [""])[0].strip().rstrip(".")
    journal = (msg.get("container-title") or [""])[0].strip()
    vol = msg.get("volume", "")
    issue = msg.get("issue", "")
    pages = msg.get("page", "")
    doi = msg.get("DOI", "")

    bits = f"{a_str} ({year}). {title}."
    if journal:
        bits += f" {journal}"
        if vol:
            bits += f", {vol}"
            if issue:
                bits += f"({issue})"
        if pages:
            bits += f", {pages}"
        bits += "."
    if doi:
        bits += f" https://doi.org/{doi}"

    if msg.get("type") != "journal-article":
        bits = f"[需人工確認格式:{msg.get('type', '?')}] " + bits
    return bits


def clean_abstract(msg: dict) -> str:
    """CrossRef 的 abstract 常含 JATS XML 標籤,清掉。"""
    ab = msg.get("abstract") or ""
    ab = re.sub(r"<[^>]+>", "", ab)
    return re.sub(r"\s+", " ", ab).strip()


def cite_key(msg: dict) -> str:
    auths = _authors(msg)
    fam = auths[0][0] if auths else "Unknown"
    year = "nd"
    dp = (msg.get("issued") or {}).get("date-parts") or []
    if dp and dp[0] and dp[0][0]:
        year = str(dp[0][0])
    return f"{re.sub(r'[^A-Za-z]', '', fam) or 'Unknown'}{year}"


def authors_short(msg: dict) -> str:
    auths = _authors(msg)
    if not auths:
        return ""
    if len(auths) == 1:
        return auths[0][0]
    if len(auths) == 2:
        return f"{auths[0][0]} & {auths[1][0]}"
    return f"{auths[0][0]} et al."


# ── PDF metadata 抽取 ─────────────────────────────────────────────────
DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Za-z0-9]+\b")


def doi_from_pdf(path: Path, max_pages: int = 3) -> str | None:
    """從 PDF 前幾頁的文字與內建 metadata 找 DOI。找不到回傳 None。"""
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit(
            "錯誤：從 PDF 抽 DOI 需要 pypdf。請執行：pip install pypdf\n"
            "（或改用 --doi 直接指定 DOI，就不需要 pypdf）"
        )
    try:
        reader = PdfReader(str(path))
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"無法讀取 PDF：{type(e).__name__}: {e}")

    meta = reader.metadata or {}
    for v in meta.values():
        if isinstance(v, str):
            m = DOI_RE.search(v)
            if m:
                return m.group(0).rstrip(".,;")

    for pg in reader.pages[:max_pages]:
        try:
            txt = pg.extract_text() or ""
        except Exception:  # noqa: BLE001
            continue
        m = DOI_RE.search(txt)
        if m:
            return m.group(0).rstrip(".,;")
    return None


# ── 文獻庫存取 ────────────────────────────────────────────────────────
def lib_path(root: Path) -> Path:
    return root / "library.json"


def load_lib(root: Path) -> dict:
    p = lib_path(root)
    if not p.exists():
        raise SystemExit(f"錯誤：找不到 {p}。請先執行：python litmatrix.py init -d {root}")
    return json.loads(p.read_text(encoding="utf-8"))


def save_lib(root: Path, lib: dict) -> None:
    lib_path(root).write_text(
        json.dumps(lib, ensure_ascii=False, indent=2), encoding="utf-8"
    )


# ── 子指令 ────────────────────────────────────────────────────────────
def cmd_init(a) -> int:
    root = Path(a.dir)
    for sub in ["01_pdf", "02_notes", "03_output"]:
        (root / sub).mkdir(parents=True, exist_ok=True)
    p = lib_path(root)
    if p.exists():
        print(f"提示：{p} 已存在，未覆蓋。")
    else:
        save_lib(root, {"created": str(date.today()), "entries": []})
        print(f"已建立 {p}")
    print(f"""
文獻資料夾結構已就緒：{root}
  01_pdf/     放 PDF 原檔
  02_notes/   放每篇的閱讀筆記（Markdown）
  03_output/  產出的 Excel 矩陣
  library.json 文獻庫（單一事實來源）

下一步：
  python litmatrix.py add -d {root} --pdf 01_pdf/xxx.pdf
  python litmatrix.py add -d {root} --doi 10.1177/0149206311436079
""")
    return 0


def cmd_lookup(a) -> int:
    msg = fetch_crossref(a.doi)
    print(f"引用代碼：{cite_key(msg)}")
    print(f"類型　　：{msg.get('type')}")
    print(f"APA7　　：{to_apa7(msg)}")
    ab = clean_abstract(msg)
    print(f"摘要　　：{(ab[:300] + '…') if len(ab) > 300 else (ab or '(CrossRef 無摘要)')}")
    return 0


def cmd_add(a) -> int:
    root = Path(a.dir)
    lib = load_lib(root)

    doi = a.doi
    pdf_rel = ""
    if a.pdf:
        pdf = Path(a.pdf)
        if not pdf.is_absolute():
            pdf = root / a.pdf
        if not pdf.exists():
            print(f"錯誤：找不到 PDF {pdf}", file=sys.stderr)
            return 1
        try:
            pdf_rel = str(pdf.relative_to(root))
        except ValueError:
            pdf_rel = str(pdf)
        if not doi:
            doi = doi_from_pdf(pdf)
            if not doi:
                print(
                    f"錯誤：無法從 {pdf.name} 找到 DOI。\n"
                    "　　　可能是掃描版 PDF（無文字層，需先 OCR），或該文獻無 DOI。\n"
                    "　　　請改用 --doi 手動指定，或用 --manual 建立僅有書目的空白條目。",
                    file=sys.stderr,
                )
                return 1
            print(f"從 PDF 找到 DOI：{doi}")

    if not doi:
        print("錯誤：請提供 --doi 或 --pdf", file=sys.stderr)
        return 1

    msg = fetch_crossref(doi)
    key = cite_key(msg)
    if any(e["key"] == key for e in lib["entries"]) and not a.force:
        print(f"提示：引用代碼 {key} 已存在，未重複加入（用 --force 可覆寫）。")
        return 0
    lib["entries"] = [e for e in lib["entries"] if e["key"] != key]

    entry = {
        "key": key,
        "apa7": to_apa7(msg),
        "authors_short": authors_short(msg),
        "year": (msg.get("issued", {}).get("date-parts") or [[""]])[0][0] or "",
        "title": (msg.get("title") or [""])[0],
        "journal": (msg.get("container-title") or [""])[0],
        "doi": msg.get("DOI", ""),
        "abstract": clean_abstract(msg),
        "pdf_path": pdf_rel,
        "added_on": str(date.today()),
    }
    for f in MANUAL_FIELDS:
        entry[f] = ""

    lib["entries"].append(entry)
    save_lib(root, lib)
    print(f"已加入：{key} — {entry['title'][:60]}")
    if not entry["abstract"]:
        print("　注意：CrossRef 未提供摘要，需自行補（許多出版社不釋出摘要）。")
    print(f"　待人工填寫的綜整欄：{'、'.join(MANUAL_FIELDS)}")
    return 0


def cmd_list(a) -> int:
    lib = load_lib(Path(a.dir))
    es = lib["entries"]
    print(f"文獻庫共 {len(es)} 篇：")
    for e in sorted(es, key=lambda x: (str(x.get("year")), x["key"])):
        done = sum(1 for f in MANUAL_FIELDS if e.get(f))
        print(f"  {e['key']:22s} {str(e.get('year')):6s} 綜整欄 {done}/{len(MANUAL_FIELDS)}  {e['title'][:48]}")
    return 0


def cmd_build(a) -> int:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font, PatternFill
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise SystemExit("錯誤：產 Excel 需要 openpyxl。請執行：pip install openpyxl")

    root = Path(a.dir)
    lib = load_lib(root)
    es = sorted(lib["entries"], key=lambda x: (str(x.get("year")), x["key"]))
    if not es:
        print("錯誤：文獻庫是空的，先用 add 加入文獻。", file=sys.stderr)
        return 1

    out = Path(a.output) if a.output else root / "03_output" / "literature_matrix.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)

    wb = Workbook()
    ws = wb.active
    ws.title = "文獻矩陣"

    hdr_fill = PatternFill("solid", fgColor="D9E2F3")
    man_fill = PatternFill("solid", fgColor="FFF2CC")  # 待人工填寫欄以黃底標示
    hdr_font = Font(name="Times New Roman", bold=True, size=11)

    for c, (fid, label) in enumerate(MATRIX_COLUMNS, 1):
        cell = ws.cell(row=1, column=c, value=label)
        cell.font = hdr_font
        cell.fill = man_fill if fid in MANUAL_FIELDS else hdr_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    widths = {
        "apa7": 60, "title": 45, "abstract": 70, "key_findings": 40,
        "gap_or_limitation": 35, "relevance": 35, "quote": 40, "journal": 28,
        "doi": 26, "theory": 22, "context": 22, "method": 20, "iv": 20,
        "dv": 20, "mediator_moderator": 20, "pdf_path": 24, "key": 18,
    }
    for c, (fid, _) in enumerate(MATRIX_COLUMNS, 1):
        ws.column_dimensions[get_column_letter(c)].width = widths.get(fid, 12)

    body = Font(name="Times New Roman", size=10)
    for r, e in enumerate(es, 2):
        for c, (fid, _) in enumerate(MATRIX_COLUMNS, 1):
            cell = ws.cell(row=r, column=c, value=e.get(fid, ""))
            cell.font = body
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if fid in MANUAL_FIELDS and not e.get(fid):
                cell.fill = man_fill

    ws.freeze_panes = "C2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(MATRIX_COLUMNS))}{len(es) + 1}"

    # 第二張表：待辦清單——哪幾篇的綜整欄還沒填
    ws2 = wb.create_sheet("待補清單")
    ws2.append(["引用代碼", "題名", "未填欄位數", "未填欄位"])
    for c in range(1, 5):
        ws2.cell(row=1, column=c).font = hdr_font
        ws2.cell(row=1, column=c).fill = hdr_fill
    for e in es:
        miss = [lbl for fid, lbl in MATRIX_COLUMNS if fid in MANUAL_FIELDS and not e.get(fid)]
        if miss:
            ws2.append([e["key"], e["title"][:60], len(miss), "、".join(miss)])
    for col, w in zip("ABCD", (18, 55, 12, 60)):
        ws2.column_dimensions[col].width = w

    wb.save(out)
    filled = sum(1 for e in es if all(e.get(f) for f in MANUAL_FIELDS))
    print(f"成功：已產出 {out}")
    print(f"　文獻 {len(es)} 篇，綜整欄全填完的有 {filled} 篇（其餘見「待補清單」工作表）。")
    print("　黃底欄位＝工具抓不到、需你讀完論文後自己填的綜整欄。")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="文獻語料庫與文獻比較矩陣建置工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  python litmatrix.py init   -d ./lit
  python litmatrix.py add    -d ./lit --doi 10.1177/0149206311436079
  python litmatrix.py add    -d ./lit --pdf 01_pdf/paper.pdf
  python litmatrix.py lookup --doi 10.5465/amj.2011.0862
  python litmatrix.py list   -d ./lit
  python litmatrix.py build  -d ./lit

CrossRef 禮貌池：設環境變數 CROSSREF_MAILTO=you@example.com 可取得較佳服務品質。
本腳本不硬編碼任何信箱。
""",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="建立文獻資料夾結構")
    p.add_argument("-d", "--dir", default="./lit", help="文獻庫根目錄（預設 ./lit）")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("add", help="加入一篇文獻")
    p.add_argument("-d", "--dir", default="./lit")
    p.add_argument("--doi", help="DOI（有 PDF 時可省略，會自動從 PDF 找）")
    p.add_argument("--pdf", help="PDF 路徑（相對於文獻庫根目錄）")
    p.add_argument("--force", action="store_true", help="引用代碼重複時覆寫")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("lookup", help="只查 DOI，不寫入文獻庫")
    p.add_argument("--doi", required=True)
    p.set_defaults(func=cmd_lookup)

    p = sub.add_parser("list", help="列出文獻庫內容與填寫進度")
    p.add_argument("-d", "--dir", default="./lit")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("build", help="產出 Excel 文獻矩陣")
    p.add_argument("-d", "--dir", default="./lit")
    p.add_argument("-o", "--output", help="輸出 xlsx 路徑")
    p.set_defaults(func=cmd_build)

    a = ap.parse_args()
    try:
        return a.func(a)
    except RuntimeError as e:
        print(f"錯誤：{e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
