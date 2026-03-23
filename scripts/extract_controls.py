"""
Step 4 of 5: Compliance Document Control Extractor
=====================================================

Reads .docx compliance/security policy documents, extracts structured
control data (IDs, descriptions, implementation guidance, and document
metadata), then writes everything into a consolidated CSV.

Usage (unified pipeline):
    python run_pipeline.py --step 4

Usage (standalone):
    python scripts/extract_controls.py
    python scripts/extract_controls.py --config dps_config.yaml
    python scripts/extract_controls.py ./input ./output

Output:
    controls_output.csv — one row per extracted control
    checkpoint.json — tracks progress for resumable runs
    errors.log — error and warning log

DEPENDENCIES:
    pip install python-docx pyyaml
    Everything else is Python stdlib. No API keys. Fully offline.
"""

import re
import csv
import os
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict

from docx import Document

from shared_utils import (
    ensure_output_dir,
    get_input_dir,
    get_output_dir,
    iter_docx_files,
    load_config,
    setup_argparse,
)


# ============================================================
# SECTION: DATA MODEL
# ============================================================

@dataclass
class ControlRow:
    """Represents a single row in the output CSV."""
    source_file: str = ""
    section_header: str = ""
    control_id: str = ""
    control_description: str = ""
    implementation_guidelines: str = ""
    purpose: str = ""
    scope: str = ""
    applicability: str = ""


# ============================================================
# SECTION: REGEX PATTERNS (built from config)
# ============================================================

def build_patterns(config: dict) -> dict:
    """Build all regex patterns from config, with sensible defaults."""
    ctrl_cfg = config.get("control_extraction", {})

    control_id = ctrl_cfg.get("control_id_pattern", r'\b[A-Z]{2,4}[-.]?\d{1,3}[-.]\d{2,4}\b')
    impl_trigger = ctrl_cfg.get("implementation_trigger",
                                r'(?i)(implementation guidance|implementation:|guidelines:|how to implement)')

    return {
        "control_id": re.compile(control_id),
        "impl_trigger": re.compile(impl_trigger),
        "section_keyword": re.compile(r'^[Ss]ection\s+\d{1,2}'),
        "numbered_title": re.compile(r'^\d{1,2}\.?\d{0,2}\s+[A-Z][a-zA-Z\s]{3,50}$'),
        "metadata_triggers": {
            "purpose": re.compile(r'\b(purpose|objective|intent)\b', re.IGNORECASE),
            "scope": re.compile(r'\b(scope|coverage|boundary)\b', re.IGNORECASE),
            "applicability": re.compile(r'\b(applicab\w*|applies to|applies for)\b', re.IGNORECASE),
        },
        "metadata_label_strip": re.compile(
            r'(?i)^\s*(purpose|objective|intent|scope|coverage|boundary'
            r'|applicability|applies to|applies for)\s*[:\-]?\s*',
        ),
    }


# ============================================================
# SECTION: LOGGING SETUP
# ============================================================

def setup_logging(output_dir: str):
    """Configure logging to write errors to the output directory."""
    os.makedirs(output_dir, exist_ok=True)

    logger = logging.getLogger("extract_controls")
    logger.setLevel(logging.DEBUG)

    # Remove existing handlers to avoid duplicates on re-run
    logger.handlers.clear()

    file_handler = logging.FileHandler(os.path.join(output_dir, "errors.log"), mode="a")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.WARNING)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(stream_handler)

    return logger


# ============================================================
# SECTION: PARAGRAPH EXTRACTION
# ============================================================

def extract_paragraphs_from_docx(filepath):
    """Open a .docx file and return a list of paragraph metadata dicts."""
    document = Document(str(filepath))
    paragraphs = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        first_run_bold = False
        if paragraph.runs:
            first_run_bold = bool(paragraph.runs[0].bold)
        style_name = paragraph.style.name if paragraph.style else ""
        paragraphs.append({"text": text, "bold": first_run_bold, "style": style_name})

    return paragraphs


# ============================================================
# SECTION: SECTION HEADER DETECTION
# ============================================================

def is_section_header(paragraph_dict, patterns):
    """Determine whether a paragraph is a section header."""
    text = paragraph_dict["text"]
    style = paragraph_dict["style"]
    bold = paragraph_dict["bold"]

    if not text or patterns["control_id"].search(text):
        return (False, "")

    if "Heading" in style:
        return (True, text)
    if patterns["section_keyword"].match(text):
        return (True, text)
    if patterns["numbered_title"].match(text):
        return (True, text)

    word_count = len(text.split())
    if text == text.upper() and len(text) < 80 and not text.endswith(".") and word_count >= 3:
        return (True, text)
    if bold and len(text) < 60 and not text.endswith("."):
        return (True, text)

    return (False, "")


# ============================================================
# SECTION: METADATA EXTRACTION
# ============================================================

def extract_metadata(paragraphs, patterns, config):
    """Scan the first N paragraphs for document-level metadata."""
    metadata = {"purpose": "", "scope": "", "applicability": ""}
    scan_limit_cfg = config.get("control_extraction", {}).get("metadata_scan_paragraphs", 40)
    scan_limit = min(scan_limit_cfg, len(paragraphs))

    trigger_positions = []
    for index in range(scan_limit):
        text = paragraphs[index]["text"]
        if not text:
            continue
        for field_name, pattern in patterns["metadata_triggers"].items():
            if pattern.search(text):
                trigger_positions.append((index, field_name))
                break

    for position_index, (para_index, field_name) in enumerate(trigger_positions):
        if metadata[field_name]:
            continue

        collected_lines = []
        if position_index + 1 < len(trigger_positions):
            stop_index = trigger_positions[position_index + 1][0]
        else:
            stop_index = scan_limit

        for capture_index in range(para_index, stop_index):
            paragraph_text = paragraphs[capture_index]["text"]
            if not paragraph_text:
                continue
            if capture_index > para_index:
                is_header, _ = is_section_header(paragraphs[capture_index], patterns)
                if is_header:
                    break
            collected_lines.append(paragraph_text)

        raw_metadata = " ".join(collected_lines)
        cleaned = patterns["metadata_label_strip"].sub("", raw_metadata, count=1)
        metadata[field_name] = clean_text(cleaned)

    return metadata


# ============================================================
# SECTION: CONTROL BLOCK SEGMENTATION
# ============================================================

def find_control_blocks(paragraphs, patterns):
    """Identify and segment individual control blocks from paragraphs."""
    blocks = []
    current_section_header = ""
    active_block = None

    for paragraph_dict in paragraphs:
        text = paragraph_dict["text"]
        is_header, header_text = is_section_header(paragraph_dict, patterns)
        if is_header:
            if active_block is not None:
                blocks.append(active_block)
                active_block = None
            current_section_header = header_text
            continue

        if not text:
            continue

        control_id_matches = patterns["control_id"].findall(text)

        if control_id_matches:
            if active_block is not None:
                blocks.append(active_block)

            for match_index, control_id in enumerate(control_id_matches):
                if match_index == 0:
                    active_block = {
                        "control_id": control_id,
                        "raw_lines": [text],
                        "section_header": current_section_header,
                    }
                else:
                    blocks.append({
                        "control_id": control_id,
                        "raw_lines": [text],
                        "section_header": current_section_header,
                    })
        elif active_block is not None:
            active_block["raw_lines"].append(text)

    if active_block is not None:
        blocks.append(active_block)

    processed_blocks = []
    for block in blocks:
        joined_text = "\n".join(block["raw_lines"])
        split_result = patterns["impl_trigger"].split(joined_text, maxsplit=1)

        if len(split_result) >= 3:
            control_description = clean_text(split_result[0])
            implementation_guidelines = clean_text(split_result[2])
        else:
            control_description = clean_text(joined_text)
            implementation_guidelines = ""

        processed_blocks.append({
            "control_id": block["control_id"],
            "control_description": control_description,
            "implementation_guidelines": implementation_guidelines,
            "section_header": block["section_header"],
        })

    return processed_blocks


# ============================================================
# SECTION: TEXT CLEANING
# ============================================================

def clean_text(text):
    """Normalize whitespace and remove non-printable characters."""
    text = text.strip()
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# ============================================================
# SECTION: SINGLE DOCUMENT PROCESSING
# ============================================================

def process_single_document(filepath, patterns, config):
    """Run the full extraction pipeline on a single .docx file."""
    filepath = Path(filepath)
    source_file = filepath.name
    paragraphs = extract_paragraphs_from_docx(filepath)

    if not paragraphs:
        print(f"  WARNING: {source_file} has 0 paragraphs, skipping.")
        return []

    metadata = extract_metadata(paragraphs, patterns, config)

    purpose_found = "Yes" if metadata["purpose"] else "No"
    scope_found = "Yes" if metadata["scope"] else "No"
    applicability_found = "Yes" if metadata["applicability"] else "No"
    print(f"  Metadata found -- Purpose: {purpose_found} | "
          f"Scope: {scope_found} | Applicability: {applicability_found}")

    control_blocks = find_control_blocks(paragraphs, patterns)
    print(f"  Controls extracted: {len(control_blocks)}")

    rows = []
    for block in control_blocks:
        row = ControlRow(
            source_file=source_file,
            section_header=block["section_header"],
            control_id=block["control_id"],
            control_description=block["control_description"],
            implementation_guidelines=block["implementation_guidelines"],
            purpose=metadata["purpose"],
            scope=metadata["scope"],
            applicability=metadata["applicability"],
        )
        rows.append(row)

    return rows


# ============================================================
# SECTION: CHECKPOINTING
# ============================================================

def load_checkpoint(checkpoint_path):
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, "r") as f:
            return json.load(f)
    return []


def save_checkpoint(checkpoint_path, completed_files):
    with open(checkpoint_path, "w") as f:
        json.dump(completed_files, f, indent=2)


# ============================================================
# SECTION: MAIN ENTRY POINT
# ============================================================

def main():
    parser = setup_argparse("Step 4: Extract controls from compliance .docx documents")
    args = parser.parse_args()

    config = load_config(args.config)
    ctrl_cfg = config.get("control_extraction", {})
    input_dir = get_input_dir(config, args.input_dir)
    output_dir = get_output_dir(config, "controls", args.output_dir)
    ensure_output_dir(output_dir)

    logger = setup_logging(output_dir)
    patterns = build_patterns(config)

    output_file = config.get("output", {}).get("controls", {}).get("output_file", "controls_output.csv")
    checkpoint_file = config.get("output", {}).get("controls", {}).get("checkpoint_file", "checkpoint.json")
    checkpoint_path = os.path.join(output_dir, checkpoint_file)
    output_csv_path = os.path.join(output_dir, output_file)

    docx_files = iter_docx_files(input_dir, config)
    if not docx_files:
        print(f"No .docx files found in {input_dir}")
        return

    enable_checkpoint = ctrl_cfg.get("enable_checkpoint", True)
    completed_files = load_checkpoint(checkpoint_path) if enable_checkpoint else []
    total_controls = 0
    files_processed = 0
    files_skipped = 0
    error_count = 0

    csv_columns = [
        "source_file", "section_header", "control_id",
        "control_description", "implementation_guidelines",
        "purpose", "scope", "applicability",
    ]

    for filepath in docx_files:
        filename = os.path.basename(filepath)

        if filename in completed_files:
            print(f"  Skipping (already processed): {filename}")
            files_skipped += 1
            continue

        print(f"  Processing: {filename}")

        try:
            rows = process_single_document(filepath, patterns, config)

            if rows:
                file_exists = os.path.exists(output_csv_path) and os.path.getsize(output_csv_path) > 0
                write_mode = "a" if file_exists else "w"

                with open(output_csv_path, write_mode, newline="", encoding="utf-8") as csv_file:
                    writer = csv.DictWriter(csv_file, fieldnames=csv_columns, quoting=csv.QUOTE_ALL)
                    if not file_exists:
                        writer.writeheader()
                    for row in rows:
                        writer.writerow(asdict(row))

            total_controls += len(rows)

            if enable_checkpoint:
                completed_files.append(filename)
                save_checkpoint(checkpoint_path, completed_files)
            files_processed += 1

        except Exception as error:
            error_count += 1
            logger.error("Failed to process %s: %s", filename, error, exc_info=True)
            print(f"  ERROR processing {filename}: {error}")

    print("\n" + "=" * 60)
    print("STEP 4 — CONTROL EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {files_processed}")
    print(f"Controls found:  {total_controls}")
    print(f"Errors:          {error_count}")
    if files_skipped:
        print(f"Skipped (checkpoint): {files_skipped}")
    print(f"\nOutput: {output_csv_path}")


if __name__ == "__main__":
    main()
