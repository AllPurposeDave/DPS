# InfoSec Policy Wiki — Draft Contract

Author net-new wiki documents in Ingest-ready format, grounded in existing
wiki content. Use when no source `.md` file exists yet — e.g., filling a gap
identified in the INDEX, drafting a control not yet covered, or writing a
policy from notes or a brief.

## Triggers
- `draft @<topic-or-control-id>` — draft one document for the named topic.
  Use Sonnet 4.5, 180k context, one-pass only.
- `draft @<topic> from <notes>` — draft from freeform notes or a brief pasted
  inline.

One document per run.

## Before you write

1. **Scan the wiki.** Read `wiki/INDEX.md` and any related files in the
   relevant domain folder. Identify:
   - What's already covered (don't duplicate).
   - What's adjacent (will become `## Related` links).
   - Gaps the new document fills.

2. **Determine routing** using the same family table as Ingest:

   | Families | Folder |
   |---|---|
   | AC, IA, PS | `access-and-identity/` |
   | CM, SC, SI, SA, MP, MA, PE | `system-protection/` |
   | AU, IR, CP, RA, PL, PM, CA, AT | `operations-and-response/` |
   | Unmapped / org-specific | `operations-and-response/` (flag) |

3. **Choose the output path.**
   `wiki/<domain>/[<subtopic>/]<family-lower>-<descriptive-slug>.md`
   — kebab-case, ≤40 chars per segment. Add a named subfolder when 3+ files
   in the domain share a clear sub-theme.

## Drafting rules

- **Ground every requirement in a real standard.** NIST SP 800-53, ISO 27001,
  CIS Controls, or org policy. Cite the source in the blockquote preamble
  (`**Source:**`). If no authoritative source is available, write
  `**Source:** *No authoritative source provided — flag for review*`.
- **Verbatim where available.** If you have the canonical requirement text
  (from notes, a pasted excerpt, or a known standard), reproduce it verbatim
  under `## Requirement`. Do not paraphrase.
- **Flag, don't invent.** If requirement wording is missing, write a clearly
  marked placeholder: `[PLACEHOLDER — insert verbatim requirement text]`.
  Never synthesize a requirement from general knowledge and present it as
  authoritative.
- **H2 max.** Use only H1 (document title) and H2 (section headers).
  No H3 or deeper.
- **20k max.** If a draft would exceed 20,000 chars, split it at H2 boundaries
  into separate named-subfolder files and report the split.
- **No invented links.** Only link to wiki files that already exist (verified
  via INDEX.md scan). If a relevant file doesn't exist yet, note it in the
  report: `[TODO — draft <slug> to complete this cross-reference]`.

## Document template

```markdown
# <Specific descriptive title — e.g., "AC-2 Account Management">

> **Family:** <Family name> | **Source:** [<standard or policy name>](<URL or "No URL — flag for review">)
> **Scope:** <scope statement — verbatim if provided, else [PLACEHOLDER]>

## Requirement

<verbatim requirement text, or [PLACEHOLDER — insert verbatim requirement text]>

## Implementation Notes

<supplemental guidance, implementation detail, or org-specific context.
 If none is available, omit this section entirely rather than padding it.>

## Related

- [<existing-doc-title>](../relative-path-to-existing-wiki-file.md) — <one-line context, not a bare ID>
```

## Report (per draft)

Surface:
- Domain folder and subtopic chosen, with rationale.
- Source standard cited and whether requirement text is verbatim or placeholder.
- Any splits performed (with resulting file paths).
- Missing cross-references flagged as TODOs.
- Any routing ambiguity.

## Hard rules
- **Never invent requirement text.** Placeholders are always preferable to
  fabricated policy language.
- **No H3+.** All structure below H2 becomes paragraphs.
- **No links to non-existent wiki files.** Verify against INDEX.md before
  writing any `## Related` entry.
- **Flag gaps, don't fill them silently.** Placeholders must be visible and
  labeled, not buried in prose.
- **`INDEX.md` is not updated by Draft.** Run `ingest` after drafts are
  reviewed and finalized to regenerate the index.
