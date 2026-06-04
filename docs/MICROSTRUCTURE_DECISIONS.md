# Microstructure line — decision log (issue #30)

Decisions captured interactively with the maintainer (M.G.) for the
**dictionary microstructure analysis** line of
[csl-atlas#30](https://github.com/sanskrit-lexicon/csl-atlas/issues/30)
(`scripts/lexico/`, extractors m1–m4). Newest round first. Each row is a
human decision, not an agent inference — recorded so the next session does not
re-litigate it.

---

## Round 1 — 2026-06-04: direction after the m1–m4 merge (PR #31)

| # | Question | Decision | Consequence |
|---|---|---|---|
| 1 | After m1–m4 merged, what should "continue" produce next? | **Unified per-lemma profile** | Build the integrative `(dict, L)` join of m1–m4 into one microstructure dataset. Code-doable now — no human blocker. |
| 2 | Which finding / Publications article to land first? | **Hold all papers** | Stay in data/tooling mode; no Article 9 (verb-derivation), 10 (compound), or 12 (citation networks) write-up yet. |
| 3 | How to handle the Russian dashboard terminology? | **Defer dashboard** | No reader-facing Observable (EN/RU) pages yet, so no RU lexicographic terminology needed now. Keeps this a data effort. |
| 4 | Scope for the indigenous-root line (m4)? | **Deepen SKD/VCP quality** | Decode SKD anubandha it-markers, split **veṭ** from seṭ/aniṭ, trim abbreviated-gaṇa noise. Broadening to SHS/YAT verbal layers is **deferred**, not dropped. |

**Net direction:** data/tooling, not prose or UI. Two deliverables in flight:

- **(A) Unified per-lemma microstructure profile** — join m1–m4 on `(dict, L)`
  into one table (the integrative dataset the four scripts were building toward).
- **(B) Deepen m4 on SKD/VCP** — raise pada/transitivity coverage via each
  dictionary's own indigenous it-marker convention; split veṭ; denoise gaṇa.

**Explicitly out of scope for now (by decision):** paper drafts (Articles 9/10/12),
the EN/RU reader dashboard, and broadening m4 to additional dictionaries.

### Open questions feeding round 2
- **(B)** needs SKD's anubandha (it-marker) convention — how to source it, and
  confirmation of the proposed decoding against real SKD entries.
- **(A)** output shape, dictionary scope, and how m3's cross-reference *edges*
  fold into a per-*lemma* profile (degree counts).

---

## Round 2 — 2026-06-04: how to execute (A) and (B)

Context brought to the table first: probing SKD/VCP showed **SKD encodes the
dhātupāṭha annotation as Vopadeva/Kavikalpadruma anubandhas** (single romanized
it-letters right after `¦`) — the exact grammatical layer VCP writes out in
`0`-abbreviations — and the two **cross-walk on shared roots**:

- `aGa`: SKD `i N gatO` ↔ VCP `idit gatO BvAdi0 Atma0 saka0 sew` ⟹ SKD `i` = idit,
  SKD `N` (ṅit) = ātmanepada.
- `akza`: SKD `na U vyAptO` ⟹ SKD `U` (ūdit) = veṭ (Pāṇ. 7.2.44).

| # | Question | Decision | Consequence |
|---|---|---|---|
| 5 | How to decode SKD's anubandhas (i/ka/Na/U/t/Sa/ya/Ya/f/ir/O/x…)? | **Cross-walk + maintainer adjudicates** | Learn the anubandha→property map empirically from roots shared by SKD and VCP (VCP spells out what SKD encodes), propose the key, M.G. corrects the linguistics. Round 3 brings the proposed key. |
| 6 | Scope of the unified per-lemma profile? | **All 43 dicts + per-dict fingerprint** | Build the full sparse `(dict,L)` join over every dict m1–m4 touched, PLUS an aggregate per-dict "microstructure fingerprint" (subentry / preverb / xref / root densities). |
| 7 | How to represent veṭ (optional seṭ)? | **Own veṭ column** | Add `vet` alongside `set`/`anit`; VCP `sew … vew` → `set=1 AND vet=1` (veṭ as a lossless refinement of seṭ). VCP `vew` = 98 roots now mis-bucketed as seṭ; SKD veṭ via `U`/ūdit. |

**Mechanical wins greenlit (no further input needed):** add the `vew`→veṭ column;
extend the gaṇa table to VCP short forms `cu0/tu0/di0/ju0/sO0` (confirming the
ambiguous `sO0`, `di0` expansions with M.G.); keep the documented first-match caveat.

### Open questions feeding round 3
- The **proposed SKD anubandha→property key** from the SKD∩VCP cross-walk, for
  M.G. to adjudicate — especially the non-pada markers (`t`, `ka`, `ma`, `f`/ṛ,
  `Sa`, `ya`, …) whose role isn't fixed by the pada cross-walk alone.
- Ambiguous gaṇa short-form expansions: `sO0` (svādi?), `di0` (divādi?).

---

## Round 3 — 2026-06-04: adjudicating the SKD anubandha key

I ran the SKD∩VCP cross-walk (`scripts/lexico/_xwalk_skd_vcp.py`, **763 unambiguous
1:1 shared roots**). It independently reproduces four Pāṇinian sūtras from raw
co-occurrence — full evidence table in `docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`:

- `Na` (ṅit) → ātmanepada 82%  [Pāṇ 1.3.12 anudāttaṅita]
- `Ya` (ñit) → ubhayapada 96%  [Pāṇ 1.3.72 svaritañitaḥ]
- `i` → idit 90%  [Pāṇ 7.1.58 idito num]
- `u` (ūdit) → veṭ 40%  [Pāṇ 7.2.44 …ūdito veṭ]
- plus `ka`/`t` → ubhaya 92–94% (Vopadeva-specific), `Sa/Si/ya/O/na/ma` → parasmaipada.

| # | Question | Decision | Consequence |
|---|---|---|---|
| 8 | Adopt the cross-walk pada key for SKD now? | **Hold for Kavikalpadruma check** | Do **not** bake SKD pada decoding into m4 yet. The key stays a documented proposal (`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`) for M.G. to verify against Vopadeva's paribhāṣā / Durgādāsa. SKD `pada` column stays blank until verified. |
| 9 | What does `f` (ṛ-anubandha, 133×, highest-freq marker) mark? It does not fix pada (50/39 para/ātma). | **Marks something specific — M.G. to specify** | Don't infer pada from ṛ. Leave pada indeterminate for ṛ-roots; reserve a column for whatever behavior M.G. names (round 4). |
| 10 | Build a prose transitivity detector for SKD (Durgādāsa `sakarmmaka`/`akarmmaka`)? | **Yes** | Anubandhas don't carry transitivity (saka ~75% across every marker); add a prose-scan signal so SKD gets a transitivity column like VCP. |

**Net:** SKD **pada** decoding is HELD (awaiting M.G.'s Kavikalpadruma verification).
Greenlit to build now: SKD **transitivity** (prose), **veṭ** column, VCP **gaṇa**
short-forms, and the **unified profile + per-dict fingerprint**.

### Open questions feeding round 4
- **What does the ṛ (`f`) it-letter mark?** (M.G. to specify — reserved as its own column.)
- **M.G.'s verification of the proposed pada key** against the Kavikalpadruma → then I bake it into m4.
- **gaṇa short-form expansions** `di0` (divādi?) and `sO0` (svādi? sautra?) — confirm to add.

---

## Build log — 2026-06-04 (what was implemented under these decisions)

All validated (`validate_lexico.py` — m1–m5 pass), **not committed** (working tree
holds the intentional release-bucket changes; awaiting a commit decision).

**(B) m4 deepening — `scripts/lexico/m4_indigenous.py`:**
- **veṭ column** (decision #7): `_VET` = `vew`; `sew … vew` ⟹ `set=1 AND vet=1`. veṭ roots: SKD 40, VCP 58.
- **VCP gaṇa short-forms** (decision #6): added `cu0`/`tu0`/`ju0` → VCP gaṇa coverage **1,593 → 1,954** (+361). Held out: `di0`, `sO0` (round 4).
- **prose transitivity** (decision #10): match stems `sakarmmak`/`akarmmak` (catches sandhi `akarmmako`/`-kaH`); SKD trans 1,150 → 1,156.
- SKD **pada** decode from anubandhas **NOT applied** (decision #8 hold); SKD pada/trans remain prose-only.

**(A) unified profile — `scripts/lexico/m5_profile.py` (new):**
- `data/lexico/microstructure_profile.csv` — **60,328 rows** over 22 dicts; lossless join of m1–m4 on `(dict, L)` (m3 edges folded to `xref_out` out-degree). Columns carry every layer + a `layers` tag (`sub|preverb|xref|root`).
- `data/lexico/microstructure_fingerprint.json` — per-dict densities + **dominant layer**, which cleanly types the dictionaries: **pwg·mw = xref**, **ap·pw·ben·ap90·stc = subentry**, **skd·vcp·krm = root**. The macro/micro thesis (issue #30) in one aggregate.
- `validate_lexico.py` extended with an m5 lossless-join invariant (profile keys == union of source keys; folded `xref_out` == m3 edge counts).

**Evidence / artifacts:** `scripts/lexico/_xwalk_skd_vcp.py` (cross-walk),
`docs/MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md` (proposed key, awaiting verification).

---

## Round 4 — 2026-06-04: defer the open linguistics, land the build

| # | Question | Decision | Consequence |
|---|---|---|---|
| 11 | What does the ṛ (`f`) it-letter mark? | **Leave for later** | Don't decode ṛ now. m4 records ṛ-roots but assigns them no pada/behavior; revisit with the pada-key verification. |
| 12 | Add gaṇa short-forms `di0` / `sO0`? | **Neither — keep holding** | Leave both out of the gaṇa table until M.G. checks VCP's own abbreviation key. (`cu0`/`tu0`/`ju0` already added stand.) |
| 13 | How to land the built lexico work? | **Commit and push / PR** | Commit the lexico + docs slice (only) and push for review — leave the release-bucket working-tree changes untouched. |

**Net:** the SKD pada decode and the two ambiguous gaṇa forms are all parked on the
same gate — M.G.'s verification against the Kavikalpadruma / VCP abbreviation tables.
Nothing more to build until then; the deliverables (A profile, B veṭ/gaṇa/transitivity)
ship as-is via PR.

**Shipped:** [csl-atlas#33](https://github.com/sanskrit-lexicon/csl-atlas/pull/33)
— branch `feature/microstructure-profile` off `main`, lexico + docs only.

## The single open gate

Everything still pending in this line waits on **one** maintainer action: verify the
proposed SKD anubandha→pada key (`MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md`) against the
Kavikalpadruma. That unblocks (a) baking SKD pada into m4, (b) the ṛ-marker column,
(c) the `di0`/`sO0` gaṇa forms. **Code-doable seams that do NOT need that gate** (open
for a future round): m3 cross-dict cross-reference graph overlap (does MW `cf.` inherit
PWG `Vgl.`? — lineage roadmap §3.1) and AP/AP90/BEN `cf.` target parsing.

---

## Round 5 — 2026-06-04: the next ungated seam

| # | Question | Decision | Consequence |
|---|---|---|---|
| 14 | Next on #30 while the SKD pada gate is open? | **m3 cross-dict cross-reference graph overlap** | Build the §3.1 lineage measure — does MW `cf.` inherit PWG `Vgl.`? |

**Built — `scripts/lexico/m6_xref_lineage.py`** (validated, m6 check added): normalizes
m3 edges (unify PWG `°` / MW `-`, drop SLP1 accents) and intersects the two edge sets.
**Finding — PARTIAL overlap:** 641 shared directed edges; **MW 21.8% / PWG 9.1%** of
cross-refs on the 2,538 lemmas both treat (Jaccard 0.069). A shared cross-reference CORE
(variant-form / cognate-root pointers, well above chance) plus large independent expansion
— **not** wholesale inheritance. Write-up: `docs/MICROSTRUCTURE_XREF_LINEAGE.md`; outputs
`xref_lineage.json` + `xref_shared_edges.csv`. Still ungated and open: AP/AP90/BEN `cf.` parsing.

---

## Round 7 — 2026-06-04: Apte `cf.` parsing (last ungated seam)

| # | Question | Decision | Consequence |
|---|---|---|---|
| 15 | How strict to parse the AP/AP90 `cf.{#…#}` slot (mixed lemma / quote / cognate / citation)? | **Lemma edges + quotes to a side file** | m3 captures lemma-like `cf.{#…#}` as cross-ref edges; multi-word / glued `{#…#}` → `xref_cf_quotes.csv`. |

**Built** (m3 extended; m5/m6 regenerated; validated, m1–m6 pass): new cf-lemma edges
**AP 609 / AP90 446 / CAE 196** (CAE a bonus — it also uses `cf.{#…#}`); **517 cf-quotes**
to the side file (AP 432, AP90 79, CAE 5); **BEN = 0** (cf. purely cognate/citation — does
no internal Sanskrit cross-referencing). MW unchanged (7,665) ⟹ MW×PWG headline unchanged.
**New result — a positive control:** AP × AP90 (same dictionary, two editions) overlap
**85.5%** vs MW × PWG **21.8%**, confirming the measure detects true descent and that MW×PWG
is a shared core, not inheritance. Doc updated: `MICROSTRUCTURE_XREF_LINEAGE.md`.

**With this, the ungated code-doable #30 seams are exhausted** — everything still open
(SKD pada decode, ṛ-marker, `di0`/`sO0` gaṇa) waits on the one maintainer gate: verifying
the proposed SKD anubandha key against the Kavikalpadruma.

---

## Round 8 — 2026-06-04: the SKD key VERIFIED (gate cleared) + SKD re-decoded

The maintainer supplied the **Śabdakalpadruma front matter** (`docs/refs/SKD_Front pages.docx`)
— Durgādāsa's **Dhātudīpikā** 46-anubandha *phala* table. This **clears the round-3 #8 hold**
and **corrects** the proposal.

| # | Question | Decision | Consequence |
|---|---|---|---|
| 16 | ṛ-anubandha meaning (round 4 #11, deferred)? | **Operation-it: caṅ a-hrasva** (Pāṇ 7.4.2) | ṛ never marked pada — explains the cross-walk's 50/39 split. |
| 17 | Rewrite the key doc? | **Yes** | `MICROSTRUCTURE_SKD_ANUBANDHA_KEY.md` is now the **authoritative** Dhātudīpikā key; the cross-walk is demoted to "empirical recovery, source-corrected." |
| 18 | Re-decode SKD via the key? | **Yes** | m4 decodes the anubandha slot → gaṇa (10 classes) + pada (ṅ/ñ only) + operation-its; new `anubandhas` column. **SKD gaṇa 1,117→1,737, pada 1,167→1,498.** |
| 19 | Trust the digitized slot first? | **Re-probed** | 1,925/2,544 SKD roots carry a faithful slot; near-total key coverage before wiring it in. |

**Headline correction:** SKD anubandhas encode **gaṇa + morphophonemic operations, NOT pada.**
The cross-walk's "pada" signals (`ka`/`Sa`/`ya`/`na`) were **gaṇa** markers (curādi/tudādi/
divādi/svādi) whose pada was a downstream correlation; **only ṅ/ñ mark pada.** The
hold-for-verification was vindicated. Also confirmed verbatim from the source: the
**"0/bindu = no anubandha"** convention — primary-source footing for "0 ≠ absent content."

### Open question feeding round 9
- SKD slot token **`ma` (72×)** is not among the 46 Dhātudīpikā anubandhas — what does it mark?

---

## Round 9 — 2026-06-04: `ma` resolved (Palsule's Kavikalpadruma)

| # | Question | Decision | Consequence |
|---|---|---|---|
| 20 | What does SKD's `ma` (72×) mark? | **`m`/mit = nici-hrasva** (penultimate shortens before ṇic, Pāṇ 6.4.92), per Palsule's KKD App. III | Added `ma`→op `nici-hrasva` to m4's `_ANU_KEY`. `ma` is an operation-it (no gaṇa/pada), so the CSV is unchanged — the key is now **complete**. |

Per G.B. Palsule (ed. *Kavikalpadruma*, Appendix III, pp. 95–100), `m` is one of the **17
anubandhas Vopadeva keeps with their Pāṇinian significance**. His account independently
**corroborates the whole key**: `k`/`ṇ`/`p` repurposed as gaṇa markers (= our curādi / phaṇādi
(bhvādi) / mucādi (tudādi)); `au`=aniṭ borrowed from the Jainendra Dhātupāṭha (= our `O`→aniṭ).
Palsule counts **43** code-letters vs the front matter's 46 — a tallying difference, not substance.
**The SKD anubandha line is now complete.**
