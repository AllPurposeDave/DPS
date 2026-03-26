# DPS: Policy Document Processing Pipeline

## Overview

The DPS (Document Processing System) pipeline and notebook workflow transform IT/InfoSec policy DOCX files into chunk-friendly documents optimized for Microsoft Copilot RAG retrieval.

The pipeline automates profiling (including word counts), control extraction, cross-reference extraction, heading fixes, splitting, and metadata injection. Notebook work handles transformation and semantic validation. Misc scripts handle supplemental audits.

## Pipeline Quick Reference

All automated steps run via `run_pipeline.py` from the project root. Config is `dps_config.yaml`.

```
python run_pipeline.py              # Run all enabled steps
python run_pipeline.py --step 0     # Run only Step 0 (profiler)
python run_pipeline.py --step 1-3   # Run Steps 1 through 3
python run_pipeline.py --step 2,4   # Run Steps 2 and 4
python run_pipeline.py --list       # Show all steps and status
```

**Pipeline steps:**

| Step | Script | What It Does | Output |
|------|--------|-------------|--------|
| 0 | `policy_profiler.py` | Scan all docs, extract metadata, classify types (A/B/C/D/E), score priority, count words | `output/0 - profiler/` |
| 1 | `extract_controls.py` | Pull structured control data with whitelist/blacklist filtering, multi-pattern ID matching, Published URL lookup, and CSV + Excel output | `output/1 - controls/` |
| 2 | `cross_reference_extractor.py` | Capture all cross-refs BEFORE any structural changes | `output/2 - cross_references/` |
| 3 | `heading_style_fixer.py` | Convert fake bold headings to real Word Heading styles | `output/3 - heading_fixes/` |
| 4 | `section_splitter.py` | Split fixed docs at H1 boundaries into RAG-sized sub-documents (greedy H2 fill to `max_characters`) | `output/4 - split_documents/` |
| 5 | `add_metadata.py` | Stamp sub-docs with identity metadata (name, URL, scope, intent, tags) | `output/5 - metadata/` |

**Always run Step 0 first.** Step 4 reads from Step 3's output. Step 5 reads from Step 4's output. Steps 1, 2 read from `input/` directly.

## Consolidated Excel Report

After every successful pipeline run, a single timestamped Excel workbook is generated in the `output/` root:

```
output/DPS_Report_2026-03-23_143052.xlsx
```

The workbook contains one sheet per step's CSV output — all in one place for filtering, sorting, and cross-referencing without opening individual files.

| Sheet | Source CSV | Useful For |
|-------|-----------|------------|
| `0 - Sections` | `section_inventory.csv` | Review standard section coverage, char counts per section |
| `0 - Tables` | `table_inventory.csv` | Spot tables with merged cells, classify by type |
| `0 - CrossRefs` | `crossref_inventory.csv` | Scan raw cross-reference candidates before Step 2 |
| `1 - Controls` | `controls_output.csv` | Review extracted controls by doc and section |
| `2 - Cross References` | `cross_references.csv` | Filter by type (internal/external), sort by source section |
| `3 - Heading Changes` | `heading_changes.csv` | Review heading style fixes, check for false positives |
| `4 - Split Manifest` | `split_manifest.csv` | Sort by char_count to spot oversized sub-docs |
| `5 - Metadata` | `metadata_manifest.csv` | Confirm metadata was applied to all sub-docs |

**Styling:** Blue header row, frozen top row, autofilter on all columns, auto-sized column widths.

**Existing CSVs are unchanged** — the workbook is additive output only. All scripts still write their individual CSVs.

Sheets are only included for CSVs that exist — partial runs (e.g. `--step 0-3`) produce a workbook with only those steps' sheets.

**To skip the report:**
```bash
python run_pipeline.py --no-excel            # skip for this run
```

Or disable permanently in `dps_config.yaml`:
```yaml
output:
  consolidated_report:
    enabled: false
```

The filename prefix can also be customized via `filename_prefix` in that same config block.

## Misc Scripts

Standalone tools in `Misc/` for supplemental audits. These do NOT run through `run_pipeline.py` — execute them directly.

### Acronym Finder (`Misc/Acronym Finder/acronym_finder.py`)

**When to use:** Run this BEFORE restructuring, alongside Step 0 profiling. Finds every acronym candidate across all docs, flags undefined ones (no parenthetical expansion found), and outputs a 5-sheet Excel report with a cross-reference matrix.

**Why it matters:** Undefined acronyms in chunks = bad RAG answers. A chunk saying "MFA is required per AC-2.1" with no expansion confuses the retrieval model. Fix undefined acronyms before notebook transformation so every section is self-contained.

```bash
cd "Misc/Acronym Finder"
python acronym_finder.py                        # Uses acronym_config.yaml defaults
python acronym_finder.py /path/to/my_config.yaml  # Custom config
```

Config: `acronym_config.yaml` — set `input_folder`, tune `ignore_list`, set `min_global_occurrences`.

**What to do with results:**
1. Sort Global Summary by "Total Occurrences" descending. Top 20-30 are highest-impact.
2. Check Undefined Acronyms sheet. Each needs an expansion added OR goes on the ignore list.
3. Check Cross-Reference Matrix for acronyms spanning 10+ docs with no definition — worst offenders.
4. Feed Undefined Acronyms sheet into Notebook 2 as a checklist (expand on first use within each section, not just first use in the document).

> **Note:** The Extract Controls standalone script that was previously in `Misc/` has been consolidated into pipeline Step 1. It supports whitelist/blacklist filtering, multiple control ID patterns, configurable heading detection, and Excel output. Word counting is now integrated into Step 0 (profiler). The standalone `word_counter.py` script remains available for ad-hoc use. Configure via `dps_config.yaml`.

## Workflow Overview

```
[Pre-flight]   Acronym Finder (Misc) → fix undefined acronyms in source docs
[Step 0]       Profile + Auto-classify all docs (includes word counts)
[Step 1]       Extract controls
[Step 2]       Extract all cross-references (snapshot before edits)
[Step 3]       Fix fake headings → real Word styles
[Step 4]       Split docs at H1 boundaries
[Step 5]       Stamp sub-docs with identity metadata (name, URL, scope, intent, tags)
[Notebook 2]   Transform each section (table flatten, cross-ref inline, etc.)
[Assembly]     MD files → DOCX via assembly script
[Notebook 3]   Semantic QA validation
[Human review] Track changes review, flag resolution, comparison notebook
[Deploy]       Upload to SharePoint, configure Copilot Studio agent
```

## Phase 1: Document Profiling

**Run:** `python run_pipeline.py --step 0`

Step 0 (`policy_profiler.py`) produces per-document:

- Total paragraph count and approximate page count (paragraph count / 30)
- All paragraphs using Word built-in Heading styles (Heading 1/2/3) vs bold-text-no-style paragraphs
- Custom named styles functioning as structural headings
- Table count, row/column counts per table, first row content per table
- Total character count and character count per H1 section
- Table density ratio (characters in tables vs total characters)
- Merged cells, nested tables, text boxes, tracked changes, comments, images, embedded objects
- Password protection, IRM protection
- Five standard section detection (Purpose, Scope, Intent, Controls, Appendix) via fuzzy match on H1 text
- Cross-reference patterns: "See Section", "refer to", "as described in", hyperlinked cross-references
- Priority score — combines table count, cross-ref count, fake headings, page count, missing sections, merged cells, oversized flag

Output format: `document_inventory.xlsx` (master spreadsheet) + `document_profiles.json` + CSVs per data type.

**Configuration tuning** (in `dps_config.yaml`):
- Adjust `headings.fake_heading_min_font_size` if fake headings aren't detected (try 11 or 10)
- Add custom heading style names to `headings.custom_heading_styles`
- Adjust `priority_scoring.weights` to rebalance what drives priority
- Set `priority_scoring.usage_frequency` to manually boost high-query policies

## Phase 2: Document Type Classification

Classification is automatic in Step 0. Each document gets a type in the inventory output.

### Classification Rules

- **Type C (Hybrid) — DEFAULT:** 10-40% table content. Mix of prose and tables. Most docs land here. Base notebook instructions are written for this type.
- **Type A (Table-Heavy Control Docs):** >40% content in tables. Control matrices, applicability tables, configuration baselines.
- **Type B (Prose-Heavy Intent Docs):** <10% table content. Long narrative sections, rationale, risk context.
- **Type D (Appendix-Dominant Docs):** >60% appendix material regardless of table density in the policy body.
- **Type E (Unclassified):** Does not fit A-D. Stop. Review manually before processing. Never force-fit.

Thresholds are configured in `dps_config.yaml` under `classification`. Documents that fall between thresholds default to Type C.

Review the Step 0 inventory for type assignments before proceeding. Override any misclassifications manually — the type determines which notebook addendum to use in Phase 3.

## Phase 3: Document Transformation

Automated pre-processing (Steps 2-4) runs first, then Copilot Notebook 2 handles the remaining transformation using the instruction templates in `references/`.

### Automated Pre-Processing (Steps 2-4)

Run before notebook work:

```bash
python run_pipeline.py --step 2-4
```

- **Step 2** snapshots all cross-references before any edits (reference for inline restatements in notebook work)
- **Step 3** converts fake bold headings to real Word Heading styles (splitter requires real styles)
- **Step 4** splits fixed docs at H1 boundaries into RAG-sized sub-documents; H2 sub-sections are accumulated greedily up to `max_characters` (default 36,000 chars), then split at the next H2 boundary — never mid-section

### Notebook Architecture (3 Notebooks)

**Notebook 1: Document Profiler + Script Generator**
- Purpose: Profile docs, generate automation scripts on demand
- Read `references/notebook1-instructions.md` for the full system instruction template

**Notebook 2: Document Transformer**
- Purpose: All document transformation (table flattening, section restructuring, context sentences, cross-ref elimination, intent-to-control linkage)
- Base instructions are written for Type C (Hybrid) since most docs are hybrids
- Type A/B/D addendums override specific behaviors for edge-case doc types
- Read `references/notebook2-instructions.md` for the full system instruction template
- Read `references/type-addendums.md` for all type-specific addendum templates

**Notebook 3: QA Validator**
- Purpose: Validate restructured documents against optimization rules
- Automated structural checks (Step 0 word counts) + semantic checks (notebook)
- Read `references/notebook3-instructions.md` for the full system instruction template

### Eight Restructuring Rules

Every transformation output must follow these rules. Embed them in Notebook 2 instructions:

1. **Split at 15-20 page boundary** (under 36,000 characters per sub-document)
2. **Self-identifying context sentence** at start of every section
3. **Eliminate cross-references** with inline restatements (use Step 2 output as the source)
4. **Flatten all tables** to prose paragraphs (Copilot cannot parse tables)
5. **Descriptive, policy-named headers** (not generic "Purpose" or "Controls")
6. **Intent-to-control linkage** in every control paragraph
7. **Summary paragraph** at document top (policy area, control count, frameworks, applicability, review date)
8. **Consistent file naming and metadata** ([Policy Area] - [Sub-Document Type] - [Version].docx)

### Notebook Output Strategy: Chunked Processing

Copilot Notebooks truncate long outputs. Do not ask the notebook to transform an entire document or even an entire Controls section in one chat. Process section-by-section:

1. **One H2 subsection per chat.** Each notebook chat handles one H2-level section (one control family, one procedure, one appendix segment).
2. **Explicit output boundaries.** Every notebook prompt must specify: "Output ONLY the restructured content for [section name]. Do not include content from other sections. Begin output with the H2 heading. End output after the last paragraph of this section."
3. **Markdown output format.** All Notebook 2 output is markdown. Instruct the notebook: "Output in markdown format. Use ## for Heading 2, ### for Heading 3. Use plain paragraphs for body text. No bullet points for control paragraphs. No code blocks around prose content."
4. **Sequential file naming.** Save each notebook output to a numbered markdown file: `[PolicyName]_[SectionNumber]_[SectionSlug].md` (e.g., `AccessControl_03_TechnicalControls.md`).
5. **Assembly happens outside the notebook.** A Python script stitches the markdown files into a single DOCX.

### MD-to-DOCX Assembly Pipeline

Notebook outputs are markdown. SharePoint needs DOCX with real Word heading styles (heading styles are chunking signals for the M365 semantic index).

**Assembly Script Requirements:**

1. Read all numbered `.md` files for a policy in order
2. Convert markdown headings to real Word Heading 1/2/3 styles (not bold text)
3. Preserve paragraph structure (one paragraph per markdown paragraph)
4. Apply the restructuring template (consistent fonts, spacing, page layout)
5. Insert page breaks at H1 boundaries
6. Output as `[PolicyName]_optimized.docx`
7. Validate heading styles are real Word styles (not manual formatting)

**Tool options:**
- `pandoc` with a reference DOCX template: `pandoc input.md -o output.docx --reference-doc=template.docx` (fastest)
- `python-docx` from scratch: more control, handles edge cases better
- Recommended: generate both options and let the user pick

**The assembly workflow per document:**
```
Notebook 2 chat 1 --> Section_01.md
Notebook 2 chat 2 --> Section_02.md
...
Assembly script   --> PolicyName_optimized.docx
Step 0 (profiler)  --> word counts in inventory (structural QA)
Notebook 3        --> Semantic checks
```

### Handling Notebook Output Failures

- **Output ends mid-sentence:** Re-run the same section with a narrower scope. Split the H2 into H3 sub-sections.
- **Notebook ignores part of the instructions:** Reduce instruction complexity. Move type-specific rules to a separate "context" message, then give the transformation command in a follow-up.
- **Output drifts from previous sections:** Include a 1-2 paragraph example of correct output from a previous section in the prompt. More effective than adding rules.

## Phase 4: Validation

Validation runs two tracks: automated structural checks (Step 0 word counts + additional scripts) and semantic checks (Notebook 3 + human review).

### Automated Structural Validation

**Step 0** (`python run_pipeline.py --step 0`) now includes word counts per document in the profiler output as a baseline QA check. For ad-hoc word counting on split sub-documents, use `python scripts/word_counter.py`.

For full structural validation, generate a batch validation script that checks per restructured document:

- Missing heading styles (fake bold headings remaining)
- Remaining tables (count per doc)
- Document length (character count vs 36,000 limit)
- Summary paragraph existence (first paragraph keyword check)
- Cross-reference pattern detection ("See Section", "refer to" remaining)
- File naming convention compliance
- Self-identifying context sentence presence per section

Output: Pass/fail scorecard per document as CSV.

### Semantic Validation (Notebook 3)

Notebook 3 runs these checks that require model judgment:

1. **Self-identification:** Does every section begin with policy name + topic sentence?
2. **Header quality:** Are all headers descriptive and policy-named?
3. **Cross-reference completeness:** Any remaining unreplaced references?
4. **Table elimination:** Any remaining tables?
5. **Intent-to-control linkage:** Sample 5 control paragraphs for dual presence of requirement + intent
6. **Isolation test:** Pick 3 random paragraphs. Read each with zero context. Can you identify: which policy, what topic, what requirement?
7. **Document length:** Under 36,000 characters?
8. **Summary paragraph completeness:** Policy area, control count, frameworks, applicability, review date all present?

### Human-in-the-Loop Validation

After automated + notebook validation:

1. **Track Changes Review:** Open restructured doc in Word with Track Changes ON. Every structural change is visible. This is the audit trail for policy intent preservation.
2. **Flag Resolution:** Resolve all [NEEDS REVIEW], [CROSS-REF], [PLACEHOLDER], [MEANING CHECK] flags from Notebook 2 output.
3. **Original vs Optimized Comparison:** Use a Copilot Notebook with both the original and optimized docs attached.

### Comparison Notebook Prompt Template

```
Compare the original policy document (Document A) with the restructured version
(Document B). For each section that exists in both:

1. CONTENT PRESERVATION: Does Document B contain every data point, control
   requirement, and policy statement from Document A? List anything missing.

2. MEANING PRESERVATION: Does any restructured sentence in Document B change
   the meaning, scope, or applicability of a requirement from Document A?
   Quote both versions for any potential meaning change.

3. TABLE CONVERSION ACCURACY: For every table in Document A, verify that
   Document B's prose version preserves every cell value. List any missing
   data points by original table location (row/column).

4. CROSS-REFERENCE RESOLUTION: For every "See Section" or "refer to" in
   Document A, verify that Document B contains an inline restatement.
   List any unresolved references.

Output a structured comparison scorecard with PASS/FAIL per check and
specific locations for all failures.
```

### Retrieval Spot-Check

After every 5 uploaded documents, generate 5 test queries and have the user run them against the Copilot agent. Query categories:

1. Broad policy question targeting one of the 5 new docs
2. Specific control lookup by ID
3. Intent explanation question
4. Cross-policy question spanning new + existing docs
5. Negative test (question about something not in the corpus)

## Phase 5: Agent Deployment

Generate Copilot Studio agent system instructions and test query suites.

### Agent Instruction Template

Read `references/agent-template.md` for the full agent system instruction template. Customize per organization.

### Test Query Suite

Generate 30-50 test queries across six categories:

1. **Broad Policy Questions** (test document retrieval + overview accuracy)
2. **Specific Control Lookups** (test chunk-level precision)
3. **Intent Explanations** (test intent-to-control linkage survival)
4. **Cross-Policy Questions** (test multi-document synthesis)
5. **Structured Data Queries** (test Dataverse control registry, if configured)
6. **Negative Tests** (test hallucination resistance)

Score each on three dimensions: Attribution (correct policy identified), Completeness (specific requirement returned), Accuracy (factually correct per source).

## Feedback Loop and Instruction Versioning

### After Every Document
Log in tracking spreadsheet: Notebook 2 failures (count + type), Notebook 3 score, flags resolved manually. 5 minutes. Non-negotiable.

### After Every 5 Documents of Same Type
Review log. If 2+ docs show same pattern failure, collect examples. Generate a deep thinking prompt for addendum writing (see below).

### Deep Thinking Prompt Templates

**Calibration Analysis (after running calibration docs):**
```
Attached are QA validation scorecards from [N] calibration documents.

Categorize every failure as:
- Pattern failure: notebook consistently does the same wrong thing
- Context failure: notebook lacks information it needs
- Judgment failure: notebook makes reasonable but wrong structural decision
- Drift failure: output correct but uses different patterns than other outputs

For each pattern failure, draft a specific instruction rule under 30 words.
Do not suggest changes to validation criteria.
Do not suggest alternative tools or workflows.
Focus only on instruction updates.
```

**Batch Retrospective (every 10-15 docs):**
```
Attached are QA scorecards from the last [N] restructured documents, all Type [X].

1. Same failure patterns across multiple docs? List them.
2. New failure patterns not seen in calibration? List them.
3. For patterns in 3+ docs, draft instruction rule under 30 words.
4. For rules not triggered in these docs, flag for potential removal.

Do not rewrite the full instruction set. Only specify additions and removals.
```

**Addendum Writing (3+ failures of same type):**
```
Here are [N] examples where Notebook 2 produced incorrect output for Type [X].
Each shows input and incorrect output.

[examples]

Identify the common pattern. Write one instruction rule under 40 words.
Do not rewrite existing instructions. Output only the new rule.
```

### Instruction Management Rules

- Never delete a base rule to accommodate a type-specific case. Add to addendum.
- If same rule appears in 3+ type addendums, promote to base instructions.
- If a rule has not triggered a failure in last 10 docs, flag for removal.
- Base + active addendum combined: stay under 800 words (operational heuristic, platform limit is 2k).
- Version all instructions. Log what changed per version.
- Include 1-2 before/after examples in addendums (100-150 words per example).

## Reference Files

Templates for notebook instructions and agent configuration. Some are stored in `SKILL/`, others are managed separately outside this repository.

| File | When to Read | Contains | Status |
|------|-------------|----------|--------|
| `SKILL/notebook2-instructions.md` | When generating transformation notebook instructions | Full Notebook 2 base system instruction template | Available |
| `SKILL/type-addendums.md` | When generating type-specific transformation instructions | All Type A/B/C/D/E addendum templates with before/after examples | Available |
| Platform constraints doc | Always, before any output | GCC model limits, ingestion paths, chunking constraints, SharePoint limits | Managed separately |
| Notebook 1 instructions | When generating profiling/scripting notebook instructions | Full Notebook 1 system instruction template | Managed separately |
| Notebook 3 instructions | When generating QA validation notebook instructions | Full Notebook 3 system instruction template with type-specific checks | Managed separately |
| Agent template | When generating Copilot Studio agent config | Agent system instruction template and test query framework | Managed separately |
| Validation plan | When generating validation scripts or retrieval tests | Script validation plan, single-variable testing protocol, compound testing | Managed separately |

## Execution Timeline

| Week | Phase | Key Actions |
|------|-------|-------------|
| 1 | Profile + Classify | Run Acronym Finder (Misc). Run `--step 0`. Review inventory CSV, priority ranking, type classification. |
| 2 | Calibrate | Run `--step 1-3` on 1 doc per type. Calibrated Notebook 2 instructions v1.0. Early retrieval check (10 queries). |
| 2-3 | Build Infrastructure | SharePoint library, restructuring template DOCX, MD-to-DOCX assembly script. |
| 3-5 | Transform Priority Batch | `--step 1-3` batch, `--step 6` metadata injection, then Notebook 2 section by section, assembly, `--step 5` QA. 2-3 sub-docs/day pace. |
| 6-7 | Dataverse Registry | `--step 4` for control extraction, Dataverse table populated, synonyms configured. |
| 7-8 | Agent Deployment | Copilot Studio agent configured, 30-50 query baseline documented. |
| 8+ | Iterate Remaining | Batches of 10-15, retrospectives per batch, instruction promotion checks. |

## Known Risks & Missing Features

### Where Policy Intent Can Drift

| Pipeline Stage | Risk | How Intent Drifts |
|---|---|---|
| **Heading Style Fixer** | Medium | A fake heading misclassified as H1 creates a false split boundary — orphaning context that belonged with the previous section. A real H1 missed means two distinct topics merge into one chunk, diluting both. |
| **Section Splitter (H1 → sub-docs)** | High | Splitting at H1 severs the narrative arc. A "Purpose" section may state intent that qualifies every control beneath it. Once split, downstream chunks lose that qualifying language. The preamble helps, but preamble ≠ full Purpose section. |
| **Section Splitter (H2 fallback)** | Medium | When an H1 section exceeds `max_characters`, H2 sub-sections are accumulated greedily until the limit is crossed, then split at the next H2 boundary. Tightly coupled subsections that together exceed the limit (e.g., a large "Scope" + "Applicability") will still land in separate docs — but the greedy approach keeps them together whenever they fit. Tune `max_characters` in `dps_config.yaml` if coupled sections are being separated. |
| **Preamble Prepend** | Low-Medium | The preamble is content before the first H1. If a doc puts its actual intent/scope *after* H1 (common in appendix-dominant Type D docs), every sub-doc gets a hollow preamble — title and version but no policy context. |
| **Table Flattening (Notebook 2)** | High | Control matrices encode relationships via row/column position. Flattening to prose requires interpreting those relationships. A "Yes" cell under "Encryption Required" next to "PII at Rest" becomes a sentence — and the sentence's wording *is* the policy now. |
| **Cross-Reference Inlining (Notebook 2)** | Medium | Replacing "See Section 4.3" with the actual text of 4.3 can change meaning if 4.3 is paraphrased or truncated. Over-inlining bloats chunks; under-inlining leaves dangling pointers. |

### Missing from the Pipeline

1. **Sub-Document Titling Strategy:** Output files named `[OriginalName] - [Heading1Text].docx` produce generic names like `*- Controls.docx` across many source docs. Needs a convention encoding source policy name + specific topic.
2. **Duplicate/Overlap Detection:** No mechanism detects when two sub-docs from different source policies cover the same topic. Copilot retrieves both and may give contradictory answers.
3. **Chunk Identity Metadata:** ~~Beyond preamble, nothing marks *where in the original doc* a chunk came from.~~ **Addressed by Step 5 (`add_metadata.py`).** Each sub-doc now gets a metadata block with document name, URL, scope, intent, and tags. URLs are sourced from `input/Doc_URL.xlsx` — one file shared by both Step 1 (Published URL column in controls export) and Step 5 (metadata injection). Effective date and parent heading chain are not yet included — add as custom fields in `metadata.fields` config if needed.
4. **Version/Staleness Tracking:** When a source doc is revised, no mechanism identifies which sub-docs need regeneration. `split_manifest.csv` needs a hash or timestamp per sub-doc.
5. **Round-Trip Validation:** No check confirms the union of all sub-doc content equals the original (minus formatting). Missing or duplicated paragraphs from XML deep-copy edge cases go unnoticed.
6. **Table Handling at Split Boundaries:** Tables attributed to the section where they start. A table spanning an H1 boundary goes entirely into the first section's sub-doc even if it semantically belongs to the next.
7. **Max Doc Count Guardrail:** No check enforces the 400-doc SharePoint/Copilot source limit. The splitter should track cumulative sub-doc count and warn before exceeding the ceiling.

Options to stay under 400: merge small adjacent sections before splitting, consolidate Type D appendix docs into shared reference docs, or exclude boilerplate sections (Document History, Approval Signatures) from output.
