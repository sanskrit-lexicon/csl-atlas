# kosha heritage_anchor is now the atlas heritage-witness anchor source (H4720, A17 edge live)

`build-heritage-witness` reads the sibling kosha `heritage_anchor` table
(read-only `node:sqlite`) with the raw SanskritLexicography crosswalk kept as
the CI-safe fallback; `validate-heritage-witness` re-verifies a deterministic
~400-row sample of witnessed rows value-for-value against kosha. Packet
schemaVersion 1.1.0 with `sourceLayer` + kosha provenance in the envelope;
page trust block refreshed. Totals unchanged (25,136 covered / 24,548
anchored) — serving layer and upstream crosswalk agree. Uprava
`interlinks_edges.tsv` row 190 (csl-atlas→kosha heritage_anchor witness
anchors) flipped proposed→live.
