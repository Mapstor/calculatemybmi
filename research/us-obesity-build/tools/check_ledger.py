#!/usr/bin/env python3
"""check_ledger.py — invariant check for kw-research canonical files.

Usage:
    python3 check_ledger.py [keyword-ledger.csv] [page-map.csv]

Defaults to research/keyword-ledger.csv and research/page-map.csv relative to cwd.
Exit 0 = clean (warnings allowed). Exit 1 = FAIL — do not present the files.
Stdlib only; both files are UTF-8 CSVs with a header row.
"""

import csv
import sys
from collections import Counter, defaultdict

ROLES = {"primary", "secondary", "tertiary", "discard"}
INTENTS = {"tool", "informational", "commercial", "navigational"}
DISCARD_REASONS = {"offtopic", "navigational", "below-floor-backlog", "duplicate-variant"}
SERP_CHECKS = {"auto", "queued", "verified-merge", "verified-split", "na"}
ARCHETYPES = {"tool", "data", "article", "hub", "structural"}
TIERS = {"T1", "T2", "T3"}
STATUSES = {"proposed", "approved", "specd", "built", "live"}

LEDGER_COLS = ["keyword", "volume", "trend_3m", "trend_yoy", "competition",
               "source_batch", "intent", "page_slug", "role", "discard_reason",
               "serp_check", "notes"]
PAGEMAP_COLS = ["slug", "hub", "archetype", "intent", "wedge", "data_source",
                "tier", "status", "notes"]

fails, warns = [], []


def fail(msg):
    fails.append(msg)


def warn(msg):
    warns.append(msg)


def norm(kw):
    return " ".join(kw.lower().split())


def read_csv(path, required_cols, label):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
    except FileNotFoundError:
        fail(f"{label}: file not found: {path}")
        return []
    except Exception as e:  # malformed CSV, encoding, etc.
        fail(f"{label}: could not read {path}: {e}")
        return []
    if rows:
        missing = [c for c in required_cols if c not in rows[0]]
        if missing:
            fail(f"{label}: missing columns: {', '.join(missing)}")
            return []
    else:
        warn(f"{label}: no data rows in {path}")
    return rows


def main():
    ledger_path = sys.argv[1] if len(sys.argv) > 1 else "research/keyword-ledger.csv"
    pagemap_path = sys.argv[2] if len(sys.argv) > 2 else "research/page-map.csv"

    ledger = read_csv(ledger_path, LEDGER_COLS, "ledger")
    pages = read_csv(pagemap_path, PAGEMAP_COLS, "page-map")

    # ---- page-map checks ----
    slugs = []
    for i, p in enumerate(pages, start=2):  # header = line 1
        slug = p.get("slug", "").strip()
        if not slug:
            fail(f"page-map line {i}: empty slug")
            continue
        slugs.append(slug)
        if p.get("archetype", "").strip() not in ARCHETYPES:
            fail(f"page-map '{slug}': bad archetype '{p.get('archetype', '')}'")
        if p.get("tier", "").strip() not in TIERS:
            fail(f"page-map '{slug}': bad tier '{p.get('tier', '')}'")
        if p.get("status", "").strip() not in STATUSES:
            fail(f"page-map '{slug}': bad status '{p.get('status', '')}'")
        if not p.get("data_source", "").strip():
            fail(f"page-map '{slug}': empty data_source (name a source or 'GAP')")
        elif p.get("data_source", "").strip() == "GAP":
            warn(f"page-map '{slug}': data_source is GAP — transparent-gap treatment required")
    dup_slugs = [s for s, c in Counter(slugs).items() if c > 1]
    for s in dup_slugs:
        fail(f"page-map: duplicate slug '{s}'")
    slug_set = set(slugs)
    for p in pages:
        hub = p.get("hub", "").strip()
        if hub and hub != "root" and hub not in slug_set:
            fail(f"page-map '{p.get('slug', '?')}': hub '{hub}' is not an existing slug or 'root'")

    # ---- ledger checks ----
    seen = {}
    by_page_role = defaultdict(lambda: defaultdict(list))
    role_count, intent_count, discard_count = Counter(), Counter(), Counter()
    for i, r in enumerate(ledger, start=2):
        kw_raw = r.get("keyword", "")
        kw = norm(kw_raw)
        if not kw:
            fail(f"ledger line {i}: empty keyword")
            continue
        if kw in seen:
            fail(f"ledger: duplicate keyword '{kw}' (lines {seen[kw]} and {i})")
        else:
            seen[kw] = i
        role = r.get("role", "").strip()
        intent = r.get("intent", "").strip()
        slug = r.get("page_slug", "").strip()
        reason = r.get("discard_reason", "").strip()
        serp = r.get("serp_check", "").strip()
        vol = r.get("volume", "").strip()

        if role not in ROLES:
            fail(f"ledger '{kw}': bad role '{role}'")
            continue
        role_count[role] += 1
        if intent and intent not in INTENTS:
            warn(f"ledger '{kw}': unknown intent '{intent}'")
        else:
            intent_count[intent or "(blank)"] += 1
        if serp and serp not in SERP_CHECKS:
            fail(f"ledger '{kw}': bad serp_check '{serp}'")
        if vol and not vol.isdigit():
            warn(f"ledger '{kw}': volume '{vol}' is not a plain integer")

        if role == "discard":
            if not reason:
                fail(f"ledger '{kw}': discard without discard_reason")
            elif reason not in DISCARD_REASONS:
                fail(f"ledger '{kw}': bad discard_reason '{reason}'")
            else:
                discard_count[reason] += 1
            if slug:
                fail(f"ledger '{kw}': discarded but page_slug set ('{slug}')")
        else:
            if not slug:
                fail(f"ledger '{kw}': role={role} but no page_slug")
            elif slug not in slug_set:
                fail(f"ledger '{kw}': page_slug '{slug}' not in page-map")
            else:
                by_page_role[slug][role].append(kw)

    # ---- per-page role checks ----
    for p in pages:
        slug = p.get("slug", "").strip()
        if not slug or p.get("archetype", "").strip() == "structural":
            continue
        primaries = by_page_role[slug]["primary"]
        secondaries = by_page_role[slug]["secondary"]
        if len(primaries) != 1:
            fail(f"page '{slug}': {len(primaries)} primaries (need exactly 1): {primaries}")
        if len(secondaries) == 0 and by_page_role[slug]:
            warn(f"page '{slug}': no secondaries")
        elif len(secondaries) > 5:
            warn(f"page '{slug}': {len(secondaries)} secondaries (expected 2-5)")
        if not by_page_role[slug]:
            warn(f"page '{slug}': no keywords assigned yet")

    # ---- report ----
    print(f"pages: {len(slugs)}  |  keywords: {len(seen)}")
    if role_count:
        print("roles:  " + "  ".join(f"{k}={v}" for k, v in sorted(role_count.items())))
    if intent_count:
        print("intent: " + "  ".join(f"{k}={v}" for k, v in sorted(intent_count.items())))
    if discard_count:
        print("discards: " + "  ".join(f"{k}={v}" for k, v in sorted(discard_count.items())))
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
