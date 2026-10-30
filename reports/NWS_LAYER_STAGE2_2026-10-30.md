# NWS layer Stage 2: the three delimited roles, and what H5 does to NWS's status

_Created: 30-10-2026 · Last updated: 30-10-2026_

**Handoff:** [H7476](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7476-GLM_csl-atlas_nws-layer-stage2_30.10.26.md)
(H7463's successor) · **Model:** GLM 5.3 (`glm-5.3`, ZCode full tier) ·
**Protocol:** [pwg-nws-pd-dcs-8294e5 report §8](https://github.com/gasyoun/Uprava/blob/main/research/notes/final_report_pwg-nws-pd-dcs-8294e5.md)
— pre-registered; the NWS↔DCS inventory join stays **out**, and no threshold
was retuned after measurement.

---

## TL;DR

The NWS layer is measured in exactly its three pre-registered roles, each
with its denominator, from committed row-level data. **H5's headword-level
verdict: divergent.** Spearman ρ between per-headword NWS attestation mass
and PW's quotation-linked mass over the **28,158 shared headwords** is
**0.3414** (t = 60.9 — significant, weak): NWS's per-headword allocation is
*not* a copy of PW's distribution, so the pre-registered confirmation cell
("tracks → transfer noise") does **not** fire. The divergence is bounded
twice, and both bounds are recorded rather than absorbed:

1. **Shape.** The decile profile *is* monotone (NWS mean mass rises
   0.97 → 6.75 references/entry across PW's mass deciles, 2 early
   inversions) and the letter-aggregate ρ is **0.9782** — the macro envelope
   tracks PW almost perfectly. What diverges is the **within-letter
   allocation**, and it is flatter than PW's: NWS's top-decile mass share is
   **38.6 %** against PW's own **67.2 %**.
2. **The upgrade conditional.** Divergence upgrades NWS toward a delimited
   witness *only together with a quantified undigitized Halle remainder*.
   That remainder is **H5940-gated** (page images rights-gated; the H6067
   OCR route exists but cannot run) and is **not quantified** on this
   substrate — so **no upgrade is claimed**: NWS stays demoted, with the
   headword-level divergence recorded as the datum that would matter once
   the gate opens.

**H6 clean:** **82 of 174** registry works attested (47.13 %), recomputed
only from the dated scrape (fetched 2026-10-06, html sha `86c9495e…`,
hash-pinned in three places) — never from filename stems; the gate enforces
that the retracted 82.7 figure appears as no published number. **The
dependence tracer:** Lex(MW) ×5,873 anchors a 13,738-token `X(MW)` internal
family (41 kinds); **3,356 prose entries (9.84 %) carry purely MW-mediated
attestation** — material the corpus side cannot validate by construction,
since DCS's own lexicographic layer is MW-derived.

Every number regenerates from the committed TSVs under
`scripts/nws_layer_check.py` (exit 0); pins in
`tests/forensic/test_nws_layer_join.py` (3/3).

## 1. Substrate

| Register | Value | Status |
|---|---|---|
| NWS lemma tar (private, H5939) | sha256 `054b05da…` | pinned, fail-closed in extractor |
| Works registry scrape | fetched 2026-10-06, html sha256 `86c9495e…`, 174 works | pinned (registry JSON committed verbatim) |
| PWG machine text | 54,634,244 B, sha256 `430c910f…` | pinned (Stage-1 substrate) |
| NWS prose entries | 34,101 of 167,990 keys (20.3 %) | **reproduced exactly** |
| Page-precise refs / literature refs | 8,440 / 8,937 | **reproduced exactly** |
| Dict-marker entries (`MW : n`) | 4,941 | **reproduced exactly** |
| PWG per-headword mass | 123,366 rows, 729,719 ql / 801,788 raw | **reproduced exactly** |

The digitized envelope is **full-alphabet** (all 48 letters carry prose,
12.1 %–35.1 % per letter): the dump is not letter-limited, and editorial
silence versus undigitized print is not separable from the dump alone.

## 2. Role 1 — attestation-mass on shared headwords vs PW

Denominators: NWS mass = attestation sigla + page-precise + literature
references per prose entry; PW mass = quotation-linked tags per headword,
**entry-family grouped** (PWG homographs share k1; a headword's mass is the
sum over its entries — last-wins would silently drop 367,676 tags).

| Measure | Value |
|---|---|
| Shared headwords (NWS prose ∩ PWG k1) | 28,158 |
| Containment of prose keys in PWG | 82.57 % (5,943 keys outside) |
| ρ(NWS total mass, PW ql), shared keys | **0.3414** (n = 28,158, t = 60.9) |
| ρ excluding the X(MW) family | 0.3330 (robust to mediation stripping) |
| ρ components | sigla 0.3432 · page-precise 0.2369 · literature 0.0085 |
| ρ letter-aggregate (48 letters) | **0.9782** |
| Decile profile (PW ↑) | 0.966 → 6.751 refs/entry, monotone, 2 inversions |
| Top-decile mass share | NWS 38.60 % vs PW 67.24 % |
| NWS-treated keys' share of PW ql mass | 77.02 % (562,047 / 729,719) |

The literature-reference component is the flattest (ρ = 0.0085): NWS's
secondary-literature harvest — its declared dominant class — is essentially
uncorrelated with PW's citation mass at headword level.

## 3. Role 2 — declared-vs-exercised (H6)

| Measure | Value |
|---|---|
| Declared (Erfasste Werke, dated scrape) | 174 |
| Attested ≥1 citation | **82** (47.13 %) |
| Zero-citation works | 92 |
| Top attested | Geldner 1907 ×1,571 · **Sircar 1966 ×1,402** · Abhyankar 1986 ×753 · Ensink 1964 ×527 |

Method contract enforced by the gate: the attested fraction is recomputed
only from the dated scrape (registry JSON, provenance intact) joined to the
parsed sigla rows; the filename-stem method that produced the retracted
82.7 % absence figure is never touched, and the figure itself is barred
from the published numbers (structural guard in `nws_layer_check.py`).

## 4. Role 3 — the dependence tracer

| Measure | Value |
|---|---|
| Lex(MW) markers | **5,873** |
| X(MW) family total / kinds | 13,738 / 41 (Kāvya(MW) ×2,014 · W(MW) ×1,718 · Buddh(MW) ×574 …) |
| Entries carrying a family marker | 7,479 (21.93 % of prose entries) |
| **Purely MW-mediated entries** | **3,356 (9.84 %)** — all attestation tokens X(MW), no page-precise or literature refs |
| Dict-marker entries (`MW : n`) | 4,941 |

## 5. H5 verdict against the declared thresholds

Operationalization (protocol pins the direction, not a number; declared
before the join ran on the measured rows, mirrored in the gate):
**tracks** = ρ ≥ 0.60 ∧ inversions ≤ 1; **divergent** = ρ < 0.40 ∨
inversions ≥ 3; else mixed. Measured: ρ = 0.3414 (< 0.40, single criterion;
inversions = 2) → **divergent**. Reading, both scales stated:

- The pre-registered confirmation — "attestation mass tracks PW's
  distribution", reducing NWS to transfer noise — **fails at headword
  level**: a transfer-noise layer would reproduce PW's concentration, and
  NWS's allocation is flatter and largely PW-independent (literature refs
  ρ ≈ 0.01).
- The macro scale tracks (letter ρ = 0.9782): NWS's *envelope* follows the
  Petersburg mass; its *allocation within letters* does not.
- The upgrade toward a delimited witness requires the undigitized Halle
  remainder quantified; it is H5940-gated and unquantified here, so the
  divergence is recorded as the single datum that could upgrade NWS once
  the gate opens — no status change is claimed on this substrate.

## 6. Pre-registered out, and reversal triggers

The NWS↔DCS inventory join stays **out** (Petersburg inventory, 22 of
167,991 keys outside; citations transferred, not re-attested — no
independent information, added transfer noise). Reversal triggers carried
from §8/§12: a full Halle dump with per-work metadata and a static
siglum-to-edition bibliography; demonstrated locus verification
contradicting the no-transcription contract; the H5940 gate opening
(quantified print remainder → the H5 upgrade conditional becomes testable).

## 7. Artefacts

| File | What it is |
|---|---|
| [`scripts/nws_layer_extract.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/nws_layer_extract.py) | local-only extractor (private tar + pwg.txt → rows), fail-closed on every kosha H6064 pin |
| [`scripts/nws_layer_join.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/nws_layer_join.py) | the three measurements from committed rows |
| [`scripts/nws_layer_check.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/nws_layer_check.py) | regeneration gate (exit non-zero on drift) |
| [`data/nws_layer/nws_headword_mass.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_headword_mass.tsv) | 34,101 rows: per-key1 mass + tracer counts |
| [`data/nws_layer/nws_works_attestation.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_works_attestation.tsv) | 174 rows: declared-vs-exercised |
| [`data/nws_layer/nws_works_registry.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_works_registry.json) | the dated scrape, verbatim (provenance intact) |
| [`data/nws_layer/pwg_headword_ql.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/pwg_headword_ql.tsv) | 123,366 rows: per-k1 PWG mass |
| [`data/nws_layer/nws_letter_envelope.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_letter_envelope.tsv) | key-space envelope per letter |
| [`data/nws_layer/nws_x_mw_census.tsv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_x_mw_census.tsv) | the X(MW) family census (41 kinds) |
| [`data/nws_layer/nws_layer_metrics.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_layer_metrics.json) | every published number + verdicts |
| [`data/nws_layer/nws_layer_pins.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/nws_layer/nws_layer_pins.json) | substrate sha pins + rights |
| [`tests/forensic/test_nws_layer_join.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_nws_layer_join.py) | 3 pin suites |

**Delivery** — Changed: new `data/nws_layer/` dataset (7 files), 3 scripts,
1 forensic test, this report. Unchanged: Stage-1 `data/pwg_dcs/` substrate
and its gate (untouched, re-verified green); the kosha pipeline (imported,
never modified). Checks: `python3 scripts/nws_layer_check.py` → exit 0;
`python3 -m pytest tests/forensic/test_nws_layer_join.py` → 3 passed;
`python3 scripts/pwg_dcs_check.py` → exit 0. Risks: the extractor needs the
private tar + csl-orig locally (documented, one command); the H5 mapping is
an execution-time operationalization of a direction-only pre-registration
(declared in script + report, mirrored in the gate); per-work counts derive
from the committed sigla rows, whose parse-level reproduction lives in
kosha's pinned selftest. Inspect: `data/nws_layer/nws_layer_metrics.json`
first, then this report §5.

Next in the programme: Stage 3 — PD/PWG/NWS triangulation, where
apparatus-type asymmetry does the diagnostic work.

_Dr. Mārcis Gasūns_
