---
name: docx-to-copilot
description: "Optimize IT/InfoSec policy DOCX files for Microsoft Copilot RAG retrieval in GCC/GCC-High environments. Use this skill whenever the user mentions: optimizing documents for Copilot, RAG retrieval optimization, policy document restructuring for AI agents, Copilot Studio knowledge base preparation, SharePoint document optimization for semantic search, table flattening for chunking, GCC Copilot agent setup, chunk-friendly document restructuring, or M365 semantic index optimization. Also trigger when the user has DOCX policy files and wants to make them retrievable by a Copilot agent, asks about ingestion paths (SharePoint vs Dataverse vs uploaded files), needs scripts to profile or transform policy documents, or references the notebook workflow for document processing. Trigger even if the user just says 'optimize my docs for Copilot' or 'prepare policies for RAG.' Do NOT trigger for general DOCX editing, PDF creation, or non-Copilot document tasks."
---

# DOCX to Copilot: Policy Document RAG Optimization

## What This Skill Does

Generates Python scripts, Copilot Notebook system instructions, and validation workflows that transform IT/InfoSec policy DOCX files into chunk-friendly documents optimized for Microsoft Copilot RAG retrieval. Designed for GCC/GCC-High environments running GPT-4o.

The user runs the scripts and notebook prompts themselves. Claude generates the tooling, not the transformed documents directly.

## Workflow Overview

This skill follows a 5-phase pipeline. Each phase produces scripts, notebook instructions, or validation artifacts. Read `references/platform-constraints.md` before generating any output to ensure GCC-specific constraints are respected.

```
Phase 1: Profile  -->  Phase 2: Classify  -->  Phase 3: Transform  -->  Phase 4: Validate  -->  Phase 5: Deploy
(Scripts)              (Auto + Confirm)         (Notebook Instructions)   (Scripts + Notebook)    (Agent Config)
```

## Phase 1: Document Profiling

Generate Python scripts using `python-docx` that extract structural data from uploaded DOCX files. Every profiling script must:

1. Handle errors per-file (try/except per document in batch operations)
2. Output to CSV/XLSX, never just console
3. Include clear comments per section
4. Never modify originals
5. Include `pip install` commands at top

### Core Profiling Script Outputs

When the user asks to profile documents, generate a single batch script that extracts per-document:

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
- Duplicate/near-duplicate paragraphs across documents (fuzzy match)

Output format: CSV with one row per document, summary row with averages and totals.

### Profiling Script Candidates

Generate these as separate scripts when requested:

| Script | Purpose | When to Generate |
|--------|---------|-----------------|
| Heading Style Auditor | Flags fake bold headings lacking real Word styles | Always (Week 1) |
| Table Density Calculator | Ratio of table content to prose per doc | Always (Week 1) |
| Section Length Distribution | Character count per H1 section across corpus | Always (Week 1) |
| Cross-Reference Counter | Count and location of all cross-refs | Always (Week 1) |
| Merged Cell / Nested Table Detector | Flags complex table structures | Always (Week 1) |
| Metadata Completeness Checker | Checks for policy name, review date, control IDs, framework refs inline | Always (Week 1) |
| Duplicate Content Finder | Fuzzy match paragraphs across all docs | Always (Week 1) |

## Phase 2: Document Type Classification

After profiling data exists, auto-classify each document and present to user for confirmation/override.

### Classification Rules

Most IT/InfoSec policy documents are hybrids: prose intent sections mixed with control tables mixed with procedural steps. The classification system reflects this reality. Hybrid is the default, not a special case.

- **Type C (Hybrid Docs) - DEFAULT:** Mix of prose and tables, often with embedded procedures in Controls sections. 10-40% table content. Most docs land here. Base notebook instructions are written for this type.
- **Type A (Table-Heavy Control Docs):** >40% content in tables. Control matrices, applicability tables, configuration baselines. Addendum overrides base for table-dominant handling.
- **Type B (Prose-Heavy Intent Docs):** <10% table content. Long narrative sections, rationale, risk context. Addendum overrides base for prose-dominant handling.
- **Type D (Appendix-Dominant Docs):** >60% appendix material (glossaries, crosswalks, reference tables) regardless of table density in the policy body. Addendum overrides base for appendix handling.
- **Type E (Unclassified):** Does not fit A-D. Requires calibration cycle before processing. Never force-fit.

Generate a classification script that reads profiling CSV output and applies these thresholds, outputting a new column with recommended type and confidence score. Documents that fall between thresholds default to Type C.

## Phase 3: Document Transformation

This phase generates Copilot Notebook system instructions and type-specific addendums. Claude does NOT transform the documents directly. Claude generates the instructions the user pastes into their Copilot Notebooks.

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
- Automated structural checks (scripts) + semantic checks (notebook)
- Read `references/notebook3-instructions.md` for the full system instruction template

### Eight Restructuring Rules

Every transformation output must follow these rules. Embed them in Notebook 2 instructions:

1. **Split at 15-20 page boundary** (under 36,000 characters per sub-document)
2. **Self-identifying context sentence** at start of every section
3. **Eliminate cross-references** with inline restatements
4. **Flatten all tables** to prose paragraphs (Copilot cannot parse tables)
5. **Descriptive, policy-named headers** (not generic "Purpose" or "Controls")
6. **Intent-to-control linkage** in every control paragraph
7. **Summary paragraph** at document top (policy area, control count, frameworks, applicability, review date)
8. **Consistent file naming and metadata** ([Policy Area] - [Sub-Document Type] - [Version].docx)

### Transformation Scripts

Generate these Python scripts for automated pre-processing before notebook work:

| Script | What It Does |
|--------|-------------|
| Table Flattener (Automated) | Converts simple tables (no merges, consistent columns) to prose using template patterns |
| Context Sentence Injector | Prepends self-identifying sentence to every H1/H2 section using filename and heading text |
| Cross-Reference Inliner (Simple) | For within-document references, copies referenced paragraph inline |
| Heading Style Fixer | Converts bold/font-size fake headings to real Word heading styles |
| Document Splitter | Splits at H1 boundaries into sub-documents under 36,000 characters |
| Summary Paragraph Generator | Inserts template summary paragraph at top using profiling data |
| Control Paragraph Standardizer | Rewrites control paragraphs to consistent pattern: ID, requirement, framework, intent |

### Script Generation Rules

All transformation scripts must:
1. Handle errors per-file
2. Output to new files (pattern: `original_name_optimized.docx`), never overwrite
3. Include clear comments
4. Include pip install commands
5. Use libraries: `python-docx`, `openpyxl`, `csv`, `os`, `glob`, `pathlib`, `re`

### Notebook Output Strategy: Chunked Processing

Copilot Notebooks truncate long outputs. Do not ask the notebook to transform an entire document or even an entire Controls section in one chat. Process section-by-section:

1. **One H2 subsection per chat.** Each notebook chat handles one H2-level section (one control family, one procedure, one appendix segment). This keeps output within the notebook's reliable output length.
2. **Explicit output boundaries.** Every notebook prompt must specify: "Output ONLY the restructured content for [section name]. Do not include content from other sections. Begin output with the H2 heading. End output after the last paragraph of this section."
3. **Markdown output format.** All Notebook 2 output is markdown. Instruct the notebook: "Output in markdown format. Use ## for Heading 2, ### for Heading 3. Use plain paragraphs for body text. No bullet points for control paragraphs. No code blocks around prose content."
4. **Sequential file naming.** Save each notebook output to a numbered markdown file: `[PolicyName]_[SectionNumber]_[SectionSlug].md` (e.g., `AccessControl_03_TechnicalControls.md`). This preserves assembly order.
5. **Assembly happens outside the notebook.** A Python script stitches the markdown files into a single DOCX. The notebook never sees the assembled output.

### MD-to-DOCX Assembly Pipeline

Notebook outputs are markdown. SharePoint needs DOCX with real Word heading styles (because heading styles are chunking signals for the M365 semantic index). This is a non-trivial conversion.

**Assembly Script Requirements (generate via Notebook 1 or Claude):**

The assembly script must:
1. Read all numbered `.md` files for a policy in order
2. Convert markdown headings to real Word Heading 1/2/3 styles (not bold text)
3. Preserve paragraph structure (one paragraph per markdown paragraph)
4. Apply the restructuring template (consistent fonts, spacing, page layout)
5. Insert page breaks at H1 boundaries
6. Output as `[PolicyName]_optimized.docx`
7. Validate heading styles are real Word styles (not manual formatting)

**Tool options for conversion:**
- `pandoc` with a reference DOCX template: `pandoc input.md -o output.docx --reference-doc=template.docx` (fastest, handles heading styles correctly if template is configured)
- `python-docx` from scratch: more control, more code, handles edge cases better
- Recommended: generate both options and let the user pick based on their environment

**The assembly workflow per document:**
```
Notebook 2 chat 1 --> Section_01.md
Notebook 2 chat 2 --> Section_02.md
Notebook 2 chat 3 --> Section_03.md
...
Assembly script   --> PolicyName_optimized.docx
Validation script --> Structural checks
Notebook 3        --> Semantic checks
```

**Template DOCX for pandoc:** Generate a Word template with pre-configured Heading 1/2/3 styles, standard margins, and the organization's preferred fonts. This template is the `--reference-doc` argument. Generate it once, reuse for all 80 docs.

### Handling Notebook Output Failures

When the notebook truncates or produces incomplete output:
- **Symptom:** Output ends mid-sentence or mid-paragraph
- **Fix:** Re-run the same section with a narrower scope. Split the H2 section into H3 sub-sections and process each in its own chat.
- **Symptom:** Notebook ignores part of the instructions
- **Fix:** Reduce instruction complexity. Move type-specific rules to a separate "context" message at the start of the chat, then give the transformation command in a follow-up message.
- **Symptom:** Output drifts from the pattern used in previous sections
- **Fix:** Include a 1-2 paragraph example of correct output from a previous section in the prompt. Budget 100-150 words for the example. This is more effective than adding rules.

## Phase 4: Validation

Validation splits into two tracks: automated structural checks (Python scripts) and semantic checks (Copilot Notebook 3 + human review).

### Automated Structural Validation Script

Generate a batch validation script that checks per restructured document:

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

After automated + notebook validation, the user performs:

1. **Track Changes Review:** Open restructured doc in Word with Track Changes ON. Every structural change is visible. This is the audit trail for policy intent preservation.
2. **Flag Resolution:** Resolve all [NEEDS REVIEW], [CROSS-REF], [PLACEHOLDER], [MEANING CHECK] flags from Notebook 2 output.
3. **Original vs Optimized Comparison:** Use a Copilot Notebook with both the original and optimized docs attached.

### Comparison Notebook Prompt Template

Generate this prompt for the user to run in a Copilot Notebook with both docs attached:

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

After every 5 uploaded documents, generate 5 test queries and have the user run them against the Copilot agent to catch retrieval problems early. Query categories:

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

Use these for meta-analysis tasks only, not per-document processing:

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

Read these before generating outputs:

| File | When to Read | Contains |
|------|-------------|----------|
| `references/platform-constraints.md` | Always, before any output | GCC model limits, ingestion paths, chunking constraints, SharePoint limits |
| `references/notebook1-instructions.md` | When generating profiling/scripting notebook instructions | Full Notebook 1 system instruction template |
| `references/notebook2-instructions.md` | When generating transformation notebook instructions | Full Notebook 2 base system instruction template |
| `references/type-addendums.md` | When generating type-specific transformation instructions | All Type A/B/C/D/E addendum templates with before/after examples |
| `references/notebook3-instructions.md` | When generating QA validation notebook instructions | Full Notebook 3 system instruction template with type-specific checks |
| `references/agent-template.md` | When generating Copilot Studio agent config | Agent system instruction template and test query framework |
| `references/validation-plan.md` | When generating validation scripts or retrieval tests | Script validation plan, single-variable testing protocol, compound testing |

## Execution Timeline (Solo Operator)

| Week | Phase | Key Deliverables |
|------|-------|-----------------|
| 1 | Profile + Classify | Master inventory CSV, priority ranking, type classification |
| 2 | Calibrate | 1 doc per type through full pipeline, calibrated notebook instructions v1.0, early retrieval check (10 queries) |
| 2-3 | Build Infrastructure | SharePoint library, restructuring template, batch splitter/fixer scripts |
| 3-5 | Transform Priority Batch | 10-15 priority docs restructured, validated, uploaded. 2-3 sub-docs/day pace. |
| 6-7 | Dataverse Registry | Control extraction script, Dataverse table populated, synonyms configured |
| 7-8 | Agent Deployment | Copilot Studio agent configured, 30-50 query baseline documented |
| 8+ | Iterate Remaining | Batches of 10-15, retrospectives per batch, instruction promotion checks |
