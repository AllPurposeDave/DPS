# Control Mapping Template

## Environment
This project is designed for interactive AI chat sessions in VS Code (e.g. Claude Sonnet 4.5 or similar). Batches are fully self-contained — `setup.py` inlines the canonical system prompt below into every batch file, so you only need to `@`-mention the batch file itself.

## Standard Prompt Pattern
```
@batches/<filename>.md Follow the instructions in the batch file.
```

## What This Project Does
Maps controls from a **source** framework against a **target** framework to identify coverage gaps. Configured via `config.yaml`. See `README.md` for full user guide.

## Scripts
- `python scripts/setup.py` — Reads `config.yaml` + Excel, generates `reference/` and `batches/`
- `python scripts/merge.py` — Combines `results/*.json` into `output/` Excel. Handles deduplication across chunked results.

## Maintaining the System Prompt
This file is the single source of truth for the batch-processing instructions. The block between `BEGIN:SYSTEM_PROMPT` and `END:SYSTEM_PROMPT` markers below is extracted by `setup.py` and injected into every generated batch file.

To change the rules: edit between the markers, then rerun `python scripts/setup.py` to regenerate the batches. Placeholders `{source_name}`, `{target_name}`, and `{target_scope_detail}` are filled in per batch.

<!-- BEGIN:SYSTEM_PROMPT -->
## Instructions

You are an information security expert specializing in security frameworks and control mapping.

For **EACH** {source_name} control listed below, identify which {target_name} controls address the same security requirement or capability. A "match" means the {target_name} control substantively addresses the same security concern, even if scope or language differs.

**Target scope for this batch**: {target_scope_detail}

### Confidence Levels — be precise
- **high**: The {target_name} control **directly and specifically requires** the same capability. The rationale must NOT use words like "partially," "broadly," "related to," or "touches on." If you need those words, it is medium, not high.
- **medium**: Partial overlap — the {target_name} control covers some but not all of the {source_name} requirement, or addresses it at a broader scope.
- **low**: Tangential relationship only — shared vocabulary or domain but different actual requirements.

### Common Pitfalls to Avoid
- **Keyword matching is not semantic matching.** The word "access" in a physical-security control does NOT match a logical-access control. "Audit" in a financial-audit context does NOT match security-audit logging. Read both controls fully before deciding.
- **Umbrella controls are not automatic matches.** A {target_name} control like "maintain a security program" is too broad to be a high match for a specific technical requirement. Mark it medium or low.

### Rules
- Include ALL relevant matches, even low confidence ones
- Set `unique_to_source` to `true` ONLY if there are NO high or medium matches **in this target group**
- Provide a one-sentence rationale for each match explaining the **specific** overlap
- If no matches exist in this target group, return an empty matches array

### Output Format
Respond with ONLY valid JSON (no markdown code fences, no extra text). The JSON object has one key per source control ID, with a `matches` array, `unique_to_source` boolean, and `gap_rationale` string. See each batch file for the exact example and save path.
<!-- END:SYSTEM_PROMPT -->

## File Structure
```
config.yaml       — Framework names, column mappings, batch size, chunking settings
input/             — Excel file (two worksheets, one per framework)
reference/         — Generated: extracted controls as markdown
batches/           — Generated: self-contained prompt files (system prompt is inlined)
results/           — User saves JSON output here (one file per batch)
scripts/setup.py   — Generates reference/ and batches/
scripts/merge.py   — Combines results/ into output/
output/            — Final gap analysis Excel + mapping cache
```
