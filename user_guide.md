# DPS User Guide

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Running the Pipeline](#running-the-pipeline)
5. [Pipeline Steps](#pipeline-steps)
6. [Configuration Reference](#configuration-reference)
7. [Output Reference](#output-reference)
8. [Utilities](#utilities)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The **Document Processing System (DPS)** is a Python pipeline that transforms IT and InfoSec policy `.docx` files into chunk-friendly documents optimized for Microsoft Copilot RAG (Retrieval-Augmented Generation) retrieval.

The pipeline runs 7 sequential steps:

| Step | Script | What It Does | Type |
|------|--------|-------------|------|
| 0 | `policy_profiler.py` | Scan & classify all documents | Read-only |
| 1 | `extract_controls.py` | Extract structured control data | Read-only |
| 2 | `cross_reference_extractor.py` | Capture cross-references | Read-only |
| 3 | `heading_style_fixer.py` | Fix fake headings to real Word styles | Transformative |
| 4 | `section_splitter.py` | Split documents at H1 boundaries into RAG-sized sub-documents | Transformative |
| 5 | `add_metadata.py` | Stamp sub-documents with identity metadata | Transformative |
| 6 | `validate_controls.py` | Validate controls exist in split output | Read-only |

**Read-only** steps (0, 1, 2, 6) only analyze documents and produce reports. Your original input files are never modified.

**Transformative** steps (3, 4, 5) create new `.docx` files with modifications. Originals in `input/` are still untouched — these steps write altered copies to their own output folders. Each transformative step feeds into the next: Step 3 produces `*_fixed.docx` files, Step 4 splits those into sub-documents, and Step 5 adds metadata to the sub-documents.

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
| `pyyaml` | >=6.0 | Read dps_config.yaml |
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
# Run all enabled steps (0 through 6)
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
python run_pipeline.py --config my_config.yaml

# Skip the consolidated Excel report at the end
python run_pipeline.py --no-excel
```

### Running Scripts Standalone

Each script can be run independently outside the pipeline:

```bash
python scripts/policy_profiler.py --config dps_config.yaml --input ./input --output ./output/0\ -\ profiler
python scripts/extract_controls.py --config dps_config.yaml ./input ./output/1\ -\ controls
python scripts/cross_reference_extractor.py --config dps_config.yaml ./input ./output/2\ -\ cross_references
python scripts/heading_style_fixer.py --config dps_config.yaml ./input ./output/3\ -\ heading_fixes
python scripts/section_splitter.py --config dps_config.yaml ./output/3\ -\ heading_fixes ./output/4\ -\ split_documents
python scripts/add_metadata.py --config dps_config.yaml ./output/4\ -\ split_documents ./output/5\ -\ metadata
python scripts/validate_controls.py --config dps_config.yaml
```

### Pipeline Behavior

- Steps run sequentially in order (0 → 6).
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

**Start here** — open `document_inventory.xlsx` to understand your document set before running further steps.

**Key config sections:** `sections`, `headings`, `cross_references.profiler_patterns`, `tables.classification`, `classification`, `thresholds`, `priority_scoring`, `search_terms`

**Output files:**

| File | Contents |
|------|----------|
| `document_inventory.xlsx` | Master spreadsheet — one row per document with all metrics |
| `document_profiles.json` | Machine-readable profiles (used by Step 5) |
| `section_inventory.csv` | One row per section per document |
| `table_inventory.csv` | One row per table per document |
| `crossref_inventory.csv` | One row per cross-reference candidate |

---

### Step 1 — Control Extractor (Read-only)

**Script:** `scripts/extract_controls.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/1 - controls/`

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

**Output columns:** `source_file`, `section_header`, `control_id`, `control_description`, `supplemental_guidance`, `miscellaneous`, `extraction_source`, `purpose`, `scope`, `applicability`

---

### Step 2 — Cross-Reference Extractor (Read-only)

**Script:** `scripts/cross_reference_extractor.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/2 - cross_references/`

> **Important:** Run this step BEFORE Steps 3-5, which modify document structure. Cross-references should be captured from the original documents.

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

### Step 3 — Heading Style Fixer (Transformative)

**Script:** `scripts/heading_style_fixer.py`
**Input:** All `.docx` files from `input/`
**Output:** `output/3 - heading_fixes/`

> **This step creates modified copies.** For each input document, a `*_fixed.docx` file is written to the output folder. Original input files are never changed.

Standardizes heading styles so Step 4 (splitter) can find section boundaries:

- Applies text deletions (configured phrases removed from all paragraphs and tables)
- Converts fake bold headings to real Word Heading 1/2/3 styles
- Maps custom heading styles (e.g., "Policy Heading 1") to standard heading styles
- Determines heading level based on numbering patterns (e.g., "1.0" → H1, "1.1" → H2, "1.1.1" → H3)

**Key config sections:** `headings`, `text_deletions`

**Output files:**

| File | Contents |
|------|----------|
| `*_fixed.docx` | One fixed document per input document |
| `heading_changes.csv` | Change log of every modification made |

**Output columns (heading_changes.csv):** `doc_name`, `paragraph_index`, `original_style`, `new_style`, `paragraph_text_preview`, `change_type`, `phrase_deleted`

---

### Step 4 — Section Splitter (Transformative)

**Script:** `scripts/section_splitter.py`
**Input:** `*_fixed.docx` files from `output/3 - heading_fixes/`
**Output:** `output/4 - split_documents/`

> **This step creates new sub-documents.** Each input document is split into multiple smaller `.docx` files. Step 4 reads from Step 3's output, not from `input/`.

Splits documents at Heading 1 boundaries to produce RAG-optimized sub-documents. Each chunk is self-contained and sized to maximize retrieval precision:

- Each sub-document is named `[OriginalName] - [Heading1Text].docx` (or `[Name] - [H1] - [H2].docx` if further split)
- Sub-documents are capped at `max_characters` (default: 36,000 chars — see tuning note below)
- Content before the first H1 (preamble) is prepended to every sub-document
- **Greedy H2 accumulation:** If an H1 section exceeds the limit, its H2 sub-sections are grouped together until adding the next one would cross the limit — then the split happens at that H2 boundary. Each chunk is as large as possible without exceeding the limit. This avoids unnecessary fragmentation from splitting at every H2.
- Preserves paragraph formatting via XML deep copy

> **Why `max_characters` matters for RAG:** RAG retrieval sends matching chunks to the LLM as context. Each chunk is retrieved as a unit — a 36k chunk where only 2k is relevant wastes 34k tokens of context budget every query. Smaller, focused chunks improve retrieval precision. Tune `max_characters` in `dps_config.yaml` for your use case: use 18,000 for dense control-heavy docs, keep 36,000 for balanced policies, raise to 72,000 only for very sparse docs.

**Key config section:** `thresholds` (`max_characters`, `chars_per_page`)

**Output files:**

| File | Contents |
|------|----------|
| `[Name] - [Heading].docx` | Sub-document files |
| `split_manifest.csv` | Manifest of all sub-documents created |

**Output columns (split_manifest.csv):** `original_doc`, `sub_doc_filename`, `heading_text`, `character_count`, `page_estimate`

---

### Step 5 — Metadata Injector (Transformative)

**Script:** `scripts/add_metadata.py`
**Input:** `.docx` files from `output/4 - split_documents/`
**Output:** `output/5 - metadata/`

> **This step creates final output documents.** Each sub-document gets a metadata block added. Step 5 reads from Step 4's output.

Stamps each sub-document with identity metadata so Copilot/RAG always knows what document a chunk came from:

- **Document name** — resolved from filename + split manifest
- **URL** — resolved from Excel lookup file or fallback template
- **Scope** — extracted from profiler data (Step 0) or direct document scan
- **Intent** — extracted from profiler data (Step 0) or direct document scan
- **Tags** — generated from document type, sections found, acronyms, and static tags

Metadata placement options: top of document, top and bottom, or Word header on every page.

**Key config section:** `metadata`

**Output files:**

| File | Contents |
|------|----------|
| `*.docx` | Sub-documents with metadata blocks |
| `metadata_manifest.csv` | Log of what metadata was applied to each file |

---

### Step 6 — Control Validator (Read-only)

**Script:** `scripts/validate_controls.py`
**Input:** `output/1 - controls/controls_output.csv` + `output/4 - split_documents/`
**Output:** `output/6 - validation/`

Validates that every control extracted in Step 1 is present in the split documents from Step 4:

- **PASS** — Control found in split docs from the same parent document
- **MISSING** — Control not found in any split document
- **RELOCATED** — Control found but in a different parent document

**Output files:**

| File | Contents |
|------|----------|
| `control_validation.csv` | One row per control with validation status |

**Output columns:** `control_id`, `source_file`, `source_section`, `found_in_split_docs`, `split_doc_filenames`, `parent_doc_match`, `status`

---

## Configuration Reference

All settings live in a single file: **`dps_config.yaml`**. The pipeline works with defaults — only change what you need.



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
| `output.controls.directory` | `"1 - controls"` | Sub-folder for Step 1 outputs. |
| `output.controls.output_file` | `"controls_output.csv"` | CSV output filename. |
| `output.controls.output_file_xlsx` | `"controls_output.xlsx"` | Excel output filename. |
| `output.controls.checkpoint_file` | `"checkpoint.json"` | Checkpoint filename for resume. |
| `output.controls.error_log` | `"errors.log"` | Error log filename. |
| `output.cross_references.directory` | `"2 - cross_references"` | Sub-folder for Step 2 outputs. |
| `output.cross_references.output_file` | `"cross_references.csv"` | Cross-references CSV filename. |
| `output.heading_fixes.directory` | `"3 - heading_fixes"` | Sub-folder for Step 3 outputs. |
| `output.heading_fixes.changes_file` | `"heading_changes.csv"` | Heading changes log filename. |
| `output.split_documents.directory` | `"4 - split_documents"` | Sub-folder for Step 4 outputs. |
| `output.split_documents.manifest_file` | `"split_manifest.csv"` | Split manifest filename. |
| `output.metadata.directory` | `"5 - metadata"` | Sub-folder for Step 5 outputs. |
| `output.metadata.manifest_file` | `"metadata_manifest.csv"` | Metadata manifest filename. |
| `output.validation.directory` | `"6 - validation"` | Sub-folder for Step 6 outputs. |
| `output.validation.output_file` | `"control_validation.csv"` | Validation results filename. |
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
| `headings.custom_style_map` | See config file | Maps your org's custom style names to standard `Heading 1`/`2`/`3` (case-insensitive keys). Used by Step 3 to convert styles the splitter can recognize. |

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

### Section 4B: Text Deletion

Remove specific phrases from documents during heading style fixing (Step 3). Deletions cascade to Steps 4 and 5.

| Key | Default | Description |
|-----|---------|-------------|
| `text_deletions.enabled` | `false` | Set to `true` to activate deletion. |
| `text_deletions.case_sensitive` | `true` | Whether phrase matching is case-sensitive. |
| `text_deletions.phrases` | `[]` (empty) | List of exact phrases to delete. After deletion, double-spaces are collapsed to single spaces. |

**Example phrases:**
```yaml
text_deletions:
  enabled: true
  case_sensitive: false
  phrases:
    - "DRAFT - NOT FOR DISTRIBUTION"
    - "CONFIDENTIAL"
    - "[INSERT DATE]"
    - "TBD"
```

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

```yaml
priority_scoring:
  usage_frequency:
    "Access_Control_Policy_POL-AC-2026-001.docx": 9
    "Incident_Response_Policy_POL-IR-2026-003.docx": 8
```

Filenames must match exactly. Default: `{}` (empty, no boost).

---

### Section 10: Key Term Search

Search for specific terms across all documents in Step 0. Results appear as columns in the Document Inventory Excel.

| Key | Default | Description |
|-----|---------|-------------|
| `search_terms.enabled` | `true` | Enable/disable key term search. |
| `search_terms.terms` | `["AC", "Cloud"]` | List of terms to search for. Each term gets its own column. Plain text only (no regex). |
| `search_terms.match_mode` | `"word"` | `"word"` = whole-word boundary (e.g., "AC" matches "AC-1" but not "ACCESS"). `"substring"` = anywhere in text (e.g., "AC" matches "ACCESS", "PRACTICAL"). |
| `search_terms.show_counts` | `true` | `true` = show occurrence count. `false` = show YES/blank. |

---

### Section 11: Control Extraction

Controls how Step 1 extracts structured control data from documents.

#### Common Settings

| Key | Default | Description |
|-----|---------|-------------|
| `control_extraction.control_id_patterns` | See below | List of regex patterns to match control IDs. |
| `control_extraction.whitelist` | `[]` | If non-empty, only matching controls are kept. Supports exact IDs (`"AC-1.001"`) and wildcards (`"AC-*"`). |
| `control_extraction.blacklist` | `[]` | Matching controls are excluded (applied after whitelist). Same syntax as whitelist. |
| `control_extraction.enable_checkpoint` | `true` | Save progress for resumable batch runs. |
| `control_extraction.output_format` | `"both"` | Output format: `"csv"`, `"xlsx"`, or `"both"`. |

**Default control ID patterns:**
```
\b[A-Z]{2,4}[-.]?\d{1,3}[-.]\d{2,4}\b     # AC-1.001, IR001.002, CFG.1.0042
\b[A-Z]{2,4}\s+\d{1,3}\.\d{2,4}\b          # AUP 1.001, ACC 01.001 (with space)
\b[A-Z]{2,4}\d{2,3}\.\d{2,4}\b              # ACC01.001 (no separator before digits)
```

If zero controls are extracted, your IDs likely use a different format. Add alternative patterns:
```yaml
control_extraction:
  control_id_patterns:
    - '\b[A-Z]{2,4}-\d{1,3}\b'              # Simple: AC-1, IR-3
    - '\b[A-Z]{2,4}\.\d{1,3}\.\d{1,3}\b'    # Dotted: AC.1.1, IR.3.2
```

#### Advanced Settings

| Key | Default | Description |
|-----|---------|-------------|
| `control_extraction.guidance_keywords` | `implementation guidance`, `implementation:`, `guidelines:`, `how to implement`, `supplemental guidance` | Keywords marking the boundary between control text and supplemental guidance. |
| `control_extraction.metadata_triggers.purpose` | `purpose`, `objective`, `intent` | Keywords to detect purpose metadata in first N paragraphs. |
| `control_extraction.metadata_triggers.scope` | `scope`, `coverage`, `boundary` | Keywords to detect scope metadata. |
| `control_extraction.metadata_triggers.applicability` | `applicability`, `applies to`, `applies for` | Keywords to detect applicability metadata. |
| `control_extraction.metadata_scan_paragraphs` | `40` | How many paragraphs from the top of each doc to scan for metadata. |
| `control_extraction.implementation_trigger` | Regex combining guidance_keywords | Regex for guidance boundary within a control block. |

#### Heading Detection (within Control Extractor)

| Key | Default | Description |
|-----|---------|-------------|
| `control_extraction.heading_detection.use_word_heading_style` | `true` | Use Word heading styles as section boundaries. |
| `control_extraction.heading_detection.section_keyword_pattern` | `^[Ss]ection\s+\d{1,2}` | Regex for "Section N" style headings. |
| `control_extraction.heading_detection.numbered_title_pattern` | `^\d{1,2}\.?\d{0,2}\s+[A-Z][a-zA-Z\s]{3,50}$` | Regex for numbered title headings. |
| `control_extraction.heading_detection.detect_allcaps` | `true` | Detect ALL-CAPS text as section headers. |
| `control_extraction.heading_detection.allcaps_max_length` | `80` | Max character length for ALL-CAPS detection. |
| `control_extraction.heading_detection.allcaps_min_words` | `3` | Minimum word count for ALL-CAPS detection. |
| `control_extraction.heading_detection.detect_bold_short` | `true` | Detect bold short text as section headers. |
| `control_extraction.heading_detection.bold_max_length` | `60` | Max character length for bold heading detection. |

---

### Section 11b: Pipeline Steps

Enable or disable individual steps. You can still run disabled steps explicitly with `--step N`.

```yaml
pipeline:
  steps:
    - name: "Step 0 - Document Profiler"
      script: "policy_profiler.py"
      enabled: true       # Set to false to skip
      description: "..."
    # ... (Steps 1-6 follow the same format)
```

| Key | Description |
|-----|-------------|
| `pipeline.steps[N].enabled` | Set to `false` to skip a step when running the full pipeline. The step can still be run explicitly with `--step N`. |

---

### Section 12: Metadata Injection

Controls how Step 5 stamps sub-documents with identity metadata.

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

Custom field examples:
```yaml
# Static field — same value on every document
- key: "classification"
  label: "Classification"
  enabled: true
  source: "static"
  value: "CUI // SP-NOFORN"

# Excel field — pulled from your URL lookup spreadsheet
- key: "owner"
  label: "Document Owner"
  enabled: true
  source: "excel"
  excel_column: "Owner"    # must match a column header in your Excel file
```

#### URL Resolution

Resolution order: Excel lookup → fallback template → "(URL not configured)"

**Excel lookup file format**

Create an Excel file (`.xlsx`) with at least two columns — one for document names and one for URLs. Column headers must match what you configure in `dps_config.yaml` (defaults: `Document Name` and `SharePoint URL`):

| Document Name | SharePoint URL |
|---|---|
| Access Control Policy | https://contoso.sharepoint.com/.../Access_Control_Policy.docx |
| Incident Response Policy | https://contoso.sharepoint.com/.../Incident_Response_Policy.docx |

- Extra columns are fine — they are ignored unless referenced as custom fields.
- The file can be on any sheet; set `metadata.url.sheet` to the sheet name or index (0 = first).
- Rows with a blank name or URL are skipped.

**How matching works**

Matching is **case-insensitive substring**: the Excel name is checked against the document name derived from the filename (underscores converted to spaces, extension stripped). A match occurs if either string contains the other. For example, `"Access Control"` in Excel will match a file named `Access_Control_Policy_v2.docx`.

Because matching is bidirectional, shorter entries match more broadly — `"Policy"` alone would match every document with "Policy" in its name. Use enough of the document name to be unique.

**Setup steps**

1. Save your Excel file somewhere in the project (e.g., `Misc/url_lookup.xlsx`).
2. In `dps_config.yaml`, set the `metadata.url` block:

```yaml
metadata:
  url:
    lookup_file: "Misc/url_lookup.xlsx"
    name_column: "Document Name"    # must match your Excel column header exactly
    url_column: "SharePoint URL"    # must match your Excel column header exactly
    sheet: 0                        # 0 = first sheet, or use the sheet name as a string
```

3. Run Step 5. The console will report how many mappings loaded and how many were resolved from Excel vs. fallback.

**If matching fails**, Step 5 will print a warning listing the column headers it actually found in your file — use that to spot header typos.

| Key | Default | Description |
|-----|---------|-------------|
| `metadata.url.lookup_file` | `""` | Path to an Excel file mapping document names to URLs. Leave empty to skip. |
| `metadata.url.name_column` | `"Document Name"` | Column header in the Excel file for document names. |
| `metadata.url.url_column` | `"SharePoint URL"` | Column header in the Excel file for URLs. |
| `metadata.url.sheet` | `0` | Sheet name (string) or index (0 = first sheet). |
| `metadata.url.fallback_template` | `""` | URL template when no Excel match is found. Use `{filename}` as placeholder. Example: `"https://contoso.sharepoint.com/sites/Policies/Shared Documents/{filename}"` |

#### Advanced Metadata Settings

| Key | Default | Description |
|-----|---------|-------------|
| `metadata.max_scope_chars` | `300` | Maximum characters for scope text extraction. |
| `metadata.max_intent_chars` | `300` | Maximum characters for intent text extraction. |
| `metadata.tags.include_doc_type` | `true` | Add document type tag (e.g., "Type-B"). |
| `metadata.tags.include_sections_found` | `true` | Add tags for detected sections (e.g., "has-scope", "has-controls"). |
| `metadata.tags.acronym_audit_file` | `""` | Path to Acronym Finder output Excel. Reads "Per Document" sheet, matches by filename. Leave empty to skip. |
| `metadata.tags.max_acronym_tags` | `15` | Maximum acronym tags per document (most-frequent first). `0` = unlimited. |
| `metadata.tags.static_tags` | `[]` | Static tags added to ALL documents (e.g., `["InfoSec", "GCC-High"]`). |

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

  1 - controls/
    controls_output.csv            # One row per control
    controls_output.xlsx           # Same data in Excel
    checkpoint.json                # Resume progress tracker
    errors.log                     # Extraction errors

  2 - cross_references/
    cross_references.csv           # One row per cross-reference

  3 - heading_fixes/
    *_fixed.docx                   # Fixed documents (one per input)
    heading_changes.csv            # Change log

  4 - split_documents/
    [Name] - [Heading].docx        # Sub-documents
    split_manifest.csv             # Manifest of all splits

  5 - metadata/
    [Name] - [Heading].docx        # Sub-documents with metadata
    metadata_manifest.csv          # What metadata was applied

  6 - validation/
    control_validation.csv         # PASS/MISSING/RELOCATED per control

  DPS_Report_2026-03-23_143052.xlsx  # Consolidated workbook (all CSVs)
```

The **consolidated report** (`DPS_Report_*.xlsx`) contains one styled sheet per step's CSV output, with blue headers, frozen top row, autofilter, and auto-sized columns.

---

## Utilities

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

## Troubleshooting

### Zero controls extracted (Step 1)

Your control IDs likely use a different format than the default regex patterns. Check your documents for the ID format, then add a matching pattern to `control_extraction.control_id_patterns`. Test patterns at [regex101.com](https://regex101.com).

Common alternative patterns:
```yaml
- '\b[A-Z]{2,4}-\d{1,3}\b'              # Simple: AC-1, IR-3
- '\b[A-Z]{2,4}\.\d{1,3}\.\d{1,3}\b'    # Dotted: AC.1.1, IR.3.2
```

### Too many fake headings detected (Step 0/3)

Fake heading detection flags bold text under a character limit. If you're getting false positives:
- Raise `headings.fake_heading_min_font_size` from `12` to `13` or `14`
- Lower `headings.fake_heading_max_chars_fixer` from `120` to `80` or `100`
- Review `heading_changes.csv` to see exactly what was converted

### Real headings showing up as "FAKE" in the profiler

Your documents likely use custom Word heading styles. In Word, click the heading and check the Styles pane for the style name, then add it to:
- `headings.custom_heading_styles` (for profiler recognition)
- `headings.custom_style_map` (for Step 3 conversion)

### Word temp files being processed

Word creates invisible `~$` lock files when a document is open. These are excluded by default via `input.exclude_patterns`. If you see errors about corrupted files, close the documents in Word before running the pipeline, or add the pattern to the exclude list.

### Resuming a failed batch run (Step 1)

If Step 1 fails mid-batch, it saves progress to `checkpoint.json`. Re-running Step 1 will skip already-processed files:

```bash
python run_pipeline.py --step 1
```

To force a fresh run, delete `output/1 - controls/checkpoint.json` before running.

### Sub-documents are too large or too small (Step 4)

Adjust `thresholds.max_characters`:
- **Too large:** Lower from `36000` to `18000` for tighter splits
- **Too small:** Raise to `50000` or higher if your context window supports it

### Metadata shows "(Not detected)" for scope/intent (Step 5)

Step 5 tries to get scope and intent from Step 0's profiler data first. If that's unavailable, it falls back to scanning the document directly. For best results:
1. Run Step 0 first so `document_profiles.json` exists
2. Check that your documents have sections matching the keywords in `sections.scope` and `sections.intent`

### Pipeline stops at a failed step

The pipeline halts on the first failure. Check the error output, fix the issue, then re-run from that step:

```bash
python run_pipeline.py --step N
```

Where `N` is the step that failed. You don't need to re-run earlier successful steps.
