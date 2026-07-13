#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_html_deck.py — slides_content.json → 自包含 HTML 簡報(引擎A:html-canvas)

用法:
    python build_html_deck.py slides_content.json -o deck.html

零第三方依賴(僅標準函式庫)。canvas 特效引擎自 ../assets/canvas-fx.js 內嵌。
鍵盤:←/→/空白鍵 換頁與逐步揭示;P 簡報者模式;Home/End 首尾頁。
"""
import argparse
import base64
import html
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):  # Windows 主控台中文輸出
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

FX_ALLOWED_LAYOUTS = {"cover", "section_divider", "closing"}
PAGE_W_IN, PAGE_H_IN = 13.333, 7.5  # 16:9;4:3 時改 10 x 7.5

EFFECT_CLASS = {
    "appear": "fx-appear",
    "fade-in": "fx-fade",
    "wipe": "fx-wipe",
    "fly-in-from-bottom": "fx-fly-bottom",
    "fly-in-from-left": "fx-fly-left",
    "fly-in-from-right": "fx-fly-right",
}


def esc(s):
    return html.escape(str(s if s is not None else ""))


def load_spec(path):
    with open(path, encoding="utf-8") as f:
        spec = json.load(f)
    for key in ("metadata", "global_settings", "slides"):
        if key not in spec:
            sys.exit(f"[錯誤] slides_content.json 缺少頂層欄位 {key}")
    return spec


def theme(spec):
    tc = spec["global_settings"].get("theme_color", {})
    return {
        "primary": tc.get("primary", "#0F172A"),
        "secondary": tc.get("secondary", "#38BDF8"),
        "accent": tc.get("accent", "#F59E0B"),
        "font_ea": spec["global_settings"].get("font_family_east_asian", "Microsoft JhengHei"),
        "font_latin": spec["global_settings"].get("font_family_latin", "Calibri"),
    }


def anim_attrs(anim):
    """元素級 animation dict → data-step 與效果 class。無 animation → 直接顯示。"""
    if not anim or "entry_order" not in anim:
        return "", ""
    cls = EFFECT_CLASS.get(anim.get("effect", "fade-in"), "fx-fade")
    dur = int(anim.get("duration_ms", 500))
    delay = int(anim.get("delay_ms", 0))
    style = f"--dur:{dur}ms;--delay:{delay}ms"
    return f' data-step="{int(anim["entry_order"])}" style="{style}"', f" step {cls}"


def bg_style(bg, default):
    if not bg:
        return f"background:{default}"
    if bg.get("type") == "gradient":
        c = bg.get("colors", [default, default])
        return f"background:linear-gradient(135deg,{c[0]},{c[-1]})"
    return f"background:{bg.get('color', default)}"


# ---------- 各版型 → 內頁 HTML ----------

def render_cover(sl, th):
    c = sl["content"]
    return (
        f'<div class="cover-box">'
        f'<h1>{esc(c.get("headline"))}</h1>'
        f'<p class="sub">{esc(c.get("sub_headline"))}</p>'
        f"</div>"
    )


def render_section(sl, th):
    c = sl["content"]
    num = esc(c.get("section_number", ""))
    return (
        f'<div class="cover-box">'
        f'<div class="secnum">{num}</div>'
        f'<h1>{esc(c.get("headline"))}</h1>'
        f"</div>"
    )


def render_closing(sl, th):
    c = sl["content"]
    contact = esc(c.get("contact", ""))
    line = f'<p class="sub">{contact}</p>' if contact else ""
    return f'<div class="cover-box"><h1>{esc(c.get("headline"))}</h1>{line}</div>'


def render_bullets_list(bullets):
    out = ["<ul class='bullets'>"]
    for b in bullets:
        anim = None
        if b.get("animation_step") is not None:
            anim = {"entry_order": b["animation_step"], "effect": "fade-in"}
        attrs, cls = anim_attrs(anim)
        lv = " lv1" if b.get("level", 0) >= 1 else ""
        out.append(f'<li class="b{lv}{cls}"{attrs}>{esc(b.get("text"))}</li>')
    out.append("</ul>")
    return "".join(out)


def render_bullet_points(sl, th):
    return f'<h2>{esc(sl.get("title"))}</h2>' + render_bullets_list(sl["content"].get("bullets", []))


def render_two_column(sl, th):
    c = sl["content"]
    cols = []
    for side in ("left", "right"):
        col = c.get(side, {})
        cols.append(
            f'<div class="col"><h3>{esc(col.get("heading"))}</h3>'
            + render_bullets_list(col.get("bullets", []))
            + "</div>"
        )
    return f'<h2>{esc(sl.get("title"))}</h2><div class="twocol">{"".join(cols)}</div>'


def render_figure(sl, th, json_dir):
    c = sl["content"]
    p = json_dir / c.get("image_path", "")
    if p.is_file():
        mime = "image/png" if p.suffix.lower() == ".png" else "image/jpeg"
        if p.suffix.lower() == ".svg":
            mime = "image/svg+xml"
        data = base64.b64encode(p.read_bytes()).decode()
        img = f'<img src="data:{mime};base64,{data}" alt="{esc(c.get("caption"))}">'
    else:
        img = f'<div class="img-missing">[圖檔未找到:{esc(c.get("image_path"))}]</div>'
    cap = f'<p class="caption">{esc(c.get("caption"))}</p>' if c.get("caption") else ""
    return f'<h2>{esc(sl.get("title"))}</h2><div class="figwrap">{img}{cap}</div>'


def render_architecture(sl, th):
    c = sl["content"]
    parts = [f'<h2>{esc(sl.get("title"))}</h2>', '<div class="arch">']
    nodes = {}
    for el in c.get("elements", []):
        pos = el.get("position", {})
        x, y = float(pos.get("x", 0)), float(pos.get("y", 0))
        w, h = float(pos.get("w", 2)), float(pos.get("h", 1))
        nodes[el.get("id")] = (x, y, w, h)
        st = el.get("style", {})
        fill = st.get("fill", th["secondary"])
        color = st.get("color", "#FFFFFF")
        fsize = st.get("font_size", 18)
        attrs, cls = anim_attrs(el.get("animation"))
        box_cls = "node" if el.get("type", "shape_box") == "shape_box" else "labelbox"
        style = (
            f"left:{x / PAGE_W_IN * 100:.2f}%;top:{y / PAGE_H_IN * 100:.2f}%;"
            f"width:{w / PAGE_W_IN * 100:.2f}%;height:{h / PAGE_H_IN * 100:.2f}%;"
            f"background:{fill if box_cls == 'node' else 'transparent'};"
            f"color:{color};font-size:{fsize}px;"
        )
        merged = attrs.replace('style="', f'style="{style}', 1) if 'style="' in attrs else f' style="{style}"'
        parts.append(f'<div class="{box_cls}{cls}"{merged}>{esc(el.get("text"))}</div>')
    # 連接線:以 SVG overlay 畫箭頭
    svg = [f'<svg class="lines" viewBox="0 0 {PAGE_W_IN * 100:.0f} {PAGE_H_IN * 100:.0f}" preserveAspectRatio="none">',
           f'<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
           f'<path d="M0,0 L6,3 L0,6 z" fill="{th["secondary"]}"/></marker></defs>']
    for cn in c.get("connections", []):
        a, b = nodes.get(cn.get("from")), nodes.get(cn.get("to"))
        if not a or not b:
            continue
        ax, ay = (a[0] + a[2]) * 100, (a[1] + a[3] / 2) * 100  # from 右緣中點
        bx, by = b[0] * 100, (b[1] + b[3] / 2) * 100            # to 左緣中點
        if bx < ax:  # 反向時改用垂直邊
            ax, ay = (a[0] + a[2] / 2) * 100, (a[1] + a[3]) * 100
            bx, by = (b[0] + b[2] / 2) * 100, b[1] * 100
        anim = cn.get("animation") or {}
        if anim.get("timeline_flow"):  # v1.0 相容
            anim.setdefault("effect", "wipe")
        attrs, cls = anim_attrs(anim if anim.get("entry_order") else None)
        if cn.get("type") == "elbow":
            mx = (ax + bx) / 2
            d = f"M{ax:.0f},{ay:.0f} L{mx:.0f},{ay:.0f} L{mx:.0f},{by:.0f} L{bx:.0f},{by:.0f}"
        else:
            d = f"M{ax:.0f},{ay:.0f} L{bx:.0f},{by:.0f}"
        svg.append(f'<g class="conn{cls}"{attrs}><path d="{d}" stroke="{th["secondary"]}" '
                   f'stroke-width="2.5" fill="none" marker-end="url(#arr)"/>')
        if cn.get("label"):
            svg.append(f'<text x="{(ax + bx) / 2:.0f}" y="{(ay + by) / 2 - 8:.0f}" '
                       f'fill="{th["primary"]}" font-size="20" text-anchor="middle">{esc(cn["label"])}</text>')
        svg.append("</g>")
    svg.append("</svg>")
    parts.append("".join(svg))
    parts.append("</div>")
    return "".join(parts)


RENDERERS = {
    "cover": render_cover,
    "section_divider": render_section,
    "closing": render_closing,
    "bullet_points": render_bullet_points,
    "two_column": render_two_column,
    "architecture_chart": render_architecture,
}


def build(spec, json_dir, fxjs):
    th = theme(spec)
    slides_html, notes, skipped, warns = [], [], [], []
    for sl in sorted(spec["slides"], key=lambda s: s.get("slide_id", 0)):
        eng = sl.get("engine_config", {})
        if eng.get("engine", "html-canvas") != "html-canvas":
            skipped.append(sl.get("slide_id"))
            continue
        layout = sl.get("layout", "bullet_points")
        fx = eng.get("fx", "none")
        if fx and fx != "none" and layout not in FX_ALLOWED_LAYOUTS:
            warns.append(f"slide {sl.get('slide_id')}: fx '{fx}' 只允許用於封面/章節/結尾頁,已忽略(見 animation-principles.md 紅線2)")
            fx = "none"
        if layout == "figure_focus":
            inner = render_figure(sl, th, json_dir)
        else:
            inner = RENDERERS.get(layout, render_bullet_points)(sl, th)
        dark = layout in ("cover", "section_divider", "closing")
        bg = bg_style(sl.get("content", {}).get("background"),
                      th["primary"] if dark else "#FFFFFF")
        fx_attr = f' data-fx="{fx}" data-fx-intensity="{eng.get("fx_intensity", "low")}"' if fx != "none" else ""
        canvas = '<canvas class="fxlayer"></canvas>' if fx != "none" else ""
        slides_html.append(
            f'<section class="slide{" dark" if dark else ""}" style="{bg}"{fx_attr}>'
            f"{canvas}<div class='inner'>{inner}</div></section>"
        )
        notes.append(sl.get("speaker_notes", ""))
    if not slides_html:
        sys.exit("[錯誤] 沒有任何頁面屬於 html-canvas 引擎;若整份走 native-pptx,請改用 build_native_pptx.py")
    for w in warns:
        print(f"[警告] {w}")
    if skipped:
        print(f"[提示] 已跳過 native-pptx 頁面:slide_id {skipped}(用 build_native_pptx.py 產出)")
    meta = spec["metadata"]
    return HTML_TEMPLATE.format(
        title=esc(meta.get("presentation_title", "Presentation")),
        author=esc(meta.get("author", "")),
        primary=th["primary"], secondary=th["secondary"], accent=th["accent"],
        font_ea=th["font_ea"], font_latin=th["font_latin"],
        slides="\n".join(slides_html),
        notes_json=json.dumps(notes, ensure_ascii=False),
        fxjs=fxjs,
    )


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root {{ --primary:{primary}; --secondary:{secondary}; --accent:{accent}; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ height:100%; background:#000; overflow:hidden;
  font-family:"{font_latin}","{font_ea}",sans-serif; }}
.slide {{ position:absolute; inset:0; opacity:0; pointer-events:none;
  transition:opacity .45s ease; }}
.slide.active {{ opacity:1; pointer-events:auto; }}
.slide .inner {{ position:relative; z-index:2; width:100%; height:100%;
  padding:5.5% 7%; display:flex; flex-direction:column; }}
.fxlayer {{ position:absolute; inset:0; width:100%; height:100%; z-index:1; }}
.slide h2 {{ color:var(--primary); font-size:2.2vw; border-bottom:3px solid var(--secondary);
  padding-bottom:.4em; margin-bottom:1em; }}
.slide.dark h1 {{ color:#fff; font-size:3.4vw; line-height:1.3; }}
.cover-box {{ margin:auto; text-align:center; }}
.cover-box .sub {{ color:var(--secondary); font-size:1.5vw; margin-top:1.2em; }}
.secnum {{ color:var(--accent); font-size:5vw; font-weight:700; margin-bottom:.2em; }}
ul.bullets {{ list-style:none; font-size:1.7vw; color:#1f2937; }}
ul.bullets li {{ padding:.45em 0 .45em 1.4em; position:relative; }}
ul.bullets li::before {{ content:""; position:absolute; left:.2em; top:1em;
  width:.45em; height:.45em; border-radius:50%; background:var(--secondary); }}
ul.bullets li.lv1 {{ margin-left:1.8em; font-size:1.45vw; }}
ul.bullets li.lv1::before {{ background:var(--accent); }}
.twocol {{ display:flex; gap:4%; flex:1; }}
.twocol .col {{ flex:1; }}
.twocol h3 {{ color:var(--secondary); font-size:1.6vw; margin-bottom:.6em; }}
.figwrap {{ flex:1; display:flex; flex-direction:column; align-items:center; justify-content:center; }}
.figwrap img {{ max-width:92%; max-height:82%; object-fit:contain; }}
.caption {{ margin-top:.8em; font-size:1.1vw; color:#4b5563; }}
.img-missing {{ color:#b91c1c; font-size:1.2vw; border:2px dashed #b91c1c; padding:2em; }}
.arch {{ position:relative; flex:1; }}
.arch .node {{ position:absolute; display:flex; align-items:center; justify-content:center;
  text-align:center; border-radius:10px; padding:.4em .6em;
  box-shadow:0 3px 10px rgba(0,0,0,.18); z-index:3; }}
.arch .labelbox {{ position:absolute; display:flex; align-items:center; z-index:3; }}
.arch svg.lines {{ position:absolute; inset:0; width:100%; height:100%; z-index:2; overflow:visible; }}
/* --- 進場動畫 --- */
.step {{ visibility:hidden; }}
.step.shown {{ visibility:visible; animation-duration:var(--dur,500ms);
  animation-delay:var(--delay,0ms); animation-fill-mode:both; }}
.fx-appear.shown {{ animation-name:none; }}
.fx-fade.shown {{ animation-name:kfade; }}
.fx-wipe.shown {{ animation-name:kwipe; }}
.fx-fly-bottom.shown {{ animation-name:kflyb; }}
.fx-fly-left.shown {{ animation-name:kflyl; }}
.fx-fly-right.shown {{ animation-name:kflyr; }}
@keyframes kfade {{ from {{ opacity:0; }} to {{ opacity:1; }} }}
@keyframes kwipe {{ from {{ clip-path:inset(100% 0 0 0); opacity:.3; }} to {{ clip-path:inset(0); opacity:1; }} }}
@keyframes kflyb {{ from {{ transform:translateY(55vh); opacity:0; }} to {{ transform:none; opacity:1; }} }}
@keyframes kflyl {{ from {{ transform:translateX(-60vw); opacity:0; }} to {{ transform:none; opacity:1; }} }}
@keyframes kflyr {{ from {{ transform:translateX(60vw); opacity:0; }} to {{ transform:none; opacity:1; }} }}
@media (prefers-reduced-motion: reduce) {{
  .step.shown {{ animation:none !important; }} .slide {{ transition:none; }} }}
/* --- 導覽與簡報者模式 --- */
#bar {{ position:fixed; bottom:0; left:0; height:4px; background:var(--secondary);
  z-index:9; transition:width .3s; }}
#pg {{ position:fixed; bottom:10px; right:16px; color:#9ca3af; font-size:13px; z-index:9; }}
#presenter {{ position:fixed; inset:auto 0 0 0; max-height:34%; background:rgba(15,23,42,.94);
  color:#e5e7eb; padding:14px 22px; font-size:15px; line-height:1.6; overflow:auto;
  z-index:10; display:none; border-top:2px solid var(--secondary); }}
#presenter.on {{ display:block; }}
#presenter .t {{ color:var(--secondary); font-size:12px; margin-bottom:4px; }}
</style>
</head>
<body>
{slides}
<div id="bar"></div><div id="pg"></div>
<div id="presenter"><div class="t">SPEAKER NOTES — P 鍵關閉</div><div id="pnote"></div></div>
<script>{fxjs}</script>
<script>
(function () {{
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var notes = {notes_json};
  var cur = 0, fx = null;
  var THEME = [getComputedStyle(document.documentElement).getPropertyValue('--secondary').trim(),
               getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()];

  function steps(slide) {{
    var m = {{}};
    slide.querySelectorAll('.step').forEach(function (el) {{
      var k = parseInt(el.getAttribute('data-step') || '0', 10);
      (m[k] = m[k] || []).push(el);
    }});
    return Object.keys(m).map(Number).sort(function (a, b) {{ return a - b; }})
      .map(function (k) {{ return m[k]; }});
  }}

  function show(i, revealAll) {{
    if (i < 0 || i >= slides.length) return;
    if (fx) {{ fx.stop(); fx = null; }}
    slides[cur].classList.remove('active');
    cur = i;
    var s = slides[cur];
    s.classList.add('active');
    s.querySelectorAll('.step').forEach(function (el) {{
      el.classList.toggle('shown', !!revealAll);
    }});
    var cv = s.querySelector('.fxlayer');
    if (cv) fx = CanvasFX.mount(cv, s.getAttribute('data-fx'),
      {{ intensity: s.getAttribute('data-fx-intensity') || 'low', colors: THEME }});
    document.getElementById('bar').style.width = ((cur + 1) / slides.length * 100) + '%';
    document.getElementById('pg').textContent = (cur + 1) + ' / ' + slides.length;
    document.getElementById('pnote').textContent = notes[cur] || '(無備忘稿)';
  }}

  function advance() {{
    var groups = steps(slides[cur]);
    for (var g = 0; g < groups.length; g++) {{
      if (!groups[g][0].classList.contains('shown')) {{
        groups[g].forEach(function (el) {{ el.classList.add('shown'); }});
        return;
      }}
    }}
    show(cur + 1);
  }}

  function back() {{
    var groups = steps(slides[cur]);
    for (var g = groups.length - 1; g >= 0; g--) {{
      if (groups[g][0].classList.contains('shown')) {{
        groups[g].forEach(function (el) {{ el.classList.remove('shown'); }});
        return;
      }}
    }}
    show(cur - 1, true);
  }}

  document.addEventListener('keydown', function (e) {{
    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {{ e.preventDefault(); advance(); }}
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); back(); }}
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1, true);
    else if (e.key === 'p' || e.key === 'P')
      document.getElementById('presenter').classList.toggle('on');
  }});
  document.addEventListener('click', function () {{ advance(); }});
  show(0);
}})();
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser(description="slides_content.json → 自包含 HTML 簡報")
    ap.add_argument("json_file")
    ap.add_argument("-o", "--output", default="deck.html")
    args = ap.parse_args()

    json_path = Path(args.json_file)
    spec = load_spec(json_path)
    fxjs_path = Path(__file__).resolve().parent.parent / "assets" / "canvas-fx.js"
    if not fxjs_path.is_file():
        sys.exit(f"[錯誤] 找不到 canvas 特效引擎:{fxjs_path}")
    fxjs = fxjs_path.read_text(encoding="utf-8")

    out = build(spec, json_path.resolve().parent, fxjs)
    Path(args.output).write_text(out, encoding="utf-8")
    n = out.count('<section class="slide')
    print(f"[完成] {args.output}({n} 頁,{len(out) / 1024:.0f} KB,自包含)")


if __name__ == "__main__":
    main()
