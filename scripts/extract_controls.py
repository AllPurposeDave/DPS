"""
Step 1: Compliance Document Control Extractor
=====================================================

Reads .docx compliance/security policy documents, extracts structured
control data (IDs, descriptions, supplemental guidance, and document
metadata), then writes everything into CSV and/or Excel output.

Features:
    - Multiple control ID patterns (any pattern triggers a match)
    - Whitelist/blacklist filtering by exact ID or prefix wildcard
    - 3-way text classification: description / supplemental guidance / miscellaneous
    - Configurable section heading detection (5 signal types)
    - CSV and/or Excel output (configurable)
    - Checkpointing for resumable batch runs

Usage (unified pipeline):
    python run_pipeline.py --step 1

Usage (standalone):
    python scripts/extract_controls.py
    python scripts/extract_controls.py --config dps_config.yaml
    python scripts/extract_controls.py ./input ./output

Output:
    controls_output.csv  — one row per extracted control (if CSV enabled)
    controls_output.xlsx — one row per extracted control (if Excel enabled)
    checkpoint.json      — tracks progress for resumable runs
    errors.log           — error and warning log

DEPENDENCIES:
    pip install python-docx pyyaml openpyxl
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
    """Represents a single row in the output."""
    source_file: str = ""
    section_header: str = ""
    control_id: str = ""
    control_description: str = ""
    supplemental_guidance: str = ""
    miscellaneous: str = ""
    purpose: str = ""
    scope: str = ""
    applicability: str = ""


# ============================================================
# SECTION: REGEX PATTERNS (built from config)
# ============================================================

def build_patterns(config: dict) -> dict:
    """Build all regex patterns from config, with sensible defaults."""
    ctrl_cfg = config.get("control_extraction", {})

    # Support both legacy single-pattern and new multi-pattern config
    id_patterns = ctrl_cfg.get("control_id_patterns", None)
    if id_patterns is None:
        legacy = ctrl_cfg.get("control_id_pattern", r'\b[A-Z]{2,4}[-.]?\d{1,3}[-.]\d{2,4}\b')
        id_patterns = [legacy]

    # Build combined regex from all patterns
    combined_pattern = "|".join(f"({p})" for p in id_patterns)
    control_id_combined = re.compile(combined_pattern)

    impl_trigger = ctrl_cfg.get("implementation_trigger",
                                r'(?i)(implementation guidance|implementation:|guidelines:|how to implement|supplemental guidance)')

    # Build guidance regex from keywords list if available, else use impl_trigger
    guidance_keywords = ctrl_cfg.get("guidance_keywords", None)
    if guidance_keywords:
        escaped_keywords = [re.escape(kw) for kw in guidance_keywords]
        guidance_pattern = "|".join(escaped_keywords)
        guidance_regex = re.compile(f"(?i)({guidance_pattern})")
    else:
        guidance_regex = re.compile(impl_trigger)

    # Build metadata trigger regexes from config or defaults
    meta_cfg = ctrl_cfg.get("metadata_triggers", {})
    metadata_regexes = {}
    all_metadata_words = []
    default_meta = {
        "purpose": ["purpose", "objective", "intent"],
        "scope": ["scope", "coverage", "boundary"],
        "applicability": ["applicability", "applies to", "applies for"],
    }
    for field_name, default_keywords in default_meta.items():
        keywords = meta_cfg.get(field_name, default_keywords)
        escaped = [re.escape(kw) for kw in keywords]
        pattern = r'\b(' + "|".join(escaped) + r')\b'
        metadata_regexes[field_name] = re.compile(pattern, re.IGNORECASE)
        all_metadata_words.extend(keywords)

    # Build metadata label strip regex
    escaped_all = [re.escape(w) for w in all_metadata_words]
    strip_pattern = r'(?i)^\s*(' + "|".join(escaped_all) + r')\s*[:\-]?\s*'

    # Build heading detection regexes from config
    hd_cfg = ctrl_cfg.get("heading_detection", {})
    section_kw = hd_cfg.get("section_keyword_pattern", r'^[Ss]ection\s+\d{1,2}')
    numbered_title = hd_cfg.get("numbered_title_pattern", r'^\d{1,2}\.?\d{0,2}\s+[A-Z][a-zA-Z\s]{3,50}$')

    return {
        "control_id": control_id_combined,
        "guidance_regex": guidance_regex,
        "section_keyword": re.compile(section_kw),
        "numbered_title": re.compile(numbered_title),
        "heading_detection": {
            "use_word_heading_style": hd_cfg.get("use_word_heading_style", True),
            "detect_allcaps": hd_cfg.get("detect_allcaps", True),
            "allcaps_max_length": hd_cfg.get("allcaps_max_length", 80),
            "allcaps_min_words": hd_cfg.get("allcaps_min_words", 3),
            "detect_bold_short": hd_cfg.get("detect_bold_short", True),
            "bold_max_length": hd_cfg.get("bold_max_length", 60),
        },
        "metadata_triggers": metadata_regexes,
        "metadata_label_strip": re.compile(strip_pattern),
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
    """Determine whether a paragraph is a section header.

    Checks multiple signals in priority order, each configurable via
    the heading_detection section in dps_config.yaml.
    """
    text = paragraph_dict["text"]
    style = paragraph_dict["style"]
    bold = paragraph_dict["bold"]
    hd = patterns["heading_detection"]

    # Skip empty paragraphs and lines containing a control ID
    if not text or patterns["control_id"].search(text):
        return (False, "")

    # Signal 1: Word heading style
    if hd["use_word_heading_style"] and "Heading" in style:
        return (True, text)

    # Signal 2: "Section N" keyword
    if patterns["section_keyword"].match(text):
        return (True, text)

    # Signal 3: Numbered title
    if patterns["numbered_title"].match(text):
        return (True, text)

    # Signal 4: ALL-CAPS short text
    if hd["detect_allcaps"]:
        word_count = len(text.split())
        if (text == text.upper()
                and len(text) < hd["allcaps_max_length"]
                and not text.endswith(".")
                and word_count >= hd["allcaps_min_words"]):
            return (True, text)

    # Signal 5: Bold short text
    if hd["detect_bold_short"]:
        if bold and len(text) < hd["bold_max_length"] and not text.endswith("."):
            return (True, text)

    return (False, "")


# ============================================================
# SECTION: METADATA EXTRACTION
# ============================================================

def extract_metadata(paragraphs, patterns, config):
    """Scan the first N paragraphs for document-level metadata."""
    metadata = {field: "" for field in patterns["metadata_triggers"]}
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
    """Identify and segment individual control blocks from paragraphs.

    Splits each block into description / supplemental_guidance / miscellaneous
    using guidance keyword boundaries.
    """
    control_id_regex = patterns["control_id"]
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

        control_id_matches = control_id_regex.findall(text)

        if control_id_matches:
            # Flatten: findall with groups returns tuples — take first non-empty
            if control_id_matches and isinstance(control_id_matches[0], tuple):
                control_id_matches = [
                    next(g for g in m if g) for m in control_id_matches
                ]

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

    # Split each block's raw text into description / guidance / miscellaneous
    guidance_regex = patterns["guidance_regex"]
    processed_blocks = []

    for block in blocks:
        joined_text = "\n".join(block["raw_lines"])
        split_result = guidance_regex.split(joined_text, maxsplit=1)

        if len(split_result) >= 3:
            description_text = clean_text(split_result[0])
            guidance_text = clean_text(split_result[2])

            # Check for a second guidance trigger — text after goes to miscellaneous
            second_split = guidance_regex.split(split_result[2], maxsplit=1)
            if len(second_split) >= 3:
                guidance_text = clean_text(second_split[0])
                miscellaneous_text = clean_text(second_split[2])
            else:
                miscellaneous_text = ""
        else:
            description_text = clean_text(joined_text)
            guidance_text = ""
            miscellaneous_text = ""

        processed_blocks.append({
            "control_id": block["control_id"],
            "control_description": description_text,
            "supplemental_guidance": guidance_text,
            "miscellaneous": miscellaneous_text,
            "section_header": block["section_header"],
        })

    return processed_blocks


# ============================================================
# SECTION: WHITELIST / BLACKLIST FILTERING
# ============================================================

def matches_filter(control_id, filter_list):
    """Check if a control ID matches any entry in a filter list.

    Supports exact matches and prefix wildcards (e.g., "AC-*").
    """
    for pattern in filter_list:
        if pattern.endswith("*"):
            if control_id.startswith(pattern[:-1]):
                return True
        else:
            if control_id == pattern:
                return True
    return False


def apply_filters(control_blocks, config):
    """Apply whitelist and blacklist filters to control blocks."""
    ctrl_cfg = config.get("control_extraction", {})
    whitelist = ctrl_cfg.get("whitelist", [])
    blacklist = ctrl_cfg.get("blacklist", [])

    filtered = control_blocks

    if whitelist:
        filtered = [b for b in filtered if matches_filter(b["control_id"], whitelist)]

    if blacklist:
        filtered = [b for b in filtered if not matches_filter(b["control_id"], blacklist)]

    return filtered


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

    purpose_found = "Yes" if metadata.get("purpose") else "No"
    scope_found = "Yes" if metadata.get("scope") else "No"
    applicability_found = "Yes" if metadata.get("applicability") else "No"
    print(f"  Metadata found -- Purpose: {purpose_found} | "
          f"Scope: {scope_found} | Applicability: {applicability_found}")

    control_blocks = find_control_blocks(paragraphs, patterns)
    print(f"  Controls extracted: {len(control_blocks)}")

    # Apply whitelist/blacklist filtering
    control_blocks = apply_filters(control_blocks, config)
    ctrl_cfg = config.get("control_extraction", {})
    if ctrl_cfg.get("whitelist") or ctrl_cfg.get("blacklist"):
        print(f"  Controls after filtering: {len(control_blocks)}")

    rows = []
    for block in control_blocks:
        row = ControlRow(
            source_file=source_file,
            section_header=block["section_header"],
            control_id=block["control_id"],
            control_description=block["control_description"],
            supplemental_guidance=block["supplemental_guidance"],
            miscellaneous=block["miscellaneous"],
            purpose=metadata.get("purpose", ""),
            scope=metadata.get("scope", ""),
            applicability=metadata.get("applicability", ""),
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
# SECTION: OUTPUT WRITERS
# ============================================================

CSV_COLUMNS = [
    "source_file", "section_header", "control_id",
    "control_description", "supplemental_guidance", "miscellaneous",
    "purpose", "scope", "applicability",
]


def write_rows_to_csv(output_path, rows, append=True):
    """Write control rows to a CSV file."""
    file_exists = os.path.exists(output_path) and os.path.getsize(output_path) > 0
    write_mode = "a" if (file_exists and append) else "w"

    with open(output_path, write_mode, newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS, quoting=csv.QUOTE_ALL)
        if not file_exists or not append:
            writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def write_rows_to_excel(output_path, rows):
    """Write control rows to an Excel file, creating it if needed."""
    from openpyxl import Workbook, load_workbook

    output_path = Path(output_path)
    if output_path.exists() and output_path.stat().st_size > 0:
        wb = load_workbook(output_path)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.title = "Controls"
        ws.append(CSV_COLUMNS)

    for row in rows:
        row_dict = asdict(row)
        ws.append([row_dict[col] for col in CSV_COLUMNS])

    wb.save(output_path)


# ============================================================
# SECTION: MAIN ENTRY POINT
# ============================================================

def main():
    parser = setup_argparse("Step 1: Extract controls from compliance .docx documents")
    args = parser.parse_args()

    config = load_config(args.config)
    ctrl_cfg = config.get("control_extraction", {})
    input_dir = get_input_dir(config, args.input_dir)
    output_dir = get_output_dir(config, "controls", args.output_dir)
    ensure_output_dir(output_dir)

    logger = setup_logging(output_dir)
    patterns = build_patterns(config)

    # Determine output format
    output_format = ctrl_cfg.get("output_format", "both")
    output_csv_file = config.get("output", {}).get("controls", {}).get("output_file", "controls_output.csv")
    output_xlsx_file = config.get("output", {}).get("controls", {}).get("output_file_xlsx", "controls_output.xlsx")
    checkpoint_file = config.get("output", {}).get("controls", {}).get("checkpoint_file", "checkpoint.json")

    checkpoint_path = os.path.join(output_dir, checkpoint_file)
    output_csv_path = os.path.join(output_dir, output_csv_file)
    output_xlsx_path = os.path.join(output_dir, output_xlsx_file)

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
                if output_format in ("csv", "both"):
                    write_rows_to_csv(output_csv_path, rows)
                if output_format in ("xlsx", "both"):
                    write_rows_to_excel(output_xlsx_path, rows)

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
    print("STEP 1 — CONTROL EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Files processed: {files_processed}")
    print(f"Controls found:  {total_controls}")
    print(f"Errors:          {error_count}")
    if files_skipped:
        print(f"Skipped (checkpoint): {files_skipped}")

    outputs = []
    if output_format in ("csv", "both"):
        outputs.append(output_csv_path)
    if output_format in ("xlsx", "both"):
        outputs.append(output_xlsx_path)
    print(f"\nOutput: {', '.join(outputs)}")


if __name__ == "__main__":
    main()
