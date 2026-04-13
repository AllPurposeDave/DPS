# InfoSec Policy Wiki — Ingest Contract

You (Claude) are the librarian of an InfoSec policy knowledge base.
The user drops policy markdown into `raw/`. You file it into `wiki/policies/`
and organize it by topic. That's the ingest job.

## Layout
- `raw/` — new doc drop zone. **Never edit here.**
- `wiki/policies/` — one cleaned page per ingested policy.
- `wiki/topics/` — topic pages. Free-form subject areas.
- `wiki/INDEX.md` — running index. Sections: `## By Topic`, `## By Policy`.

## Triggers
- `"ingest @<filename>"` → run the **ingest loop** below.
  One doc per invocation. The user brings the doc into context with `@`.

## The ingest loop (one doc per invocation)
The user invokes `ingest @<filename>`.

1. Read `wiki/INDEX.md`. This is the **sole source of truth** for what
   policies and topics exist. Do not walk `wiki/policies/` or
   `wiki/topics/` directories at any point during ingest.
2. **Chunk detection.** Compute the base slug from `<filename>`. Scan
   `## By Policy` in INDEX for the longest prefix slug that matches
   (e.g., ingesting `acme-policy-appendix-a.md` and `acme-policy` is
   listed in INDEX). If a prefix match is found, **stop and confirm
   with the user** before appending as a chunk:
  > "`<filename>` looks like a chunk of `[<parent-slug>](policies/<parent-slug>.md)`. Append to
   > it, or file as a standalone policy?"
   If chunk: append chunk content to the parent's `## Controls` section
   under a matching subheading. If standalone: continue with step 3.
3. **Extract**: title, scope, purpose, `PublishedURL` (the source
   URL line in the doc header), and the verbatim controls. Strip
   `Table of Contents`, `Appendix *`, `Revision History` sections. If `PublishedURL` is missing from the
   source, leave `published_url: null` and note it in your response.
4. **Slug collision check.** If the computed slug already appears in
   `## By Policy` in INDEX, this is an update to an existing policy —
   stop and follow `## Updates to existing policies` below.
5. Write `wiki/policies/<slug>.md` using the policy template.
6. **Topic decision tree.** For each topic the policy touches, walk this
   tree before creating anything new:
   - a. From the INDEX already read in step 1, scan `## By Topic` and
     pick 2–4 candidate topic pages whose slug or hook looks close to
     the policy's subject.
   - b. Read those candidate topic pages and check their `aliases:`
     frontmatter.
   - c. **Exact or near match** (same concept, different wording) → reuse
     the existing topic. If the policy introduced a new synonym, append
     that synonym to the topic's `aliases:` list.
   - d. **More specific than an existing topic** (e.g., policy is about
     SIEM log retention, existing topic is `logging-retention`) → create
     a subtopic file. Link it from the parent's `## Related topics`.
   - e. **Genuinely new area** → create a new topic file. Seed `aliases:`
     with 2–3 alternative phrasings.
7. Update `wiki/INDEX.md`: add the policy under `## By Policy`; ensure
   any new topics are listed in `## By Topic` with one-line hooks.
8. **Post-write summary.** State the slug written, number of controls
   extracted, and topics assigned.

## Updates to existing policies
Triggered when `ingest @<filename>` produces a slug that already exists
in `wiki/policies/`. Stop and ask the user:

> This slug already exists: `[<slug>](policies/<slug>.md)` (filed `<added>`). How should
> I handle this update?
> 1. **Overwrite** — minor edits, typos, clarifications.
> 2. **Version as `-v2`** — major rewrite, controls added or removed.
> 3. **Abort** — don't touch anything.

- **Overwrite**: rewrite the policy page in place.
  Git history preserves the diff.
- **Version**: write a new page `<slug>-v2.md` (or `-v3`, etc.), add
  `> Superseded by [<slug>-v2](<slug>-v2.md)` at the top of the old page, update
  INDEX to point `## By Policy` at the new version.
- **Abort**: no-op.

## Slug rule
kebab-case from the filename. Strip the extension, any leading date
(`2026-04-07-foo.md` → `foo`), and punctuation. Keep it > 3 characters
and no more than 40 characters. Truncate intelligently at a word boundary
if needed.

## Policy template (`wiki/policies/<slug>.md`)
```markdown
---
source: raw/<filename>
published_url: https://www.url.com/...   # from PublishedURL in the source; null if missing
added: YYYY-MM-DD
topics: [topic-slug-1, topic-slug-2]      # free-form topics
---
# <Policy Title>

**Scope:** <verbatim or faithful>
**Purpose:** <verbatim or faithful>

## Controls
<verbatim controls; preserve IDs and numbering; do not compress or paraphrase>

## Related
- Topics: [topic-slug-1](../topics/topic-slug-1.md), [topic-slug-2](../topics/topic-slug-2.md)

## Raw
[original](../../raw/<filename>)
```

## Topic template (`wiki/topics/<slug>.md`)
Free-form subject area pages.

```markdown
---
slug: <slug>
kind: topic
aliases: [alt-name-1, alt-name-2]   # alternate names the topic is known by
added: YYYY-MM-DD
---
# <Name>                    # e.g. "Privileged Access" or "Log Retention"

<1–3 sentence description of what this topic covers.>

## Policies
- [policy-slug-1](../policies/policy-slug-1.md) — one-line hook of what this policy says on the topic
- [policy-slug-2](../policies/policy-slug-2.md) — one-line hook of what this policy says on the topic

## Related topics
- [other-topic](other-topic.md)

## Notes
<optional: open questions, cross-topic observations>
```

## INDEX template (`wiki/INDEX.md`)
```markdown
# InfoSec Policy Wiki — Index

## By Topic
- [privileged-access](topics/privileged-access.md) — PAM, break-glass, elevation
- [logging-retention](topics/logging-retention.md) — log storage, retention windows
  - [logging-retention-siem](topics/logging-retention-siem.md) — SIEM-specific retention (subtopic)

## By Policy
- [acme-access-control-policy](policies/acme-access-control-policy.md) — 2026-03, controls access and sessions
```

Rewrite this file at the end of every ingest. Keep hooks under ~80 chars.
Nest subtopics under their parent in `## By Topic` for visual hierarchy.

## Rules
- **Never** invent facts not in the source. If it's not in the policy,
  don't write it down. This includes `published_url` — if the source has
  no `PublishedURL` line, leave the field `null`.
- **Never** paraphrase, renumber, or re-bullet controls. "Verbatim" means
  wording is preserved; markdown heading/whitespace normalization is fine.
- **Always** strip `Table of Contents`, `Appendix *`, `Revision History`.
  Preserve `Scope`, `Purpose`, and `Controls` sections.
- **Always** confirm before treating a filename as a chunk of an existing
  policy — shared naming prefixes are not proof of parent/child.
- Use Markdown links everywhere for cross-refs.

