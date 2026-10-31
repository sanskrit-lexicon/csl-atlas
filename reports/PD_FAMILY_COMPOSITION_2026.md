# PD family composition: privative, preverb and function-word families (H7110)

_Created: 19-10-2026 · Last updated: 19-10-2026_

_Source data: Cologne PDScan 2020 `pdtxt.zip` → `txt/pd.txt` (55,122,076 B, SHA-256
`4ee75e66…724442`, 107,620 `<L>` entries — with headword blocks, of 107,630; see
[PD_QUOTATION_UNIT_2026-10-18.md](PD_QUOTATION_UNIT_2026-10-18.md)), read-only · PWG: `csl-orig/v02/pwg/pwg.txt`
(106,067 unique `k1`) · Artifact:
[pd_family_composition.tsv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pd/pd_family_composition.tsv) ·
Builder: [pd_family_composition.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_family_composition.py) ·
Pins: [test_pd_family_composition.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/tests/forensic/test_pd_family_composition.py) ·
Handoff: [H7110](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7110-DeepSeek_csl-atlas_pd-family-extremes_19.10.26.md)_

PD gives a headword to nearly every compound and productive derivative. The A68 table
([§6.2](https://github.com/gasyoun/Uprava/blob/main/papers/A68/A68_DCS_REPRESENTATIVENESS_PD_CANON.md))
shows the policy on two families, *anna* and *agni*, both 75–78 % compounds. This pass asks
whether any other family inside *a*–*apaca-* breaks that pattern by more than 15 percentage
points, and whether the privative/negative set the section quotes (≈8,900 entries, 21.3×
without it) reproduces.

**Answer.** Three families cross the 15 pp line, and one of them can be a table row. The
function word *atha* is the real exception: 63.1 % compounds and 29.4 % simplex, against
13.8 / 11.4 % simplex in the two reference families. The privative *a‑* and negative *an‑*
sets are 99.9 % compounds, but that is true by construction and cannot fill the table's PWG
column (PWG prints no analysis parenthesis): they stay in the prose where they already are.
The privative recount reproduces the draft's **8,894 entries** under the draft's own literal
rule — but Vedic accent marks hide another ~558 privatives, so the accent-normalised count
is **9,452**, and the density multiple without them is **21.1×**, not 21.3×.

## 1. Rule

PD prints the compound analysis in a parenthesis right after the headword separator:
`agnibhāṇḍa¦ (agni-bhāṇḍa)`, `annaka¦ (anna-ka)`. The classifier is four steps, published in
full so a reader can re-run it.

| Step | Rule |
|---|---|
| Population | every unique `<k1>` for which at least one entry prints `<k1>` = `<k2>` and carries an analysis parenthesis |
| Analysis | the first `( … )` after the `¦` separator on the entry's first body line |
| Members | Unicode NFD, strip the Vedic acute/grave (U+0301, U+0300), `°` and apostrophes, NFC again; split on hyphen / en-dash / em-dash / whitespace |
| Class | one member ⇒ **simplex**; last member in the suffix set ⇒ **derivative**; otherwise ⇒ **compound** |

The derivative suffix set (IAST, 15 items, unchanged from the atlas's M12 lemmatisation
census): `ka, tva, tā, tara, tama, maya, aka, ana, ita, in, mat, vat, tṛ, tas, ya`
(`--print-suffixes` prints it). The NFC round-trip matters: PD prints *tā* both precomposed
and as `ta` + U+0304, and without it the suffix test silently misses half of them.

**Family** has two senses, and the report keeps them apart because they are not
interchangeable:

- **string family** — every headword beginning with the prefix string. This over-counts:
  `an` catches *anala*, *anila*; `a` catches the entire dictionary (104,950 headwords) and is
  not a family at all.
- **morphological family** — defined on the analysis, which is the only way to state the
  privative *a‑* and negative *an‑* sets.

### 1.1 Population reconciliation

| Quantity | Count |
|---|---:|
| unique `<k1>` in pd.txt | 104,950 |
| …with a printed analysis parenthesis | **102,747** |
| …whose only first-line parenthesis is a CORRECTIONS block `({{old->new\|date\|…}})` | 380 |
| reconciled total | **103,127** |

The A68 draft's "analysis parenthesis of 103,127 of 104,950 headwords" is therefore
reproduced exactly: the draft counted the 380 CORRECTIONS blocks as analyses, this parser
counts them but does not classify them, because an errata insertion is not a compound
analysis. The population pin in `--check` is 103,127 with a ±6 band.

## 2. The whole-alphabet split

| | compounds | derivatives | simplex |
|---|---:|---:|---:|
| This pass (102,747 classified) | 72,632 · **70.7 %** | 12,670 · **12.3 %** | 17,445 · **17.0 %** |
| A68 draft | 70.4 % | 12.7 % | 16.9 % |
| Δ | +0.3 pp | −0.4 pp | +0.1 pp |

The draft's figures are inside the ±3 pp it claims, and this pass reproduces them to 0.4 pp
on a stricter population. Anyone quoting the split should quote 70.7 / 12.3 / 17.0 with the
suffix set above; the residual is the derivative test (a compound whose last member happens
to be a suffix word counts as a compound here).

## 3. The families

Shares are over classified headwords; `PD` is the whole string family, `classified` the
subset whose analysis parsed.

| Family | kind | PD | PWG | classified | compounds | derivatives | simplex |
|---|---|---:|---:|---:|---:|---:|---:|
| *anna* (ref) | string | 877 | 33 | 875 | 78.1 % | 8.1 % | 13.8 % |
| *agni* (ref) | string | 2,312 | 170 | 2,299 | 74.6 % | 14.0 % | 11.4 % |
| *anya* | string | 4,071 | 83 | 4,047 | 71.2 % | 10.7 % | 18.0 % |
| *antar* | string | 2,735 | 135 | 2,727 | 74.2 % | 8.1 % | 17.6 % |
| *ati* | string | 7,541 | 376 | 7,507 | 77.8 % | 13.1 % | 9.1 % |
| *anu* | string | 13,849 | 604 | 13,754 | 67.6 % | 13.5 % | 18.9 % |
| *apa* | string | 875 | 444 | 870 | 76.1 % | 9.1 % | 14.8 % |
| *atra* | string | 76 | 6 | 76 | 85.5 % | 3.9 % | 10.5 % |
| ***atha*** | string | **173** | **24** | 160 | **63.1 %** | **7.5 %** | **29.4 %** |
| privative *a‑* | morph | 4,320 | n/a | 4,320 | 99.9 % | 0.1 % | 0.0 % |
| negative *an‑* | morph | 4,481 | n/a | 4,481 | 99.9 % | 0.1 % | 0.0 % |

Five examples per class per family are in the JSON envelope; the TSV carries one of each.

## 4. The >15 pp ledger, applied mechanically

A family qualifies when **one category differs from BOTH references by more than 15 pp**.
That is the handoff's rule and it is computed, not judged.

| Family | worst category | Δ vs *anna* | Δ vs *agni* | >15 pp | PWG counterpart |
|---|---|---:|---:|---|---|
| *anya* | compound | −6.9 | −3.4 | no | yes |
| *antar* | simplex | +3.8 | +6.2 | no | yes |
| *ati* | derivative | +5.0 | −0.9 | no | yes |
| *anu* | compound | −10.5 | −7.0 | no | yes |
| *apa* | derivative | +1.0 | −4.9 | no | yes |
| *atra* | compound | +7.4 | +10.9 | no | yes |
| ***atha*** | simplex | **+15.6** | **+18.0** | **yes** | yes (24) |
| privative *a‑* | compound | **+21.8** | **+25.3** | **yes** | no |
| negative *an‑* | compound | **+21.8** | **+25.3** | **yes** | no |

### Recommendation — one row, not two

1. **Add *atha* to the A68 §6.2 table.** PD 173 headwords, PWG 24 (7.2× — a smaller lead
   than *anna*'s 26.6× or *agni*'s 13.6×), 63.1 / 7.5 / 29.4. It is the only family inside
   *a*–*apaca-* that is *less* compound-hungry than both references, and it sharpens the
   section's point: PD's lemmatisation policy is compound-maximal for substantive families
   but not for function words, where it nearly matches PWG's selectivity.
2. **Do not add the privative rows.** They qualify numerically (25.3 pp), but (a) 99.9 %
   compounds is true by construction — the analysis *is* `a‑` + base — so the row states the
   definition; (b) the table's PWG column is a headword-prefix count, and PWG's machine text
   prints no analysis parenthesis, so the morphological set has no PWG counterpart to put in
   it; (c) the section already carries the privative numbers in the prose paragraph that
   follows the table. A row would duplicate a definition where the text already has a
   measurement.

_Applied in the A68 PR that accompanies this report:_ the *atha* row, and the one clause the
row forces — "Two families show the policy at work" becomes "Three families …, the third as
its exception". The two existing rows keep the draft's figures (77.5 / 8.7 / 13.8 and
73.7 / 14.9 / 11.4); this pass re-derives them at 78.1 / 8.1 / 13.8 and 74.6 / 14.0 / 11.4, a
≤0.5 pp drift that a later prose pass should fold in together with the accent-normalised
privative count of §5._

## 5. The privative recount and the density multiple

A privative/negative analysis is `a‑`/`an‑` **plus a base**, so the count is entry-level and
requires a second member; `(a)` and `(an)` are the letters, not privatives. Two rules are
reported because they differ by exactly one thing — whether a Vedic accent on the prefix
vowel counts as a different prefix.

| Rule | *a‑* | *an‑* | total | share of population | density w/o them |
|---|---:|---:|---:|---:|---:|
| Literal `a-`/`an-` (the draft's rule) | 4,419 | 4,475 | **8,894** | 8.6 % | **21.3×** |
| Accent-normalised (this pass's class rule) | 4,698 | 4,754 | **9,452** | 9.2 % | **21.1×** |

The draft's ≈8,900 and 21.3× are reproduced to 6 entries (0.07 %) by the literal rule. The
accent-normalised rule adds 558 entries: PD accents the base (*á-cyuta*, *án-ābhāsa*) as
often as it leaves it bare, and an accent on the prefix vowel does not make the formation any
less privative. So the section's "about 8,900 — 8.6 %" is the accent-blind count, and the
honest figure for the same class is ≈9,450 (9.2 %); the density multiple moves 21.3× → 21.1×.
**The qualitative claim is unaffected:** without the privatives PD is still 21× denser than
PWG per headword, an order of magnitude.

**Density multiple, recomputed** from the committed headword lists
([HeadwordLists/now-2026](https://github.com/gasyoun/SanskritLexicography/tree/master/HeadwordLists/now-2026),
Sanskrit collation, `apaca` frontier): 104,959 ÷ 4,519 = **23.2×**; 21.1× / 21.3× without
the privatives, as above.

_A68 §6.2 has since folded this in: its privative paragraph now carries 9,452 headwords
(9.2 %), 21.1×, with the accent-blind 8,894 / 8.6 % / 21.3× kept beside it as the literal
count (gasyoun/Uprava#5420, 19-10-2026)._

## 6. Limits

- **±3 pp** on shares: the derivative test is a suffix test on the analysis's last member,
  not a morphological parser. A compound whose last member is a suffix word (`…-tva`,
  `…-ka`) counts as a compound here.
- **String vs morphological** families are not comparable: *anu* is a string family of
  13,849 headwords, most of which are ordinary *anu‑* compounds, not the preverb as a lexical
  unit. No claim is made that *anu* "is" the preverb.
- **`a` is not a family.** As a prefix string it matches all 104,950 headwords, which is why
  the privative set had to be morphological.
- **One PD analysis is a mis-split:** *atra* is printed `(á-tra)`, which the rule reads as
  `a-` + `tra` (a compound); it is historically `a-trá`, a privative. The family row keeps
  the printed form — the atlas classifies what the dictionary prints, not what it should
  have printed.
- **PWG has no analysis parenthesis**, so PWG contributes only headword counts. The A68
  table's PWG column is a completeness check, not a composition measure.
- **Rights**: `pd.txt` is not committed (licence matrix family E7, PD rights unverified);
  only derived counts ship.
- The 380 CORRECTIONS-block headwords are counted in the population, not classified; they
  are 0.37 % of it.

## 7. Reproduce

```sh
curl -L -o pdtxt.zip https://www.sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip
unzip pdtxt.zip                      # → txt/pd.txt, 55,122,076 B
shasum -a 256 txt/pd.txt             # 4ee75e66…724442
python scripts/pd_family_composition.py --pd txt/pd.txt --pwg ../csl-orig/v02/pwg/pwg.txt
python scripts/pd_family_composition.py --check --pd txt/pd.txt   # exit 0 = byte-identical, pins hold
python -m pytest tests/forensic/test_pd_family_composition.py -q
```

The script is stdlib-only, deterministic, and writes both artifacts; `--check` fails closed
on a stale TSV, a stale JSON, a population outside the ±6 band, a literal privative count
outside ±2 % of 8,900, or an accent-normalised one drifting more than 10 %.

_Dr. Mārcis Gasūns_
