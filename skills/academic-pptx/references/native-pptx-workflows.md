# Native PPTX Workflows

This file documents four workflows for working with `.pptx` files at the
native OOXML level using `python-pptx` (1.0.2, already a project dependency —
no new packages are introduced by this file or by
`scripts/pptx_template_distill.py`). It exists alongside the PPTX skill's
`pptxgenjs.md`/`editing.md` because those cover the from-scratch and
JS-toolchain paths; this file covers the case where the deliverable must
start from, or be produced as, a real `.pptx` object graph that the user can
open and keep editing natively in PowerPoint.

Read this file from `SKILL.md` Step 4 whenever the task involves: extracting
a template's design system, editing pages of an existing deck in place,
producing native (re-editable) charts or tables, or inserting mathematical
notation. Each section below states what is achievable and, just as
importantly, what is **not** — overclaiming what a native-PPTX pipeline can
guarantee is the failure mode this file is written to prevent.

---

## (a) Template extraction

**Path:** `scripts/pptx_template_distill.py` (delivered alongside this file,
in `skills/academic-pptx/scripts/`).

When a user hands you an institutional template (school crest deck, a prior
paper's deck they want to match, a conference-provided template), don't
eyeball its colors and fonts from a screenshot — extract them mechanically.
`python-pptx` has no public API for reading theme colors or the font scheme,
so the script opens the `.pptx` as a zip archive and parses
`ppt/theme/theme1.xml` directly (`<a:clrScheme>` for the 12 theme colors,
`<a:fontScheme>` for major/minor Latin and East Asian typefaces), then uses
the ordinary `python-pptx` object model for everything the public API does
expose (slide dimensions, layout names, placeholder geometry).

**Output format:** a single JSON document with these top-level keys:

```json
{
  "slide_size": { "width_emu": 12192000, "height_emu": 6858000,
                   "width_cm": 33.87, "height_cm": 19.05 },
  "theme_colors": { "dk1": "000000", "lt1": "FFFFFF", "dk2": "1F4E79",
                     "lt2": "EEECE1", "accent1": "4472C4", "...": "...",
                     "hlink": "0563C1", "folHlink": "954F72" },
  "fonts": { "major": { "latin": "Calibri Light", "ea": "標楷體" },
             "minor": { "latin": "Calibri", "ea": "標楷體" } },
  "layouts": [ { "name": "Title Slide",
                 "placeholders": [ { "idx": 0, "type": "TITLE",
                                      "x_cm": 1.5, "y_cm": 2.0,
                                      "w_cm": 9.0, "h_cm": 1.5 }, ... ] }, ... ],
  "master_background": "no explicit fill found (inherits theme background)"
}
```

Use this output to drive slide construction: pull `theme_colors.accent1` into
your color plan instead of guessing a hex code, and check `fonts.major.ea`
before assuming a template wants 標楷體 versus some other CJK face — templates
built outside Taiwan often leave the `ea` typeface unset or default to a
Windows system font that is not 標楷體, and the distiller reports exactly what
is set rather than assuming.

**Honest boundary:** the script reads theme-level color and font *definitions*.
It does not resolve which specific run in body text actually uses `accent3`
versus a hard-coded RGB override — a template author can always bypass the
theme by hard-coding colors on individual runs, and the distiller has no way
to detect that without walking every run in every layout and master, which is
out of scope for a template-reconnaissance tool. If a rebuilt deck doesn't
visually match the source template, check for hard-coded run-level overrides
before assuming the distiller's theme reading was wrong.

---

## (b) Native editing of an existing file

**Path:** open the existing `.pptx` with `python-pptx`, touch only the target
slide(s)/shape(s), save.

```python
from pptx import Presentation

prs = Presentation("existing_deck.pptx")
slide = prs.slides[4]                     # only the slide that needs a change
for shape in slide.shapes:
    if shape.has_text_frame and "Results" in shape.text_frame.text:
        shape.text_frame.paragraphs[0].runs[0].text = "Results (updated)"
        break
prs.save("existing_deck.pptx")            # or a new path if you want to keep the original
```

**Honest boundary — read this before promising anything about file diffs:**
`python-pptx` does not do incremental in-place patching of the underlying zip
archive. On `.save()`, it re-serializes the **entire** package — every part,
including slides you never touched — from its in-memory XML tree back out to
a fresh zip. This means:

- **What you can guarantee:** the *content and layout* of untouched slides is
  unchanged — the same shapes, text, positions, fonts, and formatting will be
  present when the file is reopened. Round-tripping through `python-pptx`
  without modification is lossless at the object-model level for the
  properties that model exposes.
- **What you cannot guarantee:** that the saved file is byte-for-byte
  identical to the original, or that a binary diff of the two `.pptx` files
  will be empty for the untouched slide parts. Re-serialization can change
  XML attribute ordering, whitespace, zip entry compression and ordering, and
  can silently drop or normalize any XML construct `python-pptx`'s object
  model does not represent (custom XML parts it doesn't parse, certain
  vendor extensions, some animation/transition XML on slides you didn't touch).
  This is not a limitation specific to this skill's implementation — it is a
  structural property of any tool (python-pptx or otherwise) that loads OOXML
  into an object model and re-emits it, rather than doing true binary patch.

**Practical implication:** if a user needs a guarantee that unrelated slides
are byte-identical (e.g., a template a legal/branding team has signed off on
must not change at the file level even in whitespace), do not use this
workflow — recommend a true zip-level surgical patch (rewrite only the one
slide's XML part inside the existing zip without touching other parts) or,
more simply, hand-editing in PowerPoint directly. Say this limitation to the
user rather than silently shipping a file that differs more than they expect.

---

## (c) Native charts and tables

**Path:** `slide.shapes.add_chart(...)` — this produces a genuine OOXML chart
part with an embedded XLSX workbook, so in PowerPoint the user can right-click
the chart and choose **Edit Data in Excel** to change the underlying numbers
natively, exactly as if they had inserted the chart by hand. This is the
native-editability property that distinguishes it from an image export of a
matplotlib chart (which is what `management-figure` produces, appropriately,
for publication-grade static figures — use `add_chart` specifically when the
audience needs to *keep tweaking numbers in PowerPoint after delivery*).

Minimal runnable example:

```python
from pptx import Presentation
from pptx.util import Inches
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

prs = Presentation()
slide = prs.slides.add_slide(prs.slide_layouts[5])   # blank-ish layout

chart_data = CategoryChartData()
chart_data.categories = ["Q1 (lowest)", "Q2", "Q3", "Q4 (highest)"]
chart_data.add_series("Treatment effect (%)", (28, 22, 15, 8))

x, y, cx, cy = Inches(1.0), Inches(1.5), Inches(8.0), Inches(4.5)
graphic_frame = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
)
chart = graphic_frame.chart
chart.has_legend = False

prs.save("native_chart_demo.pptx")
```

For tables, the equivalent native-editability object is
`slide.shapes.add_table(rows, cols, x, y, cx, cy)`, which returns a real
`GraphicFrame`/`Table` whose cells the user can click into and edit directly
in PowerPoint — again, prefer this over a rendered table image whenever the
audience is expected to keep editing numbers after you deliver the file.

---

## (d) Formulas via OMML injection

`python-pptx` has no public API for inserting mathematical notation — there
is no `shape.add_equation()`. The viable path is direct XML injection: build
or transplant an `<a14:m>` (Office Math Markup Language, OMML) subtree into
the target run or shape's XML using `lxml` — which is already a transitive
dependency of `python-pptx` itself (it uses `lxml.etree` internally for all
XML handling), so this introduces no new dependency.

**Honest limitation:** OMML's nested structure (`<m:oMath>`, `<m:f>` for
fractions, `<m:sSup>`/`<m:sSub>` for super/subscripts, `<m:rad>` for
radicals, etc.) is genuinely difficult to hand-author correctly from a blank
page — the schema is deep, under-documented compared to core DrawingML, and
small mistakes (wrong nesting, missing `<m:ctrlPr>` run properties) tend to
produce a PowerPoint file that silently shows a blank or corrupted equation
rather than a clear error.

**The correct working method, not a shortcut — do this every time:**

1. Open PowerPoint (or LibreOffice Impress, which also round-trips OMML
   acceptably) and manually type the actual formula you need using its
   built-in equation editor. Save as `.pptx`.
2. Unzip that file and open the slide XML part containing the equation run
   (`ppt/slides/slideN.xml`). Locate the `<a14:m>`/`<m:oMath>` subtree that
   PowerPoint generated.
3. Use that real, PowerPoint-generated XML as your **template**. Write
   programmatic string substitution or `lxml` tree manipulation that swaps
   the specific numbers/variables/operators inside that known-good structure,
   rather than trying to construct the OMML tree from the schema
   specification from scratch.
4. Inject the resulting subtree into the target run via `lxml` (e.g.,
   `run._r.append(the_omml_element)` after parsing it with
   `lxml.etree.fromstring`), save, and visually verify the result — do not
   assume structural correctness just because no exception was raised.

This mirrors this skill family's L-014 lesson (documented in
the maintainer's private LESSONS log): that lesson was about a
pptxgenjs bilingual-font mis-mix caused by guessing at output XML structure
instead of dissecting a real rendered file first. The specific bug was in
`.pptx` run-property XML for CJK/Latin font pairing, but the underlying
principle — **dissect real, tool-generated output before writing
transformation rules; never hand-guess XML/OMML structure from the schema
alone** — applies identically here and in the sibling `.docx` skill's
style-XML editing (see the project convention on editing `document.xml`
directly for style-level changes). Treat "dump a real example, then
pattern-match against it" as the standard operating procedure for any OOXML
subtree this skill family has not already built tooling for, not as a
one-off workaround specific to math.

---

## When to read this file vs. the base PPTX skill

- Building a deck from scratch with no existing template → base PPTX skill's
  `pptxgenjs.md` remains the default path; only reach for this file's
  native-`python-pptx` workflows when one of (a)-(d) above is specifically
  needed (template fidelity, in-place editing, re-editable charts/tables, or
  math notation).
- Editing an already-native `.pptx` (not one produced by pptxgenjs) → this
  file's (b) is the correct path; read its honest boundary before promising
  the user anything about untouched-slide byte stability.
- Any time the deliverable must remain click-to-edit in PowerPoint after
  handoff (charts, tables, or template-matched placeholders) → prefer the
  native object types in (c) over rendered images, and say so explicitly to
  the user so they know they can edit the numbers later.
