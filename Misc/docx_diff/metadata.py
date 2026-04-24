"""Harvest metadata from a .docx (OOXML zip) file.

Covers:
  - docProps/core.xml   (Dublin Core)
  - docProps/app.xml    (application stats + environment)
  - docProps/custom.xml (user-defined custom properties)
  - filesystem stat
  - archive SHA-256
  - normalized document.xml SHA-256 (whitespace-insensitive)
  - unique w:rsid values (save-session IDs)
"""

from __future__ import annotations

import hashlib
import os
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from lxml import etree

NS = {
    "cp": "http://schemas.openxmlformats.org/package/2006/metadata/core-properties",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "app": "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties",
    "custom": "http://schemas.openxmlformats.org/officeDocument/2006/custom-properties",
    "vt": "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
}

CORE_FIELDS: list[tuple[str, str]] = [
    ("creator", "dc:creator"),
    ("lastModifiedBy", "cp:lastModifiedBy"),
    ("revision", "cp:revision"),
    ("created", "dcterms:created"),
    ("modified", "dcterms:modified"),
    ("title", "dc:title"),
    ("subject", "dc:subject"),
    ("description", "dc:description"),
    ("keywords", "cp:keywords"),
    ("category", "cp:category"),
    ("contentStatus", "cp:contentStatus"),
    ("version", "cp:version"),
]

APP_FIELDS: list[str] = [
    "Application",
    "AppVersion",
    "Company",
    "Manager",
    "Template",
    "TotalTime",
    "Pages",
    "Words",
    "Characters",
    "CharactersWithSpaces",
    "Lines",
    "Paragraphs",
    "SharedDoc",
    "HyperlinksChanged",
]


@dataclass
class Metadata:
    core: dict[str, Any] = field(default_factory=dict)
    app: dict[str, Any] = field(default_factory=dict)
    custom: dict[str, Any] = field(default_factory=dict)
    fs: dict[str, Any] = field(default_factory=dict)
    hashes: dict[str, str] = field(default_factory=dict)
    rsids: set[str] = field(default_factory=set)
    error: str | None = None


def _read(zf: zipfile.ZipFile, name: str) -> bytes | None:
    try:
        return zf.read(name)
    except KeyError:
        return None


def _text(root: etree._Element, xpath: str) -> str | None:
    hit = root.find(xpath, NS)
    if hit is None:
        return None
    return (hit.text or "").strip() or None


def _parse_core(blob: bytes | None) -> dict[str, Any]:
    if not blob:
        return {}
    root = etree.fromstring(blob)
    out: dict[str, Any] = {}
    for key, path in CORE_FIELDS:
        value = _text(root, path)
        if value is None:
            continue
        if key in ("created", "modified"):
            out[key] = _parse_iso(value)
        elif key == "revision":
            try:
                out[key] = int(value)
            except ValueError:
                out[key] = value
        else:
            out[key] = value
    return out


def _parse_app(blob: bytes | None) -> dict[str, Any]:
    if not blob:
        return {}
    root = etree.fromstring(blob)
    out: dict[str, Any] = {}
    for field_name in APP_FIELDS:
        hit = root.find(f"app:{field_name}", NS)
        if hit is None:
            continue
        raw = (hit.text or "").strip()
        if not raw:
            continue
        if field_name in {
            "TotalTime", "Pages", "Words", "Characters",
            "CharactersWithSpaces", "Lines", "Paragraphs",
            "DocSecurity", "SharedDoc", "HyperlinksChanged",
        }:
            try:
                out[field_name] = int(raw)
            except ValueError:
                out[field_name] = raw
        else:
            out[field_name] = raw
    return out


def _parse_custom(blob: bytes | None) -> dict[str, Any]:
    if not blob:
        return {}
    root = etree.fromstring(blob)
    out: dict[str, Any] = {}
    for prop in root.findall("custom:property", NS):
        name = prop.get("name")
        if not name:
            continue
        value_node = next(iter(prop), None)
        if value_node is None:
            continue
        text = (value_node.text or "").strip()
        out[name] = text
    return out


def _parse_iso(value: str) -> datetime | str:
    value = value.strip()
    if not value:
        return ""
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return value


def _normalize_xml(blob: bytes) -> bytes:
    """Reserialize XML with stripped whitespace-only text nodes so that
    cosmetic reformatting does not count as a content change.
    """
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.fromstring(blob, parser=parser)
    return etree.tostring(root, method="c14n")


def _collect_rsids(blob_settings: bytes | None, blob_doc: bytes | None) -> set[str]:
    rsids: set[str] = set()
    w = NS["w"]
    attrs_of_interest = {
        f"{{{w}}}rsidR",
        f"{{{w}}}rsidP",
        f"{{{w}}}rsidRDefault",
        f"{{{w}}}rsidRPr",
        f"{{{w}}}rsidTr",
        f"{{{w}}}rsidDel",
        f"{{{w}}}rsid",
        f"{{{w}}}val",
    }
    for blob in (blob_settings, blob_doc):
        if not blob:
            continue
        try:
            root = etree.fromstring(blob)
        except etree.XMLSyntaxError:
            continue
        for el in root.iter():
            tag = etree.QName(el.tag).localname
            if blob is blob_settings and tag in {"rsid", "rsidRoot"}:
                val = el.get(f"{{{w}}}val")
                if val:
                    rsids.add(val)
                continue
            for attr in attrs_of_interest:
                if attr in el.attrib:
                    rsids.add(el.attrib[attr])
    return rsids


def extract(path: Path) -> Metadata:
    meta = Metadata()
    try:
        stat = path.stat()
        meta.fs = {
            "size": stat.st_size,
            "mtime": datetime.fromtimestamp(stat.st_mtime),
            "ctime": datetime.fromtimestamp(stat.st_ctime),
        }
    except OSError as exc:
        meta.error = f"stat failed: {exc}"
        return meta

    try:
        raw_bytes = path.read_bytes()
    except OSError as exc:
        meta.error = f"read failed: {exc}"
        return meta
    meta.hashes["archive_sha256"] = hashlib.sha256(raw_bytes).hexdigest()

    try:
        with zipfile.ZipFile(path) as zf:
            core = _read(zf, "docProps/core.xml")
            app = _read(zf, "docProps/app.xml")
            custom = _read(zf, "docProps/custom.xml")
            document = _read(zf, "word/document.xml")
            settings = _read(zf, "word/settings.xml")
    except (zipfile.BadZipFile, OSError) as exc:
        meta.error = f"zip read failed: {exc}"
        return meta

    meta.core = _parse_core(core)
    meta.app = _parse_app(app)
    meta.custom = _parse_custom(custom)

    if document:
        try:
            normalized = _normalize_xml(document)
            meta.hashes["document_xml_sha256"] = hashlib.sha256(normalized).hexdigest()
        except etree.XMLSyntaxError:
            meta.hashes["document_xml_sha256"] = hashlib.sha256(document).hexdigest()
    meta.rsids = _collect_rsids(settings, document)

    return meta


def flatten_for_diff(meta: Metadata) -> dict[tuple[str, str], Any]:
    """Flatten metadata into a dict keyed by (category, field) for easy side-by-side diffing."""
    out: dict[tuple[str, str], Any] = {}
    for k, v in meta.core.items():
        out[("core", k)] = v
    for k, v in meta.app.items():
        out[("app", k)] = v
    for k, v in meta.custom.items():
        out[("custom", k)] = v
    for k, v in meta.fs.items():
        out[("fs", k)] = v
    for k, v in meta.hashes.items():
        out[("hash", k)] = v
    if meta.rsids:
        out[("rsid", "unique_count")] = len(meta.rsids)
    return out
