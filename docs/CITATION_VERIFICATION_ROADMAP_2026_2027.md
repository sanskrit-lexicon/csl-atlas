# Citation-verification roadmap 2026–2027 — PWG/MW loci against digital corpora

_Created: 11-07-2026 · Last updated: 11-07-2026_

**What this is.** The program plan for verifying the literary citations of the Petersburg
dictionaries (PWG, later pw/PWK) and Monier-Williams against digital corpora — per-text
resolution censuses on the model of the executed
[`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md)
(H488, 10-07-2026), plus a new per-case lane verifying Böhtlingk's *own explicit corrections*.
Authored audit-first (`--no-interview`): the genuine forks are in [§6 Decisions needed](#6-decisions-needed--rulings-pending),
each with a marked recommendation; they are mirrored to
[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) as `@DECIDE`.

## 0. Worked examples (why this program)

**brū / MBH. 7,9283.** [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt)
line 266324 (`L=53686`, `k1=brU`) carries Böhtlingk's note:

> `{#abruvam, abravIt#} ({#abravat#} <ls>MBH. 7,9283</ls> fehlerhaft für {#abravIt#}, wie die <ls>ed. Bomb.</ls> hat)`

— the Calcutta print reads *abravat* at 7,9283; Böhtlingk corrects to *abravīt* per the Bombay
edition. On the [PWG article site](https://gasyoun.github.io/SanskritLexicography/) (entry key
`br_u~~h0_00_pwg00`) the note surfaces in Russian («ошибочно вместо abravīt, как имеет ed. Bomb.»,
stored in [`RussianTranslation/src/pwg_ru_translated.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/pwg_ru_translated.jsonl)).
Until now such notes were unverifiable apparatus; with DCS, GRETIL, the typed vulgates and
[mahabharata.manipal.edu](https://mahabharata.manipal.edu) they are checkable claims. The same
entry cites `7,9283` again *as a valid ref* and corrects `7,9226` (`yenAvibruvatA praSnam`, ed.
Bomb.) — so note-mining must be context-aware, not string-global.

**Spr. 2790.** `tān havyakavyayor viprān anarhān manur abravīt` — checkable against the typed
2nd edition at [sanskrit-lexicon-scans/boesp2](https://github.com/sanskrit-lexicon-scans/boesp2)
(per-verse viewer `https://sanskrit-lexicon-scans.github.io/boesp2/web1/boesp.html?2790`), with
the ed.1/ed.2 siglum split already explicit in PWG (`Spr.` vs `Spr. (II)`).

## 1. What already exists — consume, don't rebuild

| Asset | Where | State |
|---|---|---|
| Method engine (harvest → fit continuous index → held-out gate → shuffled-null → classify) | [`scripts/forensic/f7_harivamsa_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_harvest.py) · [`f7_harivamsa_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f7_harivamsa_resolve.py) | validated (H488): 206/547 corroborated at exact śloka, ≈75× over null; held-out MW 68.4% vs 2.1% |
| Per-siglum citation counts, PWG | [`literarysource/pwg/lsextract_pwg_06.txt`](https://github.com/sanskrit-lexicon/literarysource/blob/main/pwg/lsextract_pwg_06.txt) (+ [`pwgbib.txt`](https://github.com/sanskrit-lexicon/literarysource/blob/main/pwg/pwgbib.txt) with IAST expansions) | authoritative: ALL 685,196 · `MBH.` 55,834 · `ṚV.` 54,343 · `R.` 23,286 · `HARIV.` 15,633 · `Spr.` 9,360 · `Spr. (II)` 7,309 |
| Cross-dict folded citation graph (11 dicts) | [`data/citations/`](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/citations) (`ls_citation_edges.tsv`, nodes, [`build_ls_citation_graph.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/citations/build_ls_citation_graph.py)) | per-text totals (folds sigla variants; no per-locus index): pwg→Mahābhārata 39,130 · Rāmāyaṇa 27,977 · Pāṇini 21,509 · ŚKDr 20,130 · BhāgP 19,044 · ṚV 18,837 |
| MW citation layers | [`MWS/mwauthorities`](https://github.com/sanskrit-lexicon/MWS/tree/master/mwauthorities) (Scharf–Hyman works XML, `linkmwauthorities_init.txt`) · [`MWS/relative_refs`](https://github.com/sanskrit-lexicon/MWS/tree/master/relative_refs) (`ib_resolve.py` for "ib."-refs) | MW cites `MBh. iii, 14189` (roman book + continuous verse; 29,181 hits), `R. v, 20, 26` — grammar differs from PWG's `MBH. 7,9283`; MW yield in the `<ls>` graph is only 7.9%, so MW needs its own extractor |
| Indische Sprüche, typed | [boesp1](https://github.com/sanskrit-lexicon-scans/boesp1) (ed.1, 5,419) · [boesp2](https://github.com/sanskrit-lexicon-scans/boesp2) (ed.2, 1–7,613; Malten) | complete; local [`IndischeSprueche/data/indische_sprueche.jsonl`](https://github.com/gasyoun/SanskritLexicography/blob/master/IndischeSprueche/README.md) is a 7,537-verse transcription — convenience copy, **not** the citable edition |
| DCS, local CoNLL-U | [`VisualDCS`](https://github.com/gasyoun/VisualDCS) `src/DCS-data-2026/conllu/files/` — Mahābhārata 1,995 files (`MBh, book, adhyāya`), Rāmāyaṇa, HV 118 | full + lemmatized (an *abravīt→brū* query is native); **BORI critical recension** — see §2 caveat |
| GRETIL, local mirror | [`SamudraManthanam/GRETIL-1_sanskr`](https://github.com/gasyoun/SamudraManthanam/tree/main/GRETIL-1_sanskr) `2_epic/mbh` (18 parvans) · `2_epic/ramayana` (7 kāṇḍas) | critical-family e-texts (Tokunaga/Smith); no vulgate MBH, no Sprüche on GRETIL |
| RV verse-linking pilot | [`scripts/build-citation-link-pilot.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/build-citation-link-pilot.mjs) (`<ls>` → VedaWeb `MMHHHVV`) | link-resolution done; error-verification is the W2 extension |
| Scan-locus resolver | [`RussianTranslation/src/ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py) (`Spr. 1` → scan URL; PWG#87 live hrefs) | reuse for badge/link surfacing |
| MBH name indices | [INM (Sörensen)](https://github.com/sanskrit-lexicon/INM) — Calcutta numbering · [MCI (Mehendale)](https://github.com/sanskrit-lexicon/MCI) — BORI numbering | optional anchor donors; INM×MCI shared names = a cheap Calcutta↔BORI bridge probe |

## 2. Method invariants (carried over from H488)

1. **Adjudicate against the edition cited.** PWG/MW cite the **Calcutta vulgate family** by
   continuous śloka numbers. DCS/GRETIL epics are the **critical recension**: a
   vulgate↔critical concordance structurally cannot separate "wrong number" from "verse cut by
   the editors" — measured dead end
   ([`SanskritLexicography/DEAD_ENDS.md`](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md) §8;
   DCS resolved 1 of 587 shared refs). DCS's role here is **reading/lemma evidence** (does a
   brū-form stand in the parallel verse?), never locus arithmetic.
2. **Fitted continuous index, gated.** Per-chapter offsets fitted with robust statistics on PWG
   anchors, **held out on MW**; a shuffled-N null quantifies enrichment; if the held-out gate
   fails, the error test must not run (circularity).
3. **Taxonomy.** Per ref: `corroborated` (headword at cited locus ±3) / `displaced` / `absent`;
   per Böhtlingk-note: `confirmed` / `edition-variant` / `transmission-error` / `unresolvable`.
4. **Per-dictionary citation grammars.** PWG `MBH. 7,9283` (arabic book, continuous verse) vs
   MW `MBh. iii, 14189` — two extractors, one census schema.
5. **Rights.** Harvested e-text bytes stay gitignored; published artifacts are **numbers-only**
   concordances/verdicts;
   [`/publish-safety-check`](https://github.com/gasyoun/claude-config/blob/main/commands/publish-safety-check.md)
   before any kosha release.
6. **Context-aware note mining.** The same locus string can be flagged-erroneous and valid in
   one entry (brū above) — regex alone is not a verdict.

## 3. Text classes — the queue is shaped by addressing, not only mass

**Easy class** (stable addressing + existing digital adjudicator): ṚV (VedaWeb, accented),
AV/ŚBr (GRETIL/TITUS), Pāṇini (sūtra numbers), Manu, **Spr.** (boesp1/2), and the kośas —
ŚKDr, AK, Medinī, AbhCint, Anekārtha, Trikāṇḍaśeṣa — which are **themselves CDSL digitizations**
(self-contained cross-check). High verified-citations-per-effort.

**Hard class** (continuous vulgate numbering, edition families): **MBH** (PWG 55,834 + MW
29,181), **Rāmāyaṇa** (PWG 23,286 numbered `R.`, plus a separate `R. GORR.` Gorresio lane; MW
sarga-addressed), BhāgP (Burnouf-era addressing to confirm in W0), KSS. These need the f7
fitted-index method and vetted vulgate e-texts.

**MBH adjudicator candidates to vet in W1a** (the cited Calcutta 1834–39 itself is scans-only:
[archive.org](https://archive.org/details/mahabharata_nk)):
typed BORI at [bombay.indology.info](https://bombay.indology.info/mahabharata/statement.html) (=
local GRETIL mirror); Kumbhakonam typed at
[sanskritdocuments.org](https://sanskritdocuments.org/) / [SARIT](https://sarit.github.io/);
Nilakantha-vulgate typed candidates — [hinduscriptures.in](https://www.hinduscriptures.in/),
[mahabharata.shreevatsa.net](https://mahabharata.shreevatsa.net/) (Parimal text aligned to Dutt),
the digitization catalogued at [shreevatsa.net](https://shreevatsa.net/post/mahabharata-texts-and-translations/);
[mahabharata.manipal.edu](https://mahabharata.manipal.edu) (BORI 73,797 · Kumbhakonam 96,635 ·
Sastri-Vavilla 95,286 · Tatparyanirnaya 5,180 — the only home of the last two; Angular SPA with a
private API, TLS chain fails verification, `curl -k` works; role gated by D3).

## 4. Waves

**W0 — this pass (H602, done).** Audit + this roadmap; forks parked as D1–D4; wave-1 handoffs
minted and queued.

**W1a — MBH census + Böhtlingk-notes pilot** ([H610](https://github.com/gasyoun/Uprava/blob/main/handoffs/H610-Opus_csl-atlas_mbh_citation_census_11.07.26.md)) —
Opus 4.8 (`claude-opus-4-8`), 1–2 sessions. Port f7 → `f8_mbh_*`: extract both dictionaries'
MBH refs; mine correction notes (`fehlerhaft`, `Druckfehler`, `lies`, `richtig`, `st.`) with
entry context; vet + harvest one vulgate-family e-text; fit per-book continuous index (held-out
MW, shuffled null); classify; verify each note per-case with DCS-reading evidence; deliver
`data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md` (+ meta, numbers-only CSVs). Validation
cases: brū `7,9283` (abravat→abravīt), `7,9226` (yenāvibruvatā praśnam).

**W1b — Sprüche verification census** ([H611](https://github.com/gasyoun/Uprava/blob/main/handoffs/H611-Sonnet_csl-atlas_spruche_citation_verify_11.07.26.md)) —
Sonnet 4.6 (`claude-sonnet-4-6`), 1 session. Harvest boesp1/boesp2 typed verses; extract PWG
`Spr.`/`Spr. (II)` refs (9,360 + 7,309; extend to pw/PWK sigla); verify verse-exists +
headword/pratīka containment (SLP1↔IAST via sanskrit-util); cross-edition hits = edition-siglum
error candidates; deliver `data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md` + verdict
CSV. Validation case: `Spr. 2790`.

**W2 — Rāmāyaṇa + easy-class sweep.** R. edition census first (Schlegel/Gorresio/Bombay), then
the f8 pattern; RV link-pilot → verification upgrade; Pāṇini/Manu/AV/ŚBr; kośas-vs-CDSL
self-check; BhāgP.

**W3 — long tail + surfacing.** Remaining sigla by
[`lsextract`](https://github.com/sanskrit-lexicon/literarysource/blob/main/pwg/lsextract_pwg_06.txt)
rank; an atlas tool page (IAST-first, CSV download per house rules) over the accumulated verdict
layer; article-site badges per D2; paper wiring per D4. Every wave ends with the
[`/artifact-propagate`](https://github.com/gasyoun/claude-config/blob/main/commands/artifact-propagate.md) hub sweep.

## 5. Verification cascade (standing order per MG, 11-07-2026)

For any citation: **local DCS** (lemma/reading evidence) → **local GRETIL mirror** → **curated
edition e-texts** (vetted per §3) → **Manipal spot-checks** (per D3) → **open web / scans** (the
cited print itself, via [`ls_resolver.py`](https://github.com/gasyoun/SanskritLexicography/blob/master/RussianTranslation/src/ls_resolver.py)
scan URLs) — recording at which tier the verdict landed.

## 6. Decisions needed — rulings pending

Audit-derived roadmap: D1's recommendation runs as plan-of-record (clearly dominant); D2–D4 are
parked as GTD `@DECIDE` and do not block W1.

**D1 — wave order.** *Plan-of-record: MBH + Sprüche in parallel (W1a ∥ W1b).* MBH is the
user-named flagship with both worked examples; Sprüche is near-zero setup with a typed
adjudicator already in the org. Alternatives considered: easy-class-first (max verified refs/week
but defers the flagship), MBH-only (single focus, loses the cheap Sprüche win), strict
frequency order (ignores addressing difficulty). Revisit only if W1a's vulgate vetting stalls.

**D2 — article-site verification badges.** Should verdicts surface on
[gasyoun.github.io/SanskritLexicography](https://gasyoun.github.io/SanskritLexicography/) next to
the translated notes («✓ подтверждено по ed. Bomb. / BORI 7.32.64»)? *Recommended: yes, in W3*,
keyed by `L`-id + subcard via the existing JSONL layer. Costs a build-pipeline touch in
[SanskritLexicography](https://github.com/gasyoun/SanskritLexicography); alternative is
atlas-only surfacing (zero cost there, but the notes' readers live on the article site).

**D3 — Manipal tier.** *Recommended: last-tier spot-check + a one-time API recon doc; no bulk
scraper.* Unique value = Sastri-Vavilla and Tatparyanirnaya (nowhere else machine-searchable);
risks of first-class use = fragile private SPA API, broken TLS chain, load ethics. Alternative
(bulk client over all 4 editions) buys recension breadth at real maintenance cost.

**D4 — paper vehicle.** *Recommended:* censuses feed
[A50](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) ("What the tradition cites",
currently data 4/5 · prose 1/5) and stand as per-text forensic docs; open a **new** article ID
only if W1 yields a standalone result (e.g. a measured accuracy rate for Böhtlingk's ed.-Bomb.
corrections). A10 is untouched — already at sign-off. Alternative: a dedicated "citation
forensics" paper now (premature before W1 numbers exist).

## 7. Non-goals

- **No vulgate↔critical concordance as an error adjudicator** — structurally void
  ([DEAD_ENDS §8](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)).
- **No csl-orig edits for Böhtlingk's own apparatus** — "apparatus, not errors"
  ([A10](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md));
  the correction queue stays reserved for digitization-vs-print divergences.
- **No republishing of harvested e-text bytes** (rights; numbers-only artifacts).
- **No Manipal bulk scraping** absent a D3 ruling.
- **No rebuilding** of `lsextract`/`pwgbib`/`mwauthorities`/`ls_citation_graph` — consume them.

## 8. Provenance

Audit + roadmap authored 11-07-2026 by Fable 5 (`claude-fable-5`) under
[H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md);
evidence gathered by three read-only Explore agents over csl-atlas, the org hubs, and
`csl-orig`, plus live probes of GRETIL, Manipal and the scans org. Program requested by MG
11-07-2026 (brū / MBH. 7,9283 exemplar; Manipal edition list; Spr. ed.1/ed.2 tracking; "such
work must be done for other works of MW and PWG as well").

_Dr. Mārcis Gasūns_
