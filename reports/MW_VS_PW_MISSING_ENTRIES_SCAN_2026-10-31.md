# MW missing-entries scan vs PWG/pwk — the full-inventory two-class answer

_Created: 31-10-2026 · Last updated: 31-10-2026_

**Handoff:** [H7513](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7513-GLM_csl-corrections_mw-missing-entries-scan_30.10.26.md)
· **Question:** KnbRao, 14-09-2026 (Telegram #502926; proposal recorded at
csl-corrections [#119](https://github.com/sanskrit-lexicon/csl-corrections/issues/119)):
*"Can AI be put to try-out this? — add such [MW-skipped] entries by comparing
MW with PWG/pwk."* · **Model:** GLM 5.3 (`zai-coding-plan/glm-5.3`, opencode)

---

## TL;DR

The 14-09 trial (SanskritLexicography/HeadwordLists; sup_7 scope, 13 k rows)
is widened to the **whole inventory**: every PWG/pwk base headword that MW
lacks, split into the mission's two classes with the denominator stated for
both. Over the comparison universe **|PWG ∪ pwk| = 157,994 distinct base
headwords**, **132,284 (83.7 %) resolve verbatim in MW**, leaving **25,710
candidates**:

- **(a) missing-by-error candidates — 19,465** (PWG/pwk *cite* the word; MW
  lacks it or has it under a form that no longer resolves):
  5,021 `mw_lacks` (no MW neighbour at all) · 2,961 `form_unresolved_stem` ·
  11,483 `form_unresolved_nearform` (≥0.80 folded ratio — review flags, not
  matches).
- **(b) expected absence — 6,245** (MW lacks it *and* PWG/pwk never cite it:
  derivative entries — cross-references, re-spellings, gloss-only stubs).

The strongest worklist inside (a): **897 `mw_lacks` candidates cited by
PWG/pwk and corroborated by ≥2 of 39 independent Cologne dictionaries**
(kAritra itself: BHS + Schmidt). Every row is keyed to evidence — source
file, `<L>`-header line, L/pc/k1, first `<ls>` payload.

Every number regenerates from the committed row-level TSV under
`scripts/mw_vs_pw_check.py` (exit 0); pins in
`tests/forensic/test_mw_vs_pw_missing.py` (6/6). Dataset:
[`data/mw_vs_pw/`](../data/mw_vs_pw/README.md).

## 0 — Definitions shipped with the counts

Any number in this space is definition-dependent (the 14-09 recheck §0 rule);
these are the ones this scan commits to, mirrored in
`mw_vs_pw_metrics.json → definitions`:

- **base headword** = `clean(k1)` — SLP1 letters only (accents, `*`-markers,
  digits stripped); the MW side additionally resolves `clean(k2)` aliases
  (MW's hyphenated display forms).
- **pwk** = `pw.txt` + `pwkvn.txt` — the Cologne digitization of Böhtlingk's
  *kürzerer Fassung* including its *Nachträge*; **PWG** = `pwg.txt`.
- **"PWG/pwk cite it"** = the headword has ≥1 entry in pwg/pw/pwkvn whose
  body carries an `<ls>…</ls>` tag with ≥1 alphanumeric character in its
  payload (entry-level raw-tag notion; the finer quotation-linked *unit* rule
  of `data/pwg_dcs/` measures citation units, not entry-level citability).
- **(a) missing-by-error** = candidate absent from MW verbatim that PWG/pwk
  cite — covering both "MW lacks it" and "MW has it under a form that no
  longer resolves" (`stem`/`nearform` subclasses are the review tiers where
  the resolvable-form possibility lives).
- **(b) expected absence** = candidate absent from MW verbatim that PWG/pwk
  never cite.
- **near-form** = best folded difflib ratio ≥ 0.80 with deterministic
  tie-break; a **review flag, not proof of presence** — the kAritra~kArita
  0.92 trap is pinned as the canary.

## 1 — Substrate (reuse of the H7463 Stage-1 join)

| Source | Entries | Distinct base k1 | sha256 (pinned) |
|---|---|---|---|
| `mw.txt` | 286,525 | 194,142 (k1∪k2) | `substrate_pins.json` |
| `pwg.txt` | 123,366 | 106,079 | `430c910f…` — **the H7463 `data/pwg_dcs` pin, byte-identical** |
| `pw.txt` | 170,556 | 151,346 | pinned |
| `pwkvn.txt` | 24,976 | 14,995 | pinned |

The builder **refuses to run** if pwg.txt drifts off the Stage-1 pin, and
pins the same entry register (123,366) — the join substrate is shared, not
re-derived. Corroboration shelf: 39 further v02 dictionaries (abch…yat),
each sha-pinned.

## 2 — The join

| Measure | PWG | pwk-union |
|---|---|---|
| Entries | 123,366 | 195,532 (170,556 + 24,976) |
| Distinct base k1 | 106,079 | 151,368 |
| In MW verbatim | 94,781 | 129,008 |
| Candidates | 11,298 | 22,338 |

Per-source class split (a/b): PWG 10,373/925 · pw 16,556/5,782 · pwkvn
4,332/905 (rows can carry several sources; see metrics for the union).

## 3 — The two classes

| Class | Subclass | Count | Reading |
|---|---|---|---|
| **(a) missing-by-error** 19,465 | `mw_lacks` | 5,021 | cited in PWG/pwk, no MW headword/stem/near-form neighbour |
| | `form_unresolved_stem` | 2,961 | MW carries a stem-sharing form — editorial doublet or omission |
| | `form_unresolved_nearform` | 11,483 | ≥0.80 near form in MW — the kAritra~kArita trap zone, human review |
| **(b) expected absence** 6,245 | `mw_lacks` | 1,943 | uncited derivative, no MW neighbour |
| | `form_unresolved_stem` | 940 | uncited, stem neighbour in MW |
| | `form_unresolved_nearform` | 3,362 | uncited, near-form neighbour |

Denominator for both classes: **157,994** (= in-MW 132,284 + candidates
25,710; regenerates under the check). Corroboration inside (a): 9,799 of
19,465 corroborated by ≥1 of the 39 dictionaries, **4,405 by ≥2**; inside
`mw_lacks` specifically, 897 carry ≥2 independent dictionaries — the
scan-verified-adjudication queue's natural head.

Worked rows (all regenerate from the TSV):

- `kAritra` (kāritra) — class (a), `form_unresolved_nearform` → MW `kArita`
  0.92 (a *different* word: abstract vs causative participle); sources
  `pw.txt:620963 L=216013` + `pwkvn.txt:53131 L=16013` (pc 7-331-d, MAHĀVY.
  245, 844); corroborated bhs+sch. **The motivating case, reproduced
  end-to-end and pinned.**
- `ADAtar` (ādhātar) — class (a) `mw_lanks`, cited in all three sources
  (Spr. 1758 …), corroborated ccs+fri+sch — an example of the ≥2-corroboration
  worklist the 14-09 adjudication can now extend to the full inventory.

## 4 — Caveats on the record

1. **Absence from MW is not automatically MW error** — MW never promised full
   PWG/pwk coverage; class (a) is *candidates for adjudication*, and the
   (a)/(b) split arbitrates only by citation evidence, not by MW's editorial
   policy.
2. Near-form and stem tiers are **review flags**; homonym numbers are
   collapsed by the base-headword rule, and the citation rule is the raw-tag
   notion (§0), coarser than the pwg_dcs quotation-linked unit rule.
3. pwk = `pw` + `pwkvn` is a *digitization-union* definition of Böhtlingk's
   shorter dictionary; PWG's German glosses were not translated or semantically
   compared — the join is spelling-level (SLP1).
4. The scan is read-only over csl-orig; no dictionary file was touched.

## 5 — Regeneration

```
python scripts/mw_vs_pw_missing_build.py   # ~5 min, deterministic; refuses on pwg sha drift
python scripts/mw_vs_pw_check.py           # exit 0; verifies substrate shas when csl-orig present
python -m pytest tests/forensic/test_mw_vs_pw_missing.py
```

Drafted reply for MG's review (no direct posting):
[`MW_VS_PW_DRAFT_COMMENT_csl-corrections-119_2026-10-31.md`](MW_VS_PW_DRAFT_COMMENT_csl-corrections-119_2026-10-31.md).
Prior art this widens: the 14-09 sup_7 trial +
recheck (SanskritLexicography/HeadwordLists), mirrored at
csl-corrections `issues/issue119/`.

_Dr. Mārcis Gasūns_
