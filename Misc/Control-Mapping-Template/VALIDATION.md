# Validation Guide — Control Mapping Accuracy

How to catch bad mappings before they go into a compliance deliverable.

---

## Known Failure Modes

### 1. Keyword Matching Without Semantic Understanding

**The problem**: Claude sees the word "access" in both a source and target control and calls it a match — even when one is about physical facility access and the other is about logical access control to systems.

**Where it shows up**: High-confidence matches between controls that share vocabulary but address fundamentally different domains. Common offenders: "access," "audit," "monitoring," "incident," "risk."

**How to catch it**: Spot-check every "high" confidence match where the source and target are from different security domains (e.g., a physical security source matched to a logical access target).

---

### 2. Overly Broad Target Controls Absorb Everything

**The problem**: Some frameworks have umbrella controls like "The organization establishes and maintains a security program" that technically touch every topic. Claude will match dozens of specific source controls to these catch-all targets with "medium" confidence, inflating coverage numbers.

**Where it shows up**: The Full Mapping sheet — look for any single target control ID appearing in 10+ rows. That target is probably too broad to be a meaningful match.

**How to catch it**: Sort the Full Mapping sheet by Matched Target IDs. If one target ID appears 15+ times, those matches are likely superficial. Consider whether the source controls actually satisfy that target's *specific* requirements or just vaguely overlap.

---

### 3. Missed Matches (False Negatives)

**The problem**: Claude doesn't find a valid match because:
- The source uses different terminology than the target (e.g., "logging" vs. "audit trail")
- The match is structural — the source control implies a capability rather than stating it explicitly
- In standard mode with 200+ target controls, controls in the middle of a long list get less attention

**Where it shows up**: The Source Unique sheet. Some of those "gaps" aren't actually gaps — they have valid target matches that Claude missed.

**How to catch it**: Every control on the Source Unique sheet needs a human eye. If you read the source control and can think of a plausible target match, go find it in the target reference file and verify it was missed.

---

### 4. Chunked Mode: Cross-Family Matches Dropped

**The problem**: When target chunking is enabled, Claude only sees one target family per prompt. If a source control's best match is in a different family than expected (e.g., an identity control matching to both AC- *and* IA- families), the match quality depends on which chunk the source was evaluated against.

**Where it shows up**: Controls that span domain boundaries — identity management, incident response, supply chain security, and continuous monitoring are typical cross-cutters.

**How to catch it**: After merge, look at controls that have matches in 3+ different target families. Also look at controls with *only* low-confidence matches — these may have medium/high matches hiding in a family you wouldn't expect.

---

### 5. Confidence Inflation

**The problem**: Claude tends to be generous with "high" confidence. A control that partially addresses a requirement might get "high" when "medium" is more accurate. This makes the gap analysis look better than it actually is.

**Where it shows up**: Full Mapping sheet — controls marked "high" where the rationale says things like "partially addresses," "broadly covers," or "related to."

**How to catch it**: Read the rationale column. If the rationale uses hedging language, the confidence is probably overstated. A true "high" rationale should say something like "directly requires the same capability" without qualifiers.

---

### 6. Duplicate/Stale Results Polluting Merge

**The problem**: If you reprocess a batch (maybe after tweaking the prompt or retrying), both the old and new result files sit in `results/`. merge.py loads all `*.json` files. In standard mode, the second file silently overwrites the first per control ID. In chunked mode, both get merged, potentially doubling matches.

**Where it shows up**: Match counts that are suspiciously high, or duplicate target IDs in the same source control's matches.

**How to catch it**: Before running merge, verify that `results/` contains exactly one result file per batch file in `batches/`. Delete stale results from earlier runs.

---

### 7. Description Truncation / Empty Fields

**The problem**: If the Excel source has merged cells, very long descriptions, or the column index in config.yaml is off by one, controls may extract with truncated or empty descriptions. Claude maps based on whatever text it sees — garbage in, garbage out.

**Where it shows up**: Reference files in `reference/`. Controls with empty or suspiciously short descriptions.

**How to catch it**: After running setup.py, open `reference/source_controls.md` and `reference/target_controls.md`. Skim for blank descriptions, "None" values, or controls that look nothing like the Excel source.

---

### 8. One-to-Many Doesn't Mean Coverage

**The problem**: A source control has 5 target matches, all medium confidence. It looks "covered" because it has matches — but none of those targets individually satisfy the full intent of the source control. The coverage is a mosaic that may have gaps between the pieces.

**Where it shows up**: Full Mapping sheet — controls with many medium matches but no high match.

**How to catch it**: For any source control with 3+ medium matches and no high match, read the source requirement carefully. Ask: "If I implemented all these target controls, would this source requirement actually be met?" Often the answer is no — the overlapping pieces don't add up to complete coverage.

---

## Human Validation Steps

### Step 1: Reference File Sanity Check (5 minutes)

After running `setup.py`, before processing any batches:

1. Open `reference/source_controls.md` — verify control count matches your Excel
2. Open `reference/target_controls.md` — verify control count matches your Excel
3. Spot-check 3-5 controls in each file against the raw Excel to confirm:
   - IDs are correct (not off-by-one column)
   - Descriptions are complete (not truncated or "None")
   - Supplemental fields (Title, Domain) are populated if configured
4. If anything is wrong, fix `config.yaml` column indices and re-run setup

---

### Step 2: Batch Output Spot Check (15-20 minutes)

After processing all batches, before running merge:

1. Pick 3 source controls you understand well (one per domain if possible)
2. Find their results across all result files (use `grep -l "CTRL-ID" results/*.json`)
3. For each control, manually verify:
   - **Are the high-confidence matches actually high?** Read both the source and target control text
   - **Is there an obvious match that was missed?** Search the target reference for keywords from the source control
   - **Does the rationale make sense?** Or does it just restate that they're "related"
4. If 2+ of your 3 samples have issues, consider reprocessing those batches with a smaller batch_size

---

### Step 3: Gap Analysis Validation (20-30 minutes)

After running `merge.py`:

1. **Source Unique sheet** — read every entry. For each "gap":
   - Is this genuinely unique to the source framework? Or can you name a target control that covers it?
   - If you find a missed match, note it — this indicates systematic blind spots
   - Count how many gaps you disagree with. If >20% are wrong, the mapping needs rework

2. **Target Unique sheet** — skim for surprises:
   - Are there target controls listed as "unique" that clearly overlap with source controls?
   - These indicate missed matches in the other direction

3. **Full Mapping sheet** — sort by "Unique" column, then by Match Count:
   - Controls with 0-1 matches: are these really that isolated?
   - Controls with 10+ matches: is this realistic or is Claude being too generous?
   - Filter to "high" confidence matches: do the rationales hold up?

---

### Step 4: Cross-Domain Boundary Check (10-15 minutes, chunked mode only)

1. Identify 3-5 source controls that span multiple security domains (identity, monitoring, incident response, and supply chain are common cross-cutters)
2. Check whether each has matches across multiple target families
3. If a cross-cutting control only matched to one target family, manually check the other relevant families — the chunking may have caused a miss
4. Compare against your own expert judgment: would you expect this source control to map to the AC-, AU-, SI-, and IR- families? If it only mapped to one, investigate

---

### Step 5: Coverage Math Sanity Check (5 minutes)

1. Source controls total: ___
2. Source controls with high/medium matches: ___
3. Source controls unique (gaps): ___
4. Does (2) + (3) = (1)? If not, something was lost in merge
5. Target controls total: ___
6. Target controls covered: ___
7. Target controls unique: ___
8. Does (6) + (7) = (5)?
9. Are the coverage percentages plausible for these two frameworks? (Two frameworks in the same domain typically share 40-70% coverage. Below 30% or above 90% warrants a closer look.)

---

## When to Reprocess

Reprocess a batch if:
- More than 2 of 8 controls in the batch have clearly wrong matches
- A control returned zero matches when you can easily name one
- The JSON was malformed or had wrong field names
- You changed the config (added supplemental columns) and want richer context

To reprocess: delete the result file from `results/`, re-run the batch prompt with AI or LLM, save the new output, and re-run `merge.py`.

---

## Potential Code-Level Issues

These are lower-severity issues in the setup and merge scripts that could affect accuracy under specific conditions. They don't require immediate fixes but are worth knowing about.

### 9. Silent Column Misalignment in Extraction

If `columns.id` or `columns.description` in `config.yaml` is off by one, `extract_controls()` in both `setup.py` and `merge.py` will silently extract the wrong column. There is no validation that the extracted IDs look like control identifiers or that descriptions are non-empty. The only safety net is manually reviewing `reference/source_controls.md` and `reference/target_controls.md` after running setup.

**Mitigation**: Always check the reference files after `setup.py`. If control IDs look like descriptions (or vice versa), your column indices are wrong.

### 10. Hardcoded Legacy Field Names in normalize_result()

`merge.py`'s `normalize_result()` function checks for fallback field names like `ccm_id` and `unique_to_sscf` — these are specific to the SSCF→CCM mapping. If this template is reused for a different framework pair and Claude happens to use a framework-specific field name (e.g., `nist_id`), it won't be caught and the target ID will default to `"UNKNOWN"`.

**Mitigation**: Ensure your batch prompts specify `target_id` as the field name (the current template does this). If you see `"UNKNOWN"` target IDs in the output, check the raw JSON for variant field names.

### 11. Coverage Levels Hardcoded in Chunked Merge

`merge_chunked_results()` in `merge.py` hardcodes `("high", "medium")` when deciding `has_coverage` after merging chunks, rather than reading `confidence.coverage_levels` from the config. If you changed which confidence levels count as "covered" (e.g., only "high"), the chunked merge would still treat "medium" as covered, creating a mismatch with the final gap computation in `compute_gaps()` which correctly reads the config.

**Mitigation**: Don't change `coverage_levels` away from the default `["high", "medium"]` without also updating `merge_chunked_results()`.

### 12. Space-Only Control IDs Pass Extraction

The extraction check is `if not ctrl_id: continue`, which catches `None` and empty strings. But a cell containing only whitespace (e.g., `' '`) is truthy and would create a phantom control with an effectively blank ID. The subsequent `.strip()` runs after the check.

**Mitigation**: Unlikely in practice — Excel data rarely has space-only cells. If you see blank entries in reference files, this could be the cause.

### 13. batching.group_by Silently Falls Back

If `batching.group_by` points to a column index that isn't declared in `source.columns.supplemental`, the code can't find a matching label and silently falls through to sequential (ungrouped) batching. There is no warning printed.

**Mitigation**: Ensure the column index in `group_by` also appears as a supplemental entry with a label.

### 14. Dedup Rationale Quality on Chunk Merge

When deduplicating matches across chunks, `merge_chunked_results()` keeps the entry with the highest confidence. If two chunks both returned a "high" match for the same target ID but with different rationales, the winner is determined by file processing order (alphabetical), not rationale quality.

**Mitigation**: Not easily fixable automatically. Spot-check high-confidence matches in the Full Mapping sheet to ensure rationales are substantive.
