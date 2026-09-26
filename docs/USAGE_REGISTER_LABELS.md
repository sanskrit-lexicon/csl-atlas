_Created: 23-09-2026 · Last updated: 23-09-2026_

# Usage and register labels — a comparative census across the CDSL dictionaries

The **lexicographers-only** label (`<ls>L.</ls>`) had only ever been studied for
MW alone. This page generalises the measurement: every CDSL dictionary states a
word's **usage or register** in a small, dictionary-specific set of markup
labels, and once those labels are normalised onto one closed vocabulary they can
be compared across dictionaries.

The generated data is
[`src/data/lexico/usage_register_census.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/lexico/usage_register_census.json)
(with its [`…​.source.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/src/data/lexico/usage_register_census.source.json)
envelope). The normalisation map — the load-bearing artefact — is
[`data/lexico/usage_register_mapping.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/usage_register_mapping.json).
Rebuild with `npm run build-usage-register-census`, check with
`npm run validate-usage-register-census`, test with
`node --test test/usage-register-census.test.mjs`.

## Method

A dictionary marks usage and register in three tags:

1. **`<lang>`** — the register tag proper. MW writes `<lang>Ved.</lang>`,
   `<lang>ep.</lang>`, `<lang>Class.</lang>`; PWG writes `<lang>ved.</lang>`,
   `<lang>ep.</lang>`, `<lang>klass.</lang>`, `<lang>nachved.</lang>`; the BHS
   dictionary uses it for the Middle-Indic varieties.
2. **`<ab>`** — abbreviation, mostly grammar and editorial (`acc.`, `cf.`,
   `q.v.`), but it also carries the register labels `fig.`, `lit.`, `poet.`,
   `myth.`, `Buddh.`, `vulg.`, `onomat.` and their German counterparts.
3. **`<ls>`** — the citation source. In MW the single source `L.` is the
   lexicographers-only hedge: the word is attested only in the lexica, never in
   a text.

The census is an **exact `(tag, token)` match** against the published map, not a
token match. This is deliberate and it is the whole correctness story — the same
token means different things in different tags and dictionaries:

| look-alike | what it actually is | never counted as |
|---|---|---|
| `<ab>lit.` | English *literally* (MW 217, CAE 848, BHS 387 …) | literary |
| `<ab>Lit.` | *literally* in AE/BHS | literary |
| `<lang>Lit.` / `<lang>lit.` | *Lithuanian* / *litauisch* etymon language | literary |
| `<ab>ep.` | *epithet* (MD 801, BHS 257) | epic |
| `<ab>L.` | *Latin* (AP90 69) or a cross-reference near `cf.` | lexicographer-only |
| `<lang>L.` | *Latin* etymon (AP 69) | lexicographer-only |
| `<ab>l.` | *line* (BHS, BEN), French *lieu* (BUR) | lexicographer-only |
| `<ab>obs.` | *obsolete* (grammatical form), MW | archaic |

These are published under `excluded` in the mapping and are asserted absent by
the validator and the tests. The `<lang>` tag also carries the etymon languages
(`Gk.`, `Lat.`, `Germ.`, `Goth.`, `Eng.`, …) and the `<ab>` tag carries the
grammar/editorial abbreviations; neither is a usage label and neither is counted.

A **label instance** is one markup occurrence. An **entry** is one `<L>…<LEND>`
record. The reported **rate** is instances per 1,000 entries; a record is
credited to a category when at least one of its labels maps to that category.

## Normalised vocabulary

Class **register** (usage / stylistic register):

| category | source labels |
|---|---|
| lexicographer-only | `ls:L.` |
| vedic | `lang:Ved.`, `lang:ved.`, `lang:Vedic`, `ab:Ved.`, `ab:ved.` |
| post-vedic | `lang:nachved.`, `lang:late Skt.` |
| epic | `lang:ep.` |
| classical | `lang:Class.`, `lang:classical Sanskṛt`, `lang:klass.`, `lang:Class. Skt.`, `ab:class.` |
| poetic | `ab:poet.` |
| mythological | `ab:myth.`, `ab:Myth.`, `ab:mythol.`, `ab:Mythol.` |
| buddhist | `ab:Buddh.`, `ab:buddh.`, `ab:buddhist.` |
| jaina | `ab:Jaina`, `ab:Jaina.` |
| figurative | `ab:fig.`, `ab:Fig.`, `ab:figurat.`, `ab:Figurat.`, `ab:figur.`, `ab:bildl.`, `ab:Bildl.`, `ab:uneig.`, `ab:Uneig.` |
| metaphorical | `ab:metaph.`, `ab:übertr.` |
| colloquial | `ab:coll.`, `ab:Coll.`, `ab:colloq.`, `ab:gespr.` |
| vulgar | `ab:vulg.`, `ab:Vulg.`, `ab:niedrig.` |
| archaic | `ab:arch.` |
| onomatopoeic | `ab:onom.`, `ab:onomat.`, `ab:onomatop.`, `ab:Onomat.`, `ab:Onomatop.` |

Class **dialect** (language variety): `pali` (`lang:Pāli`/`Pali`), `prakrit`
(`lang:Prākṛt`/`Prākṛ.`/`Prākrit`/`Pr.`/`Pkt.`), `apabhramsa`
(`lang:Apabhraṃśa`/`Ap.`), `desi` (`lang:Deśī`), `ardhamagadhi` (`lang:AMg.`),
`mixed-indic` (`lang:MIndic`), `jaina-maharashtri` (`lang:JM.`), `maharashtri`
(`lang:M.`), `marathi` (`lang:Mar.`/`Marāṭhī`/`mahr.`/`mahratt.`), `hindi`
(`lang:Hindi`/`Hindī`/`Hind.`), `bengali` (`lang:beng.`/`bengal.`/`Beng.`).

Class **domain** (subject-field labels used as usage statements):
`philosophical` (`ab:philos.`), `religious` (`ab:relig.`), `astronomical`
(`ab:astronom.`), `political` (`ab:polit.`).

Class **lexicographic**: `lexicographer-only` (`ls:L.`).

## Results

45 dictionaries scanned, 1,506,391 entries, 62,812 label instances —
41.7 instances per 1,000 entries, 3.86 % of entries carrying at least one
mapped label. 16 dictionaries carry a mapped label; the other 29 do not mark
register in markup.

| dict | entries | instances | entries w/ label | per 1,000 entries | leading categories |
|---|---|---|---|---|---|
| `mw` | 286,525 | 41,929 | 41,369 | 146.34 | lexicographer-only 40,212 · vedic 612 · epic 328 · figurative 245 |
| `ap` | 90,847 | 3,626 | 3,510 | 39.91 | vedic 1,915 · marathi 1,277 · figurative 416 |
| `ap90` | 34,882 | 2,258 | 2,058 | 64.73 | vedic 1,893 · figurative 365 |
| `pwg` | 123,366 | 1,909 | 1,557 | 15.47 | vedic 543 · metaphorical 341 · vulgar 243 |
| `pw` | 170,556 | 1,396 | 1,343 | 8.19 | buddhist 793 · metaphorical 247 · prakrit 161 |
| `bhs` | 17,839 | 9,106 | 5,917 | 510.45 | pali 7,162 · ardhamagadhi 703 · mixed-indic 553 |
| `bur` | 19,776 | 776 | 688 | 39.24 | figurative 776 |
| `stc` | 24,574 | 522 | 491 | 21.24 | figurative 421 · onomatopoeic 40 · philosophical 38 |
| `ben` | 25,062 | 469 | 402 | 18.71 | vedic 431 · figurative 27 |
| `cae` | 40,069 | 187 | 181 | 4.67 | figurative 187 |
| `md` | 20,749 | 275 | 247 | 13.25 | figurative 165 · prakrit 76 · colloquial 27 |
| `ae` | 11,359 | 158 | 153 | 13.91 | figurative 158 |
| `pwkvn` | 24,976 | 91 | 91 | 3.64 | prakrit 33 · buddhist 24 · pali 20 |
| `lan` | 4,944 | 70 | 65 | 14.16 | figurative 60 · colloquial 10 |
| `wil` | 44,577 | 24 | 24 | 0.54 | figurative 15 · vulgar 7 |
| `gra` | 12,785 | 16 | 9 | 1.25 | figurative 16 |

Whole-dictionary totals:

| category | class | instances | entries | share |
|---|---|---|---|---|
| lexicographer-only | lexicographic | 40,212 | 39,962 | 64.0 % |
| pali | dialect | 7,246 | 5,166 | 11.5 % |
| vedic | register | 5,534 | 5,076 | 8.8 % |
| figurative | register | 3,116 | 2,898 | 5.0 % |
| marathi | dialect | 1,295 | 1,244 | 2.1 % |
| buddhist | register | 1,077 | 1,069 | 1.7 % |
| prakrit | dialect | 797 | 771 | 1.3 % |
| ardhamagadhi | dialect | 703 | 661 | 1.1 % |
| metaphorical | register | 600 | 553 | 1.0 % |
| mixed-indic | dialect | 553 | 533 | 0.9 % |
| epic | register | 427 | 365 | 0.7 % |
| onomatopoeic | register | 355 | 354 | 0.6 % |
| vulgar | register | 250 | 236 | 0.4 % |
| classical | register | 154 | 132 | 0.2 % |
| colloquial | register | 97 | 96 | 0.2 % |
| philosophical | domain | 88 | 88 | 0.1 % |
| hindi | dialect | 55 | 53 | 0.1 % |
| post-vedic | register | 55 | 53 | 0.1 % |
| jaina-maharashtri | dialect | 41 | 40 | 0.1 % |
| maharashtri | dialect | 37 | 37 | 0.1 % |
| bengali | dialect | 32 | 29 | 0.1 % |
| apabhramsa | dialect | 23 | 23 | <0.1 % |
| mythological | register | 21 | 21 | <0.1 % |
| desi | dialect | 16 | 16 | <0.1 % |
| jaina | register | 14 | 14 | <0.1 % |
| poetic | register | 6 | 6 | <0.1 % |
| religious | domain | 4 | 4 | <0.1 % |
| astronomical | domain | 2 | 2 | <0.1 % |
| archaic | register | 1 | 1 | <0.1 % |
| political | domain | 1 | 1 | <0.1 % |

## What the census shows

1. **MW is the outlier, and the hedge is why.** 64 % of all label instances in
   the whole estate are MW's `<ls>L.</ls>` lexicographer-only hedge (40,212) —
   more than all other dictionaries' labels combined. Strip the hedge and MW's
   register marking (1,717 instances, 6.0 per 1,000 entries) is among the
   lightest of the narrative dictionaries.
2. **Four labelling cultures.** The German PW/PWG pair marks *metaphor*
   (`übertr.`, 588) and *vulgarity* (`vulg.`/`niedrig.`, 243); the English
   MW/AP/WIL/BEN/CAE use *figurative* (`fig.`) as the workhorse; the BHS
   dictionary is a dialect-label machine (510 per 1,000 entries, 84 % of its
   labels Pāli / Ardhamāgadhī / mixed-Indic); the indigenous SKD and VCP mark
   none in markup at all.
3. **`epic` is one tag, not a habit.** `<lang>ep.</lang>` is the only epic
   label, found in MW (328), PWG (97) and PW (2). The `<ab>ep.</ab>` token —
   801 in MD alone — is *epithet*, and counting it would have inflated epic by
   84 %.
4. **`lit.` had to be thrown out.** The largest apparent "literary register"
   signal in the corpus (CAE 848, BHS 387, MW 217) is the English translation
   hedge *literally*. The census reports zero literary labels, because none
   exist in the markup.
5. **The lexicographers-only label is indeed MW-only.** AP's, AP90's, GRA's and
   BUR's `L.`/`l.` resolve to *Latin*, *line* and French *lieu* — the hedge has
   no second home.

## Caveats

- **Zero is not absence.** A dictionary with no mapped label may mark register
  in prose (the indigenous SKD/VCP), or not at all; the reverse dictionaries
  simply do not carry the tags. The 29 zero-label dictionaries are listed under
  `diagnostics`.
- **Scanning is line-scoped.** A label whose token is split across lines would
  be missed; the CDSL markup never does this.
- **`<lang>` is overloaded by design.** The same tag carries the etymon
  languages; only the (tag, token) pairs in the map are register labels, and the
  etymon languages are excluded, not silently dropped.
- **The BHS dialect labels are usage-of-the-form, not usage-of-the-sense**, in
  the way the German register labels are; the class column keeps the two apart.
- The upstream revision is pinned in the `.source.json` envelope
  (`upstreamCommit`); rebuild after any csl-orig change.

_Гасунс_