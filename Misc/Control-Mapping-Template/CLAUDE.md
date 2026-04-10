# Control Mapping Template

## Environment
This project is designed for interactive AI chat sessions in VS Code (e.g. Claude Sonnet 4.5 or similar). Context is NOT loaded automatically — every relevant file must be explicitly added to the chat using `@FILE-Name` syntax before prompting.

## Standard Prompt Pattern
```
@CLAUDE.md @batches/<filename>.md Follow the instructions in the batch file.
```
Both `@CLAUDE.md` and the target batch file must be included in every chat.

## What This Project Does
Maps controls from a **source** framework against a **target** framework to identify coverage gaps. Configured via `config.yaml`. See `README.md` for full user guide.

## How to Process a Batch File

When the batch file content is provided via `@` context injection:

1. The batch file contains all instructions, source controls, target reference, and the expected output filename
2. For each source control, identify matching target controls from the reference provided
3. Output **ONLY valid JSON** — no markdown fences, no commentary, no preamble

### Output Format
```json
{
  "CTRL-01": {
    "matches": [
      {"target_id": "TGT-01", "confidence": "high", "rationale": "One sentence."},
      {"target_id": "TGT-05", "confidence": "medium", "rationale": "One sentence."}
    ],
    "unique_to_source": false,
    "gap_rationale": ""
  }
}
```

### Confidence Levels
- **high** — Target control directly addresses the same requirement
- **medium** — Partial overlap or broader scope covers the intent
- **low** — Tangential relationship only

### Rules
- Include ALL relevant matches (high, medium, and low confidence)
- `unique_to_source` = true ONLY when no high or medium matches exist
- One-sentence rationale per match explaining the relationship
- If unique, explain the gap in `gap_rationale`
- In chunked mode: `unique_to_source` refers to THIS target group only — merge.py resolves the full picture

## Operating Modes

### Standard Mode
Each batch contains source controls + the full target catalog.

### Chunked Mode
Each batch contains source controls + one target family group. The same source controls appear in multiple batches (one per target group). This is expected — merge.py combines results automatically.

## Scripts
- `python scripts/setup.py` — Reads `config.yaml` + Excel, generates `reference/` and `batches/`
- `python scripts/merge.py` — Combines `results/*.json` into `output/` Excel. Handles deduplication across chunked results.

## File Structure
```
config.yaml       — Framework names, column mappings, batch size, chunking settings
input/             — Excel file (two worksheets, one per framework)
reference/         — Generated: extracted controls as markdown
batches/           — Generated: self-contained prompt files
results/           — User saves JSON output here (one file per batch)
scripts/setup.py   — Generates reference/ and batches/
scripts/merge.py   — Combines results/ into output/
output/            — Final gap analysis Excel + mapping cache
```
