#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_response_matrix.py — 把純文字 decision letter 切成逐則意見，輸出 R&R 分診表（xlsx）

對應 SKILL.md Step 1「意見拆解與分診」：一則意見一列，欄位為
    審稿人／編號／來源區段／意見摘錄／意見全文／類型(建議)／主題標籤／落差對應(建議)／
    同意度／處理策略／修改位置／狀態／工作量(預估)／備註
其中「類型」「主題標籤」「落差對應」「工作量」是關鍵字啟發式的**建議值**，一律要人工確認；
「同意度／處理策略／修改位置／狀態」留白給使用者填，並附下拉選單。

台灣稿件常見落差→對策（本腳本的對應）：
    分診表的「落差對應(建議)」欄把每則意見對到台灣商管稿件在頂刊最常被殺的三個位置——
      落差 1 情境複製（審稿人問 why Taiwan / generalizability）
      落差 2 平行趨勢只畫圖、沒做誠實區間（問 pre-trend power / honest CI / control group）
      落差 3 只報統計顯著、缺經濟量級與基準（問 economic significance / magnitude / benchmark）
    對到落差的意見優先處理：對策句式與附表模板見
      references/rr-conventions-top-journals.md 第八節（回覆信怎麼寫）、
      q1-journal-reviewer/references/top-journal-standards.md 第五節（稿件怎麼改）。
    「統計」工作表另列三落差各被幾位審稿人提到——兩位以上提同一落差＝這一輪的主戰場。

用法：
    python scripts/make_response_matrix.py decision_letter.txt            # 輸出同名 .xlsx
    python scripts/make_response_matrix.py decision_letter.txt -o out.xlsx
    python scripts/make_response_matrix.py --demo [輸出資料夾]             # 用內建合成信實跑

輸入格式（純文字，UTF-8）：
    - 審稿人區段以獨立一行標示，如 "Reviewer 1"、"Reviewer #2:"、"Referee B"、
      "Associate Editor"、"審查人一"、"審查委員（二）"、"主編"。
    - 區段內有編號（1. / 1) / (1) / Comment 1 / 第1點 / 一、）就依編號切；
      沒有編號就依空行分段切。
    - "Major comments" / "Minor comments" 這類子標題會記進「來源區段」欄。

紀律：不改寫任何意見文字（摘錄只做截斷）；不判斷同意度；不產生回覆。
依賴：openpyxl（pip install openpyxl）。
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:  # pragma: no cover
    sys.exit("缺少 openpyxl：請先執行 pip install openpyxl")

# ──────────────────────────────────────────────────────────────────────────
# 1. 區段標頭（審稿人／編輯）偵測
# ──────────────────────────────────────────────────────────────────────────
_CJK_NUM = "一二三四五六七八九十０-９0-9ABCabc甲乙丙丁"
REVIEWER_HEADER_PATTERNS = [
    re.compile(r"^\s*(reviewer|referee)\s*(?:#|no\.?|number)?\s*([0-9]{1,2}|[A-Z])\b", re.I),
    re.compile(r"^\s*(associate\s+editor|handling\s+editor|guest\s+editor|editor(?:-in-chief)?|"
               r"co-?editor|\bAE\b)", re.I),
    re.compile(rf"^\s*(審查(?:人|委員|者)|評審(?:人|委員)?)\s*[（(]?\s*([{_CJK_NUM}]{{1,3}})\s*[）)]?", re.I),
    re.compile(r"^\s*(主編|副主編|編輯|編委|責任編輯|領域主編)\s*[:：]?"),
]
SUBSECTION_PATTERN = re.compile(
    r"^\s*(?:\*\*)?(major|minor|general|specific|other|additional|主要|次要|一般|其他|細部)"
    r"\s*(?:comments?|issues?|points?|concerns?|remarks?|意見|問題|建議)?\s*[:：]?\s*(?:\*\*)?\s*$",
    re.I,
)
SUBSECTION_LABEL = {
    "major": "Major", "主要": "Major",
    "minor": "Minor", "次要": "Minor", "細部": "Minor",
    "general": "General", "一般": "General",
    "specific": "Specific", "other": "Other", "additional": "Other", "其他": "Other",
}


def _is_header_line(line: str) -> str | None:
    """回傳正規化後的區段名稱；不是標頭就回 None。

    防呆：標頭必須短（≤80 字元、≤10 個英文字），且不以句號結尾——
    否則編輯信裡 "Reviewer 2 raised an important point." 這種句子會被誤判成標頭。
    """
    s = line.strip().strip("*_#").strip()
    if not s or len(s) > 80 or len(s.split()) > 10:
        return None
    if s.endswith((".", "。")):
        return None
    for pat in REVIEWER_HEADER_PATTERNS:
        m = pat.match(s)
        if m:
            role = m.group(1).strip()
            num = m.group(2).strip() if m.lastindex and m.lastindex >= 2 and m.group(2) else ""
            role_l = role.lower()
            if role_l.startswith(("reviewer", "referee")):
                return f"Reviewer {num}" if num else "Reviewer"
            if role_l in {"associate editor", "handling editor", "guest editor", "ae"}:
                return "Associate Editor"
            if role_l.startswith(("editor", "co-editor", "coeditor")):
                return "Editor"
            if role.startswith(("審查", "評審")):
                return f"審查人{num}" if num else "審查人"
            return "編輯"
    return None


# ──────────────────────────────────────────────────────────────────────────
# 2. 區段內逐則切分
# ──────────────────────────────────────────────────────────────────────────
ITEM_MARKER = re.compile(
    r"^\s*(?:"
    r"\(?\d{1,2}[\.\)、]\s+"                 # 1.  1)  1、
    r"|\(\d{1,2}\)\s*"                      # (1)
    r"|\d{1,2}\s*[-–:]\s+"                  # 1 -  1:
    r"|(?:comment|point|issue|concern)\s*#?\s*\d{1,2}\s*[:.\-–)]?\s*"  # Comment 1:
    r"|第\s*[0-9一二三四五六七八九十]{1,3}\s*[點項條]\s*[:：、]?\s*"        # 第1點
    r"|[一二三四五六七八九十]{1,3}、\s*"      # 一、
    r"|[（(][0-9一二三四五六七八九十]{1,3}[)）]\s*"   # （一）
    r"|[•·\-\*]\s+"                          # bullet
    r")",
    re.I,
)


def _split_numbered(lines: list[str]) -> list[str]:
    items: list[list[str]] = []
    for ln in lines:
        if ITEM_MARKER.match(ln) and ln.strip():
            items.append([ITEM_MARKER.sub("", ln, count=1).rstrip()])
        elif items:
            items[-1].append(ln.rstrip())
        elif ln.strip():
            items.append([ln.rstrip()])  # 編號前的前言，保留成第 0 則
    return ["\n".join(x).strip() for x in items if "\n".join(x).strip()]


def _split_paragraphs(lines: list[str], min_chars: int = 40) -> list[str]:
    paras: list[str] = []
    buf: list[str] = []
    for ln in lines + [""]:
        if ln.strip():
            buf.append(ln.rstrip())
        elif buf:
            paras.append("\n".join(buf).strip())
            buf = []
    # 太短的段落（客套話、單行小標）併入下一段
    merged: list[str] = []
    for p in paras:
        if merged and len(merged[-1]) < min_chars:
            merged[-1] = merged[-1] + "\n" + p
        else:
            merged.append(p)
    return [p for p in merged if p]


def split_letter(text: str) -> list[dict]:
    """回傳 [{reviewer, section, idx, text}, ...]。"""
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # 依標頭切成區段；標頭前的內容歸「Editor」
    sections: list[tuple[str, list[str]]] = [("Editor", [])]
    for ln in lines:
        name = _is_header_line(ln)
        if name:
            sections.append((name, []))
        else:
            sections[-1][1].append(ln)

    # 若第一段（Editor）是空的就丟掉；同名區段（例如 "Reviewer 1" 出現兩次）保留順序
    records: list[dict] = []
    counters: Counter = Counter()
    for name, body in sections:
        if not "".join(body).strip():
            continue
        # 子區段（Major / Minor）
        chunks: list[tuple[str, list[str]]] = [("", [])]
        for ln in body:
            m = SUBSECTION_PATTERN.match(ln)
            if m:
                chunks.append((SUBSECTION_LABEL.get(m.group(1).lower(), m.group(1)), []))
            else:
                chunks[-1][1].append(ln)
        for label, clines in chunks:
            if not "".join(clines).strip():
                continue
            n_markers = sum(1 for ln in clines if ITEM_MARKER.match(ln) and ln.strip())
            items = _split_numbered(clines) if n_markers >= 2 else _split_paragraphs(clines)
            for it in items:
                counters[name] += 1
                records.append({
                    "reviewer": name,
                    "section": label or "—",
                    "idx": counters[name],
                    "text": it,
                })
    return records


# ──────────────────────────────────────────────────────────────────────────
# 3. 類型／主題／工作量的關鍵字啟發式（只給建議值）
# ──────────────────────────────────────────────────────────────────────────
TYPE_RULES: list[tuple[str, str, list[str]]] = [
    # (類型, 工作量預估, 關鍵字)
    ("方法補做", "天級", [
        "endogen", "identif", "instrument", "iv ", "2sls", "did", "difference-in-diff",
        "parallel trend", "pre-trend", "placebo", "robust", "sensitivity", "heckman",
        "matching", "propensity", "cluster", "standard error", "fixed effect", "staggered",
        "sample", "subsample", "winsor", "specification", "estimator", "control variable",
        "economic significance", "economic magnitude", "effect size", "mechanism", "mediation",
        "moderat", "interaction", "heterogene", "re-estimate", "reestimate", "additional analysis",
        "內生", "識別", "工具變數", "平行趨勢", "安慰劑", "穩健", "敏感度", "配對", "傾向分數",
        "叢集", "標準誤", "固定效果", "交錯", "樣本", "設定", "估計", "控制變數", "經濟顯著",
        "經濟意義", "效果量", "機制", "中介", "調節", "交互", "異質", "重新估計", "補做",
    ]),
    ("理論重構", "天級", [
        "theor", "contribution", "framing", "motivat", "hypothes", "conceptual", "novel",
        "incremental", "so what", "boundary condition", "generaliz", "why taiwan", "context",
        "argument", "logic",
        "理論", "貢獻", "定位", "動機", "假說", "概念", "新意", "增量", "邊界條件", "推廣",
        "情境", "論證", "邏輯",
    ]),
    ("文獻補充", "小時級", [
        "cite", "citation", "literature", "reference", "prior work", "prior studies",
        "recent work", "omit", "overlook", "missing", "should discuss",
        "引用", "文獻", "參考", "先前研究", "近年研究", "遺漏", "忽略", "未討論",
    ]),
    ("寫作調整", "小時級", [
        "clarity", "clarif", "unclear", "confus", "typo", "grammar", "wording", "writing",
        "readab", "concise", "shorten", "length", "table", "figure", "format", "label",
        "abstract", "title", "structure", "organization", "section", "paragraph",
        "清楚", "澄清", "不清", "錯字", "文法", "措辭", "寫作", "可讀", "精簡", "篇幅",
        "表格", "圖", "格式", "標題", "摘要", "結構", "段落", "章節",
    ]),
]
TOPIC_RULES: list[tuple[str, list[str]]] = [
    ("識別/內生性", ["endogen", "identif", "instrument", "parallel", "pre-trend", "did", "causal",
                     "reverse caus", "omitted", "內生", "識別", "平行", "因果", "反向", "遺漏變數"]),
    ("穩健性", ["robust", "placebo", "sensitivity", "alternative", "winsor", "subsample",
                "穩健", "安慰劑", "敏感", "替代", "子樣本"]),
    ("經濟量級", ["economic significance", "economic magnitude", "effect size", "magnitude",
                  "practical", "經濟顯著", "經濟意義", "效果量", "量級", "實質"]),
    ("理論/貢獻", ["theor", "contribution", "hypothes", "framing", "novel", "理論", "貢獻", "假說", "定位"]),
    ("情境/推廣", ["taiwan", "generaliz", "single country", "context", "institutional",
                   "台灣", "推廣", "單一國家", "情境", "制度"]),
    ("樣本/資料", ["sample", "data", "tej", "period", "observation", "missing", "survivor",
                   "樣本", "資料", "期間", "觀察值", "遺漏值", "存活"]),
    ("衡量", ["measure", "proxy", "operationaliz", "definition", "variable",
              "衡量", "代理", "操作化", "定義", "變數"]),
    ("機制", ["mechanism", "channel", "mediat", "moderat", "heterogene", "機制", "管道", "中介", "調節", "異質"]),
    ("文獻", ["cite", "literature", "reference", "文獻", "引用"]),
    ("寫作/呈現", ["clarity", "unclear", "typo", "table", "figure", "writing", "abstract",
                   "清楚", "不清", "錯字", "表", "圖", "寫作", "摘要"]),
]


# 權重 2 的強關鍵字：同分時讓「一看就知道」的類型勝出（例：hard to follow → 寫作調整）
STRONG_KEYWORDS: dict[str, list[str]] = {
    "方法補做": ["identification", "parallel trend", "pre-trend", "robust", "endogen", "instrument",
                 "estimator", "識別", "平行趨勢", "穩健", "內生", "工具變數", "估計量"],
    "理論重構": ["theoretical contribution", "contribution", "hypothes", "boundary condition",
                 "理論貢獻", "貢獻", "假說", "邊界條件"],
    "文獻補充": ["not cited", "cite", "literature", "未引用", "引用", "文獻"],
    "寫作調整": ["hard to follow", "difficult to follow", "writing", "typo", "wording", "readab",
                 "難以理解", "寫作", "錯字", "措辭", "可讀"],
}
METADATA_LINE = re.compile(
    r"^\s*(manuscript\s*(id|no\.?|number)?|ms\.?\s*(id|no\.?)?|title|ref\.?|re|subject|date|"
    r"稿件編號|稿號|題目|標題|主旨|日期)\s*[:：]", re.I)


def is_metadata(text: str) -> bool:
    """整段都是信頭欄位（Manuscript ID: / Title: …）→ 不是意見。"""
    lines = [ln for ln in text.split("\n") if ln.strip()]
    return bool(lines) and all(METADATA_LINE.match(ln) for ln in lines)


def classify(text: str) -> tuple[str, str, str]:
    """回傳 (類型建議, 主題標籤, 工作量預估)；信頭段落回 ("—", "—", "—")。"""
    if is_metadata(text):
        return "—", "—", "—"
    t = text.lower()
    scores = {}
    for name, effort, kws in TYPE_RULES:
        s = sum(1 for k in kws if k in t) + sum(1 for k in STRONG_KEYWORDS.get(name, ()) if k in t)
        scores[name] = (s, effort)
    best = max(scores.items(), key=lambda kv: kv[1][0])
    if best[1][0] == 0:
        ctype, effort = "待判", "—"
    else:
        ctype, effort = best[0], best[1][1]
        # 方法補做且含「補跑／新增分析」字眼 → 升為週級
        if ctype == "方法補做" and any(k in t for k in
                                     ("re-estimate", "reestimate", "additional analysis", "new analysis",
                                      "collect", "hand-collect", "重新估計", "補做", "新增分析", "蒐集")):
            effort = "週級"
    topics = [name for name, kws in TOPIC_RULES if any(k in t for k in kws)]
    return ctype, "、".join(topics) if topics else "—", effort


GAP_RULES: list[tuple[str, list[str]]] = [
    ("落差1 情境複製", ["why taiwan", "generaliz", "single country", "single-country", "replicat",
                       "beyond the context", "beyond taiwan", "boundary condition", "institutional setting",
                       "推廣", "單一國家", "情境複製", "台灣情境", "為何是台灣", "邊界條件"]),
    ("落差2 平行趨勢", ["parallel trend", "pre-trend", "pretrend", "pre-period", "event study", "event-study",
                       "honest", "sensitivity to violation", "control group", "counterfactual", "staggered",
                       "two-way fixed", "twfe", "平行趨勢", "前期係數", "事件研究", "誠實區間", "控制組",
                       "反事實", "交錯"]),
    ("落差3 經濟量級", ["economic significance", "economic magnitude", "economically", "effect size",
                       "magnitude", "benchmark", "practical significance", "statistically significant but",
                       "經濟顯著", "經濟意義", "效果量", "量級", "基準", "實質意義"]),
]


def map_gaps(text: str) -> str:
    """回傳命中的落差標籤（可多個），沒命中回「—」。"""
    t = text.lower()
    hits = [name for name, kws in GAP_RULES if any(k in t for k in kws)]
    return "、".join(hits) if hits else "—"


def excerpt(text: str, n: int = 160) -> str:
    one = re.sub(r"\s+", " ", text).strip()
    return one if len(one) <= n else one[: n - 1] + "…"


# ──────────────────────────────────────────────────────────────────────────
# 4. 寫 xlsx
# ──────────────────────────────────────────────────────────────────────────
_CJK_DIGIT = {c: str(i + 1) for i, c in enumerate("一二三四五六七八九")}
_CJK_DIGIT.update({"十": "10", "甲": "1", "乙": "2", "丙": "3", "丁": "4"})
_CJK_DIGIT.update({chr(0xFF10 + i): str(i) for i in range(10)})  # 全形數字


def _code_prefix(reviewer: str) -> str:
    """Reviewer 2 → R2；審查人三 → R3；Editor／Associate Editor／編輯 → E；其餘照抄。"""
    low = reviewer.lower()
    if low.startswith(("reviewer", "referee")):
        tail = reviewer.split()[-1] if " " in reviewer else ""
        return f"R{tail}" if tail else "R"
    if reviewer in ("Editor", "Associate Editor", "編輯"):
        return "E"
    if reviewer.startswith("審查人"):
        tail = reviewer[len("審查人"):]
        return ("R" + "".join(_CJK_DIGIT.get(ch, ch) for ch in tail)) if tail else "R"
    return reviewer


HEADERS = ["審稿人", "編號", "來源區段", "意見摘錄", "意見全文", "類型(建議)", "主題標籤",
           "落差對應(建議)", "同意度", "處理策略", "修改位置", "狀態", "工作量(預估)", "備註"]
WIDTHS = [16, 8, 10, 48, 60, 12, 22, 18, 12, 30, 22, 10, 12, 24]


def write_xlsx(records: list[dict], out: Path, source_name: str) -> int:
    wb = Workbook()
    ws = wb.active
    ws.title = "分診表"
    ws.append(HEADERS)
    for c in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="DDDDDD")
        cell.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(c)].width = WIDTHS[c - 1]

    for r in records:
        ctype, topics, effort = classify(r["text"])
        section = "信頭" if ctype == "—" else r["section"]
        status = "—" if ctype == "—" else "待處理"
        gaps = "—" if ctype == "—" else map_gaps(r["text"])
        ws.append([
            r["reviewer"], f"{_code_prefix(r['reviewer'])}.{r['idx']}", section,
            excerpt(r["text"]), r["text"], ctype, topics, gaps,
            "", "", "", status, effort, "",
        ])
    n = len(records)
    for row in ws.iter_rows(min_row=2, max_row=n + 1):
        for cell in row:
            cell.alignment = Alignment(vertical="top", wrap_text=True)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(HEADERS))}{max(n + 1, 2)}"

    if n:
        dvs = {
            "F": '"方法補做,理論重構,文獻補充,寫作調整,誤解澄清,品味偏好,待判"',
            "I": '"全盤接受,部分接受,有理由不改"',
            "L": '"待處理,進行中,已修改,已回覆"',
            "M": '"小時級,天級,週級,—"',
        }
        for col, formula in dvs.items():
            dv = DataValidation(type="list", formula1=formula, allow_blank=True)
            ws.add_data_validation(dv)
            dv.add(f"{col}2:{col}{n + 1}")

    # 統計工作表
    st = wb.create_sheet("統計")
    st.append(["審稿人", "意見數", "方法補做", "理論重構", "文獻補充", "寫作調整", "待判"])
    by_rev: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        ct = classify(r["text"])[0]
        if ct != "—":  # 信頭段落不計入
            by_rev[r["reviewer"]][ct] += 1
    for rev, cnt in by_rev.items():
        st.append([rev, sum(cnt.values()), cnt["方法補做"], cnt["理論重構"], cnt["文獻補充"],
                   cnt["寫作調整"], cnt["待判"]])
    st.append([])
    st.append(["主題標籤", "命中則數", "涉及的審稿人（≥2 位＝優先檢查是否互相矛盾）"])
    topic_hits: dict[str, set] = defaultdict(set)
    topic_cnt: Counter = Counter()
    for r in records:
        for tp in classify(r["text"])[1].split("、"):
            if tp != "—":
                topic_hits[tp].add(r["reviewer"])
                topic_cnt[tp] += 1
    for tp, c in topic_cnt.most_common():
        st.append([tp, c, "、".join(sorted(topic_hits[tp]))])
    st.append([])
    st.append(["台灣稿件三落差", "命中則數", "提到的審稿人（≥2 位＝本輪主戰場）"])
    gap_hits: dict[str, set] = defaultdict(set)
    gap_cnt: Counter = Counter()
    for r in records:
        if classify(r["text"])[0] == "—":
            continue
        for g in map_gaps(r["text"]).split("、"):
            if g != "—":
                gap_hits[g].add(r["reviewer"])
                gap_cnt[g] += 1
    for g, _ in GAP_RULES:
        st.append([g, gap_cnt.get(g, 0), "、".join(sorted(gap_hits.get(g, set()))) or "—"])
    for c, w in zip("ABCDEFG", (16, 10, 12, 12, 12, 12, 40)):
        st.column_dimensions[c].width = w

    # 說明工作表
    hp = wb.create_sheet("說明")
    for line in [
        f"來源檔：{source_name}",
        "本表由 make_response_matrix.py 依關鍵字切分與標記，「類型」「主題標籤」「工作量」皆為建議值，逐列人工確認。",
        "「同意度」「處理策略」「修改位置」由使用者填；「狀態」全部變成「已回覆」才可出信（SKILL.md Step 4）。",
        "紀律：每則意見都要回；「有理由不改」全信 ≤ 2 處；矛盾意見先看「統計」表的主題交叉，再依",
        "references/rr-conventions-top-journals.md 第三節處理。",
        "切分若有誤（一則被切成兩則、或兩則黏在一起），直接在本表合併或拆列，不必回頭改信。",
        "",
        "台灣稿件常見落差→對策：「落差對應(建議)」欄標出的意見優先處理。",
        "  落差1 情境複製 → 稿件：制度特徵→理論構念表＋可移植性聲明；回覆句式見 rr-conventions 第八節。",
        "  落差2 平行趨勢 → 稿件：前期聯合檢定＋Roth (2022) 檢定力＋Rambachan & Roth (2023) 誠實區間表；",
        "                   模板見 causal-inference-architect/references/robustness-battery.md 第七節。",
        "  落差3 經濟量級 → 稿件：主表後經濟量級段＋基準表；模板見 q1-journal-reviewer/references/top-journal-standards.md 第五節。",
    ]:
        hp.append([line])
    hp.column_dimensions["A"].width = 110

    out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(out)
    return n


# ──────────────────────────────────────────────────────────────────────────
# 5. 合成測試信（純虛構：期刊、稿號、審稿人皆為佔位）
# ──────────────────────────────────────────────────────────────────────────
DEMO_LETTER = """\
Manuscript ID: JPS-0000-DEMO
Title: Family Control, Mandatory Disclosure, and Firm Value (synthetic test letter)

Dear Authors,

Thank you for submitting your manuscript to the Journal of Placeholder Studies. Two reviewers
and I have read the paper. The reviewers see potential but raise substantial concerns about
identification and about the contribution beyond the Taiwanese setting. I invite a major
revision. Please pay particular attention to Reviewer 2's points on parallel trends and to
Reviewer 1's request for economic magnitudes; both are essential for a positive outcome.

Associate Editor

Reviewer 1

Major comments

1. The paper relies on a difference-in-differences design around the disclosure mandate, but
   the identification strategy is only described in the appendix. Please move it to the main
   text and state the source of variation, the control group, and the key assumption.
2. All results are reported as statistically significant, yet the economic magnitude is never
   discussed. With roughly 18,000 firm-years, significance is unsurprising. Please report the
   effect of a one-standard-deviation change in the treatment intensity relative to the sample
   mean, and benchmark it against prior estimates from other markets.
3. The theoretical contribution reads as a replication in Taiwan of well-known findings. What do
   we learn beyond the context? Consider framing the institutional feature as a boundary
   condition rather than as background.

Minor comments

4. Table 3 reports coefficients to five decimal places; three would suffice. Variable names
   such as "FAMD" and "TQ" should be spelled out.
5. Several recent papers on staggered adoption are not cited; the literature review would
   benefit from engaging with them.

Reviewer 2

The empirical design is the main issue. The event-study figure in the appendix shows pre-period
coefficients that are individually insignificant, but the test is likely underpowered given the
small number of treated cohorts. The authors should report a joint test, discuss the power of
the pre-trend test, and present sensitivity of the estimate to violations of parallel trends
using honest confidence intervals.

Relatedly, treatment timing varies across firms because the mandate applied to firms above a
capital threshold in different years. A two-way fixed effects estimator can be biased in this
setting. Please report a heterogeneity-robust estimator and a decomposition of the TWFE weights.

I also found the writing in Section 2 hard to follow; the institutional background mixes the
history of the regulation with the theoretical argument. Separating the two would help.

審查人三

一、作者宣稱家族控制透過「聲譽機制」影響揭露品質，但全文沒有任何直接檢驗機制的分析。
    建議至少以異質性分析（高／低控制權偏離）或中介分析佐證，否則機制只是故事。
二、樣本期間涵蓋會計準則轉換年度，請說明如何處理該年度的資料斷點，或提供剔除該年度
    的穩健性結果。
三、摘要第一句從「台灣家族企業比例高」起手，讀來像情境研究；建議改以理論張力開場。
"""


def run_demo(out_dir: Path) -> tuple[Path, Path, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    letter = out_dir / "demo_decision_letter.txt"
    letter.write_text(DEMO_LETTER, encoding="utf-8")
    xlsx = out_dir / "demo_response_matrix.xlsx"
    n = write_xlsx(split_letter(DEMO_LETTER), xlsx, letter.name)
    return letter, xlsx, n


# ──────────────────────────────────────────────────────────────────────────
# 6. CLI
# ──────────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="decision letter → R&R 分診表 xlsx")
    ap.add_argument("letter", nargs="?", help="純文字 decision letter（UTF-8）")
    ap.add_argument("-o", "--out", help="輸出 xlsx 路徑（預設：與輸入同名 .xlsx）")
    ap.add_argument("--demo", nargs="?", const="", default=None, metavar="DIR",
                    help="用內建合成測試信實跑，產出 demo_decision_letter.txt 與 demo_response_matrix.xlsx"
                         "（不給 DIR 時預設 ./output/，M4 修復：不直接寫 cwd）")
    args = ap.parse_args(argv)

    if args.demo is not None:
        demo_dir = args.demo or "output"
        if not args.demo:
            print(f"[提醒] --demo 未指定 DIR，預設輸出到 ./{demo_dir}/", file=sys.stderr)
        letter, xlsx, n = run_demo(Path(demo_dir))
        print(f"[demo] 合成信：{letter}")
        print(f"[demo] 分診表：{xlsx}（{n} 則意見）")
        return 0

    if not args.letter:
        ap.print_help()
        return 2
    src = Path(args.letter)
    if not src.is_file():
        print(f"找不到檔案：{src}")
        return 1
    raw = src.read_bytes()
    text = raw.decode("utf-8", errors="replace")
    if "�" in text:
        # L1 修復(2026-09-20)：errors="replace" 會把非 UTF-8 信件(常見於 Word 另存
        # 或舊系統匯出的 Big5/cp950)無聲變成 U+FFFD 亂碼列，切分與內容都會壞掉但
        # 不會報錯——使用者可能直接拿著亂碼分診表去用。改用警告 + 嘗試 cp950 復原。
        print("[警告] 以 UTF-8 解碼出現 U+FFFD(無法辨識字元)，此信件可能不是 UTF-8"
              "（常見於 Word 另存或舊系統匯出的 Big5/cp950）。嘗試改用 cp950 解碼…",
              file=sys.stderr)
        try:
            alt = raw.decode("cp950")
        except UnicodeDecodeError:
            alt = None
        if alt is not None and "�" not in alt:
            print("[提醒] cp950 解碼未再出現亂碼字元，已改用 cp950 結果；"
                  "仍請人工核對切分結果與原信件一致。", file=sys.stderr)
            text = alt
        else:
            print("[警告] cp950 解碼仍有亂碼或失敗，維持原 UTF-8(replace) 結果——"
                  "分診表可能含亂碼列，請人工確認來源編碼並考慮另存為 UTF-8 後重跑。",
                  file=sys.stderr)
    records = split_letter(text)
    if not records:
        print("切不出任何意見：請確認信件是純文字且含審稿人標頭（Reviewer 1／審查人一）。")
        return 1
    out = Path(args.out) if args.out else src.with_suffix(".xlsx")
    n = write_xlsx(records, out, src.name)
    per = Counter(r["reviewer"] for r in records)
    print(f"分診表：{out}（{n} 則意見）")
    for rev, c in per.items():
        print(f"  {rev}: {c} 則")
    print("提醒：類型／主題／工作量為建議值，逐列人工確認；同意度與處理策略留給你填。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
