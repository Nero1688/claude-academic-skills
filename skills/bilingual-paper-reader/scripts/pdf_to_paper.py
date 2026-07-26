#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pdf_to_paper.py — 把論文 PDF（或純文字檔）轉成 reader.html 可讀的「論文資料檔」

設計重點:reader.html 是**可重複使用的閱讀器**,一篇論文只是一份資料檔(JSON)。
不是「一篇論文一個 HTML」——你把任何論文轉成 JSON,都用同一個閱讀器開。

【流程】
    PDF ──pdf_to_paper.py──> paper.json ──拖進 reader.html──> 雙欄閱讀
                                  ↑
                          Claude 在此填入譯文與預先標記

【產出的 JSON 結構】
{
  "id": "…",                       # 依內容雜湊,用於 localStorage 分辨不同論文
  "title": "…",
  "source_file": "…",
  "created": "2026-07-26",
  "glossary": {"agency theory": "代理理論"},   # 術語對照表,確保全文譯名一致
  "paragraphs": [
    {"i": 0, "orig": "原文段落…", "trans": "", "marks": []}
  ]
}
`trans` 由 Claude 填入譯文;`marks` 由 Claude 填入預先標記,格式見 reader.html 說明。

【用法】
    python pdf_to_paper.py paper.pdf -o paper.json
    python pdf_to_paper.py paper.txt -o paper.json --format txt
    python pdf_to_paper.py paper.pdf -o paper.json --min-chars 120

【依賴】pypdf（讀 PDF 時必要）；純文字輸入不需要任何套件。

⚠️ 掃描版 PDF（無文字層）抽不到文字，本工具會明確報錯而不是產出空檔。
   請先用 OCR 工具處理（如 Adobe Acrobat、ocrmypdf）再轉。

last_verified: 2026-07-26
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

# 頁首頁尾雜訊的常見樣式（單獨成行的頁碼、期刊名縮寫行等）
NOISE_PATTERNS = [
    re.compile(r"^\s*\d{1,4}\s*$"),                     # 純頁碼
    re.compile(r"^\s*Downloaded from .*$", re.I),
    re.compile(r"^\s*This content downloaded .*$", re.I),
    re.compile(r"^\s*All use subject to .*$", re.I),
    re.compile(r"^\s*Electronic copy available at.*$", re.I),
]


def is_noise(line: str) -> bool:
    return any(p.match(line) for p in NOISE_PATTERNS)


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit("錯誤：讀 PDF 需要 pypdf。請執行：pip install pypdf")
    try:
        reader = PdfReader(str(path))
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"錯誤：無法開啟 PDF（{type(e).__name__}: {e}）")

    chunks = []
    for pg in reader.pages:
        try:
            chunks.append(pg.extract_text() or "")
        except Exception:  # noqa: BLE001
            chunks.append("")
    text = "\n".join(chunks)

    if len(text.strip()) < 200:
        raise SystemExit(
            f"錯誤：從 {path.name} 只抽到 {len(text.strip())} 個字元，幾乎沒有文字。\n"
            "　　　這通常表示它是**掃描版 PDF（影像，無文字層）**。\n"
            "　　　請先用 OCR 工具處理（ocrmypdf / Adobe Acrobat）後再轉，\n"
            "　　　或改用 --format txt 餵入已 OCR 好的純文字檔。"
        )
    return text


def split_paragraphs(text: str, min_chars: int) -> list[str]:
    """把抽出的文字切成段落。

    PDF 抽出的文字常有硬換行,策略:
    1. 先以空行切成塊
    2. 塊內把單純的斷行接回去(除非該行以句號結尾且下一行像新段落開頭)
    3. 丟掉太短的塊(頁首頁尾、圖表標號等雜訊)
    """
    raw_blocks = re.split(r"\n\s*\n", text)
    paras: list[str] = []

    for block in raw_blocks:
        lines = [ln.strip() for ln in block.split("\n")]
        lines = [ln for ln in lines if ln and not is_noise(ln)]
        if not lines:
            continue
        # 接合硬換行:上一行不以句末標點結尾就接下去
        merged = ""
        for ln in lines:
            if not merged:
                merged = ln
            elif re.search(r"[.!?。！？：:;；]$", merged) and re.match(r"^[A-Z一-鿿]", ln):
                paras.append(merged)
                merged = ln
            else:
                # 英文斷字連字號接合
                merged = merged[:-1] + ln if merged.endswith("-") else merged + " " + ln
        if merged:
            paras.append(merged)

    out = []
    for p in paras:
        p = re.sub(r"\s+", " ", p).strip()
        if len(p) >= min_chars:
            out.append(p)
    return out


# 版權/授權/預印本樣板句——常出現在第一頁，會被誤認為標題
BOILERPLATE = re.compile(
    r"(grants? permission|copyright|all rights reserved|licen[sc]e|arXiv:|preprint|"
    r"doi:|creative commons|provided proper attribution|reproduce)", re.I
)


def guess_title(paras: list[str], fallback: str) -> str:
    """從前幾段猜標題，跳過版權/授權樣板句。猜不到就用檔名。"""
    for p in paras[:6]:
        if 20 <= len(p) <= 250 and not BOILERPLATE.search(p):
            return p[:200]
    return fallback


def looks_like_table(p: str) -> bool:
    """判斷段落是否為被壓平的表格／數據列。

    表格經文字抽取後會變成大量數字與短 token 的字串,翻譯它沒有意義。
    判準:數字與符號占比高、且平均 token 長度短。
    """
    tokens = p.split()
    if len(tokens) < 8:
        return False
    digitish = sum(1 for t in tokens if re.search(r"\d", t))
    avg_len = sum(len(t) for t in tokens) / len(tokens)
    return digitish / len(tokens) > 0.35 and avg_len < 6.5


def main() -> int:
    ap = argparse.ArgumentParser(
        description="把論文 PDF／純文字轉成 reader.html 可讀的論文資料檔（JSON）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""範例：
  python pdf_to_paper.py paper.pdf -o paper.json
  python pdf_to_paper.py ocr_text.txt -o paper.json --format txt
  python pdf_to_paper.py paper.pdf -o paper.json --min-chars 150

產出的 JSON 中，`trans`（譯文）與 `marks`（預先標記）留空，由 Claude 填入。
填好後把 JSON 拖進 reader.html 即可雙欄閱讀。
""",
    )
    ap.add_argument("input", help="PDF 或純文字檔路徑")
    ap.add_argument("-o", "--output", help="輸出 JSON 路徑（預設同檔名 .json）")
    ap.add_argument("--format", choices=["pdf", "txt"], help="輸入格式（預設依副檔名）")
    ap.add_argument(
        "--min-chars", type=int, default=100,
        help="段落最短字元數，低於此值視為雜訊丟棄（預設 100；註腳多的論文可調高）",
    )
    ap.add_argument("--title", help="手動指定論文標題")
    a = ap.parse_args()

    src = Path(a.input)
    if not src.exists():
        print(f"錯誤：找不到 {src}", file=sys.stderr)
        return 1

    fmt = a.format or ("pdf" if src.suffix.lower() == ".pdf" else "txt")
    text = extract_pdf_text(src) if fmt == "pdf" else src.read_text(encoding="utf-8", errors="replace")

    paras = split_paragraphs(text, a.min_chars)
    if not paras:
        print("錯誤：切不出任何段落。試著調低 --min-chars。", file=sys.stderr)
        return 1

    doc = {
        "id": hashlib.sha256(("".join(paras[:5])).encode("utf-8")).hexdigest()[:16],
        "title": a.title or guess_title(paras, src.stem),
        "source_file": src.name,
        "created": str(date.today()),
        "glossary": {},
        "paragraphs": [
            {
                "i": i,
                "orig": p,
                "trans": "",
                "marks": [],
                # 被壓平的表格：標記出來，翻譯時可略過（翻表格數字沒有意義）
                **({"skip": "likely_table"} if looks_like_table(p) else {}),
            }
            for i, p in enumerate(paras)
        ],
    }

    out = Path(a.output) if a.output else src.with_suffix(".json")
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")

    chars = sum(len(p) for p in paras)
    n_tbl = sum(1 for p in doc["paragraphs"] if p.get("skip"))
    print(f"成功：{out}")
    print(f"　段落 {len(paras)} 段，原文合計 {chars:,} 字元")
    if n_tbl:
        print(f"　其中 {n_tbl} 段疑似為壓平的表格／數據列，已標 skip=likely_table（翻譯時可略過）")
    if doc["title"] == src.stem:
        print("　注意：猜不出標題（前幾段疑似版權樣板），已用檔名。建議用 --title 指定。")
    print(f"　論文 id：{doc['id']}（reader.html 用此 id 分辨不同論文的標記）")
    print("\n下一步：")
    print("　1. 請 Claude 逐段填入 trans（譯文）與 marks（預先標記）")
    print("　2. 把 JSON 拖進 reader.html 開始閱讀")
    if len(paras) > 120:
        print(f"\n提示：段落數 {len(paras)} 偏多，翻譯會消耗較多時間；")
        print("　　　可考慮只翻你要精讀的章節（請 Claude 指定段落範圍）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
