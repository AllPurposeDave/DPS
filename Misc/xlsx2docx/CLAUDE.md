# xlsx2docx — Design Notes

## What this tool does
Converts Excel files to formatted Word documents. Primary use case: controls matrices where each row is one control — the control ID column becomes a Word heading, and remaining columns (description, guidance, notes, status) render as `key_value` content below that heading.

**There are two independent implementations** — a Python script and a VBA macro. Both produce equivalent output. They do not depend on each other and can be used separately.

| Approach | Best for |
|----------|----------|
| **Python script** (`xlsx2docx.py`) | Batch conversion, CI/CD pipelines, advanced multi-sheet rules, scripted workflows |
| **VBA macro** (`xlsx2docx_macro.bas`) | Users already in Excel who want one-click conversion without Python installed |

---

## Files
| File | Purpose |
|------|---------|
| `xlsx2docx.py` | **Python** — main conversion script (requires Python + dependencies) |
| `xlsx2docx_config.yaml` | YAML config template for the Python script — copy and customize per project |
| `xlsx2docx_macro.bas` | **VBA** — standalone Excel macro (requires Microsoft Word installed) |
| `xlsx2docx_config.xlsx` | Excel config workbook for the VBA macro — contains a "Config" sheet and a demo "Controls" sheet with sample NIST 800-53 data |
| `create_config_workbook.py` | Utility to regenerate `xlsx2docx_config.xlsx` (run once; not needed at runtime) |
| `CLAUDE.md` | This file |

---

## Python Script — Quick Start

```bash
# From this directory:
python xlsx2docx.py --input ../../input/controls.xlsx

# Scan a whole folder:
python xlsx2docx.py --input ../../input/

# Explicit config:
python xlsx2docx.py --config my_config.yaml --input controls.xlsx

# Verbose logging:
python xlsx2docx.py --input controls.xlsx -v
```

Output `.docx` files go to `output/xlsx2docx/` by default (configurable in `xlsx2docx_config.yaml`).

### Python config: `xlsx2docx_config.yaml`
YAML file with full control over input/output paths, sheet rules (glob matching, render modes), page layout, heading/body/table styles, header/footer tokens, cover page, and TOC. See the file itself for inline documentation of every key.

---

## VBA Macro — Quick Start

1. Open your data workbook in Excel.
2. *(Optional but recommended)* Copy the **Config** sheet from `xlsx2docx_config.xlsx` into your workbook and edit the values in column B.
3. Press **Alt+F11** to open the VBA editor.
4. **File > Import File** > select `xlsx2docx_macro.bas` (or paste the code into a new Module).
5. Close the VBA editor.
6. **Developer > Macros > GenerateDocx > Run** (or Alt+F8).

Output: `MyWorkbook.docx` in the same folder as the source `.xlsx`.

### VBA config: "Config" sheet in the workbook
The macro reads configuration from a worksheet named **Config** in the active workbook. The sheet uses a simple two-column layout:

| Column A (Setting) | Column B (Value) |
|---------------------|------------------|
| `heading_column` | `Control ID` |
| `heading_level` | `2` |
| `document_title` | `My Document` |
| ... | ... |

- If no "Config" sheet is found, the macro uses built-in defaults (equivalent to the Python script's defaults).
- The `xlsx2docx_config.xlsx` workbook serves as both a reference template and a ready-to-run demo. Copy just the Config sheet into any workbook, or use the entire file as-is.
- Column C in the Config sheet contains descriptions of each setting.
- Setting names are case-insensitive. Section-header rows (shaded blue) are ignored.

### `xlsx2docx_config.xlsx` contents
| Sheet | Purpose |
|-------|---------|
| **Config** | All macro settings with defaults, descriptions, and demo values pre-filled |
| **Controls** | 20 sample NIST SP 800-53 controls across 8 families (AC, AT, AU, CA, CM, IA, IR, RA, SC) — serves as demo data for testing the macro |

The Controls sheet includes multi-line cell values (newlines in Description and Guidance) and a mix of statuses (Implemented, Partially Implemented, Planned) to exercise realistic formatting.

To regenerate this file after editing the Python source:
```bash
python create_config_workbook.py
```

---

## Design Decisions

### 1. Two independent tools, same output
The Python script and VBA macro are **completely standalone**. Neither imports, calls, or depends on the other. Both exist because different users have different workflows:
- Python users get batch processing, multi-sheet glob rules, and YAML config that version-controls well.
- Excel-only users get a one-click macro with zero external dependencies (beyond Word).

Both produce the same document structure: heading per row, key-value body content, styled headers/footers with token resolution.

### 2. YAML config for Python, Excel config for VBA
The Python script uses YAML because it is easy to version-control and hand-edit. The VBA macro uses an Excel "Config" sheet because its users are already in Excel — no file format context-switch, no code editing required. The setting names are consistent between the two where they overlap.

### 3. `row_as_heading` as the primary render mode
The core use case is controls matrices where rows = controls. Each row gets a Word heading (H1 by default), and the remaining columns render as `label: value` paragraphs below — like a structured data card per control.

Other modes exist in the Python script for different shapes of data:
- `table` — flat grid (all rows in one table)
- `key_value` — 2-column settings/metadata sheet
- `list` — single-column bullet list
- `prose` — column A as free text paragraphs
- `skip` — exclude sheet

The VBA macro supports the `row_as_heading` mode only (its primary use case).

### 4. First-match sheet rules with glob patterns (Python only)
Rules in `sheets:` are evaluated top-to-bottom; the first matching rule wins. Patterns are case-insensitive globs (`fnmatch`). Put specific rules before catch-alls. Example:
```yaml
sheets:
  - match: "Summary"    # exact
    render_as: "key_value"
  - match: "Admin*"     # prefix glob
    render_as: "skip"
  - match: "*"          # catch-all — must be last
    render_as: "row_as_heading"
    heading_column: "Control ID"
```

### 5. Functions ported from Doc Template Builder
Rather than importing from `../Doc Template Builder/build_doc_from_config.py`, the heading/header/footer/cover-page logic is copied and adapted directly into both `xlsx2docx.py` and `xlsx2docx_macro.bas`. This keeps each tool self-contained — they run without needing sibling files on the Python path or VBA references.

The originals are in [build_doc_from_config.py](../Doc%20Template%20Builder/build_doc_from_config.py).
Key ported functions: `_apply_heading_style`, `_build_tab_stop_hf`, `_add_page_number_field`, `_add_num_pages_field`, `_style_table`, `_build_cover_page`.

### 6. TOC limitation
`python-docx` can insert a Word TOC field code, but the page numbers are only populated when Word recalculates the fields. After opening the document, press **Ctrl+A → F9** (or right-click the TOC → Update Field) to populate entries.

### 7. Column width scaling (`fit_to_page`) — Python only
When `fit_to_page: true`, column widths are distributed proportionally based on maximum content length per column, capped at `max_col_width` (default 3.0 in), and rescaled to fill the usable page width. This prevents tables from bleeding off the page.

### 8. Multi-line cell values
Excel cells with newlines (`Alt+Enter`) are handled consistently in both tools:
- **Python**: inserts `<w:br/>` (Word soft return) inside the same paragraph.
- **VBA**: replaces `Chr(10)` with `Chr(11)` (vertical tab = Word soft return).

Both approaches keep multi-line content within a single paragraph, preserving the bold label on the first line and consistent spacing.

---

## Config Key Reference (Python — `xlsx2docx_config.yaml`)

| Section | Key | Default | Notes |
|---------|-----|---------|-------|
| `identity.document_title` | — | `""` | Used in header/footer/cover tokens |
| `identity.date` | — | today | YYYY-MM-DD; blank = today |
| `cover_page.enabled` | — | `false` | Set true to generate a title page |
| `toc.enabled` | — | `false` | Set true to insert a TOC field |
| `page.size` | — | `Letter` | `Letter` or `A4` |
| `headings.h1.color` | — | `2F5496` | 6-digit hex, no `#` |
| `table.fit_to_page` | — | `true` | Auto-scale col widths to page |
| `sheets[].render_as` | — | `table` | `row_as_heading`, `table`, `key_value`, `list`, `prose`, `skip` |
| `sheets[].heading_column` | — | `""` | Column name → Word heading (for `row_as_heading`) |
| `sheets[].body_render` | — | `key_value` | How body columns render: `key_value`, `table_row`, `prose` |
| `sheets[].include_columns` | — | `[]` | Empty = include all columns |
| `sheets[].rename_columns` | — | `{}` | `{"Old Name": "New Label"}` |
| `sheets[].exclude_columns` | — | `[]` | Column names to omit from output |
| `include_unmatched` | — | `true` | Render unmatched sheets as `table` if true; skip if false |

## Config Key Reference (VBA — "Config" sheet)

| Setting | Default | Notes |
|---------|---------|-------|
| `heading_column` | `Control ID` | Column name whose values become Word headings |
| `heading_level` | `2` | 1=H1, 2=H2, 3=H3, 4=H4 |
| `header_row` | `1` | Row containing column headers |
| `data_start_row` | `2` | First data row |
| `skip_empty_heading` | `TRUE` | Skip rows where heading column is blank |
| `exclude_columns` | `""` | Comma-separated column names to omit |
| `include_columns` | `""` | Comma-separated columns to include (empty = all) |
| `rename_columns` | `""` | `OldName=NewLabel` pairs, comma-separated |
| `document_title` | `""` | `{document_title}` token |
| `organization_name` | `""` | `{organization_name}` token |
| `classification` | `""` | `{classification}` token |
| `author` | `""` | `{author}` token |
| `version` | `1.0` | `{version}` token |
| `date` | today | `{date}` token (YYYY-MM-DD; blank = today) |
| `page_size` | `Letter` | `Letter` or `A4` |
| `orientation` | `Portrait` | `Portrait` or `Landscape` |
| `margin_top` | `1.0` | Inches |
| `margin_bottom` | `1.0` | Inches |
| `margin_left` | `1.25` | Inches |
| `margin_right` | `1.25` | Inches |
| `body_font` | `Calibri` | Body text font |
| `body_size` | `11` | Body text size (pt) |
| `body_line_spacing` | `1.15` | Line spacing multiplier |
| `heading_font` | `Calibri` | Heading font |
| `heading_size` | `14` | Heading size (pt) |
| `heading_bold` | `TRUE` | Bold headings |
| `heading_color` | `2F5496` | 6-digit hex, no `#` |
| `label_font` | `Calibri` | Key-value label font |
| `label_size` | `11` | Label size (pt) |
| `label_bold` | `TRUE` | Bold labels |
| `label_color` | `2F5496` | 6-digit hex |
| `header_left` | `{organization_name}` | Left header (supports tokens) |
| `header_center` | `""` | Center header |
| `header_right` | `{document_title}` | Right header |
| `header_font` | `Arial` | Header font |
| `header_size` | `8` | Header size (pt) |
| `header_color` | `666666` | Header color hex |
| `footer_left` | `{classification}` | Left footer |
| `footer_center` | `Page {page} of {pages}` | Center footer (`{page}`/`{pages}` become live fields) |
| `footer_right` | `{date}` | Right footer |
| `footer_font` | `Arial` | Footer font |
| `footer_size` | `8` | Footer size (pt) |
| `footer_color` | `666666` | Footer color hex |
| `add_sheet_heading` | `FALSE` | Insert sheet name as H1 before controls |

---

## Tokens Available in Header / Footer / Cover Page

Both tools support the same tokens:

| Token | Resolves to |
|-------|-------------|
| `{document_title}` | `identity.document_title` (Python) / `document_title` setting (VBA) |
| `{organization_name}` | `identity.organization_name` / `organization_name` |
| `{classification}` | `identity.classification` / `classification` |
| `{author}` | `identity.author` / `author` |
| `{version}` | `identity.version` / `version` |
| `{date}` | `identity.date` / `date` (or today if blank) |
| `{page}` | Live Word PAGE field (current page number) |
| `{pages}` | Live Word NUMPAGES field (total pages) |

---

## Requirements

### Python script
Same as the rest of the DPS project (`requirements.txt` in the project root):
```
python-docx>=0.8.11
pyyaml>=6.0
openpyxl>=3.1.0
```

### VBA macro
- Microsoft Excel (to run the macro)
- Microsoft Word (used via late binding — no VBA reference setup needed)
- No Python, no external dependencies
