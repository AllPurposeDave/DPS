# Type-Specific Addendums for Notebook 2

## Architecture: Hybrid Is the Base

Most IT/InfoSec policy documents are hybrids (mix of prose, tables, and procedures). The Notebook 2 base instructions in `notebook2-instructions.md` are written for this reality. They handle control tables, prose intent sections, embedded procedures, and reference tables in a single instruction set.

Type A, B, and D addendums exist as overrides for documents that are unusually dominated by one content type. Append ONE override to the base instructions when a document clearly falls outside the hybrid range. For the majority of documents, use base instructions alone with no addendum.

**When to append an override:**
- Type A: Profiling shows >40% table density. The doc is mostly control matrices.
- Type B: Profiling shows <10% table density. The doc is mostly prose narrative.
- Type D: Profiling shows >60% appendix material. The policy body is short; appendix dominates.
- Type E: The doc does not fit any pattern. Stop and calibrate.

**When NOT to append an override:**
- The doc has a mix of tables and prose (10-40% table density). Use base instructions as-is. This is the default case.

## Type A Override (Table-Heavy Control Docs, >40% table content)

```
TYPE A OVERRIDE (Table-Heavy Control Docs):
These instructions override specific base behaviors for documents dominated 
by control matrices.

- Expect control matrices with columns: Control ID, Description, Framework, 
  Status, Owner. Use the standard control paragraph pattern.
- Expect nested tables where a parent table contains sub-tables per control 
  family. Flatten parent row first, then each child row, preserving hierarchy: 
  "Under the [Parent Control Family] family, Control [Child ID] requires..."
- Expect merged cells spanning multiple rows for control family headers. Treat 
  merged cell content as context prefix for all spanned rows.
- If the Controls section exceeds 10 pages of prose after flattening, recommend 
  splitting into sub-documents by control family.
- Headers for control subsections: "Technical Controls for [Control Family] 
  under the [Policy Name]"
- Prose sections (Purpose, Scope, Intent) will be short. Still apply context 
  sentences and descriptive headers to them, but the bulk of the work is table 
  flattening.

BEFORE/AFTER EXAMPLE (Type A):
BEFORE (table row): | AC-2.1 | Account Management | Review quarterly | NIST AC-2 | Implemented | IT Security |
AFTER (prose): "Control AC-2.1 (Account Management) requires that all user accounts 
be reviewed quarterly by the designated system owner. This control maps to NIST SP 
800-53 AC-2. Implementation status: Implemented. Responsible party: IT Security Team. 
To prevent unauthorized access through stale accounts (policy intent), all user accounts 
must be reviewed quarterly (Control AC-2.1)."
```

## Type B Override (Prose-Heavy Intent Docs, <10% table content)

```
TYPE B OVERRIDE (Prose-Heavy Intent Docs):
These instructions override specific base behaviors for documents with minimal 
table content.

- Tables are typically small reference tables (2-5 rows), not control matrices. 
  Convert using reference table pattern, not control paragraph pattern.
- Role/responsibility tables: "[Role] is responsible for [responsibility] as 
  defined in the [Policy Name]."
- Long Intent sections are the primary value. Do not compress. Focus on adding 
  self-identifying context sentences and eliminating cross-references.
- Summary paragraphs should emphasize risk context and organizational rationale, 
  not just control counts.
- The main transformation work is structural: headers, context sentences, 
  cross-reference elimination. Table flattening is minimal.

BEFORE/AFTER EXAMPLE (Type B):
BEFORE (reference table row): | CISO | Approves all policy exceptions | Annual |
AFTER (prose): "The Chief Information Security Officer (CISO) is responsible for 
approving all policy exceptions as defined in the Information Security Program 
Charter. This approval authority is reviewed on an annual basis."
```

## Type D Override (Appendix-Dominant Docs, >60% appendix)

```
TYPE D OVERRIDE (Appendix-Dominant Docs):
These instructions override specific base behaviors for documents where appendix 
material exceeds 60% of total content.

- Framework crosswalk tables: "Control [Org ID] aligns with [NIST Ref] and 
  [CIS Ref]. Implementation note: [note text]. This mapping is maintained as 
  part of the [Policy Name] compliance documentation."
- Glossary tables: "In the context of the [Policy Name], '[Term]' is defined 
  as [definition]."
- Glossary definitions must match the original exactly. No paraphrasing of 
  defined terms.
- Crosswalk tables with many columns: ensure EVERY framework reference in 
  every row is preserved. Missing a single mapping degrades compliance queries.
- If appendix material exceeds 20 pages after flattening, split into separate 
  sub-documents: one for glossary, one for crosswalk, one for reference tables.
- Each appendix sub-document gets its own summary paragraph identifying it as 
  appendix material for the parent policy.
- The policy body (Purpose, Scope, Intent, Controls) is short. Process it 
  normally with base instructions. The addendum work is in the appendix.

BEFORE/AFTER EXAMPLE (Type D):
BEFORE (crosswalk row): | RM-1.1 | Risk Assessment | NIST RA-3 | CIS 16.1 | ISO 27005 Clause 8 | Annual | Implemented |
AFTER (prose): "Control RM-1.1 (Risk Assessment) under the Risk Management Policy 
aligns with NIST SP 800-53 RA-3, CIS Control 16.1, and ISO 27005 Clause 8. This 
control requires annual risk assessments. Implementation status: Implemented. This 
mapping is maintained as part of the Risk Management Policy compliance documentation."
```

## Type E (Unclassified)

```
TYPE E (Unclassified Documents):
This document did not fit Types A-D based on profiling data.

- BEFORE PROCESSING: Describe the document's structure to the user. List:
  (a) percentage of content in tables vs prose
  (b) section structure (does it follow Purpose/Scope/Intent/Controls/Appendix?)
  (c) any unusual structural elements (embedded forms, multi-level nested tables, 
      non-standard section ordering)
- ASK the user which existing type it most closely resembles, or whether it 
  needs a custom transformation approach.
- If the user selects a type, apply that type's override (or base instructions 
  if they select Hybrid/C).
- If the user requests custom handling, process section by section with explicit 
  user confirmation at each step before proceeding.
- Document the custom approach. If 3+ documents need the same custom approach, 
  draft a new type override and add it to the set.
```

## Hybrid-Specific Guidance (Built Into Base Instructions)

These behaviors are in the Notebook 2 base instructions because they apply to the majority of documents:

- Control matrices: flatten using standard control paragraph pattern
- Embedded procedures: preserve step ordering in prose, maintain sequence references
- Escalation matrix tables: preserve hierarchy with conditional escalation language
- Small reference tables (roles, definitions, applicability): convert with context attribution
- Bidirectional procedure-to-control linkage when procedures reference specific controls
- Mixed sections where prose and tables alternate: process sequentially, maintaining section context

## Addendum Versioning

Track versions separately:

```
Base Instructions (Hybrid): v1.0
Type A Override: v1.0
Type B Override: v1.0
Type D Override: v1.0
Type E: v1.0
```

When updating:
1. Increment version number
2. Log what changed and why
3. Save to Instruction Versions folder
4. Re-run most recent doc of that type to verify
5. Roll back immediately if update causes regressions

### Promotion and Removal Rules

- If same rule appears in 2+ type overrides: consider promoting to base instructions
- If a rule has not triggered a failure in last 10 docs of that type: flag for removal
- Combined word count (base + active override) should stay under 800 words
- When approaching 800 words: consolidate overlapping rules before adding new ones
