# dataverse_export — Design Notes

## What this tool does
Converts control catalog Excel workbooks into Dataverse-importable CSV files optimized for M365 CoPilot Studio RAG retrieval. Supports two input sources with different control ID formats (NIST-style and org-standard), exports them as separate rows in a single denormalized Dataverse table.

## Files
| File | Purpose |
|------|---------|
| `dataverse_export.py` | Main script — reads Excel, builds RAG content, writes CSV |
| `dataverse_export_config.yaml` | YAML config — input paths, column mappings, family map |
| `CLAUDE.md` | This file |

## Quick Start

```bash
# From this directory:
python dataverse_export.py --catalog-xlsx ../../input/nist_catalog.xlsx

# Both inputs:
python dataverse_export.py --catalog-xlsx catalog.xlsx --standard-xlsx standard.xlsx

# Explicit config:
python dataverse_export.py --config my_config.yaml --catalog-xlsx controls.xlsx

# Verbose logging:
python dataverse_export.py --catalog-xlsx controls.xlsx -v
```

Output goes to `../../output/dataverse_export/` by default (configurable in YAML).

## Design Decisions

### 1. Single denormalized Dataverse table
CoPilot Studio cannot join tables. A single `dps_controls` table with all fields means every row is a self-contained answer unit for RAG retrieval. Both Control Catalog and Standard Controls rows live in the same table, distinguished by the `source` column.

### 2. Composite `rag_content` column
CoPilot Studio may search a single column for matching content. The `rag_content` column concatenates control ID, name, family, baseline, description, guidance, purpose, and scope into a structured text block. This enables queries like "What does AC-2 require?" to match on a single field.

### 3. Shared reader for both inputs
Both Excel inputs share the same column structure (matching the DPS pipeline `ControlRow` schema). A single `load_controls()` function with a `source_label` parameter handles both, reducing code duplication.

### 4. Family derivation from control ID
For NIST-style catalog controls, the family code (e.g., "AC") is extracted from the control ID via regex, then the full family name is looked up in the `family_map`. For Standard Controls, family is left blank unless explicitly provided in the input.

### 5. No merging between sources
Both inputs produce separate rows. No cross-source deduplication or merging is performed. This keeps the logic simple and preserves both perspectives on controls.

### 6. UTF-8 with BOM output
Dataverse CSV import expects UTF-8 with BOM (`utf-8-sig`). The script writes this encoding by default.

### 7. Carriage-return stripping
Multiline text fields are normalized to `\n`-only line endings. Stray `\r` characters can interfere with Dataverse's CSV field delimiter detection.

### 8. Duplicate control_id detection
The script warns (but does not halt) when duplicate `control_id` values are found across both inputs, since `control_id` is the Dataverse primary/alternate key and must be unique for upsert operations.

### 9. YAML config following xlsx2docx pattern
Self-contained config in the same directory, auto-detected by the script. CLI flags override config values. Same deep-merge pattern as xlsx2docx.py.

## Config Key Reference

| Section | Key | Default | Notes |
|---------|-----|---------|-------|
| `input.catalog_xlsx` | — | `""` | Path to NIST catalog Excel |
| `input.catalog_sheet` | — | `"Controls"` | Sheet name |
| `input.standard_xlsx` | — | `""` | Path to org-standard Excel |
| `input.standard_sheet` | — | `"Controls"` | Sheet name |
| `input.column_map` | — | (see config) | Excel header → internal field |
| `input.header_row` | — | `1` | Row with column headers |
| `input.data_start_row` | — | `2` | First data row |
| `output.directory` | — | `"../../output/dataverse_export/"` | Output folder |
| `output.controls_csv` | — | `"dps_controls_import.csv"` | CSV filename |
| `output.schema_reference` | — | `"dataverse_schema_reference.md"` | Schema doc filename |
| `family_map` | — | (20 NIST families) | Code → full name |
| `rag_content.fields` | — | (see config) | Fields included in composite column |

## Requirements

Same as the rest of the DPS project (`requirements.txt` in the project root):
```
openpyxl>=3.1.0
pyyaml>=6.0
```
