#!/usr/bin/env python3
"""
DPS — Document Processing System — Pipeline Runner
=====================================================

One command to run the entire pipeline, or pick individual steps.

HOW IT WORKS:
    1. Reads dps_config.yaml for all paths and settings
    2. Runs each enabled step in order (0 → 5)
    3. Each step's script reads from the input/ folder (or previous step's output)
    4. All outputs land in numbered sub-folders under output/

USAGE:
    python run_pipeline.py                    Run all enabled steps
    python run_pipeline.py --step 0           Run only Step 0 (profiler)
    python run_pipeline.py --step 1-3         Run Steps 1 through 3
    python run_pipeline.py --step 2,4         Run Steps 2 and 4
    python run_pipeline.py --list             Show all steps and their status
    python run_pipeline.py --config alt.yaml  Use a different config file

PIPELINE ORDER:
    Step 0  Document Profiler          → output/0 - profiler/
    Step 1  Cross-Reference Extractor  → output/1 - cross_references/
    Step 2  Heading Style Fixer        → output/2 - heading_fixes/
    Step 3  Section Splitter           → output/3 - split_documents/
    Step 4  Control Extractor          → output/4 - controls/
    Step 5  Word Counter               → output/5 - reports/

REQUIREMENTS:
    pip install -r requirements.txt
    Python 3.10 or later
"""

import argparse
import os
import subprocess
import sys
import time

import yaml


def load_config(config_path: str) -> dict:
    """Load and validate the config file."""
    if not os.path.isfile(config_path):
        print(f"ERROR: Config file not found: {config_path}")
        print("Expected dps_config.yaml in the project root.")
        print("FIX: Copy or create dps_config.yaml (see the template in this repo).")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not config or not isinstance(config, dict):
        print(f"ERROR: Config file is empty or invalid: {config_path}")
        sys.exit(1)

    return config


def parse_step_arg(step_str: str) -> list[int]:
    """
    Parse --step argument into a list of step numbers.

    Supports:
        "0"     → [0]
        "1-3"   → [1, 2, 3]
        "2,4"   → [2, 4]
        "0,2-4" → [0, 2, 3, 4]
    """
    steps = set()
    for part in step_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-", 1)
            steps.update(range(int(start), int(end) + 1))
        else:
            steps.add(int(part))
    return sorted(steps)


def get_step_definitions(config: dict, config_path: str) -> list[dict]:
    """
    Build the full list of pipeline steps with their commands and directories.
    Each step knows how to invoke its script with the right arguments.
    """
    config_dir = os.path.dirname(os.path.abspath(config_path))
    scripts_dir = os.path.join(config_dir, "scripts")
    abs_config = os.path.abspath(config_path)

    input_dir = os.path.join(config_dir, config.get("input", {}).get("directory", "./input"))
    output_root = os.path.join(config_dir, config.get("output", {}).get("directory", "./output"))

    def out(step_key):
        subdir = config.get("output", {}).get(step_key, {}).get("directory", "")
        return os.path.join(output_root, subdir)

    steps = [
        {
            "number": 0,
            "name": "Step 0 — Document Profiler",
            "description": "Scan all docs, extract metadata, classify types, score priority",
            "script": os.path.join(scripts_dir, "policy_profiler.py"),
            "args": ["--config", abs_config, "--input", input_dir, "--output", out("profiler")],
            "enabled": True,
        },
        {
            "number": 1,
            "name": "Step 1 — Cross-Reference Extractor",
            "description": "Capture all cross-refs BEFORE any structural changes",
            "script": os.path.join(scripts_dir, "cross_reference_extractor.py"),
            "args": ["--config", abs_config, input_dir, out("cross_references")],
            "enabled": True,
        },
        {
            "number": 2,
            "name": "Step 2 — Heading Style Fixer",
            "description": "Convert fake bold headings to real Word Heading styles",
            "script": os.path.join(scripts_dir, "heading_style_fixer.py"),
            "args": ["--config", abs_config, input_dir, out("heading_fixes")],
            "enabled": True,
        },
        {
            "number": 3,
            "name": "Step 3 — Section Splitter",
            "description": "Split fixed docs at H1 boundaries into sub-documents",
            "script": os.path.join(scripts_dir, "section_splitter.py"),
            "args": ["--config", abs_config, out("heading_fixes"), out("split_documents")],
            "enabled": True,
        },
        {
            "number": 4,
            "name": "Step 4 — Control Extractor",
            "description": "Extract structured control data from compliance docs",
            "script": os.path.join(scripts_dir, "extract_controls.py"),
            "args": ["--config", abs_config, input_dir, out("controls")],
            "enabled": True,
        },
        {
            "number": 5,
            "name": "Step 5 — Word Counter",
            "description": "Count words in final sub-documents (QA validation)",
            "script": os.path.join(scripts_dir, "word_counter.py"),
            "args": ["--config", abs_config, out("split_documents"), out("reports")],
            "enabled": True,
        },
    ]

    # Override enabled status from config
    pipeline_steps = config.get("pipeline", {}).get("steps", [])
    for i, step_cfg in enumerate(pipeline_steps):
        if i < len(steps):
            steps[i]["enabled"] = step_cfg.get("enabled", True)

    return steps


def list_steps(steps: list[dict]):
    """Print all pipeline steps and their enabled status."""
    print()
    print("=" * 70)
    print("  DPS Pipeline Steps")
    print("=" * 70)
    for step in steps:
        status = "ENABLED" if step["enabled"] else "DISABLED"
        marker = "  " if step["enabled"] else "  "
        print(f"  [{step['number']}] {step['name']:<45s} {status}")
        print(f"       {step['description']}")
    print()
    print("  Run all:          python run_pipeline.py")
    print("  Run one:          python run_pipeline.py --step 2")
    print("  Run range:        python run_pipeline.py --step 1-3")
    print("  Run selection:    python run_pipeline.py --step 0,2,4")
    print("=" * 70)
    print()


def run_step(step: dict, python_exe: str) -> bool:
    """
    Run a single pipeline step as a subprocess.
    Returns True if successful, False if failed.
    """
    print()
    print("=" * 70)
    print(f"  RUNNING: {step['name']}")
    print(f"  {step['description']}")
    print("=" * 70)

    cmd = [python_exe, step["script"]] + step["args"]

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=os.path.dirname(step["script"]),
            capture_output=False,
            text=True,
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            print(f"\n  [{step['name']}] completed in {elapsed:.1f}s")
            return True
        else:
            print(f"\n  [{step['name']}] FAILED (exit code {result.returncode}) after {elapsed:.1f}s")
            return False

    except FileNotFoundError:
        print(f"\n  ERROR: Script not found: {step['script']}")
        print("  FIX: Make sure all scripts are in the scripts/ folder.")
        return False
    except Exception as e:
        print(f"\n  ERROR running {step['name']}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="DPS Pipeline Runner — run the full document processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", "-c",
        default="dps_config.yaml",
        help="Path to dps_config.yaml (default: dps_config.yaml in current folder)",
    )
    parser.add_argument(
        "--step", "-s",
        default=None,
        help="Step(s) to run: 0, 1-3, 2,4 (default: all enabled steps)",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all steps and their enabled status, then exit",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    steps = get_step_definitions(config, args.config)

    if args.list:
        list_steps(steps)
        return

    # Determine which steps to run
    if args.step is not None:
        requested = parse_step_arg(args.step)
        steps_to_run = [s for s in steps if s["number"] in requested]
        if not steps_to_run:
            print(f"ERROR: No valid steps found for --step {args.step}")
            print(f"Valid step numbers: 0-{len(steps)-1}")
            sys.exit(1)
    else:
        steps_to_run = [s for s in steps if s["enabled"]]

    if not steps_to_run:
        print("No steps to run. Use --list to see available steps.")
        return

    # Banner
    print()
    print("=" * 70)
    print("  DPS — Document Processing System")
    print("=" * 70)
    print(f"  Config:  {os.path.abspath(args.config)}")
    print(f"  Input:   {os.path.abspath(config.get('input', {}).get('directory', './input'))}")
    print(f"  Output:  {os.path.abspath(config.get('output', {}).get('directory', './output'))}")
    print(f"  Steps:   {', '.join(str(s['number']) for s in steps_to_run)}")
    print("=" * 70)

    # Verify input directory exists
    input_dir = config.get("input", {}).get("directory", "./input")
    if not os.path.isdir(input_dir):
        print(f"\nERROR: Input directory does not exist: {os.path.abspath(input_dir)}")
        print("FIX: Create the input/ folder and copy your .docx files into it.")
        sys.exit(1)

    # Run each step
    python_exe = sys.executable
    results = {}
    total_start = time.time()

    for step in steps_to_run:
        success = run_step(step, python_exe)
        results[step["number"]] = success

        if not success:
            print(f"\n  Step {step['number']} failed. Stopping pipeline.")
            print("  Fix the error above, then re-run with:")
            print(f"    python run_pipeline.py --step {step['number']}")
            break

    total_elapsed = time.time() - total_start

    # Summary
    print()
    print("=" * 70)
    print("  PIPELINE SUMMARY")
    print("=" * 70)
    for step_num, success in results.items():
        status = "OK" if success else "FAILED"
        step_name = next(s["name"] for s in steps if s["number"] == step_num)
        print(f"  [{step_num}] {step_name:<45s} {status}")
    print(f"\n  Total time: {total_elapsed:.1f}s")

    failed = [n for n, ok in results.items() if not ok]
    if failed:
        print(f"\n  {len(failed)} step(s) failed. Check the output above for details.")
        sys.exit(1)
    else:
        output_dir = os.path.abspath(config.get("output", {}).get("directory", "./output"))
        print(f"\n  All steps completed successfully!")
        print(f"  Results are in: {output_dir}")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
