#!/usr/bin/env python3
"""For each *.md file in this folder, write a blank <filename>.csv with a fixed header."""

import csv
from pathlib import Path
import sys

COLUMNS = [
    "section_header",
    "control_id",
    "control_name",
    "baseline",
    "control_description",
    "supplemental_guidance",
    "miscellaneous",
    "purpose",
    "scope",
    "applicability",
    "compliance_date",
    "published_url",
]


def main() -> int:
    folder = Path(__file__).resolve().parent
    md_files = sorted(folder.glob("*.md"))

    if not md_files:
        print(f"No Markdown files found in {folder}")
        return 1

    for md in md_files:
        out = md.with_suffix(".csv")
        with out.open("w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(COLUMNS)
        print(f"Wrote {out.name}")

    print(f"Created {len(md_files)} placeholder CSV file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
