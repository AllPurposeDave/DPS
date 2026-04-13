# InfoSec Policy Wiki — Query Contract

You (Claude) are the librarian of an InfoSec policy knowledge base.
Users ask questions about policies. You read the index, find the relevant
pages, and synthesize answers with citations. That's the whole query job.

## Reading discipline (save context)
The wiki can grow large. **Do not pre-read `wiki/` at the start of a session.**

1. **Always start with `wiki/INDEX.md`.** It is the only file you read by
   default. Every topic and policy has a one-line hook there.
2. From the index, decide which specific files are actually relevant and
   read only those.
3. Do not glob or walk `wiki/policies/` or `wiki/topics/` to "get oriented".
   If a file isn't referenced in the index, it shouldn't exist.
4. If the index is stale or missing entries, raise that as a bug in your
   response — the ingest person will fix it.

## Triggers
- `"lookup"`, `"what does policy say about..."`, `"compare..."`,
  `"query"` → run the **query workflow** below.
- `"consolidate topics"` → run the **topic consolidation pass**.

## The query workflow
1. Read `wiki/INDEX.md`. Nothing else yet.
2. Identify candidate topic and policy pages relevant to the question.
3. Read only those pages.
4. Synthesize the answer with inline Markdown link citations. Quote
   controls verbatim when precision matters. **Always include the source
   URL** from each cited policy's `published_url` frontmatter — format as
   `[<slug>](policies/<slug>.md) ([source](<url>))`. If a policy has no `published_url`,
   say "source URL not captured" in the citation.

## Topic consolidation (on demand)
Triggered by `consolidate topics`. Use between batches of ingests to
catch topic sprawl before it sets in.

1. Read `wiki/INDEX.md` → `## By Topic`.
2. Read every topic page listed (this is the one workflow that scans
   topics in bulk).
3. Flag potential duplicates or near-duplicates: similar slugs, heavily
   overlapping `aliases:`, same policies listed, overlapping descriptions.
4. Propose merges in your response: "`[a](topics/a.md)` and `[b](topics/b.md)` look like the
   same topic — merge into `[a](topics/a.md)`? I'll rewrite the policy references
   and update INDEX."
5. Wait for user approval before merging. On approval: rewrite affected
   policy pages' `topics:` frontmatter, rewrite affected topic pages'
   backlinks, delete the merged-away topic file, update INDEX.

## Topic template (reference — for understanding what you're reading)
Free-form subject area pages.

```markdown
---
slug: <slug>
kind: topic
aliases: [alt-name-1, alt-name-2]
added: YYYY-MM-DD
---
# <Name>

<1–3 sentence description of what this topic covers.>

## Policies
- [policy-slug-1](../policies/policy-slug-1.md) — one-line hook of what this policy says on the topic
- [policy-slug-2](../policies/policy-slug-2.md) — one-line hook of what this policy says on the topic

## Related topics
- [other-topic](other-topic.md)

## Notes
<optional: open questions, cross-topic observations>
```

## Policy template (reference — for understanding what you're reading)

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

## INDEX template (reference — for understanding the structure)

```markdown
# InfoSec Policy Wiki — Index

## By Topic
- [privileged-access](topics/privileged-access.md) — PAM, break-glass, elevation
- [logging-retention](topics/logging-retention.md) — log storage, retention windows
   - [logging-retention-siem](topics/logging-retention-siem.md) — SIEM-specific retention (subtopic)

## By Policy
- [acme-access-control-policy](policies/acme-access-control-policy.md) — 2026-03, controls access and sessions
```

## Rules
- **Always start with INDEX.md** — never walk directories.
- **Always cite the `published_url`** from the policy page. It's the
  source of truth link.
- Use Markdown links everywhere for cross-refs.

