# A72 census v1 — computed grammatical-abbreviation polysemy across the digitized CSDL canon

_Generated: 2026-10-10T19:00:00.879Z · executor GLM-5.3-Flash (zai-coding-plan/glm-5.3-flash) via ZCode · handoff H6409_

_Created: 10-10-2026 · Last updated: 10-10-2026_

Re-founds the hand-collected homograph tables of Gasūns 2006, Latin Terms in Sanskrit Dictionaries (EURALEX XII, Torino, pp. 773–778) as a computed
census. Every number below is emitted by `scripts/build_abbrev_census.py`;
the full payload (inventories, unified label table, collision matrix,
polysemy) lives in [data/abbrev/abbrev_census.json](../data/abbrev/abbrev_census.json).

## Denominators

| Denominator | Value |
|---|---|
| Dictionaries catalogued in the csl-guides legend layer | 44 |
| … with a machine-readable legend (status data) | 18 |
| Corpus dictionaries discovered in `../csl-orig/v02` | 45 |
| … parsed (entries > 0) | 45 |
| Entries scanned | 1506391 |
| `<ab>` labels counted | 1037648 |
| `<lex>` labels counted | 776143 |
| `<lang>` labels counted | 55704 |
| Distinct labels in the unified table | 34765 |
| `<ls>` citations (H1826 registers, reused) | 1517609 |
| `<ls>` layer invariant violations | 0 |

## Corpus label census (a)

| Dict | Entries | `<ab>` | `<lex>` | `<lang>` | `<ls>` | front/back matter |
|---|---|---|---|---|---|---|
| abch | 1965 | 0 | 0 | 0 | 0 | — |
| acc | 49833 | 0 | 0 | 0 | 0 | 45/15088 B |
| acph | 163 | 0 | 0 | 0 | 0 | — |
| acsj | 240 | 0 | 0 | 0 | 0 | — |
| ae | 11359 | 35746 | 22879 | 0 | 1141 | — |
| ap | 90847 | 32859 | 30184 | 1538 | 68273 | — |
| ap90 | 34882 | 46066 | 0 | 0 | 43892 | 49387/0 B |
| armh | 7907 | 0 | 0 | 0 | 0 | — |
| ben | 25062 | 37447 | 31237 | 1243 | 49234 | — |
| bhs | 17839 | 46675 | 15286 | 18934 | 48419 | — |
| bop | 8961 | 0 | 0 | 1479 | 0 | — |
| bor | 24609 | 0 | 0 | 0 | 526 | — |
| bur | 19776 | 65461 | 0 | 670 | 0 | 82/1 B |
| cae | 40069 | 25564 | 44925 | 3 | 0 | 12/1 B |
| ccs | 30010 | 0 | 0 | 0 | 0 | — |
| fri | 8155 | 0 | 0 | 23013 | 0 | — |
| gra | 12785 | 45726 | 0 | 481 | 2341 | — |
| gst | 6780 | 0 | 0 | 14 | 0 | — |
| ieg | 7932 | 4135 | 0 | 0 | 11390 | — |
| inm | 12647 | 0 | 0 | 1 | 0 | — |
| krm | 2061 | 0 | 0 | 0 | 0 | — |
| lan | 4944 | 13216 | 0 | 1012 | 5912 | — |
| lrv | 53440 | 0 | 0 | 0 | 16650 | 0/1 B |
| mci | 2643 | 0 | 0 | 0 | 0 | — |
| md | 20749 | 46956 | 56123 | 102 | 58 | — |
| mw | 286525 | 194879 | 201942 | 3968 | 320828 | — |
| mw72 | 55390 | 0 | 0 | 1738 | 0 | — |
| mwe | 32378 | 0 | 0 | 0 | 0 | — |
| nmmb | 506 | 0 | 0 | 0 | 0 | — |
| nybj | 2479 | 0 | 0 | 0 | 0 | — |
| pe | 8799 | 0 | 0 | 0 | 0 | — |
| pgn | 485 | 0 | 0 | 0 | 0 | — |
| pui | 17512 | 0 | 0 | 0 | 0 | — |
| pw | 170556 | 107807 | 177783 | 265 | 98483 | 82/0 B |
| pwg | 123366 | 180734 | 130864 | 998 | 801788 | — |
| pwkvn | 24976 | 6194 | 11892 | 59 | 17627 | 53/0 B |
| sch | 29125 | 2 | 0 | 5 | 31041 | — |
| shs | 47326 | 0 | 0 | 0 | 0 | 3122/0 B |
| skd | 42531 | 0 | 0 | 0 | 0 | 40/0 B |
| snp | 453 | 0 | 0 | 1 | 0 | — |
| stc | 24574 | 80385 | 0 | 1 | 0 | — |
| vcp | 50135 | 0 | 0 | 0 | 0 | 39/0 B |
| vei | 3834 | 0 | 0 | 150 | 0 | — |
| wil | 44577 | 67796 | 53028 | 28 | 6 | — |
| yat | 45206 | 0 | 0 | 1 | 0 | — |

## Legend layer (front-matter abbreviation lists)

csl-guides catalogs 44 dictionaries: 18 with a machine-readable legend, 1 tokens-only (inventory, no expansions), 25 scanned-image-only or none. The legend rows are reused verbatim; this census does not re-parse prefaces.

## Collision matrix (c) — the 2006 homograph class, computed

448 abbreviation strings are polysemous (≥ 2 distinct expansions after casefold-compare). Top 25 by polysemy:

| Label | Senses | Senses → dictionaries |
|---|---|---|
| `M.` | 11 | MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289). (PWG); Manusmṛiti (in twelve adyāyas, Māndlik’s edition, 1886). (LRV); Marut. (INM); Masculine. (SHS); Matsyôpâkhyâna, i.e. episodium de diluvio. (BOP); Middle. (CAE); … +5 |
| `P.` | 11 | Parasmaipada. (AP, AP90, MD); Parasmai-pada (MW, MW72); 1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockhaus. Lipsiae 1835.) (BOP); 1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae 1835.) (BOP); Participium (GRA); Passive. (CAE); … +5 |
| `N.` | 10 | Name. (AP, AP90, CAE, MW72); NALOPĀKHYĀNA in BÖHTLINGK'S Chrestomathie (GILD. Bibl. 49). Die BOPP'sche Ausgabe (GILD. Bibl. 99) ist durch N. (BOPP) bezeichnet. (PWG); Naiṣadhacarita. (AP90); Nalus (Berol. apud Nicolai). (BOP); Name (also = title or epithet) (MW); Neuter. (SHS); … +4 |
| `A.` | 8 | Active. (CAE, MW); Ātmanepada (AE, AP90); 1) Atmanêpadum. 2) Arg'uni reditus ex Indri coelo. (*) (BOP); 1) Atman�padum. 2) Arg'uni reditus ex Indri coelo. (*) (BOP); Accusativ (GRA); Aśvin. (INM); … +2 |
| `R.` | 7 | Raghuvanśa (in nineteen sargas, Nirṇayasāgara edition, 1886). (LRV); Raghuvaṃśa (Bombay). (AP90); Root. (SHS); Rudra. (INM); RĀMĀYANA. Das 1ste und 2te Kāṇḍa nach der Ausg. von SCHLEGEL, das 3--6te nach der von GORRESIO, das 7te nach der Bomb. Ausg., wenn nicht ausdrücklich eine andere Ausgabe genannt ist. Eine eingeklammerte Zahl bezieht ist sich auf ed. Bomb. (vol. 1) (PW); RĀMĀYAṆA. Ohne eine nähere Angabe ist bei den zwei ersten Büchern die Ausgabe von SCHLEGEL (GILD. Bibl. 84), bei den vier letzten die von GORRESIO (GILD. Bibl. 85) gemeint. (PWG); … +1 |
| `V.` | 7 | Burdwan edition. (INM); Vasu. (INM); Veda, Vedic. (MD); Verb. (SHS); Vikramorvaśīyam (Bombay). (AP90); Vocativ (GRA); … +1 |
| `fig.` | 7 | Figurative (AE, AP); figuratively. (CAE, MW); Figuentative. (AP90); Figurative or figuratively. (LRV); figurative(ly). (BHS); figurative, -ly. (MD); … +1 |
| `C.` | 6 | Calcutta edition. (INM, MW); Causativ (GRA); Causative. (CAE); Chezy. (BEN); Classical (post-Vedic) Sanskrit. (MD); causatif (BUR) |
| `f.` | 6 | Feminine (AE, AP, AP90, CAE…); féminin (BUR, STC); Feminine (of adjectives). (LRV); feminine; also = for. (MD); feminine; following. (BHS); femininum (GRA) |
| `lit.` | 6 | literally. (CAE, MD, MW); Literal. (AP, AP90); Literal or literally. (LRV); Literal, literally (AE); Lithuanian (GRA); literal(ly); also, literary, found in literature, as opposed to lex. (BHS) |
| `n.` | 6 | Neuter (AE, AP, AP90, CAE…); neuter gender (MW); neutre (BUR); neutrum (GRA); nom. (STC); nominative; name. (BHS) |
| `pp.` | 6 | Past passive participle. (LRV); participe passé (BUR); participle. (CAE); past participle (MW); perfect passive participle. (MD); perge, perge‎ (GRA) |
| `D.` | 5 | Dativ (GRA); Denominative (AE); Desiderative. (CAE); Deva. (INM); SĀHITYADARPAṆA, ? [Cologne Addition] (PWG) |
| `H.` | 5 | HEMACANDRA'S ABHIDHĀNACINTĀMAṆI, ein systematisch angeordnetes synonymisches Lexicon. Herausgegeben, übersetzt und mit Anmer- kungen begleitet von OTTO BÖHTLINGK und CHARLES RIEU. St. Peters- burg 1847. (PWG); HEMAK4ANDRA'S ABHIDHĀNAK4INTĀMAṆI, Ausg. von BÖHTLINGK und RIEU. (vol. 1) (PW); Hidimbi caedes. (**) (BOP); Himmel (GRA); Hitopadeśa (Nirṇaya Sāgara Edition). (AP90) |
| `K.` | 5 | Karañja (GRA); Kinnara. (INM); Kâs'inâthus, grammaticus indicus, cujus radicum collectionem edidit Wilkinsius (The radicals of the Sanscrita Language, London 1815). (****) (BOP); Kādambarī (Bombay). (AP90); king. (MD) |
| `Pr.` | 5 | proper (MW, MW72); Priyamedha (GRA); Prākrit (Sanskrit equivalent of Prākrit word), Prākritic. (MD); prologue. (BEN); présent (BUR) |
| `S.` | 5 | Siehe (GRA); Simple. (CAE); Sādhya. (INM); Sūtra. (MD); substantif (BUR) |
| `U.` | 5 | Ubhayapada (Parasmai and Atmane). (AP); Ubhayapada (Parasmai. and Ātmane.) (AP90); Upaniṣad. (MD); Uraga. (INM); Uttararāmacarita. (AP90) |
| `act.` | 5 | actif (BUR); actif (voix active). (STC); activ (GRA); active. (MD); active; action. (BHS) |
| `comp.` | 5 | Compound (AE, AP90, BEN, MW); comparatif (BUR); comparative. (CAE); composition. (BHS); composé, composition (ne s'emploie que dans un composé). (STC) |
| `conj.` | 5 | conjonction (BUR, STC); Conjunction (AE); conjectural (MW); conjecture. (MD); conjunctive. (CAE) |
| `m.` | 5 | Masculine (AE, AP, AP90, BHS…); masculin (BUR, STC); masculine gender (MW); masculinum (GRA); meaning. (CAE) |
| `opp.` | 5 | Opposite of (AE, AP, AP90); opposed. (CAE, MW); opposite (of). (BHS); opposite. (MD); opposé (BUR) |
| `p.` | 5 | page and participle (cf. p.p.) (MW); page. (MW72); parfait (BUR); plural (GRA); possessive, v. pref. (CAE) |
| `pers.` | 5 | person. (BHS, MW, MW72); Persian. (AP90); person & th(ing). (CAE); person or personal. (CAE); personne (BUR) |

### The 2006 target strings

Each 2006 hand row reappears in the computed table: vocative/Vedic/Vikramorvaśīyam for `V.`, causal/case for `c.`, Name/neuter/Naiṣadhacarita for `N.`, Manu/Masculine for `M.`, Sūtra/siehe/substantive for `S.`, and for `f.` the MD sense «also = for» — 2006's «f. … and for (Mc)» computed. The bare single-letter rows (`m`, `s`) stay absent: their 2006 witnesses (Ln, Mc, Ko, Wb) sit outside the digitized legend set, which the denominator states honestly.

| 2006 hand row | Computed v1 (legend layer) |
|---|---|
| `V.` | Burdwan edition. (INM); Vasu. (INM); Veda, Vedic. (MD); Verb. (SHS); Vikramorvaśīyam (Bombay). (AP90); Vocativ (GRA); … +1 |
| `c.` | case (MW, MW72); Causal (AE); causatif (BUR); causativ (GRA) |
| `P.` | Parasmaipada. (AP, AP90, MD); Parasmai-pada (MW, MW72); 1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockhaus. Lipsiae 1835.) (BOP); 1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae 1835.) (BOP); Participium (GRA); Passive. (CAE); … +5 |
| `S.` | Siehe (GRA); Simple. (CAE); Sādhya. (INM); Sūtra. (MD); substantif (BUR) |
| `N.` | Name. (AP, AP90, CAE, MW72); NALOPĀKHYĀNA in BÖHTLINGK'S Chrestomathie (GILD. Bibl. 49). Die BOPP'sche Ausgabe (GILD. Bibl. 99) ist durch N. (BOPP) bezeichnet. (PWG); Naiṣadhacarita. (AP90); Nalus (Berol. apud Nicolai). (BOP); Name (also = title or epithet) (MW); Neuter. (SHS); … +4 |
| `M.` | MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS (GILD. Bibl. 289). (PWG); Manusmṛiti (in twelve adyāyas, Māndlik’s edition, 1886). (LRV); Marut. (INM); Masculine. (SHS); Matsyôpâkhyâna, i.e. episodium de diluvio. (BOP); Middle. (CAE); … +5 |
| `m` | not polysemous in the digitized legends |
| `s` | not polysemous in the digitized legends |
| `f.` | Feminine (AE, AP, AP90, CAE…); féminin (BUR, STC); Feminine (of adjectives). (LRV); feminine; also = for. (MD); feminine; following. (BHS); femininum (GRA) |

Petersburg-Wörterbuch sigla (one work, competing abbreviations — the 2006 synonymy note, computed as known sigla or expansions naming the Wörterbuch itself; publication-place mentions of St. Petersburg do not qualify):

| Siglum | Expansion (first legend row) | Dict |
|---|---|---|
| `B. R.` | Böhtlingk and Roth. | MW72 |
| `BR` | Boehtlingk and Roth, Sanskrit Wörterbuch. | BHS |
| `pw` | Boehtlingk, Sanskrit Wörterbuch in kürzerer Fassung. | BHS |

## Polysemy distribution (d)

4752 abbreviation strings carry at least one legend expansion; 448 of them (9.4%) are polysemous. In-corpus-only strings (no legend row) carry usage mass in the label table but no computed senses, so they stay out of this distribution.

| Distinct expansions per abbreviation | Label count |
|---|---|
| 1 | 4304 |
| 2 | 325 |
| 3 | 71 |
| 4 | 26 |
| 5 | 14 |
| 6 | 5 |
| 7 | 3 |
| 8 | 1 |
| 10 | 1 |
| 11 | 2 |

## Method, reuse, limits

* Corpus read via `parse_cslorig.iter_entries` (H1826 line); roster via `citation_register_gaps.discover_dicts` — the same glob as the sibling register artifacts.
* The `<ls>` source-siglum layer is NOT recomputed: it is the committed [data/obs/ls_abbreviation_frequency.json](../data/obs/ls_abbreviation_frequency.json) artifact (H1826, csl-observatory#222); this build re-runs its sum-equals-register invariant and reports violations, zero expected.
* Legends are the csl-guides per-dictionary abbreviation dataset (commit below), parsed by csl-guides from the org's canonical legend files; classification grammatical/works is carried per row.
* Comparisons are on RAW strings (case-sensitive, trailing punctuation kept) — the H1076 lesson: case folding misreads hedged sigla. Expansion equality is casefold+NFC+trailing-period-insensitive (`expansion_key`).
* Different layers, NOT rebuilt here: entry microstructure (`csl_pyutil.anatomy`), per-dictionary structure (H5325 megastructure catalogue), dictionary-genre taxonomy (H5335 lexicographic-types register). E3 (the 2006 «small classes» normative scheme) is a separate item — this census measures only.
* Limits: 26 of 44 catalogued dictionaries have no machine-readable legend, so the collision matrix is a lower bound; inline `<ab>`/`<lex>`/`<lang>` conventions differ per digitization (PW's `<ab>` carries German+Latin, MW's English); the `<ls>` layer is inventoried but its senses are not disambiguated here. BOP's legend source carries mojibake, so encoding-variant rows can inflate BOP's sense counts (visible on `P.`/`A.`) — kept raw rather than silently folded.

## Prior art read before the label-table format (github-first)

* TEI Lex-0 official repo [DARIAH-ERIC/lexicalresources](https://github.com/DARIAH-ERIC/lexicalresources) (`Schemas/TEILex0/TEILex0.odd` + parts): grammatical info lives in `gramGrp`/`gram`, usage labels in `usg` with a typed vocabulary (geographic/time/domain/…); Lex-0 keeps label *values* open, so a controlled label register is exactly the gap E3 fills. Estate precedent: csl-standards pins Lex-0 0.9.5 (A70).
* SKOS: no normative GitHub repo exists (w3c/skos 404s) — official surface is the [W3C SKOS Reference](https://www.w3.org/TR/skos-reference/); the E3 register maps naturally to skos:Concept with prefLabel (expansion) / notation (abbreviation).
* User repos consulted: BCDH/tei-lex-0 (workshop spec mirror), pdl-lex/pdl-import-postgres (Lex-0 consumer).

## Provenance

* corpus: `../csl-orig/v02`
* legends: /Users/mac/Documents/GitHub/csl-guides/src/data/abbreviations.json @ `cd79a7b0e1b09541dacd937aca9c9a10d6e95677`
* model: GLM-5.3-Flash (zai-coding-plan/glm-5.3-flash) via ZCode; handoff H6409; license CC-BY-SA-4.0

_Dr. Mārcis Gasūns_
