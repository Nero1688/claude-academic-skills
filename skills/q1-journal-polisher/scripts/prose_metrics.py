#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""prose_metrics.py — 文體訊號報告（服務 q1-journal-polisher 與 academic-journal-polisher）

用途：
    讀一份純文字或 Markdown 稿件，回報可觀察的文體統計「訊號」——句長分布、
    段落長度分布、過渡詞／AI 慣用語密度、英文被動語態粗估比例、中文「的」字
    密度、最長句與最短句的定位（行號）。

    這支腳本服務兩支潤飾技能：
      - q1-journal-polisher（--lang en，英文投稿潤飾）
      - academic-journal-polisher（--lang zh，中文投稿潤飾，透過跨技能引用呼叫本檔）

**固定聲明（每份報告開頭都會印出，不可省略、不可修改語意）**：
    「訊號不是判決；目的是審稿人可讀性，非規避偵測。」
    本腳本不判斷文章是不是 AI 寫的，也不判斷文章寫得好不好，只回報統計數字。
    數字是否代表值得注意的模式，由使用者或潤飾技能的人類判斷決定；任何單一
    數字都不構成「這篇是/不是 AI 寫的」或「這篇夠不夠格投稿」的結論。

零外部依賴：只用 Python 標準庫（re / json / statistics / argparse / pathlib）。
不發出任何網路請求，不讀寫本檔案以外的任何資源。

已知限制（誠實揭露，這是「訊號」工具而非精確語言學分析）：
    - 中文斷句以「。！？」為界，不處理引號內夾雜標點的巢狀情形。
    - 英文斷句以「. ! ?」加空白／行尾為界，用一份常見縮寫表（et al., e.g. 等）
      降低誤判，但無法涵蓋所有縮寫或小數點（如 3.5%）。
    - 被動語態偵測是規則式粗估（be 動詞＋過去分詞），非文法剖析器，會有
      漏判與誤判；只適合看「量級」與「前後稿比較」，不適合逐句究責。
    - Markdown 標題行（# 開頭）會被排除在統計之外，其餘 Markdown 語法
      （條列符號、表格）不特別處理，可能輕微影響句長統計。

用法：
    python prose_metrics.py --lang en manuscript.txt
    python prose_metrics.py --lang zh manuscript.md --json
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

DISCLAIMER = "訊號不是判決；目的是審稿人可讀性，非規避偵測。"

LEXICON_PATH = Path(__file__).resolve().parent.parent / "references" / "ai-tell-lexicon.json"

EN_ABBREVIATIONS = [
    "et al.", "e.g.", "i.e.", "cf.", "vs.", "approx.",
    "Dr.", "Mr.", "Mrs.", "Ms.", "Prof.",
    "Fig.", "Eq.", "No.", "pp.", "p.", "Vol.", "etc.",
]

# 規則式被動語態偵測：be 動詞 + (最多兩個修飾詞) + 過去分詞
_PARTICIPLE_IRREGULAR = (
    "shown|given|taken|written|done|made|known|seen|found|held|told|kept|"
    "left|put|set|read|thought|brought|bought|caught|taught|sent|spent|"
    "built|felt|meant|paid|said|understood|chosen|driven|drawn|grown"
)
PASSIVE_RE = re.compile(
    r"\b(?:am|is|are|was|were|be|been|being)\b\s+(?:\w+\s+){0,2}"
    r"(?:\w+ed\b|" + _PARTICIPLE_IRREGULAR + r")\b",
    re.IGNORECASE,
)

ZH_SENT_RE = re.compile(r"[^。！？\n]+[。！？]+")
EN_SENT_RE = re.compile(r"[^\n]+?[.!?]+(?=\s|$)")
HEADER_RE = re.compile(r"^\s{0,3}#{1,6}\s")


def load_lexicon() -> dict:
    """讀取 ai-tell-lexicon.json；找不到檔案時回傳空詞表並在 stderr 警告，不中止。"""
    if not LEXICON_PATH.is_file():
        print(f"[警告] 找不到詞表 {LEXICON_PATH}，過渡詞／AI 慣用語密度將回報為 0。", file=sys.stderr)
        return {"en": {"transition_overuse": [], "ai_tell_phrases": []},
                "zh": {"transition_overuse": [], "ai_tell_phrases": []}}
    with LEXICON_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def build_char_stream(raw_lines: list[str]) -> tuple[str, list[int]]:
    """把原始行陣列組成一份可斷句的文字流，並回傳每個字元對應的原始行號（1-indexed）。

    規則：
      - 標題行（# 開頭）整行跳過，不計入文字流。
      - 空白行 → 在文字流中插入雙換行，作為段落分隔。
      - 內容行 → 逐字元附加，行尾加一個空白（把同段落內的軟斷行接成一句）。
    這樣段落之間仍以雙換行分隔，段落內部的硬換行不會誤切句子。
    """
    chars: list[str] = []
    line_of_char: list[int] = []
    for idx, line in enumerate(raw_lines, start=1):
        if HEADER_RE.match(line):
            continue
        stripped = line.strip()
        if stripped == "":
            if not (len(chars) >= 2 and chars[-1] == "\n" and chars[-2] == "\n"):
                chars.append("\n")
                line_of_char.append(idx)
                chars.append("\n")
                line_of_char.append(idx)
            continue
        for ch in stripped:
            chars.append(ch)
            line_of_char.append(idx)
        chars.append(" ")
        line_of_char.append(idx)
    return "".join(chars), line_of_char


def protect_abbreviations(text: str) -> str:
    """把英文縮寫裡的句點換成 \\x00（長度不變，偏移量不受影響），避免誤切句子。"""
    protected = text
    for abbr in EN_ABBREVIATIONS:
        if abbr in protected:
            protected = protected.replace(abbr, abbr[:-1] + "\x00")
    return protected


def split_paragraphs(text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n{2,}", text)]
    return [p for p in paras if p]


def extract_sentences(text: str, line_of_char: list[int], lang: str) -> list[dict]:
    """回傳 [{"text":..., "line":..., "len":...}, ...]；len 依語言用不同單位。"""
    sentences: list[dict] = []
    if lang == "zh":
        matches = list(ZH_SENT_RE.finditer(text))
    else:
        protected = protect_abbreviations(text)
        matches = list(EN_SENT_RE.finditer(protected))

    last_end = 0
    for m in matches:
        raw = text[m.start():m.end()].strip()
        if not raw:
            continue
        start_idx = m.start()
        while start_idx < len(text) and text[start_idx].isspace():
            start_idx += 1
        line_no = line_of_char[start_idx] if start_idx < len(line_of_char) else (
            line_of_char[-1] if line_of_char else 1
        )
        length = len(raw) if lang == "zh" else len(raw.split())
        sentences.append({"text": raw, "line": line_no, "len": length})
        last_end = m.end()

    tail = text[last_end:].strip()
    if len(tail) > 2:
        start_idx = last_end
        while start_idx < len(text) and text[start_idx].isspace():
            start_idx += 1
        line_no = line_of_char[start_idx] if start_idx < len(line_of_char) else (
            line_of_char[-1] if line_of_char else 1
        )
        length = len(tail) if lang == "zh" else len(tail.split())
        sentences.append({"text": tail, "line": line_no, "len": length})

    return sentences


def dist_stats(values: list[float]) -> dict:
    if not values:
        return {"n": 0, "mean": None, "cv": None, "iqr": None, "q1": None, "q3": None,
                "min": None, "max": None}
    n = len(values)
    mean = statistics.mean(values)
    stdev = statistics.pstdev(values) if n > 1 else 0.0
    cv = round(stdev / mean, 3) if mean else None
    q1 = q3 = iqr = None
    if n >= 4:
        quantiles = statistics.quantiles(values, n=4, method="inclusive")
        q1, _, q3 = quantiles
        iqr = round(q3 - q1, 2)
        q1, q3 = round(q1, 2), round(q3, 2)
    return {
        "n": n, "mean": round(mean, 2), "cv": cv, "iqr": iqr,
        "q1": q1, "q3": q3, "min": round(min(values), 2), "max": round(max(values), 2),
    }


def count_lexicon_hits(text_lower_or_raw: str, phrases: list[str], case_insensitive: bool) -> dict:
    hits = {}
    hay = text_lower_or_raw.lower() if case_insensitive else text_lower_or_raw
    for phrase in phrases:
        needle = phrase.lower() if case_insensitive else phrase
        c = hay.count(needle)
        if c:
            hits[phrase] = c
    return hits


def analyze(path: Path, lang: str) -> dict:
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    text, line_of_char = build_char_stream(raw_lines)
    paragraphs = split_paragraphs(text)
    sentences = extract_sentences(text, line_of_char, lang)

    total_chars_no_space = len("".join(text.split()))
    word_count = len(text.split())

    sent_lengths = [s["len"] for s in sentences]
    sent_dist = dist_stats(sent_lengths)

    para_sent_counts = []
    for p in paragraphs:
        p_sentences = extract_sentences(p, [1] * (len(p) + 1), lang)
        para_sent_counts.append(len(p_sentences) if p_sentences else 1)
    para_dist = dist_stats(para_sent_counts)

    longest = max(sentences, key=lambda s: s["len"]) if sentences else None
    shortest = min(sentences, key=lambda s: s["len"]) if sentences else None

    lexicon = load_lexicon()
    lang_lex = lexicon.get(lang, {"transition_overuse": [], "ai_tell_phrases": []})
    case_insensitive = (lang == "en")
    transition_hits = count_lexicon_hits(text, lang_lex.get("transition_overuse", []), case_insensitive)
    ai_tell_hits = count_lexicon_hits(text, lang_lex.get("ai_tell_phrases", []), case_insensitive)

    denom_per_thousand = (word_count / 1000.0) if lang == "en" else (total_chars_no_space / 1000.0)
    denom_per_thousand = denom_per_thousand or 1.0
    transition_density = round(sum(transition_hits.values()) / denom_per_thousand, 2)
    ai_tell_density = round(sum(ai_tell_hits.values()) / denom_per_thousand, 2)

    report: dict = {
        "disclaimer": DISCLAIMER,
        "file": str(path),
        "lang": lang,
        "char_count_no_space": total_chars_no_space,
        "word_count": word_count if lang == "en" else None,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "sentence_length_dist": sent_dist,
        "sentence_length_unit": "words" if lang == "en" else "characters",
        "paragraph_sentence_count_dist": para_dist,
        "longest_sentence": longest,
        "shortest_sentence": shortest,
        "transition_word_hits": transition_hits,
        "transition_density_per_1000": transition_density,
        "ai_tell_phrase_hits": ai_tell_hits,
        "ai_tell_density_per_1000": ai_tell_density,
    }

    if lang == "en":
        passive_sentences = sum(1 for s in sentences if PASSIVE_RE.search(s["text"]))
        report["passive_voice_rough_ratio"] = (
            round(passive_sentences / len(sentences), 3) if sentences else None
        )
        report["passive_voice_sentence_count"] = passive_sentences
    else:
        de_count = text.count("的")
        report["de_char_density_per_100"] = (
            round(de_count / total_chars_no_space * 100, 2) if total_chars_no_space else None
        )
        report["de_char_count"] = de_count

    return report


def format_text_report(r: dict) -> str:
    lines = []
    bar = "=" * 70
    lines.append(bar)
    lines.append(r["disclaimer"])
    lines.append(bar)
    lines.append(f"檔案：{r['file']}　語言：{r['lang']}　字數（不含空白）：{r['char_count_no_space']}")
    lines.append(f"句子數：{r['sentence_count']}　段落數：{r['paragraph_count']}")
    lines.append("")

    sd = r["sentence_length_dist"]
    unit = "字" if r["sentence_length_unit"] == "characters" else "詞"
    lines.append(f"【句長分布】(單位：{unit})")
    if sd["n"]:
        iqr_txt = f"IQR {sd['iqr']}（Q1={sd['q1']}, Q3={sd['q3']}）" if sd["iqr"] is not None else "IQR 樣本數不足"
        lines.append(f"  平均 {sd['mean']}　CV {sd['cv']}　{iqr_txt}")
        if r["longest_sentence"]:
            lines.append(f"  最長句：{r['longest_sentence']['len']} {unit}（第 {r['longest_sentence']['line']} 行）")
        if r["shortest_sentence"]:
            lines.append(f"  最短句：{r['shortest_sentence']['len']} {unit}（第 {r['shortest_sentence']['line']} 行）")
    else:
        lines.append("  無可辨識句子")
    lines.append("")

    pd = r["paragraph_sentence_count_dist"]
    lines.append("【段落長度分布】(單位：句數/段)")
    if pd["n"]:
        lines.append(f"  平均 {pd['mean']}　CV {pd['cv']}　範圍 {pd['min']}–{pd['max']}")
    else:
        lines.append("  無可辨識段落")
    lines.append("")

    lines.append("【過渡詞／AI 慣用語密度】(次／千字或千詞)")
    lines.append(f"  過渡詞合計：{r['transition_density_per_1000']}／千　明細：{r['transition_word_hits'] or '（無命中）'}")
    lines.append(f"  AI 慣用語合計：{r['ai_tell_density_per_1000']}／千　明細：{r['ai_tell_phrase_hits'] or '（無命中）'}")
    lines.append("")

    if r["lang"] == "en":
        pv = r.get("passive_voice_rough_ratio")
        lines.append(f"【被動語態粗估比例】{pv if pv is not None else 'N/A'}（{r.get('passive_voice_sentence_count', 0)}／{r['sentence_count']} 句，規則式估計，非文法剖析）")
    else:
        dd = r.get("de_char_density_per_100")
        lines.append(f"【「的」字密度】{dd if dd is not None else 'N/A'} 次／百字（共 {r.get('de_char_count', 0)} 次）")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="文體訊號報告：句長/段落分布、過渡詞密度、被動語態或的字密度。訊號不是判決。"
    )
    parser.add_argument("input", help="輸入檔案路徑（.txt 或 .md，UTF-8）")
    parser.add_argument("--lang", choices=["en", "zh"], required=True, help="文稿語言")
    parser.add_argument("--json", action="store_true", help="輸出機器可讀 JSON（仍含 disclaimer 欄位）")
    args = parser.parse_args()

    path = Path(args.input)
    if not path.is_file():
        print(f"[錯誤] 找不到檔案：{path}", file=sys.stderr)
        return 1

    try:
        report = analyze(path, args.lang)
    except UnicodeDecodeError as e:
        # L1 修復(2026-09-20)：本檔嚴格要求 UTF-8、未捕捉例外，非 UTF-8 檔案
        # （常見於 Word 另存或舊系統匯出的 Big5/cp950）會直接噴一長串
        # traceback，使用者看不出該怎麼辦。改成友善訊息＋具體修法。
        print(
            f"[錯誤] {path} 不是合法的 UTF-8 檔案（{e}）。\n"
            "         本工具要求輸入檔為 UTF-8。若原始檔是 Word/舊系統匯出的 "
            "Big5 或 cp950，請先另存為 UTF-8 編碼（記事本「另存新檔」選 UTF-8，"
            "或 Word「另存為純文字」再指定編碼）後重跑。",
            file=sys.stderr,
        )
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_text_report(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
