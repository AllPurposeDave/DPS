"""Extract an ordered paragraph stream from a .docx.

Covers body, headers, footers, footnotes, endnotes. For each paragraph we
produce two text views:
  - accepted: w:ins kept, w:del dropped    (what Word shows if all tracked
    revisions were accepted). This is the canonical view for diffing.
  - rejected: w:ins dropped, w:del kept    (what Word shows if all were
    rejected). Captured but not diffed; surfaced via tracked-changes pipeline.
"""

from __future__ import annotations

import posixpath
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

HEADER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/header"
FOOTER_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer"
FOOTNOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/footnotes"
ENDNOTES_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/endnotes"


@dataclass
class Paragraph:
    location: str
    index: int
    accepted: str
    rejected: str
    has_tracked_changes: bool = False


@dataclass
class ExtractedDoc:
    paragraphs: list[Paragraph] = field(default_factory=list)
    error: str | None = None


def _read(zf: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        return zf.read(name)
    except KeyError:
        return None


def _rels_for(zf: zipfile.ZipFile, part_path: str) -> dict[str, tuple[str, str]]:
    """Return {rId: (target_path, type)} for the part at ``part_path``."""
    base = posixpath.dirname(part_path)
    rels_path = posixpath.join(base, "_rels", posixpath.basename(part_path) + ".rels")
    blob = _read(zf, rels_path)
    if not blob:
        return {}
    out: dict[str, tuple[str, str]] = {}
    try:
        root = etree.fromstring(blob)
    except etree.XMLSyntaxError:
        return out
    for rel in root.findall(f"{{{PKG_REL_NS}}}Relationship"):
        rid = rel.get("Id")
        target = rel.get("Target")
        rtype = rel.get("Type", "")
        if not rid or not target:
            continue
        if not target.startswith("/"):
            target = posixpath.normpath(posixpath.join(base, target))
        else:
            target = target.lstrip("/")
        out[rid] = (target, rtype)
    return out


def _paragraph_text(p_el: etree._Element, *, accept_tracked: bool) -> tuple[str, bool]:
    """Collect visible text from one <w:p>. Returns (text, had_tracked_markers)."""
    parts: list[str] = []
    had_tracked = False
    for descendant in p_el.iter():
        tag = etree.QName(descendant.tag).localname
        parent = descendant.getparent()
        ancestor_tags = []
        cur = parent
        while cur is not None:
            ancestor_tags.append(etree.QName(cur.tag).localname)
            cur = cur.getparent()
        inside_ins = "ins" in ancestor_tags
        inside_del = "del" in ancestor_tags
        if inside_ins or inside_del:
            had_tracked = True
        if tag == "t":
            if inside_del and accept_tracked:
                continue
            if inside_ins and not accept_tracked:
                continue
            parts.append(descendant.text or "")
        elif tag == "delText":
            if accept_tracked:
                continue
            parts.append(descendant.text or "")
        elif tag == "tab":
            parts.append("\t")
        elif tag == "br":
            parts.append("\n")
    return "".join(parts), had_tracked


def _extract_part(blob: bytes, location: str, out: list[Paragraph]) -> None:
    try:
        root = etree.fromstring(blob)
    except etree.XMLSyntaxError:
        return
    idx = 0
    for p in root.iter(f"{{{W}}}p"):
        accepted, tracked = _paragraph_text(p, accept_tracked=True)
        rejected, _ = _paragraph_text(p, accept_tracked=False)
        if not accepted and not rejected:
            continue
        out.append(Paragraph(location=location, index=idx, accepted=accepted,
                             rejected=rejected, has_tracked_changes=tracked))
        idx += 1


def extract(path: Path) -> ExtractedDoc:
    doc = ExtractedDoc()
    try:
        with zipfile.ZipFile(path) as zf:
            names = set(zf.namelist())
            if "word/document.xml" not in names:
                doc.error = "missing word/document.xml"
                return doc

            body = zf.read("word/document.xml")
            _extract_part(body, "body", doc.paragraphs)

            rels = _rels_for(zf, "word/document.xml")
            header_targets: list[str] = []
            footer_targets: list[str] = []
            footnotes_target: str | None = None
            endnotes_target: str | None = None
            for _rid, (target, rtype) in rels.items():
                if rtype == HEADER_REL:
                    header_targets.append(target)
                elif rtype == FOOTER_REL:
                    footer_targets.append(target)
                elif rtype == FOOTNOTES_REL:
                    footnotes_target = target
                elif rtype == ENDNOTES_REL:
                    endnotes_target = target

            for tgt in sorted(header_targets):
                blob = _read(zf, tgt)
                if blob:
                    _extract_part(blob, f"header:{posixpath.basename(tgt)}", doc.paragraphs)
            for tgt in sorted(footer_targets):
                blob = _read(zf, tgt)
                if blob:
                    _extract_part(blob, f"footer:{posixpath.basename(tgt)}", doc.paragraphs)
            if footnotes_target:
                blob = _read(zf, footnotes_target)
                if blob:
                    _extract_part(blob, "footnotes", doc.paragraphs)
            if endnotes_target:
                blob = _read(zf, endnotes_target)
                if blob:
                    _extract_part(blob, "endnotes", doc.paragraphs)
    except (zipfile.BadZipFile, OSError) as exc:
        doc.error = f"zip read failed: {exc}"
    return doc


def by_location(paragraphs: list[Paragraph]) -> dict[str, list[Paragraph]]:
    out: dict[str, list[Paragraph]] = {}
    for p in paragraphs:
        out.setdefault(p.location, []).append(p)
    return out
