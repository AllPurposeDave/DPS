"""
Shared utilities for the DPS pre-processing pipeline.

Common functions used across all pipeline scripts.
Updated to support the unified dps_config.yaml.

REQUIREMENTS:
  pip install python-docx pyyaml
  Python 3.10 or later (uses X | Y type hint syntax)

FAILURE POINT: If you see "TypeError: unsupported operand type(s) for |"
on import, your Python version is below 3.10. Upgrade Python.
"""
# pip install python-docx pyyaml

import argparse
import glob
import os
import re
import sys
from pathlib import Path


def load_config(config_path: str | None = None) -> dict:
    """
    Load the unified dps_config.yaml.

    Search order:
      1. Explicit path passed via --config
      2. ./dps_config.yaml (current directory)
      3. ../dps_config.yaml (parent directory — for running from scripts/)

    Returns the parsed YAML dict, or an empty dict if no config is found.
    """
    import yaml

    search_paths = []
    if config_path:
        search_paths.append(config_path)
    search_paths.extend([
        os.path.join(os.getcwd(), "dps_config.yaml"),
        os.path.join(os.getcwd(), "..", "dps_config.yaml"),
    ])

    for path in search_paths:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
            # Store the resolved config directory for relative path resolution
            config["_config_dir"] = os.path.dirname(os.path.abspath(path))
            return config

    return {}


def resolve_path(config: dict, relative_path: str) -> str:
    """
    Resolve a relative path from the config against the config file's directory.
    If the path is already absolute, return it as-is.
    """
    if os.path.isabs(relative_path):
        return relative_path
    config_dir = config.get("_config_dir", os.getcwd())
    return os.path.normpath(os.path.join(config_dir, relative_path))


def get_input_dir(config: dict, cli_override: str | None = None) -> str:
    """
    Get the input directory path, with CLI override taking priority.

    Priority: CLI arg > config input.directory > ./input
    """
    if cli_override:
        return cli_override
    input_dir = config.get("input", {}).get("directory", "./input")
    return resolve_path(config, input_dir)


def get_output_dir(config: dict, step_key: str, cli_override: str | None = None) -> str:
    """
    Get the output directory for a specific pipeline step.

    Args:
        config: Parsed config dict
        step_key: Key in config output section (e.g., "profiler", "cross_references")
        cli_override: CLI argument that takes priority over config

    Priority: CLI arg > config output.<step_key>.directory > ./output
    """
    if cli_override:
        return cli_override
    output_root = config.get("output", {}).get("directory", "./output")
    step_subdir = config.get("output", {}).get(step_key, {}).get("directory", "")
    full_path = os.path.join(output_root, step_subdir) if step_subdir else output_root
    return resolve_path(config, full_path)


def setup_argparse(description: str) -> argparse.ArgumentParser:
    """
    Create an argument parser with standard --config, input_dir, and output_dir args.

    All scripts now support:
      python <script>.py --config ../dps_config.yaml         # config-driven
      python <script>.py <input_dir> <output_dir>            # standalone (legacy)
      python <script>.py --config ../dps_config.yaml ./docs  # config + override

    FAILURE POINT: Passing a file path instead of a directory will cause
    downstream glob calls to find nothing and exit with "No .docx files found".
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--config",
        default=None,
        help="Path to dps_config.yaml (auto-detected if omitted)",
    )
    parser.add_argument(
        "input_dir",
        nargs="?",
        default=None,
        help="Directory containing .docx files (overrides config)",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default=None,
        help="Directory for output files (overrides config)",
    )
    return parser


def iter_docx_files(input_dir: str, config: dict | None = None) -> list[str]:
    """
    Return sorted list of .docx file paths in input_dir.
    Skips files matching exclude patterns from config.

    NOTE: Only scans the top-level directory by default.
    Set input.recursive: true in config to scan sub-folders.

    TWEAK: To scan sub-folders without config, change the pattern to
    include "**" and add recursive=True to glob.glob().

    FAILURE POINT: Returns empty list if input_dir does not exist or
    contains no .docx files. The calling script will print a warning and exit.
    """
    config = config or {}
    input_cfg = config.get("input", {})
    file_pattern = input_cfg.get("pattern", "*.docx")
    recursive = input_cfg.get("recursive", False)
    exclude_patterns = input_cfg.get("exclude_patterns", ["~$"])

    if recursive:
        pattern = os.path.join(input_dir, "**", file_pattern)
        files = glob.glob(pattern, recursive=True)
    else:
        pattern = os.path.join(input_dir, file_pattern)
        files = glob.glob(pattern)

    # Filter out excluded files
    filtered = []
    for f in files:
        basename = os.path.basename(f)
        skip = False
        for exc in exclude_patterns:
            if exc.lower() in basename.lower():
                skip = True
                break
        if not skip:
            filtered.append(f)

    filtered.sort()
    return filtered


def is_heading_style(style) -> bool:
    """
    Check if a paragraph style is a standard Word heading style (Heading 1-9).

    IMPORTANT: This only recognises the exact names "Heading 1" through "Heading 9".
    Custom styles like "Policy Heading 1" return False here — they are handled
    separately by the custom_style_map in dps_config.yaml.

    TWEAK: To also accept "Title" as a heading, change the regex to:
        r"^(Heading \d|Title)$"
    """
    if style is None:
        return False
    name = style.name if hasattr(style, "name") else str(style)
    return bool(re.match(r"^Heading \d$", name))


def get_heading_level(style) -> int | None:
    """
    Return the heading level (1-9) if the style is a standard heading, else None.

    Returns None for custom styles, Normal, Body Text, etc.
    Used by section_splitter.py to find split points.
    """
    if style is None:
        return None
    name = style.name if hasattr(style, "name") else str(style)
    match = re.match(r"^Heading (\d)$", name)
    if match:
        return int(match.group(1))
    return None


def find_parent_heading(paragraphs, index: int) -> str:
    """
    Walk backward from paragraph at `index` to find the nearest
    Heading 1 or Heading 2 paragraph. Returns the heading text,
    or "(No heading found)" if none exists above.

    Used by cross_reference_extractor.py to label which section a
    cross-reference appears in.

    TWEAK: Change `level <= 2` to `level <= 3` to also use Heading 3
    paragraphs as parent section labels.
    """
    for i in range(index - 1, -1, -1):
        level = get_heading_level(paragraphs[i].style)
        if level is not None and level <= 2:
            return paragraphs[i].text.strip()
    return "(No heading found)"


def is_paragraph_bold(paragraph) -> bool:
    """
    Check if a paragraph is bold. Checks both paragraph-level formatting
    and run-level formatting. A paragraph counts as bold if:
    - The paragraph font (via its style) is bold, OR
    - ALL runs in the paragraph are bold (and there is at least one run)

    FAILURE POINT: Mixed bold paragraphs (some runs bold, some not) return
    False because the ALL-runs check fails.

    TWEAK: To treat a paragraph as bold if ANY run is bold (more permissive),
    change the last line to:
        return any(run.bold for run in runs)
    """
    # Check paragraph-level bold (set via the style's font, not individual runs)
    if paragraph.paragraph_format and hasattr(paragraph, "style"):
        pf = paragraph.style.font if hasattr(paragraph.style, "font") else None
        if pf and pf.bold:
            return True

    # Check run-level bold: all runs must be bold
    runs = paragraph.runs
    if not runs:
        return False
    return all(run.bold for run in runs)


def sanitize_filename(text: str, max_len: int = 50) -> str:
    """
    Clean text for safe use as a filename component.
    Removes special characters, collapses whitespace, truncates.

    TWEAK: Adjust max_len if output filenames are being truncated too aggressively.
        sanitize_filename(text, max_len=80)  # allow longer names

    FAILURE POINT: If two headings produce the same sanitized name,
    section_splitter.py will silently overwrite the first output file.
    Check split_manifest.csv for duplicate sub_doc_filename values.
    """
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    if len(clean) > max_len:
        clean = clean[:max_len].rstrip()
    return clean


def paragraph_char_count(paragraph) -> int:
    """Return the character count of a paragraph's text."""
    return len(paragraph.text)


def ensure_output_dir(output_dir: str) -> None:
    """
    Create the output directory if it doesn't exist.
    Safe to call even if the directory already exists (exist_ok=True).

    FAILURE POINT: If the path is on a network drive or read-only location,
    os.makedirs will raise PermissionError. Run from a local drive if possible.
    """
    os.makedirs(output_dir, exist_ok=True)
