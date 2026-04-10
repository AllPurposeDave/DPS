# Dataverse Table Schema: dps_controls

Use this reference to create the Dataverse table manually.
The CSV import file (`dps_controls_import.csv`) maps 1:1 to these columns.

## Table: dps_controls

| Column | Display Name | Dataverse Type | Max Length | Required | Notes |
|--------|-------------|---------------|-----------|----------|-------|
| `control_id` | Control ID | Single Line Text | 50 | Yes | Primary lookup key. NIST: "AC-2", Org: "ABCD02.003" |
| `control_name` | Control Name | Single Line Text | 255 | No | e.g. "Account Management" |
| `family` | Family Code | Choice | — | No | NIST family code: AC, AT, AU, CA, CM, CP, IA, IR, MA, MP, PE, PL, PM, PS, PT, RA, SA, SC, SI, SR. Blank for Standard Controls. |
| `family_name` | Family Name | Single Line Text | 100 | No | Full name, e.g. "Access Control" |
| `description` | Description | Multiline Text | 100,000 | No | Control description |
| `supplemental_guidance` | Supplemental Guidance | Multiline Text | 100,000 | No | Additional guidance text |
| `baseline` | Baseline | Single Line Text | 100 | No | e.g. "Low, Moderate, High" |
| `purpose` | Purpose | Multiline Text | 10,000 | No | Document/control purpose |
| `scope` | Scope | Multiline Text | 10,000 | No | Scope of applicability |
| `applicability` | Applicability | Single Line Text | 500 | No | Applicability statement |
| `compliance_date` | Compliance Date | Single Line Text | 50 | No | Target compliance date |
| `published_url` | Published URL | Single Line Text (URL) | 2,000 | No | Reference URL |
| `source` | Source | Choice | — | No | "Control Catalog" or "Standard Controls" |
| `rag_content` | RAG Content | Multiline Text | 100,000 | No | Composite search column for CoPilot Studio |

## Choice Field: Family Code

| Value | Label |
|-------|-------|
| AC | AC |
| AT | AT |
| AU | AU |
| CA | CA |
| CM | CM |
| CP | CP |
| IA | IA |
| IR | IR |
| MA | MA |
| MP | MP |
| PE | PE |
| PL | PL |
| PM | PM |
| PS | PS |
| PT | PT |
| RA | RA |
| SA | SA |
| SC | SC |
| SI | SI |
| SR | SR |

## Choice Field: Source

| Value | Label |
|-------|-------|
| Control Catalog | Control Catalog |
| Standard Controls | Standard Controls |

## CSV-to-Dataverse Column Mapping

The CSV uses short internal names. Map them to Dataverse display names during import:

| CSV Header | Dataverse Display Name |
|------------|----------------------|
| `control_id` | Control ID |
| `control_name` | Control Name |
| `family` | Family Code |
| `family_name` | Family Name |
| `description` | Description |
| `supplemental_guidance` | Supplemental Guidance |
| `baseline` | Baseline |
| `purpose` | Purpose |
| `scope` | Scope |
| `applicability` | Applicability |
| `compliance_date` | Compliance Date |
| `published_url` | Published URL |
| `source` | Source |
| `rag_content` | RAG Content |

> **Note:** Dataverse prepends your solution publisher prefix to logical column
> names (e.g., `cr_control_id` or `new_control_id`). The display names above
> are what you'll see in the UI and what the CSV import wizard maps against.

## Setup Instructions

1. **Create the table** in your Dataverse environment:
   - Go to Power Apps > Tables > New table
   - Name: `dps_controls`, Display name: "DPS Controls"
   - Primary column: `control_id` (rename from default "Name")

2. **Add columns** per the schema above:
   - Single Line Text columns: set max length as noted
   - Multiline Text columns: use "Text Area" format, set max length
   - Choice columns: **create the option sets listed above before importing**
     — unmapped Choice values are silently dropped during import
   - URL column: use "URL" format for `published_url`

3. **Set up an alternate key** on `control_id`:
   - Go to the table > Keys > New key
   - Name: "Control ID Key", Column: `control_id`
   - This enables upsert (update-or-insert) for future re-imports,
     so updated controls overwrite existing rows instead of creating duplicates

4. **Import the CSV**:
   - Go to the table > Import > Import data
   - Select `dps_controls_import.csv`
   - Map CSV columns to Dataverse columns using the mapping table above
   - The CSV uses UTF-8 with BOM encoding for Dataverse compatibility

5. **Configure CoPilot Studio**:
   - Add the `dps_controls` table as a knowledge source
   - Ensure the `rag_content` column is indexed for search
   - The `rag_content` column contains all relevant control information
     in a single text block optimized for natural-language retrieval
