# Potential Issues: 80 → 400 Document Split Pipeline

## Where Policy Intent Can Change

| Pipeline Stage | Risk | How Intent Drifts |
|---|---|---|
| **Heading Style Fixer** | Medium | A fake heading misclassified as H1 creates a false split boundary — orphaning context that belonged with the previous section. A real H1 missed means two distinct topics merge into one chunk, diluting both. |
| **Section Splitter (H1 → sub-docs)** | High | Splitting at H1 severs the narrative arc. A "Purpose" section may state intent that qualifies every control beneath it. Once split, downstream chunks lose that qualifying language. The preamble helps, but preamble ≠ full Purpose section. |
| **Section Splitter (H2 fallback)** | High | When an H1 section exceeds 36k chars and gets sub-split at H2, tightly coupled subsections (e.g., "Scope" + "Applicability") land in separate docs. Each chunk reads as standalone policy when it was written as conditional on its sibling. |
| **Preamble Prepend** | Low-Medium | The preamble is content before the first H1. If a doc puts its actual intent/scope *after* H1 (common in appendix-dominant Type D docs), every sub-doc gets a hollow preamble — title and version but no policy context. |
| **Table Flattening (Notebook 2)** | High | Control matrices encode relationships via row/column position. Flattening to prose requires interpreting those relationships. A "Yes" cell under "Encryption Required" next to "PII at Rest" becomes a sentence — and the sentence's wording *is* the policy now. |
| **Cross-Reference Inlining (Notebook 2)** | Medium | Replacing "See Section 4.3" with the actual text of 4.3 can change meaning if 4.3 is paraphrased or truncated. Over-inlining bloats chunks; under-inlining leaves dangling pointers. |

## What's Missing from the Pipeline

### 1. Sub-Document Titling Strategy
**Current state:** Output files are named `[OriginalName] - [Heading1Text].docx`.
**Problem:** H1 text is often generic ("4.0 Controls", "5.0 Procedures") and repeats across all 80 source docs. With 400 output files in a flat SharePoint library, you'll have dozens of files named `*- Controls.docx`.
**Needed:** A titling convention that encodes the source policy name + the specific topic. Example: `AC-Access Control - 4.0 Logical Access Controls.docx` rather than `Access Control Policy - 4.0 Controls.docx`.

### 2. Duplicate/Overlap Detection Across Output Docs
**Current state:** No mechanism detects when two sub-docs from different source policies cover the same topic (e.g., "Incident Reporting" may appear in both the IR policy and the Acceptable Use policy).
**Needed:** Post-split similarity scan or topic tagging to flag overlapping chunks before upload — Copilot will retrieve both and may give contradictory answers if they diverge.

### 3. Chunk Identity Metadata Beyond Preamble
**Current state:** Preamble provides doc-level context, but nothing marks *where in the original doc* a chunk came from.
**Needed:** Each sub-doc should carry a lightweight header: source document, section number, effective date, and parent heading chain (e.g., "From: AC-001 Access Control Policy > 4.0 Controls > 4.2 Remote Access"). This is what Copilot's retrieval will surface in citations.

### 4. Version/Staleness Tracking Across Split Docs
**Current state:** When a source doc is revised, there's no mechanism to identify which of its 3-7 sub-docs need regeneration.
**Needed:** `split_manifest.csv` should be the source of truth — but it needs a hash or timestamp per sub-doc so you can diff against the new source and selectively re-process only changed sections.

### 5. Validation That Split Docs Reassemble to Original
**Current state:** No round-trip check. Character counts are logged but content completeness isn't verified.
**Needed:** A post-split validation that confirms the union of all sub-doc content equals the original (minus formatting). Missing paragraphs or duplicated paragraphs from XML deep-copy edge cases would otherwise go unnoticed.

### 6. Table Handling at Split Boundaries
**Current state:** Tables are attributed to the section where they start. A table that spans an H1 boundary goes entirely into the first section's sub-doc.
**Needed:** Detection + warning when a table's content semantically belongs to the *next* section (e.g., a controls table placed just before the "Controls" heading).

### 7. Max Doc Count Guardrail
**Current state:** No check enforces the 400-doc ceiling.
**Needed:** The splitter should track cumulative sub-doc count across all source files and warn before exceeding the SharePoint/Copilot source limit.

## Quick Math: 80 → 400

| Source Doc Type | Avg H1 Sections | Avg Sub-Docs After Split | Count | Total Sub-Docs |
|---|---|---|---|---|
| Type A (Table-Heavy) | 6 | 7 (H2 fallback likely) | ~20 | ~140 |
| Type B (Prose-Heavy) | 5 | 5 | ~25 | ~125 |
| Type C (Hybrid) | 5 | 6 | ~20 | ~120 |
| Type D (Appendix-Dominant) | 3 | 4 | ~10 | ~40 |
| Type E (Unclassified) | 4 | 5 | ~5 | ~25 |
| **Total** | | | **80** | **~450 (over budget)** |

You're likely over the 400 ceiling before processing starts. Options:
- Merge small adjacent sections before splitting (combine H1s under 5k chars)
- Consolidate Type D appendix docs (glossaries, crosswalks) into shared reference docs
- Exclude boilerplate sections (Document History, Approval Signatures) from output entirely
