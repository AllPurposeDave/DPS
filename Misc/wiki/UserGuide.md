# InfoSec Policy Wiki — User Guide

The wiki is a retrieval-optimized staging layer between pipeline markdown
output and a GCC High SharePoint document library that serves a Microsoft
365 Copilot declarative agent.

## End-to-end pipeline

```
Source .docx policies
      │
      ▼
DPS pipeline (Step 7 docx2md → ~15k char markdown files)
      │
      ▼
Wiki ingest (organize into 3 domain folders, normalize H1/H2, self-contain)
      │
      ▼
Markdown → .docx conversion (H1/H2 preserved, metadata written to core properties)
      │
      ▼
SharePoint document library upload (metadata columns populated)
      │
      ▼
Copilot Studio agent with 3 topics, each scoped to one domain folder
```

## The three domains

The wiki is organized into three folders, each mapping 1:1 to a SharePoint
folder and a Copilot Studio topic:

| Wiki folder | Copilot topic | Covers | Families |
|-------------|---------------|--------|----------|
| `access-and-identity/` | **Access & Identity** | Who can do what, authentication, vetting | AC, IA, PS |
| `system-protection/` | **System Protection** | Configuration, encryption, engineering, physical | CM, SC, SI, SA, MP, MA, PE |
| `operations-and-response/` | **Operations & Response** | Audit, incident, continuity, risk, governance | AU, IR, CP, RA, PL, PM, CA, AT |

Three topics, three folders, three distinct user intents. This is the
retrieval architecture.

## Ingest decision points

Claude runs ingest in batch and flags issues rather than pausing. Review the
post-ingest summary for:

**Ambiguous routing** — file had competing control families. Default routing
sent it to `operations-and-response/`. Decide whether to move it.

**Table conversion flags** — complex requirement tables were not
auto-converted. Manually rewrite as structured H2 + paragraphs or decide
to keep the table (accepting reduced retrieval quality).

**Splits** — source file was split into N wiki documents. Review that the
split boundaries are logical (one topic per output file).

## Post-ingest spot checks

- [ ] Every file landed in the expected domain folder (access controls in
      `access-and-identity/`, not `system-protection/`).
- [ ] Every doc has exactly one H1 with a descriptive title.
- [ ] Every doc starts with the self-containment preamble blockquote
      (family, source, scope).
- [ ] Controls are verbatim — no paraphrasing crept in.
- [ ] `PublishedURL` present in preamble (or explicitly noted null).
- [ ] Cross-references include context, not just a bare ID.
- [ ] Acronyms are expanded on first use.
- [ ] No tables in requirement content.

## SharePoint document library setup

### Site columns to create

| Column | Type | Source |
|--------|------|--------|
| Domain | Choice (Access & Identity, System Protection, Operations & Response) | Folder name |
| Family | Choice (AC, AU, CM, CP, IA, IR, MA, MP, PE, PL, PM, PS, RA, SA, SC, SI, AT, CA) | Detected from content |
| PublishedURL | Hyperlink | From .docx custom property |
| SourcePolicy | Single line text | From .docx custom property |
| LastIngested | Date | Auto-set on upload |

### Folder structure in SharePoint

Mirror the wiki folder structure exactly:

```
<Site> / Documents / Policy Knowledge Base /
  Access and Identity /
  System Protection /
  Operations and Response /
```

Upload preserves the folder hierarchy. Set metadata columns during upload
(via PowerShell/PnP or Power Automate).

## Copilot Studio agent configuration

Create a declarative agent with three topics:

### Topic 1: Access & Identity
- **Knowledge source:** SharePoint folder `Access and Identity`
- **Trigger phrases:** access, login, authentication, MFA, multifactor,
  privileged, account, password, contractor access, screening
- **Response style:** Quote control requirements verbatim; cite with
  PublishedURL.

### Topic 2: System Protection
- **Knowledge source:** SharePoint folder `System Protection`
- **Trigger phrases:** configuration, baseline, encryption, cryptographic,
  patch, vulnerability, media, maintenance, physical security, acquisition,
  supply chain
- **Response style:** Quote control requirements verbatim; cite with
  PublishedURL.

### Topic 3: Operations & Response
- **Knowledge source:** SharePoint folder `Operations and Response`
- **Trigger phrases:** incident, audit, log, recovery, continuity,
  contingency, risk assessment, training, awareness, compliance, ATO,
  assessment, authorization
- **Response style:** Quote control requirements verbatim; cite with
  PublishedURL.

**Fallback:** If a query doesn't trigger any topic, the default agent
searches all three folders. Accept reduced precision in this case.

## Retrieval accuracy testing

After SharePoint upload, test with a representative set of queries:

1. **Control lookups (6 queries):** "What does AC-2 say about account
   management?" / "Show me the encryption requirements." / etc. Verify
   the correct document appears in the top 3 results.
2. **Plain-language queries (6 queries):** "Can contractors access
   production?" / "How often do we patch?" / etc. Verify a relevant doc
   is retrieved and the answer quotes source text.
3. **Topic routing (3 queries per topic, 9 total):** Verify each query
   triggers the expected Copilot Studio topic.
4. **Cross-domain query (1-2):** "What's the incident response procedure
   for unauthorized access?" Should synthesize from multiple folders.

**Target:** correct document in top-3 for 80%+ of queries. Below that,
review document structure (H1 titles too generic? Self-containment preamble
missing? Too many tables?) and iterate.
