# Best Practices: Copilot Studio Agent with Unstructured Docs & Dataverse Tables

## Overview

This document covers best practices for a Copilot Studio agent that handles two distinct data shapes:

- **Unstructured (docx):** Large policy/wiki documents with many unique topics
- **Structured (Dataverse):** Control family tables with scoped requirements, control IDs, and relationships

---

## Part 1: Unstructured Documents (docx / Policy Files)

### Document Preparation

- Keep individual documents **under 20 pages / ~15,000 words**. Above this, Copilot's retrieval quality degrades.
- If a policy document is large, **split it by topic or section** into separate files before uploading. Each file should be self-contained.
- Use **clear headings, consistent formatting, and clean structure** — long unstructured walls of text produce inconsistent vector embeddings and poor chunk boundaries.
- Remove boilerplate headers/footers that add noise without semantic value.

### Knowledge Source Configuration

- Each agent supports up to **500 knowledge objects** but can only use **5 sources at a time** per query.

### Chunking Limitations and Workarounds

- Copilot Studio's built-in file ingestion uses **undocumented default chunking** — makers have no direct control over chunk size or boundaries.
- To compensate: pre-split documents so natural topic breaks align with file boundaries. Each file becomes its own retrievable chunk cluster.
- Ensure each chunk/file has **self-contained context** (e.g., include the policy name and scope at the top of each split file, not just in a master header).

### Prompting and Topic Routing

- Write **specific, scoped instructions** in the agent's system prompt: name the document set, the domain, and the expected answer format.
- For disambiguation between similar topics across multiple docs, use **Topic Inputs** to extract keywords (policy name, topic area) before routing to the knowledge source.
- Use the **AI orchestrator's topic description field** deliberately — the orchestrator uses these to decide which topic to trigger, so descriptions must be precise and non-overlapping.

---

## Part 2: Structured Data — Dataverse Tables (Control Families)

### Table and Column Design

- Up to **10 Dataverse tables** can be added per knowledge source — plan your control family schema accordingly.
- Ensure columns you want the agent to query are included in the **Active view** and the **Quick Find view** (required for searchability).
- For `Multiline Text` and `File` columns, explicitly mark them **Searchable** in the Quick Find View configuration.

### Synonyms and Glossary (Critical)

- Add **synonyms for every column** that has domain-specific names or numeric values. The AI cannot interpret column semantics without them (e.g., a column named `ctrl_scope_cd` needs a synonym like "control scope" or "applicability").
- Use the **Glossary** to define control family terminology: what "scope," "requirement level," "control family," and "control ID" mean in your domain.
- Without these, the agent misinterprets column names and produces inaccurate lookups.

### Control ID Lookups

- Dataverse knowledge sources **do not expose row GUIDs** directly. For lookup fields that require a GUID reference, add an **Agent Flow** to retrieve the GUID separately before passing it to a Dataverse action.
- For Control ID-based filtering, treat the Control ID as an entity — configure a **custom entity** in Copilot Studio so the agent can extract it from user messages (e.g., "AC-1", "SC-28") reliably.

### Handling Multiple Scopes and Requirements

- If control families have overlapping column sets but different scopes (e.g., FedRAMP vs. NIST vs. internal), use **separate tables per framework** rather than one wide table with scope flags — this keeps Quick Find views clean and prevents cross-scope confusion.
- Add a **scope/framework column synonym** so users can ask "show me AC controls for FedRAMP" and the agent correctly filters.
- For numeric requirement levels or priority columns, always provide a synonym explaining the scale (e.g., "1 = Low, 2 = Medium, 3 = High").

### Query Limits and Performance

- Dataverse knowledge queries return a **maximum of 20 rows** per call. For queries expected to return large result sets, design the agent flow to paginate or prompt the user to narrow scope.
- The **Dataverse MCP server** (public preview as of 2026) enables richer structured querying — evaluate it for complex multi-table control lookups.

---

## Part 3: Scaling to Large Knowledge Bases (1M+ Characters)

### The Core Problem

Native Copilot Studio file ingestion (Dataverse-backed) is designed for moderate-sized corpora. At 1–2M+ characters across many unique-topic documents, retrieval accuracy degrades because:

- You have **zero control over chunk boundaries** — the platform uses undocumented default chunking
- Vector search alone struggles when topics are numerous and semantically close (policy documents covering adjacent control domains look similar to the embedder)
- The 5-source-per-query limit means the orchestrator can miss relevant documents entirely

### The Enterprise Pattern: Azure AI Search as Custom Knowledge Source

Organizations at this scale bypass native file ingestion and connect Copilot Studio to **Azure AI Search** as a custom knowledge source. This unlocks:

| Capability | Native Copilot Studio | Azure AI Search |
|---|---|---|
| Chunk control | None (platform-managed) | Full (size, overlap, layout-aware) |
| Search mode | Vector only | Hybrid (keyword + semantic vector) |
| Index size | Limited by Dataverse | Enterprise-scale |
| Ranking | Default | Semantic re-ranking (BM25 + deep LM) |
| Analytics | Basic usage stats | Full query/retrieval telemetry |

### Chunking Strategy at Scale

- Use **Azure AI Search's Document Layout skill** for docx — it chunks by paragraph/heading structure, not arbitrary token count. This keeps policy sections intact.
- Add **10–15% chunk overlap** so context isn't lost at boundaries between adjacent sections.
- **Chunk size guidance:** 512–1024 tokens per chunk is the common sweet spot; larger chunks improve context but hurt precision, smaller chunks improve precision but lose surrounding context.
- For a 1.5M-character corpus (~375K tokens), expect ~500–750 chunks at 512 tokens — well within Azure AI Search index limits.

### Hybrid Search (Critical for Unique Topics)

- Enable **hybrid search** (lexical BM25 + semantic vector) rather than vector-only. For policy corpora with many unique named topics, keyword matching catches exact control names/IDs that vector search misses or blurs.
- Enable **semantic ranking** on the index: it re-scores the initial BM25/vector results with a deep language model, surfacing the most contextually relevant chunk rather than just the closest vector.
- Result: hybrid + semantic ranking is the single highest-impact configuration change for large, topic-diverse knowledge bases.

### Agentic Retrieval (Multi-Query)

- For complex user questions that span multiple topics, Azure AI Search's **agentic retrieval** pipeline automatically decomposes the query into sub-queries, runs them in parallel, and merges results — significantly improving recall vs. a single vector lookup.
- Configure this when users are likely to ask comparative or cross-policy questions ("how does the AC family differ from SC for cloud workloads?").

### Document Organization Strategy

Even with Azure AI Search, **pre-organization still matters**:

- Group documents by domain/family into separate index fields or use **metadata filters** (e.g., `framework: FedRAMP`, `topic_area: access-control`) so queries can be scoped before ranking.
- Add a `document_title` and `section_heading` metadata field to every chunk — the agent can surface these as citations, and they improve re-ranking signal.
- Maintain a **document registry** (even a simple Dataverse table) with document name, topic area, last-updated date, and chunk count — essential for knowing when to re-index after doc changes.

### Retrieval Quality Monitoring

- Use Copilot Studio's built-in analytics to track **unanswered questions and low-confidence responses** — these identify retrieval gaps, not just LLM gaps.
- Periodically run **eval sets**: a fixed set of known Q&A pairs against your corpus. Re-run after any major doc update to catch regressions from re-chunking.
- Microsoft's Copilot Studio Evaluator tool can automate this evaluation pipeline.

---

## Part 4: Mixed-Mode Agent (Unstructured + Structured Together)

### Routing Strategy

- Use **separate topics** for policy narrative questions (→ docx knowledge) vs. control lookup/filtering questions (→ Dataverse knowledge). Don't route both to a single catch-all topic.
- Configure the AI orchestrator with distinct, non-overlapping **topic descriptions** so it reliably distinguishes "explain policy X" from "list controls for family Y."
- Use **topic input variables** to capture framework name, control family, or policy area early in the conversation and use them to scope subsequent knowledge queries.

### Grounding and Source Attribution

- When answering from both sources in one session, instruct the agent to **attribute answers** ("According to [Policy Doc]..." vs. "In the [ControlFamily] table...") to help users distinguish narrative policy from structured control data.

### Testing

- Test the golden path: a user asking a policy question, then immediately a control lookup. Verify the agent switches knowledge sources cleanly without blending context.
- Test with Control IDs that exist in some frameworks but not others to verify scope filtering.
- Test policy questions that span two split documents to verify chunking doesn't lose cross-file context.

---

## Sources

- [Unstructured data as a knowledge source — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-unstructured-data)
- [Add Dataverse tables as a knowledge source — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-add-dataverse)
- [Knowledge sources summary — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/knowledge-copilot-studio)
- [Follow topic authoring best practices — Microsoft Learn](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/topic-authoring-best-practices)
- [Best practices: Tools vs. Topics + Agent Flows in Copilot Studio — Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5565962/best-practices-using-tools-vs-topics-agent-flows-i)
- [Keep it short and sweet: document length guide for Copilot — Microsoft Support](https://support.microsoft.com/en-us/topic/keep-it-short-and-sweet-a-guide-on-the-length-of-documents-that-you-provide-to-copilot-66de2ffd-deb2-4f0c-8984-098316104389)
- [Copilot Studio knowledge limitations guide — GitHub (Rickcau)](https://github.com/Rickcau/Copilot-Studio/blob/main/Knowledge_Source_Limitations_Solutions/copilot-studio-knowledge-limitations-guide.md)
- [Best practices decision tree for building Copilot Studio agents — GitHub (Azure)](https://github.com/Azure/Copilot-Studio-and-Azure/blob/main/docs/Best-Practices_decision-tree_for_building_copilot_studio_agent.md)
- [Connect to Dataverse Knowledge in Copilot Studio — matthewdevaney.com](https://www.matthewdevaney.com/connect-to-dataverse-knowledge-in-copilot-studio/)
- [Structured Data with Zero User Auth: Dataverse searchQuery in Copilot Studio](https://microsoft.github.io/mcscatblog/posts/dataverse-search-in-copilot-studio-unauthenticated-structured-data/)
- [Adding Dataverse as a Knowledge Source in Copilot Studio — Inogic](https://www.inogic.com/blog/2026/03/adding-dataverse-as-a-knowledge-source-in-microsoft-copilot-studio/)
- [Copilot Studio and data retrieval from Dataverse — Forward Forever](https://forwardforever.com/copilot-studio-and-data-retrieval-from-dataverse/)
- [Announcing new Dataverse capabilities for multi-agent operations — Microsoft Copilot Blog](https://www.microsoft.com/en-us/microsoft-copilot/blog/copilot-studio/announcing-new-microsoft-dataverse-capabilities-for-multi-agent-operations/)
