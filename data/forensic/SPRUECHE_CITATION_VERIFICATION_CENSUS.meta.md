# Metadoc — `SPRUECHE_CITATION_VERIFICATION_CENSUS.md`

_Created: 11-07-2026 · Last updated: 11-07-2026_

A document *about*
[`SPRUECHE_CITATION_VERIFICATION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md).
Not a copy of its content — its purpose, how far to trust each number, and what would improve it.

## Purpose & audience

Verifies every PWG `Spr.` / `Spr. (II)` citation of Böhtlingk's *Indische Sprüche* against the
typed 2nd-edition digitization, and records the range-only status of the 1st edition (no typed
text exists for it anywhere in the org). Audience: whoever picks up the roadmap's W1b follow-ups
(1st-edition OCR, PW/PWK siglum extension, the mismatch/edition-swap review queue), and A50
("What the tradition cites") which consumes the resulting counts.

## Provenance

- **Built:** 11-07-2026, Sonnet 5 (`claude-sonnet-5`), executing
  [H611](https://github.com/gasyoun/Uprava/blob/main/handoffs/H611-Sonnet_csl-atlas_spruche_citation_verify_11.07.26.md).
- **Method:** the mission brief asserted both `boesp1` and `boesp2` were "typed editions" — this
  was checked, not assumed, by opening both repos before writing any extraction code; only
  `boesp2` turned out to be. The quoted-pratīka extraction heuristic was iteratively corrected
  mid-run after a false-positive-heavy first pass (dense entries stack many `<ls>` citations with
  no clear quote boundary; see census §3) — the numbers below are from the corrected pipeline,
  not the first pass.

## How far to trust each number

| Claim | Confidence | Basis |
|---|---|---|
| 9,557 ed.-I + 6,320 ed.-II refs extracted (16,669 lsextract total, ~95% recall) | **hard (measured)** | direct regex extraction over committed `csl-orig/v02/pwg/pwg.txt`, cross-checked against `literarysource/pwg/lsextract_pwg_06.txt`'s frequency counts |
| `boesp1` has no typed verse text | **hard (measured)** | read every file under `boesp1/app1/`; only a verse→page index exists |
| `boesp2` covers verses 1–7,878 (9,284 keyed entries incl. footnote sub-numbers) | **hard (measured)** | full harvest of all 79 `web1/json/section*.json` files |
| 2,621 `Spr. (II)` refs corroborated (1,332 exact / 771 fuzzy / 518 lemma) | **medium** | automated SLP1/IAST substring + Jaccard + folded-prefix matching; not human-verified per-row |
| 443 `mismatch` rows | **soft — flagged for review, not confirmed defects** | several early "mismatches" during pipeline development turned out to be matching-algorithm gaps, not real citation errors (see census §3); the residual 443 needs a human pass before being treated as signal |
| 38 `edition_swap_candidate` rows | **soft — coincidence-rate flagged, not asserted** | base rate ~0.4% is plausible by chance given both editions' overlapping verse-number ranges |
| Validation case (`Spr. 2790` under `brū`) does not resolve as the roadmap describes | **hard (measured)** | read the actual PWG entry text; the quote the roadmap attributes to `Spr. 2790` belongs to the adjacent `M. 3,150` citation instead |

## Ranked improvement backlog

1. **1st-edition (`Spr.`) text-level verification — the largest gap.** 9,545 of 9,557 ed.-I refs
   are `range-only-unverifiable`; needs either OCR of `boesp1/pdfpages/*.pdf` (3 vols, 5,419
   verses) or discovery of an existing typed transcription elsewhere. Not started.
2. **Human review of the 443 `mismatch` + 38 `edition_swap_candidate` rows.** Recommended via
   `/review-sheet` before either bucket is cited as a data-quality finding anywhere else (a paper,
   a correction-queue item). Not started.
3. **PW/PWK `Spr.` siglum extension** (handoff's explicit "extend if trivially parallel, else
   queue" instruction) — queued, `pw/pwbib.txt` unread this pass.
4. **Recall gap (~5%, ~792 refs)** between this extraction and lsextract's raw count — mostly
   bare `<ls>Spr.</ls>` bibliography mentions (correctly excluded) but not fully audited; worth a
   targeted diff pass if the benchmark dataset (D4/R3) needs exact parity.

## Known limitations / caveats

- **`unverified-no-quote` (3,255 rows, 51.5% of ed. II) is not a negative signal.** It means no
  Sanskrit pratīka was adjacent to the citation in PWG's text at all (a bare page/sense
  attestation) — the verse number itself still resolves inside boesp2's range. Do not read this
  bucket as "unverifiable" in the same sense as the ed.-I range-only rows; it's simply
  evidence-free, not contradictory.
- **Matching-tier confidence is automated, not human-checked per row.** The `lemma` tier (518
  rows) in particular is a 6-char folded-prefix heuristic tuned against a ~20-row manual spot
  check during development, not a validated classifier — treat as a lead, not ground truth.
- **`Spr. 2790`'s validation-case mismatch is a roadmap-prose defect, not a citation defect** —
  see census §2. The roadmap document itself should be corrected; this metadoc/census does not
  do that (out of this handoff's scope; flagged for a human/@DO edit).

## Related documents

- Subject's index: [`data/forensic/README.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/README.md)
- Roadmap driving this wave: [`docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.md) §4 W1b, §5 cascade
- Sibling census (same program, MBH lane): [`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md) — same R3 schema, will stack into one released benchmark
- Minted under: [H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md); schema addendum from [H661](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H661-Fable_csl-atlas_citation-roadmap-acl-uplift_11.07.26.md)
- Consumes the counts: [A50](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) ("What the tradition cites")

## Revision history

| Date | Change | By |
|---|---|---|
| 11-07-2026 | Subject created (extraction + boesp2 verification + edition-swap probe); this metadoc created alongside it. | Sonnet 5 (`claude-sonnet-5`) |

_Dr. Mārcis Gasūns_
