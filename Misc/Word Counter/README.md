# Word Counter

Scans a folder of `.docx` files and produces a CSV report with the word count for each document and a grand total.

---

## Prerequisites

**Python 3.10 or later** is required.

Install the dependency:

```bash
pip install python-docx
```

---

## Usage

```bash
python word_counter.py <input_dir> [output_csv]
```

| Argument | Required | Description |
|----------|----------|-------------|
| `input_dir` | Yes | Directory containing `.docx` files |
| `output_csv` | No | Path for the output CSV (default: `word_counts.csv` inside `input_dir`) |

### Examples

```bash
# Output CSV defaults to ./docs/word_counts.csv
python word_counter.py ./docs

# Specify a custom output path
python word_counter.py ./docs ./reports/word_counts.csv
```

---

## Output

### Terminal

```
Found 3 .docx file(s) in './docs'.

  Information Security Policy.docx........................    4,521 words
  Acceptable Use Policy.docx.............................    2,108 words
  Data Retention Standard.docx...........................    1,743 words

  TOTAL..................................................    8,372 words

CSV written to: ./docs/word_counts.csv
```

### CSV — `word_counts.csv`

| filename | word_count |
|----------|-----------|
| Acceptable Use Policy.docx | 2108 |
| Data Retention Standard.docx | 1743 |
| Information Security Policy.docx | 4521 |
| TOTAL | 8372 |

---

## What Gets Counted

- All paragraph text (body, headers, footers-in-body)
- All table cell text
- Word temp files (`~$*.docx`) are automatically skipped
- Sub-folders are **not** scanned — only top-level `.docx` files

---

## Failure Points

| Issue | Cause | Fix |
|-------|-------|-----|
| `No .docx files found` | Wrong directory path or no `.docx` files present | Check the path |
| `ERROR processing <file>` | Corrupted or password-protected `.docx` | Open in Word, re-save, and retry |
| `ModuleNotFoundError: No module named 'docx'` | `python-docx` not installed | Run `pip install python-docx` |
| `TypeError: unsupported operand type(s) for \|` | Python < 3.10 | Upgrade Python |
