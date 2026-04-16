#!/usr/bin/env python3
"""Merge all CSV files in this folder into a single Excel workbook."""

from pathlib import Path
import sys

import pandas as pd


def main() -> int:
    folder = Path(__file__).resolve().parent
    csv_files = sorted(folder.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {folder}")
        return 1

    frames = []
    for csv in csv_files:
        print(f"Reading {csv.name}")
        df = pd.read_csv(csv)
        df.insert(0, "source_file", csv.name)
        frames.append(df)

    merged = pd.concat(frames, ignore_index=True)

    output = folder / "merged.xlsx"
    merged.to_excel(output, index=False)
    print(f"Wrote {len(merged)} rows from {len(csv_files)} files to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
