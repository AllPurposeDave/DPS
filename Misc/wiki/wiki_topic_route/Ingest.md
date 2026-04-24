# InfoSec Policy Wiki — Ingest Contract

Stage pipeline-produced markdown (Step 7 output) into the wiki as
retrieval-optimized chunks for Microsoft 365 Copilot.

## Layout
```
wiki/
  access-and-identity/        ← CoPilot topic (AC, IA, PS)
    account-management/       ← sub-topic (created when needed)
      ac-2-account-management.md
  system-protection/          ← CoPilot topic (CM, SC, SI, SA, MP, MA, PE)
  operations-and-response/    ← CoPilot topic (AU, IR, CP, RA, PL, PM, CA, AT, unmapped)
  INDEX.md                    ← auto-generated manifest
```
Depth rule: `domain/subtopic/file.md` only — no deeper nesting.

## Triggers
- `ingest @<filename>` — process a single source `.md` file.
  Use Sonnet 4.5, 180k context, one-pass only (no iterative back-and-forth).

One file at a time keeps per-doc accuracy high and avoids cross-doc
context bleed.

## Routing
Route by **dominant control family** in the body. Scan for control-ID
patterns (`AC-2`, `CM-6(1)`, `IR-4`); the family with the most hits wins.
No IDs → infer from title and source policy. Still ambiguous → route to
`operations-and-response/` and flag.

| Families | Folder |
|---|---|
| AC, IA, PS | `access-and-identity/` |
| CM, SC, SI, SA, MP, MA, PE | `system-protection/` |
| AU, IR, CP, RA, PL, PM, CA, AT | `operations-and-response/` |
| Unmapped / org-specific | `operations-and-response/` (flag) |

Within a domain, group related controls into a **named subfolder**
(= new CoPilot sub-topic) when any output file would exceed 20,000 chars
or when 3+ files share a clear sub-theme (e.g., `account-management/`,
`authentication/`, `incident-response/`). Subfolder name: descriptive
kebab-case, ≤40 chars. Names must be **precise and non-overlapping** —
the orchestrator routes on these names, so ambiguity degrades routing.

## Ingest loop

1. **Extract** `title`, `PublishedURL` (null if absent), `scope` (verbatim),
   and `purpose` (verbatim, if present) from frontmatter.
2. **Split at H2 boundaries** when the file exceeds **20,000 chars** or
   mixes unrelated families. Each resulting group routes to a **named
   subfolder** — that subfolder becomes a new CoPilot Studio sub-topic
   with a descriptive title. One control / one tightly related sub-family
   per output file.
3. **Route** per the table above. Write to
   `wiki/<domain>/[<subtopic>/]<family-lower>-<descriptive-slug>.md` —
   kebab-case, ≤40 chars per segment.
4. **Rewrite to the template below.** H1 for title, H2 for section
   headers only — **no H3 or deeper in any output file.** Flatten all
   H3+ from source to paragraphs. Strip TOC, Appendix, Revision History.
   **Preserve requirement wording verbatim.**
5. **Convert requirement tables to H2 + paragraph.** Tables retrieve
   poorly in Copilot. Flag genuinely complex ones for human review
   rather than lossy-convert them.
6. **Regenerate** `wiki/INDEX.md`.

## Document template

```markdown
# <Specific descriptive title — e.g., "AC-2 Account Management">

> **Family:** <Family name> | **Source:** [<policy name>](<PublishedURL>)
> **Scope:** <verbatim scope from source>

## Requirement

<verbatim control requirement text>

## Implementation Notes

<verbatim supplemental guidance from source, if present>

## Related

- [<other-doc-title>](<relative-path>) — <context on the link, not a bare ID>
```

Why this shape: Copilot chunks at H1/H2. The H1 is the top retrieval
signal — specificity wins. The blockquote preamble travels with every
retrieved chunk, so each chunk is self-contained (Family + Source + Scope).

## Report (per file)
Surface: domain folder and subtopic chosen, any routing ambiguity,
splits performed, and table-conversion flags.

## Hard rules
- **Verbatim.** Never paraphrase, renumber, or re-bullet control
  requirements. Markdown normalization (headings, whitespace) is fine.
- **Never invent.** If it's not in the source, don't write it. Missing
  `PublishedURL` → say so in the preamble.
- **Flag, don't guess.** Ambiguities go in the report.
- **H2 max.** Output files use only H1 (document title) and H2 (section
  headers). All H3+ content from source is flattened to paragraphs.
- **20k max.** No output file exceeds 20,000 characters. Files that
  would exceed this are split into separate named-subfolder files
  (new sub-topics).
- **`INDEX.md` is regenerated**, never hand-edited.
