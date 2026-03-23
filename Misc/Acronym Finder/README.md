# Acronym Finder Profiling Script

## What It Does

Scans all `.docx` files in a folder and finds every acronym candidate. Outputs a formatted Excel report with 5 sheets:

| Sheet | What's On It |
|---|---|
| **Global Summary** | Every acronym found, total count, which docs it appears in, any detected definition |
| **Per Document** | Same data broken out per file so you can see which docs are acronym-heavy |
| **Undefined Acronyms** | Acronyms where the script found NO parenthetical definition anywhere. These are your risk items for Copilot retrieval (chunks with unexpanded acronyms = bad RAG answers) |
| **Cross-Reference Matrix** | Acronym vs Document grid. Quick visual of which acronyms span which policies |
| **Config Used** | Snapshot of the settings you ran with, so the output is self-documenting |

Yellow-highlighted cells = acronyms with no definition found. Pink cells = high-frequency acronyms (20+ occurrences).

## Why This Matters for Your Copilot KB

Undefined acronyms in your policy docs are a retrieval problem. When the chunker splits a paragraph that says "MFA is required per AC-2.1" and neither MFA nor AC-2.1 is expanded anywhere in that chunk, the model has to guess. In GCC with GPT-4o, that guess is wrong more often than you'd like. This script tells you exactly where the gaps are so you can fix them before restructuring.

## Setup

### 1. Install dependencies

```bash
pip install python-docx openpyxl pyyaml
```

### 2. Put your files in place

```
your_project_folder/
  acronym_finder.py        <-- the script
  acronym_config.yaml      <-- the config
  policy_docs/             <-- put your .docx files here
    access_control.docx
    incident_response.docx
    ...
```

Or change `input_folder` in the config to point wherever your docs live.

### 3. Edit the config (optional but recommended)

Open `acronym_config.yaml` in any text editor. The main things you might want to change:

- **`input_folder`**: Path to your .docx files. Default is `./policy_docs`
- **`ignore_list`**: Add any uppercase words that aren't acronyms but keep showing up. The default list covers common English words, Roman numerals, and doc artifacts. You WILL need to add some after your first run.
- **`min_global_occurrences`**: Set to 2 or 3 if you want to filter out one-off hits. Default is 1 (show everything).

**Don't touch** the `patterns` section unless you know regex and have a specific false positive pattern to kill.

### 4. Run it

```bash
python acronym_finder.py
```

Or with a custom config path:

```bash
python acronym_finder.py /path/to/my_config.yaml
```

### 5. Open the output

Default output: `./acronym_audit.xlsx`

## What To Do With The Results

1. **First run**: Look at the Global Summary. Sort by "Total Occurrences" descending. The top 20-30 acronyms are your highest-impact targets.

2. **Check the Undefined Acronyms sheet**. Every acronym on this sheet needs one of two things:
   - A parenthetical expansion added to the doc where it first appears in each section (so chunks are self-contained)
   - Addition to the ignore list if it's a false positive

3. **Check the Cross-Reference Matrix**. Acronyms that appear in 10+ docs but have no definition are your worst offenders. These will cause retrieval confusion across your entire corpus.

4. **Iterate**: Add false positives to the ignore list in the config, re-run. Two passes usually gets you a clean report.

5. **Feed into Notebook 2**: When you restructure docs, use the Undefined Acronyms sheet as a checklist. Every section should expand its acronyms on first use within that section (not just first use in the document) because any section could become an isolated chunk.

## Troubleshooting

| Problem | Fix |
|---|---|
| "No .docx files found" | Check `input_folder` path in config. Use forward slashes even on Windows. |
| Way too many results | Increase `min_global_occurrences` to 2 or 3. Add common false positives to ignore list. |
| Missing acronyms you expected | Check if they're on the ignore list. Check `min_length` (default 2). |
| Script crashes on a specific file | That file is probably password-protected or corrupted. The script logs the error and continues with other files. |
| Slow on 80 files | Normal. Expect 1-3 minutes depending on file sizes. Tables and textboxes add scanning time. |
