# PD locus fields verified and extended — C2, 29-10-2026

_Created: 29-10-2026 · H7458 · Scope: all 107,630 entries and all 302,442 H6949 quotation tails in the published letter-`a` PD machine text · Status: **full-population deterministic extraction with complete marker reconciliation** · Evidence: fields and aggregates **derived**, no human `reviewed` claim._

## 1. Result

**105,177 of PD's 107,630 machine-readable entries — 97.72 % — carry at least one
well-formed `(siglum, locus)` pair.** The companion table retains all 107,630 entries,
including the 2,453 without such a pair.

The run materializes **391,444 pairs**: 356,478 directly siglum-bearing and 34,966
semicolon continuations with the siglum inherited under C1's rule. This is 93.23 % of
H6949's 419,890 raw attestation markers. The remaining 28,446 markers are not silently
dropped: each is accounted for by a named diagnostic class.

| Entry-level measure | Entries | Share of 107,630 |
|---|---:|---:|
| H6949 entries with at least one raw attestation marker | 105,944 | 98.43 % |
| **C2 entries with at least one well-formed `(siglum, locus)`** | **105,177** | **97.72 %** |
| Entries without a well-formed pair | 2,453 | 2.28 % |

The 767-entry difference between the first two rows consists of entries whose H6949
markers did not yield a located pair under the C2 typographic check. The other 1,686
entries were already quotation-free in H6949; they remain visible rather than being
removed from the denominator.

## 2. What verification changed

H6949 deliberately counts a broad citation-marker unit. C2 asks a narrower question:
is there actually a siglum **and a locus value**? It does not rewrite H6949 or C1.
Instead, every raw marker is reconciled exactly.

### Siglum-bearing markers

| Class | Count |
|---|---:|
| Well-formed direct `(siglum, locus)` pairs | 356,478 |
| Lowercase discourse tokens not accepted as sigla (`cf.`, `comm.`, `etc.` …) | 8,926 |
| Candidate siglum with no following locus (`Nāg.`, bare `Ed.`, source-only references …) | 10,925 |
| Roman-numeral tokens already consumed by the preceding locus, not separate sigla | 7,841 |
| Edition qualifiers split from their siglum by a `[Page…]` marker | 47 |
| **Total, exactly H6949's siglum-locus count** | **384,217** |

### Continuation markers

| Class | Count |
|---|---:|
| Well-formed continuation pairs | 34,966 |
| Semicolon tails with digits but no parseable initial locus | 310 |
| Digits belonging only to a `[Page…]` marker | 344 |
| Continuations with no assignable preceding siglum | 53 |
| **Total, exactly H6949's continuation count** | **35,673** |

These classes answer different questions. In particular, `marker_consumed_by_locus`
is mostly a correction of H6949's double reading of roman numerals, not missing text;
`siglum_without_locus` can be a legitimate unlocated reference; and an unassigned
continuation is an unresolved residue, not a reason to invent a siglum.

## 3. Extension to explicit fields

The new locus-level TSV gives every accepted pair a stable sequential `locus_id` and
carries its entry `lid`, printed page, headword, quotation and citation positions,
siglum, normalized locus, kind (`siglum` / `continuation`), and exact raw citation with
whitespace normalized. Two examples from `akāmataḥ` (`L=1531`) illustrate the unit:

```text
ManuSm.  2. 181   siglum
ManuSm.  9. 242   continuation
ManuSm. 11. 45    continuation
```

The extractor also repairs forms that a count-only pass cannot represent faithfully:

- `TaiS. V. v. 1. 6` is one pair, not a `TaiS.` pair plus a new `V.` siglum.
- `ṚV. vi. [Page…] 17. 8` retains the complete locus `vi. 17. 8`.
- `NyāySu. [Page…] (So.) 72. 2` yields one `NyāySu.` pair; `(So.)` is not another work.
- `MahāBhā. i. (App.) 64. 27` retains the appendix qualifier inside the locus.
- `Śiśu- Va. 3. 4` becomes `ŚiśuVa.` only because the joined siglum exists independently
  in the committed PD siglum census.
- A segment such as `it stands for all its 18 varieties` does not manufacture a
  continuation from the letter `i` or from the digits later in the prose.

The result is **typographic validation**, not a claim that the cited work has been
identified or that the locus resolves in an external edition. Those are separate C3
questions.

## 4. Method and reproducibility

1. Reused the canonical PDScan 2020 `txt/pd.txt`: 55,122,076 bytes, SHA-256
   `4ee75e6619ee2bd86a331586bb922101e0ae090f9edd981752cfac36ed724442`.
2. Traversed block runs with H6949's own `quotation_units.split_blocks` and headword /
   whitespace rules. The traversal reproduces all **302,442 quotations** and the frozen
   **107,630 / 384,217 / 35,673 / 419,890** aggregates without changing their artifacts.
3. Required a numeric or roman-numeral locus after each candidate siglum. Lowercase
   tokens are rejected unless the independent `pd_siglum_families.tsv` census knows them.
4. Applied C1's continuation inheritance, while leaving unresolved continuations explicit.
5. Removed `[Page…]` metadata for field extraction, but separately reconciled its effects
   on H6949's raw counts: 344 page-only pseudo-continuations and 47 split qualifiers.
6. Added hand-derived controls for direct loci, continuations, discourse abbreviations,
   roman numerals, page breaks, appendix qualifiers, line-wrapped sigla, prose digits,
   variant/editor notes, sense boundaries, and unassigned continuations.
7. Made the builder fail on any source-hash, population, order, quotation-total, or
   per-class reconciliation drift. `--check` rebuilds and byte-compares all four outputs
   and checks the report's headline values. More precisely, the comparisons are on parsed
   TSV rows and JSON values, not raw bytes.

Commands:

```sh
python3.13 scripts/pd_locus_fields.py --pd /path/to/pd.txt
python3.13 scripts/pd_locus_fields.py --check --pd /path/to/pd.txt
python -m pytest tests/forensic/test_pd_locus_fields.py -q
python -m pytest tests/forensic/test_quotation_units.py tests/forensic/test_pd_edition_availability.py -q
```

Expected C2 check:

```text
PASS C2 105,177/107,630 entries = 97.72%; 391,444 well-formed pairs
```

## 5. Artifacts

- [`pd_locus_fields.tsv`](../data/pd/pd_locus_fields.tsv) — 391,444 explicit pairs with entry and quotation provenance.
- [`pd_locus_coverage_by_entry.tsv`](../data/pd/pd_locus_coverage_by_entry.tsv) — all 107,630 entries, frozen H6949 counts beside C2 counts and coverage status.
- [`pd_locus_rejections.tsv`](../data/pd/pd_locus_rejections.tsv) — diagnostic classes, occurrence and entry counts, up to three examples per siglum/class.
- [`pd_locus_fields_summary.json`](../data/pd/pd_locus_fields_summary.json) — protocol, headline metrics, complete reconciliation, diagnostics, and input hashes.
- [`scripts/pd_locus_fields.py`](../scripts/pd_locus_fields.py) — deterministic builder and checker.
- [`tests/forensic/test_pd_locus_fields.py`](../tests/forensic/test_pd_locus_fields.py) — 14 hand-derived controls.

## 6. Limits and next measurement

- **Coverage is within H6949's quotation tails.** This pass extends counts into fields;
  it does not harvest a new population of references outside those tails.
- **Well-formed is not externally resolved.** A numeric locus can still be OCR-damaged,
  ambiguous, or incompatible with an available edition.
- **No human precision or κ is claimed.** The 97.72 % figure is deterministic typographic
  coverage, not a human-adjudicated correctness score.
- **The 2,453 uncovered entries are not all conversion failures.** They include H6949's
  cross-reference/formal entries and entries carrying only bare or non-locus references.
- **The 53 unassigned continuations remain open.** They are preserved in the diagnostic
  output rather than speculatively attached to a work.

The next useful increment is C3: resolve the extracted sigla and loci against AOB edition
identities and scan targets, while keeping work identity, edition identity, and locus
resolution as three separate measures.

_29-10-2026 — Kimi (`kimi-code-plan-global/k3.1-pro`), H7458/C2; full-population extraction, independent tail reconciliation, and explicit unresolved residue._
