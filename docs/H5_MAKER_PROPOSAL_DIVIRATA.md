# H5 Maker Proposal — divaraṭa → diviraṭa (MW, PWG), with the evidence packet

_Created: 24-09-2026 · Last updated: 24-09-2026_

**Status: DRAFT — written for transmission to the Cologne Digital Sanskrit Dictionaries
maintainers. Nothing has been filed upstream: no issue, PR, or commit exists or was
created in [csl-orig](https://github.com/sanskrit-lexicon/csl-orig) or any other Cologne
surface. Sending this proposal is a human step, tracked in the Atlas FAIR roadmap
(SanskritLexicography `ROADMAP_ATLAS_FAIR_PUBLICATIONS_2026_2027.md`, Q3 2026: "Clear H5
maker proposal to Cologne makers").**

Evidence pinned to csl-orig revision
[`f4c08c578b330e2379e38f54d3a541f1564b8eee`](https://github.com/sanskrit-lexicon/csl-orig/commit/f4c08c578b330e2379e38f54d3a541f1564b8eee)
(2026-09-20). All line numbers below resolve at that revision. Evidence labels follow
[docs/EVIDENCE_LABELS.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md):
`observed` = read directly from the source record; `derived` = computed from committed data.

This document extends the generated internal packet
[docs/H5_MAKER_CORRECTION_PROPOSAL.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H5_MAKER_CORRECTION_PROPOSAL.md)
(proposal ID `h5-maker-correction:01:h5:mw-pwg-shared-doublet:MW-PWG:divaraTa:devaraTa`)
into the external form a Cologne maintainer can act on. It adds the printed-edition scan
loci, the full cross-dictionary witness table, and the corpus attestation. Line-number
note: the June packet's GitHub anchors for the two MW entries (`#L309834`, `#L310248`)
were correct at its 2026-06-07 generation revision; at the current pin both shifted by
one line (`#L309835`, `#L310249`) — this document cites the pinned numbers.

_Encoding note (for non-Cologne readers): citations below use the Cologne internal
transliteration, where capital `T` = ṭ, `A` = ā, `I` = ī. So `divaraTa` = divaraṭa
(दिवरट) and `diviraTa` = diviraṭa (दिविरट)._

_Гасунс_

## 1. Summary

Two Cologne digital dictionary entries carry the headword `divaraTa` (divaraṭa):

- [MW L92243](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L309835)
  — `<s>diva—raTa</s> ¦ <ab>w.r.</ab> for <s>divi-</s> (<ab>q.v.</ab>)`
- [PWG L32945](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt#L165464)
  — `{#divaraTa#}¦ <ls>VP. 445</ls> falsche Form für {#diviraTa#}.`

Both entries declare — in their own words — that divaraṭa is the **wrong reading** for
diviraṭa (`w.r.` = wrong reading; `falsche Form` = wrong form). Neither carries any
independent lexical content: no sense, no analysis, only the pointer to diviraṭa. Every
independent witness in the Cologne estate (PW, Vācaspatyam, Sørensen's Index of Names in
the Mahābhārata) and the DCS corpus records **only** diviraṭa; divaraṭa occurs nowhere.

We therefore ask the makers to confirm that `divaraTa` in MW and PWG is a
source-declared wrong-reading cross-reference to `diviraTa`, not an independent
headword — and, if cheap, to expose that linkage in the digital search/index layer.

## 2. The exact proposed change

**Ask A (data-quality confirmation — the real ask).** Confirm that in the digital
editions MW and PWG, `divaraTa` (MW L92243; PWG L32945) is understood as a
source-declared wrong reading of `diviraTa` (MW L92364; PWG L33004) and is not an
independent lexical item. A one-line confirmation ("yes, these are wrong-reading
cross-references") closes the atlas-side H5 ghost-candidate review; we will then treat
`divaraTa` as source-declared wrong-form in our cross-dictionary headword layers.

**Ask B (optional index improvement — only if cheap).** If the Cologne digital search
layer can redirect or alias a `divaraṭa` lookup to the `diviraṭa` entry content, we
request that it do so for these two entries. **No entry text is proposed for change**:
both printed entries already declare the wrong reading themselves; the print is correct
scholarship and must stay untouched. If a redirect is not feasible, no upstream action
is needed — the atlas layer handles it locally.

_What is NOT proposed_: any edit to csl-orig or any Cologne repository from our side;
any change to the printed text or its transcription; deletion or modification of the
two wrong-reading entries.

## 3. Dictionary witnesses

All rows `observed` at the pinned csl-orig revision. `—` = form absent from that
dictionary's headword stock.

| Dictionary | divaraṭa | diviraṭa | Entry record | Body (transliterated) | Printed locus (`<pc>`) |
|---|---|---|---|---|---|
| MW (Monier-Williams 1899) | ✓ | ✓ | [mw.txt L92243](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L309835) | `diva—raTa ¦ w.r. for divi- (q.v.)` | p. 478, col. 3 |
| MW | — | ✓ | [mw.txt L92364](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/mw/mw.txt#L310249) | `divi—raTa ¦ m. N. of several men (v.l. diva-), MBh.; Hariv.; Pur.` | p. 479, col. 1 |
| PW (Böhtlingk & Roth, Sanskrit-Wörterbuch) | — | ✓ | [pw.txt L50335](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pw/pw.txt#L206741) | `diviraTa ¦ m. N. pr. verschiedener Männer.` | vol. 3, p. 89, col. b |
| PWG (Böhtlingk, Sanskrit-Wörterbuch in kürzerer Fassung) | ✓ | ✓ | [pwg.txt L32945](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt#L165464) | `divaraTa ¦ VP. 445 falsche Form für diviraTa.` | vol. 3, p. 620 |
| PWG | — | ✓ | [pwg.txt L33004](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/pwg/pwg.txt#L165728) | `diviraTa ¦ (divi loc. + raTa) m. N. pr. eines Sohnes des Bhumanyu MBH. 1,3714. des Dadhivāhana MBH. 12,1796. HARIV. 1694. des Khanapāna ... BHĀG. P. 9,23,6.` — ends `Vgl. divaraTa.` | vol. 3, p. 623 |
| VCP (Vācaspatyam) | — | ✓ | [vcp.txt L25025](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/vcp/vcp.txt#L327526) | Devanagari entry with the genealogy verses (`tato diviraTo 'Bavat ...` — son of Bhūmanyu, "Cakratulya-parākrama") | `<pc>3588,a` |
| INM (Sørensen, An Index to the Names in the Mahābhārata) | — | ✓ | [inm.txt L3636](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/inm/inm.txt#L43478), [L3637](https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02/inm/inm.txt#L43483) | two entries for `diviraTa` (two homs); Sørensen romanizes the name in the body as "Diviratha" (raTa = older spelling of ratha) — "Diviratha, the son of Bhumanyu. § 152" | `<pc>256-1` (p. 256) |
| DCS-2021 corpus (Hellwig) | — | ✓ | [dcs_lemma_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dcs/dcs_lemma_summary.json) | `diviraTa: freqBand 2, attested: true` | — |

The pattern is one-directional: **every witness that mentions the word at all carries
diviraṭa; divaraṭa exists only in MW and PWG, and in both of those the wrong form is
flagged by the dictionary itself.** Note also that MW's own diviraṭa entry already
registers the manuscript variant (`v.l. diva-`): the variant lives where the content
lives, and the two standalone `divaraTa` entries duplicate only the pointer.

## 4. Scan loci

All scan links verified live (HTTP 200) on 24-09-2026. The `<pc>` values in the table
above are the authoritative printed loci (page, column); the scan viewer navigates
half-pages, so `side=a`/`side=b` below are half-page approximations of the column.

| Dictionary entry | Printed locus | Scan link |
|---|---|---|
| MW, divaraṭa (L92243) | p. 478, col. 3 | [MWScan p. 478, side b](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/index.php?page=478&side=b) |
| MW, diviraṭa (L92364) | p. 479, col. 1 | [MWScan p. 479, side a](https://www.sanskrit-lexicon.uni-koeln.de/scans/MWScan/2020/web/index.php?page=479&side=a) |
| PW, diviraṭa (L50335) | vol. 3, p. 89, col. b | [PWScan p. 89](https://www.sanskrit-lexicon.uni-koeln.de/scans/PWScan/2020/web/index.php?page=89&side=a) |
| PWG, divaraṭa (L32945) | vol. 3, p. 620 | [PWGScan p. 620](https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/web/index.php?page=620&side=a) |
| PWG, diviraṭa (L33004) | vol. 3, p. 623 | [PWGScan p. 623](https://www.sanskrit-lexicon.uni-koeln.de/scans/PWGScan/2020/web/index.php?page=623&side=a) |
| VCP, diviraṭa (L25025) | `<pc>3588,a` | [VCPScan p. 3588](https://www.sanskrit-lexicon.uni-koeln.de/scans/VCPScan/2020/web/index.php?page=3588&side=a) |
| INM, diviraṭa (L3636/L3637) | p. 256 | [INMScan p. 256](https://www.sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/index.php?page=256&side=a) |

## 5. Corpus attestation

**DCS-2021** (Oliver Hellwig, DCS ~2021 snapshot, CC BY), as committed in the atlas
[data/dcs/dcs_lemma_summary.json](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/dcs/dcs_lemma_summary.json)
(schemaVersion 1.0.0, generated by VisualDCS 2026-06-13, 83,239 lemmas, source
`src/DCS-data-2021/_8.csv`; counts `derived`):

- `diviraTa` — attested, `freqBand: 2` = rare (2–9 occurrences under the summary's
  log10 banding rule: 1 = hapax, 2 = 2–9, 3 = 10–99 …).
- `divaraTa` — **not attested** (0 occurrences in the 83,239-lemma summary).

**Text loci cited by the sources themselves** (as recorded in the entries above; these
are the places a maintainer can check the word in the Mahābhārata/Harivaṃśa/Purāṇa
text tradition):

- Mahābhārata — Böhtlingk chapter loci 1,3714 (son of Bhūmanyu) and 12,1796 (son of
  Dadhivāhana), per PWG L33004; "MBh." bare, per MW L92364.
- Harivaṃśa — 1694 (PWG); "Hariv." bare (MW).
- Bhāgavata Purāṇa 9,23,6 — diviraṭa as son of Khanapāna, per PWG L33004.
- Viṣṇu Purāṇa, p. 445 — the locus of the **wrong form**, per PWG L32945.

**Atlas cross-check** (`derived`): the committed
[data/forensic/mbh_citation_inventory.csv](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/mbh_citation_inventory.csv)
already classifies the two PWG MBH citations as `full` (machine-resolvable to Böhtlingk
chapter loci) and MW's as `bare` — rows `PWG,1,3714,full,,33004,diviraTa`,
`PWG,12,1796,full,,33004,diviraTa`, `MW,,,bare,,92364,diviraTa`.

## 6. Reasoning: why divaraṭa is a source-declared wrong form

1. `observed` — MW L92243 says `w.r. for divi-`; PWG L32945 says `falsche Form für
   diviraTa`. The dictionaries themselves declare it.
2. `derived` — at the pinned csl-orig revision, divaraṭa is a headword in exactly two
   of the seven witnesses checked (MW, PWG); PW, VCP, INM, and DCS carry only
   diviraṭa.
3. `observed` — MW L92364 registers the variant reading `v.l. diva-` inside the
   diviraṭa entry itself.
4. `derived` — DCS-2021: 0 occurrences of divaraṭa; diviraṭa attested (rare band).
5. `observed` — PWG L33004 gives the only morphological analysis in play:
   diviraṭa = divi (locative of div "sky") + raṭa (m. "car"); no analysis of
   "divaraṭa" exists anywhere.

This matches the source-check disposition of the atlas H5 maker-QA packet
([docs/H5_MAKER_QA_CANDIDATES.md](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H5_MAKER_QA_CANDIDATES.md),
candidate #8, 2026-06-07): `source-declared-correction-candidate`, accepted correction
`diviraTa` — with the detector's nearest neighbour `devaraTa` (`deva-raṭa` "god's car",
AV., TS., Br. — a real, distinct word) rejected as a correction target.

## 7. Scope and boundaries

- **Draft only.** This document has not been sent; no issue/PR/commit was created in
  csl-orig or any Cologne surface (verified 24-09-2026: no open or closed issue in
  sanskrit-lexicon/csl-orig mentions either form).
- **Transmission is a human step** — the Atlas FAIR roadmap Q3 2026 row stays open
  until the proposal is actually sent; the `makerDecision` fields of the internal
  packet (`submittedBy`, `submittedAt`, `externalIssueUrl`, `makerDisposition`)
  remain null until then.
- **No parser, corpus, DCS, or standards work changes** with this document; it is
  evidence assembly on already-committed atlas layers.

## 8. Verification appendix

Each claim re-checkable at the pinned csl-orig revision
(`f4c08c578b330e2379e38f54d3a541f1564b8eee`):

```bash
# 1. The two wrong-reading entries (must print the w.r. / falsche Form entry headers)
sed -n '309835p' v02/mw/mw.txt
sed -n '165464p' v02/pwg/pwg.txt
# 2. The diviraTa entries
sed -n '310249p' v02/mw/mw.txt
sed -n '165728p' v02/pwg/pwg.txt
sed -n '206741,206742p' v02/pw/pw.txt
sed -n '327526,327531p' v02/vcp/vcp.txt
sed -n '43478,43487p' v02/inm/inm.txt
# 3. Headword-stock pattern: divaraTa only in MW/PWG
grep -x 'divaraTa' v02/*/vcp.txt v02/inm/inm.txt v02/pw/pw.txt   # expect no output
# 4. Corpus pattern (atlas)
grep -c '"divaraTa"' data/dcs/dcs_lemma_summary.json             # expect 0 (exit 1)
grep -o '"diviraTa":{"freqBand":2,"attested":true}' data/dcs/dcs_lemma_summary.json
# 5. MBH citation cross-check (atlas)
grep 'diviraTa' data/forensic/mbh_citation_inventory.csv
```

_Гасунс_
