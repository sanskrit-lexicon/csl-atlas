# ORCID gap census — the four ATLAS repos

_Created: 23-09-2026 · Last updated: 23-09-2026_

Who is still missing an ORCID iD in the citation metadata of the four ATLAS
repos. Read-only census: **no iD was invented, guessed or looked up.** Every row
below is a literal observation of a file on disk at the revisions in the
coverage table.

## Scope and coverage

Four repos, six metadata files. Two repos ship a `.zenodo.json`, two do not.

| Repo | `CITATION.cff` | `.zenodo.json` |
|---|---|---|
| [`csl-atlas`](https://github.com/sanskrit-lexicon/csl-atlas) | ✅ present | ✅ present |
| [`csl-standards`](https://github.com/sanskrit-lexicon/csl-standards) | ✅ present | ❌ absent |
| [`VisualDCS`](https://github.com/gasyoun/VisualDCS) | ✅ present | ❌ absent |
| [`csl-observatory`](https://github.com/sanskrit-lexicon/csl-observatory) | ✅ present | ✅ present |

No `codemeta.json` and no `contributors:` key exists in any of the six files —
the census therefore covers every `authors:` (CFF) and `creators:` (Zenodo)
entry, which is the complete set of person-level metadata in scope.

**Method:** read each file, enumerate every `authors:` / `creators:` entry, and
record the line span of each entry that carries no `orcid:` key. Line numbers
are 1-based, as read.

## Summary

| Metric | Count |
|---|---|
| Repos inspected | 4 |
| Metadata files inspected | 6 |
| Person entries total | 10 |
| Entries **with** an ORCID iD | 4 |
| Entries **without** an ORCID iD | **6** |

The gap is not zero: six entries need an iD.

## Missing ORCID iDs — the fix list

Each row is one entry with no `orcid:` key. "Fix at" names the exact line to
edit (add or uncomment the `orcid:` key there).

| # | Repo | File | Entry (as written) | Line(s) | Fix at |
|---|---|---|---|---|---|
| 1 | `csl-atlas` | `CITATION.cff` | Funderburk, Jim (`alias: funderburkjim`) | 17–20 | line 20 — the placeholder `# orcid: ...  # TODO` is commented out; replace it with the real `orcid:` |
| 2 | `csl-atlas` | `CITATION.cff` | Andhrabharati (alias only) | 21 | line 21 — add an `orcid:` key; the entry also still needs `family-names` / `given-names` (its own `# TODO: confirm preferred legal name and ORCID`) |
| 3 | `csl-atlas` | `.zenodo.json` | `{ "name": "Gasūns, Mikhail" }` | 9 | line 9 — add `"orcid"` to the object |
| 4 | `csl-atlas` | `.zenodo.json` | `{ "name": "Funderburk, Jim" }` | 10 | line 10 — add `"orcid"` |
| 5 | `csl-atlas` | `.zenodo.json` | `{ "name": "Andhrabharati" }` | 11 | line 11 — add `"orcid"` |
| 6 | `csl-standards` | `CITATION.cff` | Gasūns, Mārcis | 5–6 | line 6 — add an `orcid:` key (the same person's iD is already present in three sibling files, see below) |

### Exact `file:line` short form

```
csl-atlas/CITATION.cff:20          (Funderburk, Jim — placeholder commented out)
csl-atlas/CITATION.cff:21          (Andhrabharati)
csl-atlas/.zenodo.json:9           (Gasūns, Mikhail)
csl-atlas/.zenodo.json:10          (Funderburk, Jim)
csl-atlas/.zenodo.json:11          (Andhrabharati)
csl-standards/CITATION.cff:6       (Gasūns, Mārcis)
```

## Entries that already carry an ORCID iD (context)

Listed so the census is complete and the "present" side is auditable.

| Repo | File | Entry | Line(s) | iD |
|---|---|---|---|---|
| `csl-atlas` | `CITATION.cff` | Gasūns, Mārcis | 13–16 | `0000-0003-4513-884X` |
| `VisualDCS` | `CITATION.cff` | Gasūns, Mārcis | 11–13 | `0000-0003-4513-884X` |
| `csl-observatory` | `CITATION.cff` | Gasūns, Mārcis | 21–23 | `0000-0003-4513-884X` |
| `csl-observatory` | `.zenodo.json` | Gasūns, Mārcis | 7–9 | `0000-0003-4513-884X` |

## Adjacent inconsistencies observed (not ORCID gaps, but visible in the same pass)

1. **Same person, present iD in one file and missing in another.** Gasūns,
   Mārcis carries `0000-0003-4513-884X` in `csl-atlas/CITATION.cff:16`,
   `VisualDCS/CITATION.cff:13`, `csl-observatory/CITATION.cff:23` and
   `csl-observatory/.zenodo.json:9` — yet has none in
   `csl-atlas/.zenodo.json:9` or `csl-standards/CITATION.cff:6`. Rows 3 and 6 of
   the fix list are the same person as an already-populated entry, so those two
   fixes need no new information, only propagation.
2. **Name variant.** `csl-atlas/.zenodo.json:9` writes `"Gasūns, Mikhail"`,
   while every other file writes `"Gasūns, Mārcis"`. This is a name-consistency
   defect, separate from the ORCID gap; flagged, not fixed here.

## Out of scope — deliberately not counted

Entries under `references:` are **cited upstream works**, not authors or
contributors of the citing repo, so they are excluded from the gap count. They
are recorded here so nothing is silently dropped:

| Repo | File | Reference entry | Line(s) | ORCID |
|---|---|---|---|---|
| `csl-atlas` | `CITATION.cff` | Cologne Digital Sanskrit Dictionaries project (corporate name) | 39–40 | n/a — corporate author, no iD applies |
| `VisualDCS` | `CITATION.cff` | Hellwig, Oliver (upstream DCS corpus) | 40–41 | none in file; upstream author, not a VisualDCS contributor |

If the scope is later widened to cited works, `VisualDCS/CITATION.cff:40–41` is
the one human entry that would join the list.

## What this census does NOT do

- It does not invent, guess, resolve or look up any ORCID iD for anyone. Rows
  without an iD stay without an iD until a human supplies the value.
- It does not edit the six metadata files. It records where the edits go.

_Гасунс_
