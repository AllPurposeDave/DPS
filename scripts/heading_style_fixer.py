"""
Step 3: Heading Style Fixer
=============================

RUN THIS AFTER cross_reference_extractor.py, before section_splitter.py.

Converts fake headings (bold text with no Word Heading style) to real
Word Heading 1/2/3 styles. The splitter (Step 4) depends on correct
Heading styles to know where to cut.

Usage (unified pipeline):
    python run_pipeline.py --step 3

Usage (standalone):
    python scripts/heading_style_fixer.py
    python scripts/heading_style_fixer.py --config dps_config.yaml
    python scripts/heading_style_fixer.py ./input ./output

Output:
    *_fixed.docx files — one per input doc, with corrected heading styles
    heading_changes.csv — change log of every style modification

FAILURE POINT: After this script runs, ALWAYS review heading_changes.csv.
False positives (bold labels, bold table headers, bold "NOTE:" text) will
be incorrectly promoted to heading styles.
"""
# pip install python-docx

import csv
import os
import re
import traceback

from docx import Document

from shared_utils import (
    ensure_output_dir,
    get_input_dir,
    get_output_dir,
    is_heading_style,
    is_paragraph_bold,
    iter_docx_files,
    load_config,
    setup_argparse,
)


def build_heading_patterns(config: dict) -> tuple:
    """Build heading level regex patterns from config."""
    headings_cfg = config.get("headings", {})
    h1 = re.compile(headings_cfg.get("heading1_pattern", r"^(?:\d+\.0\s+|[IVXLC]+\.\s+)"))
    h2 = re.compile(headings_cfg.get("heading2_pattern", r"^(?:\d+\.\d+\s+|[A-Z]\.\s+)"))
    h3 = re.compile(headings_cfg.get("heading3_pattern", r"^\d+\.\d+\.\d+\s+"))
    return h1, h2, h3


def build_custom_style_map(config: dict) -> dict:
    """Build custom style map from config, falling back to defaults."""
    headings_cfg = config.get("headings", {})
    config_map = headings_cfg.get("custom_style_map", {})
    if config_map:
        # Normalize keys to lowercase
        return {k.strip().lower(): v for k, v in config_map.items()}

    # Fallback defaults
    return {
        "policy heading 1": "Heading 1",
        "policy heading 2": "Heading 2",
        "policy heading 3": "Heading 3",
        "policyheading1": "Heading 1",
        "policyheading2": "Heading 2",
        "policyheading3": "Heading 3",
        "doc heading 1": "Heading 1",
        "doc heading 2": "Heading 2",
        "doc heading 3": "Heading 3",
        "heading1": "Heading 1",
        "heading2": "Heading 2",
        "heading3": "Heading 3",
        "title heading": "Heading 1",
        "section heading": "Heading 1",
        "subsection heading": "Heading 2",
    }


def determine_heading_level(text: str, re_h1, re_h2, re_h3, default_level: int = 2) -> str:
    """
    Determine the appropriate heading style based on numbering patterns.
    Returns 'Heading 1', 'Heading 2', 'Heading 3', or default.

    CHECK ORDER IS IMPORTANT:
    RE_HEADING3 must be checked before RE_HEADING2 because "1.1.1 " also matches
    the RE_HEADING2 pattern.
    """
    stripped = text.strip()
    if re_h3.match(stripped):
        return "Heading 3"
    if re_h1.match(stripped):
        return "Heading 1"
    if re_h2.match(stripped):
        return "Heading 2"
    return f"Heading {default_level}"


def is_fake_heading(paragraph, max_chars: int = 120) -> bool:
    """
    Detect fake headings: paragraphs that look like headings but don't
    have a Word Heading style applied.

    A paragraph is a fake heading if ALL of these are true:
    - Bold formatting (paragraph-level or all runs bold)
    - Short (under max_chars characters)
    - Does NOT end with a period
    - Does NOT already have a Heading style
    """
    text = paragraph.text.strip()
    if not text:
        return False
    if is_heading_style(paragraph.style):
        return False
    if len(text) >= max_chars:
        return False
    if text.endswith("."):
        return False
    if not is_paragraph_bold(paragraph):
        return False
    return True


def get_custom_style_mapping(style_name: str, style_map: dict):
    """Check if a style name matches a known custom heading style."""
    if not style_name:
        return None
    normalized = style_name.strip().lower()
    return style_map.get(normalized)


def apply_text_deletions(doc, config: dict) -> list[dict]:
    """
    Delete configured phrases from all paragraph and table cell text.
    Modifies run.text to preserve formatting (bold, font, etc.).
    Returns a list of deletion records for the change log.
    """
    deletion_cfg = config.get("text_deletions", {})
    if not deletion_cfg.get("enabled", False):
        return []

    phrases = deletion_cfg.get("phrases", [])
    if not phrases:
        return []

    case_sensitive = deletion_cfg.get("case_sensitive", True)
    deletions = []

    def delete_from_run(run, phrase, location):
        """Delete a phrase from a run's text. Returns True if changed."""
        original = run.text
        if not original:
            return False
        if case_sensitive:
            if phrase not in original:
                return False
            new_text = original.replace(phrase, "")
        else:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            if not pattern.search(original):
                return False
            new_text = pattern.sub("", original)
        # Collapse multiple spaces
        new_text = re.sub(r'  +', ' ', new_text).strip()
        deletions.append({
            "location": location,
            "phrase_deleted": phrase,
            "original_preview": original[:80],
        })
        run.text = new_text
        return True

    # Process paragraphs
    for idx, para in enumerate(doc.paragraphs):
        for run in para.runs:
            for phrase in phrases:
                delete_from_run(run, phrase, f"Paragraph {idx}")

    # Process table cells
    for t_idx, table in enumerate(doc.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                for para in cell.paragraphs:
                    for run in para.runs:
                        for phrase in phrases:
                            delete_from_run(run, phrase, f"Table {t_idx}, Row {r_idx}, Cell {c_idx}")

    return deletions


def process_document(filepath: str, output_dir: str, config: dict) -> tuple[list[dict], list[dict]]:
    """
    Process a single .docx file: apply text deletions, fix heading styles, save as _fixed.docx.
    Returns a tuple: (heading_changes, deletion_records).
    """
    headings_cfg = config.get("headings", {})
    max_chars = headings_cfg.get("fake_heading_max_chars_fixer", 120)
    default_level = headings_cfg.get("default_heading_level", 2)
    style_map = build_custom_style_map(config)
    re_h1, re_h2, re_h3 = build_heading_patterns(config)

    doc = Document(filepath)
    filename = os.path.basename(filepath)

    # Apply text deletions FIRST (before heading analysis)
    deletion_records = apply_text_deletions(doc, config)
    base_name = os.path.splitext(filename)[0]
    changes = []

    for idx, para in enumerate(doc.paragraphs):
        original_style = para.style.name if para.style else "None"
        new_style = None

        # Check for custom named styles that should be standard headings
        if not is_heading_style(para.style) and para.style:
            mapped = get_custom_style_mapping(para.style.name, style_map)
            if mapped:
                new_style = mapped

        # Check for fake headings (bold + short + no period + no heading style)
        if new_style is None and is_fake_heading(para, max_chars):
            new_style = determine_heading_level(para.text, re_h1, re_h2, re_h3, default_level)

        # Apply the style change if needed
        if new_style:
            para.style = doc.styles[new_style]
            text_preview = para.text.strip()[:80]
            changes.append({
                "doc_name": filename,
                "paragraph_index": idx,
                "original_style": original_style,
                "new_style": new_style,
                "paragraph_text_preview": text_preview,
            })

    # Save the fixed document
    output_path = os.path.join(output_dir, f"{base_name}_fixed.docx")
    doc.save(output_path)

    return changes, deletion_records


def main():
    parser = setup_argparse("Step 3: Fix heading styles in .docx policy documents")
    args = parser.parse_args()

    config = load_config(args.config)
    input_dir = get_input_dir(config, args.input_dir)
    output_dir = get_output_dir(config, "heading_fixes", args.output_dir)
    ensure_output_dir(output_dir)

    docx_files = iter_docx_files(input_dir, config)
    if not docx_files:
        print(f"No .docx files found in {input_dir}")
        return

    changes_file = config.get("output", {}).get("heading_fixes", {}).get("changes_file", "heading_changes.csv")
    csv_path = os.path.join(output_dir, changes_file)
    fieldnames = [
        "doc_name", "paragraph_index", "original_style",
        "new_style", "paragraph_text_preview",
        "change_type", "phrase_deleted",
    ]

    all_changes = []
    total_deletions = 0
    files_processed = 0
    files_failed = 0

    for filepath in docx_files:
        filename = os.path.basename(filepath)
        try:
            changes, deletion_records = process_document(filepath, output_dir, config)
            # Tag heading changes
            for c in changes:
                c["change_type"] = "heading_fix"
                c["phrase_deleted"] = ""
            # Convert deletion records to CSV rows
            for d in deletion_records:
                all_changes.append({
                    "doc_name": filename,
                    "paragraph_index": d["location"],
                    "original_style": "",
                    "new_style": "[DELETED]",
                    "paragraph_text_preview": d["original_preview"],
                    "change_type": "text_deletion",
                    "phrase_deleted": d["phrase_deleted"],
                })
            all_changes.extend(changes)
            total_deletions += len(deletion_records)
            files_processed += 1
            del_msg = f", {len(deletion_records)} deletion(s)" if deletion_records else ""
            print(f"  Processing {filename}... {len(changes)} heading(s) fixed{del_msg}")
        except Exception as e:
            files_failed += 1
            print(f"  ERROR processing {filename}: {e}")
            traceback.print_exc()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_changes)

    heading_count = sum(1 for c in all_changes if c.get("change_type") == "heading_fix")
    print("\n" + "=" * 60)
    print("STEP 3 — HEADING STYLE FIXER SUMMARY")
    print("=" * 60)
    print(f"Files processed:      {files_processed}")
    print(f"Files failed:         {files_failed}")
    print(f"Total headings fixed: {heading_count}")
    print(f"Total text deletions: {total_deletions}")
    print(f"\nFixed documents written to: {output_dir}")
    print(f"Change log written to: {csv_path}")


if __name__ == "__main__":
    main()
