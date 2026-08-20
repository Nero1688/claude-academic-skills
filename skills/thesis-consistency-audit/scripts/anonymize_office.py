#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
anonymize_office.py — 投稿前的 Office 檔案身分資訊稽核與清除（雙盲審查用）

【為什麼需要】
多數 SSCI／TSSCI 期刊採**雙盲審查**，要求投稿檔案不得含作者身分資訊。
但 .docx/.pptx/.xlsx 是壓縮檔，作者資訊藏在好幾個地方，肉眼看不到：
  - docProps/core.xml  →  dc:creator（建立者）、cp:lastModifiedBy（最後修改者）
  - docProps/app.xml   →  Company（公司/學校）、Manager
  - docProps/custom.xml→  自訂屬性（有時含系所、計畫編號）
  - word/comments.xml  →  **每則註解都帶作者姓名與縮寫**
  - 追蹤修訂          →  每個 w:ins / w:del 都帶 w:author 與時間戳

**期刊 desk reject 的常見原因之一，就是投稿檔洩漏作者身分。**
Word 的「檢查文件」不一定會清乾淨追蹤修訂與註解裡的作者名。

【兩種模式】
  預設（匿名化）  ：清除所有身分欄位，供**雙盲投稿**使用
  --set-author    ：改填指定姓名，供**最終定稿／存檔**使用（非投稿版）

【重要紀律：不靜默刪除內容】
註解與追蹤修訂**含有內容**，不只是中繼資料。本工具預設**只報告不刪除**，
要一併處理必須明確加 --strip-comments / --strip-revisions。
清除前一律先備份（除非 --no-backup）。

【用法】
    python anonymize_office.py 論文.docx                    # 只稽核，不改檔
    python anonymize_office.py 論文.docx --apply            # 匿名化（雙盲投稿）
    python anonymize_office.py 論文.docx --apply --strip-comments --strip-revisions
    python anonymize_office.py 定稿.docx --apply --set-author "陳某某"
    python anonymize_office.py *.docx --apply               # 批次

支援 .docx / .pptx / .xlsx。

last_verified: 2026-08-14
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import zipfile
from datetime import date
from pathlib import Path

# 會洩漏身分的中繼資料欄位（標籤名 → 中文說明）
IDENTITY_TAGS = {
    "dc:creator": "建立者",
    "cp:lastModifiedBy": "最後修改者",
    "dc:title": "標題",
    "dc:subject": "主旨",
    "cp:keywords": "關鍵字",
    "dc:description": "備註",
    "cp:category": "分類",
    "cp:contentStatus": "內容狀態",
}
APP_TAGS = {
    "Company": "公司／機構",
    "Manager": "主管",
    "Application": "產生工具",
    "AppVersion": "工具版本",
}

SUPPORTED = {".docx", ".pptx", ".xlsx", ".docm", ".pptm", ".xlsm"}


# 開頭標籤的通用樣式。(?![^>]*/>) 用來排除自閉合標籤 <Tag/>——
# 否則 <Company/> 會被誤當成開頭標籤，再貪婪跨抓到後面同名標籤的 </Company>，
# 把中間無關的 XML 全部吃進來（此為實測踩到的 bug）。
def _open_tag(t: str) -> str:
    return rf"<{re.escape(t)}\b(?![^>]*/>)[^>]*>"


def _tag_values(xml: str, tags: dict) -> dict:
    """抓出各標籤的現值（空字串代表存在但為空）。"""
    out = {}
    for t in tags:
        e = re.escape(t)
        m = re.search(rf"{_open_tag(t)}(.*?)</{e}>", xml, re.S)
        if m:
            out[t] = m.group(1).strip()
        elif re.search(rf"<{e}\b[^>]*/>", xml):
            out[t] = ""
    return out


def _blank_tags(xml: str, tags) -> str:
    """把標籤內容清空（保留標籤本身，避免破壞 OOXML schema）。"""
    for t in tags:
        e = re.escape(t)
        xml = re.sub(
            rf"({_open_tag(t)})(.*?)(</{e}>)",
            r"\1\3",
            xml,
            flags=re.S,
        )
    return xml


def _set_tag(xml: str, tag: str, value: str) -> str:
    e = re.escape(tag)
    if re.search(rf"{_open_tag(tag)}.*?</{e}>", xml, re.S):
        return re.sub(
            rf"({_open_tag(tag)})(.*?)(</{e}>)",
            lambda m: m.group(1) + value + m.group(3),
            xml,
            flags=re.S,
        )
    return re.sub(rf"<{e}\b[^>]*/>", f"<{tag}>{value}</{tag}>", xml, count=1)


def audit(path: Path) -> dict:
    """稽核一個檔案，回傳發現的身分資訊。不修改檔案。"""
    rep = {"file": path.name, "core": {}, "app": {}, "custom": False,
           "comment_authors": set(), "revision_authors": set(),
           "comment_count": 0, "revision_count": 0}
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if "docProps/core.xml" in names:
            rep["core"] = _tag_values(z.read("docProps/core.xml").decode("utf-8", "ignore"),
                                      IDENTITY_TAGS)
        if "docProps/app.xml" in names:
            rep["app"] = _tag_values(z.read("docProps/app.xml").decode("utf-8", "ignore"),
                                     APP_TAGS)
        rep["custom"] = "docProps/custom.xml" in names

        for n in names:
            if re.search(r"(comments|commentsExtended)\.xml$", n):
                x = z.read(n).decode("utf-8", "ignore")
                a = re.findall(r'w:author="([^"]*)"', x) + re.findall(r'author="([^"]*)"', x)
                rep["comment_authors"].update(v for v in a if v.strip())
                rep["comment_count"] += len(re.findall(r"<w:comment[\s>]", x))
            if n.endswith("document.xml") or "/slides/" in n or n.endswith("sheet1.xml"):
                x = z.read(n).decode("utf-8", "ignore")
                ins = re.findall(r'<w:(?:ins|del)\b[^>]*w:author="([^"]*)"', x)
                rep["revision_authors"].update(v for v in ins if v.strip())
                rep["revision_count"] += len(ins)
    return rep


def print_report(rep: dict) -> bool:
    """印出稽核報告。回傳 True 代表有身分洩漏風險。"""
    risky = False
    print(f"\n=== {rep['file']} ===")

    found = {k: v for k, v in rep["core"].items() if v}
    if found:
        risky = True
        print("  ⚠️ docProps/core.xml 含資訊：")
        for k, v in found.items():
            print(f"       {IDENTITY_TAGS[k]:8s}（{k}）= 「{v}」")
    else:
        print("  ✓ core.xml 身分欄位皆空")

    fa = {k: v for k, v in rep["app"].items() if v}
    if fa:
        for k, v in fa.items():
            mark = "⚠️" if k in ("Company", "Manager") else "  "
            if k in ("Company", "Manager"):
                risky = True
            print(f"  {mark} app.xml {APP_TAGS[k]}（{k}）= 「{v}」")

    if rep["custom"]:
        risky = True
        print("  ⚠️ 含 docProps/custom.xml（自訂屬性，可能有系所／計畫編號）")

    if rep["comment_authors"]:
        risky = True
        print(f"  🚨 註解 {rep['comment_count']} 則，作者：{sorted(rep['comment_authors'])}")
        print("       → 註解含內容，預設不刪；要刪請加 --strip-comments")
    if rep["revision_authors"]:
        risky = True
        print(f"  🚨 追蹤修訂 {rep['revision_count']} 處，作者：{sorted(rep['revision_authors'])}")
        print("       → 追蹤修訂含內容，預設不刪；要刪請加 --strip-revisions")

    if not risky:
        print("  ✅ 未發現身分洩漏風險，可直接雙盲投稿")
    return risky


def apply_clean(path: Path, author: str | None, strip_comments: bool,
                strip_revisions: bool, backup: bool) -> None:
    """重寫檔案：清除或改寫身分資訊。"""
    if backup:
        bak = path.with_suffix(path.suffix + f".bak-{date.today():%Y%m%d}")
        if not bak.exists():
            shutil.copy2(path, bak)
            print(f"  已備份 → {bak.name}")
        else:
            print(f"  （同日備份已存在，不覆蓋：{bak.name}）")

    tmp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            n = item.filename
            data = zin.read(n)

            if n == "docProps/custom.xml":
                print("  已移除 docProps/custom.xml")
                continue
            if strip_comments and re.search(r"(comments|commentsExtended|commentsIds)\.xml$", n):
                print(f"  已移除 {n}")
                continue

            if n in ("docProps/core.xml", "docProps/app.xml"):
                x = data.decode("utf-8", "ignore")
                if n == "docProps/core.xml":
                    x = _blank_tags(x, IDENTITY_TAGS)
                    if author:
                        x = _set_tag(x, "dc:creator", author)
                        x = _set_tag(x, "cp:lastModifiedBy", author)
                else:
                    x = _blank_tags(x, ("Company", "Manager"))
                data = x.encode("utf-8")

            if strip_revisions and (n.endswith("document.xml") or "/slides/" in n):
                x = data.decode("utf-8", "ignore")
                # 只把作者名改成匿名，不刪修訂內容（刪內容會改變文件）
                x = re.sub(r'(w:author=")[^"]*(")', r"\1Author\2", x)
                x = re.sub(r'(w:date=")[^"]*(")', r"\g<1>2000-01-01T00:00:00Z\2", x)
                data = x.encode("utf-8")

            zout.writestr(item, data)

    tmp.replace(path)
    mode = f"已改填作者「{author}」" if author else "已匿名化（雙盲投稿用）"
    print(f"  ✅ {mode}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="投稿前 Office 檔案身分資訊稽核與清除（雙盲審查用）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  python anonymize_office.py 論文.docx                 # 只稽核，不動檔案
  python anonymize_office.py 論文.docx --apply         # 匿名化（雙盲投稿）
  python anonymize_office.py 論文.docx --apply --strip-comments --strip-revisions
  python anonymize_office.py 定稿.docx --apply --set-author "你的姓名"

⚠️ 雙盲投稿請用**預設的匿名模式**，不要用 --set-author。
   --set-author 是給最終定稿／個人存檔版用的。

⚠️ 本工具只處理**檔案中繼資料**。正文裡的自我引用
   （「如同作者先前研究（陳，2024）所示…」）、致謝、
   基金計畫編號仍須人工檢查——那是最常見的雙盲破功點。
""",
    )
    ap.add_argument("files", nargs="+", help="要處理的檔案（可多個）")
    ap.add_argument("--apply", action="store_true", help="實際寫入變更（不加只稽核）")
    ap.add_argument("--set-author", metavar="NAME", help="改填指定作者（定稿用，非雙盲）")
    ap.add_argument("--strip-comments", action="store_true", help="一併移除註解（含內容）")
    ap.add_argument("--strip-revisions", action="store_true", help="追蹤修訂作者匿名化")
    ap.add_argument("--no-backup", action="store_true", help="不建立備份（不建議）")
    a = ap.parse_args()

    targets = []
    for pat in a.files:
        p = Path(pat)
        targets.extend(sorted(p.parent.glob(p.name)) if any(c in pat for c in "*?") else [p])

    if not targets:
        print("錯誤：找不到符合的檔案", file=sys.stderr)
        return 1

    risky_any = False
    for f in targets:
        if not f.exists():
            print(f"跳過（不存在）：{f}", file=sys.stderr)
            continue
        if f.suffix.lower() not in SUPPORTED:
            print(f"跳過（不支援 {f.suffix}）：{f.name}", file=sys.stderr)
            continue
        try:
            rep = audit(f)
        except zipfile.BadZipFile:
            print(f"跳過（不是有效的 Office 檔）：{f.name}", file=sys.stderr)
            continue

        risky = print_report(rep)
        risky_any = risky_any or risky
        if a.apply:
            apply_clean(f, a.set_author, a.strip_comments, a.strip_revisions,
                        not a.no_backup)

    if not a.apply:
        print("\n（以上為稽核結果，未修改任何檔案。要實際清除請加 --apply）")
    print("\n📌 雙盲投稿前仍須人工檢查：正文自我引用、致謝、基金計畫編號、"
          "圖檔浮水印、檔名是否含姓名。")
    return 1 if (risky_any and not a.apply) else 0


if __name__ == "__main__":
    sys.exit(main())
