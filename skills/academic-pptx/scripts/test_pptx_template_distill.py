#!/usr/bin/env python3
"""test_pptx_template_distill.py

Deterministic, rerunnable self-test for pptx_template_distill.py.

The hard part of testing a theme-color/font reader is getting a .pptx file
whose theme color and East Asian font are known in advance -- python-pptx's
public API is read-mostly for theme parts (there is no
`slide_master.theme.color_scheme.accent1 = ...` setter). So this test builds
its own synthetic fixture instead of relying on a hand-prepared file:

  1. Use python-pptx to create a base Presentation() -- this gives us a
     complete, valid .pptx package (all required parts, correct
     relationships) using the library's own default template, so we start
     from something guaranteed structurally valid rather than hand-rolling
     OOXML from scratch.
  2. Save it to a throwaway path.
  3. Re-open that saved file as a zip archive, locate its theme part (reusing
     pptx_template_distill's own relationship-resolution logic, so the test
     and the tool agree on how to find it), parse the theme XML with
     ElementTree, and directly rewrite two things we control precisely:
       - accent1's <a:srgbClr val="..."/> to a color chosen for this test
       - minorFont's <a:ea typeface="..."/> to "標楷體" (DFKai-SB), per this
         skill family's Chinese-font-discipline convention
  4. Write a new zip that is byte-identical to the original except for that
     one replaced theme part (all other parts are copied through unchanged),
     producing the synthetic fixture.
  5. Run pptx_template_distill.distill() on the fixture and assert the
     round-tripped color and font exactly match what was written in step 3.

This stays within "python-pptx + zipfile + xml.etree.ElementTree only" --
step 1 uses python-pptx's public API to get a valid base package; steps 3-4
use zipfile/ElementTree to perform the targeted, deterministic mutation that
python-pptx's public API does not expose a way to do.

Run with:
    python test_pptx_template_distill.py
Exits 0 and prints "ALL ASSERTIONS PASSED" on success; raises AssertionError
(non-zero exit) on failure.
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import os
import posixpath
import sys as _sys
import tempfile
import zipfile
from xml.etree import ElementTree as ET

# Make the sibling module importable regardless of the caller's cwd.
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptx import Presentation  # noqa: E402
import pptx_template_distill as distiller  # noqa: E402

A_NS = distiller.A_NS

# --- Test fixture parameters (deterministic, chosen for this test) --------
TEST_ACCENT1_HEX = "E69F00"     # Okabe-Ito "orange" -- distinctive, not a
                                  # color the default Office theme would ever
                                  # already have, so a match can't be a
                                  # coincidence.
TEST_MINOR_EA_FONT = "標楷體"     # DFKai-SB, this skill family's CJK font
                                  # discipline default (see
                                  # references/academic-style-catalog.md).


def a(tag):
    return distiller.a(tag)


def build_synthetic_pptx(dst_path):
    """Create dst_path: a .pptx whose theme has accent1=TEST_ACCENT1_HEX and
    minorFont/ea typeface=TEST_MINOR_EA_FONT, and nothing else changed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        base_path = os.path.join(tmp, "base.pptx")

        # Step 1-2: a structurally valid base package via python-pptx's own
        # default template.
        Presentation().save(base_path)

        # Step 3: find the theme part the same way the tool itself does.
        with zipfile.ZipFile(base_path) as zf:
            master_paths = sorted(
                n for n in zf.namelist()
                if n.startswith("ppt/slideMasters/slideMaster") and n.endswith(".xml")
            )
            assert master_paths, "base.pptx unexpectedly has no slide master part"
            theme_path = distiller.find_theme_part_for_master(zf, master_paths[0])
            assert theme_path is not None, "could not resolve theme part on base.pptx"

            theme_xml_bytes = zf.read(theme_path)

        # Record every original part so the rewritten zip is a faithful copy
        # except for the one part we intentionally mutate.
        ET.register_namespace("a", A_NS)
        root = ET.fromstring(theme_xml_bytes)
        theme_elements = root.find(a("themeElements"))
        clr_scheme = theme_elements.find(a("clrScheme"))
        font_scheme = theme_elements.find(a("fontScheme"))

        accent1_el = clr_scheme.find(a("accent1"))
        assert accent1_el is not None, "base theme has no <a:accent1> -- unexpected template shape"
        srgb_el = accent1_el.find(a("srgbClr"))
        assert srgb_el is not None, (
            "base theme's accent1 is not an <a:srgbClr> -- this fixture builder "
            "assumes python-pptx's default template uses a fixed RGB accent1; "
            "if that ever changes, extend this test to handle <a:sysClr> too."
        )
        srgb_el.set("val", TEST_ACCENT1_HEX)

        minor_font_el = font_scheme.find(a("minorFont"))
        assert minor_font_el is not None, "base theme has no <a:minorFont>"
        minor_ea_el = minor_font_el.find(a("ea"))
        assert minor_ea_el is not None, "base theme's minorFont has no <a:ea> element"
        minor_ea_el.set("typeface", TEST_MINOR_EA_FONT)

        new_theme_bytes = ET.tostring(root, encoding="UTF-8", xml_declaration=True)

        # Step 4: rewrite the zip, replacing only the theme part.
        with zipfile.ZipFile(base_path) as zin, \
             zipfile.ZipFile(dst_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == theme_path:
                    data = new_theme_bytes
                zout.writestr(item, data)

    return theme_path


def main():
    with tempfile.TemporaryDirectory() as tmp:
        fixture_path = os.path.join(tmp, "synthetic_template.pptx")
        theme_path = build_synthetic_pptx(fixture_path)

        assert os.path.isfile(fixture_path), "synthetic fixture was not created"

        # Step 5: run the real tool under test on the fixture we just built.
        spec = distiller.distill(fixture_path)

        written_accent1 = TEST_ACCENT1_HEX
        read_back_accent1 = spec["theme_colors"]["accent1"]

        written_minor_ea = TEST_MINOR_EA_FONT
        read_back_minor_ea = spec["fonts"]["minor"]["ea"]

        print("Fixture theme part :", theme_path)
        print("Fixture file        :", fixture_path)
        print(f"accent1   written = {written_accent1!r}   read back = {read_back_accent1!r}")
        print(f"minor/ea  written = {written_minor_ea!r}   read back = {read_back_minor_ea!r}")

        assert read_back_accent1 == written_accent1, (
            f"accent1 mismatch: wrote {written_accent1!r}, distill() read back {read_back_accent1!r}"
        )
        assert read_back_minor_ea == written_minor_ea, (
            f"minor/ea font mismatch: wrote {written_minor_ea!r}, distill() read back {read_back_minor_ea!r}"
        )

        # Sanity check the rest of the spec is still well-formed (not part of
        # the color/font assertion, but catches gross breakage in the same run).
        assert spec["slide_size"]["width_emu"] > 0
        assert len(spec["layouts"]) > 0, "expected at least one slide layout in the default template"

    print("ALL ASSERTIONS PASSED")


if __name__ == "__main__":
    main()
