---
name: control_ingest
description: Claude contract for extracting controls from markdown policy docs into controls.csv
type: instruction
---

# Controls2CSV — Extraction Contract

You extract compliance controls from markdown policy docs in `raw/` and
append them to `output/controls.csv`.

## Layout
- `raw/` — input drop zone. **Never edit.**
- `output/controls.csv` — append-only, one row per control.
- `output/errors.log` — anything skipped or ambiguous.

## Triggers
- `extract @<filename>` → run **Extract** below.
- `update @<filename>` → run **Update** below.

One doc per invocation. The user brings the doc into context with `@`.

## Extract

1. Read `raw/<filename>`. Skip `Table of Contents`, `Appendix *`,
   `Revision History`, and crosswalk / framework-mapping tables.
2. Pull doc-level metadata once (used on every row): `purpose`, `scope`,
   `applicability`, `compliance_date` (date after "as of Month D, YYYY"
    near a `Compliance Date` heading), `published_url` (from a
   `PublishedURL:` header line). Empty if absent — never invent.
3. Find control blocks. A block starts where a control ID appears in a
   markdown heading (`#`, `##`, `###`), a bolded line (`**...**`), or a
   table row. Control IDs look like a short letter prefix followed by
   numbers with optional dots, dashes, or parens — e.g. `AC-1`,
   `AC-1.001`, `MON02.001`, `IA-5(1)`, `PR.AC-1`, `CM-7(1)(a)`. **Ignore
   inline references** like "see also AC-1.002" and plain section numbers
   like `4.2.1` — those are not new controls.
4. For each block, fill a row:
   - `control_id` — verbatim.
   - `control_name` — title around the ID. Example:
     `MON02.001 (L, M, H) - SIEM Log Ingestion` → name is
     `SIEM Log Ingestion`. Also handles the name appearing before the ID.
     Strip `Control` / `Control ID` prefixes.
   - `baseline` — `(L, M, H)` normalized to `L,M,H`. Empty if absent.
   - `section_header` — the closest markdown heading above the block.
   - `control_description` — full body text of the control, **verbatim**.
     Descriptions can be long and carry useful context — keep all of it.
     Whitespace normalization only; no paraphrasing or renumbering. Stops
     where guidance begins (see below).
   - `supplemental_guidance` — text under `Implementation Guidance`,
     `Supplemental Guidance`, `Guidelines`, `How to implement`, or
     `Implementation:`. Everything after that label belongs here.
   - `miscellaneous` — leftovers like `References:`, `Related Controls:`.
   - `extraction_source` — `Text` or `Table`.
   - `source_file` — the filename.
5. Append to `output/controls.csv` (create with header if missing).
   Wrap fields containing `,`, `"`, or newlines in `"`; escape `"` as `""`.
6. Report: rows added, blocks skipped (and why), missing metadata fields.

## Update

1. Read `controls.csv`. Find rows where `source_file` matches.
2. Re-run Extract in memory. Diff by `(source_file, control_id)`:
   - **New** → append.
   - **Removed** → leave existing row, log to `errors.log`.
   - **Changed** → stop and ask: overwrite, or keep both and log the diff?
3. Never silently overwrite — there is no undo once a row is replaced.

## CSV schema

Fixed column order:

```
source_file,section_header,control_id,control_name,baseline,control_description,supplemental_guidance,miscellaneous,extraction_source,purpose,scope,applicability,compliance_date,published_url
```

## Rules
- **Verbatim controls.** Wording preserved; whitespace may be normalized.
- **Never invent.** Empty fields are fine; fabricated ones are not.
- **One row per ID per doc.** If an ID appears more than once, keep the
  occurrence where the control is actually defined (heading, bold line, or
  table row) and log the rest as references.
- **Skip crosswalks** (Control ID column + only framework columns) and
  **revision histories** (Version + Date + Changes columns).
- **Append-only** to `controls.csv`. Updates go through the Update flow.
- **Log ambiguity** to `errors.log` with filename and reason.
