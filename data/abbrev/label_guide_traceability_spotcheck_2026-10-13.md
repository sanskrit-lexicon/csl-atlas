# H6465 — row-traceability spot-check log (guide row → census payload row)

_Date: 2026-10-13 · executor GLM-5.3-Flash (zai-coding-plan/glm-5.3-flash) via ZCode · handoff H6465_

Mechanical spot-check: 8 of the 138 guide evidence rows drawn by seeded RNG (seed 6465) and re-opened
against [data/abbrev/abbrev_census.json](abbrev_census.json). Each check re-reads `labelTable[label].legends`
and the `polysemy[label].nExpansions` count; PASS = expansion verbatim + dict verbatim + census sense count equal.
The full-table guarantee is enforced continuously by `scripts/test_build_abbrev_label_guide.py` (9 cases) and
`npm run build-abbrev-label-guide -- --check` (byte-parity gate); this log is the bounded human-readable receipt.

| # | Guide row (label) | Census field checked | Payload value | Guide value | Verdict |
|---|---|---|---|---|---|
| 1 | `K.` | legends+polysemy | expansion 'Karañja' dicts GRA; senses 5 | same | PASS |
| 2 | `P.` | legends+polysemy | expansion '1) Parasmaipadum. 2) Påtaliputra (ed. H. Brockha' dicts BOP; senses 11 | same | PASS |
| 3 | `U.` | legends+polysemy | expansion 'Upaniṣad.' dicts MD; senses 5 | same | PASS |
| 4 | `med.` | legends+polysemy | expansion 'medium' dicts GRA; senses 1 | same | PASS |
| 5 | `P.` | legends+polysemy | expansion "PĀṆINI'S acht Bücher grammatischer Regeln (GILD." dicts PWG; senses 11 | same | PASS |
| 6 | `P.` | legends+polysemy | expansion 'PĀṆINI. (vol. 1)' dicts PW; senses 11 | same | PASS |
| 7 | `R.` | legends+polysemy | expansion 'RĀMĀYANA. Das 1ste und 2te Kāṇḍa nach der Ausg. ' dicts PW; senses 7 | same | PASS |
| 8 | `S.` | legends+polysemy | expansion 'Sādhya.' dicts INM; senses 5 | same | PASS |

Not-in-census labels flagged in the guide: `inj.` — each verified absent from `labelTable` (absence is itself a computed payload fact; the guide never glosses them).

**Overall: 8/8 PASS** · guide `docs/A72_LABEL_READING_GUIDE.ru.md` · TSV twin `data/abbrev/label_guide_rows.tsv`.
