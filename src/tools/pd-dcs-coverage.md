---
title: PD × DCS corpus coverage
toc: false
---

# What share of the Poona Dictionary's canon does DCS cover?

The **Poona Dictionary** (PD, *An Encyclopaedic Dictionary of Sanskrit on Historical
Principles*) cites its sources by siglum — a de-facto declaration of the Sanskrit literary
canon. The **Digital Corpus of Sanskrit** (DCS) is the largest lemmatised Sanskrit corpus.
This page measures one against the other, for PD's published **a-** volumes. Full write-up:
[PD_DCS_CORPUS_COVERAGE_2026.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md).

```js
const metrics = FileAttachment("../data/pd/pd_dcs_metrics.json").json();
const crosswalk = FileAttachment("../data/pd/pd_dcs_text_crosswalk.tsv").tsv({typed: true});
const residue = FileAttachment("../data/pd/pd_dcs_residue_top.tsv").tsv({typed: true});
```

```js
function tile(label, value, sub) {
  return htl.html`<div style="border:1px solid var(--theme-foreground-faint);border-radius:8px;padding:0.75rem 1rem">
    <div style="font-size:0.8rem;color:var(--theme-foreground-muted)">${label}</div>
    <div style="font-size:1.9rem;font-weight:700;line-height:1.1">${value}</div>
    <div style="font-size:0.8rem;color:var(--theme-foreground-muted)">${sub}</div>
  </div>`;
}
```

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.75rem;margin:1rem 0">
${tile("PD-citation-weighted", metrics.metric_pd_citation_weighted_pct + "%", "of what PD cites is in DCS")}
${tile("Title-level", "~2.4–4.8%", metrics.n_covered_dcs_titles + " of ~" + metrics.n_primary_works_skeleton_estimate + " works")}
${tile("DCS-token-weighted (2026)", metrics.metric_dcs_token_weighted_2026_pct + "%", "of DCS's mass is PD-cited")}
${tile("DCS-token-weighted (2021)", metrics.metric_dcs_token_weighted_2021_pct + "%", "+3.8 pp by 2026")}
</div>

**The two headline numbers diverge on purpose.** DCS holds only a **quarter** of PD's
citation practice (metric 1) yet its **own bulk is 78 % PD-cited** (metric 3): DCS is a deep
sample of the archaic/classical *core* PD leans on, not of PD's encyclopedic *breadth*.

## Where PD's citation mass goes

```js
const massData = [
  {band: "Covered by DCS", occ: metrics.covered_mass, kind: "covered"},
  {band: "Residue (not in DCS)", occ: metrics.residue_mass, kind: "residue"},
  {band: "Secondary scholarship", occ: metrics.secondary_mass, kind: "secondary"},
  {band: "Structural / grammatical", occ: metrics.structural_mass, kind: "structural"}
];
```

```js
Plot.plot({
  marginLeft: 170,
  x: {label: "PD siglum occurrences (a- volumes)", grid: true},
  y: {label: null},
  color: {domain: ["covered","residue","secondary","structural"],
          range: ["#2c7fb8","#d95f0e","#7a7a7a","#bdbdbd"], legend: false},
  marks: [
    Plot.barX(massData, {x: "occ", y: "band", fill: "kind", sort: {y: "-x"}}),
    Plot.text(massData, {x: "occ", y: "band", text: d => d.occ.toLocaleString(),
                         dx: 4, textAnchor: "start"}),
    Plot.ruleX([0])
  ]
})
```

## Top residue — PD works DCS does not hold

The purāṇas, the lexicographic tradition (kośa), classical kāvya, and the grammatical
commentary layer. The single largest item (Padmapurāṇa, 3,506) outweighs all but three
*covered* texts.

```js
Plot.plot({
  marginLeft: 200,
  height: 640,
  x: {label: "PD citations", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(residue, {x: "pd_citations", y: "work", fill: "#d95f0e", sort: {y: "-x"}}),
    Plot.ruleX([0])
  ]
})
```

## Covered DCS texts, by PD citation frequency

```js
Plot.plot({
  marginLeft: 220,
  height: 720,
  x: {label: "PD citations", grid: true},
  y: {label: null},
  marks: [
    Plot.barX(crosswalk, {x: "pd_citations", y: "dcs_title", fill: "#2c7fb8",
                          sort: {y: "-x", limit: 40}}),
    Plot.ruleX([0])
  ]
})
```

## Trust Block

- **Evidence.** PD sigla harvested from
  [pd.txt](https://github.com/drdhaval2785/SanskritSpellCheck/blob/master/external_src/pd/pd.txt)
  (107,630 entries, 398,359 citation occurrences); DCS inventory + token counts from
  [VisualDCS Corpus-Delta 2021–2026](https://github.com/gasyoun/VisualDCS/blob/main/derived-data/Corpus-Delta-2021-2026/per_text_token_delta.csv)
  (276 texts). n and dates are on every artifact.
- **Method.** Anchored on DCS's bounded 276-text set; every siglum carries an adjudicated
  `match_type` (covered / residue / secondary / structural). Scripts:
  [pd_extract_sigla.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_extract_sigla.py),
  [pd_dcs_crosswalk.py](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/pd_dcs_crosswalk.py).
- **Limitations.** PD is published under letter **a-** only (6 of 37+ volumes), so these are
  PD's sources *as exercised under a-*, not its full canon. Siglum→title expansion is
  Opus-adjudicated, not sourced from PD's printed abbreviation list. See the report's §6.
- **Owner repo.** `csl-atlas`. Data:
  [data/pd/](https://github.com/sanskrit-lexicon/csl-atlas/tree/main/data/pd).
- **Download.** [Covered-text crosswalk (TSV)](../data/pd/pd_dcs_text_crosswalk.tsv) ·
  [Top residue (TSV)](../data/pd/pd_dcs_residue_top.tsv) ·
  [Metrics (JSON)](../data/pd/pd_dcs_metrics.json).

## Covered-text crosswalk (data table)

```js
Inputs.table(crosswalk, {
  columns: ["dcs_title","pd_sigla","pd_citations","dcs_tok_2026","dcs_chapters","coverage_grade"],
  header: {dcs_title: "DCS text", pd_sigla: "PD siglum", pd_citations: "PD cites",
           dcs_tok_2026: "DCS tokens (2026)", dcs_chapters: "DCS chapters",
           coverage_grade: "grade"},
  sort: "pd_citations", reverse: true
})
```

## Conclusions — and the dictionary's own clock

The residue matters more because **the dictionary that would define it will not finish for
centuries.** The Poona Dictionary began publishing in **1976**; fifty years later it has issued
~6 bound volumes / 6,056 pages / 104,959 lemmas and reached only **a-** to ~`apaca-` — it has
not finished the *short* vowel `a`, let alone `ā`. At one volume every **8.3 years** against
its ~37-volume plan, **PD completes in roughly 250 years — around 2280.**

<div style="border-left:3px solid var(--theme-foreground-focus);padding:0.5rem 1rem;margin:1rem 0">
At today's printing speed, <b>31 volumes remain ≈ 258 years</b> (range ~117 yr at a 20-volume
scope to ~258 yr at 37). The most telling number is the present: <b>after 50 years, PD is still
inside the letter a.</b>
</div>

**A geometric corpus against an arithmetic dictionary.** DCS grew 4.58 M → 5.69 M tokens in five
years — **+4.45 %/yr, doubling every ~16 years** — while PD spent five decades in one letter.
The two scale by different laws and do not converge: over one 30-year planning horizon DCS grows
~×3.7 (to ~21 M tokens, absorbing most of the purāṇas and kāvya it now lacks), while PD adds ~3–4
volumes and merely finishes `a`. The 75 % residue this page measures is therefore **a moving
front, not a permanent deficit** — DCS's 2021→2026 Vedic surge is what closing it looks like.

```js
Plot.plot({
  height: 150, marginLeft: 96, marginRight: 20,
  x: {label: "year", domain: [1976, 2290], grid: true, tickFormat: "d"},
  y: {label: null, domain: ["DCS tokens", "PD (a–)"], padding: 0.5},
  marks: [
    Plot.barX([{y:"PD (a–)", x1:2026, x2:2284}], {y:"y", x1:"x1", x2:"x2", fill:"#d95f0e", fillOpacity:0.35}),
    Plot.barX([{y:"PD (a–)", x1:1976, x2:2026}], {y:"y", x1:"x1", x2:"x2", fill:"#2c7fb8"}),
    Plot.barX([{y:"DCS tokens", x1:1976, x2:2026}], {y:"y", x1:"x1", x2:"x2", fill:"#2c7fb8", fillOpacity:0.5}),
    Plot.text([{y:"PD (a–)", x:2155, t:"~258 yr remaining → ~2284"}], {y:"y", x:"x", text:"t", fill:"#d95f0e", fontSize:11}),
    Plot.ruleX([2026], {strokeDasharray:"3,3", stroke:"currentColor", strokeOpacity:0.4})
  ]
})
```

### Three yardsticks — AP, PWG, MW

Locate PD's frontier (`apaca-`) inside three *finished* Sanskrit dictionaries and the horizon
sharpens. After 50 years PD has reached only **4–6 % of the alphabetical span** a complete
dictionary covers — yet its coverage of just `a-`…`apaca-` (104,959 lemmas) already holds **as
many entries as the entire Petersburger Wörterbuch**, exceeds all of Apte, and is 54 % of all
Monier-Williams. Per headword PD is **13–23× denser** than any completed dictionary.

```js
const bench = [
  {d:"MW · Monier-Williams", whole:194084, done:7856, dens:13.4},
  {d:"PWG · Petersburg (gr.)", whole:106082, done:4519, dens:23.2},
  {d:"AP · Apte", whole:88867, done:5414, dens:19.4}
];
```

```js
Plot.plot({
  marginLeft: 150, height: 190, x: {label: "headwords / lemmas", grid: true},
  y: {label: null, domain: bench.map(b=>b.d)},
  marks: [
    Plot.barX(bench, {y:"d", x:"whole", fill:"#9e9e9e", fillOpacity:0.35}),
    Plot.ruleX([104959], {stroke:"#d95f0e", strokeWidth:2}),
    Plot.text([{x:104959, y:bench[0].d, t:"PD's a– alone = 104,959"}], {x:"x", y:"y", text:"t", fill:"#d95f0e", dy:-14, textAnchor:"middle", fontSize:11}),
    Plot.text(bench, {y:"d", x:"whole", text:d=>d.whole.toLocaleString(), textAnchor:"start", dx:4, fontSize:10, fill:"currentColor"}),
    Plot.ruleX([0])
  ]
})
```

<div style="font-size:0.85rem;color:var(--theme-foreground-muted);margin:-0.5rem 0 0.5rem">Grey = each finished dictionary's whole-alphabet headword count; the orange line is what PD holds under <b>a-</b> alone. Coverage so far: MW 4.1 %, PWG 4.3 %, Apte 6.1 %.</div>

**Two speeds, by what year does PD finish?** Anchoring scope two ways — the ~37-volume plan vs
holding PD's current density — and the rate at 121 pp/yr (its 50-year average) vs a post-2019
200 pp/yr:

| Completion year | @ 121 pp/yr | @ 200 pp/yr |
|---|---:|---:|
| 37-volume plan (~31k pp left) | **~2284** | **~2182** |
| current density held (~144k pp left) | ~3211 | ~2744 |

Scope moves the finish by ~900 years; a 65 % speed-up buys only ~100–470. Completion stays
centuries out either way — the constraint is PD's density, not its pace.

### Milestones — clearing `a`, the vowels, the halfway mark

Turning the horizon into dates (at current density; both rates carried through):

| Milestone | @ 121 pp/yr | @ 200 pp/yr |
|---|---:|---:|
| End of the short vowel `a` (before `ā`) | **~2094** | ~2067 |
| End of ALL vowels (`a ā i … au`) | **~2179** | ~2119 |
| Mid-dictionary (50 % of headwords, at `p`) | ~2594 | ~2370 |
| Full completion (density held) | ~3211 | ~2744 |

PD will not clear even the *short* vowel `a` until **~2094** — the letter `a` alone is ~118
years of work. The vowel block (one-sixth of the alphabet) is not done until **~2179**; the
alphabetical mid-point sits at `p`, not `k`, because Sanskrit is so front-loaded with prefix
families. *(Vowel milestones are firm; consonant ones are upper bounds — the 37-volume plan
compresses them.)*

### Is `a` the hardest letter?

A good question — is `a` hardest because it holds all the `a-`/`an-` privative compounds
(`a-dharma` "non-dharma", `an-artha` "misfortune"), the negated samāsas buildable from almost
any word? The headword lists answer precisely — and it depends on the dictionary:

```js
const letters = [
  {l:"s", n:25075}, {l:"p", n:21051}, {l:"v", n:18598}, {l:"a", n:18463, hi:true},
  {l:"k", n:12997}, {l:"m", n:11180}, {l:"ś", n:10215}, {l:"n", n:8330},
  {l:"d", n:7793}, {l:"t", n:5421}
];
```

```js
Plot.plot({
  height: 220, marginLeft: 30, x: {label: "initial letter (Monier-Williams)"}, y: {label: "headwords", grid: true},
  marks: [
    Plot.barY(letters, {x:"l", y:"n", fill: d=>d.hi?"#d95f0e":"#2c7fb8", sort:{x:"-y"}}),
    Plot.text(letters, {x:"l", y:"n", text:d=>d.n.toLocaleString(), dy:-6, fontSize:9, fill:"currentColor"}),
    Plot.ruleY([0])
  ]
})
```

In **MW and PWG**, `a` is only the **4th**-largest letter — the sibilant **`s`** wins, then
**`p`** and **`v`**. But in **Apte** (the compound-inclusive practical dictionary) **`a` is #1
at 14.3 %**, exactly because the privative and prefix families (`a-`, `an-`, `ā-`, `adhi-`,
`anu-`…) import a negated or prefixed twin of much of the language under `a`. So the samāsa
intuition is real — but `s`/`p`/`v` carry their own huge prefix families (`sam-`, `pra-`,
`vi-`…) and rival it. **The sting: PD's hardest letters are still ahead** — `s`, `p` and `v`
each hold *more* MW headwords than the `a` that has already cost fifty years.

**And how many `a`-entries are actually compounds? — 83 %.** MW's printed-form list marks every
compound joint with a dash: of the 23,590 `a`/`ā`-entries, **19,601 (83 %) are dash-marked
samāsas**, only ~4,000 simple stems. `a` is overwhelmingly a letter of *combinations*, not roots
— which is the deepest reason a maximalist dictionary drowns in it: it isn't defining ~4,000
words, it's documenting ~20,000 compounds, each with its own attestations.

### The long-dictionary league table

**Same language, done fast.** Seven Sanskrit/Indo-Aryan dictionaries were *completed* in 10–27
years — Böhtlingk's *kürzere Fassung* logged **151,349 lemmas across the whole alphabet in ten
years**. Only the two that chose exhaustive historical detail stall:

| Sanskrit / Indo-Aryan | Span | Years | Lemmas | Status |
|---|---|---:|---:|---|
| WIL · Wilson | 1819–1832 | ~13 | 43,939 | ✓ |
| KOW · Kossowicz (Skt-Rus) | 1854 | — | 13,488 *(Russian-ordered)* | ✗ incomplete |
| **GST · Goldstücker** | 1856–1864 | ~8 | 6,761 | ✗ **abandoned in `a`** |
| PWG · Böhtlingk–Roth (gr.) | 1855–1875 | 20 | 106,083 | ✓ |
| PW · Böhtlingk (kürzere) | 1879–1889 | **10** | 151,349 | ✓ |
| MW · Monier-Williams | 1872–1899 | ~27 | 194,084 | ✓ |
| KEWA · Mayrhofer (etym.) | 1956–1980 | 24 | — | ✓ |
| EWA · Mayrhofer (etym.) | 1986–2001 | 15 | — | ✓ |
| BORI Prakrit Dict. (CDPL) | 1988–ongoing | 38+ | 33,600 *(3 vols, a→`u`)* | ⧗ far from finished |
| **PD · Poona Dictionary** | **1976–~2284⁺** | **~308⁺** | 104,959 *(a-)* | ⧗ **still in `a`** |

**The graveyard of `a`.** Sanskrit is not the problem — exhaustive detail is. The proof is
170 years old: **Goldstücker's 1856 remake of Wilson set out to improve the whole dictionary,
sank into the letter `a`, published 6,761 exhaustive entries, and was abandoned there at his
death** — the one clean death-in-`a`. Two contemporaries are often lumped in but don't belong:
**Kossowicz** (1854, Sanskrit→Russian) reached 13,488 entries but is ordered by the **Russian**,
not Sanskrit, alphabet and left unfinished — a partial work of a different kind, not on the
Sanskrit-letter axis at all; and Böhtlingk–Roth's PWG spent its whole first volume (1855) on `a-`
yet *completed the alphabet*, because it refused to be exhaustive. PD is Goldstücker's project
reborn at ~16× the density (104,959 vs
6,761 for `a`) — the same undertaking, the same letter, the same trap. Why `a` traps the
exhaustive is anatomised in [Letter anatomy](/tools/letter-anatomy): it heads five preverb
families plus the privative, so 83 % of its entries are compounds, not roots.

**The controlled experiment — two dictionaries, one city, one editor.** Across town in the same
Pune, the **Bhandarkar Institute** (BORI) *Comprehensive & Critical Dictionary of the Prakrit
Languages* began in **1988** — twelve years *younger* than PD — and has already reached **`a`
through `ujjhittu`**: all the vowels and into the consonants, ~33,600 lexemes against a bounded
~90,000-entry plan — **still far from finished** (~37 % after 38 years), but *moving through the
alphabet*, which is the point. Its founding editor was **A. M. Ghatage — the very scholar who
edited PD's first volumes.** Same man, same city, same decade; the difference is *scope*. BORI
bounded its corpus and cleared the vowels in 38 years; PD chose the unbounded maximum and in 50
has not left `a`. A great Sanskrit-family dictionary finishes only if it refuses to let `a`
become infinite.

**PD's real peers are the century-long giants** — and it is projected to outlast them all. No
dictionary ever *finished* took more than ~180 years:

| Century-long giants | Language | Span | Years | Status |
|---|---|---|---:|---|
| OED, 1st ed. | English | 1857–1928 | 71 | ✓ |
| CAD · Chicago Assyrian | Akkadian | 1921–2011 | 90 | ✓ |
| Grimm · Deutsches Wb. | German | 1838–1961 | 123 | ✓ (rev. 2016) |
| SAOB · Swedish Academy | Swedish | 1893–2023 | 130 | ✓ |
| WNT · Nederlandsche Taal | Dutch | 1864–1998 | 134 | ✓ |
| TLL · Thes. Linguae Latinae | Latin | 1894–~2050 | ~156 | ⧗ |
| **PD · Poona Dictionary** | **Sanskrit** | **1976–~2284⁺** | **~308⁺** | **⧗ still in `a`** |

Even PD's fastest scenario (2182, 206 yr) exceeds the longest dictionary ever completed; its
density-held scenario is ~9× the Dutch WNT. On present course PD becomes the longest single
lexicographic project in history — a direct consequence of its 13–23× density, not of any lack
of effort.

### The other model — born-digital corpus lexicography

Every dictionary above belongs to one paradigm: the print historical dictionary, composed from
slips and published alphabetically over decades. The sharpest contrast is the paradigm that
*retires* it. **[TamiLex](https://www.tamilex.uni-hamburg.de)** (Universität Hamburg), a digital
lexicography project for **Tamil**, differs from PD in *kind*, not speed:

- **Born-digital, not print-fascicule** — a queryable database is never *stuck* at a letter; the
  death-in-`a` trap is structurally impossible.
- **Whole-language-at-once, not alphabetical** — partial-but-growing coverage everywhere at once,
  not `a` perfected before `b` is touched. PD's centuries-long horizon is an artifact of the
  alphabetical-completion constraint a database doesn't have.
- **Corpus-integrated, not corpus-blind** — lexicon and attestation are one system. For Sanskrit,
  dictionary (PD) and corpus (DCS) are *separate* — this whole study is the after-the-fact weld.
- **Aggregative and open, not from-scratch and print.**

**TamiLex is, for Tamil, essentially what the next section recommends for Sanskrit.** The drastic
difference isn't that it's faster — it's that it *abandons the model whose clock this page has been
measuring*. PD may be the last of the great print historical dictionaries; DCS welded to a lexical
layer is the Sanskrit form of what comes after. *(Exact TamiLex figures pending — the site returned
a transient error at time of writing; the comparison turns on paradigm, not dates.)*

### Who finishes a dictionary — and why

Are Germans simply the best dictionary-makers, and Indians confined to the kośa? The record says
no — it is about **method, institution and scope**, not nation.

- **The real German trait is finishability, not maximalism.** The German/European school dominated
  historical lexicography through its academies and a discipline Mayrhofer put as a rule: *do not
  begin a dictionary you cannot finish.* **PD is not German** — it is a Deccan-College institutional
  project on the *slip-archive* method (slips now merely scanned); its problem is unbounded scope,
  not any imported method.
- **The "entries shrank over time" pattern is European, not Indian.** The [entry-size study](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/LETTER_ANATOMY_AND_ENTRY_SIZE_2026.md)
  found the decay in **PWG (−0.19), PWK (−0.34), Grassmann (−0.20)** (and it runs through KEWA/EWA
  and the big non-Sanskrit dictionaries) — while the two Indian encyclopaedias **SKD and VCP show
  none** (ρ≈0.00). The belief that funding-cut compression was an Indian failing is backwards.
- **The finished dictionaries were near-solo.** **V. S. Apte** (Fergusson College, Pune) compiled
  a complete, still-standard Sanskrit–English dictionary *almost alone* and **died at 34** (1858–92),
  two years after it appeared; Böhtlingk carried the *kürzere Fassung* single-handed. A bounded
  scope + a single vision finishes; a large institution + an unbounded scope (PD) does not.
- **Indians did not do "only kośas."** The kośa is a sophisticated genre, not a ceiling — and
  beyond it Apte, **SKD** and **VCP** are *finished* Indian encyclopaedias. The struggling projects
  are the modern *institutional* ones (BORI far from done; the Madras Tamil Lexicon now remade in
  Hamburg as TamiLex).

**Verdict:** the great dictionaries came from wherever **bounded scope met a discipline of
finishability** — most often the German academy, and the lone scholar who scoped to one lifetime.
PD is stuck because it is *unbounded and institutional*, not because it is Indian; the reef named
`a` sinks the exhaustive of every nation alike.

**What follows.** DCS *attests*; PD *analyses* — a corpus cannot supply PD's historical
sense-development, so for the 97 % of the lexicon PD has not reached it remains the only project
attempting it. But the practical conclusion is unambiguous: **don't wait for the dictionary —
feed the corpus.** The highest-leverage additions to DCS are exactly PD's high-frequency
uncovered works, and PD's own citation frequency (the residue chart above) is a ready-made
digitisation priority list. Full argument: [reports/PD_DCS_CORPUS_COVERAGE_2026.md §8](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/reports/PD_DCS_CORPUS_COVERAGE_2026.md).
