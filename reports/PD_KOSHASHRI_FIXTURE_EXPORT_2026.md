# PD KoshaSHRI fixture TSV export (H7316)

_Created: 29-10-2026 · Executor: Kimi (`kimi-code-plan-global/k3.1-pro`) · Status: complete_

## Verdict

The first fixture-only KoshaSHRI export is complete: **one `agni` entry and
1,400 citation-reference rows**, generated deterministically from the recovered
response and adapter. The first meaning preserves the required distinction of
**242 citation texts → 248 citation-reference rows** (237 single-reference,
four two-reference and one three-reference citations). All 29 meanings are
present.

## Inputs and recovery

- The response is the public single-entry GET
  `https://koshashri-dc.ac.in/search/vocable/3b892686-9184-4bce-a2cc-aaa78551e517`.
  It is staged locally as `data/pd/koshashri_vocable.json` (2,768,644 bytes,
  SHA-256 `1a8322bb948fd579c7c7177260ec3df2a88cec4bdee71b70ea21fa423ee0d88e`).
  The byte size matches the 26-10 capture record; all contract canaries were
  revalidated on 29-10. No login, POST, socket subscription or bulk crawl was used.
- The adapter was recovered verbatim from the local 27-10 write record and is
  now committed as `scripts/pd_koshashri_vocable.py`. The schema map came from
  the same record. No second parser or work registry was built.
- Work resolution consumes H7296's `data/pd/pd_work_edition_map.tsv` read-only.
  Only exact `ṚV.` is resolved, to `PDW-ecd09ac913`; every other siglum remains
  unresolved rather than being guessed.

## Outputs

| Artifact | Contents |
|---|---|
| `data/pd/pd_koshashri_entries.tsv` | One entry with stable `koshashri:<uuid>` ID, Devanagari/IAST headwords, grammar, raw source fields, volume, sandhi and nested-vocable JSON, validation state and provenance |
| `data/pd/pd_koshashri_citations.tsv` | 1,400 rows with stable entry/sense/citation IDs, raw quotation text, siglum, locus array/scheme, raw work date, work-resolution state, validation state and provenance |
| `scripts/pd_koshashri_fixture_export.py` | Offline deterministic builder and `--check`; no network and no raw-response emission |
| `tests/forensic/test_pd_koshashri_fixture_export.py` | Five offline pins, including a changed-canary refusal and an always-on synthetic multi-reference/nested-sense test |

The volume object remains `{volumeNumber: 4, name: Volume 2}`. One nested
vocable is retained. Sense paths such as `1`, `2i` and `2ii` stay distinct.
The malformed source prefix `<s<small>` is preserved, not repaired. Every
citation row is `unvalidated_pending_double_annotation`.

## Verification

```text
python3 scripts/pd_koshashri_fixture_export.py --check
OK: 1 entry, 1400 citation-reference rows; canaries and byte identity green

python3.13 -m pytest tests/forensic/test_pd_koshashri_fixture_export.py -q
5 passed in 14.17s
```

A second build was byte-identical. Removing one first-meaning citation returns
exit 2 with `STOP_CANARY_MISMATCH`. Output SHA-256 pins:

- entries: `29f3cbf7654256762d380e279ffd364acf24106d080803f8b760f09f1bf35fdd`
- citations: `e325dad1369f61ed7e16c7a293ea9d8ac1c04813bd214424e2a4bd6812f67257`

## Rights, boundaries and risks

KoshaSHRI is **all rights reserved**. The full response remains a restricted
local input and is **not committed**. Only the single fixture expressly scoped
by H7316 is exported; there is no bulk publication, no new work ID and no
independent-witness claim. H7296's registry, raw source response and csl-orig
are unchanged. Unresolved works and malformed source strings remain explicit
risks, not silently normalized facts.

Inspect first: `pd_koshashri_citations.tsv` rows for sense `:1`, where the
242→248 split is visible, then the entry row's `nested_vocables`,
`source_volume` and `grammatical_note_raw_html` fields.
