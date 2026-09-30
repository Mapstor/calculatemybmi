#!/usr/bin/env python3
"""check_sources.py — invariant check for the data-sourcing registry.

Usage:
    python3 check_sources.py [data-sources.csv] [page-map.csv]

Defaults: research/data-sources.csv, research/page-map.csv (page-map optional —
cross-checks are skipped with a warning if absent). Exit 0 = clean (warnings
allowed). Exit 1 = FAIL — do not present the files. Stdlib only; UTF-8 CSVs.
"""

import csv
import sys
from collections import Counter

STATUSES = {"verified", "candidate", "GAP"}
ACCESS = {"api", "bulk", "page"}
TIERS = {"A", "B", "C"}
KEYREQ = {"yes", "no", ""}
REQUIRED_COLS = ["domain", "source", "publisher", "url", "endpoint", "access",
                 "license", "tier", "cadence", "granularity", "format",
                 "key_required", "attribution", "verified_date", "next_check",
                 "coverage", "sample_note", "status", "pages_served", "notes"]
VERIFIED_REQUIRED = ["url", "attribution", "verified_date", "next_check",
                     "coverage", "sample_note"]

fails, warns = [], []


def fail(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def read_csv(path, label, required=None):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        return None
    except Exception as e:
        fail(f"{label}: could not read {path}: {e}")
        return []
    if rows and required:
        missing = [c for c in required if c not in rows[0]]
        if missing:
            fail(f"{label}: missing columns: {', '.join(missing)}")
            return []
    if not rows:
        warn(f"{label}: no data rows in {path}")
    return rows


def main():
    reg_path = sys.argv[1] if len(sys.argv) > 1 else "research/data-sources.csv"
    pm_path = sys.argv[2] if len(sys.argv) > 2 else "research/page-map.csv"

    reg = read_csv(reg_path, "registry", REQUIRED_COLS)
    if reg is None:
        fail(f"registry: file not found: {reg_path}")
        reg = []
    pages = read_csv(pm_path, "page-map")
    if pages is None:
        warn(f"page-map not found at {pm_path} — cross-checks skipped")
        pages = []

    # ---- registry checks ----
    domains = []
    status_count = Counter()
    for i, r in enumerate(reg, start=2):
        dom = r.get("domain", "").strip()
        if not dom:
            fail(f"registry line {i}: empty domain")
            continue
        domains.append(dom)
        status = r.get("status", "").strip()
        if status not in STATUSES:
            fail(f"registry '{dom}': bad status '{status}'")
            continue
        status_count[status] += 1
        if r.get("access", "").strip() and r.get("access", "").strip() not in ACCESS:
            warn(f"registry '{dom}': unknown access '{r.get('access', '')}'")
        if r.get("tier", "").strip() and r.get("tier", "").strip() not in TIERS:
            warn(f"registry '{dom}': unknown tier '{r.get('tier', '')}'")
        if r.get("key_required", "").strip() not in KEYREQ:
            warn(f"registry '{dom}': key_required should be yes/no")
        if not r.get("url", "").strip():
            fail(f"registry '{dom}': empty url")
        if status == "verified":
            for col in VERIFIED_REQUIRED:
                if not r.get(col, "").strip():
                    fail(f"registry '{dom}': verified but '{col}' is empty")
        if status == "GAP" and not r.get("notes", "").strip():
            fail(f"registry '{dom}': GAP without treatment in notes")

    for d, c in Counter(domains).items():
        if c > 1:
            fail(f"registry: duplicate domain '{d}'")
    dom_status = {r.get("domain", "").strip(): r.get("status", "").strip() for r in reg}

    # ---- page-map cross-checks ----
    slug_set = set()
    if pages:
        for p in pages:
            slug = p.get("slug", "").strip()
            if slug:
                slug_set.add(slug)
        for p in pages:
            slug = p.get("slug", "").strip()
            if not slug or p.get("archetype", "").strip() == "structural":
                continue
            ds = p.get("data_source", "").strip()
            if not ds:
                fail(f"page '{slug}': empty data_source")
            elif ds not in dom_status:
                fail(f"page '{slug}': data_source '{ds}' not in registry")
            elif dom_status[ds] == "candidate":
                fail(f"page '{slug}': data_source '{ds}' is only candidate — verify before build")
            elif dom_status[ds] == "GAP":
                warn(f"page '{slug}': rides a GAP domain '{ds}' — page must carry the gap treatment")
        for r in reg:
            for s in [x.strip() for x in r.get("pages_served", "").split(";") if x.strip()]:
                if s not in slug_set:
                    warn(f"registry '{r.get('domain', '?')}': pages_served slug '{s}' not in page-map")

    # ---- report ----
    print(f"registry rows: {len(domains)}")
    if status_count:
        print("status: " + "  ".join(f"{k}={v}" for k, v in sorted(status_count.items())))
    for w in warns:
        print(f"WARN: {w}")
    for f_ in fails:
        print(f"FAIL: {f_}")
    if fails:
        print(f"\nRESULT: FAIL ({len(fails)} violations, {len(warns)} warnings) — fix before presenting.")
        return 1
    print(f"\nRESULT: OK ({len(warns)} warnings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
