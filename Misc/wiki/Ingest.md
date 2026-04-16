# InfoSec Policy Wiki — Ingest Contract

Stage pipeline-produced markdown (Step 7 output) into the wiki as
retrieval-optimized chunks for Microsoft 365 Copilot.

## Layout
- `wiki/access-and-identity/` — AC, IA, PS
- `wiki/system-protection/` — CM, SC, SI, SA, MP, MA, PE
- `wiki/operations-and-response/` — AU, IR, CP, RA, PL, PM, CA, AT, and unmapped
- `wiki/INDEX.md` — auto-generated manifest (regenerated every ingest)
- `wiki/ACRONYMS.md` — auto-generated glossary of unique acronyms

## Triggers
- `ingest @<filename>` — process a single source `.md` file

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

## Ingest loop

1. **Extract** `title`, `PublishedURL` (null if absent), `scope` (verbatim),
   and `purpose` (verbatim, if present) from frontmatter.
2. **Split at H2 boundaries** if the file mixes unrelated families or
   exceeds ~20k chars. One control / one tightly related sub-family per
   output file.
3. **Route** per the table above. Write to
   `wiki/<domain>/<family-lower>-<descriptive-slug>.md` — kebab-case,
   ≤40 chars total.
4. **Rewrite to the template below.** Exactly one descriptive H1
   (promote a control ID into H1 for single-control docs). Flatten
   H3+ to paragraphs. Strip TOC, Appendix, Revision History.
   **Preserve requirement wording verbatim.**
5. **Convert requirement tables to H2 + paragraph.** Tables retrieve
   poorly in Copilot. Flag genuinely complex ones for human review
   rather than lossy-convert them.
6. **Acronyms.** Expand on first use in the doc ("Multifactor
   Authentication (MFA)"). Register every unique acronym in
   `wiki/ACRONYMS.md` with its expansion and a link to this doc as
   the first-seen source. If already registered with a *different*
   expansion (genuine collision), add a disambiguated entry
   (`**CA (Assessment & Authorization)**` vs
   `**CA (Certification Authority)**`) and flag.
7. **Regenerate** `wiki/INDEX.md` and `wiki/ACRONYMS.md`.

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
signal — specificity wins. The blockquote preamble makes every retrieved
chunk self-contained.

## Report (per file)
Surface: domain folder chosen, any routing ambiguity, splits performed,
table-conversion flags, and acronym collisions.

## Hard rules
- **Verbatim.** Never paraphrase, renumber, or re-bullet control
  requirements. Markdown normalization (headings, whitespace) is fine.
- **Never invent.** If it's not in the source, don't write it. Missing
  `PublishedURL` → say so in the preamble.
- **Flag, don't guess.** Ambiguities go in the report.
- **`INDEX.md` and `ACRONYMS.md` are regenerated**, never hand-edited.
