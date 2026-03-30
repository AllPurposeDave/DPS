# Validation Review Workflow

## What This Folder Contains

| File | Purpose |
|------|---------|
| **control_validation.csv** | Machine-readable validation status for each control (PASS / MISSING / RELOCATED) |
| **validation_review.xlsx** | Human review workbook with confidence scoring, source context, and input sheets |
| **README.md** | This file — instructions for the review workflow |

After review, the feedback script produces:
| File | Purpose |
|------|---------|
| **confirmed_controls.csv** | The authoritative control set (reviewed + manually added, minus false positives) |
| **feedback_report.txt** | Summary of review findings, error patterns, and config suggestions |
| **suggested_config_changes.yaml** | Machine-readable config patch (only if clear patterns found) |

---

## How to Review validation_review.xlsx

> **Important:** Open in Microsoft Excel (not Google Sheets — data validation dropdowns may not work).

### Step 1: Check the Summary Sheet
Open the **Summary** sheet to understand the scope:
- Total controls, confidence band counts (Red / Yellow / Green)
- Per-document breakdown and flag frequency

### Step 2: Understand the Color Coding
The **Validation Review** sheet is sorted worst-first:
- **Red rows (0-30):** Review these first — likely extraction errors
- **Yellow rows (31-60):** Suspicious — worth spot-checking
- **Green rows (61-100):** Likely correct — sample 10-20% for calibration

### Step 3: Review Each Control (Red First)
For each row, compare:
- **Source Context (col H):** The surrounding paragraphs from the original document, with `>>>` marking the control line
- **Extracted Description (col I):** What the pipeline extracted

Also check:
- **Section Header (col F):** Is this the real section, or a suspect one (crosswalk, glossary)?
- **Extraction Source (col G):** "Table" extractions are more error-prone than "Text"
- **Baseline (col K) / Control Name (col L):** Verify if present

### Step 4: Set Validation Status (Column M — Dropdown)

| Status | When to Use |
|--------|-------------|
| **Correct** | Extraction is accurate — control ID, description, and metadata are right |
| **Wrong-FalsePositive** | This is NOT a real control (e.g., crosswalk table reference, inline mention) |
| **Wrong-Description** | Control is real but the extracted description text is wrong or truncated |
| **Wrong-Guidance** | Guidance text is wrong, or guidance was mixed into the description |
| **Wrong-Baseline** | Baseline (L/M/H) is incorrect |
| **Wrong-Section** | Control was placed under the wrong section header |
| **Missing-Content** | Control is real but key content was not captured |
| **Needs-Review** | Unsure — flag for a second reviewer |

### Step 5: Add Reviewer Notes (Column N)
Be specific about what is wrong and what the correct value should be:
- Good: "Description should stop at 'Implementation Guidance:' — everything after is guidance"
- Good: "This is a crosswalk table entry, not a real control"
- Bad: "wrong"

### Step 6: Add Missing Controls (Third Sheet)
If you spot a control in a source document that the extractor **missed entirely**, go to
the **Add Missing Controls** sheet and enter it manually. Required fields:
- **Control ID** — the ID as it appears in the document
- **Source File** — which .docx it came from (use the dropdown)
- **Section Header** — which section it appears under
- **Control Description** — the full control text

Optional: Supplemental Guidance, Baseline, Control Name, Reviewer Notes.

### Step 7: Save and Hand Off
- Save the file — keep the **.xlsx format** and **do not rename it**
- The feedback script expects `validation_review.xlsx` in this folder

---

## Flag Reference

| Flag | Confidence Penalty | What It Means |
|------|--------------------|---------------|
| EMPTY_DESCRIPTION | -40 | No control description was extracted |
| SHORT_DESCRIPTION | -30 | Description is under 20 characters |
| LONG_DESCRIPTION | -20 | Description exceeds 2000 characters |
| SUSPECT_SECTION | -35 | Found in a section like Revision History, Glossary, or Framework Crosswalk |
| APPENDIX_SECTION | -15 | Found in an Appendix section |
| DUPLICATE_ID_SAME_DOC | -25 | Same control ID extracted multiple times from the same document |
| DUPLICATE_ID_CROSS_DOC | -10 | Same control ID appears in different source documents |
| TABLE_HEADERS_IN_DESC | -20 | Description contains table header text (extraction boundary error) |
| GUIDANCE_IN_DESC | -15 | Description contains guidance keywords (boundary set too far) |
| TABLE_SOURCE | -10 | Control was extracted from a Word table (less context available) |
| EMPTY_BASELINE | -10 | No baseline when sibling controls have baselines |
| EMPTY_NAME | -5 | No control name when sibling controls have names |
| MULTI_CONTROL_PARAGRAPH | -10 | Multiple control IDs share the same paragraph |

---

## How This Feeds Back Into the Pipeline

After completing your review:

```
python scripts/ingest_review_feedback.py
python scripts/ingest_review_feedback.py --config dps_config.xlsx
```

This reads your reviewed `validation_review.xlsx` and produces:

1. **confirmed_controls.csv** — The authoritative control set:
   - Controls marked "Correct" + unreviewed controls (assumed correct)
   - Manually added controls from the "Add Missing Controls" sheet
   - Excludes controls marked "Wrong-FalsePositive"

2. **feedback_report.txt** — Analysis of review findings:
   - Review coverage and status breakdown
   - Missing controls added by reviewer
   - Error patterns and per-document accuracy
   - Config improvement suggestions

3. **suggested_config_changes.yaml** — Actionable config changes (if patterns detected)

---

## Tips for Efficient Review

- **Sort by Confidence** (default) — worst rows first, so you catch real problems early
- **Filter by Source File** — focus on one document at a time for consistency
- **Use the Summary sheet's flag frequency** — if one flag dominates, investigate that pattern
- **If you see the same error 5+ times**, note it in Reviewer Notes — it likely indicates a config fix
- **Don't review every green row** — sample 10-20% to calibrate, then trust the rest
- **Use the "Add Missing Controls" sheet** whenever you notice the extractor missed something
