#!/usr/bin/env python3
"""
create_config_excel.py — Generate doc_template_config.xlsx

Creates a fresh Excel config workbook for the Doc Template Builder.
Fill in the values, then run build_doc_from_config.py to produce the Word doc.

Usage:
  python create_config_excel.py                          # default: doc_template_config.xlsx
  python create_config_excel.py -o my_template_config.xlsx
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, List

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation


# ── Styling constants (matches DPS Excel styling) ───────────────────────────

HEADER_FONT = Font(name="Arial", bold=True, size=10, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
THIN_BORDER = Border(
    left=Side(style="thin", color="CCCCCC"),
    right=Side(style="thin", color="CCCCCC"),
    top=Side(style="thin", color="CCCCCC"),
    bottom=Side(style="thin", color="CCCCCC"),
)
SUBHEADER_FONT = Font(name="Arial", bold=True, size=10, color="2F5496")
SUBHEADER_FILL = PatternFill(start_color="D6E4F0", end_color="D6E4F0", fill_type="solid")
DESC_FONT = Font(name="Arial", size=9, color="666666")
WRAP_ALIGN = Alignment(vertical="top", wrap_text=True)


# ── Helper functions ─────────────────────────────────────────────────────────

def _style_headers(ws, headers: List[str]):
    """Write header row and apply standard styling."""
    ws.append(headers)
    for cell in ws[1]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER
    ws.freeze_panes = "A2"


def _add_subheader(ws, text: str, ncols: int = 3):
    """Add a sub-header row (# prefixed in column A)."""
    row = [f"# {text}"] + [""] * (ncols - 1)
    ws.append(row)
    r = ws.max_row
    for c in range(1, ncols + 1):
        cell = ws.cell(row=r, column=c)
        cell.font = SUBHEADER_FONT
        cell.fill = SUBHEADER_FILL
        cell.border = THIN_BORDER


def _add_setting(ws, setting: str, value: Any, description: str = ""):
    """Add a Setting | Value | Description row."""
    ws.append([setting, value, description])
    ws.cell(row=ws.max_row, column=3).font = DESC_FONT


def _add_bool_validation(ws, col_letter: str, min_row: int, max_row: int):
    """Add TRUE/FALSE dropdown validation to a column range."""
    dv = DataValidation(type="list", formula1='"TRUE,FALSE"', allow_blank=True)
    dv.error = "Please select TRUE or FALSE"
    dv.errorTitle = "Invalid value"
    ws.add_data_validation(dv)
    dv.add(f"{col_letter}{min_row}:{col_letter}{max_row}")


def _auto_column_widths(ws):
    """Auto-fit column widths with wrapping for wide columns."""
    WRAP_THRESHOLD = 50
    wrap_cols = set()
    for col_idx in range(1, ws.max_column + 1):
        max_width = 0
        for row in ws.iter_rows(min_col=col_idx, max_col=col_idx, values_only=True):
            val = row[0]
            if val is not None:
                max_width = max(max_width, len(str(val)))
        letter = get_column_letter(col_idx)
        if max_width > WRAP_THRESHOLD:
            ws.column_dimensions[letter].width = 65
            wrap_cols.add(col_idx)
        else:
            ws.column_dimensions[letter].width = min(max_width + 4, 65)
    if wrap_cols:
        for data_row in ws.iter_rows(min_row=2):
            for cell in data_row:
                if cell.column in wrap_cols:
                    cell.alignment = WRAP_ALIGN


def _finalize_sheet(ws):
    """Apply auto-widths and autofilter."""
    _auto_column_widths(ws)
    if ws.max_column and ws.max_row:
        last_col = get_column_letter(ws.max_column)
        ws.auto_filter.ref = f"A1:{last_col}{ws.max_row}"


# ── Heading defaults ─────────────────────────────────────────────────────────

# (key, default_value, description)
H1_DEFAULTS = [
    ("placeholder_text", "Section Title",    "Placeholder text inserted as a demo H1 paragraph"),
    ("font_name",        "Calibri",           "Font family name"),
    ("font_size",        16,                  "Font size in pt"),
    ("bold",             "TRUE",              "Bold? TRUE or FALSE"),
    ("italic",           "FALSE",             "Italic? TRUE or FALSE"),
    ("color",            "2F5496",            "Hex RGB color — 6 digits, no # prefix (e.g. 2F5496)"),
    ("space_before",     12,                  "Space before paragraph in pt"),
    ("space_after",      6,                   "Space after paragraph in pt"),
    ("keep_with_next",   "TRUE",              "Keep heading with the next paragraph? TRUE or FALSE"),
]

H2_DEFAULTS = [
    ("placeholder_text", "Subsection Title",  "Placeholder text inserted as a demo H2 paragraph"),
    ("font_name",        "Calibri",           "Font family name"),
    ("font_size",        14,                  "Font size in pt"),
    ("bold",             "TRUE",              "Bold? TRUE or FALSE"),
    ("italic",           "FALSE",             "Italic? TRUE or FALSE"),
    ("color",            "2F5496",            "Hex RGB color — 6 digits, no # prefix (e.g. 2F5496)"),
    ("space_before",     10,                  "Space before paragraph in pt"),
    ("space_after",      4,                   "Space after paragraph in pt"),
    ("keep_with_next",   "TRUE",              "Keep heading with the next paragraph? TRUE or FALSE"),
]

BOOL_KEYS = {"bold", "italic", "keep_with_next"}


# ── Sheet builders ───────────────────────────────────────────────────────────

def _build_readme(wb):
    ws = wb.create_sheet("README")
    ws.append(["Doc Template Config Workbook"])
    ws.cell(row=1, column=1).font = Font(name="Arial", bold=True, size=14, color="2F5496")
    ws.append([])
    instructions = [
        "This workbook controls the heading styles and document settings used by build_doc_from_config.py.",
        "",
        "HOW TO USE:",
        "  1. Edit values in the 'Document' and 'Heading Styles' sheets.",
        "  2. Settings sheets use:  Setting | Value | Description  columns.",
        "  3. Sub-headers (rows starting with #) separate groups — do NOT delete them.",
        "  4. Boolean fields (bold, italic, keep_with_next) have TRUE/FALSE dropdowns.",
        "  5. Empty Value cells use the built-in default.",
        "",
        "HOW TO RUN:",
        "  1. Generate this config (already done):",
        "       python create_config_excel.py",
        "  2. Edit values in this workbook as needed.",
        "  3. Generate the Word doc template:",
        "       python build_doc_from_config.py",
        "       python build_doc_from_config.py --config doc_template_config.xlsx -o my_template.docx",
        "",
        "COLOR FORMAT:",
        "  Enter hex RGB colors as 6 uppercase digits with NO # prefix.",
        "  Examples:  2F5496  (DPS blue)   |   000000  (black)   |   FFFFFF  (white)",
        "",
        "HEADING STYLE KEYS (in 'Heading Styles' sheet):",
        "  h1.*  — controls the Heading 1 style",
        "  h2.*  — controls the Heading 2 style",
        "  The placeholder_text value is the text inserted into the demo document.",
    ]
    for line in instructions:
        ws.append([line])
    ws.column_dimensions["A"].width = 80


def _build_document_sheet(wb):
    ws = wb.create_sheet("Document")
    _style_headers(ws, ["Setting", "Value", "Description"])

    _add_subheader(ws, "Document Defaults")
    _add_setting(ws, "output_filename", "doc_template.docx",
                 "Output .docx filename (relative to where you run the script)")
    _add_setting(ws, "body_font_name",  "Calibri",
                 "Default body text font (applied to Normal style)")
    _add_setting(ws, "body_font_size",  11,
                 "Default body font size in pt")

    _add_subheader(ws, "Page Margins (inches)")
    _add_setting(ws, "margin_top",    1.0,  "Top margin in inches")
    _add_setting(ws, "margin_bottom", 1.0,  "Bottom margin in inches")
    _add_setting(ws, "margin_left",   1.25, "Left margin in inches")
    _add_setting(ws, "margin_right",  1.25, "Right margin in inches")

    _finalize_sheet(ws)


def _build_heading_styles_sheet(wb):
    ws = wb.create_sheet("Heading Styles")
    _style_headers(ws, ["Setting", "Value", "Description"])

    bool_rows = []

    for level_label, defaults in [("Heading 1", H1_DEFAULTS), ("Heading 2", H2_DEFAULTS)]:
        prefix = "h1" if level_label == "Heading 1" else "h2"
        _add_subheader(ws, level_label)
        for key, val, desc in defaults:
            _add_setting(ws, f"{prefix}.{key}", val, desc)
            if key in BOOL_KEYS:
                bool_rows.append(ws.max_row)

    for r in bool_rows:
        _add_bool_validation(ws, "B", r, r)

    _finalize_sheet(ws)


# ── Main ─────────────────────────────────────────────────────────────────────

def generate_config_workbook(output_path: str):
    wb = Workbook()
    wb.remove(wb.active)  # remove default empty sheet

    _build_readme(wb)
    _build_document_sheet(wb)
    _build_heading_styles_sheet(wb)

    wb.save(output_path)
    print(f"  Config workbook saved: {output_path}")
    print(f"  Sheets: {', '.join(wb.sheetnames)}")
    print()
    print("  Edit values in 'Document' and 'Heading Styles', then run:")
    print("    python build_doc_from_config.py")


def main():
    parser = argparse.ArgumentParser(
        description="Generate doc_template_config.xlsx — heading style config for build_doc_from_config.py"
    )
    parser.add_argument(
        "-o", "--output",
        default="doc_template_config.xlsx",
        help="Output path for the config workbook (default: doc_template_config.xlsx)",
    )
    args = parser.parse_args()

    try:
        generate_config_workbook(args.output)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
