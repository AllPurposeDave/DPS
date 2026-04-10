# Control Mapping Template

A reusable template for mapping any two security control frameworks against each other using AI or LLM in VS Code. No API key required — works entirely through interactive AI or LLM sessions.

This produces a **many-to-many mapping**: each source control can match multiple target controls, and each target control can be matched by multiple source controls. The output captures every relationship with a confidence level, then computes gap analysis from the combined results.

---

## Quick Start

```
1. Clone/copy this template folder for your project
2. Place your Excel file in input/
3. Edit config.yaml to match your Excel layout
4. Run:  python scripts/setup.py
5. Process each batch with AI or LLM
6. Run:  python scripts/merge.py
```

---

## Prerequisites

- Python 3.8+
- [Continue Extension](https://www.continue.dev/) for VS Code (configured with Claude Sonnet 4.5)
- An Excel file with two worksheets (one per framework)

```bash
pip install -r requirements.txt
```

> **Continue Extension note:** Continue does not automatically read files — all context must be manually added to each chat using `@FILE-Name` syntax. See Step 5 for the exact prompt pattern.

---

## Step-by-Step Guide

### Step 1: Prepare Your Input

Place a single `.xlsx` file in the `input/` folder. The file must have **two worksheets**, one for each control framework.

Each worksheet needs at minimum:
| Column | Purpose | Example |
|--------|---------|---------|
| Control ID | Unique identifier | AC-1, SSCF-IAM-01 |
| Description | Control requirement text | "The organization manages..." |

Additional columns (Title, Domain, Details, Guidelines) are optional but improve mapping accuracy.

### Step 2: Configure

Edit `config.yaml`. Every field has inline comments explaining what it does.

**Key settings to update:**

| Setting | What to change | Example |
|---------|---------------|---------|
| `project_name` | Your project label | `"NIST 800-53 to ISO 27001"` |
| `input_file` | Path to your Excel | `"input/controls.xlsx"` |
| `source.name` | Source framework name | `"NIST 800-53"` |
| `source.sheet_name` | Excel tab name (exact, case-sensitive) | `"NIST"` |
| `source.columns.id` | Column index for Control ID (0-based) | `0` (column A) |
| `source.columns.description` | Column index for description | `3` (column D) |
| `target.name` | Target framework name | `"ISO 27001"` |
| `target.sheet_name` | Excel tab name | `"ISO"` |
| `target.columns.id` | Column index for Control ID | `0` |
| `target.columns.description` | Column index for description | `1` |

**Column indices are 0-based:**
```
Column A = 0    Column D = 3
Column B = 1    Column E = 4
Column C = 2    Column F = 5
```

**Adding supplemental columns** (optional, improves context for mapping):
```yaml
supplemental:
  - index: 0
    label: "Domain"      # Used for grouping in output
  - index: 1
    label: "Title"       # Displayed inline in prompts
  - index: 4
    label: "Details"     # Extra context for mapping
```

### Step 3: Choose Your Mode

#### Standard Mode (target < 200 controls)
Leave `target.chunking.enabled: false`. Each batch prompt includes the full target catalog. Simple and effective for smaller target frameworks.

**Batch count:** `ceil(source_controls / batch_size)`
Example: 36 source controls ÷ 8 per batch = 5 batch files

#### Chunked Mode (target 200+ controls)
Set `target.chunking.enabled: true`. Target controls are split by family prefix (e.g., AC-, CM-, SI-) and each source batch is mapped against each target group separately.

**When to use chunked mode:**
- Target has 200+ controls
- Target uses prefixed IDs (AC-1, CM-2, SI-3)
- Target language is dense with overlapping requirements (typical of NIST)

**Batch count:** `source_batches × target_chunks`
Example: 5 source batches × 8 target groups = 40 batch files

**Why chunked mode is more accurate:**
- Claude focuses on fewer, related controls per prompt
- Dense control language doesn't overwhelm the context window
- Controls in the middle of long reference lists don't get skipped
- merge.py automatically combines and deduplicates matches across chunks

**Chunking config:**
```yaml
target:
  chunking:
    enabled: true
    strategy: "prefix"        # Split by ID prefix
    separator: "-"            # AC-1 → family "AC"
    max_controls_per_chunk: 60  # Combine small families together
```

`max_controls_per_chunk` prevents tiny families (e.g., PM with 2 controls) from becoming their own batch — they get combined with adjacent families until the limit is reached.

### Step 4: Run Setup

```bash
python scripts/setup.py
```

This generates:
- `reference/source_controls.md` — readable reference of all source controls
- `reference/target_controls.md` — readable reference of all target controls
- `batches/*.md` — self-contained prompt files, one per batch

Review the output to verify correct control counts and batch breakdown.

### Step 5: Process Batches

For each `.md` file in `batches/`, open a new Continue chat and use this prompt pattern:

> **`@CLAUDE.md @batches/<filename>.md` Follow the instructions in the batch file.**

The `@` mentions inject the file contents directly into the model's context. Both files must be included:
- `@CLAUDE.md` — provides the output format rules and confidence level definitions
- `@batches/<filename>.md` — provides the source controls, target reference, and save instructions

The model will:
1. Read the injected batch file (contains source controls and target reference)
2. Analyze each source control against the target controls
3. Output a JSON mapping

**Save the JSON output** to `results/<batch_name>_result.json` (the batch file tells you the exact filename). Press **Ctrl+Enter** to confirm the file write in Continue.

**Tips:**
- Process batches in any order — use a fresh Continue chat per batch
- Work across multiple sessions — results accumulate in `results/`
- If a batch seems wrong, delete its result file and reprocess
- In chunked mode, the same source controls appear in multiple batches (one per target group) — this is expected
- Do not reuse a chat session across batches — stale context degrades accuracy

### Step 6: Merge Results

```bash
python scripts/merge.py
```

This:
1. Loads all `results/*.json` files
2. In chunked mode: merges matches across target families, deduplicates by target ID (keeps highest confidence)
3. Validates completeness (reports missing source controls)
4. Computes gap analysis
5. Writes `output/<project_name>_GapAnalysis.xlsx`

**Output sheets:**

| Sheet | Contents |
|-------|----------|
| Source Unique | Source controls with no high/medium target matches (gaps) |
| Target Unique | Target controls not matched by any source control |
| Full Mapping | Every source control with matched target IDs, confidence, rationale, match count |

Also saves `output/mapping_cache.json` — the combined, normalized mapping data.

**You can run merge at any time** — it will report which source controls are still missing and produce a partial output. Re-run after processing more batches.

---

## Mapping Cardinality

The output captures one-to-many and many-to-one relationships between source and target controls. Completeness depends on the model's semantic accuracy — this is best-effort coverage, not exhaustive enumeration.

| Relationship | How it works |
|--------------|--------------|
| **1-to-many** | One source control matches several target controls (common when a specific requirement maps to multiple areas of the target framework) |
| **Many-to-1** | Multiple source controls match the same target control (common with broad "umbrella" target controls) |
| **1-to-0** | A source control with no high/medium target matches — flagged as a gap on the "Source Unique" sheet |
| **0-to-1** | A target control not matched by any source control — flagged on the "Target Unique" sheet |

Every match includes a confidence level (`high`, `medium`, `low`) and a rationale. The gap analysis uses only `high` and `medium` matches to determine coverage — `low` matches are recorded but don't count as "covered."

---

## Accuracy Guidance

| Scenario | Recommended Settings |
|----------|---------------------|
| Small source, small target (<100 each) | Standard mode, batch_size 8-10 |
| Small source, large target (200+) | Chunked mode, batch_size 5-8 |
| Large source, large target | Chunked mode, batch_size 5, group_by domain |
| NIST-based target (dense language) | Chunked mode, max_controls_per_chunk 40-60 |

**Factors that affect accuracy:**
- **Batch size** — fewer source controls per prompt = more attention per control
- **Target chunking** — splitting large catalogs dramatically reduces missed matches
- **Supplemental columns** — Domain, Title, and Details give Claude more context to differentiate similar controls
- **Control description quality** — vague descriptions produce vague matches

---

## File Structure

```
Control-Mapping-Template/
├── config.yaml              ← Edit this first
├── README.md                ← You are here
├── CLAUDE.md                ← Instructions for AI or LLM sessions
├── requirements.txt         ← Python dependencies
├── input/                   ← Place your Excel file here
│   └── controls.xlsx
├── scripts/
│   ├── setup.py             ← Step 4: generates reference/ and batches/
│   └── merge.py             ← Step 6: combines results/ into output/
├── reference/               ← Generated: human-readable control lists
│   ├── source_controls.md
│   └── target_controls.md
├── batches/                 ← Generated: self-contained prompt files
│   └── *.md
├── results/                 ← Save Claude's JSON output here
│   └── *_result.json
└── output/                  ← Final gap analysis
    ├── *_GapAnalysis.xlsx
    └── mapping_cache.json
```

---

## Example Configurations

### SSCF (36 controls) → CCM (207 controls) — Chunked Mode
```yaml
project_name: "SSCF to CCM Mapping"
source:
  name: "SSCF"
  sheet_name: "SSCF"
  columns:
    id: 2
    description: 3
    supplemental:
      - index: 0
        label: "Domain"
      - index: 1
        label: "Title"
      - index: 4
        label: "Details"
      - index: 5
        label: "Guidelines"
target:
  name: "CCM"
  sheet_name: "CCM"
  columns:
    id: 2
    description: 3
    supplemental:
      - index: 0
        label: "Domain"
      - index: 1
        label: "Title"
  chunking:
    enabled: true
    strategy: "prefix"
    separator: "-"
    max_controls_per_chunk: 50
batching:
  group_by: 0
  batch_size: 8
```
Result: 48 batch files (8 source batches × 6 target chunks, grouped by SSCF domain)

### Custom Framework → NIST 800-53 (400+ controls) — Chunked Mode
```yaml
project_name: "Custom to NIST 800-53"
source:
  name: "Custom Framework"
  sheet_name: "Custom"
  columns:
    id: 0
    description: 1
    supplemental:
      - index: 2
        label: "Domain"
target:
  name: "NIST 800-53"
  sheet_name: "NIST"
  columns:
    id: 0
    description: 1
    supplemental:
      - index: 2
        label: "Title"
  chunking:
    enabled: true
    strategy: "prefix"
    separator: "-"
    max_controls_per_chunk: 50
batching:
  group_by: 2
  batch_size: 5
```
Result: ~40-60 batch files (source batches × NIST family groups)
