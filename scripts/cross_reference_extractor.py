"""
Step 1 of 5: Cross-Reference Extractor
========================================

RUN THIS FIRST before any other processing script.

Extracts all cross-references from every .docx file BEFORE any structural
changes are made. Must run first while original section numbering is intact.

Cross-references like "See Section 4.3" become unresolvable after heading
fixes or document splits change the structure — so we capture them now.

Usage (unified pipeline):
    python run_pipeline.py --step 1

Usage (standalone):
    python scripts/cross_reference_extractor.py
    python scripts/cross_reference_extractor.py --config dps_config.yaml
    python scripts/cross_reference_extractor.py ./input ./output

Output:
    cross_references.csv — one row per cross-reference found

FAILURE POINT: If you run this AFTER heading_style_fixer.py, the source_section
column will reflect the new heading structure, not the original one. Re-run
on the original files if you need accurate section attribution.

FAILURE POINT: This script is read-only — it does NOT modify any .docx files.
"""
# pip install python-docx

import csv
import os
import re
import traceback

from docx import Document

from shared_utils import (
    ensure_output_dir,
    find_parent_heading,
    get_input_dir,
    get_output_dir,
    iter_docx_files,
    load_config,
    setup_argparse,
)

# ---------------------------------------------------------------------------
# Cross-reference regex patterns
# ---------------------------------------------------------------------------
# Each tuple: (compiled_regex, reference_type)
# reference_type is "internal" for section numbers, "external" for policy/doc names
#
# HOW TO ADD A NEW PATTERN:
#   1. Add a new tuple at the end of the list
#   2. Use re.IGNORECASE if your phrase can appear in any capitalisation
#   3. The first capture group ( ) must contain the target reference
#
# NOTE: External reference patterns use document_name_keywords from config
# if available. The default list is built from CROSS_REF_PATTERNS below.

def build_doc_keyword_alternation(config: dict) -> str:
    """Build the regex alternation group for document name keywords from config."""
    keywords = config.get("cross_references", {}).get("document_name_keywords", [
        "Policy", "Standard", "Plan", "Procedure", "Guide",
        "Guideline", "Program", "Framework", "Charter",
    ])
    return "(?:" + "|".join(re.escape(k) for k in keywords) + ")"


def build_cross_ref_patterns(config: dict) -> list[tuple]:
    """Build cross-reference patterns, using document_name_keywords from config."""
    kw = build_doc_keyword_alternation(config)

    return [
        # "See Section 4.3" and variants
        (re.compile(r"[Ss]ee\s+[Ss]ection\s+([\d]+(?:\.[\d]+)*)", re.IGNORECASE), "internal"),
        # "refer to Section 4.3"
        (re.compile(r"[Rr]efer\s+to\s+[Ss]ection\s+([\d]+(?:\.[\d]+)*)", re.IGNORECASE), "internal"),
        # "per Section 4.3"
        (re.compile(r"[Pp]er\s+[Ss]ection\s+([\d]+(?:\.[\d]+)*)", re.IGNORECASE), "internal"),
        # "as described in Section 4.3"
        (re.compile(r"[Aa]s\s+described\s+in\s+[Ss]ection\s+([\d]+(?:\.[\d]+)*)", re.IGNORECASE), "internal"),
        # "as described in [Policy/Document Name]"
        (re.compile(r"[Aa]s\s+described\s+in\s+(?:the\s+)?([A-Z][A-Za-z\s&-]{4,}" + kw + r")"), "external"),
        # "as defined in Section 4.3"
        (re.compile(r"[Aa]s\s+defined\s+in\s+[Ss]ection\s+([\d]+(?:\.[\d]+)*)", re.IGNORECASE), "internal"),
        # "as defined in [Policy Name]"
        (re.compile(r"[Aa]s\s+defined\s+in\s+(?:the\s+)?([A-Z][A-Za-z\s&-]{4,}" + kw + r")"), "external"),
        # "refer to [document name]"
        (re.compile(r"[Rr]efer\s+to\s+(?:the\s+)?([A-Z][A-Za-z\s&-]{4,}" + kw + r")"), "external"),
        # "in accordance with [Policy Name]"
        (re.compile(r"[Ii]n\s+accordance\s+with\s+(?:the\s+)?([A-Z][A-Za-z\s&-]{4,}" + kw + r")"), "external"),
    ]


def extract_hyperlink_refs(paragraph, doc_rels, config: dict) -> list[dict]:
    """
    Extract cross-references from hyperlinks whose display text contains
    a section number or policy name.
    """
    if not config.get("cross_references", {}).get("detect_hyperlink_crossrefs", True):
        return []

    kw = build_doc_keyword_alternation(config)
    refs = []
    try:
        from docx.oxml.ns import qn

        for hyperlink in paragraph._element.findall(qn("w:hyperlink")):
            display_text = ""
            for run_elem in hyperlink.findall(qn("w:r")):
                for text_elem in run_elem.findall(qn("w:t")):
                    if text_elem.text:
                        display_text += text_elem.text

            if not display_text.strip():
                continue

            section_match = re.search(r"[Ss]ection\s+([\d]+(?:\.[\d]+)*)", display_text)
            policy_match = re.search(r"([A-Z][A-Za-z\s&-]{4,}" + kw + r")", display_text)

            if section_match:
                refs.append({
                    "matched_text": display_text.strip(),
                    "reference_type": "internal",
                    "target_reference": section_match.group(1),
                })
            elif policy_match:
                refs.append({
                    "matched_text": display_text.strip(),
                    "reference_type": "external",
                    "target_reference": policy_match.group(1).strip(),
                })
    except Exception:
        pass
    return refs


def process_document(filepath: str, patterns: list[tuple], config: dict) -> list[dict]:
    """Process a single .docx file and return a list of cross-reference records."""
    doc = Document(filepath)
    filename = os.path.basename(filepath)
    paragraphs = doc.paragraphs
    records = []

    for idx, para in enumerate(paragraphs):
        text = para.text
        if not text.strip():
            continue

        # Check regex patterns
        for pattern, ref_type in patterns:
            for match in pattern.finditer(text):
                target = match.group(1).strip()
                records.append({
                    "source_doc": filename,
                    "source_section": find_parent_heading(paragraphs, idx),
                    "source_paragraph_index": idx,
                    "matched_text": match.group(0).strip(),
                    "reference_type": ref_type,
                    "target_reference": target,
                    "resolution_status": "",
                })

        # Check hyperlinks
        hyperlink_refs = extract_hyperlink_refs(para, doc.part.rels, config)
        for href in hyperlink_refs:
            records.append({
                "source_doc": filename,
                "source_section": find_parent_heading(paragraphs, idx),
                "source_paragraph_index": idx,
                "matched_text": href["matched_text"],
                "reference_type": href["reference_type"],
                "target_reference": href["target_reference"],
                "resolution_status": "",
            })

    return records


def main():
    parser = setup_argparse("Step 1: Extract cross-references from .docx policy documents")
    args = parser.parse_args()

    config = load_config(args.config)
    input_dir = get_input_dir(config, args.input_dir)
    output_dir = get_output_dir(config, "cross_references", args.output_dir)
    ensure_output_dir(output_dir)

    patterns = build_cross_ref_patterns(config)

    docx_files = iter_docx_files(input_dir, config)
    if not docx_files:
        print(f"No .docx files found in {input_dir}")
        return

    output_file = config.get("output", {}).get("cross_references", {}).get("output_file", "cross_references.csv")
    csv_path = os.path.join(output_dir, output_file)
    fieldnames = [
        "source_doc", "source_section", "source_paragraph_index",
        "matched_text", "reference_type", "target_reference", "resolution_status",
    ]

    all_records = []
    files_processed = 0
    files_failed = 0
    doc_summary = {}

    for filepath in docx_files:
        filename = os.path.basename(filepath)
        try:
            records = process_document(filepath, patterns, config)
            all_records.extend(records)
            doc_summary[filename] = len(records)
            files_processed += 1
            print(f"  Processing {filename}... {len(records)} cross-references found")
        except Exception as e:
            files_failed += 1
            print(f"  ERROR processing {filename}: {e}")
            traceback.print_exc()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    print("\n" + "=" * 60)
    print("STEP 1 — CROSS-REFERENCE EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {files_processed}")
    print(f"Files failed:    {files_failed}")
    print(f"Total cross-references found: {len(all_records)}")
    print()
    print("Per-document counts:")
    for doc_name, count in sorted(doc_summary.items()):
        print(f"  {doc_name}: {count}")
    print(f"\nOutput written to: {csv_path}")


if __name__ == "__main__":
    main()
