"""CLI entry point for docx_diff.

Usage:
    python "Misc/docx_diff/docx_diff.py"
    python "Misc/docx_diff/docx_diff.py" --folder1 A --folder2 B --output report.xlsx
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pairing import (
    MATCHED, MATCHED_FUZZY, MATCHED_NORMALIZED,
    ORPHAN_DIFF1, ORPHAN_DIFF2, pair_folders,
)
import metadata as metadata_mod
import text_extract
import text_diff as text_diff_mod
import tracked_changes
import comments as comments_mod
import signals as signals_mod
from excel_writer import PairResult, write_workbook


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mature .docx diff checker.")
    parser.add_argument("--folder1", type=Path, default=SCRIPT_DIR / "Diff 1",
                        help="First folder of .docx files (default: ./Diff 1).")
    parser.add_argument("--folder2", type=Path, default=SCRIPT_DIR / "Diff 2",
                        help="Second folder of .docx files (default: ./Diff 2).")
    parser.add_argument("--output", type=Path, default=None,
                        help="Output .xlsx path (default: docx_diff_report_<timestamp>.xlsx).")
    parser.add_argument("--fuzzy-threshold", type=float, default=0.9,
                        help="SequenceMatcher ratio threshold for fuzzy filename pairing.")
    parser.add_argument("--verbose", action="store_true",
                        help="Print per-file progress.")
    return parser.parse_args(argv)


def _analyze_pair(pair, verbose: bool) -> PairResult:
    result = PairResult(pair=pair)
    if verbose:
        print(f"  - {pair.name} [{pair.match_kind}]")
    if pair.path1:
        result.meta1 = metadata_mod.extract(pair.path1)
    if pair.path2:
        result.meta2 = metadata_mod.extract(pair.path2)
    if pair.path1 and pair.path2:
        ext1 = text_extract.extract(pair.path1)
        ext2 = text_extract.extract(pair.path2)
        result.para_diff = text_diff_mod.diff(ext1.paragraphs, ext2.paragraphs)
        tc1 = tracked_changes.extract(pair.path1)
        tc2 = tracked_changes.extract(pair.path2)
        result.tracked = tracked_changes.diff(tc1, tc2)
        com1 = comments_mod.extract(pair.path1)
        com2 = comments_mod.extract(pair.path2)
        result.comments = comments_mod.diff(com1, com2)
        result.signals = signals_mod.compute(
            result.meta1, result.meta2, tc1, tc2, com1, com2,
        )
    return result


def _summarize(results: list[PairResult]) -> tuple[int, int, int, int]:
    identical = 0
    changed = 0
    orphans = 0
    errors = 0
    for r in results:
        kind = r.pair.match_kind
        if kind in (ORPHAN_DIFF1, ORPHAN_DIFF2):
            orphans += 1
            continue
        if not (r.meta1 and r.meta2):
            errors += 1
            continue
        archive_eq = r.meta1.hashes.get("archive_sha256") == r.meta2.hashes.get("archive_sha256")
        has_diffs = bool(r.para_diff) or (
            r.tracked and (r.tracked.only_in_1 or r.tracked.only_in_2)
        ) or (
            r.comments and (r.comments.only_in_1 or r.comments.only_in_2)
        )
        if archive_eq and not has_diffs:
            identical += 1
        else:
            changed += 1
    return identical, changed, orphans, errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    folder1: Path = args.folder1
    folder2: Path = args.folder2
    if not folder1.is_dir():
        print(f"Error: folder1 not found: {folder1}", file=sys.stderr)
        return 2
    if not folder2.is_dir():
        print(f"Error: folder2 not found: {folder2}", file=sys.stderr)
        return 2

    output: Path = args.output or (
        SCRIPT_DIR / f"docx_diff_report_{datetime.now().strftime('%Y-%m-%d_%H%M')}.xlsx"
    )

    pairs = pair_folders(folder1, folder2, fuzzy_threshold=args.fuzzy_threshold)
    if not pairs:
        print(f"No .docx files found in {folder1} or {folder2}.")
        return 1

    if args.verbose:
        print(f"Pairing {len(pairs)} entries:")
    results = [_analyze_pair(p, args.verbose) for p in pairs]

    write_workbook(results, output)

    identical, changed, orphans, errors = _summarize(results)
    print(
        f"{len(pairs)} entries · {identical} identical · {changed} changed · "
        f"{orphans} orphans · {errors} errors → {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
