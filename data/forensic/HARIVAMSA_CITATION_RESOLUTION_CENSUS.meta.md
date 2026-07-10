# Metadoc — `HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`

_Created: 10-07-2026 · Last updated: 10-07-2026_

A document *about* [`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md).
Not a copy of its content — its purpose, how far to trust each number, and what would improve it.

## Purpose & audience

Settles **which text can adjudicate a *wrong* `HARIV. N` citation**, so nobody re-attempts the
shared-erroneous-citation upgrade of A10 against the wrong witness or via a concordance. Audience:
whoever picks up [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md),
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
| Vulgate e-text coverage 11,646 / 16,374 = 71.1% | **firm** | scripted harvest of both page series; depends on the site being complete-as-published |
| Reachable shared refs 474 / 565 = **83.9%** | **soft-ish** | the band boundaries (esp. P2's ~12,562 upper edge) are cumulative *estimates* from Kinjawadekar verse counts, **not** Calcutta-verified. The figure shifts once the continuous index is actually fitted (H488 Task 2). Treat as a close estimate, not settled. |
| `HARIV. 19850` is a typo | **firm** | exceeds the 16,374 ceiling by ~3,500; but the *correct* value is unknown |

## Ranked improvement backlog

1. **Replace the estimated band boundaries with fitted ones.** The 83.9% reachability rests on
   cumulative verse-count estimates for the parvan edges. Once H488 Task 2 fits the continuous index,
   re-derive the P1/P2/P3 split from the fitted index and update §4. → status: **open**, gated on H488.
2. **Close the Bhaviṣya-parvan gap (91 refs, 16.1%).** The e-text is thin there. Either accept 83.9%
   in the paper or OCR Calcutta Vol. IV (pp. 445–1007). Log the exclusion either way. → **open**.
3. **Resolve `HARIV. 19850`.** Establish the true reading (needs the vulgate text at that neighbourhood)
   before it can go to `/cologne-correction-queue` as a change file. → **open**, gated on Task 1.
4. **Record the held-out calibration verdict.** When H488 Task 2 runs, its held-out PWG-fit/MW-test
   agreement rate is the single number that says whether the whole census is *usable* for an error
   test. Add it here as the trust gate. → **open**, gated on H488.

## Known limitations / caveats

- **The 83.9% is a plan-time estimate, not a result.** See backlog #1 — the exact figure is
  contingent on the index fit.
- **Rights.** The Kinjawadekar text (1936, volunteer transcription) may be measured freely but not
  necessarily *republished*; a `kosha` release needs `/publish-safety-check` first.
- **Circularity risk in the downstream test.** The census enables H488, but H488's error test is only
  valid if the index is fitted robustly and validated held-out. The census does not itself run that
  test and must not be read as having proven any shared error exists.

## Related documents

- Subject's index: [`data/forensic/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/README.md)
- Sibling topic doc: [`CITATION_TAGGING.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/CITATION_TAGGING.md)
- Consumes the census: [`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md) §6
- Executable follow-up: [H488](https://github.com/gasyoun/Uprava/blob/main/handoffs/H488-Opus_csl-atlas_harivamsa_vulgate_citation_resolution_10.07.26.md)
- Negative result: [`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8
- Infra gotcha: [`Uprava/FINDINGS.md`](https://github.com/gasyoun/Uprava/blob/main/FINDINGS.md) §55

## Revision history

| Date | Change | By |
|---|---|---|
| 10-07-2026 | Subject created (citation-form census + adjudicability table + vulgate harvest census); this metadoc created alongside it. | Opus 4.8 (`claude-opus-4-8`) |

_Dr. Mārcis Gasūns_
