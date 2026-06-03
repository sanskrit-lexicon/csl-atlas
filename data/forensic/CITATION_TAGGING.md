# Citation tagging across CDSL dictionaries — a correction

**Status**: corrects an error in the F1 framing (and a repeat of the 2026-05-30
SKD/VCP miscall). **`<ls>`-count = 0 does NOT mean "citation-free".**

`f1_citations.py` and `parse_cslorig.py` count only `<ls>…</ls>` tags. That tag is a
**Western critical-apparatus** convention. Several dictionaries cite *densely* but in
the **indigenous Sanskrit commentarial** style, which carries no `<ls>` tag:

- `iti <authority>` — attribution (`… iti kavikalpadrumaH`, `… iti jyotizam`)
- `“ … ”` — quoted verse / passage
- `X0` — abbreviated authority (the SLP1 rendering of the abbreviation marker:
  `tri0`, `pu0`, `jE0`, `BA0`, `amara0`)

## Measured (csl-orig/v02, raw counts)

| dict | `<ls>` | `iti` | indigenous markers* | citation profile |
|---|---|---|---|---|
| **SKD** (Śabdakalpadruma) | 0 | **84,616** | 60,980 | **densest in corpus** — indigenous |
| **VCP** (Vācaspatyam) | 0 | **30,928** | 153,664 | **densest in corpus** — indigenous |
| INM (Mahābhārata name index) | 0 | 963 | 12,421 | dense — quote/reference |
| MW72 (Monier-Williams 1872) | 0 | 5,022 | 1,740 | moderate — refs in prose |
| SHS (Śabda-sāgara) | 0 | 2,370 | 1,261 | moderate — indigenous |
| PE (Purāṇa index) | 0 | 1,389 | 2,378 | moderate |
| BOP (Bopp glossarium) | 0 | 764 | 1,187 | moderate |
| CCS (Cappeller, German) | 0 | 368 | 7 | genuinely light |
| CAE (Cappeller, English) | 0 | 981 | 12 | genuinely light |
| YAT (Yates) | 0 | 749 | 63 | light |
| — `<ls>`-tagging set — | | | | |
| PWG / PW / MW | 571k / 88k / 312k | — | — | Western `<ls>` apparatus |
| PWKVN/SCH/AP/AP90/BEN/BHS/LRV/GRA/AE/BOR/WIL/MD | >0 | — | — | Western `<ls>` apparatus |

\* rough density proxy (quotes + `X0` abbreviation markers); conflated, read as
"indigenous-citation markup present", not an exact quote count.

## Consequence for the forensic work

- **F1 (citation forensics) is valid as scoped**: it compares the `<ls>`-tagging
  *Western-tradition* dicts, where PWG/PW/MW all live. The MW↔Petersburg result stands —
  it never claimed anything about SKD/VCP.
- **F1 simply cannot see** SKD/VCP/INM citations (different convention). They are
  *excluded for lack of `<ls>`*, **not** because they are citation-free. A cross-tradition
  citation study would need an **indigenous-citation parser** (`iti`+authority, `“…”`,
  `X0`) — partially prototyped earlier in `observatory/.../macro_profile.py`.
- Wherever earlier notes/messages said "dicts with zero citations (…skd/vcp…)", read
  "zero **`<ls>`-tagged** citations". SKD and VCP are in fact the most heavily-citing
  dictionaries in the corpus.

**Recurring lesson** (third occurrence): validate a detector against real entries before
labelling — never infer "absent" from "untagged-in-the-one-scheme-I-parsed".
