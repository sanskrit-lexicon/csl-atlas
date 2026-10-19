_Created: 19-10-2026 · Last updated: 19-10-2026_

# Release candidate — csl-atlas core dossier v1.0.0 / repo v0.20.0

Status: **RELEASE CANDIDATE, NOT PUBLISHED.** This note records exactly what is
ready, what is blocked, and how to finish the release without minting a fake
DOI.

## What is frozen

| Item | Value |
|---|---|
| Dataset | `src/data/dicts/core-dossier/` |
| Dataset version | 1.0.0 |
| Release tag | `v0.20.0` (not yet created) |
| Frozen data revision | [`12bd3d1`](https://github.com/sanskrit-lexicon/csl-atlas/commit/12bd3d1c7e698d9c508267ceac4ac2b834db1f88) |
| csl-orig revision | `f4c08c578b330e2379e38f54d3a541f1564b8eee` |
| Records | 28,524 lemmas |
| Provenance sidecar | `src/data/dicts/core-dossier/.source.json` |
| Payload tree SHA-256 | `5d88357ed16fb27f15a580e904bdd910d457d13d3a1e953788743dc2d5d9aa80` |
| Licence | CC BY-SA 4.0 |

## Release payload

- `docs/ONTOLEX_PROFILE_CORE_DOSSIER.md` — field mapping, worked `iti` example,
  no-equivalent list.
- `docs/DATA_STATEMENT_CORE_DOSSIER.md` — motivation, provenance, licence,
  limitations, maintenance, review split.
- `src/data/dicts/core-dossier/.source.json` — input/output hashes and pinned
  revisions.
- `src/data/dicts/core-dossier/README.md` — dataset-level citation block.
- `README.md` and `src/index.md` — "Cite this dataset" blocks.
- `CITATION.cff` and `.zenodo.json` — version `0.20.0`, date 2026-10-19,
  concept DOI unchanged.
- `docs/DATASET_LICENCE_MATRIX.md` — core-dossier row added.
- `csl-standards` issue — one-line pointer naming the normative exporter owner.

## DOI status

- **Concept DOI:** [`10.5281/zenodo.21419691`](https://doi.org/10.5281/zenodo.21419691)
  — verified on 2026-10-19: `curl -I https://doi.org/10.5281/zenodo.21419691`
  returned HTTP/2 302 to `https://zenodo.org/doi/10.5281/zenodo.21419691`.
- **Version DOI for v0.20.0:** **not minted.** Zenodo mints a version DOI when
  a GitHub release is published from the repository's default branch. The
  H7102 change is a product-repo PR; org standing rules require a human to
  merge it, and this worktree cannot publish a release from an unmerged branch.

Do **not** mint a DOI manually, do **not** tag a non-merged commit, and do
**not** claim a version DOI in `CITATION.cff`, `.zenodo.json`, the README, or
the landing page until Zenodo returns one.

## Exact blocker

Product repo (`sanskrit-lexicon/csl-atlas`) merge policy: handoff-scoped work
ships as a PR, and `gh_merge` refuses product repos. Zenodo is connected, but
it releases only from the default branch. The only missing external act is a
human merge of the H7102 PR and publication of `v0.20.0`.

## Post-merge steps (for the human or a follow-up handoff)

```bash
# 1. Merge the H7102 PR to main.
# 2. Check out the merged main commit.
git checkout main
git pull --ff-only origin main
git log -1 --format='%H %cI'

# 3. Tag and publish.
git tag -a v0.20.0 -m "csl-atlas v0.20.0 — core dossier dataset 1.0.0"
git push origin v0.20.0
gh release create v0.20.0 \
  --title "csl-atlas v0.20.0 — core dossier dataset 1.0.0" \
  --notes-file docs/RELEASE_CANDIDATE_CORE_DOSSIER.md

# 4. Zenodo mints the version DOI. Read it from the Zenodo record, then:
curl -sI "https://doi.org/10.5281/zenodo.<version>" | head

# 5. Add the version DOI to CITATION.cff, .zenodo.json, README.md, and
#    src/index.md in a small follow-up PR; do not guess it.
```

## Verification before merge

1. `curl -I https://doi.org/10.5281/zenodo.21419691` returns 200/302.
2. `git show 12bd3d1 -- src/data/dicts/core-dossier/manifest.json` confirms the
   frozen data revision.
3. Recompute `.source.json` hashes with the commands in the profile §8.
4. Open `docs/ONTOLEX_PROFILE_CORE_DOSSIER.md` §7 and confirm the `iti` tuple
   matches `shards/69.json` exactly.
5. Confirm the profile names the no-equivalent fields (sense text, coverage
   count, record count, composite grammar tokens, source-line citation,
   transliteration, entry identity).
6. Confirm `docs/DATA_STATEMENT_CORE_DOSSIER.md` and the README citation block
   are present in the PR diff.

## Risks

- The dataset has no sense rows; an exporter must not fabricate
  `ontolex:Sense` from it. The profile makes this explicit.
- Zenodo's concept DOI currently resolves to the latest release (0.19.x until
  v0.20.0 is published). A reader who follows it before the release sees the
  previous version; the README says so.
- `package.json` version is `0.18.0`, while release tags are `0.19.x` and this
  candidate is `0.20.0`. The release metadata is tag-driven; bumping
  `package.json` is out of H7102 scope and should not block the tag.
