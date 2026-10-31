#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""H7513 — MW missing-entries scan vs PWG/pwk (csl-corrections #119, KnbRao).

KnbRao's proposal (issue #119, 14-09-2026 Telegram #502926): compare MW with
PWG/pwk to find MW entries missing *by error*. This is the full-inventory
corpus job the 14-09 trial (SanskritLexicography/HeadwordLists, sup_7 scope)
pointed at: every PWG/pwk base headword that MW lacks, classified into

  (a) missing-by-error candidates  — PWG/pwk CITE it (>=1 <ls> tag with a
      payload anywhere under that headword) and MW lacks it or has it only
      under a form that no longer resolves (stem / near-form review tiers);
  (b) expected absence             — MW lacks it AND PWG/pwk never cite it
      (derivative entries: cross-references, re-spellings, gloss-only stubs).

Denominators are stated for both classes over the comparison universe
|distinct base headwords in PWG ∪ pwk| (pwk = pw + pwkvn, the Cologne
digitization of Böhtlingk's kürzerer Fassung incl. its Nachträge).

Substrate reuse (data/pwg_dcs/, H7463): the builder refuses to run when the
local pwg.txt sha256 does not equal the Stage-1 pin (430c910f…), and pins the
same entry register (123,366). Every published number regenerates from the
committed row-level TSV under scripts/mw_vs_pw_check.py (exit non-zero on
drift).

Definitions shipped with every count (§0 of the report):
  base headword  = clean(k1) — SLP1 letters only (accents/*-markers stripped);
                   the MW side also resolves via clean(k2) aliases.
  "PWG/pwk cite it" = the headword has >=1 entry in pwg.txt/pw.txt/pwkvn.txt
                   whose body carries an <ls>…</ls> tag with >=1 alphanumeric
                   character in its payload (raw-tag notion; the finer
                   quotation-linked unit rule of pwg_dcs measures units, not
                   entry-level citability).
  stem tier      = MW carries a headword sharing the trial's stem suffix key;
  near-form tier = best folded difflib ratio >= 0.80 against MW (deterministic
                   tie-break; a review flag, NOT proof of presence — the
                   kAritra~kArita 0.92 trap).

Deterministic: stdlib only, no set iteration reaches an output, byte-stable
rerun.    python scripts/mw_vs_pw_missing_build.py [--v02 DIR] [--out-data DIR]
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import sys
import time
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_V02 = Path(os.environ.get(
    "CSL_ORIG_V02",
    os.path.join(os.path.expanduser("~"), "Documents", "GitHub", "csl-orig", "v02"),
))

RE_HDR = re.compile(r"^<L>([^<\s]+)<pc>([^<]*)<k1>([^<\s]*)<k2>([^<\s]*)")
RE_LS = re.compile(r"<ls(?:\s[^>]*)?>(.*?)</ls>", re.S)

# H7463 Stage-1 substrate pins this job deliberately reuses (data/pwg_dcs).
PWGDCS_PINS = ROOT / "data" / "pwg_dcs" / "pwg_substrate_pins.json"
PWG_SHA_PIN = "430c910f8b0c9229d89ef1580b2385883ce5f4e2ee83dfc6ecb7d6251bb62166"
PWG_ENTRIES_PIN = 123366

SOURCES = [  # code -> relative machine text under v02/
    ("pwg", "pwg/pwg.txt"),
    ("pw", "pw/pw.txt"),
    ("pwkvn", "pwkvn/pwkvn.txt"),
]
MW_REL = "mw/mw.txt"
CORROB_EXCLUDE = {"mw", "mw72", "mwe", "pw", "pwg", "pwkvn", "etymology_stats"}

SLP1_IAST = {
    "A": "ā", "I": "ī", "U": "ū", "f": "ṛ", "F": "ṝ", "x": "ḷ", "X": "ḹ",
    "E": "ai", "O": "au", "M": "ṃ", "H": "ḥ", "N": "ṅ", "Y": "ñ", "w": "ṭ",
    "W": "ṭh", "q": "ḍ", "Q": "ḍh", "R": "ṇ", "T": "th", "D": "dh", "L": "ḻ",
    "S": "ś", "z": "ṣ", "K": "kh", "G": "gh", "C": "ch", "J": "jh",
    "P": "ph", "B": "bh",
}


def iast(s: str) -> str:
    return "".join(SLP1_IAST.get(c, c) for c in s)


def clean(hw: str) -> str:
    """Keep SLP1 letters only (strip *-markers, accents, digits, separators)."""
    return "".join(c for c in hw if c.isalpha())


def stemkey(hw: str) -> str:
    c = clean(hw)
    for suf in ("aH", "aM", "as", "am", "an", "at", "eH", "oH",
                "A", "a", "I", "i", "U", "u", "F", "f", "o", "e"):
        if c.endswith(suf) and len(c) > len(suf):
            return c[: -len(suf)]
    return c


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iter_entries(path: Path):
    """Yield dicts: L, pc, k1, k2, line (1-based <L> header line), ls payloads."""
    cur = None
    with open(path, encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            m = RE_HDR.match(line)
            if m:
                if cur is not None:
                    yield cur
                cur = {"L": m.group(1), "pc": m.group(2), "k1": m.group(3),
                       "k2": m.group(4), "line": lineno, "ls": []}
                continue
            if cur is None or line.startswith("<LEND>"):
                if cur is not None and line.startswith("<LEND>"):
                    yield cur
                    cur = None
                continue
            for tag_m in RE_LS.finditer(line):
                cur["ls"].append(tag_m.group(1))
    if cur is not None:
        yield cur


def cited_payloads(entry) -> list:
    """<ls> payloads carrying at least one alphanumeric char (citation tags)."""
    out = []
    for p in entry["ls"]:
        if any(ch.isalnum() for ch in p):
            out.append(" ".join(p.split()))
    return out


def fold(s: str) -> str:
    return s.lower()


def main() -> int:
    t0 = time.time()
    ap = argparse.ArgumentParser()
    ap.add_argument("--v02", type=Path, default=DEFAULT_V02)
    ap.add_argument("--out-data", type=Path,
                    default=ROOT / "data" / "mw_vs_pw")
    args = ap.parse_args()
    v02 = args.v02
    out_dir: Path = args.out_data
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- substrate reuse gate: pwg.txt must equal the H7463 Stage-1 pin ----
    pwg_path = v02 / "pwg" / "pwg.txt"
    pwg_sha = sha256(pwg_path)
    substrate_pin = {}
    if PWGDCS_PINS.is_file():
        substrate_pin = json.loads(PWGDCS_PINS.read_text(encoding="utf-8"))
    if pwg_sha != PWG_SHA_PIN:
        print(f"REFUSED: pwg.txt sha256 {pwg_sha[:12]}… != H7463 Stage-1 pin "
              f"{PWG_SHA_PIN[:12]}… — the substrate changed, re-pin deliberately",
              file=sys.stderr)
        return 1
    print(f"[substrate] pwg.txt sha256 == H7463 pin ({pwg_sha[:12]}…) OK", flush=True)

    # ---- MW inventory (k1 + k2 aliases), stem index, fuzzy buckets ----
    mw_inv: set = set()
    mw_entries = 0
    for e in iter_entries(v02 / MW_REL):
        mw_entries += 1
        for hw in (e["k1"], e["k2"]):
            c = clean(hw)
            if c:
                mw_inv.add(c)
    stem_index: dict = defaultdict(list)
    for hw in sorted(mw_inv):
        stem_index[stemkey(hw)].append(hw)
    buckets: dict = defaultdict(list)
    for hw in sorted(mw_inv):
        buckets[(fold(hw)[0], len(hw))].append(hw)
    print(f"[mw] entries={mw_entries} distinct base headwords (k1∪k2)={len(mw_inv)}",
          flush=True)

    # ---- source inventories with per-headword aggregation ----
    src_stats: dict = {}
    agg: dict = defaultdict(dict)  # hw -> {code: {...}}
    for code, rel in SOURCES:
        path = v02 / rel
        n_entries = 0
        hw_entries: dict = {}
        for e in iter_entries(path):
            n_entries += 1
            hw = clean(e["k1"])
            if not hw:
                continue
            cp = cited_payloads(e)
            rec = hw_entries.setdefault(hw, {
                "n_entries": 0, "n_cited": 0, "n_ls": 0,
                "best_line": None, "best_L": None, "best_pc": None,
                "best_k1": None, "best_k2": None, "sample": None,
            })
            rec["n_entries"] += 1
            rec["n_ls"] += len(e["ls"])
            better = (rec["best_line"] is None) or (cp and rec["n_cited"] == 0)
            if cp:
                rec["n_cited"] += 1
            if better:
                rec.update({"best_line": e["line"], "best_L": e["L"],
                            "best_pc": e["pc"], "best_k1": e["k1"],
                            "best_k2": e["k2"],
                            "sample": (cp[0][:90] if cp else "")})
        for hw, rec in hw_entries.items():
            agg[hw][code] = rec
        src_stats[code] = {
            "file": rel.replace("/", "/"),
            "bytes": path.stat().st_size,
            "sha256": sha256(path),
            "entries": n_entries,
            "distinct_base": len(hw_entries),
        }
        print(f"[{code}] entries={n_entries} distinct base k1={len(hw_entries)} "
              f"({time.time()-t0:.0f}s)", flush=True)

    # substrate register cross-check (H7463): PWG entries pinned at 123,366
    if src_stats["pwg"]["entries"] != PWG_ENTRIES_PIN:
        print(f"REFUSED: pwg entry count {src_stats['pwg']['entries']} != "
              f"H7463 pin {PWG_ENTRIES_PIN}", file=sys.stderr)
        return 1
    print(f"[substrate] pwg entries == {PWG_ENTRIES_PIN} (H7463 pin) OK", flush=True)

    # ---- corroboration shelf: every other v02 dictionary, k1 inventories ----
    corroborators: dict = {}
    for d in sorted(p for p in v02.iterdir() if p.is_dir()):
        if d.name in CORROB_EXCLUDE:
            continue
        f = d / f"{d.name}.txt"
        if not f.is_file():
            continue
        inv = set()
        for e in iter_entries(f):
            c = clean(e["k1"])
            if c:
                inv.add(c)
        corroborators[d.name] = inv
    print(f"[corroboration] {len(corroborators)} dictionaries: "
          f"{','.join(sorted(corroborators))} ({time.time()-t0:.0f}s)", flush=True)

    # ---- the join: candidates = PWG∪pwk base headwords absent from MW ----
    universe = set(agg.keys())
    exact = {hw for hw in universe if hw in mw_inv}
    candidates = sorted(universe - exact)

    def fuzzy_best(hw: str):
        """Best MW near-form, deterministic (trial tie-break: case-sensitive
        ratio, then lexicographically smallest candidate)."""
        fk = fold(hw)
        best, bc, bcs = 0.0, "", None
        cset = set(hw)
        for ln in (len(hw) - 1, len(hw), len(hw) + 1):
            for cand in buckets.get((fk[0], ln), ()):
                inter = len(cset & set(cand))
                if inter / max(len(cset | set(cand)), 1) < 0.7:
                    continue
                r = difflib.SequenceMatcher(None, fk, fold(cand)).ratio()
                if r > best:
                    best, bc, bcs = r, cand, None
                elif r == best and r > 0.0:
                    if bcs is None:
                        bcs = difflib.SequenceMatcher(None, hw, bc).ratio()
                    cs = difflib.SequenceMatcher(None, hw, cand).ratio()
                    if cs > bcs or (cs == bcs and cand < bc):
                        bc, bcs = cand, cs
        return best, bc

    rows = []
    n_a = n_b = 0
    sub_counts = defaultdict(int)
    for hw in candidates:
        per = agg[hw]
        cited = any(rec["n_cited"] > 0 for rec in per.values())
        # resolution tier against MW
        sk = stemkey(hw)
        tier, mw_match, ratio = "NO-MATCH", "", 0.0
        if sk in stem_index:
            tier, mw_match = "stem", stem_index[sk][0]
        else:
            r, bc = fuzzy_best(hw)
            if r >= 0.80:
                tier, mw_match, ratio = "nearform", bc, round(r, 2)
        if tier == "NO-MATCH":
            subclass = "mw_lacks"
        else:
            subclass = "form_unresolved_" + tier
        cls = "a_missing_by_error" if cited else "b_expected_absence"
        if cited:
            n_a += 1
        else:
            n_b += 1
        sub_counts[f"{cls}.{subclass}"] += 1
        corr = [code for code in sorted(corroborators) if hw in corroborators[code]]
        ev = []
        for code in ("pwg", "pw", "pwkvn"):
            if code in per:
                r_ = per[code]
                ev.append(f"{code}.txt:{r_['best_line']} L={r_['best_L']} "
                          f"pc={r_['best_pc']} k1={r_['best_k1']} "
                          f"cited={r_['n_cited']}/{r_['n_entries']}"
                          + (f' ls="{r_["sample"]}"' if r_["sample"] else ""))
        rows.append({
            "class": cls, "subclass": subclass, "slp1": hw, "iast": iast(hw),
            "sources": "+".join(c for c in ("pwg", "pw", "pwkvn") if c in per),
            "mw_tier": tier, "mw_fuzzy": mw_match, "fuzzy_ratio": ratio,
            "corroboration_n": len(corr),
            "corroboration_dicts": ",".join(corr),
            "evidence": " | ".join(ev),
        })
    print(f"[join] universe={len(universe)} exact-in-MW={len(exact)} "
          f"candidates={len(candidates)} (a={n_a} b={n_b}) ({time.time()-t0:.0f}s)",
          flush=True)

    # ---- canary: the motivating case must reproduce ----
    ka = next((r for r in rows if r["slp1"] == "kAritra"), None)
    assert ka is not None, "canary kAritra must be a candidate"
    # the known ground truth (14-09 trial): kAritra is absent from mw.txt and
    # fuzzy-hits the DIFFERENT word kArita at 0.92 — the near-form trap itself
    assert ka["class"] == "a_missing_by_error", ka
    assert ka["subclass"] == "form_unresolved_nearform", ka
    assert ka["mw_fuzzy"] == "kArita" and ka["fuzzy_ratio"] == 0.92, ka
    assert "pw" in ka["sources"] and "pwkvn" in ka["sources"], ka
    print(f"[canary] kAritra -> {ka['class']}/{ka['subclass']} "
          f"sources={ka['sources']} corrob={ka['corroboration_dicts']}", flush=True)
    assert "kArApaka" in mw_inv, "sanity: kArApaka must resolve in MW"

    # ---- outputs ----
    per_source_cls = {}
    for code, rel in SOURCES:
        src_hws = {hw for hw, per in agg.items() if code in per}
        per_source_cls[code] = {
            "entries": src_stats[code]["entries"],
            "distinct_base": src_stats[code]["distinct_base"],
            "in_mw_exact": len(src_hws & mw_inv),
            "candidates": len(src_hws - mw_inv),
            "a_missing_by_error": sum(1 for r in rows if code in r["sources"].split("+")
                                      and r["class"] == "a_missing_by_error"),
            "b_expected_absence": sum(1 for r in rows if code in r["sources"].split("+")
                                      and r["class"] == "b_expected_absence"),
        }
    metrics = {
        "dataset": "mw_vs_pw/mw_missing_entries_scan",
        "created": "2026-10-31",
        "handoff": "H7513",
        "question": "csl-corrections #119 / Telegram #502926 (KnbRao 14-09-2026)",
        "definitions": {
            "base_headword": "clean(k1); MW side also resolves clean(k2) aliases",
            "pwk": "pw.txt + pwkvn.txt (kürzerer Fassung incl. Nachträge)",
            "cited": ">=1 <ls> tag with >=1 alphanumeric char in payload, in any "
                     "entry of that headword in pwg/pw/pwkvn (raw-tag notion)",
            "a_missing_by_error": "candidate (absent from MW exact) that PWG/pwk cite; "
                                  "covers 'MW lacks it' and 'MW has it under a form "
                                  "that no longer resolves' (stem/nearform subclasses)",
            "b_expected_absence": "candidate absent from MW exact that PWG/pwk never "
                                  "cite (derivative entries)",
            "nearform": "difflib folded ratio >= 0.80, deterministic tie-break; "
                        "review flag, NOT proof of presence",
        },
        "substrate_reuse": {
            "pwg_txt_sha256": pwg_sha,
            "pwg_dcs_pin_file": "data/pwg_dcs/pwg_substrate_pins.json",
            "pwg_dcs_pin_sha_matches": substrate_pin.get("pwg_txt", {}).get(
                "sha256") == pwg_sha,
            "pwg_entries_pin": PWG_ENTRIES_PIN,
        },
        "mw": {"entries": mw_entries, "distinct_base": len(mw_inv)},
        "sources": {c: src_stats[c] for c, _ in SOURCES},
        "pwk_union": {
            "entries": src_stats["pw"]["entries"] + src_stats["pwkvn"]["entries"],
            "distinct_base": len({hw for hw, per in agg.items()
                                  if "pw" in per or "pwkvn" in per}),
        },
        "comparison_universe": {
            "denominator": len(universe),
            "definition": "|distinct base k1 headwords in PWG ∪ pwk|",
            "in_mw_exact": len(exact),
            "candidates_total": len(candidates),
        },
        "classes": {
            "a_missing_by_error": {
                "count": n_a,
                "denominator": len(universe),
                "subclasses": dict(sorted(
                    (k, v) for k, v in sub_counts.items()
                    if k.startswith("a_"))),
            },
            "b_expected_absence": {
                "count": n_b,
                "denominator": len(universe),
                "subclasses": dict(sorted(
                    (k, v) for k, v in sub_counts.items()
                    if k.startswith("b_"))),
            },
        },
        "per_source": per_source_cls,
        "corroboration": {
            "dictionaries": sorted(corroborators),
            "a_with_ge1": sum(1 for r in rows if r["class"] == "a_missing_by_error"
                              and r["corroboration_n"] >= 1),
            "a_with_ge2": sum(1 for r in rows if r["class"] == "a_missing_by_error"
                              and r["corroboration_n"] >= 2),
            "a_nomatch_with_ge2": sum(
                1 for r in rows if r["class"] == "a_missing_by_error"
                and r["subclass"] == "mw_lacks" and r["corroboration_n"] >= 2),
        },
        "canary": {"kAritra": {
            "class": ka["class"], "subclass": ka["subclass"],
            "sources": ka["sources"], "mw_tier": ka["mw_tier"],
            "corroboration_dicts": ka["corroboration_dicts"]}},
    }
    (out_dir / "mw_vs_pw_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    pins = {
        "created": "2026-10-31",
        "dataset": "mw_vs_pw/substrate_pins",
        "license": "CC-BY-SA-4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "note": "machine texts live off-git in csl-orig (never committed); "
                "pwg.txt is pinned to the H7463 Stage-1 substrate sha",
        "mw_txt": {"path": str((v02 / MW_REL)), "bytes": (v02 / MW_REL).stat().st_size,
                   "sha256": sha256(v02 / MW_REL), "entries": mw_entries},
        "sources": src_stats,
        "corroboration_shas": {c: sha256(v02 / c / f"{c}.txt")
                               for c in sorted(corroborators)},
    }
    (out_dir / "substrate_pins.json").write_text(
        json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cols = ["class", "subclass", "slp1", "iast", "sources", "mw_tier", "mw_fuzzy",
            "fuzzy_ratio", "corroboration_n", "corroboration_dicts", "evidence"]
    with open(out_dir / "mw_missing_candidates.tsv", "w", encoding="utf-8",
              newline="") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in sorted(rows, key=lambda r: (r["class"], r["slp1"])):
            fh.write("\t".join(str(r[c]) for c in cols) + "\n")

    print(f"[out] {out_dir} ({time.time()-t0:.0f}s) rows={len(rows)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
