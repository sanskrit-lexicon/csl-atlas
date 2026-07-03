# A06 (P6 Order Is the Dictionary) — Hostile Pre-Submission Review

_Created: 03-07-2026 · Last updated: 03-07-2026_

**Paper:** [docs/articles/paper_kosha_macrostructure.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md)
**Reviewer:** Fable 5 (`claude-fable-5`), adversarial referee pass per H114 (Fable window S12), in the A01/A03 mold.
**Verdict: MINOR REVISION** — every count re-verified exact against the committed artifact; the manuscript is argumentatively strong and honest about its own instrument, but the reference apparatus was a `[TODO]`, and one framing fact has gone stale (CDSL gained a fifth kośa in 2026-06). All agent-doable findings applied in this pass.

---

## 1. Figure re-verification — all counts CONFIRMED

Independently re-derived from [`data/lexico/kosha_macrostructure.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosha_macrostructure.json):

- ARMH: 7,907 records / 860 verse-locators / 5 kāṇḍas; per-kāṇḍa 1,462 / 3,959 / 597 / 958 / 931 (sums to 7,907); mean 9.19 ("9.2"), median 8, synonymic k1–4 mean 9.18; heaven 10.59 ("10.6"), earth 8.59 ("8.6"), kāṇḍa-5 9.31 ("9.3"); largest sets 56 (Viṣṇu, `vn 1.1.1.21`) / 47 (Sun) / 45 (Śiva); kāṇḍa openers `svar` / `BU` / `vaqavAmuKa` confirm the heaven→earth→nether reading — all exact.
- ABCH: 1,965 records / 4,619 lexemes; per-kāṇḍa 41 / 271 / 811 / 602 / 6 / 203 + avyaya 31 (sums to 1,965); gender apparatus 13,284 tags; puM 7,015 / klī 3,110 / strī 2,524 / puṃklī 385 / puṃstrī 122 — all exact.
- ACPH 163/383 and ACSJ 240/491, both with the parent's six-kāṇḍa order intact per `kanda_order` — exact (the supplements spell the fifth book `nāraka-` vs ABCH `naraka-`, an orthographic variant with no bearing on the inheritance claim).

## 2. Major findings

**M1 — The reference apparatus was a TODO.** *Secondary* ended in "[TODO: author to insert specific citations]", Vogel/Wiegand/Svensén were name-drops without bibliographic data, and the body had zero in-text citations — for IJL this is a desk-reject regardless of the analysis quality. *Fix (applied):* full references supplied for Vogel 1979 (the standard genre history), Zgusta 1971, Svensén 2009, and Hausmann & Wiegand 1989 (the macro-/microstructure survey the paper's central term comes from), each wired into the text at its natural anchor (§1 semasiological/onomasiological; §2.1 genre; §5 macrostructure-as-lexicographic-act). The Fort-William/Wilson descent claim (§2.1, §5) is now flagged `[author to verify: Wilson 1819 preface]` rather than standing bare — it is load-bearing for the "bridge to the lineage" argument and needs a page-level source only the author can confirm.

**M2 — "The CDSL holds four koshas" is stale.** csl-orig gained a **fifth** synonymic kośa in 2026-06 — NMMB, Bhoja's *Nāmamālikā* (grouped `<syns>` model *without* the `<s>` wrapper; 2,265 lexemes, 521 unique — the format-blindness that [PR #192](https://github.com/sanskrit-lexicon/csl-atlas/pull/192) fixed in the corpus collapse pipeline, where NMMB was previously counted as 0). A referee cross-checking the corpus would find the paper's own repository contradicting its framing sentence. *Fix (applied):* §2.1 and Table 1 now state the 2026-06 snapshot scope and register NMMB as newly digitized, out of scope for this analysis and queued for the next revision — which also strengthens §4.3: NMMB is a *third* digitization variant of the same genre.

**M3 — Anti-salami: no pointer to P1, and §4.3's hazard is already solved in the atlas's own metric.** The incommensurable-counts warning (§4.3) reads as if corpus statistics over koshas were an open hazard — but P1 §3.2 / OBS-R's collapse metric already normalises kośa records to `<syns>` lexemes, i.e. practices exactly what §4.3 preaches. Not saying so invites "the authors' own companion paper ignores this warning" — the opposite of the truth. *Fix (applied):* §4.3/§5 now cross-cite P1 §3.2 as the implementation of the recommended normalisation; P1 and P4 added to a proper companion-papers block.

## 3. Minor findings

**m1 — Relative links** in the preamble and §3 (`../../data/…`) die outside the repo blob view. *Fix (applied):* full blob URLs.

**m2 — Gender-total transparency.** §4.4's 13,284 total is correct, but the five tags it enumerates sum to 13,156; the remainder sits in rarer combinations (`puṃdvi` 39, `strīklī` 29, `puṃba` 21, …). *Fix (applied):* "with rarer combinations making up the remainder of the 13,284" so a checking referee doesn't stall on the arithmetic.

**m3 — Table 1 lists ACSJ author as "Jinadeva (attr.)"** — kept, but now consistent with the References' "(attr.)" hedge.

## 4. Fixes applied in this pass

All M/m findings above, same branch/PR as this review. Remaining gates are **author-only**: byline; venue; the Wilson-1819 verification (M1); and the (already-acknowledged) absence of the Amarakośa itself from CDSL.

## 5. Checked and sound (no action)

- The zero-meaning argument is the series' strongest instance and correctly scoped; §4.2's honest reclassification of kāṇḍa 5 (homonymic, lexeme-density not synonym-density) is exactly what a hostile referee would otherwise write.
- The Jain-signature reading (Arhats above gods; mass in the human world, 811/1,965; hell at 6) is fully supported by the committed per-kāṇḍa counts.
- The incommensurability argument (§4.3) is sound and important — now properly wired to the series (M3).

_Dr. Mārcis Gasūns_
