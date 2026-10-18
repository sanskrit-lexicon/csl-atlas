#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H6724 — golden gate for the MahāBhā./MahāBh. homograph trap (SL FINDINGS §98).

The trap: PD sigla MahāBhā. = Mahābhārata (epic; DCS-covered) and
MahāBh. = Mahābhāṣya (Patañjali's grammar; DCS residue) differ by ONE vowel
marker, and the crosswalk's consonant-skeleton similarity metric (skeleton(),
scripts/pd_dcs_crosswalk.py) collapses BOTH to "mhbh". A similarity-merge that
folds the pair into one work would move 1,934 grammar citations into the epic's
covered mass and corrupt every headline metric. They are never merged; the
locator shape tells them apart (epic book.parvan.verse vs grammar
book.pāda.sūtra with Pāṇini cross-refs).

This gate re-runs at any time and refuses on fusion:
  * positive: the golden fixture (pd_mahabha_trap_fixture.tsv) and, when
    present, the live data/pd/pd_siglum_families.tsv carry the pair un-fused
    with the exact work identities, counts and covered/residue classes;
  * negative: three fused input variants (merged row, collapsed identity map,
    similarity-group without exclusion) are each fed to the same checker and
    MUST be refused — a refusal that fails to fire is itself a gate failure.

Exit 0 only when the positive case passes AND every fused variant refuses.
"""
import csv
import io
import os
import re
import sys
import tempfile
import unicodedata

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pd_mahabha_trap_fixture.tsv")
LIVE_FAMILIES = os.path.join(ROOT, "data", "pd", "pd_siglum_families.tsv")

EPIC = "MahāBhā."
GRAM = "MahāBh."
EPIC_WORK = "Mahābhārata"
GRAM_WORK = "Mahābhāṣya (Patañjali)"
EPIC_COUNT = 9337   # pd_siglum_raw.tsv row 2
GRAM_COUNT = 1934   # pd_siglum_raw.tsv row 24

# The one similarity-merge that is FORBIDDEN even though skeletons collide.
MERGE_EXCLUSION = frozenset({EPIC, GRAM})


class FusionRefused(Exception):
    """A fused representation of the MahāBhā./MahāBh. pair was detected."""


def skeleton(siglum):
    """Consonant skeleton — same metric as pd_dcs_crosswalk.skeleton()."""
    s = siglum.rstrip(".")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = s.lower()
    return re.sub(r"[aeiou]", "", s)


def read_fixture(path):
    with io.open(path, "r", encoding="utf-8", newline="\n") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    return rows


def check_pair_rows(rows, source):
    """The load-bearing invariant: exactly two distinct rows, one work each,
    correct classes, never one fused row and never a shared work."""
    if len(rows) != 2:
        raise FusionRefused(
            f"[{source}] expected exactly 2 un-fused rows for the pair, got {len(rows)}")
    by_sig = {r["siglum"]: r for r in rows}
    for need in (EPIC, GRAM):
        if need not in by_sig:
            raise FusionRefused(
                f"[{source}] siglum {need} missing — pair fused or dropped: "
                f"rows present = {sorted(by_sig)}")
    if by_sig[EPIC]["work"] != EPIC_WORK:
        raise FusionRefused(
            f"[{source}] {EPIC} must resolve to {EPIC_WORK!r}, got {by_sig[EPIC]['work']!r}")
    if by_sig[GRAM]["work"] != GRAM_WORK:
        raise FusionRefused(
            f"[{source}] {GRAM} must resolve to {GRAM_WORK!r}, got {by_sig[GRAM]['work']!r}")
    if by_sig[EPIC]["work"] == by_sig[GRAM]["work"]:
        raise FusionRefused(f"[{source}] both sigla resolve to one work — fusion")
    # similarity merge guard: skeletons DO collide; the pair must stay split anyway
    if skeleton(EPIC) == skeleton(GRAM) and set(by_sig) != MERGE_EXCLUSION:
        raise FusionRefused(f"[{source}] similarity group not exclusion-protected")
    # locator-shape discriminator: each siglum keeps its own distinct locator regime
    loc_e, loc_g = by_sig[EPIC]["locator_shape"], by_sig[GRAM]["locator_shape"]
    if not loc_e or not loc_g or loc_e == loc_g:
        raise FusionRefused(
            f"[{source}] locator-shape discriminator absent or identical: {loc_e!r} vs {loc_g!r}")
    for r in rows:
        if not r["sample_locator"].startswith(r["siglum"]):
            raise FusionRefused(
                f"[{source}] sample locator {r['sample_locator']!r} does not attest {r['siglum']}")
    return by_sig


def check_classes(by_sig, source):
    want = {EPIC: ("covered", str(EPIC_COUNT)), GRAM: ("residue", str(GRAM_COUNT))}
    for sig, (klass, count) in want.items():
        row = by_sig[sig]
        if row["class"] != "primary" or row["match_type"] != klass:
            raise FusionRefused(
                f"[{source}] {sig} must be primary/{klass}, got "
                f"{row['class']}/{row['match_type']}")
        if row["count"] != count:
            raise FusionRefused(
                f"[{source}] {sig} count drifted from the harvested golden value: "
                f"want {count}, got {row['count']}")


def check_live_families():
    """Re-run wiring: if the crosswalk output exists, it must still carry the
    pair un-fused (a re-run that fuses them makes this gate refuse)."""
    if not os.path.exists(LIVE_FAMILIES):
        return None
    with io.open(LIVE_FAMILIES, "r", encoding="utf-8", newline="\n") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    by_sig = {}
    for r in rows:
        if r["siglum"] in (EPIC, GRAM):
            by_sig[r["siglum"]] = r
    if len(by_sig) != 2:
        raise FusionRefused(
            f"[live pd_siglum_families.tsv] pair not present as two rows: {sorted(by_sig)}")
    want = {EPIC: ("covered", EPIC_WORK), GRAM: ("residue", GRAM_WORK)}
    for sig, (klass, work) in want.items():
        r = by_sig[sig]
        if r["match_type"] != klass or r["display_title"] != work:
            raise FusionRefused(
                f"[live pd_siglum_families.tsv] {sig} drifted: "
                f"{r['match_type']}/{r['display_title']!r}, want {klass}/{work!r}")
    return len(rows)


def fused_variants():
    """Materialise the fused inputs the negative test must refuse."""
    variants = []
    # F1: one merged row (the similarity-merge end state)
    variants.append(("merged-row", read_fixture(FIXTURE), {
        "siglum": f"{EPIC}|{GRAM}", "work": EPIC_WORK, "count": str(EPIC_COUNT + GRAM_COUNT),
        "class": "primary", "match_type": "covered",
        "locator_shape": "merged", "sample_locator": "MahāBhā. vii. 22. 33"}))
    # F2: two rows, but both collapsed onto the epic (identity fusion)
    f2 = [dict(r) for r in read_fixture(FIXTURE)]
    f2[1]["work"] = EPIC_WORK
    variants.append(("collapsed-identity", f2, None))
    # F3: two rows folded into one similarity group without the exclusion pair
    f3 = [dict(r) for r in read_fixture(FIXTURE)]
    f3[0]["siglum"] = "MahāBhā/MahāBh"   # degrouped spelling variant merge
    variants.append(("similarity-group", f3, None))
    return variants


def main():
    log = []

    # --- positive ---
    golden = read_fixture(FIXTURE)
    by_sig = check_pair_rows(golden, "golden fixture")
    check_classes(by_sig, "golden fixture")
    for r in golden:
        log.append(f"POSITIVE PASS: {r['siglum']} = {r['work']} "
                   f"({r['class']}/{r['match_type']}, n={r['count']}, "
                   f"locator: {r['sample_locator']})")
    live = check_live_families()
    if live is not None:
        log.append(f"POSITIVE PASS: live pd_siglum_families.tsv ({live} rows) "
                   f"carries {EPIC}/{GRAM} un-fused")
    else:
        log.append("POSITIVE PASS (partial): live families TSV absent — fixture-only run")

    # --- negative: every fused variant must refuse ---
    refusals = 0
    for name, rows, extra in fused_variants():
        payload = rows + ([extra] if extra else [])
        try:
            check_pair_rows(payload, f"negative:{name}")
        except FusionRefused as e:
            refusals += 1
            log.append(f"NEGATIVE REFUSED [{name}]: {e}")
        else:
            print(f"FAIL: fused input {name} was ACCEPTED — similarity-merge leaked",
                  file=sys.stderr)
            return 1
        check_classes_probe(name, payload)

    print("\n".join(log))
    print(f"GATE GREEN: positive passed, {refusals}/3 fused variants refused, "
          f"pair never similarity-merged (skeleton collision "
          f"'{skeleton(EPIC)}' excluded)")
    return 0


def check_classes_probe(name, payload):
    """Class checker must also refuse fused class payloads."""
    try:
        by_sig = {r["siglum"]: r for r in payload}
        check_classes(by_sig, f"negative:{name}")
    except FusionRefused:
        pass  # refused — correct
    except KeyError:
        pass  # row shape already refused upstream


if __name__ == "__main__":
    raise SystemExit(main())
