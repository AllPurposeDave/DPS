# DPS: Manual, Human, and AI-Assisted Validation Steps

This document consolidates all steps requiring human judgment, manual action, or Copilot Notebook processing. Automated pipeline steps are covered in `Project Plan.md`.

---

## Human-Validated Input Files

These files live in `input/` and represent curated, reviewed data. They are consumed by multiple pipeline steps. **Do not delete without backing up — they require human effort to recreate.**

| File | Created By | Validated How | Consumed By | Purpose |
|------|-----------|---------------|-------------|---------|
| `input/Doc_URL.xlsx` | User (manual) | User enters document names and SharePoint URLs after reviewing Step 0/2 output | Steps 2, 6, 7, 8 | Maps document names to published URLs for controls export, metadata injection, and frontmatter |
| `input/Acronym_Definitions.xlsx` | User (curated from Step 1 output) | User reviews Step 1 audit, removes false positives, confirms definitions | Steps 6, 7, 8 | Verified per-document acronym lists embedded in metadata tags, MD frontmatter, and JSONL chunks |
| `input/*.docx` | Source documents | Organizational policy documents — the pipeline never modifies these | Steps 0-4, 7, 8 | Original policy documents to be processed |
| `dps_config.xlsx` | User + generator script | User tunes settings iteratively across pipeline runs | All steps | Pipeline configuration — thresholds, patterns, field definitions |

### Validation Flow

```
Step 1 output (acronym_audit.xlsx)  ──human review──►  input/Acronym_Definitions.xlsx
Step 0/2 output (document names)    ──human review──►  input/Doc_URL.xlsx
Step 9 output (validation_review)   ──human review──►  feedback ingestion script
```

The pattern is consistent: pipeline steps produce **unvalidated candidates**, a human reviews and curates them into **validated input files**, and downstream steps consume the validated versions.

---

## Phase 2: Manual Classification Review

Classification is automatic in Step 0, but requires human review before proceeding.

Review the Step 0 inventory for type assignments before proceeding. Override any misclassifications manually — the type determines which notebook addendum to use in Phase 3.

- **Type C (Hybrid) — DEFAULT:** 10-40% table content. Mix of prose and tables. Most docs land here. Base notebook instructions are written for this type.
- **Type A (Table-Heavy Control Docs):** >40% content in tables. Control matrices, applicability tables, configuration baselines.
- **Type B (Prose-Heavy Intent Docs):** <10% table content. Long narrative sections, rationale, risk context.
- **Type D (Appendix-Dominant Docs):** >60% appendix material regardless of table density in the policy body.
- **Type E (Unclassified):** Does not fit A-D. **Stop. Review manually before processing. Never force-fit.**

---

## Phase 3: Copilot Notebook Transformation

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

### Handling Notebook Output Failures

- **Output ends mid-sentence:** Re-run the same section with a narrower scope. Split the H2 into H3 sub-sections.
- **Notebook ignores part of the instructions:** Reduce instruction complexity. Move type-specific rules to a separate "context" message, then give the transformation command in a follow-up.
- **Output drifts from previous sections:** Include a 1-2 paragraph example of correct output from a previous section in the prompt. More effective than adding rules.

### MD-to-DOCX Assembly

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

---

## Phase 4: Validation

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

---

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

---

## Acronym Review (Step 1 Output)

After running Step 1 (`python run_pipeline.py --step 1`):

1. Open `output/1 - acronyms/acronym_audit.xlsx`
2. Sort **Global Summary** sheet by "Total Occurrences" descending. Top 20-30 are highest-impact.
3. Yellow rows = undefined acronyms. Each needs an expansion added to the source doc OR goes on the `ignore_list` in `acronym_config.yaml`.
4. Feed undefined acronyms into Notebook 2 as a checklist (expand on first use within each section, not just first use in the document).
5. Save curated results to `input/Acronym_Definitions.xlsx` for use by Steps 6, 7, 8.
