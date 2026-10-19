"""The report renderer (one source of the published table and the verdict text)."""
from __future__ import annotations

from .core import *                     # noqa: F401,F403 - constants + helpers
from .core import (ALPHA, CLOCKS, DICTS, EFFECT_FLOOR, HANDOFF, MIN_POWER,
                   PRIMARY_CLOCK, REPORT_DATE)

# ------------------------------------------------------------------ report
def fmt(v, nd=3, pct=False):
    if v is None:
        return "—"
    if pct:
        return f"{100 * v:.1f}%"
    if isinstance(v, float):
        return f"{v:+.{nd}f}" if abs(v) < 100 and nd else f"{v:.{nd}f}"
    return str(v)


def render_report(summary: dict) -> str:
    pd = summary["pd_clocks"]
    ctl = summary["controls"]
    verdict = summary["verdict"]
    L = []
    a = L.append
    a(f"# PD sense-order against four non-historical dictionaries — {REPORT_DATE}\n")
    a(f"_Handoff [{HANDOFF}] · script `scripts/pd_sense_order_compare.py` · "
      f"summary `data/pd/pd_sense_order_compare_summary.json`_\n")
    a(f"**Verdict ({PRIMARY_CLOCK.upper()} clock, pre-registered rule): {verdict['text']}**\n")
    a("## What was measured\n")
    a("The object is the order of **senses** inside an entry, not the order of citations "
      "inside a sense (that is `PD_CITATION_ORDER_FULL_2026.md`, H7093). Each sense division "
      "contributes the earliest datable citation filed under it; the sequence of those dates in "
      "sense order is then tested for a rising tendency. Both sides use the same statistic, "
      "imported from `scripts/pd_sense_order.py`, and the same two date instruments H7093 joined: "
      "DCS (Dice ≥ 0.90) and Dharmamitra (Dice ≥ 0.82, earliest stratum of a base title). "
      "Thresholds are fixed in the script and never relaxed per dictionary.\n")
    a("## PD side — own-data canary\n")
    a("Recomputed from `data/pd/pd_citation_order_full.tsv` before any control was read. Every "
      "count and both τ values reproduce `data/pd/pd_sense_order_summary.json` exactly, so the "
      "control columns below are comparable to the published PD figure rather than to a re-implementation.\n")
    a("| clock | entries ≥3 senses | τ | null 2.5–97.5 % | median first→last | two-sense forward rate |")
    a("|---|---|---|---|---|---|")
    for clock in CLOCKS:
        c = pd[clock]
        n = c["null"]
        a(f"| {clock} | {c['entries_three_plus_senses']:,} | {c['mean_tau_position_vs_earliest']:+.3f} | "
          f"{n['p2_5']:+.3f} … {n['p97_5']:+.3f} | {fmt(c['median_last_minus_first_years'], 0)} y | "
          f"{c['two_sense_forward_rate']:.3f} ({c['two_sense_later_sense_later_date']:,}/{c['entries_two_senses']:,}) |")
    a("")
    a("## Control side — per dictionary, per clock\n")
    a("| dict | clock | records | sense divisions w/ citations | `<ls>` resolved | dated citations | "
      "entries w/ series | two-sense forward rate (exact 95 % CI) | entries ≥3 | τ | null band | median drift |")
    a("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for code in DICTS:
        st = ctl[code]["stats"]
        for clock in CLOCKS:
            c = ctl[code]["clocks"][clock]
            n = c["null"]
            ci = c["two_sense_forward_rate_ci95"]
            fwd = (f"{c['two_sense_forward_rate']:.3f} ({ci[0]:.3f}–{ci[1]:.3f})"
                   if c["two_sense_forward_rate"] is not None else "—")
            a(f"| {code.upper()} | {clock} | {st['records']:,} | {st['sense_divisions']:,} | "
              f"{st['ls_resolved']:,}/{st['ls_instances']:,} "
              f"({100 * st['ls_resolved'] / max(st['ls_instances'], 1):.1f}%) | "
              f"{st['dated_instances'][clock]:,} | {c['entries_with_series']:,} | {fwd} | "
              f"{c['entries_three_plus_senses']:,} | "
              f"{('%.3f' % c['mean_tau_position_vs_earliest']) if c['mean_tau_position_vs_earliest'] is not None else '—'} | "
              f"{('%.3f … %.3f' % (n['p2_5'], n['p97_5']))} | "
              f"{fmt(c['median_last_minus_first_years'], 0)} y |")
    a("")
    a(f"## The pre-registered comparison ({PRIMARY_CLOCK.upper()} clock, primary)\n")
    a(f"Effect floor Δτ ≥ +{EFFECT_FLOOR:.2f}; family α = {ALPHA:.2f} with Holm across the scored "
      f"dictionaries; a dictionary is scored at ≥{MIN_POWER} entries with ≥3 datable senses.\n")
    a("| dict | entries ≥3 | τ_dict | Δτ = τ_PD − τ_dict | bootstrap 95 % CI | one-sided p | Holm p | floor | α |")
    a("|---|---|---|---|---|---|---|---|---|")
    pd_tau = pd[PRIMARY_CLOCK]["mean_tau_position_vs_earliest"]
    for code in DICTS:
        r = verdict["rows"][code]
        tau_d = ctl[code]["clocks"][PRIMARY_CLOCK]["mean_tau_position_vs_earliest"]
        ci = r["delta_tau_ci95"]
        a(f"| {code.upper()} | {r['entries_three_plus_senses']:,} | "
          f"{('%.3f' % tau_d) if tau_d is not None else '—'} | "
          f"{('%+.3f' % r['delta_tau']) if r['delta_tau'] is not None else '—'} | "
          f"{('%.3f … %.3f' % (ci[0], ci[1])) if ci else '—'} | "
          f"{('%.4f' % r['p_one_sided']) if r['p_one_sided'] is not None else '—'} | "
          f"{('%.4f' % r['p_holm']) if r['p_holm'] is not None else '—'} | "
          f"{'yes' if r['clears_floor'] else 'no'} | {'yes' if r['clears_alpha'] else 'no'} |")
    a("")
    a("")
    worst = min(verdict["scored"], key=lambda c: verdict["rows"][c]["delta_tau"])
    mw = verdict["rows"]["mw"]
    a(f"**How the verdict is reached.** The decisive row is **PWG**: τ = "
      f"{ctl['pwg']['clocks'][PRIMARY_CLOCK]['mean_tau_position_vs_earliest']:.3f} against PD's "
      f"{pd_tau:.3f} — PD is *below* a dictionary without the OED's historical remit, and the "
      f"bootstrap CI on Δτ ({verdict['rows']['pwg']['delta_tau_ci95'][0]:+.3f} … "
      f"{verdict['rows']['pwg']['delta_tau_ci95'][1]:+.3f}) excludes zero. MW is the second "
      f"failure and the closer call: Δτ = {mw['delta_tau']:+.3f}, "
      f"{EFFECT_FLOOR - mw['delta_tau']:.3f} below the floor, so it would not decide the verdict "
      f"alone. PW and AP clear the floor comfortably — they show no chronological order at all. "
      f"The `dcs` replication clock gives the same ordering (PWG "
      f"{ctl['pwg']['clocks']['dcs']['mean_tau_position_vs_earliest']:.3f}, MW "
      f"{ctl['mw']['clocks']['dcs']['mean_tau_position_vs_earliest']:.3f}, PW "
      f"{ctl['pw']['clocks']['dcs']['mean_tau_position_vs_earliest']:+.3f}, AP "
      f"{ctl['ap']['clocks']['dcs']['mean_tau_position_vs_earliest']:+.3f}).\n")
    a("### What this changes in the A68 footnote (`[^chronology]`)\n")
    a("The footnote's closing sentence says the partly-forced order is one \"that no comparative "
      "test has yet separated\". That test now exists, so the sentence is replaced by:\n")
    a("> A rising sense sequence is not by itself editorial chronology — senses carry a "
      "partly-forced order (literal → figurative → technical) — and the comparative test now "
      "separates it: run on PWG, PW, MW and AP with the same statistic and the same date joins "
      "(19-10-2026), PD's τ = +0.32 is **not** distinctive. PWG, a dictionary without the OED's "
      "historical remit, orders its senses at least as chronologically (τ = +0.41, Δτ = −0.08 "
      "against PD, one-sided permutation P = 1.00), and MW sits at +0.23, short of the "
      "pre-registered +0.10 floor by 0.004. On this evidence the *historical principles* reading "
      "of PD's sense order is withdrawn; the tendency is shared with non-historical dictionaries "
      "([comparison report](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/"
      "PD_SENSE_ORDER_COMPARE_2026.md)). This paper uses the citations as canon evidence, not as "
      "a chronology, and no number here depends on the order being monotone.\n")
    a("")
    a("### Robustness — τ by entry size (primary clock)\n")
    a("PWG root entries can carry 100+ Bedeutungen; this split keeps them from carrying the "
      "result alone. A size band with no entries is reported as such, never omitted.\n")
    a("| dict | 3–7 senses: entries | τ | ≥8 senses: entries | τ |")
    a("|---|---|---|---|---|")
    for code in DICTS:
        bands = ctl[code]["clocks"][PRIMARY_CLOCK].get("tau_by_size") or {}
        small, large = bands.get("3_to_7") or {}, bands.get("8_plus") or {}
        a(f"| {code.upper()} | {small.get('entries', 0):,} | "
          f"{('%.3f' % small['mean_tau']) if small.get('mean_tau') is not None else '—'} | "
          f"{large.get('entries', 0):,} | "
          f"{('%.3f' % large['mean_tau']) if large.get('mean_tau') is not None else '—'} |")
    pd_bands = pd[PRIMARY_CLOCK].get("tau_by_size") or {}
    ps, pl = pd_bands.get("3_to_7") or {}, pd_bands.get("8_plus") or {}
    a(f"| PD | {ps.get('entries', 0):,} | "
      f"{('%.3f' % ps['mean_tau']) if ps.get('mean_tau') is not None else '—'} | "
      f"{pl.get('entries', 0):,} | "
      f"{('%.3f' % pl['mean_tau']) if pl.get('mean_tau') is not None else '—'} |")
    a("")
    a("τ_PD on the primary clock: "
      f"{pd_tau:+.3f} (n = {pd[PRIMARY_CLOCK]['entries_three_plus_senses']:,} entries).\n")
    a("## Pre-registered rule (verbatim from the script's header)\n")
    a("1. Primary clock **dm** (the clock the A68 footnote quotes); `dcs` replicates.\n"
      "2. A dictionary is scored at ≥30 entries with ≥3 datable senses.\n"
      "3. Δτ = τ_PD − τ_dictionary, one-sided permutation p (5,000 relabellings, H0: PD is not "
      "higher), bootstrap 95 % CI, Holm across the scored family at α = 0.05.\n"
      "4. **STAND** iff every scored dictionary shows Δτ ≥ +0.10 and Holm p ≤ 0.05.\n"
      "5. **WITHDRAWN** if any scored dictionary fails either condition — then the A68 footnote "
      "says the tendency is shared with non-historical dictionaries and the 'historical principles' "
      "name is not evidenced by sense order.\n"
      "6. **INCONCLUSIVE**, footnote unchanged, if fewer than two dictionaries are scored.\n")
    a("## Limits that travel with these numbers\n")
    a("* **Unit is the quotation, not the editor's date.** A sense's date is its earliest quoted "
      "passage; a sense can be historically early and filed under a late quotation.\n"
      "* **Undated senses are skipped, not imputed.** An entry contributes a series only if it has "
      "two or more senses that resolve to a dated work, so coverage is a fraction of the dictionary "
      "and the denominators above are the honest population.\n"
      "* **Resolution ceiling is the binding constraint.** Non-historical dictionaries cite "
      "lexicographers, grammarians and medieval compendia that the DCS/Dharmamitra chronologies do "
      "not date; the per-dictionary `<ls>`-resolved and dated-citation columns say how much of each "
      "dictionary this instrument can actually see.\n"
      "* **Sense unit is the numbered meaning.** PD's unit is its numbered `{@n@}` division; the "
      "control's unit is therefore the numbered Bedeutung (`— 12〉` in PWG/PW, the numbered "
      "sub-record in MW, the weapon-point bullet in AP). A lettered sub-sense (`a〉`, `— β〉`) folds "
      "into its parent, so its quotations still count towards the parent's earliest date — the same "
      "nesting PD's division rows have. On PWG the fold *raises* τ (0.372 → 0.406 on dm), i.e. the "
      "verdict does not rest on the split.\n"
      "* **Homonyms are merged per headword family** (one entry = headword + homonym tag), matching "
      "f10's grouping; a split-homonym convention would change sequence lengths, not the direction.\n"
      "* **MW segmentation** follows f10: numbered sub-records are senses, and a root record's "
      "`<div n=\"to\">` glosses are additional senses; MW's plain numbered senses inside one "
      "record are not split, so MW's series are more conservative (longer, fewer entries) than "
      "PWG's.\n"
      "* **DCS and Dharmamitra are one lineage, not two instruments** (ρ = 0.94 on 56 shared "
      "works), so the two clocks replicate a chronology; they do not double the evidence.\n"
      "* **The forced canonical order** (literal → figurative → technical) is shared by every "
      "dictionary and is exactly what the control measures; it is reported, never corrected away.\n")
    a("## Reproduction\n")
    a("```sh\n"
      "python scripts/pd_sense_order_compare.py --build   # writes the JSON + this report\n"
      "python scripts/pd_sense_order_compare.py --check   # recomputes and compares (slow: nulls)\n"
      "python -m pytest tests/forensic/test_pd_sense_order_compare.py -q   # pinned rows, seconds\n"
      "```\n")
    a("Inputs are read-only: `../csl-orig/v02/{pwg,pw,mw,ap}`, `../csl-guides/src/data/"
      "abbreviations.json`, `data/citations/mw-source-abbreviations.tsv`, "
      "`test/_h6943_dcs_texts_clean.json`, `src/data/external/dharmamitra-chronology.json`.\n")
    a(f"_Handoff {HANDOFF} · Dr. Mārcis Gasūns_\n")
    return "\n".join(L)

