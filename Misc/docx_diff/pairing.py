"""Pair .docx files between two folders.

Matching ladder:
    1. Exact filename           -> MATCHED
    2. Normalized filename      -> MATCHED_NORMALIZED
    3. Fuzzy (SequenceMatcher)  -> MATCHED_FUZZY
    4. Unmatched                -> ORPHAN_DIFF1 / ORPHAN_DIFF2
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

MATCHED = "MATCHED"
MATCHED_NORMALIZED = "MATCHED_NORMALIZED"
MATCHED_FUZZY = "MATCHED_FUZZY"
ORPHAN_DIFF1 = "ORPHAN_DIFF1"
ORPHAN_DIFF2 = "ORPHAN_DIFF2"

_SUFFIX_RE = re.compile(
    r"\s+(v\d+|\(\d+\)|final|draft|copy|latest)$",
    flags=re.IGNORECASE,
)
_SEP_RE = re.compile(r"[-_]+")
_WS_RE = re.compile(r"\s+")


@dataclass
class Pair:
    name: str
    path1: Path | None
    path2: Path | None
    match_kind: str
    similarity: float = 1.0


def normalize(filename: str) -> str:
    """Normalize a docx filename for pairing. Lowercases, collapses separators,
    and strips trailing version suffixes so that e.g. ``Policy_v2.docx`` and
    ``Policy v2.docx`` collide, and ``Policy - Final.docx`` collides with
    ``Policy.docx``.
    """
    stem = Path(filename).stem
    stem = stem.lower()
    stem = _SEP_RE.sub(" ", stem)
    stem = _WS_RE.sub(" ", stem).strip()
    prev = None
    while prev != stem:
        prev = stem
        stem = _SUFFIX_RE.sub("", stem).strip()
    return stem


def _list_docx(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    return sorted(
        p for p in folder.iterdir()
        if p.is_file() and p.suffix.lower() == ".docx" and not p.name.startswith("~$")
    )


def pair_folders(folder1: Path, folder2: Path, fuzzy_threshold: float = 0.9) -> list[Pair]:
    files1 = _list_docx(folder1)
    files2 = _list_docx(folder2)

    pairs: list[Pair] = []
    by_name1 = {p.name: p for p in files1}
    by_name2 = {p.name: p for p in files2}

    matched1: set[str] = set()
    matched2: set[str] = set()

    for name, path1 in by_name1.items():
        if name in by_name2:
            pairs.append(Pair(name, path1, by_name2[name], MATCHED))
            matched1.add(name)
            matched2.add(name)

    norm1 = {normalize(n): n for n in by_name1 if n not in matched1}
    norm2 = {normalize(n): n for n in by_name2 if n not in matched2}
    for key, n1 in list(norm1.items()):
        if key in norm2:
            n2 = norm2[key]
            display = n1 if n1 == n2 else f"{n1}  ≈  {n2}"
            pairs.append(Pair(display, by_name1[n1], by_name2[n2], MATCHED_NORMALIZED))
            matched1.add(n1)
            matched2.add(n2)
            del norm1[key]
            del norm2[key]

    rem1 = [(norm, by_name1[name]) for norm, name in norm1.items()]
    rem2 = [(norm, by_name2[name]) for norm, name in norm2.items()]
    used2: set[int] = set()
    for norm_a, path_a in rem1:
        best_idx = -1
        best_ratio = fuzzy_threshold
        for idx, (norm_b, _) in enumerate(rem2):
            if idx in used2:
                continue
            r = SequenceMatcher(None, norm_a, norm_b).ratio()
            if r > best_ratio:
                best_ratio = r
                best_idx = idx
        if best_idx >= 0:
            _, path_b = rem2[best_idx]
            used2.add(best_idx)
            display = f"{path_a.name}  ≈  {path_b.name}"
            pairs.append(Pair(display, path_a, path_b, MATCHED_FUZZY, best_ratio))
            matched1.add(path_a.name)
            matched2.add(path_b.name)

    for name, path1 in by_name1.items():
        if name not in matched1:
            pairs.append(Pair(name, path1, None, ORPHAN_DIFF1))
    for name, path2 in by_name2.items():
        if name not in matched2:
            pairs.append(Pair(name, None, path2, ORPHAN_DIFF2))

    pairs.sort(key=lambda p: (p.match_kind, p.name.lower()))
    return pairs
