"""Parse Word comments and diff them between two documents.

Handles:
    word/comments.xml            - the base comment body/author/date
    word/commentsExtended.xml    - parent links, resolved/done state
    word/commentsExtensible.xml  - durableId (not used for matching)

Also resolves each comment's anchor text by finding the w:commentRangeStart /
w:commentRangeEnd pair in word/document.xml and concatenating the text between
them.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"


@dataclass
class Comment:
    comment_id: str
    parent_id: str | None
    author: str
    initials: str
    date: datetime | str | None
    anchor_text: str
    text: str
    resolved: bool

    @property
    def key(self) -> tuple[str, str, str]:
        date_str = self.date.isoformat() if isinstance(self.date, datetime) else str(self.date or "")
        return (self.author, date_str, self.text)


@dataclass
class CommentsDiff:
    only_in_1: list[Comment]
    only_in_2: list[Comment]
    in_both: list[Comment]


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


def _resolve_anchors(body_blob: bytes) -> dict[str, str]:
    """Walk the document body and, for each commentRangeStart/End, capture
    the visible text between them."""
    out: dict[str, str] = {}
    try:
        root = etree.fromstring(body_blob)
    except etree.XMLSyntaxError:
        return out
    active: dict[str, list[str]] = {}
    start_tag = f"{{{W}}}commentRangeStart"
    end_tag = f"{{{W}}}commentRangeEnd"
    t_tag = f"{{{W}}}t"
    del_tag = f"{{{W}}}delText"
    for el in root.iter():
        if el.tag == start_tag:
            cid = el.get(f"{{{W}}}id")
            if cid is not None:
                active[cid] = []
        elif el.tag == end_tag:
            cid = el.get(f"{{{W}}}id")
            if cid is not None and cid in active:
                out[cid] = "".join(active.pop(cid))
        elif el.tag == t_tag or el.tag == del_tag:
            if active:
                text = el.text or ""
                for buf in active.values():
                    buf.append(text)
    for cid, buf in active.items():
        out.setdefault(cid, "".join(buf))
    return out


def _parse_extended(blob: bytes | None) -> dict[str, dict[str, str]]:
    """Return {paraId: {parentParaId, done}} from commentsExtended.xml."""
    out: dict[str, dict[str, str]] = {}
    if not blob:
        return out
    try:
        root = etree.fromstring(blob)
    except etree.XMLSyntaxError:
        return out
    for ext in root.iter(f"{{{W15}}}commentEx"):
        para_id = ext.get(f"{{{W15}}}paraId")
        if not para_id:
            continue
        out[para_id] = {
            "parentParaId": ext.get(f"{{{W15}}}paraIdParent", "") or "",
            "done": ext.get(f"{{{W15}}}done", "0") or "0",
        }
    return out


def extract(path: Path) -> list[Comment]:
    out: list[Comment] = []
    try:
        with zipfile.ZipFile(path) as zf:
            comments_blob = _read(zf, "word/comments.xml")
            if not comments_blob:
                return out
            body_blob = _read(zf, "word/document.xml") or b""
            extended = _parse_extended(_read(zf, "word/commentsExtended.xml"))
            anchors = _resolve_anchors(body_blob)

            try:
                root = etree.fromstring(comments_blob)
            except etree.XMLSyntaxError:
                return out

            for c in root.iter(f"{{{W}}}comment"):
                cid = c.get(f"{{{W}}}id", "")
                author = c.get(f"{{{W}}}author", "") or ""
                initials = c.get(f"{{{W}}}initials", "") or ""
                date = _parse_date(c.get(f"{{{W}}}date"))
                text = _collect_text(c)
                para_id = None
                for p in c.iter(f"{{{W}}}p"):
                    para_id = p.get(f"{{{W14}}}paraId")
                    if para_id:
                        break
                ext_info = extended.get(para_id or "", {}) if para_id else {}
                out.append(Comment(
                    comment_id=cid,
                    parent_id=ext_info.get("parentParaId") or None,
                    author=author,
                    initials=initials,
                    date=date,
                    anchor_text=anchors.get(cid, ""),
                    text=text,
                    resolved=ext_info.get("done", "0") == "1",
                ))
    except (zipfile.BadZipFile, OSError):
        return out
    return out


def diff(a: list[Comment], b: list[Comment]) -> CommentsDiff:
    keys_a = {c.key: c for c in a}
    keys_b = {c.key: c for c in b}
    only_a = [c for k, c in keys_a.items() if k not in keys_b]
    only_b = [c for k, c in keys_b.items() if k not in keys_a]
    both = [c for k, c in keys_a.items() if k in keys_b]
    return CommentsDiff(only_in_1=only_a, only_in_2=only_b, in_both=both)


def latest_date(comments: list[Comment]) -> datetime | None:
    best: datetime | None = None
    for c in comments:
        if isinstance(c.date, datetime):
            if best is None or c.date > best:
                best = c.date
    return best
