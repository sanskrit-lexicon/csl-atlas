# PD edition availability by citation mass — C1, 29-10-2026

_Created: 29-10-2026 · Scope: all 419,890 H6949 attestations in the published letter-`a` PD machine text · Status: **landed as a bounded, reproducible lower-bound measurement** · Evidence: counts **derived**, live text probes **observed**, no human `reviewed` claim._

## 1. Result

**At least 189,400 of PD's 419,890 attestations — 45.11 % — sit on a work for which a
machine-readable text was positively verified in DCS, GRETIL, or Archive.org.** This is a
lower bound: the remaining 54.89 % is unresolved, not evidence of absence.

For the stricter question — whether the **same edition named by the AOB** is available —
the confirmed figure is **23,173 / 419,890 = 5.52 %**. Work-level availability and
AOB-edition identity are deliberately not conflated.

| Availability class | Raw sigla | Attestations | Share of 419,890 |
|---|---:|---:|---:|
| Full work-level text | 250 | 144,615 | 34.44 % |
| Partial text | 107 | 44,030 | 10.49 % |
| Embedded in another available text | 1 | 755 | 0.18 % |
| **Total positively available** | **358** | **189,400** | **45.11 %** |
| Unresolved / not yet established | 5,006 | 230,490 | 54.89 % |
| **Total** | **5,364** | **419,890** | **100.00 %** |

The available mass is distributed as follows. A siglum is assigned to one evidence route,
so these rows sum to the headline without double counting.

| Evidence route | Raw sigla | Attestations | Share of all attestations |
|---|---:|---:|---:|
| DCS crosswalk | 120 | 98,890 | 23.55 % |
| GRETIL, including the hand-checked residue rows | 84 | 32,404 | 7.72 % |
| Archive.org with a live text-layer probe | 154 | 58,106 | 13.84 % |
| **Total** | **358** | **189,400** | **45.11 %** |

Within the 381,898 attestations whose harvested siglum is classed `primary`, availability is
**189,400 / 381,898 = 49.59 %**. The 37,992 attestations classed `secondary`, `structural`,
or `unclassified` remain unresolved; they are not silently treated as unavailable works.

The companion AOB projection contains all **1,437** declared entries: 1,040 have direct
attestation mass, 32 are fully available, 103 partially available, 43 are ambiguous because a
raw siglum points to several AOB works, and 1,259 remain unresolved. These are entry counts,
not percentages of citation mass and not absence verdicts; shared-siglum mass is never
apportioned speculatively.

## 2. What the number means

The measurement answers a practical question: for nearly half of PD's citation mass, a
researcher can open a machine-readable text of the cited work today. It does **not** say
that this text is the AOB edition, that its chapter boundaries match PD's loci, or that its
OCR is quotation-grade. The much smaller 5.52 % AOB-exact result is the warning against
using the 45.11 % headline as an edition-alignment claim.

Partial witnesses count as **available partial**, never as full coverage. Examples are the
Śabdakhaṇḍa of the Tattvacintāmaṇi, adhyāyas 27–43 of the Pauṣkarasaṃhitā, one part of the
Nyāyamañjarī, and the Samayaprakāśa of the Vīramitrodaya. The Vārttika embedded in the
available Mahābhāṣya is reported separately again.

## 3. AOB-exact confirmations

The table lists the 13 principal sigla with exact-edition evidence. OCR and spelling variants
carrying another 215 attestations are included in the total but not repeated as separate works.

| Siglum | Attestations | AOB witness verified | Availability |
|---|---:|---|---|
| VīraMi. | 3,476 | 1908 fasciculus within the AOB 1906–1936 publication span | partial |
| ManuBh. | 3,327 | BI 1939, volume III indexes | partial |
| MīmāKau. | 2,253 | Chowkhamba Sanskrit Series 1924 | partial |
| BālamBha. | 1,849 | Vyavahāra-Bālambhaṭṭī 1914 | partial |
| SmṛtiCan. | 1,715 | Saṃskāra-kāṇḍa 1914 | partial |
| Prasā. | 1,491 | BSS parts 1–2, 1925/1931 | full |
| Bhām. | 1,481 | BI 1880 Bhāmatī | full |
| Aparā. | 1,303 | Ānandāśrama parts 1–2, 1903/1904 | full |
| VedāntKa. | 1,248 | VSS 13, parts 1–2 | full |
| Subhāṣi. | 1,240 | Peterson 1886, catalogue marks missing pages | partial |
| HarVi. | 1,201 | Kāvyamālā 22, 1890 | full |
| RasGaṅ. | 1,200 | Kāvyamālā 12, 1947 | full |
| Vaija. | 1,174 | Gustav Oppert 1893 | full |
| **Principal rows** | **22,958** | — | — |
| **With attested siglum variants** | **23,173** | — | **5.52 % of all attestations** |

All exact-edition witnesses are Archive.org records with a non-empty `_djvu.txt` successfully
fetched on 29-10-2026. Catalogue presence alone was never sufficient.

## 4. Method

1. **Population.** Reused the H6949 quotation-unit parser over the canonical PDScan 2020
   `txt/pd.txt` (55,122,076 bytes, SHA-256
   `4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442`). The parser
   reproduces 384,217 siglum loci + 35,673 continuation loci = **419,890 attestations**
   exactly.
2. **Continuation assignment.** Each bare semicolon continuation inherits the immediately
   preceding siglum in its citation tail. There are 104 continuation loci (0.0248 % of the
   denominator) with no assignable preceding siglum; they remain visible as unresolved rather
   than being attached speculatively.
3. **DCS.** Reused the committed DCS crosswalk and its full/partial grades; no re-derivation
   of the older 398,359-occurrence metric was substituted for the 419,890-attestation
   denominator.
4. **GRETIL.** Reused the hand-checked H7298 residue evidence and added only candidates whose
   title and work identity were checked against the live GRETIL index. Actual text files were
   then probed. Bhaṭṭadīpikā's indexed GRETIL XML/HTML/TXT links all returned 404, so that
   route was excluded; an Archive.org text was used instead.
5. **Archive.org.** Searched the highest-mass unresolved works, inspected metadata and file
   inventories, and required an HTTP 200/206 response with non-empty machine-readable text.
   Multi-volume works are `full` only when the necessary set was established; otherwise they
   are `partial`.
6. **Identity controls.** Shared sigla do not acquire a work title or availability through a
   many-to-one registry join. Index-of-Works titles take precedence, with AOB and registry
   labels as fallbacks. GRETIL's Jayamaṅgalā on the Sāṃkhyakārikā was rejected because AOB's
   Jayamaṅgalā is on the Kāmasūtra. The Laghu- and full Siddhāntakaumudī were not merged.
7. **Unknowns.** No row was marked `unavailable_verified`: this pass did not exhaustively
   prove absence for any work. Unprobed, ambiguous, and unresolved rows stay `unresolved`.

The hand-derived unit controls cover continuation inheritance, unassigned continuations,
non-quotation continuation tails, and the rule that unresolved is never available.

## 5. Largest remaining primary-work gaps

These are the highest-mass unresolved primary rows after the final probe batch. They are a
work queue, not an absence verdict.

| Siglum | Attestations | Work / current identity |
|---|---:|---|
| PadmP. | 3,849 | Padmapurāṇa; absent in DCS/GRETIL, exact Archive.org text not established |
| ŚivārkaMaDī. | 2,770 | Śivārkamaṇidīpikā |
| BṛĀraUBhVā. | 2,056 | Bṛhadāraṇyakopaniṣadbhāṣyavārtika |
| BhaviP. | 1,705 | Bhaviṣyapurāṇa; absent in DCS/GRETIL, exact Archive.org text not established |
| CaturCin. | 1,495 | Caturvargacintāmaṇi |
| LaCandr. | 1,470 | Laghucandrikā on Advaitasiddhi |
| PāṇḍaC. | 1,307 | Pāṇḍavacarita |
| NyāyRa. | 1,195 | Nyāyaratnākara |
| AṇuBh. | 1,128 | Aṇubhāṣya |
| ManvaVi. | 1,127 | Manvarthavivṛti |
| PāraS. | 1,085 | Pārameśvarasaṃhitā |
| AbhinBhā. | 1,079 | Abhinavabhāratī |
| JaineVyā. | 1,067 | Jainendravyākaraṇa |
| BālaKrī. | 1,057 | Bālakrīḍa on Yājñavalkyasmṛti / Viśvarūpa |
| GaṇeP. | 1,054 | Gaṇeśapurāṇa |

## 6. Limits and next measurement

- **This is a lower bound, not a completed absence census.** The unresolved 54.89 % needs
  further title resolution and source probing before a final availability percentage can be
  quoted without the qualifier.
- **The AOB-exact figure is also a lower bound.** Direct AOB entry links currently cover
  295,931 attestations (70.48 %); unresolved identity joins cannot be promoted to exact
  editions.
- **OCR quality is untested.** A live text layer proves machine readability, not quotation
  fidelity, completeness of every page, or locus-level compatibility.
- **Partial is not full.** The 10.49 % partial and 0.18 % embedded mass must not be added to
  the 34.44 % full mass in a claim about complete works.
- **No human κ or review is claimed.** The result is a deterministic aggregation over named
  evidence, with live probe receipts; it does not close the parity report's human-review row.

The next useful increment is a bounded probe of the 15 primary rows above, followed by the
secondary/structural identity layer. It should raise the lower bound without changing the
rule that unknown is not absent.

## 7. Reproduce

```sh
python3.13 scripts/pd_edition_availability.py --pd /path/to/pd.txt
python3.13 scripts/pd_edition_availability.py --check --pd /path/to/pd.txt
python3.13 -m pytest tests/forensic/test_pd_edition_availability.py -q
```

Expected check: `PASS C1 189,400/419,890 = 45.11% work-level; 5.52% AOB-exact`.

Artifacts:

- [`pd_edition_availability_by_siglum.tsv`](../data/pd/pd_edition_availability_by_siglum.tsv) — every raw siglum, its locus/continuation split, availability class, identity basis and evidence reference.
- [`pd_edition_availability_by_aob.tsv`](../data/pd/pd_edition_availability_by_aob.tsv) — all 1,437 AOB entries with direct mass, availability projection and shared-siglum ambiguity kept separate.
- [`pd_edition_availability_summary.json`](../data/pd/pd_edition_availability_summary.json) — denominator, headline measures, source/status/class breakdowns, input hashes, evidence labels and top unresolved rows.
- [`pd_edition_availability_evidence.tsv`](../data/pd/pd_edition_availability_evidence.tsv) — curated live evidence; full/partial and work-level/AOB-exact kept explicit.
- [`pd_edition_availability_probes_2026-10-29.json`](../data/pd/pd_edition_availability_probes_2026-10-29.json) — GRETIL and Archive.org text-probe receipts.
- [`scripts/pd_edition_availability.py`](../scripts/pd_edition_availability.py) and [`tests/forensic/test_pd_edition_availability.py`](../tests/forensic/test_pd_edition_availability.py) — deterministic builder and controls.

_29-10-2026 — Kimi Work; full-population parse, bounded live-source verification, and explicit unresolved residue._
