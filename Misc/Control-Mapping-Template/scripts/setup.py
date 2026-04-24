#!/usr/bin/env python3
"""Setup script: Extract controls from Excel and generate batch prompt files.

Usage:
    python scripts/setup.py
    python scripts/setup.py --config path/to/config.yaml
"""

import argparse
import math
import re
import sys
from collections import OrderedDict
from pathlib import Path

import openpyxl
import yaml

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config(config_path):
    with open(config_path) as f:
        return yaml.safe_load(f)


SYSTEM_PROMPT_MARKER = re.compile(
    r"<!--\s*BEGIN:SYSTEM_PROMPT\s*-->(.*?)<!--\s*END:SYSTEM_PROMPT\s*-->",
    re.DOTALL,
)


def load_system_prompt(claude_md_path):
    """Extract the canonical system prompt block from CLAUDE.md."""
    if not claude_md_path.exists():
        print(f"ERROR: CLAUDE.md not found at {claude_md_path}")
        sys.exit(1)
    text = claude_md_path.read_text(encoding="utf-8")
    match = SYSTEM_PROMPT_MARKER.search(text)
    if not match:
        print(f"ERROR: BEGIN:SYSTEM_PROMPT / END:SYSTEM_PROMPT markers not found in {claude_md_path}")
        sys.exit(1)
    return match.group(1).strip()


# ---------------------------------------------------------------------------
# Excel extraction
# ---------------------------------------------------------------------------

def extract_controls(filepath, sheet_name, col_cfg, header_row):
    """Extract controls from an Excel worksheet based on column config.

    Returns a list of dicts with keys: id, description, and each supplemental label.
    """
    wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
    ws = wb[sheet_name]

    controls = []
    for row in ws.iter_rows(min_row=header_row + 1, values_only=True):
        ctrl_id = row[col_cfg["id"]] if len(row) > col_cfg["id"] else None
        if not ctrl_id:
            continue

        ctrl = {
            "id": str(ctrl_id).strip(),
            "description": str(row[col_cfg["description"]] or "").strip()
            if len(row) > col_cfg["description"] else "",
        }

        for sup in col_cfg.get("supplemental", []):
            idx = sup["index"]
            label = sup["label"]
            ctrl[label] = str(row[idx] or "").strip() if len(row) > idx else ""

        controls.append(ctrl)

    wb.close()
    return controls


# ---------------------------------------------------------------------------
# Reference file generation
# ---------------------------------------------------------------------------

def write_reference_file(filepath, framework_name, controls, supplemental_labels):
    """Write a markdown reference file for a set of controls."""
    lines = [f"# {framework_name} Controls Reference", ""]

    # Group by Domain if present, otherwise flat list
    if "Domain" in supplemental_labels:
        groups = OrderedDict()
        for ctrl in controls:
            domain = ctrl.get("Domain", "Ungrouped")
            groups.setdefault(domain, []).append(ctrl)

        for domain, ctrls in groups.items():
            lines.append(f"## {domain}")
            lines.append("")
            for ctrl in ctrls:
                lines.append(format_control_entry(ctrl, supplemental_labels))
            lines.append("")
    else:
        for ctrl in controls:
            lines.append(format_control_entry(ctrl, supplemental_labels))
        lines.append("")

    filepath.write_text("\n".join(lines), encoding="utf-8")
    print(f"  Wrote {filepath.name}: {len(controls)} controls")


def format_control_entry(ctrl, supplemental_labels):
    """Format a single control as a markdown list item."""
    parts = [f"**{ctrl['id']}**"]

    # Add Title inline if present
    if "Title" in supplemental_labels and ctrl.get("Title"):
        parts.append(f"| {ctrl['Title']}")

    # Add description
    parts.append(f"| {ctrl['description']}")

    line = " ".join(parts)

    # Add other supplemental fields as sub-items (skip Domain and Title, already used)
    extras = []
    for label in supplemental_labels:
        if label in ("Domain", "Title"):
            continue
        value = ctrl.get(label, "")
        if value:
            extras.append(f"  - *{label}*: {value}")

    if extras:
        return f"- {line}\n" + "\n".join(extras)
    return f"- {line}"


# ---------------------------------------------------------------------------
# Target reference (compact format for embedding in prompts)
# ---------------------------------------------------------------------------

def build_target_reference(controls, supplemental_labels):
    """Build the target controls reference text for embedding in batch prompts."""
    lines = []

    if "Domain" in supplemental_labels:
        groups = OrderedDict()
        for ctrl in controls:
            domain = ctrl.get("Domain", "Ungrouped")
            groups.setdefault(domain, []).append(ctrl)

        for domain, ctrls in groups.items():
            lines.append(f"### {domain}")
            for ctrl in ctrls:
                title = ctrl.get("Title", "")
                title_part = f" | {title}" if title else ""
                lines.append(f"- **{ctrl['id']}**{title_part} | {ctrl['description']}")
            lines.append("")
    else:
        for ctrl in controls:
            title = ctrl.get("Title", "")
            title_part = f" | {title}" if title else ""
            lines.append(f"- **{ctrl['id']}**{title_part} | {ctrl['description']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Target chunking
# ---------------------------------------------------------------------------

def chunk_target_controls(controls, chunking_cfg, target_sup_labels=None):
    """Split target controls into family-based chunks.

    Returns a list of dicts: {"name": str, "label": str, "controls": list}
    """
    if target_sup_labels is None:
        target_sup_labels = ["Domain", "Title"]
    strategy = chunking_cfg.get("strategy", "prefix")

    if strategy == "prefix":
        return _chunk_by_prefix(controls, chunking_cfg, target_sup_labels)
    elif strategy == "column":
        return _chunk_by_column(controls, chunking_cfg, target_sup_labels)
    else:
        print(f"  WARNING: Unknown chunking strategy '{strategy}', using all controls as one chunk")
        return [{"name": "all", "label": "All Controls", "controls": controls}]


def _chunk_by_prefix(controls, chunking_cfg, target_sup_labels):
    """Group controls by their ID prefix (e.g., AC-1 → AC)."""
    separator = chunking_cfg.get("separator", "-")
    max_per_chunk = chunking_cfg.get("max_controls_per_chunk", 60)
    max_chars = chunking_cfg.get("max_chars_per_chunk", 0)

    # Extract prefix for each control
    families = OrderedDict()
    for ctrl in controls:
        prefix = ctrl["id"].split(separator)[0].strip() if separator in ctrl["id"] else ctrl["id"]
        families.setdefault(prefix, []).append(ctrl)

    # Sort controls within each family so enhancements (e.g., AC-2(1)) sit next
    # to their base (AC-2). This matters both for the packing logic and the
    # final reference the model reads.
    for prefix, ctrls in families.items():
        ctrls.sort(key=lambda c: _id_sort_key(c["id"], separator))

    # Combine small families if max_per_chunk > 0
    if max_per_chunk > 0 or max_chars > 0:
        return _combine_small_families(
            families, max_per_chunk, max_chars, separator, target_sup_labels,
        )
    else:
        return [
            {"name": _sanitize_name(prefix), "label": f"Family: {prefix}", "controls": ctrls}
            for prefix, ctrls in families.items()
        ]


def _chunk_by_column(controls, chunking_cfg, target_sup_labels):
    """Group controls by a column value."""
    col_idx = chunking_cfg.get("group_by_column")
    max_per_chunk = chunking_cfg.get("max_controls_per_chunk", 60)
    max_chars = chunking_cfg.get("max_chars_per_chunk", 0)
    separator = chunking_cfg.get("separator", "-")

    if col_idx is None:
        print("  WARNING: column strategy requires group_by_column, falling back to one chunk")
        return [{"name": "all", "label": "All Controls", "controls": controls}]

    # We need the raw column value — but controls are already extracted with labels.
    # Use "Domain" if available, otherwise fall back to "Group"
    groups = OrderedDict()
    for ctrl in controls:
        # Try Domain first, then any supplemental that matches the column index
        group_key = ctrl.get("Domain", "Ungrouped")
        groups.setdefault(group_key, []).append(ctrl)

    for key, ctrls in groups.items():
        ctrls.sort(key=lambda c: _id_sort_key(c["id"], separator))

    if max_per_chunk > 0 or max_chars > 0:
        return _combine_small_families(
            groups, max_per_chunk, max_chars, separator, target_sup_labels,
        )
    else:
        return [
            {"name": _sanitize_name(key), "label": key, "controls": ctrls}
            for key, ctrls in groups.items()
        ]


# ---------------------------------------------------------------------------
# ID parsing — base ID and sort key (handles enhancements like AC-2(1)(a))
# ---------------------------------------------------------------------------

_ENH_RE = re.compile(r"\d+")


def _base_id(ctrl_id, separator):
    """Return the base control ID, stripping any enhancement suffix.

    Examples with separator="-":
      AC-2       -> AC-2
      AC-2(1)    -> AC-2
      AC-2(1)(a) -> AC-2
      A&A-01     -> A&A-01
    """
    paren = ctrl_id.find("(")
    if paren >= 0:
        return ctrl_id[:paren].strip()
    return ctrl_id.strip()


def _id_sort_key(ctrl_id, separator):
    """Build a sort key so enhancements sit immediately after their base.

    Returns a tuple (main_int, enhancement_ints, raw_suffix). A control with no
    leading integer after the separator (e.g., a free-form ID) falls back to
    string sort via the final tuple element.
    """
    if separator in ctrl_id:
        prefix, _, rest = ctrl_id.partition(separator)
    else:
        prefix, rest = ctrl_id, ""
    # rest looks like "2", "2(1)", "2(1)(a)", "01.1", etc.
    # Split off the base integer (everything before the first non-digit or "(").
    i = 0
    while i < len(rest) and rest[i].isdigit():
        i += 1
    try:
        main_num = int(rest[:i]) if i > 0 else -1
    except ValueError:
        main_num = -1
    remainder = rest[i:]
    enhancement_nums = tuple(int(m) for m in _ENH_RE.findall(remainder))
    # Trailing string keeps letter-suffixes (e.g. "(1)(a)") in deterministic order
    return (prefix, main_num, enhancement_nums, remainder)


# ---------------------------------------------------------------------------
# Chunk packing — size-aware combination and splitting
# ---------------------------------------------------------------------------

def _estimate_chunk_chars(controls, target_sup_labels):
    """Measure how many chars `controls` will occupy in an embedded target block.

    Uses build_target_reference output length — exact and cheap.
    """
    if not controls:
        return 0
    return len(build_target_reference(controls, target_sup_labels))


def _combine_small_families(families, max_per_chunk, max_chars=0,
                            separator="-", target_sup_labels=None):
    """Pack families into chunks respecting BOTH control-count and char budgets.

    - Families larger than max_per_chunk (or max_chars) get split via
      _split_family_by_range, preserving base-control + enhancements adjacency.
    - Smaller families are combined up to the same limits.
    """
    if target_sup_labels is None:
        target_sup_labels = ["Domain", "Title"]

    chunks = []
    current_names = []
    current_controls = []

    def _flush():
        nonlocal current_names, current_controls
        if current_controls:
            chunks.append(_make_chunk(current_names, current_controls))
            current_names = []
            current_controls = []

    def _exceeds(controls):
        if max_per_chunk > 0 and len(controls) > max_per_chunk:
            return True
        if max_chars > 0 and _estimate_chunk_chars(controls, target_sup_labels) > max_chars:
            return True
        return False

    for family_name, ctrls in families.items():
        # Does this single family on its own exceed either budget?
        if _exceeds(ctrls):
            _flush()
            sub_chunks = _split_family_by_range(
                family_name, ctrls, max_per_chunk, max_chars,
                separator, target_sup_labels,
            )
            chunks.extend(sub_chunks)
            continue

        # Would combining this family with what we've accumulated exceed budgets?
        if current_controls and _exceeds(current_controls + ctrls):
            _flush()

        current_names.append(family_name)
        current_controls.extend(ctrls)

    _flush()
    return chunks


def _split_family_by_range(family_name, ctrls, max_per_chunk, max_chars,
                           separator, target_sup_labels):
    """Split an oversize single family into numeric-range sub-chunks.

    Enhancements (AC-2(1), AC-2(1)(a)) are kept with their base control (AC-2)
    — the unit of packing is the "base group". Chunks are labeled with their
    first and last IDs so the model sees `Family: AC (AC-01..AC-14(3))`.
    """
    # Already sorted by _id_sort_key in _chunk_by_prefix/_chunk_by_column.
    base_groups = OrderedDict()
    for ctrl in ctrls:
        base = _base_id(ctrl["id"], separator)
        base_groups.setdefault(base, []).append(ctrl)

    sub_chunks = []
    current = []

    def _flush():
        nonlocal current
        if current:
            first_id = current[0]["id"]
            last_id = current[-1]["id"]
            name = _sanitize_name(f"{family_name}_{first_id}_to_{last_id}")
            label = f"Family: {family_name} ({first_id}..{last_id})"
            sub_chunks.append({"name": name, "label": label, "controls": list(current)})
            current = []

    for base, group in base_groups.items():
        # If a single base group alone busts the budget, emit it on its own and warn.
        projected_count = len(group)
        projected_chars = _estimate_chunk_chars(group, target_sup_labels)
        single_exceeds = (
            (max_per_chunk > 0 and projected_count > max_per_chunk)
            or (max_chars > 0 and projected_chars > max_chars)
        )
        if single_exceeds:
            _flush()
            first_id = group[0]["id"]
            last_id = group[-1]["id"]
            print(f"  WARNING: base control {base} + enhancements = "
                  f"{projected_count} controls / {projected_chars} chars — exceeds chunk budget; "
                  f"emitting as its own chunk")
            name = _sanitize_name(f"{family_name}_{first_id}_to_{last_id}")
            label = f"Family: {family_name} ({first_id}..{last_id})"
            sub_chunks.append({"name": name, "label": label, "controls": list(group)})
            continue

        # Would appending this base group to current exceed a budget? Flush first.
        if current:
            combined = current + group
            combined_count = len(combined)
            combined_chars = _estimate_chunk_chars(combined, target_sup_labels)
            if ((max_per_chunk > 0 and combined_count > max_per_chunk)
                    or (max_chars > 0 and combined_chars > max_chars)):
                _flush()
        current.extend(group)

    _flush()
    return sub_chunks


def _make_chunk(names, controls):
    """Create a chunk dict from a list of family names and their controls."""
    if len(names) == 1:
        label = f"Family: {names[0]}"
        name = _sanitize_name(names[0])
    else:
        label = f"Families: {', '.join(names)}"
        name = f"{_sanitize_name(names[0])}_to_{_sanitize_name(names[-1])}"
    return {"name": name, "label": label, "controls": controls}


# ---------------------------------------------------------------------------
# Source batching
# ---------------------------------------------------------------------------

def create_batches(controls, batch_cfg, source_cfg):
    """Split source controls into batches based on config."""
    group_by_idx = batch_cfg.get("group_by")
    batch_size = batch_cfg.get("batch_size", 8)

    # Find the supplemental label that maps to group_by index
    group_label = None
    if group_by_idx is not None:
        for sup in source_cfg["columns"].get("supplemental", []):
            if sup["index"] == group_by_idx:
                group_label = sup["label"]
                break

    if group_label:
        # Group by the specified column, then split large groups
        groups = OrderedDict()
        for ctrl in controls:
            key = ctrl.get(group_label, "Ungrouped")
            groups.setdefault(key, []).append(ctrl)

        batches = []
        for group_name, group_ctrls in groups.items():
            if len(group_ctrls) <= batch_size:
                batches.append({
                    "name": _sanitize_name(group_name),
                    "label": group_name,
                    "controls": group_ctrls,
                })
            else:
                # Split into sub-batches
                n_parts = math.ceil(len(group_ctrls) / batch_size)
                for part_idx in range(n_parts):
                    start = part_idx * batch_size
                    end = start + batch_size
                    chunk = group_ctrls[start:end]
                    batches.append({
                        "name": f"{_sanitize_name(group_name)}_{part_idx + 1}",
                        "label": f"{group_name} (part {part_idx + 1})",
                        "controls": chunk,
                    })
    else:
        # Sequential chunks
        batches = []
        n_batches = math.ceil(len(controls) / batch_size)
        for i in range(n_batches):
            start = i * batch_size
            end = start + batch_size
            chunk = controls[start:end]
            batches.append({
                "name": f"batch_{i + 1:02d}",
                "label": f"Batch {i + 1} ({chunk[0]['id']} - {chunk[-1]['id']})",
                "controls": chunk,
            })

    return batches


def _sanitize_name(name):
    """Convert a group name to a safe filename component."""
    return name.replace(" ", "_").replace("/", "-").replace("&", "and")[:40]


# ---------------------------------------------------------------------------
# Batch prompt generation
# ---------------------------------------------------------------------------

BATCH_TEMPLATE = """\
# Batch: {batch_label}
# Source: {source_name} -> Target: {target_name}
# Controls in this batch: {control_ids}
# Count: {count}
# Target scope: {target_scope}

---

{system_prompt}

---

## {source_name} Controls to Map

{source_controls_section}

---

## {target_name} Controls Reference — {target_scope} ({target_count} controls)

{target_reference}

---

## Required Output Format

Respond with ONLY valid JSON (no markdown code fences, no extra text).
The JSON object has one key per source control ID:

```
{{
  "{example_id}": {{
    "matches": [
      {{"target_id": "XXX-01", "confidence": "high", "rationale": "One sentence explanation."}},
      {{"target_id": "YYY-02", "confidence": "medium", "rationale": "One sentence explanation."}}
    ],
    "unique_to_source": false,
    "gap_rationale": ""
  }},
  ...
}}
```

**Save the output as:** `results/{result_filename}`
"""


def format_source_controls(controls, supplemental_labels, prompt_fields=None):
    """Format source controls for embedding in a batch prompt.

    `prompt_fields` is the subset of supplemental labels to embed. If None, all
    supplemental fields are embedded (legacy behavior). Description is always shown.
    """
    if prompt_fields is None:
        allowed = set(supplemental_labels)
    else:
        allowed = set(prompt_fields)

    lines = []
    for ctrl in controls:
        lines.append(f"### {ctrl['id']}")
        if "Title" in allowed and ctrl.get("Title"):
            lines.append(f"**Title**: {ctrl['Title']}")
        if "Domain" in allowed and ctrl.get("Domain"):
            lines.append(f"**Domain**: {ctrl['Domain']}")
        lines.append(f"**Description**: {ctrl['description']}")
        for label in supplemental_labels:
            if label in ("Domain", "Title"):
                continue
            if label not in allowed:
                continue
            value = ctrl.get(label, "")
            if value:
                lines.append(f"**{label}**: {value}")
        lines.append("")
    return "\n".join(lines)


def write_batch_file(batch, batch_dir, source_name, target_name,
                     target_reference, target_count, supplemental_labels,
                     system_prompt, target_scope="Full Catalog",
                     target_scope_detail=None, prompt_fields=None):
    """Write a self-contained batch prompt file."""
    controls = batch["controls"]
    control_ids = ", ".join(c["id"] for c in controls)
    example_id = controls[0]["id"]
    result_filename = f"{batch['name']}_result.json"

    if target_scope_detail is None:
        target_scope_detail = f"All {target_count} {target_name} controls"

    source_section = format_source_controls(controls, supplemental_labels, prompt_fields)

    formatted_system_prompt = system_prompt.format(
        source_name=source_name,
        target_name=target_name,
        target_scope_detail=target_scope_detail,
    )

    content = BATCH_TEMPLATE.format(
        batch_label=batch["label"],
        source_name=source_name,
        target_name=target_name,
        control_ids=control_ids,
        count=len(controls),
        target_scope=target_scope,
        target_scope_detail=target_scope_detail,
        source_controls_section=source_section,
        target_reference=target_reference,
        target_count=target_count,
        example_id=example_id,
        result_filename=result_filename,
        system_prompt=formatted_system_prompt,
    )

    filepath = batch_dir / f"{batch['name']}.md"
    filepath.write_text(content, encoding="utf-8")
    return filepath


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract controls and generate batch prompts")
    parser.add_argument("--config", default=str(PROJECT_DIR / "config.yaml"),
                        help="Path to config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)

    system_prompt = load_system_prompt(PROJECT_DIR / "CLAUDE.md")

    input_path = PROJECT_DIR / config["input_file"]
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        print(f"Place your Excel file at: {input_path}")
        sys.exit(1)

    # --- Extract controls ---
    print("=" * 60)
    print("Step 1: Extracting controls from Excel")
    print("=" * 60)

    source_cfg = config["source"]
    target_cfg = config["target"]

    source_controls = extract_controls(
        input_path, source_cfg["sheet_name"],
        source_cfg["columns"], source_cfg.get("header_row", 1),
    )
    print(f"  Extracted {len(source_controls)} {source_cfg['name']} controls")

    target_controls = extract_controls(
        input_path, target_cfg["sheet_name"],
        target_cfg["columns"], target_cfg.get("header_row", 1),
    )
    print(f"  Extracted {len(target_controls)} {target_cfg['name']} controls")

    # --- Write reference files ---
    print(f"\n{'=' * 60}")
    print("Step 2: Writing reference files")
    print("=" * 60)

    ref_dir = PROJECT_DIR / "reference"
    ref_dir.mkdir(exist_ok=True)

    source_sup_labels = [s["label"] for s in source_cfg["columns"].get("supplemental", [])]
    target_sup_labels = [s["label"] for s in target_cfg["columns"].get("supplemental", [])]

    # Which source fields to embed in batch prompts (defaults to Title+Domain if unset).
    # Description is always embedded; unlisted fields stay in reference/ only.
    source_prompt_fields = source_cfg.get("prompt_fields", ["Title", "Domain"])

    write_reference_file(
        ref_dir / "source_controls.md",
        source_cfg["name"], source_controls, source_sup_labels,
    )
    write_reference_file(
        ref_dir / "target_controls.md",
        target_cfg["name"], target_controls, target_sup_labels,
    )

    # --- Generate batch prompts ---
    print(f"\n{'=' * 60}")
    print("Step 3: Generating batch prompt files")
    print("=" * 60)

    batch_dir = PROJECT_DIR / "batches"
    batch_dir.mkdir(exist_ok=True)

    # Clear old batch files
    for old_file in batch_dir.glob("*.md"):
        old_file.unlink()

    # Create source batches
    source_batches = create_batches(source_controls, config["batching"], source_cfg)

    # Check if target chunking is enabled
    chunking_cfg = target_cfg.get("chunking", {})
    chunking_enabled = chunking_cfg.get("enabled", False)

    if chunking_enabled:
        # --- CHUNKED MODE: source_batch × target_chunk ---
        target_chunks = chunk_target_controls(target_controls, chunking_cfg, target_sup_labels)
        print(f"\n  Target chunking: ON ({len(target_chunks)} target groups)")
        for tc in target_chunks:
            families = [c["id"].split(chunking_cfg.get("separator", "-"))[0]
                        for c in tc["controls"]]
            unique_families = sorted(set(families))
            print(f"    {tc['label']}: {len(tc['controls'])} controls "
                  f"({', '.join(unique_families)})")

        total_planned = len(source_batches) * len(target_chunks)
        pad = len(str(total_planned))
        total_batches = 0
        for src_batch in source_batches:
            for tgt_chunk in target_chunks:
                total_batches += 1
                prefix = f"{total_batches:0{pad}d}_of_{total_planned}"
                cross_name = f"{prefix}_{src_batch['name']}_x_{tgt_chunk['name']}"
                cross_label = f"[{total_batches}/{total_planned}] {src_batch['label']} × {tgt_chunk['label']}"

                cross_batch = {
                    "name": cross_name,
                    "label": cross_label,
                    "controls": src_batch["controls"],
                }

                # Build target reference for just this chunk
                chunk_reference = build_target_reference(
                    tgt_chunk["controls"], target_sup_labels
                )

                scope_detail = (
                    f"Only {tgt_chunk['label']} — {len(tgt_chunk['controls'])} controls. "
                    f"Other target families are covered in separate batches."
                )

                filepath = write_batch_file(
                    cross_batch, batch_dir,
                    source_cfg["name"], target_cfg["name"],
                    chunk_reference, len(tgt_chunk["controls"]),
                    source_sup_labels,
                    system_prompt,
                    target_scope=tgt_chunk["label"],
                    target_scope_detail=scope_detail,
                    prompt_fields=source_prompt_fields,
                )

        print(f"\n  Generated {total_batches} batch files "
              f"({len(source_batches)} source × {len(target_chunks)} target)")

    else:
        # --- STANDARD MODE: source batches with full target catalog ---
        target_reference = build_target_reference(target_controls, target_sup_labels)

        total_planned = len(source_batches)
        pad = len(str(total_planned))
        total_batches = 0
        for i, batch in enumerate(source_batches, start=1):
            prefix = f"{i:0{pad}d}_of_{total_planned}"
            numbered_batch = {
                **batch,
                "name": f"{prefix}_{batch['name']}",
                "label": f"[{i}/{total_planned}] {batch['label']}",
            }
            filepath = write_batch_file(
                numbered_batch, batch_dir,
                source_cfg["name"], target_cfg["name"],
                target_reference, len(target_controls),
                source_sup_labels,
                system_prompt,
                prompt_fields=source_prompt_fields,
            )
            ids = ", ".join(c["id"] for c in batch["controls"])
            print(f"  {filepath.name}: {len(batch['controls'])} controls ({ids})")
            total_batches += 1

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print("Setup Complete")
    print("=" * 60)
    print(f"  Source controls:  {len(source_controls)} ({source_cfg['name']})")
    print(f"  Target controls:  {len(target_controls)} ({target_cfg['name']})")
    if chunking_enabled:
        print(f"  Target chunks:    {len(target_chunks)}")
    print(f"  Batch files:      {total_batches}")
    print(f"  Reference files:  reference/source_controls.md, reference/target_controls.md")
    print(f"\nNext steps:")
    print(f"  1. Open each batch file in batches/")
    print(f"  2. Tell Claude: 'Read batches/<file>.md and follow its instructions'")
    print(f"  3. Save output to results/<batch_name>_result.json")
    print(f"  4. When all batches are done, run: python scripts/merge.py")


if __name__ == "__main__":
    main()
