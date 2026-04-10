# DPS User Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Running the Pipeline](#running-the-pipeline)
5. [Pipeline Steps](#pipeline-steps)
6. [Configuration Reference](#configuration-reference)
7. [Output Reference](#output-reference)
8. [File Lifecycle: What to Keep, What to Delete](#file-lifecycle-what-to-keep-what-to-delete)
9. [Utilities](#utilities)
   - [Word Counter](#word-counter-scriptsword_counterpy)
   - [Control Attribute Analyzer](#control-attribute-analyzer-miscanalyze_control_attributespy)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The **Document Processing System (DPS)** is a Python pipeline that transforms policy `.docx` files into chunk-friendly documents optimized for RAG (Retrieval-Augmented Generation) retrieval.

The pipeline runs 10 sequential steps:

| Step | Script | What It Does | Type |
|------|--------|-------------|------|
| 0 | `policy_profiler.py` | Scan & classify all documents | Read-only |
| 1 | `acronym_finder.py` | Scan for acronym candidates and generate audit Excel | Read-only |
| 2 | `extract_controls.py` | Extract structured control data | Read-only |
| 3 | `cross_reference_extractor.py` | Capture cross-references | Read-only |
| 4 | `heading_style_fixer.py` | Fix fake headings to real Word styles | Transformative |
| 5 | `section_splitter.py` | Split documents at H1 boundaries into RAG-sized sub-documents | Transformative |
| 6 | `add_metadata.py` | Stamp sub-documents with identity metadata | Transformative |
| 7 | `docx2md.py` | Convert .docx to clean Markdown with YAML frontmatter | Conversion |
| 8 | `docx2jsonl.py` | Convert .docx to chunked JSONL for RAG ingestion | Conversion |
| 9 | `validate_controls.py` | Validate controls exist in split output | Read-only |

**Read-only** steps (0, 1, 2, 3, 9) only analyze documents and produce reports. Your original input files are never modified.

**Transformative** steps (4, 5, 6) create new `.docx` files with modifications. Originals in `input/` are still untouched — these steps write altered copies to their own output folders. Each transformative step feeds into the next: Step 4 produces `*_fixed.docx` files, Step 5 splits those into sub-documents, and Step 6 adds metadata to the sub-documents.

**Conversion** steps (7, 8) convert .docx files to other formats (Markdown and JSONL). They support two input modes:
- **Pure Conversion**: Read directly from `input/` — no transformations applied.
- **Optimized** (default): Read from a pipeline step's output (e.g. `heading_fixes` from Step 4). Configurable via `pure_conversion` and `optimized_source_step` settings.

After all steps complete, a consolidated Excel report is generated with one sheet per step's CSV output.

---

## Prerequisites

- **Python 3.10** or later (uses `X | Y` type hint syntax)
- Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies:
| Package | Version | Purpose |
|---------|---------|---------|
| `python-docx` | >=0.8.11 | Read/write .docx files (all scripts) |
| `pyyaml` | >=6.0 | Read dps_config.yaml (legacy fallback only) |
| `openpyxl` | >=3.1.0 | Write Excel spreadsheets |

---

## Quick Start

1. **Place your `.docx` files** in the `input/` folder.
2. **Run the pipeline:**
   ```bash
   python run_pipeline.py
   ```
3. **Find results** in `output/` — start with `output/0 - profiler/document_inventory.xlsx`.

That's it. The default config works out of the box for most policy document sets.

---

## Running the Pipeline

### Basic Usage

```bash
# Run all enabled steps (0 through 9)
python run_pipeline.py

# List all steps and their enabled/disabled status
python run_pipeline.py --list
```

### Running Specific Steps

```bash
# Run a single step
python run_pipeline.py --step 0

# Run a range of steps
python run_pipeline.py --step 1-3

# Run specific steps (comma-separated)
python run_pipeline.py --step 2,4

# Mix ranges and individual steps
python run_pipeline.py --step 0,2-4
```

### Additional Options

```bash
# Use an alternative config file
python run_pipeline.py --config my_config.xlsx

# Skip the consolidated Excel report at the end
python run_pipeline.py --no-excel
```

### Running Scripts Standalone

Each script can be run independently outside the pipeline:

```bash
python scripts/policy_profiler.py --config dps_config.xlsx --input ./input --output ./output/0\ -\ profiler
python scripts/extract_controls.py --config dps_config.xlsx ./input ./output/2\ -\ controls
python scripts/cross_reference_extractor.py --config dps_config.xlsx ./input ./output/3\ -\ cross_references
python scripts/heading_style_fixer.py --config dps_config.xlsx ./input ./output/4\ -\ heading_fixes
python scripts/section_splitter.py --config dps_config.xlsx ./output/4\ -\ heading_fixes ./output/5\ -\ split_documents
python scripts/add_metadata.py --config dps_config.xlsx ./output/5\ -\ split_documents ./output/6\ -\ metadata
python scripts/validate_controls.py --config dps_config.xlsx
```

### Pipeline Behavior

- Steps run sequentially in order (0 → 9).
- If a step fails, the pipeline stops and reports which step failed.
- Re-run from the failed step with `--step N` after fixing the issue.
- Elapsed time is displayed per step and for the total run.

---

## Pipeline Steps

### Step 0 — Document Profiler (Read-only)

**Script:** `scripts/policy_profiler.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/0 - profiler/`

Scans every document and produces a comprehensive inventory:

- Detects heading styles (built-in, custom, and fake bold headings)
- Classifies standard sections (Purpose, Scope, Intent, Controls, Appendix)
- Classifies all tables (control matrix, applicability, reference, crosswalk, role/responsibility)
- Detects cross-references (internal section refs and external document refs)
- Flags formatting anomalies (text boxes, tracked changes, comments, images, embedded objects, password/IRM protection)
- Auto-classifies documents as Type A/B/C/D/E based on content ratios
- Computes priority scores for optimization ordering
- Counts words per document
- Searches for key terms across all documents
- Extracts date metadata for lifecycle tracking (modified date, compliance date, freshness status)

**Start here** — open `document_inventory.xlsx` to understand your document set before running further steps.

**Key config sections:** `sections`, `headings`, `cross_references.profiler_patterns`, `tables.classification`, `classification`, `thresholds`, `priority_scoring`, `search_terms`

**Output files:**

| File | Contents |
|------|----------|
| `document_inventory.xlsx` | Master spreadsheet — one row per document with all metrics |
| `document_profiles.json` | Machine-readable profiles (used by Step 6) |
| `section_inventory.csv` | One row per section per document |
| `table_inventory.csv` | One row per table per document |
| `crossref_inventory.csv` | One row per cross-reference candidate |

**Lifecycle tracking columns** in `document_inventory.xlsx`:

| Column | Source | Description |
|--------|--------|-------------|
| Modified | Word core properties | Last modified date from the `.docx` file's built-in metadata |
| Compliance Date | Body text scan | Extracted from "Compliance Date" heading or "as of Month DD, YYYY" pattern |
| Freshness | Computed from compliance date | Traffic-light status: **Overdue** (>365 days, red), **Review Soon** (30–365 days, yellow), **Current** (<30 days, green) |

These columns also appear in the consolidated DPS Report under the "0 - Document Inventory" sheet.

---

### Step 1 — Acronym Finder (Read-only)

**Script:** `scripts/acronym_finder.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/1 - acronyms/`

Scans every document for acronym candidates and generates a multi-sheet Excel audit report. Run early — undefined acronyms in RAG chunks produce poor retrieval answers (a chunk saying "MFA is required per AC-2.1" with no expansion confuses the model).

- Detects pure-caps acronyms (NIST, MFA), mixed-with-numbers (AC-2, 800-53), slash-separated (IT/OT), and parenthetical definitions
- Flags acronyms with no parenthetical expansion found anywhere in the corpus (highlighted yellow)
- Builds a cross-reference matrix showing which acronyms span which documents
- Output Excel feeds into Steps 7 and 8 when acronym metadata is enabled

**Key config section:** `acronym_finder` (Section 15 in `dps_config.xlsx`)

**Output files:**

| File | Contents |
|------|----------|
| `acronym_audit.xlsx` | Acronym Definitions (with Status dropdown + instruction row), Per Document, Global Summary, Undefined Acronyms, Cross-Reference Matrix, Custom Tags (with instruction row), Config Used |

**Using the output:**

1. **Run Step 1** — produces `output/1 - acronyms/acronym_audit.xlsx`
2. **Open it** — review the "Acronym Definitions" sheet. Use the **Status** dropdown (column D) to mark each row as Confirmed, False Positive, or Needs Review. Fill in missing definitions in column C (yellow-highlighted rows). **Do not delete rows** — use "False Positive" status instead so downstream steps automatically filter them out.
3. **Fill in Custom Tags** — go to the "Custom Tags" sheet and enter comma-separated tags for each document (e.g., `access control, CUI, FedRAMP-High`).
4. **Save a copy to `input/`** — the filename doesn't matter, just make sure the config key (`metadata.tags.acronym_definitions_file`) points to it.
5. **Steps 6/7/8 read it** — they look for the "Acronym Definitions" sheet (falling back to "Per Document"), columns A (`Document`) and B (`Acronym`). Rows with Status="False Positive" are automatically skipped.

> **Tip:** Open **Global Summary** and sort by "Total Occurrences" descending to find the highest-impact acronyms first. The **Undefined Acronyms** sheet highlights entries with no detected definition — these are your priority targets.

**Troubleshooting:**

| Problem | Fix |
|---------|-----|
| "No .docx files found" | Check `input_folder` path in config. Use forward slashes even on Windows. |
| Way too many results | Increase `min_global_occurrences` to 2 or 3 in config. Add common false positives to the `ignore_list`. |
| Missing acronyms you expected | Check if they're on the `ignore_list`. Check `min_length` (default 2). |
| Script crashes on a specific file | That file is probably password-protected or corrupted. The script logs the error and continues with other files. |
| Slow on large corpus | Normal. Expect 1–3 minutes for 80+ files depending on size. Tables and textboxes add scanning time. |

---

### Step 2 — Control Extractor (Read-only)

**Script:** `scripts/extract_controls.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/2 - controls/`

Extracts structured control data from compliance documents:

- Matches control IDs using configurable regex patterns (e.g., `AC-1.001`, `IR001.002`)
- Classifies text into: control description, supplemental guidance, miscellaneous
- Extracts document-level metadata (purpose, scope, applicability)
- Supports whitelist/blacklist filtering by control ID
- Checkpointing allows resuming interrupted batch runs

**Key config section:** `control_extraction`

**Output files:**

| File | Contents |
|------|----------|
| `controls_output.csv` | One row per control (if CSV output enabled) |
| `controls_output.xlsx` | One row per control (if Excel output enabled) |
| `checkpoint.json` | Progress tracker for resumable runs |
| `errors.log` | Extraction errors and warnings |

**Output columns:** `source_file`, `section_header`, `control_id`, `control_name`, `baseline`, `control_description`, `supplemental_guidance`, `miscellaneous`, `extraction_source`, `purpose`, `scope`, `applicability`, `compliance_date`, `published_url`

> **Published URL:** If `input/Doc_URL.xlsx` is populated with document names and URLs, Step 2 includes the matching URL in every control row. This is the same file used by Step 6 for metadata injection — one input file serves both steps. See [URL Resolution](#url-resolution) for setup details.

---

### Step 3 — Cross-Reference Extractor (Read-only)

**Script:** `scripts/cross_reference_extractor.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/3 - cross_references/`

> **Important:** Run this step BEFORE Steps 4-6, which modify document structure. Cross-references should be captured from the original documents.

Extracts three types of references:

- **Internal:** "See Section 4.3", "Refer to Section 2"
- **External:** "Refer to the Access Control Policy", "As defined in the Encryption Standard"
- **URLs:** Bare text URLs, hyperlink URLs, internal bookmarks

**Key config section:** `cross_references`

**Output files:**

| File | Contents |
|------|----------|
| `cross_references.csv` | One row per cross-reference |

**Output columns:** `source_doc`, `source_section`, `source_paragraph_index`, `matched_text`, `reference_type`, `target_reference`, `resolution_status`, `target_url`, `url_display_text`, `url_type`

---

### Step 4 — Heading Style Fixer (Transformative)

**Script:** `scripts/heading_style_fixer.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/4 - heading_fixes/`

> **This step creates modified copies.** For each input document, a `*_fixed.docx` file is written to the output folder. Original input files are never changed.

Standardizes heading styles and performs document cleanup so Step 5 (splitter) can find section boundaries and Copilot KB accuracy is maximized:

- Removes Word Table of Contents paragraphs (TOC 1/2/3 styles) that create false matches in retrieval
- Clears page headers and footers (branding, page numbers, classification banners)
- Applies text deletions (configured phrases removed from all paragraphs and tables)
- Converts fake bold headings to real Word Heading 1/2/3 styles
- Maps custom heading styles (e.g., "Policy Heading 1") to standard heading styles
- Determines heading level based on numbering patterns (e.g., "1.0" → H1, "1.1" → H2, "1.1.1" → H3)
- Removes orphan revision/change history tables (detected by column headers: version + date + changes/author)
- Flattens Terms & Definitions tables to prose paragraphs (`**Term**: Definition`)
- Applies section-level deletions (heading + all content until next same/higher-level heading)

**Key config sections:** `headings`, `text_deletions`

**Output files:**

| File | Contents |
|------|----------|
| `*_fixed.docx` | One fixed document per input document |
| `heading_changes.csv` | Change log of every modification made |

**Output columns (heading_changes.csv):** `doc_name`, `paragraph_index`, `original_style`, `new_style`, `paragraph_text_preview`, `change_type`, `phrase_deleted`

**Change types logged:** `heading_fix`, `text_deletion`, `section_deletion`, `toc_removal`, `header_footer_cleared`, `revision_table_removed`, `definition_table_flattened`

---

### Step 5 — Section Splitter (Transformative)

**Script:** `scripts/section_splitter.py`
**Input:** `*_fixed.docx` files from `output/4 - heading_fixes/`
**Output:** `output/5 - split_documents/`

> **This step creates new sub-documents.** Each input document is split into multiple smaller `.docx` files. Step 5 reads from Step 4's output, not from `input/`.

Splits documents at Heading 1 boundaries to produce RAG-optimized sub-documents. Each chunk is self-contained and sized to maximize retrieval precision:

- Each sub-document is named `[OriginalName] - [Heading1Text].docx` (or `[Name] - [H1] - [H2].docx` if further split)
- Sub-documents are capped at `max_characters` (default: 36,000 chars — see tuning note below)
- Content before the first H1 (preamble) is prepended to every sub-document
- **Greedy H2 accumulation:** If an H1 section exceeds the limit, its H2 sub-sections are grouped together until adding the next one would cross the limit — then the split happens at that H2 boundary. Each chunk is as large as possible without exceeding the limit. This avoids unnecessary fragmentation from splitting at every H2.
- Preserves paragraph formatting via XML deep copy

> **Why `max_characters` matters for RAG:** RAG retrieval sends matching chunks to the LLM as context. Each chunk is retrieved as a unit — a 36k chunk where only 2k is relevant wastes 34k tokens of context budget every query. Smaller, focused chunks improve retrieval precision. Tune `max_characters` on the Thresholds sheet in `dps_config.xlsx` for your use case: use 18,000 for dense control-heavy docs, keep 36,000 for balanced policies, raise to 72,000 only for very sparse docs.

**Key config section:** `thresholds` (`max_characters`, `chars_per_page`)

**Output files:**

| File | Contents |
|------|----------|
| `[Name] - [Heading].docx` | Sub-document files |
| `split_manifest.csv` | Manifest of all sub-documents created |

**Output columns (split_manifest.csv):** `original_doc`, `sub_doc_filename`, `heading_text`, `character_count`, `page_estimate`

---

### Step 6 — Metadata Injector (Transformative)

**Script:** `scripts/add_metadata.py`
**Input:** `.docx` files from `output/5 - split_documents/`
**Output:** `output/6 - metadata/`

> **This step creates final output documents.** Each sub-document gets a metadata block added. Step 6 reads from Step 5's output.

Stamps each sub-document with identity metadata so Copilot/RAG always knows what document a chunk came from:

- **Document name** — resolved from filename + split manifest
- **URL** — resolved from Excel lookup file or fallback template
- **Scope** — extracted from profiler data (Step 0) or direct document scan
- **Intent** — extracted from profiler data (Step 0) or direct document scan
- **Tags** — generated from document type, sections found, acronyms (from `input/Acronym_Definitions.xlsx`, the same verified file used by Steps 7/8), and static tags

Metadata placement options: top of document, top and bottom, or Word header on every page.

**Key config section:** `metadata`

**Output files:**

| File | Contents |
|------|----------|
| `*.docx` | Sub-documents with metadata blocks |
| `metadata_manifest.csv` | Log of what metadata was applied to each file |

---

### Step 7 — DOCX to Markdown (Conversion)

**Script:** `scripts/docx2md.py`
**Input:** Configurable — `input/` (Pure Conversion) or `output/4 - heading_fixes/` (Optimized, default)
**Output:** `output/7 - markdown/`

Converts `.docx` files to clean Markdown with YAML frontmatter. Output is optimized for RAG ingestion. Supports two input modes:

- **Optimized** (default): reads from Step 4's heading-fixed files for cleaner heading structure
- **Pure Conversion**: reads directly from `input/`, bypassing all transformations

For full configuration details see [Section 13: DOCX to Markdown](#section-13-docx-to-markdown-docx2md) in the Configuration Reference.

---

### Step 8 — DOCX to JSONL (Conversion)

**Script:** `scripts/docx2jsonl.py`
**Input:** Configurable — `input/` (Pure Conversion) or `output/4 - heading_fixes/` (Optimized, default)
**Output:** `output/8 - jsonl/`

Converts `.docx` files to chunked JSONL for RAG/vector DB ingestion. Each output file contains one JSON object per chunk with `text`, `PublishedURL`, `Tags`, heading context, and configurable metadata. Supports the same Pure/Optimized input modes as Step 7.

---

### Step 9 — Control Validator (Read-only)

**Script:** `scripts/validate_controls.py`
**Input:** `output/2 - controls/controls_output.csv` + `output/5 - split_documents/` + `input/*.docx`
**Output:** `output/9 - validation/`

**Prerequisites:** Steps 2, 4, and 5 must have run first.

Validates that every control extracted in Step 2 is present in the split documents from Step 5, and generates a human-review workbook to triage extraction quality.

**Validation statuses:**

- **PASS** — Control found in split docs from the same parent document
- **MISSING** — Control not found in any split document
- **RELOCATED** — Control found but in a different parent document

**Confidence scoring (validation_review.xlsx):**

Each control is scored 0–100 based on extraction quality signals. Reviewers work through red rows first:

| Band | Score | Meaning |
|------|-------|---------|
| Red | 0–30 | Review first — likely extraction error |
| Yellow | 31–60 | Suspicious — worth spot-checking |
| Green | 61–100 | Likely correct |

Flags that reduce confidence: `EMPTY_DESCRIPTION`, `SHORT_DESCRIPTION`, `LONG_DESCRIPTION`, `SUSPECT_SECTION`, `APPENDIX_SECTION`, `DUPLICATE_ID_SAME_DOC`, `DUPLICATE_ID_CROSS_DOC`, `TABLE_HEADERS_IN_DESC`, `GUIDANCE_IN_DESC`, `TABLE_SOURCE`, `EMPTY_BASELINE`, `EMPTY_NAME`, `MULTI_CONTROL_PARAGRAPH`

**Output files:**

| File | Contents |
|------|----------|
| `control_validation.csv` | One row per control with validation status |
| `validation_review.xlsx` | Three-sheet workbook: confidence-scored controls for human review, summary statistics, and a template for adding missed controls |
| `README.md` | Step-by-step reviewer instructions (regenerated each run) |

**Output columns (control_validation.csv):** `control_id`, `source_file`, `source_section`, `found_in_split_docs`, `split_doc_filenames`, `parent_doc_match`, `status`

**Validation Review workbook columns:** `Row #`, `Confidence`, `Flags`, `Control ID`, `Source File`, `Section Header`, `Extraction Source`, `Source Context`, `Extracted Description`, `Extracted Guidance`, `Baseline`, `Control Name`, `Validation Status` (dropdown), `Reviewer Notes`

**Validation Status dropdown options:** `Correct`, `Wrong-FalsePositive`, `Wrong-Description`, `Wrong-Guidance`, `Wrong-Baseline`, `Wrong-Section`, `Missing-Content`, `Needs-Review`

**"Add Missing Controls" sheet:** A blank template for reviewers to enter controls the extractor missed. Columns: `Control ID`, `Source File`, `Section Header`, `Control Description`, `Supplemental Guidance`, `Baseline`, `Control Name`, `Reviewer Notes`.

### Validation Feedback Loop

After a human reviews `validation_review.xlsx`, the feedback ingestion script reads the annotations and produces the authoritative control set plus improvement suggestions.

**Script:** `scripts/ingest_review_feedback.py`

```bash
python scripts/ingest_review_feedback.py
python scripts/ingest_review_feedback.py --config dps_config.xlsx
```

**Workflow:**

1. **Run Step 9** to generate `validation_review.xlsx` (and the accompanying `README.md`)
2. **Open the README** in the validation output folder for detailed review instructions
3. **Review the workbook** in Excel:
   - Set `Validation Status` (col M) for each control, starting with red rows
   - Add `Reviewer Notes` (col N) describing corrections
   - Use the **"Add Missing Controls"** sheet to enter any controls the extractor missed
4. **Save the file** (keep the .xlsx name and format)
5. **Run the feedback script** to produce outputs

**Feedback outputs:**

| File | Contents |
|------|----------|
| `confirmed_controls.csv` | The authoritative control set: correct + unreviewed controls + manually added missing controls, minus false positives. Same CSV schema as `controls_output.csv`. |
| `feedback_report.txt` | Review coverage, status breakdown, excluded/added controls, flag accuracy analysis, per-document stats, and config improvement suggestions. |
| `suggested_config_changes.yaml` | Machine-readable config patch with blacklist additions, suspect section additions, and pattern suggestions (only generated when clear patterns are detected). |

**How confirmed_controls.csv is built:**

- Controls marked **"Correct"** or **left unreviewed** are kept (unreviewed = assumed correct)
- Controls marked **"Wrong-FalsePositive"** are excluded
- Controls from the **"Add Missing Controls"** sheet are appended (with `extraction_source` set to `Manual-Review`)
- All other statuses (Wrong-Description, Wrong-Guidance, etc.) are kept but flagged in the report

**Config suggestions the script can detect:**

- 3+ false positives sharing a control ID prefix → suggests adding to `control_extraction.blacklist`
- 3+ false positives sharing a section header → suggests adding to `SUSPECT_SECTIONS`
- Missing controls with IDs that don't match current regex → suggests new `control_id_pattern`
- GUIDANCE_IN_DESC flag correlating with description errors → suggests reviewing `guidance_keywords`

---

## Configuration Reference

All settings live in a single Excel workbook: **`dps_config.xlsx`**. The pipeline works with defaults — only change what you need.

> **Legacy support:** If `dps_config.xlsx` is not found, the pipeline falls back to `dps_config_fallback.yaml`. Both formats produce the same internal configuration. Excel is the recommended format for day-to-day use.

### How to Edit `dps_config.xlsx`

The workbook has 20 sheets (Quick Start + README + 18 configuration sheets). Each sheet controls a different part of the pipeline.

**General rules:**
- **Close the file in Excel before running the pipeline.** An open file causes permission errors on Windows.
- The **Setting** column (A) and **Value** column (B) are the only columns the pipeline reads. The **Description** column (C) is for your reference — editing it has no effect.
- **Do not rename sheet tabs.** The parser matches sheets by exact name (e.g., `Input`, `Output`, `Headings`). A renamed sheet is silently skipped.
- **Do not delete or rename `# Sub-header` rows** (rows starting with `#` in column A). These separate blocks within a sheet. Removing them merges blocks together and causes incorrect parsing.
- **Do not rearrange columns.** The parser expects Setting | Value | Description order.
- **Use Excel TRUE/FALSE for booleans** — not "yes"/"no" or "1"/"0". Cells with data validation dropdowns enforce this.
- **Regex patterns** should be entered as plain text on a single line. Test patterns at [regex101.com](https://regex101.com) before pasting.
- **Empty rows are skipped** — you can add blank rows for visual spacing without affecting the config.

**Adding new entries:**
- To add a keyword (e.g., a new section keyword, search term, or exclude pattern), insert a new row in the appropriate list block and enter the value in column A.
- To add a custom heading style, add it in **both** the `# Custom Heading Styles` list and the `# Heading Style Map` on the Headings sheet.
- To add a control ID regex pattern, add a new row under `# Control ID Patterns` on the Control Extraction sheet. Test the regex first.

**Regenerating the template:**
If the workbook becomes corrupted or you want to start fresh with all defaults:
```bash
python generate_config_template.py -o dps_config.xlsx
```

### Maintainer: Changing Workbook Structure Safely

This section is for updating the Excel config creator itself (`generate_config_template.py`), not normal day-to-day config edits.

#### If you want to reorder columns

1. Update the sheet builder headers and row writes in `generate_config_template.py`.
2. Update parser column assumptions in `scripts/shared_utils.py` (for example `_parse_settings_rows()` and any sheet-specific column indexing).
3. Regenerate and sanity-check parse:

```bash
python generate_config_template.py --from-yaml dps_config_fallback.yaml --output dps_config.xlsx
python run_pipeline.py --list
```

#### If you want to rename worksheet tabs

1. Change the tab name in `generate_config_template.py`.
2. Update `load_config_xlsx()` sheet name mapping in `scripts/shared_utils.py`.
3. Regenerate and run `python run_pipeline.py --list` to ensure the section still loads.

Note: parser matching is exact by sheet name. Renaming only in Excel (without code updates) causes that section to be skipped.

#### If you want to add or remove columns in table-like blocks

Examples: Pipeline rows, Metadata Fields, section deletion table.

1. Change table headers and row shapes in `generate_config_template.py`.
2. Update the matching parser in `scripts/shared_utils.py` so new columns are read and removed columns are no longer expected.
3. Update consuming script logic if parsed keys changed.
4. Regenerate and run a step that uses the modified section.

#### Source of truth and fallback

- Primary human-edited config: `dps_config.xlsx`
- Fallback/seed config: `dps_config_fallback.yaml`

When changing generator defaults, keep YAML defaults aligned unless you intentionally want different fallback behavior.

### Section 1: Input

Controls where your source `.docx` files are located.

| Key | Default | Description |
|-----|---------|-------------|
| `input.directory` | `"./input"` | Path to the folder containing your `.docx` policy documents. Can be absolute or relative. |
| `input.pattern` | `"*.docx"` | File glob pattern for matching documents. |
| `input.recursive` | `false` | Scan sub-folders inside the input directory. Set `true` if docs are organized in sub-folders. |
| `input.exclude_patterns` | `["~$", "_optimized", "_backup", "_fixed", "template"]` | Skip files matching any of these patterns (case-insensitive substring match). Word creates invisible `~$` temp files when a doc is open. |

**When to change:**
- Point `directory` to wherever your `.docx` files live.
- Add to `exclude_patterns` if you have files that should be skipped (e.g., drafts, archives).
- Set `recursive: true` if your documents are nested in sub-folders.

---

### Section 2: Output

Controls where results are written and filenames for each step's output.

| Key | Default | Description |
|-----|---------|-------------|
| `output.directory` | `"./output"` | Root output folder. Sub-folders are auto-created. |
| `output.profiler.directory` | `"0 - profiler"` | Sub-folder for Step 0 outputs. |
| `output.profiler.inventory_file` | `"document_inventory.xlsx"` | Master spreadsheet filename. |
| `output.profiler.json_file` | `"document_profiles.json"` | Machine-readable profiles filename. |
| `output.profiler.sections_file` | `"section_inventory.csv"` | Section inventory filename. |
| `output.profiler.tables_file` | `"table_inventory.csv"` | Table inventory filename. |
| `output.profiler.crossrefs_file` | `"crossref_inventory.csv"` | Cross-reference inventory filename. |
| `output.acronyms.directory` | `"1 - acronyms"` | Sub-folder for Step 1 outputs. |
| `output.acronyms.output_file` | `"acronym_audit.xlsx"` | Acronym audit workbook filename. |
| `output.controls.directory` | `"2 - controls"` | Sub-folder for Step 2 outputs. |
| `output.controls.output_file` | `"controls_output.csv"` | CSV output filename. |
| `output.controls.output_file_xlsx` | `"controls_output.xlsx"` | Excel output filename. |
| `output.controls.checkpoint_file` | `"checkpoint.json"` | Checkpoint filename for resume. |
| `output.controls.error_log` | `"errors.log"` | Error log filename. |
| `output.cross_references.directory` | `"3 - cross_references"` | Sub-folder for Step 3 outputs. |
| `output.cross_references.output_file` | `"cross_references.csv"` | Cross-references CSV filename. |
| `output.heading_fixes.directory` | `"4 - heading_fixes"` | Sub-folder for Step 4 outputs. |
| `output.heading_fixes.changes_file` | `"heading_changes.csv"` | Heading changes log filename. |
| `output.split_documents.directory` | `"5 - split_documents"` | Sub-folder for Step 5 outputs. |
| `output.split_documents.manifest_file` | `"split_manifest.csv"` | Split manifest filename. |
| `output.metadata.directory` | `"6 - metadata"` | Sub-folder for Step 6 outputs. |
| `output.metadata.manifest_file` | `"metadata_manifest.csv"` | Metadata manifest filename. |
| `output.markdown.directory` | `"7 - markdown"` | Sub-folder for Step 7 outputs. |
| `output.jsonl.directory` | `"8 - jsonl"` | Sub-folder for Step 8 outputs. |
| `output.validation.directory` | `"9 - validation"` | Sub-folder for Step 9 outputs. |
| `output.validation.output_file` | `"control_validation.csv"` | Validation results filename. |
| `output.validation.review_file` | `"validation_review.xlsx"` | Validation review workbook filename. |
| `output.consolidated_report.enabled` | `true` | Generate a single `.xlsx` workbook with all CSVs after the pipeline completes. |
| `output.consolidated_report.filename_prefix` | `"DPS_Report"` | Prefix for the timestamped report file (e.g., `DPS_Report_2026-03-23_143052.xlsx`). |

**When to change:**
- Change `directory` if you want output written elsewhere.
- Set `consolidated_report.enabled: false` to skip the final Excel workbook.
- Rename output files if your workflow expects different filenames.

---

### Section 3: Document Structure Detection

Keywords the profiler (Step 0) matches against H1 headings to classify standard sections. Documents missing standard sections get flagged as higher priority.

| Key | Default Keywords | Description |
|-----|-----------------|-------------|
| `sections.purpose` | `purpose`, `policy purpose`, `1.0 purpose`, `document purpose` | Keywords identifying the Purpose section. |
| `sections.scope` | `scope`, `policy scope`, `2.0 scope`, `applicability`, `applicability and scope` | Keywords identifying the Scope section. |
| `sections.intent` | `intent`, `policy intent`, `3.0 intent`, `objective`, `policy objective`, `security objective` | Keywords identifying the Intent/Objective section. |
| `sections.controls` | `controls`, `technical controls`, `security controls`, `4.0 controls`, `control requirements`, `requirements`, `policy requirements`, `implementation requirements` | Keywords identifying the Controls section. |
| `sections.appendix` | `appendix`, `appendices`, `5.0 appendix`, `supplementary`, `reference`, `references`, `glossary`, `definitions` | Keywords identifying the Appendix section. |

**When to change:** Only if your organization uses different section names than listed above. For example, if your policies use "Policy Statement" instead of "Purpose", add `"policy statement"` to the `purpose` list.

---

### Section 4: Heading Detection

Controls how headings are detected, classified, and fixed across Steps 0 and 3.

#### Built-in and Custom Styles

| Key | Default | Description |
|-----|---------|-------------|
| `headings.builtin_styles` | `Heading 1` through `Heading 4` (both cases) | Standard Word heading style names. Rarely needs editing. |
| `headings.custom_heading_styles` | `Policy Heading 1`, `Policy Heading 2`, `TOC Heading`, `AppendixHeading` | Custom heading style names used in your org's Word templates. Add styles here if they show up as "FAKE" in the profiler but are real headings in Word. |
| `headings.custom_style_map` | See config file | Maps your org's custom style names to standard `Heading 1`/`2`/`3` (case-insensitive keys). Used by Step 4 to convert styles the splitter can recognize. |

**How to find your org's custom styles:** In Word, click a heading, then check the Styles pane on the Home tab for the active style name.

#### Fake Heading Detection

A "fake heading" is bold text with no Word Heading style applied. The profiler flags these; the heading fixer converts them.

| Key | Default | Description |
|-----|---------|-------------|
| `headings.fake_heading_min_font_size` | `12` | Minimum font size (pt) for bold text to be considered a fake heading. Lower to `11` if too few detected; raise to `13`-`14` if too many false positives. |
| `headings.fake_heading_max_chars` | `200` | Maximum character length for profiler fake heading detection (wider net for review). |
| `headings.fake_heading_max_chars_fixer` | `120` | Maximum character length for fixer fake heading conversion (tighter to avoid false positives). |

#### Heading Level Assignment

Regex patterns that determine what heading level to assign to a fake heading based on its numbering.

| Key | Default | Description |
|-----|---------|-------------|
| `headings.heading1_pattern` | `^(?:\d+\.0\s+\|[IVXLC]+\.\s+)` | Matches H1 numbering (e.g., "1.0 Purpose", "III. Controls"). |
| `headings.heading2_pattern` | `^(?:\d+\.\d+\s+\|[A-Z]\.\s+)` | Matches H2 numbering (e.g., "1.1 Access", "A. Overview"). |
| `headings.heading3_pattern` | `^\d+\.\d+\.\d+\s+` | Matches H3 numbering (e.g., "1.1.1 Sub-section"). |
| `headings.default_heading_level` | `2` | Default level when no numbering pattern matches. Change to `1` if your un-numbered bold headings are mostly top-level. |

---

### Section 4B: Text Deletion & Document Cleanup

Remove noise from documents during heading style fixing (Step 4). All cleanup operations cascade to Steps 5, 6, 7, and 8.

#### Phrase & Section Deletion

| Key | Default | Description |
|-----|---------|-------------|
| `text_deletions.enabled` | `false` | Set to `true` to activate phrase and section deletion. |
| `text_deletions.case_sensitive` | `true` | Whether phrase matching is case-sensitive. |
| `text_deletions.phrases` | `[]` (empty) | List of exact phrases to delete. After deletion, double-spaces are collapsed to single spaces. |
| `text_deletions.section_deletions` | `[]` (empty) | List of section-level deletions. Each entry has `heading` (case-insensitive substring match on heading text), `delete` (TRUE/FALSE), and optional `description`. Deletes the heading and all content until the next heading of same or higher level. |

#### Document Cleanup Toggles

These boolean toggles enable additional cleanup operations independent of the `enabled` setting above:

| Key | Default | Description |
|-----|---------|-------------|
| `text_deletions.remove_table_of_content` | `false` | Remove paragraphs with Word TOC styles (`TOC 1`, `TOC 2`, `TOC 3`, etc.). These are generated by Word's Insert Table of Contents feature and cannot be caught by section deletion. Eliminates page-number noise like `"4.1 Access Control .......... 12"` from Copilot retrieval. |
| `text_deletions.remove_headers_footers` | `false` | Clear all page header and footer text (branding, page numbers, classification banners). Uses a safe approach — empties run text rather than removing XML parts. |
| `text_deletions.remove_revision_tables` | `false` | Remove revision/change history tables detected by column headers containing "version" + "date" + "changes"/"description"/"author". Catches tables that don't live under a "Revision History" heading. |
| `text_deletions.flatten_definition_tables` | `false` | Convert Terms & Definitions tables (under headings matching "Terms", "Definitions", or "Glossary") to prose paragraphs in the format `**Term**: Definition`. The section heading is preserved. |

**Example phrases (on the Text Deletions sheet):**
| Value | Description |
|-------|-------------|
| DRAFT - NOT FOR DISTRIBUTION | Watermark text |
| CONFIDENTIAL | Classification banner |
| [INSERT DATE] | Placeholder text |
| TBD | Placeholder text |

**Example section deletions:**
| Section Heading | Delete | Description |
|-----------------|--------|-------------|
| Table of Contents | TRUE | Remove TOC section (under a heading) |
| Revision History | TRUE | Version tracking noise |
| Change History | TRUE | Version tracking noise |
| Document Information | TRUE | Metadata already captured by Step 0/6 |

Set `enabled` to TRUE and `case_sensitive` to TRUE or FALSE as needed in the settings block above the phrases list.

> **Warning:** Deletions are permanent in the output files. Original input files are never modified. Review `heading_changes.csv` after running to verify what was removed.

---

### Section 5: Cross-Reference Detection

Controls cross-reference detection for Step 0 (profiling) and Step 2 (extraction).

#### Profiler Patterns (Step 0)

Regex patterns for counting cross-references during profiling. These are used for metrics only.

| Key | Default Patterns |
|-----|-----------------|
| `cross_references.profiler_patterns` | `see section\s+[\d\.]+[a-z]?`, `refer to\s+(section\|the)`, `as described in\s+(the\|section)`, `per section\s+[\d\.]+`, `in accordance with\s+(the\|section)`, `as defined in\s+(the\|section)`, `as outlined in\s+(the\|section)`, `per the organization's\s+\w+`, `see the\s+\w+\s+policy`, `as specified in\s+(the\|section)` |

#### Extraction Patterns (Step 2)

Each entry has a `phrase` (lead-in text) and `type` (`"internal"` or `"external"`):

- **Internal** patterns match `"<phrase> Section <number>"` (e.g., "See Section 4.3")
- **External** patterns match `"<phrase> [the] <Document Name>"` where the final word is in `document_name_keywords`

Default enabled patterns:

| Phrase | Type |
|--------|------|
| `see` | internal |
| `refer to` | internal |
| `per` | internal |
| `as described in` | internal, external |
| `as defined in` | internal, external |
| `refer to` | external |
| `in accordance with` | external |

Additional commented-out patterns in the config: `as outlined in`, `as specified in`, `pursuant to`, `noted in`, `as required by`, `consistent with`, `established in`, `governed by`, `mandated by`.

#### Other Cross-Reference Settings

| Key | Default | Description |
|-----|---------|-------------|
| `cross_references.detect_hyperlink_crossrefs` | `true` | Detect hyperlinks whose display text looks like a section or policy reference. |
| `cross_references.detect_urls` | `true` | Extract URLs from hyperlinks and bare text. |
| `cross_references.document_name_keywords` | `Policy`, `Standard`, `Plan`, `Procedure`, `Guide`, `Guideline`, `Program`, `Framework`, `Charter` | External patterns match document names ending in one of these keywords. Add keywords like `"Manual"`, `"Directive"`, `"Handbook"` if your org uses them. |

---

### Section 6: Table Classification

Keywords matched against table header rows to classify table types in Step 0.

| Table Type | Keywords | Min Columns |
|------------|----------|-------------|
| `control_matrix` | control id, control, requirement, framework, nist, status, implementation, responsible, owner | 3 |
| `applicability_table` | applies to, applicability, system, environment, in scope, yes, no, n/a | 2 |
| `reference_table` | term, definition, acronym, glossary, abbreviation, description | 2 |
| `crosswalk_table` | nist, cis, cmmc, iso, mapping, alignment, framework | 3 |
| `role_responsibility` | role, responsibility, responsible, accountable, raci | 2 |

**When to change:** Add keywords if your tables use different header terminology (e.g., add `"obligation"` to `control_matrix` if your org uses that instead of "requirement").

---

### Section 7: Document Type Classification

Auto-classifies documents into types based on content analysis in Step 0.

| Type | Rule | Description |
|------|------|-------------|
| **Type A** (Table-Heavy) | >40% of character content in tables | Documents dominated by control matrices and reference tables. |
| **Type B** (Prose-Heavy) | <10% of character content in tables | Narrative policy documents with minimal tabular data. |
| **Type C** (Hybrid) | 10-40% tables | Most common — mix of prose and tables. |
| **Type D** (Appendix-Dominant) | >60% of content in appendix sections | Documents where appendices dwarf the main body. |
| **Type E** (Unclassified) | Doesn't fit A-D | Catch-all for unusual structures. |

| Key | Default | Description |
|-----|---------|-------------|
| `classification.type_a.min_table_content_pct` | `40` | Minimum table content percentage for Type A. |
| `classification.type_b.max_table_content_pct` | `10` | Maximum table content percentage for Type B. |
| `classification.type_c.procedure_keywords` | `step 1`, `step 2`, `procedure`, `escalation`, `workflow`, `response process`, `playbook` | Keywords that signal embedded procedures in hybrid docs. |
| `classification.type_d.min_appendix_content_pct` | `60` | Minimum appendix content percentage for Type D. |

---

### Section 8: Size & Optimization Thresholds

| Key | Default | Description |
|-----|---------|-------------|
| `thresholds.max_characters` | `36000` | Maximum characters per sub-document. 36,000 ~ 20 pages, fits Copilot Studio / GPT-4o context window. Increase for larger context windows; decrease (try `18000`) for tighter splits. |
| `thresholds.max_pages` | `20` | Approximate page equivalent (reporting only). |
| `thresholds.paragraphs_per_page` | `30` | Used for page estimation. Lower to `20`-`25` if estimates are too high; raise to `35`-`40` if too low. |
| `thresholds.chars_per_page` | `1800` | Characters per page for split manifest estimates. Lower (`1200`) for table-heavy docs; higher (`2200`) for dense prose. |
| `thresholds.section_dominance_pct` | `50` | Flag sections exceeding this percentage of total document length. |
| `thresholds.high_table_count` | `10` | Flag documents with more tables than this threshold. |

**Key setting:** `max_characters` is the most impactful threshold. It determines how aggressively documents are split. Lower values produce smaller, more focused chunks; higher values preserve more context per chunk.

---

### Section 9: Priority Scoring

Controls how the profiler (Step 0) ranks documents by optimization difficulty. Higher score = more work needed = process sooner.

#### Weights

| Key | Default | Description |
|-----|---------|-------------|
| `priority_scoring.weights.table_count` | `2.0` | More tables = harder to optimize. |
| `priority_scoring.weights.cross_ref_count` | `1.5` | More cross-references = more manual work. |
| `priority_scoring.weights.fake_heading_count` | `1.0` | Fake headings break chunking. |
| `priority_scoring.weights.page_count` | `0.5` | Longer documents need more splitting. |
| `priority_scoring.weights.missing_sections` | `1.5` | Missing standard sections = structural problems. |
| `priority_scoring.weights.merged_cells` | `1.0` | Merged cells complicate table flattening. |
| `priority_scoring.weights.over_size_limit` | `3.0` | Over character limit is a hard retrieval problem. |

Weights are relative — adjust ratios to change what matters most for your environment.

#### Per-Document Usage Frequency (Optional)

Boost priority for frequently-used documents. Scale: 0-10, multiplied by 2.0 and added to priority.

On the **Priority Scoring** sheet under `# Usage Frequency`, add rows with the filename in the Key column and score in the Value column:

| Key | Value |
|-----|-------|
| Access_Control_Policy_POL-AC-2026-001.docx | 9 |
| Incident_Response_Policy_POL-IR-2026-003.docx | 8 |

Filenames must match exactly. Default: empty (no boost).

---

### Section 10: Key Term Search

Search for specific terms across all documents in Step 0. Results appear as columns in the Document Inventory Excel.

| Key | Default | Description |
|-----|---------|-------------|
| `search_terms.enabled` | `true` | Enable/disable key term search. |
| `search_terms.terms` | `["AC", "Cloud", "NIST"]` | List of terms to search for. Each term gets its own column. Plain text only (no regex). |
| `search_terms.match_mode` | `"word"` | `"word"` = whole-word boundary (e.g., "AC" matches "AC-1" but not "ACCESS"). `"substring"` = anywhere in text (e.g., "AC" matches "ACCESS", "PRACTICAL"). |
| `search_terms.show_counts` | `true` | `true` = show occurrence count. `false` = show YES/blank. |

---

### Section 11: Control Extraction

Controls how Step 2 extracts structured control data from documents. All settings are on the **Control Extraction** sheet in `dps_config.xlsx`.

The sheet is organized into 7 blocks (separated by blue `# Sub-header` rows):

#### Block 1: Common Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `require_bold_control_id` | TRUE | Only extract control IDs that appear in bold text. Set FALSE if your IDs aren't bold. |
| `enable_checkpoint` | TRUE | Save progress so re-runs skip already-processed files. Delete `checkpoint.json` to force a fresh run. |
| `output_format` | `both` | Output format: `csv`, `xlsx`, or `both` (dropdown). |

#### Block 2: Control ID Patterns (Regex)

One regex pattern per row in column A. The extractor scans document text for matches.

**Default patterns (pre-populated):**

| Pattern | Matches |
|---------|---------|
| `\b[A-Z]{2,4}[-.]?\d{1,3}[-.]\d{2,4}\b` | AC-1.001, IR001.002, CFG.1.0042 |
| `\b[A-Z]{2,4}\s+\d{1,3}\.\d{2,4}\b` | AUP 1.001, ACC 01.001 (space-separated) |
| `\b[A-Z]{2,4}\d{2,3}\.\d{2,4}\b` | ACC01.001 (no separator before digits) |

**How to add patterns:** Insert a new row below the existing patterns and enter your regex in column A. There is no limit on the number of patterns.

**If zero controls are extracted**, your IDs likely use a different format. Common alternatives:

| Pattern | Matches |
|---------|---------|
| `\b[A-Z]{2,4}-\d{1,3}\b` | Simple: AC-1, IR-3 |
| `\b[A-Z]{2,4}\.\d{1,3}\.\d{1,3}\b` | Dotted: AC.1.1, IR.3.2 |

> **Tip:** Test your regex at [regex101.com](https://regex101.com) before adding. Make sure to select the "Python" flavor.

#### Block 3: Whitelist / Blacklist

Filter which controls are kept or excluded after extraction. **One control ID per row** in column A, prefixed with `whitelist:` or `blacklist:`.

**Format:** Each entry is `whitelist:ID` or `blacklist:ID` — the prefix tells the parser which list it belongs to.

| Entry in column A | Effect |
|-------------------|--------|
| `whitelist:AC-1.001` | Keep only this exact control (whitelist) |
| `whitelist:AC-*` | Keep all controls starting with "AC-" (wildcard) |
| `blacklist:IR-2.003` | Exclude this exact control (blacklist) |
| `blacklist:DRAFT-*` | Exclude all controls starting with "DRAFT-" |

**Rules:**
- **No limit** on the number of entries — add as many rows as needed.
- If the whitelist has **any** entries, **only** matching controls are kept. Leave the whitelist empty to keep all controls.
- The blacklist is applied **after** the whitelist. Use it to carve out exceptions.
- Supports **exact IDs** (e.g., `AC-1.001`) and **prefix wildcards** (e.g., `AC-*`). The `*` must be at the end.
- **Leave this entire block empty** (no `whitelist:` or `blacklist:` rows) to keep all extracted controls — this is the default.

**Examples:**

*Keep only Access Control and Incident Response controls:*
| Column A |
|----------|
| `whitelist:AC-*` |
| `whitelist:IR-*` |

*Keep everything except drafts and a specific obsolete control:*
| Column A |
|----------|
| `blacklist:DRAFT-*` |
| `blacklist:AC-99.001` |

*Keep only AC controls, but exclude AC-0 series:*
| Column A |
|----------|
| `whitelist:AC-*` |
| `blacklist:AC-0*` |

#### Block 4: Guidance Keywords

One keyword per row in column A. When a paragraph contains one of these keywords, text after it is classified as "supplemental guidance" rather than "control description."

| Default Keywords |
|-----------------|
| implementation guidance |
| implementation: |
| guidelines: |
| how to implement |
| supplemental guidance |

**How to add:** Insert a new row and type the keyword in column A. No limit on entries.

#### Block 5: Metadata Triggers

Two-column table (Category | Keyword) that controls how the extractor finds document-level metadata (purpose, scope, applicability). The extractor scans the first N paragraphs (set by `metadata_scan_paragraphs`) for these keywords.

| Category (col A) | Keyword (col B) |
|-------------------|----------------|
| purpose | purpose |
| purpose | objective |
| purpose | intent |
| scope | scope |
| scope | coverage |
| scope | boundary |
| applicability | applicability |
| applicability | applies to |
| applicability | applies for |

**How to add:** Insert a row with the category in column A and keyword in column B. You can add multiple keywords per category.

#### Block 6: Heading Detection (Advanced)

Controls how the extractor identifies section headings within documents. These settings use dot-notation (e.g., `heading_detection.detect_allcaps`).

| Setting | Default | Description |
|---------|---------|-------------|
| `heading_detection.use_word_heading_style` | TRUE | Use Word heading styles as section boundaries. |
| `heading_detection.section_keyword_pattern` | `^[Ss]ection\s+\d{1,2}` | Regex for "Section N" style headings. |
| `heading_detection.numbered_title_pattern` | `^\d{1,2}\.?\d{0,2}\s+[A-Z][a-zA-Z\s]{3,50}$` | Regex for numbered title headings. |
| `heading_detection.detect_allcaps` | TRUE | Detect ALL-CAPS text as section headers. |
| `heading_detection.allcaps_max_length` | 80 | Max character length for ALL-CAPS detection. |
| `heading_detection.allcaps_min_words` | 3 | Minimum word count for ALL-CAPS detection. |
| `heading_detection.detect_bold_short` | TRUE | Detect bold short text as section headers. |
| `heading_detection.bold_max_length` | 60 | Max character length for bold heading detection. |

#### Block 7: Implementation Trigger

| Setting | Default | Description |
|---------|---------|-------------|
| `implementation_trigger` | `(?i)(implementation guidance\|...)` | Regex for guidance boundary within a control block. Combines the guidance keywords into a single pattern. |
| `metadata_scan_paragraphs` | 40 | How many paragraphs from the top of each doc to scan for metadata triggers. |

---

### Section 11b: Pipeline Steps

Enable or disable individual steps. You can still run disabled steps explicitly with `--step N`.

On the **Pipeline** sheet, each row is a step with columns: Step | Name | Script | Enabled | Description.

| Key | Description |
|-----|-------------|
| `Enabled` column | Set to FALSE to skip a step when running the full pipeline. The step can still be run explicitly with `--step N`. |

---

### Section 12: Metadata Injection

Controls how Step 6 stamps sub-documents with identity metadata.

#### Placement and Formatting

| Key | Default | Description |
|-----|---------|-------------|
| `metadata.placement` | `"top"` | Where to insert the metadata block: `"top"` (best for most RAG scenarios), `"top_and_bottom"` (for longer chunks where top may be truncated), `"each_page"` (Word header on every page, for Word/PDF viewing). |
| `metadata.add_separator` | `true` | Add a horizontal rule after the metadata block. |
| `metadata.font_size` | `8` | Font size (pt) for metadata text. |
| `metadata.label_color` | `"2F5496"` | Hex RGB color for metadata labels (blue). |

#### Fields

Each metadata field can be independently enabled/disabled and reordered:

| Field Key | Label | Source | Description |
|-----------|-------|--------|-------------|
| `name` | Document | `auto` | Resolved from filename + split manifest. |
| `url` | URL | `auto` | Resolved from Excel lookup or fallback template. |
| `scope` | Scope | `auto` | Extracted from profiler data (Step 0) or direct doc scan. |
| `intent` | Intent | `auto` | Extracted from profiler data (Step 0) or direct doc scan. |
| `tags` | Tags | `auto` | Generated from doc type, sections, acronyms. |

Custom field examples (on the **Metadata** sheet under `# Metadata Fields`):

| Key | Label | Enabled | Source | Value |
|-----|-------|---------|--------|-------|
| classification | Classification | TRUE | static | CUI // SP-NOFORN |
| owner | Document Owner | TRUE | excel | *(leave blank — set Excel Column below)* |

For `excel` source fields, also add the `excel_column` setting (e.g., `Owner`) — this must match a column header in your `Doc_URL.xlsx` file.

#### URL Resolution

**One file, two steps:** The `input/Doc_URL.xlsx` file provides document URLs to both Step 2 (Published URL column in controls output) and Step 6 (URL field in metadata blocks). You only need to maintain one URL mapping file.

Resolution order (Step 6): Excel lookup → fallback template → "(URL not configured)"
Resolution order (Step 2): Excel lookup → empty string

**Excel lookup file format**

A template `Doc_URL.xlsx` is included in the `input/` folder with two columns:

| Document_Name | URL |
|---|---|
| Access Control Policy | https://contoso.sharepoint.com/.../Access_Control_Policy.docx |
| Incident Response Policy | https://contoso.sharepoint.com/.../Incident_Response_Policy.docx |

- Extra columns are fine — they are ignored unless referenced as custom fields.
- The file can be on any sheet; set `metadata.url.sheet` to the sheet name or index (0 = first).
- Rows with a blank name or URL are skipped.

**Recommended workflow:**

1. Run Step 0 or Step 2 first to discover the exact document names in your input folder.
2. Open `input/Doc_URL.xlsx` and enter each document name in the `Document_Name` column with its corresponding published URL.
3. Re-run Step 2 to populate the `published_url` column in controls output, or run Step 6 to stamp URLs into metadata blocks.

**How matching works**

Matching is **case-insensitive substring**: the Excel name is checked against the document name derived from the filename (underscores converted to spaces, extension stripped). A match occurs if either string contains the other. For example, `"Access Control"` in Excel will match a file named `Access_Control_Policy_v2.docx`.

Because matching is bidirectional, shorter entries match more broadly — `"Policy"` alone would match every document with "Policy" in its name. Use enough of the document name to be unique.

**Configuration**

The default config points to `input/Doc_URL.xlsx`. These settings are on the **Metadata** sheet:

| Setting | Value | Description |
|---------|-------|-------------|
| url.lookup_file | ./input/Doc_URL.xlsx | Path to URL lookup spreadsheet |
| url.name_column | Document_Name | Must match your Excel column header exactly |
| url.url_column | URL | Must match your Excel column header exactly |
| url.sheet | 0 | 0 = first sheet, or use the sheet name as a string |

**If matching fails**, Step 2 and Step 6 will print a warning listing the column headers actually found in your file — use that to spot header typos.

| Key | Default | Description |
|-----|---------|-------------|
| `metadata.url.lookup_file` | `"./input/Doc_URL.xlsx"` | Path to the Excel file mapping document names to URLs. Leave empty to skip. |
| `metadata.url.name_column` | `"Document_Name"` | Column header in the Excel file for document names. |
| `metadata.url.url_column` | `"URL"` | Column header in the Excel file for URLs. |
| `metadata.url.sheet` | `0` | Sheet name (string) or index (0 = first sheet). |
| `metadata.url.fallback_template` | `""` | URL template when no Excel match is found (Step 6 only). Use `{filename}` as placeholder. Example: `"https://contoso.sharepoint.com/sites/Policies/Shared Documents/{filename}"` |

#### Advanced Metadata Settings

| Key | Default | Description |
|-----|---------|-------------|
| `metadata.max_scope_chars` | `300` | Maximum characters for scope text extraction. |
| `metadata.max_intent_chars` | `300` | Maximum characters for intent text extraction. |
| `metadata.tags.include_doc_type` | `true` | Add document type tag (e.g., "Type-B"). |
| `metadata.tags.include_sections_found` | `true` | Add tags for detected sections (e.g., "has-scope", "has-controls"). |
| `metadata.tags.acronym_definitions_file` | `"./input/Acronym_Definitions.xlsx"` | Path to the human-verified Acronym Definitions file (same file used by Steps 7/8). Preferred source for acronym tags. |
| `metadata.tags.acronym_audit_file` | `""` | Path to raw Acronym Finder output Excel. Used as fallback only when no definitions file is found. |
| `metadata.tags.max_acronym_tags` | `15` | Maximum acronym tags per document (most-frequent first). `0` = unlimited. |
| `metadata.tags.static_tags` | `[]` | Static tags added to ALL documents (e.g., `["InfoSec", "GCC-High"]`). |

#### Custom Tags (Per-Document)

You can assign custom tags to individual documents by adding a **"Custom Tags"** sheet to your `Acronym_Definitions.xlsx` file (or `acronym_audit.xlsx`). These are **merged** with auto-generated tags — nothing is overwritten, no separate file needed.

**Setup:**

Open `input/Acronym_Definitions.xlsx` and add a sheet called **"Custom Tags"** with two columns:

| Document_Name | Tags |
|---|---|
| Access Control Policy | CUI, FedRAMP-High, Priority |
| Incident Response Policy | SOC, CIRT, Critical-Path |
| Data Protection Policy | PII, Encryption |

That's it — no config changes needed. Step 6 reads the "Custom Tags" sheet automatically when it loads the acronym definitions file. Step 8 (JSONL) also reads from the same sheet.

> **Tip:** If you run Step 1 (Acronym Finder) first, the output `acronym_audit.xlsx` already includes an empty "Custom Tags" sheet pre-populated with document names — just fill in the Tags column.

**How it works:**
- Tags are comma-separated in the Tags column
- Document name matching is case-insensitive and normalized (handles underscores, extensions, suffixes)
- Custom tags appear **after** auto-generated tags (doc type, sections, acronyms) and **before** static tags
- Duplicates across all tag sources are automatically removed (first occurrence wins)
- Auto-generated acronym tags, validation steps (Step 9), and all other pipeline steps are **completely unaffected**

**Example result** for "Access Control Policy":
```
Tags: Type-C, has-scope, has-controls, AC, MFA, CUI, FedRAMP-High, Priority, InfoSec
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^
       auto-generated (doc type + sections + acronyms)   custom tags           static tags
```

---

### Section 13: DOCX to Markdown (`docx2md`)

All settings live under the `docx2md:` key in `dps_config.xlsx`. This section controls **Step 7** (`scripts/docx2md.py`) and its standalone invocation.

#### General Settings

| Key | Default | Description |
|-----|---------|-------------|
| `output_directory` | `./output/7 - markdown` | Where converted `.md` files are written (relative to config file). |
| `include_metadata_frontmatter` | `true` | Write YAML frontmatter block at the top of each `.md` file. |
| `metadata_placement` | `top` | `top` = frontmatter only, `top_and_bottom` = also appends a readable metadata block at the end of the file. |
| `table_strategy` | `auto` | `markdown` = always use pipe tables, `html` = always use HTML tables, `auto` = use HTML only for tables with merged cells. |
| `image_handling` | `extract` | `extract` = save images to a `<docname>_images/` subfolder and insert Markdown image links, `skip` = ignore images. |
| `extract_text_boxes` | `true` | Extract floating text box content and insert it inline in the document body. |
| `clean_smart_quotes` | `true` | Replace curly quotes (`""`), en/em dashes, and ellipsis with ASCII equivalents. |
| `strip_zero_width_chars` | `true` | Remove zero-width and BOM characters from output. |
| `promote_control_ids_to_heading` | `true` | Promote paragraphs matching a control ID pattern to H2 headings. Uses `control_extraction` patterns from the main pipeline config. |
| `max_heading_level` | `2` | Maximum heading depth in output. Headings deeper than this level are collapsed (e.g., `2` means H3+ becomes H2). Set to `6` to disable. |
| `log_file_prefix` | `docx2md_log` | Prefix for the timestamped Excel log file (e.g., `docx2md_log_2026-03-24_143052.xlsx`). |

#### Metadata Fields

Configured as a list under `docx2md.metadata_fields`. Each entry produces one key in the YAML frontmatter. Fields are written in the order listed.

```yaml
metadata_fields:
  - name: "fieldName"     # key name in the frontmatter
    source: "source_type" # where the value comes from
    default: ""           # fallback if source returns nothing
```

**Built-in source types:**

| Source | Example | Description |
|--------|---------|-------------|
| `filename` | `filename` | Basename of the `.docx` file |
| `converted_date` | `converted_date` | ISO timestamp of the conversion run |
| `doc_url` | `doc_url` | URL from `input/Doc_URL.xlsx` (same file used by pipeline Steps 1 and 5) |
| `core:<prop>` | `core:title`, `core:author`, `core:created` | Word core document properties |
| `filename_regex:<pattern>` | `filename_regex:([A-Z]+-\d{4}-\d+)` | Regex applied to the filename stem; returns first capture group |
| `static:<value>` | `static:InfoSec` | Literal value stamped on every document |
| `excel_lookup_list:<file>:<sheet>:<key>:<value>` | See below | Multi-value lookup from any Excel file; returns a YAML list |

**`excel_lookup_list` format:**

Reads all rows in `<sheet>` where `<key>` column matches the current `.docx` filename, and returns all matching `<value>` column entries as a YAML list (e.g., `["MFA", "NIST", "RAG"]`). Matching is case-insensitive and normalizes underscores, hyphens, and spaces — so `Policy_Doc.docx` matches an Excel entry of `Policy-Doc` or `policy doc`.

```yaml
- name: "Tags"
  source: "excel_lookup_list:./input/Acronym_Definitions.xlsx:Acronym Definitions:Document:Acronym"
  default: ""
```

The `doc_url` source loads the URL mapping automatically when any field uses it — `include_doc_url: true` is not required when using `metadata_fields`.

#### Renaming a Metadata Field Across the Dual Config Layers

Metadata field names (the keys that appear in JSONL chunks and Markdown frontmatter) are defined in multiple places due to the dual config system. Renaming a field — for example, changing `acronyms` to `Tags` — requires updates in **all** of these locations or the old name will persist in some outputs.

**Where field names live:**

| Layer | File | What to change |
|-------|------|----------------|
| **YAML fallback** | `dps_config_fallback.yaml` | Find the `- name: "oldName"` entry under `docx2md.metadata_fields` and change it |
| **Generator defaults** | `generate_config_template.py` | Find the `{"name": "oldName", ...}` entry in the default `metadata_fields` list (look for `_build_docx2md_sheet`) and change it |
| **Excel config** | `dps_config.xlsx` | Regenerate from YAML after updating the above: `python generate_config_template.py --from-yaml dps_config_fallback.yaml` |
| **JSONL script** | `scripts/docx2jsonl.py` | Search for `chunk["oldName"]` and rename the key — this script hardcodes the acronym/tag field name rather than reading it from config |

**Step-by-step:**

1. **Edit `dps_config_fallback.yaml`** — change the `name:` value in the `metadata_fields` list (under `docx2md:`)
2. **Edit `generate_config_template.py`** — change the matching `{"name": ...}` entry in the default metadata fields
3. **Regenerate the Excel config:**
   ```bash
   python generate_config_template.py --from-yaml dps_config_fallback.yaml --output dps_config.xlsx
   ```
4. **Edit `scripts/docx2jsonl.py`** — rename the hardcoded chunk key (e.g., `chunk["Tags"] = ...`)
5. **Verify** — re-run Steps 7 and 8 on a test document and confirm the new key name appears in both `.md` frontmatter and `.jsonl.txt` output

> **Why is this spread across so many files?** The Markdown converter (`docx2md.py`) reads field names dynamically from config, so updating config is enough for `.md` output. But `docx2jsonl.py` writes the acronym/tag field with a hardcoded key name, so it requires a code change too. The YAML fallback, generator, and Excel config are three representations of the same settings — all three must agree, and the generator is the bridge between them.

> **Tip:** If you only use the Excel config (not the YAML fallback), you can skip step 1 and instead edit the field name directly on the **Docx2md** sheet in `dps_config.xlsx`. But you'll still need step 4 (the JSONL script edit), and the next time you regenerate the Excel from YAML, your manual edit will be overwritten unless the YAML is also updated.

---

## Output Reference

After a full pipeline run, the output directory looks like this:

```
output/
  0 - profiler/
    document_inventory.xlsx        # Master spreadsheet (START HERE)
    document_profiles.json         # Machine-readable profiles
    section_inventory.csv          # One row per section per doc
    table_inventory.csv            # One row per table per doc
    crossref_inventory.csv         # One row per cross-reference

  1 - acronyms/
    acronym_audit.xlsx             # Multi-sheet acronym report (Global Summary, Per Document, etc.)

  2 - controls/
    controls_output.csv            # One row per control
    controls_output.xlsx           # Same data in Excel
    checkpoint.json                # Resume progress tracker
    errors.log                     # Extraction errors

  3 - cross_references/
    cross_references.csv           # One row per cross-reference

  4 - heading_fixes/
    *_fixed.docx                   # Fixed documents (one per input)
    heading_changes.csv            # Change log

  5 - split_documents/
    [Name] - [Heading].docx        # Sub-documents
    split_manifest.csv             # Manifest of all splits

  6 - metadata/
    [Name] - [Heading].docx        # Sub-documents with metadata
    metadata_manifest.csv          # What metadata was applied

  7 - markdown/
    *.md                           # One Markdown file per .docx
    docx2md_log_<timestamp>.xlsx   # Per-file conversion log

  8 - jsonl/
    *.jsonl.txt                    # One chunked JSONL file per .docx

  9 - validation/
    control_validation.csv         # PASS/MISSING/RELOCATED per control
    validation_review.xlsx         # Confidence-scored controls for human review

  DPS_Report_<timestamp>.xlsx      # Consolidated workbook (all CSVs)
```

The **consolidated report** (`DPS_Report_*.xlsx`) contains one styled sheet per step's CSV/Excel output, with blue headers, frozen top row, autofilter, and auto-sized columns.

**Consolidated report sheets:**

| Sheet Name | Source Step | Source File | Contents |
|------------|-----------|-------------|----------|
| Pipeline Issues | (all) | `pipeline_issues.csv` | Warnings/errors from the run (always first, only present if issues exist) |
| 0 - Document Inventory | Step 0 | `document_inventory.xlsx` | Master document metrics (one row per document) |
| 0 - Sections | Step 0 | `section_inventory.csv` | One row per section per document |
| 0 - Tables | Step 0 | `table_inventory.csv` | One row per table per document |
| 0 - CrossRefs | Step 0 | `crossref_inventory.csv` | One row per cross-reference candidate |
| 1 - Controls | Step 2 | `controls_output.csv` | One row per extracted control |
| 2 - Cross References | Step 3 | `cross_references.csv` | One row per cross-reference |
| 3 - Heading Changes | Step 4 | `heading_changes.csv` | Every heading style change made |
| 4 - Split Manifest | Step 5 | `split_manifest.csv` | Every sub-document created |
| 5 - Metadata | Step 6 | `metadata_manifest.csv` | Metadata applied to each sub-document |
| 6 - Validation | Step 9 | `control_validation.csv` | PASS/MISSING/RELOCATED per control |
| 6 - Validation Review | Step 9 | `validation_review.xlsx` | Confidence-scored controls for human review |
| 6 - Validation Summary | Step 9 | `validation_review.xlsx` | Aggregate validation statistics |

Sheets are only included when the source file exists (i.e., the corresponding step has been run).

---

## File Lifecycle: What to Keep, What to Delete

The pipeline produces two kinds of files: **human-validated input files** that require effort to create and should be preserved, and **pipeline-generated output files** that can be regenerated at any time.

### Human-Validated Files (Do Not Delete)

These files live in `input/` and represent curated, reviewed data consumed by multiple pipeline steps. Deleting them means repeating the human review process.

| File | How It's Created | What Depends On It |
|------|-----------------|-------------------|
| **`input/*.docx`** | Source policy documents from your organization | Everything — the pipeline starts here |
| **`input/Doc_URL.xlsx`** | You create this manually. Run Step 0 or 2 first to discover document names, then enter each name and its SharePoint URL. | Steps 2, 6, 7, 8 use it for Published URL in controls, metadata blocks, MD frontmatter, and JSONL chunks |
| **`input/Acronym_Definitions.xlsx`** | Run Step 1 to generate `acronym_audit.xlsx`, then review and curate: remove false positives, confirm definitions, fill in Custom Tags. Save the curated copy to `input/Acronym_Definitions.xlsx`. See [Acronym Definitions Lifecycle](#acronym-definitions-lifecycle) below. | Steps 6, 7, 8 use it for acronym tags, custom tags, MD frontmatter lists, and JSONL chunk metadata |
| **`dps_config.xlsx`** | Generated once by `generate_config_template.py`, then tuned by you over multiple pipeline runs | All steps read this for their settings |

**Backup strategy:** Back up `input/` and `dps_config.xlsx` before major changes. These files contain human judgment that cannot be regenerated.

### Pipeline Output Files (Safe to Delete)

Everything under `output/` is machine-generated. Re-running the relevant step recreates it. Delete freely to save space or start fresh.

| Folder | Step | Safe to Delete? | Notes |
|--------|------|----------------|-------|
| `output/0 - profiler/` | Step 0 | Yes | Re-run `--step 0`. Step 6 reads `document_profiles.json` from here — re-run Step 0 before Step 6 if deleted. |
| `output/1 - acronyms/` | Step 1 | Yes | Re-run `--step 1`. This is the **unvalidated** audit — your curated version is `input/Acronym_Definitions.xlsx`. |
| `output/2 - controls/` | Step 2 | Yes | Re-run `--step 2`. Delete `checkpoint.json` to force a full re-extraction. |
| `output/3 - cross_references/` | Step 3 | Yes | Re-run `--step 3`. |
| `output/4 - heading_fixes/` | Step 4 | Yes | Re-run `--step 4`. Step 5 reads from here — re-run Step 4 before Step 5 if deleted. |
| `output/5 - split_documents/` | Step 5 | Yes | Re-run `--step 5`. Steps 6 and 9 read from here. |
| `output/6 - metadata/` | Step 6 | Yes | Re-run `--step 6`. Steps 7/8 can optionally read from here. |
| `output/7 - markdown/` | Step 7 | Yes | Re-run `--step 7`. |
| `output/8 - jsonl/` | Step 8 | Yes | Re-run `--step 8`. |
| `output/9 - validation/` | Step 9 | Yes | Re-run `--step 9`. If you've reviewed `validation_review.xlsx` and run the feedback script, back up `confirmed_controls.csv` first — that file contains your review decisions. |
| `output/DPS_Report_*.xlsx` | Pipeline | Yes | Re-run the pipeline to regenerate. |

### How the Validated Files Are Created

```
1. Run Step 0             → Discover document names in your input folder
2. Run Step 1             → Get raw acronym candidates (acronym_audit.xlsx)
3. Create Doc_URL.xlsx    → Open input/Doc_URL.xlsx, enter document names + URLs
                            from Step 0 output. One row per document.
4. Create Acronym_Definitions.xlsx
                          → Open Step 1's acronym_audit.xlsx. Review the
                            "Acronym Definitions" sheet — remove false positives,
                            confirm definitions. Fill in "Custom Tags" sheet with
                            per-document tags. Save to input/Acronym_Definitions.xlsx.
5. Run Steps 2-9          → Pipeline uses both validated files automatically
```

**Key point:** Steps 1 and 0 produce **unvalidated candidates**. You review them and create **validated input files**. Downstream steps (2, 6, 7, 8) consume the validated versions. The audit outputs are intermediate — useful for review but not authoritative.

### Cleaning Up

To delete all output and start fresh:
```bash
rm -rf output/
python run_pipeline.py
```

Your `input/` files (source .docx, Doc_URL.xlsx, Acronym_Definitions.xlsx) and `dps_config.xlsx` are untouched — the pipeline never writes to `input/` or modifies the config.

---

## Utilities

Utilities are standalone scripts that support the pipeline but are not pipeline steps. Run them manually as needed.

### Acronym Definitions Lifecycle

`input/Acronym_Definitions.xlsx` is the curated, human-validated version of Step 1's output. It feeds acronym tags, custom tags, and definitions into Steps 6, 7, and 8. Here's the full workflow.

#### Step 1: Generate the Audit

```bash
python run_pipeline.py --step 1
```

This scans all `.docx` files in your input folder and produces `output/1 - acronyms/acronym_audit.xlsx` — a 7-sheet workbook:

| Sheet | What It Contains | Your Action |
|-------|-----------------|-------------|
| **Acronym Definitions** | One row per document-acronym pair. Auto-detected definitions filled in; undefined ones highlighted yellow. Row 2 is a gray instruction row explaining each column. **Status** column has a dropdown (Confirmed / False Positive / Needs Review). | **Curate this sheet** — set Status for each row, fill in missing definitions, add notes. Do NOT delete rows — mark them "False Positive" instead so there's an audit trail. |
| **Per Document** | Detailed occurrence data: counts, sections found in, definition(s) detected. | Reference only — use for context when deciding what to keep. |
| **Global Summary** | All acronyms ranked by total occurrences across all documents. Undefined entries highlighted yellow. | Sort by "Total Occurrences" descending. Focus on the top 20-30 highest-impact acronyms first. |
| **Undefined Acronyms** | Filtered view of acronyms with no auto-detected definition. | Each needs a definition added or goes on the `ignore_list` in config. |
| **Cross-Reference Matrix** | Which acronyms appear in which documents (matrix view). | Reference only — helps spot inconsistencies across documents. |
| **Custom Tags** | Pre-populated with all document names. Row 2 is a gray instruction row showing the expected comma-separated format. | **Fill in per-document tags** — comma-separated values (e.g., `access control, authentication, MFA`). Do NOT edit the Document_Name column. |
| **Config Used** | Snapshot of the acronym finder config used for this run. | Reference only — useful for reproducibility. |

#### Step 2: Human Review and Curation

Open `output/1 - acronyms/acronym_audit.xlsx` and work through these validation steps:

1. **"Acronym Definitions" sheet** — the primary sheet:
   - **Use the Status dropdown** (column D) for every row:
     - **Confirmed** — acronym is real, definition is correct
     - **False Positive** — not a real acronym (e.g., `PDF`, `USB`, file extensions, Roman numerals). These rows are **skipped** by Steps 6, 7, and 8 — they won't become tags or metadata.
     - **Needs Review** — uncertain, come back later. Treated the same as blank (kept in output).
   - For yellow-highlighted rows (no definition found): add the correct expansion manually in column C, or if the acronym should be ignored globally across all future runs, add it to the `ignore_list` in `dps_config.xlsx` under `acronym_finder:` settings
   - Verify auto-detected definitions are correct — the scanner finds parenthetical expansions but may pick up wrong text
   - Use the **Notes** column (E) to flag anything for future review

   > **Do not delete rows.** Use "False Positive" status instead. Deleted rows reappear on the next Step 1 run with no audit trail. Marked rows stay visible and are automatically filtered out by downstream steps.

2. **"Global Summary" sheet** — prioritization guide:
   - Sort by "Total Occurrences" descending
   - High-occurrence undefined acronyms are the biggest risk for RAG quality — prioritize those

3. **"Custom Tags" sheet** — optional enrichment:
   - Each row has a document name pre-populated from Step 1; enter comma-separated tags in the Tags column
   - Tags must be **comma-separated** — e.g., `access control, authentication, CUI` (three tags). Without commas, the entire cell becomes a single tag.
   - These tags are merged into the document's metadata alongside auto-generated tags
   - Leave the Tags cell empty if no custom tags are needed for that document
   - **Do not edit the Document_Name column** — it must match the filenames in your input folder. If you rename input files, re-run Step 1 to get fresh names.

#### Step 3: Save the Curated File

Save your reviewed copy to:
```
input/Acronym_Definitions.xlsx
```

Keep only the sheets that have data. The pipeline looks for sheets by name ("Acronym Definitions" and "Custom Tags"), so sheet order doesn't matter. The instruction rows (row 2, gray italics) are automatically skipped by all consumers.

#### What Consumes It

| Step | What It Reads | How It Uses It |
|------|--------------|----------------|
| **Step 6 (Metadata)** | "Acronym Definitions" sheet + "Custom Tags" sheet | Generates per-document tags from acronyms and custom tags; embeds into sub-documents. Skips rows with Status="False Positive". |
| **Step 7 (Markdown)** | "Acronym Definitions" sheet | Embeds acronym lists in YAML frontmatter (via `excel_lookup_list`/`excel_lookup_dict` config) |
| **Step 8 (JSONL)** | "Acronym Definitions" sheet + "Custom Tags" sheet | Includes acronyms and custom tags in chunk metadata for RAG retrieval. Skips rows with Status="False Positive". Only includes acronyms that have definitions. Prints warnings for documents with no metadata matches. |

#### Re-Running After Changes

If you add new source documents or want to refresh the acronym scan:

1. Run Step 1 again — produces a fresh `acronym_audit.xlsx`
2. Compare with your existing `input/Acronym_Definitions.xlsx` to pick up new acronyms
3. Update the curated file and re-run Steps 6-8

> **Tip:** Your curated `input/Acronym_Definitions.xlsx` is never overwritten by the pipeline. Step 1 always writes to `output/1 - acronyms/`, keeping your validated input safe.

#### Common Mistakes and Troubleshooting

| Problem | Symptom | Fix |
|---------|---------|-----|
| Tags not appearing in JSONL output | Step 8 prints "N document(s) had no matching custom tags" | Check that Document_Name values in the Custom Tags sheet match your input filenames. The matching is fuzzy (ignores underscores/hyphens/case/extension) but won't match typos. |
| Acronym definitions not appearing in JSONL | Step 8 prints "N without definitions skipped" | Fill in the Definition column (C) for acronyms you want in the output. Blank definitions are intentionally excluded from JSONL metadata. |
| False positive acronyms appearing in metadata | Tags contain entries like `PDF`, `USB` | Set Status to "False Positive" in the Acronym Definitions sheet and re-run Steps 6-8. |
| "Custom Tags" sheet not found | Step 6/8 prints "NOTE: Sheet 'Custom Tags' not found" | Ensure the sheet is named exactly "Custom Tags" (case-insensitive). Do not rename it. |
| All tags appear as one long string | JSONL shows `["access control authentication"]` instead of `["access control", "authentication"]` | Tags must be comma-separated in the Excel cell. Add commas between tags. |
| Acronyms from a previous run reappear | Rows deleted from the audit come back after re-running Step 1 | Use Status="False Positive" instead of deleting rows. Or add the acronym to the `ignore_list` in config for permanent suppression. |
| Short document name matches wrong document | e.g., "IR" matches both "Incident Response" and "IR Plan" | Use full document names in the Excel. The matching uses substring containment — short names are ambiguous. |

---

### Word Counter (`scripts/word_counter.py`)

Standalone utility for counting words in `.docx` files. Not part of the pipeline — run it separately.

```bash
# Count words in split documents (default)
python scripts/word_counter.py

# Count words in a specific folder
python scripts/word_counter.py --input ./output/5\ -\ metadata
```

Outputs `word_counts.csv` with per-document and total word counts.

---

### Control Attribute Analyzer (`Misc/analyze_control_attributes.py`)

Standalone diagnostic utility. Scans all input `.docx` files for every control ID match and captures formatting and context attributes for each hit. Use this to identify false positives and fine-tune your `control_id_patterns`, whitelist, and blacklist before running Step 2.

```bash
python Misc/analyze_control_attributes.py
python Misc/analyze_control_attributes.py --config dps_config.xlsx
python Misc/analyze_control_attributes.py ./input ./output/2\ -\ controls
```

Outputs `control_attributes_analysis.csv` (written to the Step 2 controls output folder) with one row per control ID match. Columns include: `source_file`, `paragraph_index`, `control_id`, `match_position`, `paragraph_text`, `context_before`, `context_after`, `paragraph_bold`, `paragraph_italic`, `paragraph_underline`, `font_size_pt`, `font_name`, `paragraph_style`, `is_heading_style`, `paragraph_source` (Text or Table[row][col]), `sentence_contains_period`.

**Typical workflow:** Run this first, filter the CSV by `paragraph_source` and `paragraph_bold` to distinguish real controls from table cross-references, then adjust your config patterns accordingly.

---

### Baseline & Name Parser Tests (`scripts/test_parse_baseline_and_name.py`)

Developer test script for the `parse_baseline_and_name` function in `extract_controls.py`. Verifies correct parsing of control header lines in all supported formats (ID-first, name-before-ID, trailing baselines, em-dashes, etc.). Not needed for normal pipeline use.

```bash
# Run from the DPS project root
python scripts/test_parse_baseline_and_name.py
```

Prints PASS/FAIL for each test case and exits with a non-zero code if any tests fail.

---

## Troubleshooting

### Config file issues

#### "Config file not found" error

The pipeline looks for `dps_config.xlsx` in the current directory. Make sure you run from the DPS project root:
```bash
cd /path/to/DPS
python run_pipeline.py
```
Or specify the path explicitly: `python run_pipeline.py --config /path/to/dps_config.xlsx`

#### "Permission denied" or "file is not a zip file" when reading config

**Cause:** The `.xlsx` file is open in Excel or another program.
**Fix:** Close the file in Excel/LibreOffice, then re-run the pipeline.

#### Config loads but a section is missing or empty

**Cause:** A sheet tab was renamed (e.g., `Input` → `Inputs`) or a `# Sub-header` row was deleted/changed.
**Fix:** Open the README sheet in `dps_config.xlsx` to see the expected sheet names and sub-header names. Alternatively, regenerate a fresh template:
```bash
python generate_config_template.py -o dps_config_fresh.xlsx
```
Then copy your custom values from the old file into the fresh template.

#### Boolean setting not working (e.g., `enabled` stays off)

**Cause:** You typed `"yes"`, `"true"`, or `"1"` as text instead of using Excel's built-in TRUE/FALSE.
**Fix:** Delete the cell contents, then select TRUE or FALSE from the dropdown. If there's no dropdown, type `TRUE` or `FALSE` (Excel auto-converts these to boolean values).

#### Regex pattern not matching expected text

**Cause:** Extra whitespace, line breaks, or curly quotes were introduced when pasting into Excel.
**Fix:**
1. Check for trailing spaces — click into the cell and press End to see where the cursor lands
2. Make sure quotes are straight (`"`) not curly (`""`), which Excel's autocorrect may substitute
3. Test the exact cell contents at [regex101.com](https://regex101.com)

---

### Pipeline step issues

#### Zero controls extracted (Step 2)

Your control IDs likely use a different format than the default regex patterns. Check your documents for the ID format, then add a matching pattern on the **Control Extraction** sheet under `# Control ID Patterns`. Test patterns at [regex101.com](https://regex101.com).

Common alternative patterns:

| Value | Description |
|-------|-------------|
| `\b[A-Z]{2,4}-\d{1,3}\b` | Simple: AC-1, IR-3 |
| `\b[A-Z]{2,4}\.\d{1,3}\.\d{1,3}\b` | Dotted: AC.1.1, IR.3.2 |

#### Too many fake headings detected (Step 0/4)

Fake heading detection flags bold text under a character limit. If you're getting false positives:
- On the **Headings** sheet, raise `fake_heading_min_font_size` from `12` to `13` or `14`
- Lower `fake_heading_max_chars_fixer` from `120` to `80` or `100`
- Review `heading_changes.csv` to see exactly what was converted

#### Real headings showing up as "FAKE" in the profiler

Your documents likely use custom Word heading styles. In Word, click the heading and check the Styles pane for the style name, then on the **Headings** sheet add it to:
- `# Custom Heading Styles` list (for profiler recognition)
- `# Heading Style Map` (for Step 4 conversion — map your style name to `Heading 1`, `Heading 2`, or `Heading 3`)

**Important:** Add the style in **both** places. Adding it to only one causes the profiler to recognize it but Step 4 won't convert it (or vice versa).

#### Word temp files being processed

Word creates invisible `~$` lock files when a document is open. These are excluded by default via `input.exclude_patterns`. If you see errors about corrupted files, close the documents in Word before running the pipeline, or add the pattern to the exclude list on the **Input** sheet.

#### Resuming a failed batch run (Step 2)

If Step 2 fails mid-batch, it saves progress to `checkpoint.json`. Re-running Step 2 will skip already-processed files:

```bash
python run_pipeline.py --step 2
```

To force a fresh run, delete `output/2 - controls/checkpoint.json` before running.

#### Sub-documents are too large or too small (Step 5)

On the **Thresholds** sheet, adjust `max_characters`:
- **Too large:** Lower from `36000` to `18000` for tighter splits
- **Too small:** Raise to `50000` or higher if your context window supports it

#### Metadata shows "(Not detected)" for scope/intent (Step 6)

Step 6 tries to get scope and intent from Step 0's profiler data first. If that's unavailable, it falls back to scanning the document directly. For best results:
1. Run Step 0 first so `document_profiles.json` exists
2. Check that your documents have sections matching the keywords on the **Sections** sheet (scope and intent categories)

#### Pipeline stops at a failed step

The pipeline halts on the first failure. Check the error output, fix the issue, then re-run from that step:

```bash
python run_pipeline.py --step N
```

Where `N` is the step that failed. You don't need to re-run earlier successful steps.

---

### Common Excel editing mistakes

| Mistake | What happens | How to fix |
|---------|-------------|------------|
| Renamed a sheet tab | That config section loads as empty defaults | Rename the tab back to the exact name (see README sheet) |
| Deleted a `# Sub-header` row | Settings from that block merge into the wrong block | Re-add the row. Run `generate_config_template.py` to see correct sub-header text |
| Changed column order | Settings parsed with wrong keys/values | Restore: Setting \| Value \| Description (or Key \| Value \| Description for maps) |
| Added a keyword row with column A empty | Row is silently skipped | Enter the value in column A |
| Added too many search terms (>20) | Step 0 runs slowly; inventory Excel gets very wide | Keep search terms under 20. Each term adds a column to the inventory |
| Pasted a regex with curly/smart quotes | Pattern fails to match | Replace curly quotes with straight quotes. Disable Excel autocorrect for the cell |
| Saved as `.xls` instead of `.xlsx` | `InvalidFileException` error | Re-save as `.xlsx` (File → Save As → Excel Workbook) |
| File is password-protected | Pipeline can't open the file | Remove protection (File → Info → Protect Workbook → remove password) |
