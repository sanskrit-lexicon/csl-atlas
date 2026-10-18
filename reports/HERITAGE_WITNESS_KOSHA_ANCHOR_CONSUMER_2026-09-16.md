# Heritage witness now reads kosha `heritage_anchor` — A17 consumer edge report

_Created: 16-09-2026 · Last updated: 16-09-2026_

Handoff: [H4720](https://github.com/gasyoun/Uprava/blob/main/handoffs/H4720-OxAlpha_csl-atlas_xwalk-a17-kosha-heritage-anchor-witness_14.09.26.md) — census row [A17](https://github.com/gasyoun/Uprava/blob/main/reports/CROSSWALK_CANDIDATE_MAPPINGS_CENSUS_14-09-2026.md) (csl-atlas → kosha heritage_anchor witness anchors, "вторая нога свидетельского слоя Heritage", edge `proposed` since S1 R5 / 27-08-2026, Uprava `interlinks_edges.tsv` row 190).

## What changed

1. `scripts/build-heritage-witness.mjs` — the anchor source is now the sibling
   kosha checkout's `heritage_anchor` table (H345 ingest, 1 row per raw
   `mw_key1`), loaded read-only via `node:sqlite` (`loadKoshaHeritageRows`,
   never throws). The raw SanskritLexicography crosswalk stays as the
   documented fallback when `kosha.db` is absent — CI-safe, since neither
   sibling exists on CI runners and the committed packet is the artifact.
   Packet `schemaVersion` 1.0.0 → 1.1.0; new `sourceLayer` field
   (`kosha.heritage_anchor` | `crosswalk.tsv`); the `.source.json` envelope
   gains `koshaCommit` + `koshaHeritageAnchorRows`.
2. `scripts/validate-heritage-witness.mjs` — new kosha witness-anchoring
   check: packet totals may only under-count kosha raw rows (the normalized
   fold collapses homonyms), and a deterministic ~1-in-N sample (~400 rows) of
   witnessed rows is re-verified value-for-value against the kosha table
   (anchor string + covered flag + tier direction, both directions).
3. `src/data/heritage/heritage_witness.json` + `.source.json` — regenerated
   from the kosha layer.
4. `src/tools/heritage-witness.md` — Chart Trust Block provenance refresh
   (source/validation/next-action/external-dependencies).
5. `test/heritage-witness.test.mjs` — mapping + fold test for
   `koshaRowsToCrosswalkRows`; committed-packet schema pin bumped to 1.1.0.

## What stayed

The join key (normalized SLP1 `normalizeLemma`), the fold semantics
(anchored / covered-no-anchor / absent), the page's rendering, and the
committed-artifact-as-CI-fallback pattern all unchanged. Heritage evidence
remains read-only and never re-derived here.

## Checks

- `npm run build-heritage-witness` — PASS: 194,083 MW headwords; anchor
  source `kosha heritage_anchor (185803 rows)`; heritage covered 25,136
  (13.0%): anchored 24,548, covered-no-anchor 588.
- `npm run validate-heritage-witness` — PASS, including the new line:
  `kosha witness check ran (406 of 25136 witnessed rows sampled against
  185803 kosha heritage_anchor rows; kosha raw covered 25140/anchored 24549)`.
  Packet 25,136/24,548 ≤ kosha raw 25,140/24,549, exactly the fold direction
  the check enforces.
- `npm run verify` (clean-tree full gate: node --test, 12 validators,
  deterministic-regen ×2, build, audit) — run on the PR branch; result
  recorded in the PR description.
- **On our data:** totals unchanged vs the crosswalk-built packet
  (25,136 / 24,548 / 588) — the kosha serving layer and the raw crosswalk
  agree, which is the point of the sample check.

## Risks

- The kosha path is best-effort runtime detection: a future kosha schema
  change to `heritage_anchor` would silently fall back to the crosswalk (by
  design — never throws), so a drift would show as `sourceLayer:
  "crosswalk.tsv"` in the envelope, not as a failure. The validate script's
  kosha check only fires when the sibling exists; CI stays green either way.
- `koshaCommit`/`generatedAt` in the envelope are build-time stamps and
  re-diff on every local regen — known noise for `npm run verify` clean-tree
  checks, same as the pre-existing crosswalkCommit behaviour.

## Inspect

Open `scripts/validate-heritage-witness.mjs` (the kosha sample check, lines
~122–175), then `scripts/build-heritage-witness.mjs` (`loadKoshaHeritageRows`,
`koshaRowsToCrosswalkRows`), then the envelope
`src/data/heritage/heritage_witness.source.json`.

Edge side: Uprava `interlinks_edges.tsv` row 190 flipped `proposed` → `live`
referencing this PR, in the same pass.

_Гасунс_
