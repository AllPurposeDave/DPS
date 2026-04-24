# Docx_Split

A standalone utility that splits large Microsoft Word documents into smaller
files sized for downstream ingestion pipelines (RAG, search indexing, chunked
review). Each output file is annotated with its published URL and respects
heading-level boundaries so that semantic sections remain intact. The tool is
a single Python script with no dependency on any enclosing repository and may
be copied into another project unchanged.

---

## Behaviour

For every `.docx` in the input directory the script will:

1. Match the filename stem (without the `.docx` extension) against the
   `Document_Name` column of `input/Doc_URL.xlsx`.
2. Remove every section listed in that row's `Delete_Headings` column,
   including all of its subsections.
3. Pack the remaining content greedily into output files, each at or below
   the configured character limit. Splits occur only at Heading 1, 2, or 3
   boundaries, so sections are never broken mid-body.
4. Write a `Published URL:` paragraph at the top of every output. Optionally,
   repeat the URL in the page header so that it appears on every rendered
   page.
5. Name each output `<source_stem> - <first_heading_in_chunk>.docx`.

---

## Installation

```bash
pip install -r requirements.txt
```

Required packages: `python-docx`, `openpyxl`, `PyYAML`. No system binaries are
required.

---

## Running the script

```bash
python split_docs.py
```

Output files are written to `output/`. A summary reporting per-file chunk
counts and any warnings is printed at completion.

An alternate configuration file may be supplied via `--config <path>`.

---

## Directory layout

```
Docx_Split/
├── split_docs.py         the splitter script
├── config.yaml           runtime configuration
├── requirements.txt
├── README.md             this file
├── input/
│   ├── Doc_URL.xlsx      URL and deletion mapping
│   └── *.docx            source documents
└── output/               generated split files
```

---

## Populating `Doc_URL.xlsx`

The workbook must contain a sheet named `URL Mapping` with three columns:

| Document_Name | URL | Delete_Headings |
|---|---|---|
| Acceptable_Use_Policy_POL-AU-2026-006 | https://contoso.sharepoint.com/... | `Appendix A, Appendix B, Revision History` |
| Data_Classification_POL-DC-2026-003 | https://contoso.sharepoint.com/... | *(blank if no deletions are required)* |

Rules:

- **`Document_Name`** must match the source filename stem exactly — no
  `.docx` extension, underscores preserved. Matching is case-insensitive.
- **`URL`** is the value written into every chunk produced from that
  document.
- **`Delete_Headings`** is optional. Multiple headings may be comma-separated.
  Matching is case-insensitive and exact on the heading text: `Appendix A`
  matches a heading whose text is `appendix a` but not `Appendix A.1`.
  Removing a heading also removes all of its subsections.

Documents not listed in the workbook are still processed. Such outputs have
no URL preamble and no sections are deleted.

---

## Configuration (`config.yaml`)

All settings live in `config.yaml`. Paths are resolved relative to the config
file's directory; absolute paths are also accepted.

| Key | Default | Description |
|---|---|---|
| `input_dir` | `input` | Directory scanned for `*.docx` files. |
| `output_dir` | `output` | Destination for split output files. |
| `url_xlsx` | `input/Doc_URL.xlsx` | Path to the URL and deletion mapping workbook. |
| `url_xlsx_sheet` | `URL Mapping` | Worksheet name within the workbook. |
| `doc_name_column` | `Document_Name` | Column containing the document stem. |
| `url_column` | `URL` | Column containing the published URL. |
| `delete_headings_column` | `Delete_Headings` | Column containing comma-separated headings to remove. |
| `max_char_count` | `36000` | Maximum character count per output file. |
| `heading_levels` | `[1, 2, 3]` | Heading levels eligible as split boundaries. |
| `url_preamble_enabled` | `true` | Whether to write `Published URL: <url>` at the top of each output. |
| `url_preamble_label` | `"Published URL:"` | Label printed before the URL. |
| `url_repeat_in_page_header` | `false` | When true, also writes the URL into the document page header. Intended for RAG pipelines that chunk per page. |
| `flatten_2_col_table` | `false` | When true, two-column tables without merged cells are replaced by a heading and one `col1: col2` paragraph per row. See "Table flattening" below. |
| `flatten_2_col_separator` | `": "` | Separator placed between the two columns. |
| `flatten_2_col_heading_level` | `2` | Heading level of the paragraph inserted above flattened rows. |
| `flatten_2_col_heading_default` | `"Definitions"` | Heading used when the first row cannot be identified as a header. |
| `filename_suffix_max_len` | `50` | Maximum length of the heading suffix used in output filenames. |

---

## Table flattening

Retrieval-augmented generation pipelines typically index Word tables poorly.
When enabled, two-column tables are rewritten as prose.

With `flatten_2_col_table: true`:

| Term | Definition |
|---|---|
| RAG | Retrieval-Augmented Generation |
| SLA | Service Level Agreement |

becomes, in the output file:

```
Term and Definition                 ← Heading 2 (configurable)
RAG: Retrieval-Augmented Generation
SLA: Service Level Agreement
```

Flattening rules:

- Only tables with exactly two columns are eligible. Tables with three or
  more columns are left unchanged.
- Tables containing merged cells (`vMerge` vertical or `gridSpan` horizontal)
  are not flattened; they are preserved as-is and their count is reported in
  the run summary so that they can be reviewed manually.
- The heading text is taken from the first row when that row is recognised as
  a header — either via the Word "Header Row" attribute or via a heuristic
  (both cells short with at least one bold run). Otherwise the configured
  default is used and every row is emitted as data.
- The inserted heading is a genuine Heading 2 paragraph and is therefore
  eligible as a split boundary. A flattened glossary can start its own chunk.

---

## Troubleshooting

**Word reports "unreadable content" when opening an output file.**
The source document may be corrupt, or it may have been saved as `.doc` and
renamed. Open the source in Word and save it as `.docx`.

**An output file exceeds `max_char_count`.**
A single section between two eligible headings is larger than the configured
cap. The section is emitted as-is and a warning is logged. To reduce output
size, either add level 4 to `heading_levels` or split the section inside the
source document.

**Headings are not detected.**
Only Word's built-in `Heading 1`, `Heading 2`, and `Heading 3` paragraph
styles are recognised. Custom styles are ignored. Open the source document,
select a heading paragraph, and confirm that the style dropdown reads
`Heading 1` (etc.).

**An entry in the run summary reports `(no URL)`.**
The filename stem does not match any row in `Doc_URL.xlsx`. Verify the
`Document_Name` column for spelling and underscore placement. Matching is
case-insensitive.

**A `Delete_Headings` entry does not remove the section.**
Matching is exact on the normalised heading text (case-insensitive; leading
and trailing whitespace stripped; internal whitespace collapsed). If the
heading reads `Appendix A - Control Mappings`, the full string must appear
in the spreadsheet — not just `Appendix A`.

---

## Sample output

Source: `Acceptable_Use_Policy.docx` (80,000 characters, 12 top-level
sections) with `max_char_count: 36000`:

```
output/
├── Acceptable_Use_Policy - Purpose.docx            (28,400 chars)
├── Acceptable_Use_Policy - Acceptable Use.docx     (34,900 chars)
└── Acceptable_Use_Policy - Enforcement.docx        (11,300 chars)
```

The first paragraph of each output reads:
`Published URL: https://contoso.sharepoint.com/...`
