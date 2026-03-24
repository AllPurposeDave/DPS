"""
Step 6: Control Validation
============================

Validates that all controls extracted by Step 1 (extract_controls.py) are
present in the split documents produced by Step 4 (section_splitter.py).

Reads:
    - output/1 - controls/controls_output.csv  (source controls)
    - output/4 - split_documents/*.docx         (split documents)
    - output/4 - split_documents/split_manifest.csv (sub-doc → parent mapping)

Outputs:
    - output/6 - validation/control_validation.csv

Usage (unified pipeline):
    python run_pipeline.py --step 6

Usage (standalone):
    python scripts/validate_controls.py
    python scripts/validate_controls.py --config ../dps_config.yaml

PREREQUISITES: Steps 1, 3, and 4 must have run first.
"""

import csv
import os
import re
import traceback

from docx import Document

from shared_utils import (
    ensure_output_dir,
    load_config,
    setup_argparse,
)


CSV_COLUMNS = [
    "control_id",
    "source_file",
    "source_section",
    "found_in_split_docs",
    "split_doc_filenames",
    "parent_doc_match",
    "status",
]


def build_control_id_regex(config: dict) -> re.Pattern:
    """Build a combined regex from the control_id_patterns in config."""
    ctrl_cfg = config.get("control_extraction", {})
    id_patterns = ctrl_cfg.get("control_id_patterns", None)
    if id_patterns is None:
        legacy = ctrl_cfg.get("control_id_pattern", r'\b[A-Z]{2,4}[-.]?\d{1,3}[-.]\d{2,4}\b')
        id_patterns = [legacy]
    combined = "|".join(f"({p})" for p in id_patterns)
    return re.compile(combined)


def load_source_controls(controls_csv_path: str) -> list[dict]:
    """
    Read controls_output.csv and extract unique control records.
    Returns list of dicts with control_id, source_file, source_section.
    """
    controls = []
    seen = set()
    with open(controls_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            control_id = row.get("control_id", "").strip()
            source_file = row.get("source_file", "").strip()
            section = row.get("section_header", "").strip()
            if not control_id:
                continue
            key = (control_id, source_file)
            if key not in seen:
                seen.add(key)
                controls.append({
                    "control_id": control_id,
                    "source_file": source_file,
                    "source_section": section,
                })
    return controls


def load_split_manifest(manifest_path: str) -> dict:
    """
    Read split_manifest.csv to map sub-doc filenames to parent documents.
    Returns dict: {sub_doc_filename: original_doc}
    """
    mapping = {}
    if not os.path.exists(manifest_path):
        return mapping
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sub_doc = row.get("sub_doc_filename", "").strip()
            original = row.get("original_doc", "").strip()
            if sub_doc:
                mapping[sub_doc] = original
    return mapping


def scan_split_documents(split_doc_dir: str, control_regex: re.Pattern) -> dict:
    """
    Open each .docx in the split documents directory, extract all text,
    and find all control IDs present.
    Returns dict: {control_id: [list of split doc filenames]}
    """
    control_to_docs = {}
    docx_files = sorted([
        f for f in os.listdir(split_doc_dir)
        if f.lower().endswith(".docx") and not f.startswith("~$")
    ])

    for filename in docx_files:
        filepath = os.path.join(split_doc_dir, filename)
        try:
            doc = Document(filepath)
        except Exception as e:
            print(f"  WARNING: Could not open {filename}: {e}")
            continue

        # Extract all text from paragraphs and tables
        text_parts = [p.text for p in doc.paragraphs]
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text_parts.append(cell.text)
        full_text = "\n".join(text_parts)

        # Find all control IDs in this document
        matches = control_regex.findall(full_text)
        # findall with groups returns tuples; flatten to get actual matched strings
        found_ids = set()
        for match in matches:
            if isinstance(match, tuple):
                # Take the first non-empty group
                for group in match:
                    if group:
                        found_ids.add(group)
                        break
            else:
                found_ids.add(match)

        for cid in found_ids:
            control_to_docs.setdefault(cid, []).append(filename)

    return control_to_docs


def normalize_parent_name(original_doc: str, source_file: str) -> bool:
    """
    Check if a split doc's parent matches the source file.
    Handles _fixed suffix and common naming variations.
    """
    # Strip _fixed suffix from original_doc
    orig = original_doc.replace("_fixed", "").strip()
    src = source_file.strip()
    # Compare base names without extension
    orig_base = os.path.splitext(orig)[0].lower()
    src_base = os.path.splitext(src)[0].lower()
    return orig_base == src_base


def validate_controls(
    source_controls: list[dict],
    control_to_docs: dict,
    manifest_mapping: dict,
) -> list[dict]:
    """
    Cross-reference source controls against split document findings.
    Returns validation records.
    """
    results = []

    for ctrl in source_controls:
        cid = ctrl["control_id"]
        source_file = ctrl["source_file"]
        source_section = ctrl["source_section"]

        found_docs = control_to_docs.get(cid, [])
        found = len(found_docs) > 0

        # Check parent document match
        parent_match = False
        if found and manifest_mapping:
            for doc_name in found_docs:
                parent = manifest_mapping.get(doc_name, "")
                if parent and normalize_parent_name(parent, source_file):
                    parent_match = True
                    break

        # Determine status
        if not found:
            status = "MISSING"
            parent_match_str = ""
        elif not manifest_mapping:
            status = "PASS"
            parent_match_str = "N/A"
        elif parent_match:
            status = "PASS"
            parent_match_str = "YES"
        else:
            status = "RELOCATED"
            parent_match_str = "NO"

        results.append({
            "control_id": cid,
            "source_file": source_file,
            "source_section": source_section,
            "found_in_split_docs": "YES" if found else "NO",
            "split_doc_filenames": ", ".join(found_docs) if found_docs else "",
            "parent_doc_match": parent_match_str,
            "status": status,
        })

    return results


def main():
    parser = setup_argparse("Step 6: Validate controls in split documents")
    args = parser.parse_args()

    config = load_config(args.config)
    output_cfg = config.get("output", {})
    config_dir = config.get("_config_dir", os.getcwd())

    # Resolve output root
    output_root = output_cfg.get("directory", "./output")
    if not os.path.isabs(output_root):
        output_root = os.path.normpath(os.path.join(config_dir, output_root))

    # Resolve Step 1 controls CSV path
    controls_cfg = output_cfg.get("controls", {})
    controls_dir = os.path.join(output_root, controls_cfg.get("directory", "1 - controls"))
    controls_file = controls_cfg.get("output_file", "controls_output.csv")
    controls_csv_path = os.path.join(controls_dir, controls_file)

    if not os.path.exists(controls_csv_path):
        # Try xlsx → csv fallback
        alt_path = controls_csv_path.replace(".xlsx", ".csv")
        if os.path.exists(alt_path):
            controls_csv_path = alt_path
        else:
            print(f"ERROR: Controls output not found at {controls_csv_path}")
            print("Step 1 (extract_controls.py) must run first.")
            return

    # Resolve Step 4 split documents directory
    split_cfg = output_cfg.get("split_documents", {})
    split_dir = os.path.join(output_root, split_cfg.get("directory", "4 - split_documents"))
    manifest_file = split_cfg.get("manifest_file", "split_manifest.csv")
    manifest_path = os.path.join(split_dir, manifest_file)

    if not os.path.isdir(split_dir):
        print(f"ERROR: Split documents directory not found at {split_dir}")
        print("Steps 3-4 (heading_style_fixer + section_splitter) must run first.")
        return

    # Resolve Step 6 output directory
    validation_cfg = output_cfg.get("validation", {})
    validation_dir = os.path.join(output_root, validation_cfg.get("directory", "6 - validation"))
    validation_file = validation_cfg.get("output_file", "control_validation.csv")
    ensure_output_dir(validation_dir)
    output_path = os.path.join(validation_dir, validation_file)

    # Build control ID regex
    control_regex = build_control_id_regex(config)

    # Step A: Load source controls
    print("  Loading source controls from Step 1...")
    source_controls = load_source_controls(controls_csv_path)
    if not source_controls:
        print("  WARNING: No controls found in controls output. Nothing to validate.")
        return
    print(f"  Found {len(source_controls)} unique control(s) from {len(set(c['source_file'] for c in source_controls))} document(s)")

    # Step B: Load split manifest
    manifest_mapping = load_split_manifest(manifest_path)
    if not manifest_mapping:
        print("  WARNING: Split manifest not found or empty. Parent-doc matching will be skipped.")

    # Step C: Scan split documents
    print("  Scanning split documents for control IDs...")
    control_to_docs = scan_split_documents(split_dir, control_regex)
    unique_ids_found = len(control_to_docs)
    print(f"  Found {unique_ids_found} unique control ID(s) across split documents")

    # Step D: Validate
    print("  Cross-referencing...")
    results = validate_controls(source_controls, control_to_docs, manifest_mapping)

    # Write output CSV
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(results)

    # Summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    missing = sum(1 for r in results if r["status"] == "MISSING")
    relocated = sum(1 for r in results if r["status"] == "RELOCATED")

    print()
    print("=" * 60)
    print("STEP 6 — CONTROL VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Total source controls: {total}")
    print(f"Found (PASS):          {passed}  ({round(passed/total*100, 1) if total else 0}%)")
    print(f"Missing:               {missing}  ({round(missing/total*100, 1) if total else 0}%)")
    print(f"Relocated:             {relocated}  ({round(relocated/total*100, 1) if total else 0}%)")

    if missing > 0:
        print(f"\nMISSING CONTROLS:")
        for r in results:
            if r["status"] == "MISSING":
                print(f"  {r['control_id']}  from  {r['source_file']}")

    if relocated > 0:
        print(f"\nRELOCATED CONTROLS (found in different parent doc):")
        for r in results:
            if r["status"] == "RELOCATED":
                print(f"  {r['control_id']}  from  {r['source_file']}  →  {r['split_doc_filenames'][:60]}")

    print(f"\nValidation output written to: {output_path}")


if __name__ == "__main__":
    main()
