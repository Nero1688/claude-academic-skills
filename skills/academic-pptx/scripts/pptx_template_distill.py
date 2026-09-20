#!/usr/bin/env python3
"""pptx_template_distill.py

Extract a .pptx template's design system into a JSON spec: slide size, theme
colors, theme fonts, slide-layout placeholder geometry, and a master
background hint.

Why this script exists: python-pptx's public object model has no API for
reading theme colors or the font scheme -- <a:clrScheme> and <a:fontScheme>
live inside ppt/theme/themeN.xml and are simply not exposed as python-pptx
objects. This script opens the .pptx as a zip archive (a .pptx IS a zip of
OOXML parts) and parses that one XML part directly with the standard-library
xml.etree.ElementTree, then falls back to python-pptx's ordinary public API
for everything it DOES expose (slide dimensions, slide layouts, placeholder
idx/type/position).

No new pip dependencies are introduced: python-pptx (already installed for
this skill family, 1.0.2) plus the standard library (zipfile,
xml.etree.ElementTree, json, argparse, posixpath, sys).

Usage:
    python pptx_template_distill.py <input.pptx> [-o output.json]

See references/native-pptx-workflows.md section (a) for how this fits into
the broader native-PPTX workflow set, and scripts/test_pptx_template_distill.py
for a deterministic self-test that generates a synthetic .pptx with a known
theme color and East Asian font, then asserts the round trip through this
script is exact.
"""
import sys

# Guard against mojibake when this script's stdout is piped through a
# non-UTF-8 Windows console codepage while printing Chinese font names
# (e.g. 標楷體) in the JSON output.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import argparse
import json
import posixpath
import zipfile
from xml.etree import ElementTree as ET

from pptx import Presentation

A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"

EMU_PER_CM = 360000.0  # 914400 EMU/inch / 2.54 cm/inch

COLOR_SLOTS = [
    "dk1", "lt1", "dk2", "lt2",
    "accent1", "accent2", "accent3", "accent4", "accent5", "accent6",
    "hlink", "folHlink",
]


def a(tag):
    """Build a fully-qualified {namespace}tag lookup key for DrawingML."""
    return "{%s}%s" % (A_NS, tag)


def emu_to_cm(value):
    """Convert an EMU length to centimeters, rounded to 2 decimal places.

    Returns None (rather than raising or returning 0) when the source value
    itself is None -- this happens for layout placeholders whose position is
    inherited from the slide master and not restated in the layout's own
    XML. We report that honestly as "not set at this level" instead of
    inventing a coordinate.
    """
    if value is None:
        return None
    return round(int(value) / EMU_PER_CM, 2)


def find_theme_part_for_master(zf, master_path):
    """Resolve the theme XML part path for a given slide master part path.

    A .pptx does not hard-code 'theme1.xml' as the theme filename -- the
    slide master points at its theme via a relationship in its .rels file,
    of type '.../relationships/theme'. This function reads that
    relationship and resolves its (relative) Target against the master's
    own directory, the same way an OOXML consumer is required to.

    Returns None if no such relationship is found (malformed or unusual
    package) rather than guessing 'ppt/theme/theme1.xml'.
    """
    master_dir = posixpath.dirname(master_path)
    master_name = posixpath.basename(master_path)
    rels_path = posixpath.join(master_dir, "_rels", master_name + ".rels")
    try:
        rels_xml = zf.read(rels_path)
    except KeyError:
        return None

    root = ET.fromstring(rels_xml)
    for rel in root:
        rel_type = rel.get("Type", "")
        if rel_type.endswith("/theme"):
            target = rel.get("Target", "")
            # L5-b fix (2026-09-20): OOXML allows an absolute Target such as
            # "/ppt/theme/theme1.xml". posixpath.join() then discards
            # master_dir and keeps the leading "/", but zip archive members
            # are stored WITHOUT a leading slash -- zf.read() would raise a
            # raw KeyError instead of the "no theme found" fallback this
            # function is meant to provide. Strip it so both relative and
            # absolute Targets resolve to a valid zip member name.
            return posixpath.normpath(posixpath.join(master_dir, target)).lstrip("/")
    return None


def read_theme(zf, theme_path):
    """Parse ppt/theme/themeN.xml for <a:clrScheme> and <a:fontScheme>.

    Color resolution: each color slot holds either <a:srgbClr val="RRGGBB"/>
    (an explicit fixed color) or <a:sysClr val="..." lastClr="RRGGBB"/> (a
    reference to a Windows system color, e.g. "windowText", with lastClr
    recording the RGB value PowerPoint last resolved it to). We report the
    resolvable hex value in both cases, since that is what a template author
    actually sees rendered.
    """
    theme_xml = zf.read(theme_path)
    root = ET.fromstring(theme_xml)
    theme_elements = root.find(a("themeElements"))
    if theme_elements is None:
        raise ValueError(f"{theme_path} has no <a:themeElements> -- not a valid theme part")

    clr_scheme = theme_elements.find(a("clrScheme"))
    font_scheme = theme_elements.find(a("fontScheme"))

    theme_colors = {}
    for slot in COLOR_SLOTS:
        el = clr_scheme.find(a(slot)) if clr_scheme is not None else None
        value = None
        if el is not None:
            srgb = el.find(a("srgbClr"))
            if srgb is not None:
                value = srgb.get("val")
            else:
                sysclr = el.find(a("sysClr"))
                if sysclr is not None:
                    value = sysclr.get("lastClr")
        theme_colors[slot] = value

    def read_font_group(tag):
        grp = font_scheme.find(a(tag)) if font_scheme is not None else None
        if grp is None:
            return {"latin": None, "ea": None}
        latin_el = grp.find(a("latin"))
        ea_el = grp.find(a("ea"))
        latin = latin_el.get("typeface") if latin_el is not None else None
        ea = ea_el.get("typeface") if ea_el is not None else None
        # OOXML represents "not set" as typeface="" (empty string), not as a
        # missing attribute. Normalize both cases to None so callers only
        # have to check for one falsy sentinel.
        return {"latin": latin or None, "ea": ea or None}

    fonts = {
        "major": read_font_group("majorFont"),
        "minor": read_font_group("minorFont"),
    }
    return theme_colors, fonts


def placeholder_type_name(ph_format):
    """Return the placeholder type as a plain string name, or None.

    ph_format.type is a python-pptx EnumValue (PP_PLACEHOLDER_TYPE member);
    .name gives the readable constant name (e.g. "TITLE", "SUBTITLE").
    """
    t = ph_format.type
    if t is None:
        return None
    return getattr(t, "name", str(t))


def describe_master_background(master):
    """One-line human-readable hint about the slide master's background.

    python-pptx exposes background.fill.type, which is None when the master
    has no explicit background override (it then inherits the theme's
    background definition, which this script does not attempt to resolve
    further -- that would require walking the theme's <a:bg1>/<a:bg2> +
    format-scheme background fill, which is out of scope for a
    template-reconnaissance tool focused on colors/fonts/geometry).
    """
    try:
        fill_type = master.background.fill.type
    except Exception as exc:  # pragma: no cover - defensive, reported not swallowed
        return f"Could not determine master background ({exc.__class__.__name__}: {exc})."
    if fill_type is None:
        return "No explicit background fill on the slide master (inherits theme background)."
    return f"Slide master has an explicit background fill: {fill_type}."


def distill(pptx_path):
    prs = Presentation(pptx_path)

    slide_w, slide_h = prs.slide_width, prs.slide_height
    result = {
        "source_file": pptx_path,
        "slide_size": {
            "width_emu": int(slide_w),
            "height_emu": int(slide_h),
            "width_cm": emu_to_cm(slide_w),
            "height_cm": emu_to_cm(slide_h),
        },
        "theme_colors": {},
        "fonts": {},
        "layouts": [],
        "master_background": None,
    }

    with zipfile.ZipFile(pptx_path) as zf:
        master_paths = sorted(
            name for name in zf.namelist()
            if name.startswith("ppt/slideMasters/slideMaster") and name.endswith(".xml")
        )
        if not master_paths:
            raise ValueError(f"{pptx_path}: no slide master part found -- not a valid .pptx?")

        theme_path = find_theme_part_for_master(zf, master_paths[0])
        if theme_path is None:
            raise ValueError(
                f"{pptx_path}: could not resolve a theme relationship for {master_paths[0]}"
            )

        theme_colors, fonts = read_theme(zf, theme_path)
        result["theme_colors"] = theme_colors
        result["fonts"] = fonts
        result["_theme_source_part"] = theme_path

        if len(master_paths) > 1:
            result["_note_multiple_masters"] = (
                f"{len(master_paths)} slide masters found in this file; the theme "
                f"reported above is read from {master_paths[0]} only. Other masters "
                f"may reference a different theme part -- rerun per-master if needed."
            )

    for layout in prs.slide_masters[0].slide_layouts:
        layout_info = {"name": layout.name, "placeholders": []}
        for ph in layout.placeholders:
            pf = ph.placeholder_format
            layout_info["placeholders"].append({
                "idx": pf.idx,
                "type": placeholder_type_name(pf),
                "x_cm": emu_to_cm(ph.left),
                "y_cm": emu_to_cm(ph.top),
                "w_cm": emu_to_cm(ph.width),
                "h_cm": emu_to_cm(ph.height),
            })
        result["layouts"].append(layout_info)

    result["master_background"] = describe_master_background(prs.slide_masters[0])

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Distill a .pptx template's theme colors, fonts, slide "
                     "size, and layout/placeholder geometry into a JSON spec."
    )
    parser.add_argument("input", help="Path to the input .pptx template file")
    parser.add_argument("-o", "--output", default=None,
                         help="Path to write the JSON spec to (default: stdout)")
    args = parser.parse_args()

    spec = distill(args.input)
    output_text = json.dumps(spec, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"Wrote template spec to {args.output}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
