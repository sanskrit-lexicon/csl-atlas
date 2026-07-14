# Metadoc — `HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`

_Created: 10-07-2026 · Last updated: 11-07-2026_

> **Status: H488 has been executed** ([PR #239](https://github.com/sanskrit-lexicon/csl-atlas/pull/239), 10-07-2026).
> The plan-time estimates this metadoc originally hedged are now measured; the trust table and backlog
> below are updated accordingly. Result in one line: the shared apparatus resolves against the vulgate
> as **verifiably correct** (206/565 corroborate at the exact cited śloka, ~75× over null), so there is
> **no shared error to find** — a positive measured null, not a data-availability block. A10 stays
> "very strong, not airtight."

A document *about* [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md).
Not a copy of its content — its purpose, how far to trust each number, and what would improve it.

## Purpose & audience

Settles **which text can adjudicate a *wrong* `HARIV. N` citation**, so nobody re-attempts the
shared-erroneous-citation upgrade of A10 against the wrong witness or via a concordance. Audience:
whoever picks up [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md),
and any future reader tempted (as [PR #235](https://github.com/sanskrit-lexicon/csl-atlas/pull/235)
was) to reach for a vulgate↔critical concordance.

## Provenance

- **Built:** 10-07-2026, Opus 4.8 (`claude-opus-4-8`), in the session that scoped H488.
- **Method:** premise verified *before* design (per an explicit user ruling) — the PWG/MW citation
  forms were measured by grep over `csl-orig`, not assumed; the vulgate e-text's coverage was
  measured by a scripted harvest, not trusted from its index page. Prior-art was checked *before*
  proposing OCR, which is how the free Kinjawadekar e-text was found instead.
- **Supersedes:** the "recension artifact / needs a concordance" framing recorded in A10 §6 by
  [PR #235](https://github.com/sanskrit-lexicon/csl-atlas/pull/235). That framing was not wrong about
  the edition mismatch — it was wrong that a concordance could repair it.

## How far to trust each number

| Claim | Confidence | Basis |
|---|---|---|
| PWG 15,415 numbered `HARIV.` refs, range 1–16,369 | **hard** | direct grep over committed `csl-orig/v02/pwg/pwg.txt` |
| MW 1,053 numbered refs, 5,229 bare sigils | **hard** | direct grep over `csl-orig/v02/mw/mw.txt` |
| DCS = 118-chapter critical edition | **hard** | file census in `VisualDCS` |
| Vulgate e-text coverage **15,364 / 16,374 = 93.8%** | **hard (measured)** | full harvest of both page series, H488 Task 1. Supersedes the 71.1% plan estimate — the pre-execution harvest sampled only the `_mpr` series |
| Index trustworthy: held-out MW 68.4% within ±3 vs 2.1% null (~33×) | **hard (measured)** | the circularity gate — fitted on 14,471 PWG anchors, validated on 815 held-out MW anchors, H488 Task 2 |
| **206 / 565 (37.7%) corroborate at the exact cited śloka** vs 0.5% null (~75×) | **hard (measured)** | H488 Task 3; the 83.9% *estimate* this table originally carried was plan-time and is retired |
| Shared **error** signal = measured null | **hard (measured)** | displaced cases fall *below* their shuffled null (79 vs 200), no clustering — the apparatus is correct, so nothing is wrong to share |
| `HARIV. 19850` is a typo | **firm** | exceeds the 16,374 ceiling by ~3,500; the *correct* value is still unknown |

## Ranked improvement backlog

1. **Replace the estimated band boundaries with fitted ones.** → ✅ **done** ([PR #239](https://github.com/sanskrit-lexicon/csl-atlas/pull/239)) —
   the continuous index was fitted and §6 replaced §4's estimates with measured resolutions
   (`harivamsa_continuous_index_offsets.csv`).
2. **Close the Bhaviṣya-parvan gap.** → **largely resolved** — the full harvest reached 93.8% (not the
   feared thin coverage), so OCR of Calcutta Vol. IV is no longer on the critical path. Any residual
   unreached refs are itemized in §6; reopen only if a specific reference needs the printed edition.
3. **Resolve `HARIV. 19850`.** → **open** — still a reported typo of unknown true reading; can now be
   chased against the harvested vulgate neighbourhood and, once established, routed to
   `/cologne-correction-queue`.
4. **Record the held-out calibration verdict.** → ✅ **done** — 68.4% within ±3 vs 2.1% null (~33×),
   the gate that made the error test legitimate to run. Captured in the trust table above and §6.

## Known limitations / caveats

- **Read §6, not §4, for settled numbers.** §4's 83.9% reachability was the pre-execution estimate;
  the harvest reached 93.8% and §6 carries the measured resolutions. §4 is retained as the scoping
  record only.
- **The null is a null, read it correctly.** "No shared error found" here means *the shared apparatus
  is verifiably correct against the vulgate* — a positive result — **not** that the test was blocked
  (which was the earlier DCS situation). Do not cite this as "inconclusive".
- **Rights.** The Kinjawadekar text (1936, volunteer transcription) may be measured freely but not
  necessarily *republished*; a `kosha` release of the harvested text needs `/publish-safety-check` first.

## Intended use / known misuse

**Intended use.** Settling, for anyone touching A10's `HARIV. N` citation evidence, which text can
actually adjudicate a *wrong* Harivaṃśa citation (the Kinjawadekar vulgate via the fitted continuous
index — §6 of the subject), and at what confidence each headline number (93.8% coverage, 68.4%
held-out agreement, 206/565 corroborated) should be trusted. It is the reference for *why* the
concordance route is closed (§3 of the subject) so nobody reopens it.

**Known/likely misuse:**
- **Citing §4's 83.9%/71.1% as current.** Those are the pre-execution *plan-time* estimates; §6 (93.8%
  coverage, the fitted held-out-validated index) is the settled figure. §4 is scoping history only —
  reading it in isolation (e.g. skimming just the top of the subject doc) understates the coverage.
- **Reading the null result as inconclusive or as a blocked test.** "No shared error found" (§6-B) is a
  *measured, positive* result — the shared apparatus verifies as correct against the vulgate — not the
  earlier DCS situation where the test could not be run at all. Citing this census as evidence A10's
  error test was "blocked" or "inconclusive" misrepresents it.
- **Treating the concordance file (`harivamsa_vulgate_concordance.csv`) as a vulgate↔critical (DCS/BORI)
  concordance.** It is a *vulgate-internal* concordance (Kinjawadekar addressing ↔ Calcutta continuous
  numbering) — a genuine vulgate↔critical concordance is a different, unbuilt object, and per §3 of the
  subject it would not help the error test anyway (a structural argument, not a data gap).
- **Republishing the harvested Kinjawadekar text bytes** (as opposed to the derived numeric mapping)
  without running [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
  first — see the Rights caveat above.
- **Using the continuous-index offset as verse-exact for any single citation.** It carries ±1–2
  calibration noise (68.4% within ±3 held-out); fine for the aggregate corroboration statistic this
  census reports, not fine as a claim that a specific `HARIV. N` maps to one exact Kinjawadekar verse
  without checking the offset caveats in subject §6.

## Maintenance & sunset plan

The subject document is owned by whoever holds A10 ([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md))
in the `csl-atlas` repo — currently maintained ad hoc by the agent session touching that paper, not a
standing pipeline or scheduled job. There is no automated regeneration: the census and its four CSV/JSON
outputs (`harivamsa_vulgate_concordance.csv`, `harivamsa_continuous_index_offsets.csv`,
`harivamsa_shared_citation_resolution.csv`, `f7_report.json`) are one-shot outputs of
[`f7_harivamsa_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_harvest.py)
and [`f7_harivamsa_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py),
re-runnable if `csl-orig`'s PWG/MW citation forms change materially or the upstream Kinjawadekar
e-text is re-harvested.

This metadoc itself was briefly stale by header date only: the subject was synced to H488's measured
results one day after this metadoc was first written (commit
[`606db08`](https://github.com/sanskrit-lexicon/csl-atlas/commit/606db0862b26afd045eaa80329139fae04db6054),
11-07-2026, "docs sync: reconcile Harivamsa census + metadoc with H488 results") — both files were kept
in lockstep in that same commit, so content never actually drifted out of sync; only the `Last updated`
header lagged by a day until this pass.

**Sunset trigger.** This census/metadoc pair is considered archived (no further updates expected) once
A10 either lands the shared-erroneous-citation claim as "very strong, not airtight" in a published
venue, or the paper's framing changes such that the Harivaṃśa test is dropped entirely. If a future
vulgate↔critical (DCS/BORI) concordance is ever built for other purposes (§3 of the subject notes this
is possible), it is a *new* object and gets its own doc + metadoc rather than folding into this one.

## Deprecation status

`active` — A10 still cites this census's §6 results as its evidence base, and the backlog above has
one open item (`HARIV. 19850`'s true reading).

## Related documents

- Subject's index: [`data/forensic/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/README.md)
- Sibling topic doc: [`CITATION_TAGGING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/CITATION_TAGGING.md)
- Consumes the census: [`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) §6
- Executable follow-up: [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md)
- Negative result: [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8
- Infra gotcha: [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) §55

## Revision history

| Date | Change | By |
|---|---|---|
| 10-07-2026 | Subject created (citation-form census + adjudicability table + vulgate harvest census); this metadoc created alongside it. | Opus 4.8 (`claude-opus-4-8`) |
| 10-07-2026 | H488 executed ([PR #239](https://github.com/sanskrit-lexicon/csl-atlas/pull/239)): §6 results appended to subject; metadoc synced — trust table flipped to measured, backlog #1/#4 closed, #2 downgraded, plan-time caveats retired. | Opus 4.8 (`claude-opus-4-8`) |
| 11-07-2026 | template v2 backfill (H663) | Sonnet 5 (`claude-sonnet-5`) |

_Dr. Mārcis Gasūns_
