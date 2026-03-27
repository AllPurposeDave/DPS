#!/usr/bin/env python3
"""
build_doc_from_config.py — Build a Word doc template from doc_template_config.xlsx

Reads the Excel config produced by create_config_excel.py, applies heading styles
(font, size, bold, italic, color, spacing) to a fresh .docx, and inserts one
placeholder paragraph per heading level.

Usage:
  python build_doc_from_config.py
  python build_doc_from_config.py --config doc_template_config.xlsx -o my_template.docx
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Any

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from openpyxl import load_workbook


# ── Config parsing ───────────────────────────────────────────────────────────

def _coerce_value(val: Any) -> Any:
    """Convert an Excel cell value to a Python type."""
    if val is None:
        return None
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val
    s = str(val).strip()
    if s.upper() == "TRUE":
        return True
    if s.upper() == "FALSE":
        return False
    try:
        as_int = int(s)
        if str(as_int) == s:
            return as_int
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _parse_settings_sheet(ws) -> dict:
    """
    Read a Setting | Value | Description sheet.
    Skips rows where column A is blank or starts with '#'.
    Returns {setting_key: coerced_value}.
    """
    result = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        key = row[0] if row else None
        if not key:
            continue
        key = str(key).strip()
        if key.startswith("#"):
            continue
        val = _coerce_value(row[1] if len(row) > 1 else None)
        if val is not None:
            result[key] = val
    return result


def _load_config(xlsx_path: str) -> dict:
    """
    Load Document and Heading Styles sheets from the config workbook.

    Returns:
        {
          "document":  {setting: value, ...},
          "headings":  {
              "h1": {field: value, ...},
              "h2": {field: value, ...},
          }
        }
    """
    wb = load_workbook(xlsx_path, read_only=True, data_only=True)
    config: dict = {}

    if "Document" in wb.sheetnames:
        config["document"] = _parse_settings_sheet(wb["Document"])
    else:
        logging.warning("'Document' sheet not found in config — using defaults.")
        config["document"] = {}

    if "Heading Styles" in wb.sheetnames:
        flat = _parse_settings_sheet(wb["Heading Styles"])
        headings: dict = {}
        for dotkey, val in flat.items():
            level, _, field = dotkey.partition(".")
            if level and field:
                headings.setdefault(level, {})[field] = val
        config["headings"] = headings
    else:
        logging.warning("'Heading Styles' sheet not found in config — heading styles unchanged.")
        config["headings"] = {}

    wb.close()
    return config


# ── Style application ────────────────────────────────────────────────────────

def _parse_hex_color(hex_str: Any) -> RGBColor:
    """Parse a 6-digit hex string (e.g. '2F5496') to RGBColor. Falls back to DPS blue."""
    try:
        s = str(hex_str).strip().lstrip("#")
        return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))
    except (ValueError, IndexError, TypeError):
        logging.warning("Could not parse color '%s' — using default blue.", hex_str)
        return RGBColor(0x2F, 0x54, 0x96)


def _apply_heading_style(doc: Document, style_name: str, hcfg: dict) -> None:
    """Modify a built-in heading style in doc using values from hcfg."""
    try:
        style = doc.styles[style_name]
    except KeyError:
        logging.warning("Style '%s' not found in document — skipping.", style_name)
        return

    font = style.font
    if "font_name" in hcfg:
        font.name = str(hcfg["font_name"])
    if "font_size" in hcfg:
        font.size = Pt(hcfg["font_size"])
    if "bold" in hcfg:
        font.bold = bool(hcfg["bold"])
    if "italic" in hcfg:
        font.italic = bool(hcfg["italic"])
    if "color" in hcfg:
        font.color.rgb = _parse_hex_color(hcfg["color"])

    pf = style.paragraph_format
    if "space_before" in hcfg:
        pf.space_before = Pt(hcfg["space_before"])
    if "space_after" in hcfg:
        pf.space_after = Pt(hcfg["space_after"])
    if "keep_with_next" in hcfg:
        pf.keep_with_next = bool(hcfg["keep_with_next"])

    logging.info("Applied style '%s': %s", style_name, hcfg)


def _set_page_margins(doc: Document, doc_cfg: dict) -> None:
    """Set page margins on the first section from config values (in inches)."""
    section = doc.sections[0]
    if "margin_top" in doc_cfg:
        section.top_margin = Inches(doc_cfg["margin_top"])
    if "margin_bottom" in doc_cfg:
        section.bottom_margin = Inches(doc_cfg["margin_bottom"])
    if "margin_left" in doc_cfg:
        section.left_margin = Inches(doc_cfg["margin_left"])
    if "margin_right" in doc_cfg:
        section.right_margin = Inches(doc_cfg["margin_right"])


def _apply_body_defaults(doc: Document, doc_cfg: dict) -> None:
    """Apply body font settings to the Normal style."""
    try:
        normal = doc.styles["Normal"]
        if "body_font_name" in doc_cfg:
            normal.font.name = str(doc_cfg["body_font_name"])
        if "body_font_size" in doc_cfg:
            normal.font.size = Pt(doc_cfg["body_font_size"])
    except KeyError:
        logging.warning("'Normal' style not found — body defaults not applied.")


# ── Document builder ─────────────────────────────────────────────────────────

def build_doc_from_config(config_path: str, output_path: str | None) -> None:
    logging.info("Loading config: %s", config_path)
    config = _load_config(config_path)

    doc_cfg = config.get("document", {})
    headings_cfg = config.get("headings", {})

    # Resolve output path: CLI arg overrides config setting
    if not output_path:
        output_path = str(doc_cfg.get("output_filename", "doc_template.docx"))

    doc = Document()

    # Apply document-level settings
    _set_page_margins(doc, doc_cfg)
    _apply_body_defaults(doc, doc_cfg)

    # Apply heading styles
    level_map = [
        ("h1", "Heading 1", 1),
        ("h2", "Heading 2", 2),
    ]
    for level_key, style_name, _ in level_map:
        if level_key in headings_cfg:
            _apply_heading_style(doc, style_name, headings_cfg[level_key])

    # Remove the default blank paragraph that Document() creates
    for para in list(doc.paragraphs):
        para._element.getparent().remove(para._element)

    # Insert one placeholder paragraph per heading level
    for level_key, _, heading_level in level_map:
        default_text = "Section Title" if heading_level == 1 else "Subsection Title"
        placeholder = headings_cfg.get(level_key, {}).get("placeholder_text", default_text)
        doc.add_heading(str(placeholder), level=heading_level)

    doc.save(output_path)
    logging.info("Saved: %s", output_path)
    print(f"  Document template saved: {output_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(
        description="Build a Word doc template from doc_template_config.xlsx"
    )
    parser.add_argument(
        "--config", "-c",
        default="doc_template_config.xlsx",
        help="Path to the Excel config workbook (default: doc_template_config.xlsx)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output .docx path — overrides output_filename in config",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.config):
        print(f"ERROR: Config file not found: {args.config}", file=sys.stderr)
        print("  Run create_config_excel.py first to generate the config workbook.", file=sys.stderr)
        sys.exit(1)

    try:
        build_doc_from_config(args.config, args.output)
    except Exception as exc:
        logging.error("Failed: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
