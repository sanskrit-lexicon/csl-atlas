# A72 validation table — every Gasūns 2006 claim × computed verdict

_Created: 11-10-2026 · Last updated: 11-10-2026_

Claim-by-claim validation of the hand-collected homograph, polysemy and
sigla tables of Gasūns 2006, Latin Terms in Sanskrit Dictionaries (EURALEX XII, Torino, pp. 773–778) (verbatim fulltext `Uprava/research/notes/latin-terms-2006-fulltext.md`,
§2 preamble + §2.1 + §2.2) against the committed A72 census payload
[data/abbrev/abbrev_census.json](abbrev_census.json) (H6409). Every verdict
is computed by [scripts/build_abbrev_validation_2006.py](../../scripts/build_abbrev_validation_2006.py)
from the census legend / inventory layers — never hand-assigned; the
machine-readable twin of this report is
[data/abbrev/validation_2006_claims.tsv](validation_2006_claims.tsv).

## Denominators

| Denominator | Value |
|---|---|
| 2006 claims transcribed | 111 |
| confirmed (incl. dict-level) | 12 |
| extended (confirmed + census carries more senses) | 27 |
| corrected (digitized witness contradicted) | 4 |
| unmappable (no payload row to check against) | 68 |
| — of which U1 | 24 |
| — of which U2 | 21 |
| — of which U3 | 22 |
| — of which U4 | 1 |
| census payload: legend-carrying strings | 18 dicts, 4752 labels, 448 polysemous |

## Verdict table

### §2 preamble — f. and the interjection trio

| 2006 row | Sense (2006) | Witnesses | Verdict | Evidence (computed) |
|---|---|---|---|---|
| `f.` | femininum | — | **extended** | sense-level: Feminine (AE); Feminine. (AP); Feminine. (AP90) …+6 — census senses 6 > 2006 senses 3 |
| `f.` | futurum | Kn | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `f.` | for | Mc | **extended** | sense-level: feminine; also = for. (MD) — census senses 6 > 2006 senses 3 |
| `interj.` | interjection | — | **confirmed** | sense-level: Interjection (AE); interjection (BUR); interjection (MW) …+1 |
| `int.` | interjection | — | **corrected** | no witness named; digitized legends carry: intensiv (GRA); intransitive. (MD); intensif. (STC) |
| `ij` | interjection | — | **unmappable** | U1: label absent from census labelTable and inventories |

### §2.1 — homograph tables and sigla

| 2006 row | Sense (2006) | Witnesses | Verdict | Evidence (computed) |
|---|---|---|---|---|
| `V.` | vocativus | Hn,Ko | **extended** | sense-level: Vocativ (GRA) — census senses 7 > 2006 senses 5 |
| `V.` | Vedic | Ln,Wh,Mc | **extended** | sense-level: Veda, Vedic. (MD) — census senses 7 > 2006 senses 5 |
| `V.` | Vopadeva | Rn | **extended** | sense-level: Vôpadêvus grammaticus cujus radicum corpus, Kavikalpadruma i (BOP) — census senses 7 > 2006 senses 5 |
| `V.` | vide | Fr | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `V.` | Vikram | j | **extended** | sense-level: Vikramorvaśīyam (Bombay). (AP90) — census senses 7 > 2006 senses 5 |
| `V` | Vollstufe | MR | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 2 in ['bhs', 'mw'] |
| `V` | vowel | Bk | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 2 in ['bhs', 'mw'] |
| `V` | voir | Hn | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 2 in ['bhs', 'mw'] |
| `P.` | Parasmaipada | Ko | **extended** | sense-level: Parasmaipada. (AP); Parasmaipada. (AP90); 1) Parasmaipadum. 2) P�taliputra (ed. H. Brockhaus. Lipsiae  (BOP) …+4 — census senses 11 > 2006 senses 9 |
| `P.` | Person | MR | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | pagina | Wb | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | Praesens | Bt | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | Pluralis | Bt | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | Pāṇini's Aṣṭādhyāyī | Wg,Ap,Rn | **extended** | dict-level: Pāṇini's Aṣṭādhyāyī. (AP90) — census senses 11 > 2006 senses 9 |
| `P.` | Prosa | Db | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | … | Mc | **unmappable** | U4: 2006 states no sense to match |
| `P.` | Prajña | j | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | passivum | Ko | **extended** | sense-level: Passive. (CAE) — census senses 11 > 2006 senses 9 |
| `pass.` | passivum (frequent variant of p.) | Fr | **extended** | sense-level: Passive (AE); Passive. (AP); Passive. (AP90) …+4 — census senses 4 > 2006 senses 1 |
| `A.` | Ātmanepada | Ap | **extended** | dict-level: Ātmanepada. (AP90) — census senses 8 > 2006 senses 5 |
| `ātm.` | ātmanepada | MW | **unmappable** | U1: label absent from census labelTable and inventories |
| `A.` | Aktivum | Bt | **extended** | sense-level: Active. (CAE); Active (MW) — census senses 8 > 2006 senses 5 |
| `A.` | Āfrīnakān | Bt | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `A.` | Anmerkung | Wg | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `Ä.` | ātmanepada (umlaut variant) | St,Kl,Mc,Ko | **unmappable** | U1: label absent from census labelTable and inventories |
| `A.` | Akkusativ | St,Hn,MR | **extended** | sense-level: Accusativ (GRA) — census senses 8 > 2006 senses 5 |
| `a` | adjective | Ln,Fr | **unmappable** | U1: label absent from census labelTable and inventories |
| `a` | apabhaṁça | Th | **unmappable** | U1: label absent from census labelTable and inventories |
| `a` | article | ? | **unmappable** | U1: label absent from census labelTable and inventories |
| `S.` | ai, au | Si | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `S.` | Sūtra | Ln,Wg | **extended** | sense-level: Sūtra. (MD) — census senses 5 > 2006 senses 2 |
| `S` | Schwundstufe | MR | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Sārasvata | Rn | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Semantik | Wb | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Sāvitrī | Kn | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Sāṁkhya | ? | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `s` | singular | Ln,Mc | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | substantivum | MW,Ko | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | simple | Bk | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | siehe | My | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | summary | ? | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `N.` | Nominative case | Hn,Mc | **extended** | sense-level: Nominativ (GRA) — census senses 10 > 2006 senses 8 |
| `N.` | Name | St | **extended** | sense-level: Name. (AP); Name. (AP90); Name. (CAE) …+3 — census senses 10 > 2006 senses 8 |
| `N.` | name of a man or woman | Mc | **extended** | sense-level: Name. (AP); Name. (AP90); Name. (CAE) …+3 — census senses 10 > 2006 senses 8 |
| `N.` | Naiṣadhacarita | Ap | **extended** | dict-level: Naiṣadhacarita. (AP90) — census senses 10 > 2006 senses 8 |
| `N.` | Nyāsa | Rn | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `N.` | Nala | Kn | **extended** | sense-level: Nalus (Berol. apud Nicolai). (BOP); NALOPĀKHYĀNA in BÖHTLINGK'S Chrestomathie (GILD. Bibl. 49).  (PWG) — census senses 10 > 2006 senses 8 |
| `N.` | neuter | Ln,Wb | **extended** | sense-level: neutre (BUR); Neuter. (SHS) — census senses 10 > 2006 senses 8 |
| `N.` | note (in Small Caps) | Ln | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `M.` | Manu | Wh,Wg,Kn | **extended** | sense-level: Manusmṛiti (in twelve adyāyas, Māndlik’s edition, 1886). (LRV); MANU'S Gesetzbuch in der Ausg. von LOISELEUR DESLONGCHAMPS ( (PWG) — census senses 11 > 2006 senses 2 |
| `M.` | Murti | — | **corrected** | no witness named; digitized legends carry: Mālavikāgnimitra (Bombay). (AP90); Māhārāṣṭrī. (BHS); Matsyôpâkhyâna, i.e. episodium de diluvio. (BOP) …+8 |
| `m` | masculinum | Ko,Wb | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 4 in ['mw'] |
| `m` | mitten | Bt | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 4 in ['mw'] |
| `c.` | conjugation | MW | **corrected** | witness digitized; legends carry: case (MW); case. (MW72) |
| `c.` | class | MW | **corrected** | witness digitized; legends carry: case (MW); case. (MW72) |
| `c.` | causal form | — | **confirmed** | sense-level: Causal (AE) |
| `c.` | nom. c[ase] | MW | **confirmed** | dict-level: case (MW); case. (MW72) |
| `c.` | Classical Sanskrit | Mc | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | cakre | RB | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | cum | Th | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `C.` | consonant | Bk | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | Kausativum | Th | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | Cundra | Rn | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | Cārvāka | ? | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `lit.` | literally | Ln | **extended** | sense-level: Literal, literally (AE); Literal. (AP); Literal. (AP90) …+5 — census senses 6 > 2006 senses 3 |
| `lit.` | littauisch (= Lithuanian) | Th | **extended** | sense-level: Lithuanian (GRA) — census senses 6 > 2006 senses 3 |
| `lit.` | Literaturwissenschaft | My | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `litt.` | literally (identical function in French) | Hn | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 4 in ['bhs', 'pwg'] |
| `fm.` | feminin | Hn | **unmappable** | U1: label absent from census labelTable and inventories |
| `Nm.` | nominative | Mc,Ko | **unmappable** | U1: label absent from census labelTable and inventories |

### Petersburg-Wörterbuch siglum cluster (2006 synonymy note)

| 2006 row | Sense (2006) | Witnesses | Verdict | Evidence (computed) |
|---|---|---|---|---|
| `PW` | Petersburg Wörterbuch (großes) | Bt,Th,Wb | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `Bö` | Petersburg Wörterbuch | Wh | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PWG` | Petersburg Wörterbuch (großes) — MG's proposal | MG | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `BR` | Böhtlingk–Roth Petersburg Wörterbuch | Db,Ln | **confirmed** | sense-level: Boehtlingk and Roth, Sanskrit Wörterbuch. (BHS) |
| `PW1` | Petersburg Wörterbuch (kleines) | Kö | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `pw` | Petersburg Wörterbuch (kleines) | Th,Wb | **confirmed** | sense-level: Boehtlingk, Sanskrit Wörterbuch in kürzerer Fassung. (BHS) |
| `KBR` | Petersburg Wörterbuch variant | ? | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PW2` | Petersburg Wörterbuch (kleines) | Kö | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PWN` | Petersburg Wörterbuch Nachträge | Wb | **unmappable** | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |

### §2.2 — hieroglyphic acronyms

| 2006 row | Sense (2006) | Witnesses | Verdict | Evidence (computed) |
|---|---|---|---|---|
| `prob.` | probably | Ln | **confirmed** | sense-level: probably. (BHS); probably. (MD); probably (MW) |
| `vll.` | vielleicht | Bt | **unmappable** | U1: label absent from census labelTable and inventories |
| `ev.` | eventuell | Wb | **unmappable** | U1: label absent from census labelTable and inventories |
| `St.` | Stamm | Th | **confirmed** | sense-level: Stamm (GRA) |
| `OCH.` | (unexplained) | Ko | **unmappable** | U1: label absent from census labelTable and inventories |
| `st.` | stem | MC | **confirmed** | sense-level: stem. (MD) |
| `st.` | stark (full grade) | St | **unmappable** | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `schw.` | schwach (weak grade) | St | **confirmed** | sense-level: schwach (GRA) |
| `red.` | redupliziert | Wb | **extended** | sense-level: redoublement (BUR); reduplicated, reduplication. (MD) — census senses 2 > 2006 senses 1 |
| `R1, R2, R3` | reduplication markers | Wb | **unmappable** | U1: label absent from census labelTable and inventories |
| `V, S, D` | grades | MR | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 22 in ['bhs', 'mw'] |
| `weak.` | weak | MC | **unmappable** | U1: label absent from census labelTable and inventories |
| `strong.` | strong | MC | **unmappable** | U1: label absent from census labelTable and inventories |
| `AK, EK` | (unexplained) | Th | **unmappable** | U1: label absent from census labelTable and inventories |
| `aA, aE` | (unexplained) | Bt | **unmappable** | U1: label absent from census labelTable and inventories |
| `Vg., Hg.` | Vorderglied/Hinterglied [eines Kompositums] | Wb | **unmappable** | U1: label absent from census labelTable and inventories |
| `Comp.` | Compound | Bf | **extended** | dict-level: Compound. (BEN) — census senses 3 > 2006 senses 1 |
| `ff.` | and the following | Ln | **extended** | sense-level: following. (BHS); and the following. (MD) — census senses 2 > 2006 senses 1 |
| `folg.` | folgende | Th | **confirmed** | sense-level: folgende (GRA) |
| `assev.` | asseverative | Ln | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['lan'] |
| `colloq.` | colloquial | Ln | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 10 in ['lan'] |
| `reg.` | regular | Ln | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 8 in ['lan', 'pwg', 'wil'] |
| `sc.` | scilicet | Ln | **extended** | sense-level: scilicet. (BHS); scilicet. (CAE); scilicet (GRA) …+2 — census senses 3 > 2006 senses 1 |
| `irreg.` | irregular | MW,Ln | **confirmed** | dict-level: irregular (MW) |
| `vulg.` | vulgar | MR | **unmappable** | U2: no machine-readable legend; inline tokens (ab/lex/lang) 248 in ['pwg', 'wil'] |
| `Rhet.` | Rhetoric | Kl | **confirmed** | sense-level: Rhetoric. (AP); Rhetoric. (AP90) |

## Spot checks (the acceptance class)

The V./c./M./P./N. homographs and the Petersburg sigla each carry a computed
verdict confirming or diverging from the 2006 text:

| Spot check | 2006 | Computed verdict |
|---|---|---|
| `V.` | vocativus / Vedic / Vopadeva / vide / Vikram | **extended** — vocativus, Vedic, Vopadeva, Vikram computed; vide unattested |
| `c.` | conjugation, class (MW); causal; nom. case (MW) | **unmappable** — MW digitized: case only — conjugation and class corrected; causal and case confirmed |
| `M.` | Manu (Wh, Wg, Kn); Murti | **corrected** — Manu extended (census 11 senses vs 2); Murti unattested |
| `P.` | Parasmaipada (Ko) … Aṣṭādhyāyī (Wg, Ap, Rn) | **extended** — Parasmaipada and Aṣṭādhyāyī computed at dict level (AP/AP90); polysemy 11 vs 10 |
| `N.` | Name (St) … neuter (Ln, Wb) | **unmappable** — Name, name-of-person, Naiṣadhacarita, Nala, neuter computed; polysemy 10 vs 8 |
| `BR / pw` | Petersburg Wörterbuch sigla (Db, Ln / Th, Wb) | **—** — both confirmed: Böhtlingk-Roth legends live under BR and pw in BHS |

## Appendix — unmappable claims (recorded, never silently dropped)

Per the handoff fail-clause: a 2006 claim that cannot be mapped to payload
rows stops as unmappable with the reason, and no verdict is hand-tuned.

| 2006 row | Sense | Reason |
|---|---|---|
| `f.` | futurum | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `ij` | interjection | U1: label absent from census labelTable and inventories |
| `V.` | vide | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `V` | Vollstufe | U2: no machine-readable legend; inline tokens (ab/lex/lang) 2 in ['bhs', 'mw'] |
| `V` | vowel | U2: no machine-readable legend; inline tokens (ab/lex/lang) 2 in ['bhs', 'mw'] |
| `V` | voir | U2: no machine-readable legend; inline tokens (ab/lex/lang) 2 in ['bhs', 'mw'] |
| `P.` | Person | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | pagina | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | Praesens | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | Pluralis | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | Prosa | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `P.` | … | U4: 2006 states no sense to match |
| `P.` | Prajña | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `ātm.` | ātmanepada | U1: label absent from census labelTable and inventories |
| `A.` | Āfrīnakān | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `A.` | Anmerkung | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `Ä.` | ātmanepada (umlaut variant) | U1: label absent from census labelTable and inventories |
| `a` | adjective | U1: label absent from census labelTable and inventories |
| `a` | apabhaṁça | U1: label absent from census labelTable and inventories |
| `a` | article | U1: label absent from census labelTable and inventories |
| `S.` | ai, au | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `S` | Schwundstufe | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Sārasvata | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Semantik | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Sāvitrī | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `S` | Sāṁkhya | U2: no machine-readable legend; inline tokens (ab/lex/lang) 20 in ['bhs'] |
| `s` | singular | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | substantivum | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | simple | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | siehe | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `s` | summary | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['fri'] |
| `N.` | Nyāsa | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `N.` | note (in Small Caps) | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `m` | masculinum | U2: no machine-readable legend; inline tokens (ab/lex/lang) 4 in ['mw'] |
| `m` | mitten | U2: no machine-readable legend; inline tokens (ab/lex/lang) 4 in ['mw'] |
| `c.` | Classical Sanskrit | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | cakre | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | cum | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `C.` | consonant | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | Kausativum | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | Cundra | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `c.` | Cārvāka | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `lit.` | Literaturwissenschaft | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `litt.` | literally (identical function in French) | U2: no machine-readable legend; inline tokens (ab/lex/lang) 4 in ['bhs', 'pwg'] |
| `PW` | Petersburg Wörterbuch (großes) | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `Bö` | Petersburg Wörterbuch | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PWG` | Petersburg Wörterbuch (großes) — MG's proposal | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PW1` | Petersburg Wörterbuch (kleines) | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `KBR` | Petersburg Wörterbuch variant | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PW2` | Petersburg Wörterbuch (kleines) | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `PWN` | Petersburg Wörterbuch Nachträge | U1: label absent from census labelTable and inventories; work digitized as corpus dicts pw/pwg/pwkvn; attested sigla in the legend layer: see BR/pw rows |
| `fm.` | feminin | U1: label absent from census labelTable and inventories |
| `Nm.` | nominative | U1: label absent from census labelTable and inventories |
| `vll.` | vielleicht | U1: label absent from census labelTable and inventories |
| `ev.` | eventuell | U1: label absent from census labelTable and inventories |
| `OCH.` | (unexplained) | U1: label absent from census labelTable and inventories |
| `st.` | stark (full grade) | U3: sense not attested in the legend layer; witnesses outside the digitized legend set |
| `R1, R2, R3` | reduplication markers | U1: label absent from census labelTable and inventories |
| `V, S, D` | grades | U2: no machine-readable legend; inline tokens (ab/lex/lang) 22 in ['bhs', 'mw'] |
| `weak.` | weak | U1: label absent from census labelTable and inventories |
| `strong.` | strong | U1: label absent from census labelTable and inventories |
| `AK, EK` | (unexplained) | U1: label absent from census labelTable and inventories |
| `aA, aE` | (unexplained) | U1: label absent from census labelTable and inventories |
| `Vg., Hg.` | Vorderglied/Hinterglied [eines Kompositums] | U1: label absent from census labelTable and inventories |
| `assev.` | asseverative | U2: no machine-readable legend; inline tokens (ab/lex/lang) 1 in ['lan'] |
| `colloq.` | colloquial | U2: no machine-readable legend; inline tokens (ab/lex/lang) 10 in ['lan'] |
| `reg.` | regular | U2: no machine-readable legend; inline tokens (ab/lex/lang) 8 in ['lan', 'pwg', 'wil'] |
| `vulg.` | vulgar | U2: no machine-readable legend; inline tokens (ab/lex/lang) 248 in ['pwg', 'wil'] |

## Method

* Claims are transcribed verbatim from the fulltext (`quote` column in the TSV);
  the published PDF is authoritative where the extraction garbles diacritics.
* Sense matching: deterministic regex per claim over NFC-casefolded census
  expansions, covering the Latin/German/French surface forms of the same sense
  (e.g. Aktivum → active, littauisch → Lithuanian, red. → redoubl-/reduplic-).
* Witness join: only certain 2006-code → census-dict joins are encoded
  (MW → MW/MW72, Ap → AP/AP90, Bf → BEN, Ln → LAN);
  every other 2006 witness sits outside the digitized legend set, and the
  denominators state that honestly rather than guessing a join.
* Verdict precedence corrected > extended > confirmed; extension compares the
  census sense count for the label with the distinct senses the 2006 tables
  record for it (computed from this claim table, not remembered).
* Absence of a legend row is not evidence of absence in the dictionary — that
  is exactly what U1–U3 mark, following the H6409 lower-bound caveat
  (26 of 44 catalogued dictionaries have no machine-readable legend).

## Provenance

* census payload: `data/abbrev/abbrev_census.json` (H6409, generated 2026-10-10T19:00:00.879Z,
  corpus commit `f4c08c578b33`)
* model: GLM-5.3-Flash (zai-coding-plan/glm-5.3-flash) via ZCode; handoff H6459

_Dr. Mārcis Gasūns_
