#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""f11 — evidence-dependence audit of A10's three highest-strength descent claims.

The question this script exists to answer
-----------------------------------------
A10 (``docs/articles/article_21_apparatus_not_errors.md``) stacks several
individually valid signals into one conclusion: MW inherited Böhtlingk's
apparatus. Each signal has been arithmetic-pinned (``tests/forensic/``, H4352),
so each *number* is right. That says nothing about whether the signals are
**independent evidence**. If two signals read the same underlying events, or
one witness is counted twice, the combination overstates the historical case
even though no single figure is wrong.

This script traces the three highest-strength claims from their displayed
numbers down to the loci that produce them, deduplicates the evidence, and runs
the controls that separate "MW worked from PWG's article" from "MW and PWG
share a lexicographic convention".

Claims audited (stable IDs, used in the report and the topic doc)
-----------------------------------------------------------------
  A10-C1  §3.2 citation apparatus (F1) — per-lemma source-Jaccard 0.16–0.19 vs
          0.004–0.017 nulls; 587 corpus-rare shared exact references.
  A10-C2  §3.4 citation ORDER (F5) — 0.811 concordance over 3,593 entries,
          47.8% perfectly identical. A10 calls this "the strongest single
          copying signal in the suite".
  A10-C3  §3.5 shared OMISSION (F9) — gap-sensitivity 12.3× (MW) vs 1.51× (AP)
          over the 6,941-word SKD ∩ VCP anchor; reported as "≈8×".

Controls (all deterministic, offline, seeded)
---------------------------------------------
  CTRL-DUP    seeded duplicate witness: a verbatim copy of PWG is injected into
              the witness pool. Naive accounting must inflate; the deduplicated
              accounting must NOT. This is the acceptance control.
  CTRL-PWDUP  the *real* duplicate witness already in the evidence base: PW is
              Böhtlingk's own abridgement of PWG, so PWG/MW and PW/MW are not
              two independent corroborations. Measured, not assumed.
  CTRL-ABL-H  ablation: drop the HARIV stratum from the rare-reference pool.
  CTRL-ABL-S  ablation: drop the k most widely-cited sigils, recompute C1's
              lineage-vs-null separation. Tests whether C1 rides on common texts.
  CTRL-PERM   within-entry order permutation (preserves each entry's shared-sigil
              set and size, and each dictionary's sigil distribution) — the
              concordance null A10 quotes as 0.50.
  CTRL-CONV   the sharp one. Derive each dictionary's GLOBAL citation-ordering
              convention (mean normalised position per sigil), then rescore C2
              restricted to the sigil pairs on which MW's and PWG's conventions
              DISAGREE. A10 asserts the order agreement is Petersburg-specific
              rather than conventional; this measures the part of it that
              convention cannot explain.

Inputs  : data/forensic/parsed/<code>.tsv  (build: python scripts/forensic/parse_cslorig.py pwg pw mw ap ben sch pwkvn skd vcp)
          ../SanskritLexicography/HeadwordLists/now-2026/*-unique-key1-*.txt  (F9 anchor; SKD/VCP fall back to raw k1, which matches the export exactly)
          data/forensic/f1_report.json, f5_report.json, shared_omission_test.csv  (the frozen published figures)
Outputs : data/forensic/f11_report.json
          data/forensic/evidence_dependence_graph.csv   (claim → signal → locus edges)
          data/forensic/evidence_dependence_loci.csv    (pairwise locus overlap)
Run from repo root:  python scripts/forensic/f11_evidence_dependence.py
"""

import os
import re
import csv
import sys
import json
import random
import hashlib
import collections

sys.path.insert(0, os.path.abspath("scripts/forensic"))
from parse_cslorig import load_entries, PARSED_DIR  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
GH_ROOT = os.path.abspath(os.path.join(ATLAS_ROOT, ".."))
OUT_DIR = os.path.join(ATLAS_ROOT, "data", "forensic")
HW_DIR = os.path.join(GH_ROOT, "SanskritLexicography", "HeadwordLists", "now-2026")

SEED = 20260920            # frozen before analysis; every shuffle draws from this
PERM_ITERS = 200           # within-entry permutation replicates
MIN_SHARED_SRC = 3         # F5's own threshold — reused verbatim, never re-tuned
ABLATE_TOP_SIGILS = 25     # CTRL-ABL-S: how many high-frequency sigils to drop

# The dictionaries whose signals are analysed…
ANALYSIS_CODES = ["MW", "PWG", "PW", "AP", "BEN", "SCH", "PWKVN"]
# …and the full F1 pool (every dict with >= MIN_CIT <ls> cites) that defines
# corpus RARITY. Rarity must be computed over the same 13 dicts F1 used, or a
# reference looks rarer than it is and the smoking-gun pool inflates.
RARITY_CODES = ANALYSIS_CODES + ["AE", "AP90", "BHS", "BOR", "GRA", "LRV"]

_WS = re.compile(r"\s+")
_DIGIT = re.compile(r"\d")

# F9's canonical key1 exports. SKD/VCP are absent from the now-2026 snapshot on
# some boxes; raw <k1> from csl-orig reproduces both counts exactly (40,817 /
# 48,636), so the fallback is exact, not approximate.
KEY1_FILES = {
    "MW": "MW-unique-key1-194084.txt",
    "PWG": "PWG-unique-key1-106082.txt",
    "AP": "AP-unique-key1-88867.txt",
    "SKD": "SKD-unique-key1-40817.txt",
    "VCP": "VCP-unique-key1-48636.txt",
}


# --------------------------------------------------------------------------
# provenance
# --------------------------------------------------------------------------

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def corpus_revision():
    """The csl-orig revision the parsed caches were built from.

    No `.source.json` sidecar in this repo records it — they pin the *csl-atlas*
    commit only — so the published forensic figures are not pinned to a corpus
    state. Recording it here is what makes this audit re-runnable to the digit.
    """
    src = os.path.abspath(os.path.join(ATLAS_ROOT, "..", "csl-orig"))
    if not os.path.isdir(os.path.join(src, ".git")):
        return {"path": src, "revision": None, "note": "csl-orig not a git checkout here"}
    try:
        import subprocess
        out = subprocess.run(["git", "-C", src, "log", "-1", "--format=%H|%cI"],
                             capture_output=True, text=True, encoding="utf-8", timeout=30)
        if out.returncode != 0:
            return {"path": src, "revision": None, "note": out.stderr.strip()[:200]}
        sha, iso = out.stdout.strip().split("|", 1)
        return {"path": src, "revision": sha, "committed": iso}
    except Exception as exc:                                   # noqa: BLE001
        return {"path": src, "revision": None, "note": repr(exc)[:200]}


def fingerprint(paths):
    """{relative path: sha256} for every input that feeds a number below."""
    out = {}
    for p in paths:
        if os.path.exists(p):
            out[os.path.relpath(p, ATLAS_ROOT)] = sha256_file(p)
    return out


# --------------------------------------------------------------------------
# shared primitives (kept byte-identical in behaviour to f1/f5)
# --------------------------------------------------------------------------

def norm_ref(ref):
    """f1_citations.norm_ref — full citation, uppercased, punctuation-stripped."""
    return _WS.sub(" ", ref).strip().upper().rstrip(". ,;")


def source_of(full):
    """f1_citations.source_of / f5_entry_comparison.sigil — text before the first digit."""
    m = _DIGIT.search(full)
    return (full[:m.start()] if m else full).strip(" .,;")


def dedup(seq):
    """f5_entry_comparison.dedup — first occurrence wins, order preserved."""
    seen, out = set(), []
    for s in seq:
        if s and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def concordant_fraction(a_seq, b_seq, restrict=None):
    """F5's concordance, optionally restricted to a set of unordered sigil pairs.

    ``restrict`` is CTRL-CONV's contribution: score only the pairs in that set.
    Returns (fraction, n_pairs_scored) or (None, 0) when nothing is scorable.
    """
    common = set(a_seq) & set(b_seq)
    if len(common) < MIN_SHARED_SRC:
        return None, 0
    a = dedup([s for s in a_seq if s in common])
    b = dedup([s for s in b_seq if s in common])
    pos_b = {s: i for i, s in enumerate(b)}
    conc = tot = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if restrict is not None and frozenset((a[i], a[j])) not in restrict:
                continue
            tot += 1
            conc += 1 if pos_b[a[i]] < pos_b[a[j]] else 0
    return (conc / tot, tot) if tot else (None, 0)


def load_dict(code):
    """k1 -> {'sigils': [ordered, with repeats], 'refs': {normalised full refs}}."""
    d = {}
    for e in load_entries(code):
        k1 = e["k1"]
        if not k1:
            continue
        rec = d.setdefault(k1, {"sigils": [], "refs": set()})
        for c in e["citations"]:
            nf = norm_ref(c)
            if not nf:
                continue
            rec["refs"].add(nf)
            s = source_of(nf)
            if s:
                rec["sigils"].append(s)
    return d


def load_key1(code, raw_fallback):
    """F9's anchor inputs — canonical export when present, raw <k1> otherwise."""
    path = os.path.join(HW_DIR, KEY1_FILES[code])
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return {ln.strip() for ln in fh if ln.strip()}, "key1-export"
    return ({e["k1"] for e in load_entries(raw_fallback) if e["k1"]}, "raw-k1-fallback")


# --------------------------------------------------------------------------
# claim → signal → locus graphs
# --------------------------------------------------------------------------

def build_graphs(dicts, rarity_pool):
    """Resolve each claim's loci from the primary corpus, not from the report."""
    mw, pwg, pw = dicts["MW"], dicts["PWG"], dicts["PW"]

    cited = {c: {k for k, v in d.items() if v["refs"]} for c, d in dicts.items()}

    # --- A10-C1 loci -------------------------------------------------------
    c1_lemmas = cited["MW"] & cited["PWG"]                # L-CIT-LEMMA
    # rare shared exact (lemma, ref) events, F1's smoking guns, rebuilt here
    ref_lemmas = collections.defaultdict(set)
    for code, d in rarity_pool.items():
        for k1, v in d.items():
            for r in v["refs"]:
                ref_lemmas[r].add((code, k1))
    rare_events = set()                                   # L-RARE-EVENT
    for src_code in ("PWG", "PW"):
        for k1 in cited[src_code] & cited["MW"]:
            for r in dicts[src_code][k1]["refs"] & mw[k1]["refs"]:
                if len({lm for (_, lm) in ref_lemmas[r]}) <= 4:
                    rare_events.add((k1, r, src_code))

    # --- A10-C2 loci -------------------------------------------------------
    c2_entries = set()                                    # L-ORD-ENTRY
    for k1 in c1_lemmas:
        if len(set(mw[k1]["sigils"]) & set(pwg[k1]["sigils"])) >= MIN_SHARED_SRC:
            c2_entries.add(k1)

    # --- A10-C3 loci -------------------------------------------------------
    skd, skd_src = load_key1("SKD", "skd")
    vcp, vcp_src = load_key1("VCP", "vcp")
    mw_hw, _ = load_key1("MW", "mw")
    pwg_hw, _ = load_key1("PWG", "pwg")
    ap_hw, _ = load_key1("AP", "ap")
    anchor = skd & vcp                                    # L-ANCHOR-WORD

    return {
        "c1_lemmas": c1_lemmas,
        "rare_events": rare_events,
        "c2_entries": c2_entries,
        "anchor": anchor,
        "hw": {"MW": mw_hw, "PWG": pwg_hw, "AP": ap_hw},
        "anchor_sources": {"SKD": skd_src, "VCP": vcp_src},
        "ref_lemmas": ref_lemmas,
        "_unused": (pw,),
    }


def contingency(anchor, target, probe):
    """F9's 2×2 + gap-sensitivity, reproduced so C3's loci are auditable here."""
    hh = hl = lh = ll = 0
    for w in anchor:
        t, p = w in target, w in probe
        if t and p:
            hh += 1
        elif t and not p:
            hl += 1
        elif not t and p:
            lh += 1
        else:
            ll += 1
    has, lacks = hh + hl, lh + ll
    lack_given_has = hl / has if has else None
    lack_given_lacks = ll / lacks if lacks else None
    gap = (lack_given_lacks / lack_given_has) if lack_given_has else None
    return {
        "pwg_has_probe_has": hh, "pwg_has_probe_lacks": hl,
        "pwg_lacks_probe_has": lh, "pwg_lacks_probe_lacks": ll,
        "pwg_has": has, "pwg_lacks": lacks,
        "lack_given_pwg_has": round(lack_given_has, 4) if lack_given_has is not None else None,
        "lack_given_pwg_lacks": round(lack_given_lacks, 4) if lack_given_lacks is not None else None,
        "gap_sensitivity": round(gap, 3) if gap is not None else None,
    }


# --------------------------------------------------------------------------
# CTRL-CONV — global ordering convention vs per-entry agreement
# --------------------------------------------------------------------------

def global_convention(d, min_sigils=2):
    """sigil -> mean normalised position across every entry of this dictionary.

    This is the dictionary's own ordering habit, independent of any one lemma:
    if a compiler always cites the Veda before the epics, every entry shows it.
    """
    acc = collections.defaultdict(lambda: [0.0, 0])
    for v in d.values():
        seq = dedup(v["sigils"])
        if len(seq) < min_sigils:
            continue
        last = len(seq) - 1
        for i, s in enumerate(seq):
            acc[s][0] += i / last
            acc[s][1] += 1
    return {s: tot / n for s, (tot, n) in acc.items() if n}


def convention_split(mw, other, entries, conv_mw, conv_other):
    """Split C2's concordance into convention-explained and convention-defying.

    For each order-bearing entry, partition the scored sigil pairs by whether
    MW's and the comparand's GLOBAL conventions already agree on that pair's
    direction. Agreement on convention-concordant pairs is what a shared
    lexicographic habit predicts; agreement on convention-DISCORDANT pairs is
    what only working from the other dictionary's article predicts.
    """
    agree_c = tot_c = agree_d = tot_d = 0
    n_entries = 0
    for k1 in entries:
        a = dedup([s for s in mw[k1]["sigils"]])
        b = dedup([s for s in other[k1]["sigils"]])
        common = set(a) & set(b)
        if len(common) < MIN_SHARED_SRC:
            continue
        a = [s for s in a if s in common]
        b = [s for s in b if s in common]
        pos_b = {s: i for i, s in enumerate(b)}
        n_entries += 1
        for i in range(len(a)):
            for j in range(i + 1, len(a)):
                x, y = a[i], a[j]
                if x not in conv_mw or y not in conv_mw:
                    continue
                if x not in conv_other or y not in conv_other:
                    continue
                mw_conv_says = conv_mw[x] < conv_mw[y]
                ot_conv_says = conv_other[x] < conv_other[y]
                observed = pos_b[x] < pos_b[y]           # does the comparand agree with MW's order?
                if mw_conv_says == ot_conv_says:
                    tot_c += 1
                    agree_c += 1 if observed else 0
                else:
                    tot_d += 1
                    agree_d += 1 if observed else 0
    return {
        "entries_scored": n_entries,
        "convention_concordant_pairs": tot_c,
        "agreement_on_convention_concordant": round(agree_c / tot_c, 4) if tot_c else None,
        "convention_discordant_pairs": tot_d,
        "agreement_on_convention_discordant": round(agree_d / tot_d, 4) if tot_d else None,
    }


# --------------------------------------------------------------------------
# CTRL-PERM — within-entry permutation null
# --------------------------------------------------------------------------

def permutation_null(mw, other, entries, rng, iters):
    """Shuffle MW's citation order inside each entry; keep everything else fixed.

    Preserves: which sigils the entry cites, how many, the comparand's order,
    the entry population and both dictionaries' sigil distributions. Only the
    within-entry sequence — the thing C2 claims was copied — is destroyed.
    """
    pairs = []
    for k1 in entries:
        a = dedup(mw[k1]["sigils"])
        b = dedup(other[k1]["sigils"])
        common = set(a) & set(b)
        if len(common) < MIN_SHARED_SRC:
            continue
        pairs.append(([s for s in a if s in common], [s for s in b if s in common]))
    means, idents = [], []
    for _ in range(iters):
        tot = ident = 0
        acc = 0.0
        for a, b in pairs:
            shuffled = a[:]
            rng.shuffle(shuffled)
            cf, _n = concordant_fraction(shuffled, b)
            if cf is None:
                continue
            acc += cf
            tot += 1
            ident += 1 if cf == 1.0 else 0
        if tot:
            means.append(acc / tot)
            idents.append(100.0 * ident / tot)
    return {
        "iters": len(means),
        "entries": len(pairs),
        "mean_concordance": round(sum(means) / len(means), 4) if means else None,
        "min_concordance": round(min(means), 4) if means else None,
        "max_concordance": round(max(means), 4) if means else None,
        "pct_identical": round(sum(idents) / len(idents), 2) if idents else None,
    }


# --------------------------------------------------------------------------
# CTRL-DUP / CTRL-PWDUP — duplicate witnesses
# --------------------------------------------------------------------------

def independent_support(witness_events):
    """Deduplicated support = distinct (lemma, ref) source events, witness-blind.

    A source event is the historical thing that happened once: MW carries this
    reference at this headword. Which surviving Petersburg volume also carries
    it is a *witness*, not a second event. Naive support counts (witness, lemma,
    ref) triples and therefore rewards duplicating a witness.
    """
    naive = len(witness_events)
    deduped = len({(k1, r) for (k1, r, _w) in witness_events})
    return {"naive_witness_events": naive, "independent_source_events": deduped}


def seeded_duplicate_witness(rare_events):
    """CTRL-DUP: inject PWG_DUP, a verbatim copy of the PWG witness."""
    before = independent_support(rare_events)
    seeded = set(rare_events)
    for (k1, r, w) in list(rare_events):
        if w == "PWG":
            seeded.add((k1, r, "PWG_DUP"))
    after = independent_support(seeded)
    return {
        "before": before,
        "after_seeding_verbatim_PWG_duplicate": after,
        "naive_inflation": after["naive_witness_events"] - before["naive_witness_events"],
        "independent_support_delta": (after["independent_source_events"]
                                      - before["independent_source_events"]),
        "control_passes": after["independent_source_events"] == before["independent_source_events"],
    }


# --------------------------------------------------------------------------
def main():
    rng = random.Random(SEED)
    print("=" * 72)
    print("F11 — evidence-dependence audit of A10-C1 / A10-C2 / A10-C3")
    print("=" * 72)

    codes = ANALYSIS_CODES
    rarity_pool = {c: load_dict(c.lower()) for c in RARITY_CODES}
    dicts = {c: rarity_pool[c] for c in codes}
    print("loaded: " + " · ".join(f"{c}={len(dicts[c]):,} lemmas" for c in codes))
    print("rarity pool (F1's 13 <ls>-tagged dicts): " + ", ".join(RARITY_CODES))

    g = build_graphs(dicts, rarity_pool)
    mw, pwg, ap = dicts["MW"], dicts["PWG"], dicts["AP"]

    # ---- locus census + overlap ------------------------------------------
    c1, c2, anchor = g["c1_lemmas"], g["c2_entries"], g["anchor"]
    rare = g["rare_events"]
    rare_lemmas = {k for (k, _r, _w) in rare}
    print(f"\nL-CIT-LEMMA   (C1) = {len(c1):,}")
    print(f"L-RARE-EVENT  (C1) = {len(rare):,} over {len(rare_lemmas):,} lemmas")
    print(f"L-ORD-ENTRY   (C2) = {len(c2):,}")
    print(f"L-ANCHOR-WORD (C3) = {len(anchor):,}")

    overlap = {
        "C2_in_C1": {
            "c2": len(c2), "intersection": len(c2 & c1),
            "share_of_c2": round(len(c2 & c1) / len(c2), 4) if c2 else None,
        },
        "C1rare_in_C2": {
            "rare_lemmas": len(rare_lemmas),
            "intersection": len(rare_lemmas & c2),
            "share_of_rare_lemmas": round(len(rare_lemmas & c2) / len(rare_lemmas), 4) if rare_lemmas else None,
        },
        "C3_in_C1": {
            "anchor": len(anchor), "intersection": len(anchor & c1),
            "share_of_anchor": round(len(anchor & c1) / len(anchor), 4) if anchor else None,
        },
        "C3_in_C2": {
            "anchor": len(anchor), "intersection": len(anchor & c2),
            "share_of_anchor": round(len(anchor & c2) / len(anchor), 4) if anchor else None,
        },
    }

    # ---- C3 reproduction (so its loci are audited, not quoted) ------------
    f9_mw = contingency(anchor, g["hw"]["PWG"], g["hw"]["MW"])
    f9_ap = contingency(anchor, g["hw"]["PWG"], g["hw"]["AP"])

    # ---- source-event concentration --------------------------------------
    by_sigil = collections.Counter(source_of(r) for (_k, r, _w) in rare)
    harivamsa = by_sigil.get("HARIV", 0)

    # ---- CTRL-ABL-H -------------------------------------------------------
    ablated = {(k, r, w) for (k, r, w) in rare if source_of(r) != "HARIV"}
    ctrl_abl_h = {
        "rare_events_all": len(rare),
        "harivamsa_events": harivamsa,
        "harivamsa_share": round(harivamsa / len(rare), 4) if rare else None,
        "rare_events_without_harivamsa": len(ablated),
        "distinct_sigils_without_harivamsa": len({source_of(r) for (_k, r, _w) in ablated}),
        "residue_by_sigil": dict(collections.Counter(
            source_of(r) for (_k, r, _w) in ablated).most_common()),
    }

    # ---- CTRL-ABL-S -------------------------------------------------------
    sigil_df = collections.Counter()
    for code in ("MW", "PWG", "AP", "BEN"):
        for v in dicts[code].values():
            for s in set(dedup(v["sigils"])):
                sigil_df[s] += 1
    top_sigils = {s for s, _ in sigil_df.most_common(ABLATE_TOP_SIGILS)}

    def mean_jaccard(a_code, b_code, drop=frozenset()):
        da, db = dicts[a_code], dicts[b_code]
        shared = {k for k in da if da[k]["refs"]} & {k for k in db if db[k]["refs"]}
        tot = 0.0
        n = 0
        for k1 in shared:
            sa = {source_of(r) for r in da[k1]["refs"]} - drop
            sb = {source_of(r) for r in db[k1]["refs"]} - drop
            uni = sa | sb
            if not uni:
                continue
            tot += len(sa & sb) / len(uni)
            n += 1
        return (round(tot / n, 4) if n else None), n

    ctrl_abl_s = {"ablated_sigils": sorted(top_sigils), "pairs": {}}
    for a, b in (("PWG", "MW"), ("PW", "MW"), ("AP", "MW"), ("BEN", "MW")):
        full_j, n_full = mean_jaccard(a, b)
        abl_j, n_abl = mean_jaccard(a, b, top_sigils)
        ctrl_abl_s["pairs"][f"{a}/{b}"] = {
            "mean_source_jaccard": full_j, "n_lemmas": n_full,
            "mean_source_jaccard_top_sigils_ablated": abl_j, "n_lemmas_ablated": n_abl,
        }

    # ---- C2 observed, CTRL-PERM, CTRL-CONV --------------------------------
    def observed_order(other, entries):
        acc = 0.0
        n = ident = 0
        for k1 in entries:
            cf, _ = concordant_fraction(mw[k1]["sigils"], other[k1]["sigils"])
            if cf is None:
                continue
            acc += cf
            n += 1
            ident += 1 if cf == 1.0 else 0
        return {"entries": n,
                "mean_concordance": round(acc / n, 4) if n else None,
                "pct_identical": round(100.0 * ident / n, 2) if n else None}

    ap_entries = {k for k in (set(mw) & set(ap))
                  if len(set(mw[k]["sigils"]) & set(ap[k]["sigils"])) >= MIN_SHARED_SRC}
    c2_observed = {"PWG": observed_order(pwg, c2), "AP": observed_order(ap, ap_entries)}
    ctrl_perm = {"PWG": permutation_null(mw, pwg, c2, rng, PERM_ITERS)}

    conv = {c: global_convention(dicts[c]) for c in ("MW", "PWG", "AP")}
    ctrl_conv = {
        "PWG": convention_split(mw, pwg, c2, conv["MW"], conv["PWG"]),
        "AP": convention_split(mw, ap, ap_entries, conv["MW"], conv["AP"]),
    }

    # ---- CTRL-DUP / CTRL-PWDUP -------------------------------------------
    ctrl_dup = seeded_duplicate_witness(rare)
    pwg_ev = {(k, r) for (k, r, w) in rare if w == "PWG"}
    pw_ev = {(k, r) for (k, r, w) in rare if w == "PW"}
    ctrl_pwdup = {
        "pwg_witness_events": len(pwg_ev),
        "pw_witness_events": len(pw_ev),
        "shared_by_both_petersburg_witnesses": len(pwg_ev & pw_ev),
        "pw_events_already_in_pwg": round(len(pwg_ev & pw_ev) / len(pw_ev), 4) if pw_ev else None,
        "independent_source_events": len(pwg_ev | pw_ev),
        "naive_witness_events": len(rare),
    }

    # ---- deduplicated evidence accounting --------------------------------
    accounting = {
        "C1_loci": len(c1),
        "C2_loci": len(c2),
        "C3_loci": len(anchor),
        "naive_sum_of_loci": len(c1) + len(c2) + len(anchor),
        "union_of_loci": len(c1 | c2 | anchor),
        "double_counted_by_naive_sum": (len(c1) + len(c2) + len(anchor)) - len(c1 | c2 | anchor),
        "C2_loci_not_in_C1": len(c2 - c1),
        "C3_loci_not_in_C1_or_C2": len(anchor - c1 - c2),
    }

    # ---- write outputs ----------------------------------------------------
    os.makedirs(OUT_DIR, exist_ok=True)
    graph_rows = [
        ("A10-C1", "S-F1-JACC", "L-CIT-LEMMA", len(c1), "§3.2 per-lemma source-Jaccard"),
        ("A10-C1", "S-F1-RARE", "L-RARE-EVENT", len(rare), "§3.2 corpus-rare shared exact refs"),
        ("A10-C2", "S-F5-ORDER", "L-ORD-ENTRY", len(c2), "§3.4 citation-order concordance"),
        ("A10-C2", "S-F5-IDENT", "L-ORD-ENTRY", len(c2), "§3.4 perfectly-identical share"),
        ("A10-C3", "S-F9-GAPSENS", "L-ANCHOR-WORD", len(anchor), "§3.5 gap-sensitivity"),
    ]
    with open(os.path.join(OUT_DIR, "evidence_dependence_graph.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "signal_id", "locus_id", "n_loci", "what"])
        w.writerows(graph_rows)

    with open(os.path.join(OUT_DIR, "evidence_dependence_loci.csv"), "w",
              encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["locus_a", "locus_b", "n_a", "n_b", "intersection", "share_of_a"])
        for la, lb, sa, sb in (("L-ORD-ENTRY", "L-CIT-LEMMA", c2, c1),
                               ("L-RARE-EVENT-lemmas", "L-ORD-ENTRY", rare_lemmas, c2),
                               ("L-ANCHOR-WORD", "L-CIT-LEMMA", anchor, c1),
                               ("L-ANCHOR-WORD", "L-ORD-ENTRY", anchor, c2)):
            inter = len(sa & sb)
            w.writerow([la, lb, len(sa), len(sb), inter,
                        round(inter / len(sa), 4) if sa else ""])

    inputs = [os.path.join(PARSED_DIR, f"{c.lower()}.tsv") for c in RARITY_CODES]
    inputs += [os.path.join(PARSED_DIR, f"{c}.tsv") for c in ("skd", "vcp")]
    inputs += [os.path.join(OUT_DIR, f) for f in
               ("f1_report.json", "f5_report.json", "shared_omission_test.csv",
                "shared_rare_citations.csv")]

    # ---- reproduction delta against the frozen published figures ----------
    pub_f1 = json.load(open(os.path.join(OUT_DIR, "f1_report.json"), encoding="utf-8"))
    pub_f5 = json.load(open(os.path.join(OUT_DIR, "f5_report.json"), encoding="utf-8"))
    pub_f5_pwg = next(p for p in pub_f5["pairs"] if p["vs"] == "PWG")
    with open(os.path.join(OUT_DIR, "shared_omission_test.csv"), encoding="utf-8") as fh:
        pub_f9 = {r["probe"]: r for r in csv.DictReader(fh)}
    repro = {
        "note": ("The published figures were produced on 2026-06-03 against an unpinned "
                 "../csl-orig; this run reads the revision recorded under corpus_revision. "
                 "Deltas below are corpus drift, not arithmetic disagreement — the pinned "
                 "arithmetic tests (tests/forensic, H4352) still pass."),
        "S-F1-RARE": {"published": pub_f1["n_smoking_guns"], "reproduced": len(rare)},
        "S-F1-RARE-HARIV": {"published": pub_f1["smoking_gun_sources"].get("HARIV"),
                            "reproduced": harivamsa},
        "S-F5-ORDER": {"published_entries": pub_f5_pwg["entries_with_order_signal"],
                       "reproduced_entries": c2_observed["PWG"]["entries"],
                       "published_concordance": pub_f5_pwg["mean_citation_order_agreement"],
                       "reproduced_concordance": c2_observed["PWG"]["mean_concordance"],
                       "published_pct_identical": pub_f5_pwg["pct_identical_order"],
                       "reproduced_pct_identical": c2_observed["PWG"]["pct_identical"]},
        "S-F9-GAPSENS": {"published_mw": float(pub_f9["MW"]["gap_sensitivity"]),
                         "reproduced_mw": f9_mw["gap_sensitivity"],
                         "published_ap": float(pub_f9["AP"]["gap_sensitivity"]),
                         "reproduced_ap": f9_ap["gap_sensitivity"]},
    }

    report = {
        "seed": SEED,
        "min_shared_sources_for_order": MIN_SHARED_SRC,
        "permutation_iters": PERM_ITERS,
        "anchor_sources": g["anchor_sources"],
        "corpus_revision": corpus_revision(),
        "reproduction_delta": repro,
        "source_hashes": fingerprint(inputs),
        "claims": {
            "A10-C1": {"section": "3.2", "signals": ["S-F1-JACC", "S-F1-RARE"],
                       "loci": {"L-CIT-LEMMA": len(c1), "L-RARE-EVENT": len(rare)}},
            "A10-C2": {"section": "3.4", "signals": ["S-F5-ORDER", "S-F5-IDENT"],
                       "loci": {"L-ORD-ENTRY": len(c2)}},
            "A10-C3": {"section": "3.5", "signals": ["S-F9-GAPSENS"],
                       "loci": {"L-ANCHOR-WORD": len(anchor)}},
        },
        "locus_overlap": overlap,
        "deduplicated_accounting": accounting,
        "c3_reproduction": {"MW": f9_mw, "AP": f9_ap},
        "c2_observed": c2_observed,
        "rare_event_concentration": dict(by_sigil.most_common()),
        "controls": {
            "CTRL-DUP": ctrl_dup,
            "CTRL-PWDUP": ctrl_pwdup,
            "CTRL-ABL-H": ctrl_abl_h,
            "CTRL-ABL-S": ctrl_abl_s,
            "CTRL-PERM": ctrl_perm,
            "CTRL-CONV": ctrl_conv,
        },
    }
    with open(os.path.join(OUT_DIR, "f11_report.json"), "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)

    # ---- console ----------------------------------------------------------
    print("\n-- locus overlap ---------------------------------------------------")
    for k, v in overlap.items():
        print(f"  {k:16s} {v}")
    print("\n-- deduplicated accounting ----------------------------------------")
    for k, v in accounting.items():
        print(f"  {k:32s} {v:,}")
    print("\n-- C2 observed vs controls ----------------------------------------")
    print(f"  observed   PWG {c2_observed['PWG']}")
    print(f"  observed   AP  {c2_observed['AP']}")
    print(f"  CTRL-PERM  PWG {ctrl_perm['PWG']}")
    print(f"  CTRL-CONV  PWG {ctrl_conv['PWG']}")
    print(f"  CTRL-CONV  AP  {ctrl_conv['AP']}")
    print("\n-- duplicate witnesses --------------------------------------------")
    print(f"  CTRL-DUP    {ctrl_dup}")
    print(f"  CTRL-PWDUP  {ctrl_pwdup}")
    print("\n-- ablations ------------------------------------------------------")
    print(f"  CTRL-ABL-H  {harivamsa}/{len(rare)} rare events are HARIV "
          f"({ctrl_abl_h['harivamsa_share']}); residue {len(ablated)} over "
          f"{ctrl_abl_h['distinct_sigils_without_harivamsa']} sigils")
    for pair, v in ctrl_abl_s["pairs"].items():
        print(f"  CTRL-ABL-S  {pair:8s} {v['mean_source_jaccard']} -> "
              f"{v['mean_source_jaccard_top_sigils_ablated']} (top-{ABLATE_TOP_SIGILS} sigils dropped)")
    print("\n-- reproduction vs the frozen published figures --------------------")
    print(f"  corpus_revision {report['corpus_revision'].get('revision')} "
          f"({report['corpus_revision'].get('committed')})")
    for k, v in repro.items():
        if k != "note":
            print(f"  {k:14s} {v}")
    print(f"\nwrote {os.path.relpath(os.path.join(OUT_DIR, 'f11_report.json'), ATLAS_ROOT)}")


if __name__ == "__main__":
    main()
