# Citation-verification roadmap 2026–2027 — PWG/MW loci against digital corpora

_Created: 11-07-2026 · Last updated: 02-09-2026_

> **Truth-pass 02-09-2026** (H3775) — `roadmap_handoff_truth.py --check` flagged this
> page drained but still living: **7 of 7 referenced handoffs have shipped, zero remain OPEN**.
> Kept at this path per MG ruling 31-08-2026 (do not archive) — the strategy/plan
> layer still holds even though its backlog has fully closed. A future session
> reopening work here should mint a fresh H### rather than un-close these.

**What this is.** The program plan for verifying the literary citations of the Petersburg
dictionaries (PWG, later pw/PWK) and Monier-Williams against digital corpora — per-text
resolution censuses on the model of the executed
[`HARIVAMSA_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/HARIVAMSA_CITATION_RESOLUTION_CENSUS.md)
(H488, 10-07-2026), plus a new per-case lane verifying Böhtlingk's *own explicit corrections*.
Authored audit-first (`--no-interview`): the genuine forks are in [§6 Decisions needed](#6-decisions-needed--rulings-pending),
each with a marked recommendation; they are mirrored to
[`Uprava/GTD_NEXT_ACTIONS.md`](https://github.com/gasyoun/Uprava/blob/main/GTD_NEXT_ACTIONS.md) as `@DECIDE`.
Amended 11-07-2026 (H661) with the ACL-lineage method uplift — four rulings R1–R4 taken
interactively by MG, see [§2a](#2a-acl-lineage-method-uplift--rulings-r1r4-11-07-2026).

## 0. Worked examples (why this program)

**brū / MBH. 7,9283.** [`csl-orig/v02/pwg/pwg.txt`](https://github.com/sanskrit-lexicon/csl-orig/blob/main/v02/pwg/pwg.txt)
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

## 2a. ACL-lineage method uplift — rulings R1–R4 (11-07-2026)

The program as first written verified citations by **locus arithmetic + headword presence**
only. The ACL claim-verification tradition ([FEVER, Thorne et al. NAACL 2018](https://aclanthology.org/N18-1074/)
and the [FEVER workshop series](https://aclanthology.org/volumes/2024.fever-1/)) separates
*evidence retrieval* from *verdict classification* — the retrieval half was missing. Four
rulings taken interactively by MG, 11-07-2026 (H661):

**R1 — quote-retrieval lane, character-fuzzy, in W1a.** Many PWG entries quote the text they
cite (`yenAvibruvatA praSnam`; full Spr. verses). W1a gains a **deterministic** retrieval
lane: SLP1-normalized character/n-gram fuzzy search of the quoted pratīka across the whole
harvested corpus, *independent of the cited locus*. Normalization-before-matching is the
measured lesson of [allusive text-reuse detection (LaTeCH-CLfL 2019)](https://aclanthology.org/W19-2514/)
— short quotes with few shared words are the hard case, and character-level normalized
matching is the floor method. Payoffs: (a) tiered evidence strength
(`quote-exact` ≫ `quote-fuzzy` ≫ `lemma` ≫ `headword`), (b) `displaced` upgrades from a
dead-end verdict to `displaced-to-<locus>` — a correctable fact, the actual scholarly payoff,
(c) a free baseline comparison (fitted-index-only vs retrieval-only vs hybrid) that hardens
every census against circularity objections. **Embeddings are deliberately NOT in W1a** (the
pipeline stays deterministic per house rules) — the embedding lane
(BuddhaNexus / [SansTib, LREC 2022](https://aclanthology.org/2022.lrec-1.724/) /
[Vedic similarity measures, NLP4DH 2024](https://aclanthology.org/2024.nlp4dh-1.12/)-style
million-scale NN search, DharmaMitra stack) gets its own Fable-tier planning handoff
[H662](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H662-Fable_csl-atlas_embedding-retrieval-lane-plan_11.07.26.md),
planned from the start, adopted where character-fuzzy saturates (paraphrase-level reuse, W2+).
**Plan delivered 11-07-2026:**
[`docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md)
(primary candidate MITRA-E; two-step offline import per house pattern; pilot + adoption
criterion in its §5).

**R2 — gold-standard adjudication set, in W2.** ~200 stratified refs (text class × verdict
class), adjudicated blind with an LLM second annotator (the A44 precedent), reporting
agreement + confusion, so every census from W2 on states measured per-class precision — not
just the aggregate shuffled-null gate. W1 censuses ship without it and get their precision
numbers retro-fitted when the W2 gold set lands.

**R3 — benchmark framing (refines D4).** The verdict layer is built as a **releasable
benchmark dataset** for citation verification in historical lexicography (plausibly the first
of its kind): numbers-only, with a datasheet. The schema fields this requires are cheap in W1
and expensive to retrofit, so they are **mandatory from the first census**: per-ref stable ID,
evidence tier (`quote-exact`/`quote-fuzzy`/`lemma`/`headword`/`none`), verdict class, and the
[§5 cascade](#5-verification-cascade-standing-order-per-mg-11-07-2026) tier where the verdict
landed. A **resource-paper article ID is minted only after W1 numbers exist** (per the
roadmap's own "premature before W1" logic); candidate venues:
[LaTeCH-CLfL](https://aclanthology.org/volumes/2025.latechclfl-1/) (SIGHUM, *ACL-colocated),
NLP4DH. A50 still consumes the counts either way.

**R4 — DharmaMitra engagement after the W1a pilot.** Their production parallel-passage /
semantic-search stack ([Nehrdich](https://sebastian-nehrdich.github.io/), Berkeley) is exactly
the W2+ embedding tech. Outreach is drafted (via `/outreach-draft`, never auto-sent) **after**
W1a produces concrete pilot numbers — a far stronger opener than a cold "we plan to". Until
then, local deterministic tools only.

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

**W1a — MBH census + Böhtlingk-notes pilot ✅ DONE (H610, 11-07-2026, Opus 4.8 `claude-opus-4-8`).**
Delivered [`data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md)
(+ meta), scripts [`f8_mbh_census.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_census.py)
+ [`f8_mbh_verify.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_verify.py),
numbers-only CSVs ([PR #247](https://github.com/sanskrit-lexicon/csl-atlas/pull/247)). Results:
PWG **66,103** MBH loci + MW **29,178**; **2,466** Böhtlingk correction notes; character-fuzzy
quote-retrieval (R1) confirmed **956** notes against BORI reading-evidence (39 % ≈ Harivaṃśa
37.7 %), R3 benchmark schema emitted. Case `7,9226` (yenāvibruvatā praśnam) → confirmed
quote-exact at BORI `07,170.032`; `7,9283` (abravat→abravīt) → D3 escalation.
**The fitted-index locus census was BLOCKED and deferred** at H610 — no free bulk
Nilakantha-vulgate e-text existed (BORI-only ⇒ [DEAD_ENDS §8b](https://github.com/gasyoun/SanskritLexicography/blob/master/DEAD_ENDS.md)).
**✅ UNBLOCKED and done for book 7 (Droṇa), 12-07-2026, Opus 4.8 (`claude-opus-4-8`),
[H761](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H761-Opus_csl-atlas_mbh_fitted_index_nilakantha_vulgate_unblocked_12.07.26.md).**
The premise is refuted: a full Nīlakaṇṭha vulgate (83,971 shlokas, 18 parvans) was scraped from
[sanatana.in](https://sanatana.in/mahabharata/) into CommentaryStrategies
([PR #83](https://github.com/gasyoun/CommentaryStrategies/pull/83)). The f7 fitted-index method
now runs against it for Droṇaparva
([`MBH_DRONA_FITTED_INDEX_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_DRONA_FITTED_INDEX_CENSUS.md),
[`f8_mbh_drona_fitted_index.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_drona_fitted_index.py)):
book-7 vulgate 9,641 shlokas / 202 adhyāyas; PWG 3,590 + MW 194 anchors. **Held-out gate PASSES**
— MW agreement **48.1 %** (90/187) within ±3, δ peaked exactly at 0, vs a **0.0 %** shuffled-N
null; exemplar `MBH. 7,9283` → vulgate 7.200.24 (`…droṇaputram athābravīt`) end-to-end.
Classification: 847 corroborated (29.6 %, vs 0.7 % null), 1,084 displaced, 931 absent; clear
displacement 486 **below** the 1,035 chance mean ⇒ no shared-error excess.
**✅ GENERALIZED to all 18 parvans, 12-07-2026, Opus 4.8 (`claude-opus-4-8`)** —
[`f8_mbh_harvest.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_harvest.py)
(csl-atlas-native harvest of the full sanatana.in vulgate, 83,971 verses) +
[`f8_mbh_resolve.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f8_mbh_resolve.py)
fit the per-parvan index for every book and fold the results into
[`MBH_CITATION_RESOLUTION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/MBH_CITATION_RESOLUTION_CENSUS.md)
§2/§4. **Pooled held-out MW 55.2 % (2,234/4,048) vs 1.4 % null (≈ 40×); every parvan passes;
book 7 reproduces H761's 90/187 exactly.** Note-locus census 409 corroborated / 787 displaced /
1,270 absent. Manipal Sastri-Vavilla (D3) / Calcutta OCR fully moot for the locus census.

**W1b — Sprüche verification census — DONE 11-07-2026** ([H611](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H611-Sonnet_csl-atlas_spruche_citation_verify_11.07.26.md),
Sonnet 5 `claude-sonnet-5`, 1 session). **Scope correction: `boesp1` has no typed text** (only a
scan-page index) — only `Spr. (II)` (6,320 refs extracted) got full text verification; `Spr.`
(9,557 refs) is range-only. Results: 2,621 corroborated (1,332 exact/771 fuzzy/518 lemma) · 443
mismatch (flagged for review, not confirmed) · 3,255 no-quote-to-check · 38 edition-siglum-swap
candidates. **Validation case `Spr. 2790` does not resolve as described above** — the quoted text
this roadmap attributes to it (`tān havyakavyayor…`) actually belongs to the adjacent `M. 3,150`
citation in the same PWG entry, not to `Spr. 2790`; see
[`SPRUECHE_CITATION_VERIFICATION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md)
§2 for the correct reading and full results. Delivered
[`SPRUECHE_CITATION_VERIFICATION_CENSUS.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_CENSUS.md) +
[`SPRUECHE_CITATION_VERIFICATION_VERDICT.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/SPRUECHE_CITATION_VERIFICATION_VERDICT.csv)
(R3 schema). **Not done this pass:** PW/PWK siglum extension, 1st-edition OCR/text-level
verification, human review of the mismatch/swap-candidate queues — queued as census §7 follow-ups.

**W2 — Rāmāyaṇa + easy-class sweep.** R. edition census first (Schlegel/Gorresio/Bombay), then
the f8 pattern; RV link-pilot → verification upgrade; Pāṇini/Manu/AV/ŚBr; kośas-vs-CDSL
self-check; BhāgP. **Per R2:** build the ~200-ref stratified gold set (blind LLM second
annotator) and retro-fit measured per-class precision onto the W1 censuses. **Per R1/H662:**
adopt the embedding retrieval lane here if it clears the
[plan's §5.4 adoption criterion](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EMBEDDING_RETRIEVAL_LANE_PLAN.md)
(parity gate + ≥ 25 new adjudicated paraphrase parallels; pilot handoff mints at W2 time).

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

Audit-derived roadmap: D1's recommendation runs as plan-of-record (clearly dominant); D2–D3
remain parked as GTD `@DECIDE` and do not block W1; D4 was ruled 11-07-2026 (see R3 in
[§2a](#2a-acl-lineage-method-uplift--rulings-r1r4-11-07-2026)).

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

**D4 — paper vehicle.** ~~*Recommended:* censuses feed A50 and stand as per-text forensic
docs; open a new article ID only if W1 yields a standalone result.~~ **RULED 11-07-2026 (R3,
supersedes the open fork):** benchmark-dataset framing adopted — schema fields mandatory from
W1, resource-paper article ID minted after W1 numbers exist, candidate venues
LaTeCH-CLfL / NLP4DH; [A50](https://github.com/gasyoun/Uprava/blob/main/ARTICLES.md) ("What
the tradition cites", currently data 4/5 · prose 1/5) still consumes the counts. A10 is
untouched — already at sign-off.

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
[H602](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H602-Fable_csl-atlas_citation-verification-roadmap_11.07.26.md);
evidence gathered by three read-only Explore agents over csl-atlas, the org hubs, and
`csl-orig`, plus live probes of GRETIL, Manipal and the scans org. Program requested by MG
11-07-2026 (brū / MBH. 7,9283 exemplar; Manipal edition list; Spr. ed.1/ed.2 tracking; "such
work must be done for other works of MW and PWG as well").

§2a ACL-lineage uplift (rulings R1–R4) added 11-07-2026 by Fable 5 (`claude-fable-5`) under
[H661](https://github.com/gasyoun/Uprava/blob/main/handoffs/archive/H661-Fable_csl-atlas_citation-roadmap-acl-uplift_11.07.26.md),
after an ACL Anthology method crosswalk and an interactive four-question ruling round with MG.
Improvement analysis + backlog live in the companion metadoc
[`CITATION_VERIFICATION_ROADMAP_2026_2027.meta.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/CITATION_VERIFICATION_ROADMAP_2026_2027.meta.md).

_Dr. Mārcis Gasūns_
