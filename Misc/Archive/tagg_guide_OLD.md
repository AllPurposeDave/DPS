# Tagging Guide — Extracting Tags from .md and Injecting into .docx

This guide walks you through using Claude Sonnet (or any capable LLM) to pull
key, unique tags out of a markdown (`.md`) version of a document, then feed
those tags into the DPS pipeline so they end up stamped onto the matching
`.docx` sub-documents at Step 5 (Metadata Injection).

---

## Why tag documents at all?

Tags live inside the metadata block that Step 5 prepends to every sub-document
(see [add_metadata.py](../scripts/add_metadata.py)). Downstream RAG / Copilot
retrieval uses those tags as discriminators — good tags should be:

- **Unique** to the document (not generic words every doc would also match).
- **Retrieval-worthy** — phrases a user would actually type when searching.
- **Stable** — proper nouns, system names, framework IDs, controls families,
  regulation names, not transient phrasing.

Auto-generated tag sources (doc type, standard sections found, unique acronyms)
already cover structural signals. This guide is about the **custom tags** layer
— the semantic keywords a human would care about that only an LLM read of the
content will surface.

---

## End-to-end flow

```
.docx  ──Step 7──►  .md  ──Sonnet prompt──►  tag list  ──paste──►  Acronym_Definitions.xlsx
                                                                     "Custom Tags" sheet
                                                                            │
                                                                       Step 5 reads
                                                                            │
                                                                            ▼
                                                                 .docx with tags stamped
```

You only need a markdown version of the doc to do the LLM extraction. If you
haven't run Step 7 yet, run the pipeline up through it, or convert the one
document you care about:

```bash
python scripts/docx2md.py --config dps_config.xlsx input/ output/7\ -\ markdown/
```

---

## Step 1 — Pick the markdown file

Open the `.md` for the document you want to tag, typically under
[output/7 - markdown/](../output/7%20-%20markdown/). Note its **base filename**
(without the `.md` extension and any `_fixed` / `_optimized` suffix) — that's
what you'll enter in the `Document_Name` column later. The matcher in
[add_metadata.py:816-875](../scripts/add_metadata.py#L816-L875) is tolerant of
case and underscores/spaces, but cleaner names match more reliably.

---

## Step 2 — Prompt Sonnet

Open a Sonnet chat (Claude.ai, Continue, or the API) and paste the full
markdown body along with the prompt below. The prompt is tuned to produce
output in exactly the shape the `Custom Tags` sheet expects.

> ### Prompt to paste into Sonnet
>
> ```
> You are tagging a policy/standard/procedure document for a RAG retrieval
> system. I will paste the full markdown contents below. Your job is to
> surface the KEY, UNIQUE tags that will help a retrieval system discriminate
> THIS document from ~100 other infosec/policy documents in the same corpus.
>
> Rules for tag selection:
>   1. Prefer PROPER NOUNS and specific identifiers — system names, framework
>      IDs (e.g., NIST 800-53 AC-2), regulation names (e.g., HIPAA, FedRAMP),
>      named technologies, team names, internal programme names.
>   2. Prefer DOMAIN KEYWORDS a user would literally type when searching for
>      this document (e.g., "mfa enrollment", "byod", "data classification").
>   3. Reject generic words that would apply to most policy documents
>      ("policy", "security", "document", "requirements", "compliance"),
>      unless paired with a specific qualifier (e.g., "PCI compliance" is OK).
>   4. Reject section-structure words ("scope", "purpose", "roles") —
>      the pipeline already tags those automatically.
>   5. Reject acronyms that are already defined elsewhere — the pipeline
>      already tags unique acronyms automatically. Only include an acronym
>      if it's a brand or product name (e.g., "Okta", "CrowdStrike").
>   6. Keep each tag short: 1–4 words, lower-case unless a proper noun.
>   7. Produce 8–15 tags total. Quality over quantity.
>
> Output format — return EXACTLY these two lines, nothing else, no prose,
> no markdown fences, no explanation:
>
> Document_Name: <base filename you infer from the doc, no extension>
> Tags: tag one, tag two, tag three, ...
>
> Here is the markdown:
>
> <PASTE FULL .md CONTENTS HERE>
> ```

Sonnet should reply with something like:

```
Document_Name: Access Control Policy
Tags: access provisioning, joiner-mover-leaver, privileged access review, Okta, Azure AD, least privilege, quarterly recert, HIPAA
```

If the first line doesn't match your actual filename (because the doc title
differs from the filename), overwrite it with the real base filename — that's
the value the pipeline matches on.

---

## Step 3 — Paste into `Acronym_Definitions.xlsx`

Open the acronym definitions workbook referenced in your config. Default path
(see `metadata.tags.acronym_definitions_file` in
[dps_config_fallback.yaml](../dps_config_fallback.yaml)):

```
./input/Acronym_Definitions.xlsx
```

Add (or edit) a sheet named **`Custom Tags`** with this structure:

| Document_Name          | Tags                                                                                       |
|------------------------|--------------------------------------------------------------------------------------------|
| Access Control Policy  | access provisioning, joiner-mover-leaver, privileged access review, Okta, Azure AD, HIPAA  |
| Data Classification    | data classification, PII, PHI, public/internal/confidential, DLP, Purview labels           |
| ...                    | ...                                                                                        |

Rules that keep the Step 5 loader happy (see
[add_metadata.py:458-490](../scripts/add_metadata.py#L458-L490)):

- Sheet name **must contain** `custom tags` (case-insensitive).
- Header row must include a column whose name contains `document`, `doc`,
  `file`, or `name`, **and** a column whose name contains `tag`.
- `Tags` cell must be a **comma-separated string** (not a list, not one tag per row).
- One row per document. Re-running the pipeline overwrites previous output,
  so you can freely edit and re-run.
- `Document_Name` is matched with `match_doc_name()` — underscores, `.docx`,
  and `_fixed` suffixes are normalised away, so you don't need to include them.

---

## Step 4 — Run Step 5 (Metadata Injection)

From the project root:

```bash
python run_pipeline.py --step 5
```

Or standalone:

```bash
python scripts/add_metadata.py --config dps_config.xlsx
```

Watch the console output. For each file you should see a line like:

```
    Processing Access Control Policy - Scope.docx...
      Document:   Access Control Policy (from auto)
      ...
      Tags:       Type-B, has-scope, has-controls, access provisioning, joiner-mover-leaver, Okta, Azure AD, HIPAA (from auto)
```

Your custom tags appear **merged** with the auto-generated ones (doc type,
sections-found, unique acronyms, static tags). Duplicates are removed
case-insensitively by
[generate_tags()](../scripts/add_metadata.py#L781-L875).

---

## Step 5 — Verify

Three places to verify tags landed correctly:

1. **`metadata_manifest.csv`** in
   [output/5 - metadata/](../output/5%20-%20metadata/) — has a `tags` column
   and a `tag_count` column per sub-document. Grep for your expected values.
2. **Open a stamped `.docx`** in Word — the `Tags` heading should be visible
   in the metadata block at the top (or wherever `metadata.placement` is set).
3. **If tags are missing**, the most common causes are:
   - `Document_Name` typo — the matcher does tolerant matching but not fuzzy
     matching. Confirm a substring overlap with the actual filename.
   - Sheet name doesn't contain `custom tags`.
   - `Tags` column is empty or uses semicolons instead of commas.
   - The sub-document's *parent* doesn't match — Step 5 looks up tags against
     the parent document name from `split_manifest.csv`, not the sub-doc name.

---

## Tips for scaling to many documents

- **Batch the LLM step.** Paste one document per conversation turn and keep
  the system prompt stable; Sonnet will stay consistent in format.
- **Review for over-fitting.** If a tag is *only* meaningful to the author
  and never something a searcher would type, cut it.
- **Don't re-tag on every run.** Custom tags are additive to the auto layer,
  so once you've added 8–15 solid ones per doc you're done. Only revisit
  when the document itself materially changes.
- **Consider static tags** (`metadata.tags.static_tags` in config) for values
  that apply to *every* document (e.g., `InfoSec`, `GCC-High`). Don't waste
  custom tags on org-wide labels.
