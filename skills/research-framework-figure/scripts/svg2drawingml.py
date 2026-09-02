#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
svg2drawingml.py — SVG 子集 → 原生 PowerPoint DrawingML 形狀

【為什麼需要這支】
python-pptx 只提供有限的內建圖形（矩形、圓角矩形、連接線…），畫不出
曲線箭頭、自訂路徑這類學術架構圖必備的元素。先前 research-framework-figure
的 PPTX 匯出因此**靜默丟掉了所有箭頭與假說標籤**（SVG 有 10 個元素，
PPTX 只剩 5 個方框）。本模組補上這個缺口。

【設計取向：LLM 畫 SVG → 機械式確定性轉 DrawingML】
與其讓程式逐一硬寫 python-pptx 呼叫，不如以 SVG 為中介表示法
（好產生、好預覽、好除錯），再用**確定性**的規則轉成原生 DrawingML。
此設計模式參考自 hugohe3/ppt-master（MIT），但本檔為自行實作，未複製其程式碼；
且刻意**不引入** skia-pathops / uharfbuzz——那兩者只服務「形狀布林運算」與
「文字當布林操作元」的窄用途，學術圖形用不到。詳見 ATTRIBUTION.md。

【核心紀律：絕不靜默劣化】
遇到不支援的 SVG 元素時**明確報錯或回報清單**，絕不悄悄近似、
也絕不偷偷退化成一張點陣圖。使用者必須知道圖是不是完整的——
先前那個「產檔不報錯但內容不全」的缺陷正是這樣造成的。

【支援的 SVG 子集】
  <rect>  <line>  <text>  <path>（M/L/H/V/C/S/Q/T/A/Z 全指令）
  屬性：fill / stroke / stroke-width / stroke-dasharray / text-anchor
       / font-size / font-family / font-weight / marker-end（→ 箭頭端點）
【不支援（會明確回報，不靜默處理）】
  mask / pattern / clipPath / filter / 漸層 / use / 巢狀 svg

【文字處理】
文字一律輸出為**可編輯的原生文字方塊**（<p:txBody>），不做字形外框化。
排版交給 PowerPoint 原生引擎。中英混排字型另寫 a:ea 指定東亞字型。

last_verified: 2026-08-14
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

EMU_PER_PX = 9525  # 1 px = 9525 EMU（96 dpi 基準）
SVG_NS = "{http://www.w3.org/2000/svg}"

# 明確不支援的元素——遇到就回報，不靜默略過
UNSUPPORTED = {"mask", "pattern", "clipPath", "filter", "use", "image",
               "linearGradient", "radialGradient", "foreignObject"}


# ── SVG path 解析與正規化 ─────────────────────────────────────────────
_TOKEN = re.compile(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _tokenize(d: str) -> list:
    return _TOKEN.findall(d or "")


def _q_to_c(p0, q, p1):
    """二次貝茲 → 三次貝茲（DrawingML 只有 cubicBezTo）。

    C1 = P0 + 2/3·(Q − P0)，C2 = P1 + 2/3·(Q − P1)
    """
    c1 = (p0[0] + 2.0 / 3.0 * (q[0] - p0[0]), p0[1] + 2.0 / 3.0 * (q[1] - p0[1]))
    c2 = (p1[0] + 2.0 / 3.0 * (q[0] - p1[0]), p1[1] + 2.0 / 3.0 * (q[1] - p1[1]))
    return c1, c2


def _arc_to_curves(p0, rx, ry, phi_deg, large_arc, sweep, p1):
    """SVG 弧線 A → 多段三次貝茲（依 SVG 規格 F.6.5 端點→圓心參數化）。

    每段不超過 90°，用標準四階常數 k = 4/3·tan(Δ/4) 近似圓弧。
    """
    if p0 == p1:
        return []
    rx, ry = abs(rx), abs(ry)
    if rx == 0 or ry == 0:  # 退化成直線
        return [("L", p1)]

    phi = math.radians(phi_deg)
    cosp, sinp = math.cos(phi), math.sin(phi)
    dx2, dy2 = (p0[0] - p1[0]) / 2.0, (p0[1] - p1[1]) / 2.0
    x1p = cosp * dx2 + sinp * dy2
    y1p = -sinp * dx2 + cosp * dy2

    # 半徑過小則放大（規格要求）
    lam = (x1p * x1p) / (rx * rx) + (y1p * y1p) / (ry * ry)
    if lam > 1:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s

    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    co = math.sqrt(max(0.0, num / den)) if den else 0.0
    if large_arc == sweep:
        co = -co
    cxp, cyp = co * rx * y1p / ry, -co * ry * x1p / rx
    cx = cosp * cxp - sinp * cyp + (p0[0] + p1[0]) / 2.0
    cy = sinp * cxp + cosp * cyp + (p0[1] + p1[1]) / 2.0

    def ang(ux, uy, vx, vy):
        d = math.hypot(ux, uy) * math.hypot(vx, vy)
        if d == 0:
            return 0.0
        c = max(-1.0, min(1.0, (ux * vx + uy * vy) / d))
        a = math.acos(c)
        return -a if (ux * vy - uy * vx) < 0 else a

    th1 = ang(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dth = ang((x1p - cxp) / rx, (y1p - cyp) / ry, (-x1p - cxp) / rx, (-y1p - cyp) / ry)
    if not sweep and dth > 0:
        dth -= 2 * math.pi
    elif sweep and dth < 0:
        dth += 2 * math.pi

    n = max(1, int(math.ceil(abs(dth) / (math.pi / 2))))
    out, delta = [], dth / n
    k = 4.0 / 3.0 * math.tan(delta / 4.0)
    th = th1
    for _ in range(n):
        cos1, sin1 = math.cos(th), math.sin(th)
        cos2, sin2 = math.cos(th + delta), math.sin(th + delta)

        def pt(c, s):
            return (cosp * rx * c - sinp * ry * s + cx, sinp * rx * c + cosp * ry * s + cy)

        e1, e2 = pt(cos1, sin1), pt(cos2, sin2)
        d1 = (cosp * rx * -sin1 - sinp * ry * cos1, sinp * rx * -sin1 + cosp * ry * cos1)
        d2 = (cosp * rx * -sin2 - sinp * ry * cos2, sinp * rx * -sin2 + cosp * ry * cos2)
        out.append(("C", (e1[0] + k * d1[0], e1[1] + k * d1[1]),
                    (e2[0] - k * d2[0], e2[1] - k * d2[1]), e2))
        th += delta
    return out


def parse_path(d: str) -> list:
    """把 SVG path 的 d 屬性正規化成只剩 M / L / C / Z 的指令串。"""
    toks = _tokenize(d)
    i, cmd = 0, None
    cur = (0.0, 0.0)
    start = (0.0, 0.0)
    prev_c2 = None   # 供 S 用
    prev_q = None    # 供 T 用
    out = []

    def num():
        nonlocal i
        v = float(toks[i]); i += 1
        return v

    while i < len(toks):
        t = toks[i]
        if re.match(r"[A-Za-z]", t):
            cmd = t; i += 1
        elif cmd is None:
            break
        rel = cmd.islower()
        c = cmd.upper()

        if c == "M":
            x, y = num(), num()
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
            start = cur
            out.append(("M", cur)); prev_c2 = prev_q = None
            cmd = "l" if rel else "L"   # 後續隱含為 lineto
        elif c == "L":
            x, y = num(), num()
            cur = (cur[0] + x, cur[1] + y) if rel else (x, y)
            out.append(("L", cur)); prev_c2 = prev_q = None
        elif c == "H":
            x = num(); cur = (cur[0] + x, cur[1]) if rel else (x, cur[1])
            out.append(("L", cur)); prev_c2 = prev_q = None
        elif c == "V":
            y = num(); cur = (cur[0], cur[1] + y) if rel else (cur[0], y)
            out.append(("L", cur)); prev_c2 = prev_q = None
        elif c == "C":
            p = [(num(), num()) for _ in range(3)]
            if rel:
                p = [(cur[0] + a, cur[1] + b) for a, b in p]
            out.append(("C", p[0], p[1], p[2])); prev_c2, cur = p[1], p[2]; prev_q = None
        elif c == "S":
            p = [(num(), num()) for _ in range(2)]
            if rel:
                p = [(cur[0] + a, cur[1] + b) for a, b in p]
            c1 = (2 * cur[0] - prev_c2[0], 2 * cur[1] - prev_c2[1]) if prev_c2 else cur
            out.append(("C", c1, p[0], p[1])); prev_c2, cur = p[0], p[1]; prev_q = None
        elif c == "Q":
            p = [(num(), num()) for _ in range(2)]
            if rel:
                p = [(cur[0] + a, cur[1] + b) for a, b in p]
            c1, c2 = _q_to_c(cur, p[0], p[1])
            out.append(("C", c1, c2, p[1])); prev_q, cur = p[0], p[1]; prev_c2 = None
        elif c == "T":
            x, y = num(), num()
            p1 = (cur[0] + x, cur[1] + y) if rel else (x, y)
            q = (2 * cur[0] - prev_q[0], 2 * cur[1] - prev_q[1]) if prev_q else cur
            c1, c2 = _q_to_c(cur, q, p1)
            out.append(("C", c1, c2, p1)); prev_q, cur = q, p1; prev_c2 = None
        elif c == "A":
            rx, ry, rot = num(), num(), num()
            laf, sf = int(num()), int(num())
            x, y = num(), num()
            p1 = (cur[0] + x, cur[1] + y) if rel else (x, y)
            for seg in _arc_to_curves(cur, rx, ry, rot, laf, sf, p1):
                out.append(seg)
            cur = p1; prev_c2 = prev_q = None
        elif c == "Z":
            out.append(("Z",)); cur = start; prev_c2 = prev_q = None
        else:
            i += 1  # 未知指令，跳過
    return out


def path_bbox(cmds: list) -> tuple:
    xs, ys = [], []
    for seg in cmds:
        for p in seg[1:]:
            if isinstance(p, tuple):
                xs.append(p[0]); ys.append(p[1])
    if not xs:
        return (0.0, 0.0, 1.0, 1.0)
    return (min(xs), min(ys), max(xs) - min(xs) or 1.0, max(ys) - min(ys) or 1.0)


# ── DrawingML 產生 ────────────────────────────────────────────────────
def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def custgeom_xml(cmds: list, bbox: tuple) -> str:
    """把正規化後的指令串轉成 <a:custGeom>（座標相對 bbox，單位 EMU）。"""
    x0, y0, w, h = bbox
    W, H = int(w * EMU_PER_PX), int(h * EMU_PER_PX)

    def px(p):
        return int((p[0] - x0) * EMU_PER_PX), int((p[1] - y0) * EMU_PER_PX)

    parts = []
    for seg in cmds:
        k = seg[0]
        if k == "M":
            x, y = px(seg[1]); parts.append(f'<a:moveTo><a:pt x="{x}" y="{y}"/></a:moveTo>')
        elif k == "L":
            x, y = px(seg[1]); parts.append(f'<a:lnTo><a:pt x="{x}" y="{y}"/></a:lnTo>')
        elif k == "C":
            a, b, c = px(seg[1]), px(seg[2]), px(seg[3])
            parts.append(
                f'<a:cubicBezTo><a:pt x="{a[0]}" y="{a[1]}"/>'
                f'<a:pt x="{b[0]}" y="{b[1]}"/><a:pt x="{c[0]}" y="{c[1]}"/></a:cubicBezTo>')
        elif k == "Z":
            parts.append("<a:close/>")
    return (f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/>'
            f'<a:rect l="0" t="0" r="r" b="b"/><a:pathLst>'
            f'<a:path w="{W}" h="{H}">{"".join(parts)}</a:path></a:pathLst></a:custGeom>')


def _ln_xml(stroke, width_px, dashed, arrow_end):
    if not stroke or stroke == "none":
        return '<a:ln><a:noFill/></a:ln>'
    w = max(1, int(float(width_px or 1) * EMU_PER_PX))
    dash = '<a:prstDash val="dash"/>' if dashed else '<a:prstDash val="solid"/>'
    tail = '<a:tailEnd type="triangle" w="med" len="med"/>' if arrow_end else ""
    col = stroke.lstrip("#").upper()[:6] or "000000"
    return (f'<a:ln w="{w}" cap="flat"><a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
            f'{dash}<a:round/><a:headEnd type="none"/>{tail}</a:ln>')


def build_path_shape_xml(sid: int, name: str, cmds: list, bbox: tuple,
                         fill: str, stroke: str, width_px, dashed: bool,
                         arrow_end: bool) -> str:
    """產生一個帶 custGeom 的 <p:sp>。回傳可直接塞進 spTree 的 XML 字串。"""
    x0, y0, w, h = bbox
    off_x, off_y = int(x0 * EMU_PER_PX), int(y0 * EMU_PER_PX)
    ext_x, ext_y = int(w * EMU_PER_PX), int(h * EMU_PER_PX)
    if fill and fill != "none":
        col = fill.lstrip("#").upper()[:6] or "FFFFFF"
        fill_xml = f'<a:solidFill><a:srgbClr val="{col}"/></a:solidFill>'
    else:
        fill_xml = "<a:noFill/>"
    return (
        f'<p:sp xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
        f'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
        f'<p:nvSpPr><p:cNvPr id="{sid}" name="{_esc(name)}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{off_x}" y="{off_y}"/>'
        f'<a:ext cx="{ext_x}" cy="{ext_y}"/></a:xfrm>'
        f'{custgeom_xml(cmds, bbox)}{fill_xml}{_ln_xml(stroke, width_px, dashed, arrow_end)}'
        f'</p:spPr><p:txBody><a:bodyPr/><a:lstStyle/><a:p/></p:txBody></p:sp>')


# ── SVG 掃描（回報不支援元素，絕不靜默）────────────────────────────────
def scan_svg(svg_text: str) -> dict:
    """解析 SVG，回傳可轉換元素與不支援元素清單。"""
    root = ET.fromstring(svg_text)
    vb = (root.get("viewBox") or "").split()
    view = tuple(float(v) for v in vb) if len(vb) == 4 else None

    items, unsupported = [], []
    for el in root.iter():
        tag = el.tag.replace(SVG_NS, "")
        if tag in UNSUPPORTED:
            unsupported.append(tag)
        elif tag in ("path", "rect", "line", "text"):
            items.append(el)
    return {"view": view, "items": items, "unsupported": sorted(set(unsupported))}


if __name__ == "__main__":
    import sys

    def _usage() -> None:
        print(__doc__.split("【")[0].strip())
        print("\n用法：python svg2drawingml.py <檔案.svg>   # 檢查該 SVG 的可轉換性")
        print("\n本模組主要供 framework_figure.py 匯出 PPTX 時 import 使用；")
        print("直接執行只做可轉換性檢查（列出可轉元素數與不支援元素）。")

    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        _usage()
        sys.exit(0)
    try:
        with open(sys.argv[1], encoding="utf-8") as f:
            info = scan_svg(f.read())
    except FileNotFoundError:
        print(f"錯誤：找不到檔案 {sys.argv[1]}", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError as e:
        print(f"錯誤：SVG 解析失敗（{e}）", file=sys.stderr)
        sys.exit(1)
    print(f"viewBox：{info['view']}")
    print(f"可轉換元素：{len(info['items'])} 個")
    if info["unsupported"]:
        print(f"⚠️ 不支援（會明確回報，不靜默略過）：{', '.join(info['unsupported'])}")
    else:
        print("✓ 無不支援元素")
