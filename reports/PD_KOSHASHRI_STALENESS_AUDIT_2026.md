# PD KoshaSHRI staleness audit — three panels, four verdicts

_Created: 27-10-2026 · Handoff: [H7300](https://github.com/gasyoun/Uprava/blob/main/handoffs/H7300-DeepSeek_csl-atlas_pd-koshashri-staleness-audit_26.10.26.md) · Executor: Kimi Work (Kimi) (filename tier DeepSeek retained as provenance, H3688) · Extends: H6698 C7 (14-10-2026) and the two-digitisations markup audit (25-10-2026)_

**Verdict line.** Cologne's digital PD is **stale by 11 volumes / 1,728 pages / 11 years**
against the print record (ends vol 24, 2008, p. 4328; print reaches vol 35, 2019,
p. 6056 — the Pune-only tail 2009–2019); KoshaSHRI's portal metadata is **current
through 2019** as of 27-10-2026. The markup schemas are **different in kind**, not in
age. In the v7/v8 bracketed-source-mark control **no conversion loss and no editorial
divergence** was found (20/20 marks consistent). For the 2009–2019 print record the
fidelity panel is **STOP_NO_PRINT_ACCESS** — no positive editorial claim is made.

## Panel A — markup capability

`data/pd/pd_koshashri_markup_comparison.tsv` — 12 axes, each with its evidence and
verification date (27-10-2026 re-probes vs carried 25-10-2026 facts marked per row).

Headlines, all re-verified 27-10-2026 unless noted:

- Cologne: one record per entry — `<L>` 107,630 · `<pc>` 107,630 · `<k1>/<k2>`
  107,630 each; **`<ls>` = 0, `<ab>` = 0, `<info>` = 0** (the 25-10 correction:
  PDScan carries no citation markup; sigla are plain text). Bulk text in one zip
  (19,018,957 B → 55,122,076 B), CC BY-NC-SA 3.0, per-entry public HTML.
- KoshaSHRI: no public per-entry artefact (preview login-walled, re-probed
  27-10-2026: `Sign in` title), no bulk export, robots/sitemap 404 (re-probed),
  JS shell + SockJS/STOMP rendering (25-10); the one public machine surface is the
  per-volume JSON (33/35 ids answer).

**Verdict — schema-staleness:** `COLOGNE_FLAT_RECORD_SCHEMA (no <ls>/<ab>/<info>;
sigla plain text) vs PUNE_STRUCTURED_DB (typed per-volume JSON); Pune's entry-level
schema is UNKNOWN_NOT_PUBLICLY_OBSERVABLE — login-walled, never probed past the gate`.
This is an asymmetry of kind and openness, not evidence that either schema is
"stale"; the honest unknown is Pune's entry schema, which the public surface does
not show.

## Panel B — dated content coverage

`data/pd/pd_koshashri_content_coverage.tsv` — the 35-slot KoshaSHRI volume table
(snapshot 27-10-2026) joined to the committed H7275 publication ledger by page
overlap; one row per print volume, `in_cologne_digital_text` from the ledger.

| Measure | Cologne digital | Pune-only tail | Print record |
|---|---|---|---|
| Volumes | 24 (1–24) | **11 (25–35)** | 35 |
| Pages | 4,328 (pp. 1–4328) | **1,728 distinct (pp. 4329–6056)** | 6,056 |
| Years | 1976–2008 | **2009–2019** | 1976–2019 |
| Share of print pages | 71.5 % | 28.5 % | 100 % |

**Verdict — content-coverage:** `COLOGNE_DIGITAL_STALE: ends vol 24 (2008, p. 4328);
the print record reaches vol 35 (2019, p. 6056); Pune-only tail = 11 volumes /
1,728 pages / 2009–2019; KoshaSHRI portal metadata current through 2019 as of
27-10-2026`. Every estate number measured on the machine text is a floor on the
dictionary: it cannot see the 2009–2019 tail at all.

**Source anomalies, explicit** (all carried in the verdicts JSON):

- Portal ids **12 and 14** answer error pages (the gap C7 saw on 14-10-2026,
  unchanged — canary K5); their pages/years come from the H7275 ledger and are
  marked `ledger-fallback`, unverified against the portal.
- Year disagreements portal vs ledger: vol 6 (1980 vs 1981), vol 32 region
  (2016 vs 2015/2016), vol 33 (2017 vs 2016/2018).
- Boundary disagreements in the 5521–5708 region: the **portal** lists vol 32
  (5521–5608) *inside* vol 31 (5409–5608) — an 88-page internal overlap (the naive
  per-volume page sum 1,816 vs the deduped 1,728 tail is exactly this overlap);
  the **ledger** double-lists pp. 5609–5708 under rows 32 and 33 (100 pages
  double-listed). Both sources carry the defect; the deduped figure is used.
- Page 2888 is absent from both sources (vol 15/16 boundary) — consistent gap,
  likely a plate page.

## Panel C — same-print-page fidelity: the v7/v8 bracket-mark control

`data/pd/pd_v78_bracket_mark_control.tsv` — 20 mark observations on 4 print pages
(Cologne scans `pd7-3485.pdf`, `pd7-3549.pdf`, `pd7-3559.pdf`, `pd8-4168.pdf`,
fetched 27-10-2026, eyeballed at full resolution, not committed), each compared
against the machine text of the same printed page.

The decision rule (locked in the handoff): a bracketed source mark present in
print but absent from the machine text = **conversion loss**; absent from both =
**editorial change** only after the print check; present in both = consistent.

| Cell | n | Examples |
|---|---|---|
| consistent (print ✓ machine ✓) | **20** | `[DBHS.]` ×12 (L89300, L89301, L89302 ×2, L89316, L89318, L89325, L89330, L90861, L90863, L90874); `[VIŚVA.]` ×3 (L90866, L104962, L104964); editorial brackets `[better subantamātraprasaṅgaḥ]`, `[Read …]` ×2, `[AltGr. II. 1 nt. 26]`, `[m. Liṅgānu. (Vā.) 14. 19c.]`; grammar brackets sampled on the antara page |
| conversion loss (print ✓ machine ✗) | **0** | — |
| editorial-change candidate (print ✗ machine ✗) | **0** | — |

Two negative controls make the control honest: L89324 (*anopalambha*) carries a
**bare** `DBHS.` in print and bare in the machine text; L90861 (*antamaśatas*)
carries bare `DBHS.` inside `(v.l. …)` parentheses in both. Bracket *absence*
matches print too — so the bracket/no-bracket variation in the machine text is
print-faithful, not conversion noise. In vols 7–8 the machine text carries 141
bracketed lexicon-siglum marks across 135 entries (census, sigla set PW/pw/MW/
APTE/DBHS/VIŚVA./ŚabdaKaDru.); the 20-mark sample covers the densest pages.

**Verdict — conversion-loss:** `NOT_DETECTED_IN_V78_SAMPLE: 20/20 bracketed source
marks on 4 print pages of vols 7–8 present in both print and machine text; 0
print-only marks; sample is not the dictionary`.

**Verdict — editorial-change:** `NO_POSITIVE_CLAIM: tags alone prove nothing; in
the v7/v8 print-checked sample no divergence was seen (20 marks, incl.
bare-vs-bracketed DBHS. variation matching print); for the 2009–2019 tail:
STOP_NO_PRINT_ACCESS`.

**2009–2019 sub-panel: `STOP_NO_PRINT_ACCESS`.** No page images of ledger rows
9.1–35 are reachable in the estate or over the read-only archive routes (H7275
layer-2 precedent, 26-10-2026); KoshaSHRI entry preview is login-walled and no
permission is held. Nothing about entry/text differences in the 2009–2019 print
record is claimed.

## Five canaries

`data/pd/pd_koshashri_canaries.tsv` — all five hold at build time and are pinned
in `tests/forensic/test_pd_koshashri_staleness_audit.py`:

1. **K1** vol 1 = 1976, pp. 1–216, A.M. Ghatage.
2. **K2** vol 35 = 2019, pp. 5881–6056, closing *abhigamyamānaparadārādi*.
3. **K3** Cologne `<L>` = 107,630 and `<ls>` = 0 (the 25-10 correction stays fixed).
4. **K4** `total_vocables` = 100 in every answering record — a constant, never a census.
5. **K5** the portal gap persists: error ids = [12, 14], 33/35 answer.

## Rights / provenance

`data/pd/pd_koshashri_rights_provenance.md`. KoshaSHRI is all-rights-reserved:
public per-volume JSON metadata only, no entry text, no circumvention, no bulk
harvest, no relicensing. Cologne is CC BY-NC-SA 3.0: derived counts only; scan
PDFs eyeballed and discarded, not committed.

## Limits / unknowns

- KoshaSHRI's entry-level markup and schema remain **unobservable** (login wall);
  nothing here claims it is poor, absent or stale.
- The 2009–2019 print-vs-digital fidelity is **unmeasured** (STOP_NO_PRINT_ACCESS).
- Vols 12/14 metadata are ledger-fallback; the 5521–5708 boundary region disagrees
  between the two sources; page 2888 is a consistent gap.
- The v7/v8 control samples 20 marks on 4 pages of two volumes; it detects gross
  conversion loss, not rare loss.

## Repro

```bash
python3 scripts/pd_koshashri_staleness_audit.py --check   # artifacts + canaries, offline
python3 -m pytest tests/forensic/test_pd_koshashri_staleness_audit.py -q
```

Live probes (27-10-2026, browser UA; no authentication):

```bash
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
for n in $(seq 1 35); do curl -sS -A "$UA" "https://koshashri-dc.ac.in/search/fetchVolumeInfo/$n"; done
curl -sS -A "$UA" -c jar -o /dev/null https://koshashri-dc.ac.in/
curl -sS -A "$UA" -b jar https://koshashri-dc.ac.in/search/preview/1 | grep -o '<title>[^<]*'
curl -sS -A "$UA" -o pdtxt.zip "https://sanskrit-lexicon.uni-koeln.de/scans/PDScan/2020/downloads/pdtxt.zip"
for p in 7-3485 7-3549 7-3559 8-4168; do
  curl -sS -A "$UA" -o "pd$p.pdf" "https://www.sanskrit-lexicon.uni-koeln.de/scans/PDScan/PDScanpdf/pd$p.pdf"
done
```

_Dr. Mārcis Gasūns_
