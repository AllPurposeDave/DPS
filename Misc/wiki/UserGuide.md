# InfoSec Policy Wiki — User Guide

Operational checklists the human owner should follow alongside the
automated ingest process.

## Ingest workflow

```
 ┌─────────────────────┐
 │  Prepare raw doc     │
 │  (≤ 20k chars, move  │
 │  appendix controls)  │
 └────────┬────────────┘
          │
          ▼
 ┌─────────────────────┐
 │  Drop doc into raw/  │
 │  ingest @<filename>  │
 └────────┬────────────┘
          │
          ▼
 ┌─────────────────────┐
 │  Chunk detection:    │
 │  slug prefix match?  │
 └────────┬────────────┘
          │
     ┌────┴────┐
     │ Match?  │──Yes──▶ Claude asks:
     └────┬────┘         append as chunk
       No │              or standalone?
          ▼
 ┌─────────────────────┐
 │  Slug collision      │
 │  check in INDEX      │
 └────────┬────────────┘
          │
     ┌────┴────┐
     │ Exists? │──Yes──▶ Claude asks:
     └────┬────┘         overwrite, version
       No │              as -v2, or abort?
          ▼
 ┌─────────────────────┐
 │  Extract, write      │
 │  policy + topics,    │
 │  update INDEX        │
 └────────┬────────────┘
          │
          ▼
 ┌─────────────────────┐
 │  Post-ingest spot    │
 │  check (slug, URL,   │
 │  controls, topics)   │
 └────────┬────────────┘
          │
          ▼
     ┌────┴────┐
     │ 10–15   │──No──┐
     │ docs?   │      │
     └────┬────┘      │
       Yes│           │
          ▼           │
 ┌─────────────────┐  │
 │ Review topics/  │  │
 │ for bloat;      │  │
 │ split or trim   │  │
 └────────┬────────┘  │
          │           │
          ▼           │
     ┌────┴────┐      │
     │ More    │◄─────┘
     │ docs?   │
     └────┬────┘
       No │
          ▼
 ┌─────────────────────┐
 │  Consolidate topics  │
 │  (on demand)         │
 └─────────────────────┘
```

## Pre-ingest checklist

- [ ] Raw doc is ≤ 20,000 characters. Split oversized docs before dropping
      them into `raw/`.
- [ ] If the doc has appendices containing **numbered controls or control
      matrices** (common in NIST/FedRAMP-derived policies), verify those
      appendices are included in the body — the ingest contract strips
      `Appendix *` sections by default. Move critical appendix controls
      into the main `Controls` section of the raw doc before ingesting.
- [ ] If the doc contains a `PublishedURL` line in the header, confirm the
      URL is correct. If no URL exists, the policy will be filed with
      `published_url: null` — you can add it later.

## Mid-ingest review: topic page size

After every **10–15 ingested docs**, pause and review topic pages for
bloat:

1. Scan `wiki/topics/` for files that have grown large (rough threshold:
   > 3,000 characters or > 15 entries in `## Policies`).
2. For oversized topic pages, consider:
   - **Splitting** into subtopics (set `parent:` in frontmatter).
   - **Trimming hooks** — each policy line under `## Policies` should be
     a single short sentence, not a paragraph.
3. After splitting, update `wiki/INDEX.md` to nest the new subtopic
   under its parent in `## By Topic`.

This keeps topic pages lean and prevents context-budget overruns during
future ingests (the model reads 2–4 topic pages per ingest).

## Ingest decision points

During ingest, Claude will pause and ask you to decide on two situations:

**Chunk detection** — If the filename's slug is a prefix match for an
existing policy in INDEX (e.g., `acme-policy-appendix-a` matches
`acme-policy`), Claude will ask: append as a chunk, or file as standalone?
A shared prefix isn't proof of a parent/child relationship — use your
judgment.

**Slug collision** — If the computed slug already exists in INDEX, this is
a policy update. Claude will offer three options:
1. **Overwrite** — minor edits, typos, clarifications (bumps `updated:`).
2. **Version as `-v2`** — major rewrite with controls added or removed.
3. **Abort** — don't touch anything.

## Post-ingest spot checks

After each ingest, verify the summary the model provides:

- [ ] Slug written matches expectations.
- [ ] `published_url` is present and correct (or noted as `null`).
- [ ] Control count looks reasonable for the source doc.
- [ ] Topic assignments make sense — veto or rename if not.
- [ ] Skim the written `wiki/policies/<slug>.md` to confirm controls
      were not truncated or paraphrased.

## Topic consolidation

Between batches, run `consolidate topics` to catch sprawl. Claude will
scan all topic pages and flag duplicates or near-duplicates (similar slugs,
overlapping aliases, same policies listed). It proposes merges and waits
for your approval before rewriting anything.
