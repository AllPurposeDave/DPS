# InfoSec Policy Wiki — User Guide

Checklists for the human owner alongside the automated ingest process.


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
