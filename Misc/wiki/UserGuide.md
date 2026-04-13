# InfoSec Policy Wiki — User Guide

Checklists for the human owner alongside the automated ingest process.

## Pre-ingest checklist

- [ ] Appendix controls get stripped by default — move any numbered
      controls or control matrices into the main `Controls` section
      before ingesting.
- [ ] Confirm `PublishedURL` in the header is correct. Missing URLs
      will be filed as `published_url: null`.

## Mid-ingest review: topic page size

Every **10–15 docs**, review topic pages for bloat (>3,000 chars or
>15 policy entries). Split into subtopics or trim hooks as needed,
then update INDEX.

## Ingest decision points

Claude will pause and ask on two situations:

**Chunk detection** — Filename slug prefix-matches an existing policy.
 Decide: append as chunk or file standalone. Shared prefix ≠ parent/child.

**Slug collision** — Slug already exists in INDEX. Options:
1. **Overwrite** — minor edits, typos, clarifications.
2. **Version as `-v2`** — major rewrite, controls added or removed.
3. **Abort** — don't touch anything.

## Post-ingest spot checks

- [ ] Slug matches expectations.
- [ ] `published_url` present and correct (or noted `null`).
- [ ] Control count reasonable for the source doc.
- [ ] Topic assignments make sense.
- [ ] Skim `wiki/policies/<slug>.md` — controls not truncated or paraphrased.

## Topic consolidation

Between batches, run `consolidate topics`. Claude flags duplicate/near-
duplicate topics and proposes merges — waits for approval before rewriting.
