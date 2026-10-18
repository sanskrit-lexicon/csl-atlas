# ORCID gap census — the four ATLAS repos (H5306)

_Created: 24-09-2026 · Last updated: 24-09-2026_

Census of every author/contributor entry **without an ORCID iD** across
`CITATION.cff` and `.zenodo.json` in csl-atlas, csl-standards, VisualDCS and
csl-observatory. No iD was invented or looked up; each gap row says the exact
file and line to fix. Reproduce with
`python3 scripts/orcid_gap_census.py` (pinned revs below; all four verified
equal to live `origin/main` on 24-09-2026).

**Result: 7 person entries missing an iD — 6 same-repo fixable, 1 third-party
reference author.** csl-observatory is fully covered (zero gaps).

## Pinned revisions (all == origin/main at census time)

| Repo | Rev | Files present |
|---|---|---|
| [csl-atlas](https://github.com/sanskrit-lexicon/csl-atlas/tree/bbca791) | `bbca791` | CITATION.cff + .zenodo.json |
| [csl-standards](https://github.com/sanskrit-lexicon/csl-standards/tree/2a0c294) | `2a0c294` | CITATION.cff only |
| [VisualDCS](https://github.com/gasyoun/VisualDCS/tree/6277c8b) | `6277c8b` | CITATION.cff only |
| [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory/tree/3f0d700) | `3f0d700` | CITATION.cff + .zenodo.json |

## Gaps to fix (6 same-repo entries)

1. **csl-atlas `CITATION.cff` line 20** — Funderburk, Jim (authors[1],
   [L17–20](https://github.com/sanskrit-lexicon/csl-atlas/blob/bbca791/CITATION.cff#L17-L20)):
   the placeholder `# orcid: ...  # TODO` at L20 is commented out. Fix:
   uncomment and fill `orcid: "https://orcid.org/…"` once Jim's verified iD is
   at hand.
2. **csl-atlas `CITATION.cff` line 21** — Andhrabharati (authors[2],
   alias-only entry): no `orcid:` key at all, and the inline TODO also asks to
   confirm the preferred legal name. Fix both at
   [L21](https://github.com/sanskrit-lexicon/csl-atlas/blob/bbca791/CITATION.cff#L21).
3. **csl-atlas `.zenodo.json` line 9** — creator "Gasūns, Mikhail"
   ([L9](https://github.com/sanskrit-lexicon/csl-atlas/blob/bbca791/.zenodo.json#L9)):
   no `orcid` field. Note the name reads **Mikhail** here vs **Mārcis** in
   CITATION.cff L14 — a pre-existing name discrepancy, flagged not fixed.
4. **csl-atlas `.zenodo.json` line 10** — creator "Funderburk, Jim": no
   `orcid` field; same person as gap 1, use the same verified iD.
5. **csl-atlas `.zenodo.json` line 11** — creator "Andhrabharati": no
   `orcid` field; same person as gap 2.
6. **csl-standards `CITATION.cff` line 6** — Gasūns, Mārcis
   ([L5–6](https://github.com/sanskrit-lexicon/csl-standards/blob/2a0c294/CITATION.cff#L5-L6),
   the repo's only author): no `orcid:` key. Readily fillable from estate
   evidence — the same author carries
   `https://orcid.org/0000-0003-4513-884X` in csl-atlas
   [CITATION.cff L16](https://github.com/sanskrit-lexicon/csl-atlas/blob/bbca791/CITATION.cff#L16),
   VisualDCS [CITATION.cff L13](https://github.com/gasyoun/VisualDCS/blob/6277c8b/CITATION.cff#L13)
   and csl-observatory
   [CITATION.cff L23](https://github.com/sanskrit-lexicon/csl-observatory/blob/3f0d700/CITATION.cff#L23);
   add after L6 on MG's confirmation.

## Third-party reference entry (1, optional)

1. **VisualDCS `CITATION.cff` line 41** — Hellwig, Oliver, author of the
   cited upstream DCS in `references[0]`
   ([L40–41](https://github.com/gasyoun/VisualDCS/blob/6277c8b/CITATION.cff#L40-L41)):
   no `orcid:` key. No iD for him exists anywhere in the estate; fill only
   from his verified ORCID record, never guessed.

## Zero-gap and absent-file observations

1. **csl-observatory: zero missing.** CITATION.cff L23 and .zenodo.json L9
   both carry the iD (URL form / bare `0000-0003-4513-884X`).
2. **VisualDCS main author covered:** Gasūns has the iD at CITATION.cff L13.
3. **`.zenodo.json` absent** in csl-standards and VisualDCS — nothing to
   census there; if either repo ever mints a Zenodo upload, create the file
   with creators carrying `orcid` from the start.

## How this was produced

```
python3 scripts/orcid_gap_census.py     # in csl-atlas; prints the 7 gaps above
```

The script parses both file formats, skips non-person blocks (keywords,
identifiers, `- type:` containers), and reports each person entry's start
line and orcid presence. It never resolves or proposes iDs.

_Гасунс_
