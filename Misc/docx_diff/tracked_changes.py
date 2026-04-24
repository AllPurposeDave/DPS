"""Parse tracked revisions (w:ins / w:del / w:moveFrom / w:moveTo) across all
word parts and diff them between two documents."""

from __future__ import annotations

import posixpath
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

REV_TAGS = {"ins", "del", "moveFrom", "moveTo"}


@dataclass
class TrackedChange:
    rev_type: str
    author: str
    date: datetime | str | None
    location: str
    text: str

    @property
    def key(self) -> tuple[str, str, str, str]:
        date_str = self.date.isoformat() if isinstance(self.date, datetime) else str(self.date or "")
        return (self.rev_type, self.author, date_str, self.text)


@dataclass
class TrackedDiff:
    only_in_1: list[TrackedChange]
    only_in_2: list[TrackedChange]
    in_both: list[TrackedChange]


def _read(zf: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        return zf.read(name)
    except KeyError:
        return None


def _parse_date(raw: str | None) -> datetime | str | None:
    if not raw:
        return None
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return raw


def _collect_text(el: etree._Element) -> str:
    parts: list[str] = []
    for node in el.iter():
        tag = etree.QName(node.tag).localname
        if tag in ("t", "delText"):
            parts.append(node.text or "")
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br":
            parts.append("\n")
    return "".join(parts)


def _parts_for_revisions(zf: zipfile.ZipFile) -> list[tuple[str, bytes]]:
    """Return (location_label, blob) for every word part that can contain revisions."""
    out: list[tuple[str, bytes]] = []
    body = _read(zf, "word/document.xml")
    if body:
        out.append(("body", body))
    rels = _read(zf, "word/_rels/document.xml.rels")
    if not rels:
        return out
    try:
        root = etree.fromstring(rels)
    except etree.XMLSyntaxError:
        return out
    header_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
    footer_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
    footnotes_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes"
    endnotes_type = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes"
    labels = {
        header_type: "header",
        footer_type: "footer",
        footnotes_type: "footnotes",
        endnotes_type: "endnotes",
    }
    for rel in root.findall(f"{{{PKG_REL_NS}}}Relationship"):
        rtype = rel.get("Type", "")
        target = rel.get("Target", "")
        if rtype not in labels or not target:
            continue
        if not target.startswith("/"):
            target = posixpath.normpath(posixpath.join("word", target))
        else:
            target = target.lstrip("/")
        blob = _read(zf, target)
        if blob:
            label = labels[rtype]
            name = posixpath.basename(target)
            out.append((f"{label}:{name}", blob))
    return out


def extract(path: Path) -> list[TrackedChange]:
    out: list[TrackedChange] = []
    try:
        with zipfile.ZipFile(path) as zf:
            for location, blob in _parts_for_revisions(zf):
                try:
                    root = etree.fromstring(blob)
                except etree.XMLSyntaxError:
                    continue
                for el in root.iter():
                    tag = etree.QName(el.tag).localname
                    if tag not in REV_TAGS:
                        continue
                    author = el.get(f"{{{W}}}author", "") or ""
                    date_raw = el.get(f"{{{W}}}date")
                    text = _collect_text(el)
                    out.append(TrackedChange(
                        rev_type=tag,
                        author=author,
                        date=_parse_date(date_raw),
                        location=location,
                        text=text,
                    ))
    except (zipfile.BadZipFile, OSError):
        return out
    return out


def diff(a: list[TrackedChange], b: list[TrackedChange]) -> TrackedDiff:
    keys_a = {c.key: c for c in a}
    keys_b = {c.key: c for c in b}
    only_a = [c for k, c in keys_a.items() if k not in keys_b]
    only_b = [c for k, c in keys_b.items() if k not in keys_a]
    both = [c for k, c in keys_a.items() if k in keys_b]
    return TrackedDiff(only_in_1=only_a, only_in_2=only_b, in_both=both)


def latest_date(changes: list[TrackedChange]) -> datetime | None:
    best: datetime | None = None
    for c in changes:
        if isinstance(c.date, datetime):
            if best is None or c.date > best:
                best = c.date
    return best
