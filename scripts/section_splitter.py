"""
Step 4: Section Splitter
===========================

RUN THIS AFTER heading_style_fixer.py has produced *_fixed.docx files.

Splits each _fixed.docx at Heading 1 boundaries into sub-documents,
each under the character limit (default 36,000). Prepends the document
preamble (content before first H1) to every sub-document.

Usage (unified pipeline):
    python run_pipeline.py --step 4

Usage (standalone):
    python scripts/section_splitter.py
    python scripts/section_splitter.py --config dps_config.yaml
    python scripts/section_splitter.py ./output/3\ -\ heading_fixes/ ./output/4\ -\ split_documents/

Input:
    Reads *_fixed.docx files from Step 3's output directory.

Output:
    Sub-document .docx files named "[OriginalName] - [Heading1Text].docx"
    split_manifest.csv — manifest of all sub-documents created

FAILURE POINT: This script ONLY processes files ending in "_fixed.docx".
If Step 3 was not run, this script will find nothing.

FAILURE POINT: Check split_manifest.csv after running:
  - "Full Document - No Heading 1 found" = heading fixer didn't work for that doc
  - Duplicate sub_doc_filename values = second overwrote the first
  - character_count above limit = needs manual H2 insertion
"""
# pip install python-docx

import csv
import os
import re
import traceback

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

from shared_utils import (
    ensure_output_dir,
    get_output_dir,
    get_heading_level,
    iter_docx_files,
    load_config,
    sanitize_filename,
    setup_argparse,
)


def get_paragraph_text_length(paragraph) -> int:
    return len(paragraph.text)


def compute_section_chars(paragraphs: list) -> int:
    return sum(len(p.text) for p in paragraphs)


def find_heading1_indices(paragraphs) -> list[int]:
    indices = []
    for i, para in enumerate(paragraphs):
        if get_heading_level(para.style) == 1:
            indices.append(i)
    return indices


def find_heading2_indices(paragraphs, start: int, end: int) -> list[int]:
    indices = []
    for i in range(start, end):
        if get_heading_level(paragraphs[i].style) == 2:
            indices.append(i)
    return indices


def copy_paragraph(source_para, target_doc):
    """Copy a paragraph preserving formatting via XML deep copy."""
    from copy import deepcopy
    from docx.oxml.ns import qn

    new_para = target_doc.add_paragraph()
    new_para._element.getparent().remove(new_para._element)
    new_elem = deepcopy(source_para._element)
    target_doc.element.body.append(new_elem)


def copy_table(source_table, target_doc):
    """Copy a table preserving structure via XML deep copy."""
    from copy import deepcopy

    new_elem = deepcopy(source_table._element)
    target_doc.element.body.append(new_elem)


def build_element_sequence(doc):
    """
    Build an ordered sequence of body elements (paragraphs and tables)
    to preserve correct interleaved ordering when splitting.
    Returns list of tuples: (element_type, object, paragraph_index_or_None)
    """
    from docx.oxml.ns import qn

    elements = []
    para_idx = 0
    table_idx = 0
    paragraphs = doc.paragraphs
    tables = doc.tables

    for child in doc.element.body:
        if child.tag == qn("w:p"):
            if para_idx < len(paragraphs):
                elements.append(("paragraph", paragraphs[para_idx], para_idx))
                para_idx += 1
        elif child.tag == qn("w:tbl"):
            if table_idx < len(tables):
                elements.append(("table", tables[table_idx], None))
                table_idx += 1

    return elements


def create_sub_document(preamble_elements: list, section_elements: list, output_path: str) -> int:
    """Create a sub-document containing preamble + section elements. Returns char count."""
    sub_doc = Document()

    if sub_doc.paragraphs:
        default_para = sub_doc.paragraphs[0]._element
        default_para.getparent().remove(default_para)

    total_chars = 0

    for elem_type, elem_obj, _ in preamble_elements:
        if elem_type == "paragraph":
            copy_paragraph(elem_obj, sub_doc)
            total_chars += len(elem_obj.text)
        elif elem_type == "table":
            copy_table(elem_obj, sub_doc)
            for row in elem_obj.rows:
                for cell in row.cells:
                    total_chars += len(cell.text)

    for elem_type, elem_obj, _ in section_elements:
        if elem_type == "paragraph":
            copy_paragraph(elem_obj, sub_doc)
            total_chars += len(elem_obj.text)
        elif elem_type == "table":
            copy_table(elem_obj, sub_doc)
            for row in elem_obj.rows:
                for cell in row.cells:
                    total_chars += len(cell.text)

    sub_doc.save(output_path)
    return total_chars


def split_at_heading2(
    preamble_elements: list, section_elements: list,
    base_name: str, heading1_text: str, output_dir: str,
    sub_counter: int, chars_per_page: int,
) -> list[dict]:
    """Further split a section at Heading 2 boundaries when it exceeds the limit."""
    records = []

    h2_indices = []
    for i, (elem_type, elem_obj, _) in enumerate(section_elements):
        if elem_type == "paragraph" and get_heading_level(elem_obj.style) == 2:
            h2_indices.append(i)

    if not h2_indices:
        safe_heading = sanitize_filename(heading1_text)
        out_name = f"{base_name} - {safe_heading}.docx"
        out_path = os.path.join(output_dir, out_name)
        char_count = create_sub_document(preamble_elements, section_elements, out_path)
        records.append({
            "original_doc": f"{base_name}_fixed.docx",
            "sub_doc_filename": out_name,
            "heading_text": heading1_text,
            "character_count": char_count,
            "page_estimate": round(char_count / chars_per_page, 1),
        })
        return records

    split_points = h2_indices + [len(section_elements)]
    chunk_start = 0

    for sp_idx, sp_end in enumerate(split_points):
        chunk_elements = section_elements[chunk_start:sp_end]
        if not chunk_elements:
            chunk_start = sp_end
            continue

        first_elem = chunk_elements[0]
        if first_elem[0] == "paragraph" and get_heading_level(first_elem[1].style) in (1, 2):
            sub_heading = first_elem[1].text.strip()
        else:
            sub_heading = heading1_text

        safe_heading = sanitize_filename(f"{heading1_text} - {sub_heading}")
        out_name = f"{base_name} - {safe_heading}.docx"
        out_path = os.path.join(output_dir, out_name)

        char_count = create_sub_document(preamble_elements, chunk_elements, out_path)
        records.append({
            "original_doc": f"{base_name}_fixed.docx",
            "sub_doc_filename": out_name,
            "heading_text": sub_heading,
            "character_count": char_count,
            "page_estimate": round(char_count / chars_per_page, 1),
        })
        chunk_start = sp_end

    return records


def process_document(filepath: str, output_dir: str, max_chars: int, chars_per_page: int) -> list[dict]:
    """Process a single _fixed.docx file: split at Heading 1 boundaries."""
    doc = Document(filepath)
    filename = os.path.basename(filepath)
    base_name = os.path.splitext(filename)[0]
    if base_name.endswith("_fixed"):
        base_name = base_name[:-6]

    elements = build_element_sequence(doc)
    records = []

    if not elements:
        return records

    h1_element_indices = []
    for i, (elem_type, elem_obj, _) in enumerate(elements):
        if elem_type == "paragraph" and get_heading_level(elem_obj.style) == 1:
            h1_element_indices.append(i)

    if not h1_element_indices:
        safe_name = sanitize_filename(base_name)
        out_name = f"{safe_name} - Full Document.docx"
        out_path = os.path.join(output_dir, out_name)
        char_count = create_sub_document([], elements, out_path)
        records.append({
            "original_doc": filename,
            "sub_doc_filename": out_name,
            "heading_text": "(Full Document - No Heading 1 found)",
            "character_count": char_count,
            "page_estimate": round(char_count / chars_per_page, 1),
        })
        return records

    preamble_elements = elements[:h1_element_indices[0]]
    section_boundaries = h1_element_indices + [len(elements)]

    for sec_idx in range(len(h1_element_indices)):
        start = section_boundaries[sec_idx]
        end = section_boundaries[sec_idx + 1]
        section_elements = elements[start:end]

        heading1_elem = section_elements[0]
        heading1_text = heading1_elem[1].text.strip() if heading1_elem[0] == "paragraph" else "Untitled Section"

        section_chars = 0
        preamble_chars = 0
        for elem_type, elem_obj, _ in section_elements:
            if elem_type == "paragraph":
                section_chars += len(elem_obj.text)
            elif elem_type == "table":
                for row in elem_obj.rows:
                    for cell in row.cells:
                        section_chars += len(cell.text)
        for elem_type, elem_obj, _ in preamble_elements:
            if elem_type == "paragraph":
                preamble_chars += len(elem_obj.text)
            elif elem_type == "table":
                for row in elem_obj.rows:
                    for cell in row.cells:
                        preamble_chars += len(cell.text)

        total_chars = preamble_chars + section_chars

        if total_chars > max_chars:
            sub_records = split_at_heading2(
                preamble_elements, section_elements, base_name,
                heading1_text, output_dir, sec_idx, chars_per_page,
            )
            records.extend(sub_records)
        else:
            safe_heading = sanitize_filename(heading1_text)
            out_name = f"{base_name} - {safe_heading}.docx"
            out_path = os.path.join(output_dir, out_name)
            char_count = create_sub_document(preamble_elements, section_elements, out_path)
            records.append({
                "original_doc": filename,
                "sub_doc_filename": out_name,
                "heading_text": heading1_text,
                "character_count": char_count,
                "page_estimate": round(char_count / chars_per_page, 1),
            })

    return records


def main():
    parser = setup_argparse("Step 4: Split _fixed.docx policy documents at Heading 1 boundaries")
    args = parser.parse_args()

    config = load_config(args.config)
    thresholds = config.get("thresholds", {})
    max_chars = thresholds.get("max_characters", 36_000)
    chars_per_page = thresholds.get("chars_per_page", 1800)

    # Input: Step 3's output directory (heading fixes)
    if args.input_dir:
        input_dir = args.input_dir
    else:
        input_dir = get_output_dir(config, "heading_fixes")

    output_dir = get_output_dir(config, "split_documents", args.output_dir)
    ensure_output_dir(output_dir)

    # Only process _fixed.docx files
    all_files = iter_docx_files(input_dir, config)
    docx_files = [f for f in all_files if os.path.basename(f).endswith("_fixed.docx")]

    if not docx_files:
        print(f"No *_fixed.docx files found in {input_dir}")
        print("Run heading_style_fixer.py (Step 3) first to generate _fixed.docx files.")
        return

    manifest_file = config.get("output", {}).get("split_documents", {}).get("manifest_file", "split_manifest.csv")
    csv_path = os.path.join(output_dir, manifest_file)
    fieldnames = [
        "original_doc", "sub_doc_filename", "heading_text",
        "character_count", "page_estimate",
    ]

    all_records = []
    files_processed = 0
    files_failed = 0

    for filepath in docx_files:
        filename = os.path.basename(filepath)
        try:
            records = process_document(filepath, output_dir, max_chars, chars_per_page)
            all_records.extend(records)
            files_processed += 1
            print(f"  Processing {filename}... {len(records)} sub-document(s) created")
        except Exception as e:
            files_failed += 1
            print(f"  ERROR processing {filename}: {e}")
            traceback.print_exc()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_records)

    print("\n" + "=" * 60)
    print("STEP 4 — SECTION SPLITTER SUMMARY")
    print("=" * 60)
    print(f"Files processed:        {files_processed}")
    print(f"Files failed:           {files_failed}")
    print(f"Total sub-docs created: {len(all_records)}")

    over_limit = [r for r in all_records if r["character_count"] > max_chars]
    if over_limit:
        print(f"\nWARNING: {len(over_limit)} sub-document(s) still exceed {max_chars:,} characters:")
        for r in over_limit:
            print(f"  {r['sub_doc_filename']}: {r['character_count']:,} chars")

    print(f"\nSub-documents written to: {output_dir}")
    print(f"Manifest written to: {csv_path}")


if __name__ == "__main__":
    main()
