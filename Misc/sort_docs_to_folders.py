#!/usr/bin/env python3
"""Move each .docx in this folder into its assigned Folder 1..5."""

# ============================================================
# CONFIG — Edit this mapping only.
# Each entry: "<docx filename>": "<destination folder>"
# Destination must be one of: "Folder 1".."Folder 5".
# Filenames are matched exactly (case-sensitive, include .docx).
# Any .docx not listed here is left in place and reported.
# ============================================================
DOC_TO_FOLDER = {
    # "Profile_Report_A.docx": "Folder 1",
    # "Profile_Report_B.docx": "Folder 2",
}
# ============================================================

from pathlib import Path
import shutil
import sys

FOLDERS = ["Folder 1", "Folder 2", "Folder 3", "Folder 4", "Folder 5"]


def main() -> int:
    folder = Path(__file__).resolve().parent

    bad = {name: dest for name, dest in DOC_TO_FOLDER.items() if dest not in FOLDERS}
    if bad:
        print("Invalid destinations in DOC_TO_FOLDER (must be one of Folder 1..5):")
        for name, dest in bad.items():
            print(f"  {name} -> {dest!r}")
        return 2

    docx_files = sorted(folder.glob("*.docx"))
    if not docx_files:
        print(f"No .docx files found in {folder}")
        return 0

    moved = 0
    skipped = []
    for doc in docx_files:
        target = DOC_TO_FOLDER.get(doc.name)
        if not target:
            skipped.append(doc.name)
            continue
        dest_dir = folder / target
        dest_dir.mkdir(exist_ok=True)
        shutil.move(str(doc), str(dest_dir / doc.name))
        print(f"Moved {doc.name} -> {target}")
        moved += 1

    print(f"Moved {moved}, skipped {len(skipped)}")
    if skipped:
        print("Unmapped: " + ", ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
