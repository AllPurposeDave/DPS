"""
Tests for parse_baseline_and_name in extract_controls.py.

Run from the DPS project root:
    python scripts/test_parse_baseline_and_name.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from extract_controls import parse_baseline_and_name

CASES = [
    # (description, text, control_id, expected_baseline, expected_name)

    # --- Standard formats (ID first) ---
    ("ID only",
     "AC-1.001",
     "AC-1.001", "", ""),

    ("ID + baseline only",
     "AC-1.001 (L, M, H)",
     "AC-1.001", "L,M,H", ""),

    ("ID + baseline + name",
     "AC-1.001 (L, M, H) - Access Control Policy",
     "AC-1.001", "L,M,H", "Access Control Policy"),

    ("ID + name only (no baseline)",
     "AC-1.001 - Access Control Policy",
     "AC-1.001", "", "Access Control Policy"),

    ("ID + name + trailing baseline (yesterday's fix)",
     "AC-1.001 - Access Control Policy (L, M, H)",
     "AC-1.001", "L,M,H", "Access Control Policy"),

    ("ID + name + trailing baseline, single letter",
     "AC-1.001 - Access Control Policy (H)",
     "AC-1.001", "H", "Access Control Policy"),

    ("ID + name + trailing baseline (L only)",
     "AC-1.001 - Access Control Policy (L)",
     "AC-1.001", "L", "Access Control Policy"),

    # --- Name before ID (today's fix) ---
    ("Name before ID, baseline after with dash",
     "Access Control Policy ACC10.111 - (L, M, H)",
     "ACC10.111", "L,M,H", "Access Control Policy"),

    ("Name before ID, baseline after no dash",
     "Access Control Policy ACC10.111 (L, M, H)",
     "ACC10.111", "L,M,H", "Access Control Policy"),

    ("Name before ID, no baseline",
     "Access Control Policy ACC10.111",
     "ACC10.111", "", "Access Control Policy"),

    ("Name before ID, baseline after with em-dash",
     "Encryption Standard ENC-2.005 \u2014 (M, H)",
     "ENC-2.005", "M,H", "Encryption Standard"),

    # --- Edge cases ---
    ("Trailing description text after name+baseline",
     "AC-1.001 (L) - Access Control Policy some extra text",
     "AC-1.001", "L", "Access Control Policy some extra text"),

    ("ID not in text",
     "AC-1.001 - Access Control Policy",
     "ZZ-9.999", "", ""),
]


def run_tests():
    passed = 0
    failed = 0

    for desc, text, ctrl_id, exp_baseline, exp_name in CASES:
        baseline, name = parse_baseline_and_name(text, ctrl_id)
        ok = (baseline == exp_baseline) and (name == exp_name)
        status = "PASS" if ok else "FAIL"
        if ok:
            passed += 1
        else:
            failed += 1

        print(f"[{status}] {desc}")
        if not ok:
            print(f"       text:     {text!r}")
            print(f"       ctrl_id:  {ctrl_id!r}")
            print(f"       baseline: got={baseline!r}  expected={exp_baseline!r}")
            print(f"       name:     got={name!r}  expected={exp_name!r}")

    print(f"\n{passed}/{passed+failed} tests passed", "✓" if not failed else "✗")
    return failed


if __name__ == "__main__":
    sys.exit(run_tests())
