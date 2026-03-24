"""
Step 2: Cross-Reference Extractor
========================================

RUN THIS FIRST before any other processing script.

Extracts all cross-references from every .docx file BEFORE any structural
changes are made. Must run first while original section numbering is intact.

Cross-references like "See Section 4.3" become unresolvable after heading
fixes or document splits change the structure — so we capture them now.

Usage (unified pipeline):
    python run_pipeline.py --step 2

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
# Patterns are loaded from dps_config.yaml → cross_references.extraction_patterns
# Each config entry has: phrase (lead-in text) and type ("internal" or "external")
#
# Internal patterns match: <phrase> Section <number>
# External patterns match: <phrase> [the] <Document Name ending in keyword>
#
# Fallback defaults are used if the config section is missing.

# Fallback patterns used when config has no extraction_patterns
_DEFAULT_EXTRACTION_PATTERNS = [
    {"phrase": "see",               "type": "internal"},
    {"phrase": "refer to",          "type": "internal"},
    {"phrase": "per",               "type": "internal"},
    {"phrase": "as described in",   "type": "internal"},
    {"phrase": "as defined in",     "type": "internal"},
    {"phrase": "as described in",   "type": "external"},
    {"phrase": "as defined in",     "type": "external"},
    {"phrase": "refer to",          "type": "external"},
    {"phrase": "in accordance with","type": "external"},
]


def build_doc_keyword_alternation(config: dict) -> str:
    """Build the regex alternation group for document name keywords from config."""
    keywords = config.get("cross_references", {}).get("document_name_keywords", [
        "Policy", "Standard", "Plan", "Procedure", "Guide",
        "Guideline", "Program", "Framework", "Charter",
    ])
    return "(?:" + "|".join(re.escape(k) for k in keywords) + ")"


def build_cross_ref_patterns(config: dict) -> list[tuple]:
    """Build cross-reference patterns from config extraction_patterns entries."""
    kw = build_doc_keyword_alternation(config)

    entries = config.get("cross_references", {}).get(
        "extraction_patterns", _DEFAULT_EXTRACTION_PATTERNS
    )

    patterns = []
    for entry in entries:
        phrase = entry["phrase"]
        ref_type = entry["type"]
        # Escape the phrase for regex safety, then allow flexible whitespace
        escaped = re.escape(phrase).replace(r"\ ", r"\s+")

        if ref_type == "internal":
            regex = re.compile(
                escaped + r"\s+[Ss]ection\s+([\d]+(?:\.[\d]+)*)",
                re.IGNORECASE,
            )
        else:  # external
            regex = re.compile(
                escaped + r"\s+(?:the\s+)?([A-Z][A-Za-z\s&-]{4,}" + kw + r")",
            )
        patterns.append((regex, ref_type))

    return patterns


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


def extract_url_records(paragraph, doc_rels, config: dict) -> list[dict]:
    """
    Extract URLs from hyperlinks and bare text in a paragraph.
    Returns records for external URLs, internal bookmark links, and bare text URLs.
    """
    if not config.get("cross_references", {}).get("detect_urls", True):
        return []

    urls = []
    try:
        from docx.oxml.ns import qn

        # Extract URLs from hyperlinks
        for hyperlink in paragraph._element.findall(qn("w:hyperlink")):
            display_text = ""
            for run_elem in hyperlink.findall(qn("w:r")):
                for text_elem in run_elem.findall(qn("w:t")):
                    if text_elem.text:
                        display_text += text_elem.text

            # Check for external hyperlink (r:id attribute)
            r_id = hyperlink.get(qn("r:id"))
            if r_id and r_id in doc_rels:
                target_url = doc_rels[r_id].target_ref
                urls.append({
                    "target_url": target_url,
                    "url_display_text": display_text.strip() if display_text.strip() else "",
                    "url_type": "external",
                })

            # Check for internal bookmark link (w:anchor attribute)
            anchor = hyperlink.get(qn("w:anchor"))
            if anchor:
                urls.append({
                    "target_url": anchor,
                    "url_display_text": display_text.strip() if display_text.strip() else "",
                    "url_type": "internal",
                })

        # Extract bare text URLs from paragraph
        bare_url_pattern = re.compile(r"https?://[^\s<>\"]+|www\.[^\s<>\"]+")
        for match in bare_url_pattern.finditer(paragraph.text):
            urls.append({
                "target_url": match.group(0),
                "url_display_text": "",
                "url_type": "bare_text",
            })

    except Exception:
        pass

    return urls


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
                    "target_url": "",
                    "url_display_text": "",
                    "url_type": "",
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
                "target_url": "",
                "url_display_text": "",
                "url_type": "",
            })

        # Check for URLs
        url_records = extract_url_records(para, doc.part.rels, config)
        for url_record in url_records:
            records.append({
                "source_doc": filename,
                "source_section": find_parent_heading(paragraphs, idx),
                "source_paragraph_index": idx,
                "matched_text": "",
                "reference_type": "",
                "target_reference": "",
                "resolution_status": "",
                "target_url": url_record["target_url"],
                "url_display_text": url_record["url_display_text"],
                "url_type": url_record["url_type"],
            })

    return records


def main():
    parser = setup_argparse("Step 2: Extract cross-references from .docx policy documents")
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
        "target_url", "url_display_text", "url_type",
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
    print("STEP 2 — CROSS-REFERENCE EXTRACTION SUMMARY")
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
