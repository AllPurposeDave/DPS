"""Compute "which is newer" signals for a file pair.

Every signal is a row showing Diff 1 value, Diff 2 value, and which side the
signal points to (or tie / missing / n/a). No composite score, no verdict.
The reviewer reads the agreement/disagreement pattern and decides.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from metadata import Metadata
from tracked_changes import TrackedChange, latest_date as latest_tc_date
from comments import Comment, latest_date as latest_comment_date

DIFF1 = "Diff 1"
DIFF2 = "Diff 2"
TIE = "tie"
MISSING = "missing"
NA = "n/a"


@dataclass
class Signal:
    name: str
    diff1_value: Any
    diff2_value: Any
    points_to: str
    note: str = ""


def _points(v1: Any, v2: Any, *, larger_is_newer: bool = True) -> str:
    if v1 is None and v2 is None:
        return MISSING
    if v1 is None:
        return DIFF2 if larger_is_newer else DIFF1
    if v2 is None:
        return DIFF1 if larger_is_newer else DIFF2
    if v1 == v2:
        return TIE
    if larger_is_newer:
        return DIFF1 if v1 > v2 else DIFF2
    return DIFF1 if v1 < v2 else DIFF2


def _num(val: Any) -> int | float | None:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return val
    try:
        return int(val)
    except (TypeError, ValueError):
        try:
            return float(val)
        except (TypeError, ValueError):
            return None


def _dt(val: Any) -> datetime | None:
    if isinstance(val, datetime):
        return val
    return None


def compute(
    meta1: Metadata,
    meta2: Metadata,
    tc1: list[TrackedChange],
    tc2: list[TrackedChange],
    com1: list[Comment],
    com2: list[Comment],
) -> list[Signal]:
    out: list[Signal] = []

    # --- Timestamp signals ---
    for key in ("modified", "created"):
        v1 = _dt(meta1.core.get(key))
        v2 = _dt(meta2.core.get(key))
        out.append(Signal(f"core.{key}", v1, v2, _points(v1, v2)))

    # --- Save counter ---
    r1 = _num(meta1.core.get("revision"))
    r2 = _num(meta2.core.get("revision"))
    out.append(Signal("core.revision", r1, r2, _points(r1, r2)))

    # --- lastModifiedBy (identity, not newer/older) ---
    l1 = meta1.core.get("lastModifiedBy")
    l2 = meta2.core.get("lastModifiedBy")
    if l1 is None and l2 is None:
        points = MISSING
    elif l1 == l2:
        points = TIE
    else:
        points = NA
    out.append(Signal("core.lastModifiedBy", l1, l2, points,
                      note="identity check only; no newer/older judgment"))

    # --- app.TotalTime (cumulative edit minutes) ---
    t1 = _num(meta1.app.get("TotalTime"))
    t2 = _num(meta2.app.get("TotalTime"))
    out.append(Signal("app.TotalTime (edit minutes)", t1, t2, _points(t1, t2)))

    # --- app.AppVersion ---
    av1 = meta1.app.get("AppVersion")
    av2 = meta2.app.get("AppVersion")
    if av1 is None and av2 is None:
        points = MISSING
    elif av1 == av2:
        points = TIE
    else:
        points = NA
    out.append(Signal("app.AppVersion", av1, av2, points,
                      note="identity check only; version strings aren't reliably ordered"))

    # --- Size hints ---
    for f in ("Words", "Pages", "Characters"):
        v1 = _num(meta1.app.get(f))
        v2 = _num(meta2.app.get(f))
        points = _points(v1, v2)
        out.append(Signal(f"app.{f}", v1, v2, points,
                          note="size delta is a hint only (growth doesn't always mean newer)"))

    # --- Unique rsid count (more save sessions) ---
    r1 = len(meta1.rsids) if meta1.rsids else None
    r2 = len(meta2.rsids) if meta2.rsids else None
    out.append(Signal("unique w:rsid count", r1, r2, _points(r1, r2)))

    # --- Last tracked-change date ---
    t1 = latest_tc_date(tc1)
    t2 = latest_tc_date(tc2)
    out.append(Signal("last tracked-change date", t1, t2, _points(t1, t2)))

    # --- Last comment date ---
    c1 = latest_comment_date(com1)
    c2 = latest_comment_date(com2)
    out.append(Signal("last comment date", c1, c2, _points(c1, c2)))

    # --- Filesystem mtime ---
    m1 = _dt(meta1.fs.get("mtime"))
    m2 = _dt(meta2.fs.get("mtime"))
    out.append(Signal("filesystem mtime", m1, m2, _points(m1, m2),
                      note="filesystem mtime can be overwritten by copy operations"))

    # --- Hash equality ---
    h1 = meta1.hashes.get("archive_sha256")
    h2 = meta2.hashes.get("archive_sha256")
    out.append(Signal("archive SHA-256",
                      h1, h2,
                      TIE if h1 == h2 and h1 is not None else NA,
                      note="equal means byte-identical files"))

    d1 = meta1.hashes.get("document_xml_sha256")
    d2 = meta2.hashes.get("document_xml_sha256")
    out.append(Signal("normalized document.xml SHA-256",
                      d1, d2,
                      TIE if d1 == d2 and d1 is not None else NA,
                      note="equal means identical body content (ignoring cosmetic XML reserialization)"))

    return out


def tally(signals: list[Signal]) -> dict[str, int]:
    out = {DIFF1: 0, DIFF2: 0, TIE: 0, MISSING: 0, NA: 0}
    for s in signals:
        out[s.points_to] = out.get(s.points_to, 0) + 1
    return out
