"""Convert output/controls.csv into markdown, one file per source doc.

Run after the Controls2CSV ingest:
    python csv_to_md.py

Edit the CONFIG block below to change which columns are emitted.
"""

import csv
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

HERE = Path(__file__).parent
CSV_PATH = HERE / "output" / "controls.csv"
MD_DIR = HERE / "output" / "md"

# One markdown file per unique value in this column. Set to None for a single
# combined file.
GROUP_BY = "source_file"

# Column used as the section title for each control.
TITLE_COLUMN = "control_id"

# Columns rendered as labeled fields under each control, in this order.
# Remove or reorder freely. Empty values are skipped.
FIELDS = [
    ("control_name", "Name"),
    ("baseline", "Baseline"),
    ("section_header", "Section"),
    ("control_description", "Description"),
    ("supplemental_guidance", "Supplemental Guidance"),
    ("miscellaneous", "Miscellaneous"),
]

# Doc-level metadata printed once at the top of each file.
HEADER_FIELDS = [
    ("purpose", "Purpose"),
    ("scope", "Scope"),
    ("applicability", "Applicability"),
    ("compliance_date", "Compliance Date"),
    ("published_url", "Published URL"),
]

# ---------------------------------------------------------------------------


def render_control(row):
    title = row.get(TITLE_COLUMN, "").strip() or "(no id)"
    lines = [f"## {title}", ""]
    for col, label in FIELDS:
        val = (row.get(col) or "").strip()
        if not val:
            continue
        if "\n" in val or len(val) > 120:
            lines.append(f"**{label}:**")
            lines.append("")
            lines.append(val)
        else:
            lines.append(f"**{label}:** {val}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_header(group_key, sample_row):
    lines = [f"# {group_key}", ""]
    for col, label in HEADER_FIELDS:
        val = (sample_row.get(col) or "").strip()
        if val:
            lines.append(f"- **{label}:** {val}")
    if lines[-1] != "":
        lines.append("")
    return "\n".join(lines) + "\n"


def safe_name(s):
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)


def main():
    if not CSV_PATH.exists():
        sys.exit(f"Missing {CSV_PATH}")

    MD_DIR.mkdir(parents=True, exist_ok=True)

    groups = {}
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row.get(GROUP_BY, "") if GROUP_BY else "controls"
            groups.setdefault(key or "unknown", []).append(row)

    for key, rows in groups.items():
        header = render_header(key, rows[0])
        body = "\n".join(render_control(r) for r in rows)
        out = MD_DIR / f"{safe_name(Path(key).stem)}.md"
        out.write_text(header + "\n" + body, encoding="utf-8")
        print(f"Wrote {out}  ({len(rows)} controls)")


if __name__ == "__main__":
    main()
