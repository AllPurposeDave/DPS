# docx_diff — .docx difference checker

Compare every `.docx` in `Diff 1/` against its counterpart in `Diff 2/` and produce a multi-sheet Excel report covering metadata, text, tracked changes, and comments.

## What it does

- **Pairs files** across the two folders by exact or normalized filename (handles dashes, underscores, extra spaces, and trailing suffixes like `v2`, `(2)`, `final`, `draft`, `copy`, `latest`).
- **Harvests metadata** from `docProps/core.xml`, `docProps/app.xml`, `docProps/custom.xml`, plus filesystem stat, archive SHA-256, normalized `document.xml` SHA-256, and unique `w:rsid` save-session IDs.
- **Diffs text** paragraph-by-paragraph across body, headers, footers, footnotes, and endnotes — with inline word-level highlights rendered as colored rich text inside a single Excel cell (red strikethrough for deletions, green bold for insertions).
- **Compares tracked changes** (`w:ins`, `w:del`, `w:moveFrom`, `w:moveTo`) and flags which revisions are unique to each side.
- **Compares comments** including replies and threading from `word/comments.xml` and its extended variants.
- **Surfaces every "which is latest" signal side-by-side** — `core.modified`, `core.revision`, `app.TotalTime`, rsid count, last tracked-change date, last comment date, filesystem mtime, archive hash, normalized content hash — and does **not** pick a winner. The reviewer reads the agreement/disagreement pattern and judges.

## Usage

```
python "Misc/docx_diff/docx_diff.py"
```

Runs with the defaults: compares the sibling `Diff 1/` and `Diff 2/` folders and writes `docx_diff_report_<timestamp>.xlsx` next to the script.

Flags:

```
--folder1 PATH           Override Diff 1 folder
--folder2 PATH           Override Diff 2 folder
--output  PATH           Override output xlsx path
--fuzzy-threshold FLOAT  Minimum SequenceMatcher ratio for fuzzy pairing (default 0.9)
--verbose                Print per-file progress
```

## Workbook layout

| Sheet | Contents |
|---|---|
| Summary | One row per file pair: match kind, identical?, counts per category, signal tally. |
| Signals | One row per `(file, signal)`: Diff 1 value, Diff 2 value, which side the signal points to. |
| Metadata | One row per `(file, field)` across core / app / custom / fs / hash / rsid categories. |
| Text Diff | One row per changed paragraph with an inline colored word diff cell. |
| Tracked Changes | One row per tracked revision, grouped by which side has it. |
| Comments | One row per comment / reply, grouped by which side has it. |
| Orphans | Files present in only one folder. |

## Dependencies

Covered by the repo's existing [requirements.txt](../../requirements.txt): `python-docx`, `openpyxl`, `lxml`. Plus stdlib `zipfile`, `hashlib`, `difflib`.
