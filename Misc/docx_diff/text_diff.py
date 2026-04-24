"""Diff two paragraph streams.

Produces paragraph-level add/remove/change records, plus for each "change"
a word-level inline opcode list suitable for colored Excel rich-text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from text_extract import Paragraph, by_location

CHANGED_RATIO = 0.6
_WORD_SPLIT_RE = re.compile(r"(\s+|[^\w\s])")


@dataclass
class ParagraphDiff:
    location: str
    index1: int | None
    index2: int | None
    kind: str  # added | removed | changed | equal (equal excluded from output)
    text1: str
    text2: str
    inline_ops: list[tuple[str, str]] = field(default_factory=list)


def _tokenize(text: str) -> list[str]:
    """Split text into words, whitespace, and single punctuation tokens."""
    if not text:
        return []
    pieces = _WORD_SPLIT_RE.split(text)
    return [p for p in pieces if p]


def inline_diff(a: str, b: str) -> list[tuple[str, str]]:
    """Return a list of (op, text) tuples where op is one of equal/insert/delete."""
    tokens_a = _tokenize(a)
    tokens_b = _tokenize(b)
    sm = SequenceMatcher(a=tokens_a, b=tokens_b, autojunk=False)
    ops: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            ops.append(("equal", "".join(tokens_a[i1:i2])))
        elif tag == "delete":
            ops.append(("delete", "".join(tokens_a[i1:i2])))
        elif tag == "insert":
            ops.append(("insert", "".join(tokens_b[j1:j2])))
        elif tag == "replace":
            ops.append(("delete", "".join(tokens_a[i1:i2])))
            ops.append(("insert", "".join(tokens_b[j1:j2])))
    return ops


def _diff_location(paras_a: list[Paragraph], paras_b: list[Paragraph],
                   location: str) -> list[ParagraphDiff]:
    texts_a = [p.accepted for p in paras_a]
    texts_b = [p.accepted for p in paras_b]
    sm = SequenceMatcher(a=texts_a, b=texts_b, autojunk=False)
    out: list[ParagraphDiff] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "delete":
            for k in range(i1, i2):
                out.append(ParagraphDiff(location, paras_a[k].index, None,
                                         "removed", texts_a[k], "",
                                         inline_diff(texts_a[k], "")))
        elif tag == "insert":
            for k in range(j1, j2):
                out.append(ParagraphDiff(location, None, paras_b[k].index,
                                         "added", "", texts_b[k],
                                         inline_diff("", texts_b[k])))
        elif tag == "replace":
            # pair them up positionally; leftover side becomes pure add/remove
            pairs = min(i2 - i1, j2 - j1)
            for k in range(pairs):
                a_text = texts_a[i1 + k]
                b_text = texts_b[j1 + k]
                ratio = SequenceMatcher(a=a_text, b=b_text, autojunk=False).ratio()
                kind = "changed" if ratio >= CHANGED_RATIO else "replaced"
                out.append(ParagraphDiff(location,
                                         paras_a[i1 + k].index,
                                         paras_b[j1 + k].index,
                                         kind, a_text, b_text,
                                         inline_diff(a_text, b_text)))
            for k in range(pairs, i2 - i1):
                idx = i1 + k
                out.append(ParagraphDiff(location, paras_a[idx].index, None,
                                         "removed", texts_a[idx], "",
                                         inline_diff(texts_a[idx], "")))
            for k in range(pairs, j2 - j1):
                idx = j1 + k
                out.append(ParagraphDiff(location, None, paras_b[idx].index,
                                         "added", "", texts_b[idx],
                                         inline_diff("", texts_b[idx])))
    return out


def diff(paragraphs_a: list[Paragraph], paragraphs_b: list[Paragraph]) -> list[ParagraphDiff]:
    by_a = by_location(paragraphs_a)
    by_b = by_location(paragraphs_b)
    all_locations: list[str] = sorted(set(by_a) | set(by_b))
    out: list[ParagraphDiff] = []
    for loc in all_locations:
        out.extend(_diff_location(by_a.get(loc, []), by_b.get(loc, []), loc))
    return out
