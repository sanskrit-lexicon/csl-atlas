# Metadoc — L0_GQD_VALIDATION.md

_Created: 26-07-2026 · Last updated: 26-07-2026_

Companion record for [`L0_GQD_VALIDATION.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/L0_GQD_VALIDATION.md).

## Purpose

Gives the L0 convention stemma the one number a reviewer asks for and the layer previously
could not produce: **how much of the documented genealogy does the whole tree recover?**
Everything before it was pairwise (bootstrap support per known edge, nearest-neighbour LOO),
which cannot answer a question about a topology.

## Audience

Reviewers of Paper H §5 / Paper M §4.1.5, and any session that wants to cite the L0 stemma's
accuracy. Not a reader-facing page — the site-facing summary is one sentence in the
`/tools/lexicographic-conventions` trust block.

## Provenance

- Handoff [H1578](https://github.com/gasyoun/Uprava/blob/main/handoffs/H1578-Fable_csl-atlas_l0-gqd-validation_24.07.26.md),
  agenda §6 backlog #8. Executed 26-07-2026 by **Fable 5 (`claude-fable-5`)**.
- Method: Pompei, Loreto & Tria (2011) PLOS ONE 6(6):e20109 eq. 8, as used for tree
  evaluation by Rama, List, Wahle & Jäger (2018), NAACL-HLT (arXiv:1804.05416).
- Generator [`scripts/L0/s7_gqd.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/L0/s7_gqd.py)
  (`--selftest`, 21 checks) · gate
  [`scripts/validate-l0-gqd.mjs`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/validate-l0-gqd.mjs)
  (in `npm run verify`).
- The metric is re-implemented from the published definition rather than taken from a
  package. Deliberate: the L0 stage list already carries `dendropy`/`scikit-bio` in
  `requirements.txt` but neither implements GQD's polytomous-gold normalisation, and the
  handoff's stop condition forbade a black-box surrogate.

## Ranked improvement backlog

1. **B-cubed F1 on the same gold** — the second Rama-et-al. metric, still unimplemented.
   Cheap now that the gold trees are committed, and it scores membership rather than
   quartets, so it fails differently.
2. **A network-aware score.** The headline limitation is structural: five documented edges
   (all tier-A ones into MW) cannot be represented in a tree gold at all, so 0.1456 is a
   floor. A reticulation-aware agreement measure would be the only way to credit them.
3. **Grow the gold.** It resolves 5 groups over 14 of 32 dictionaries. Every dictionary that
   gains a documented parent (csl-atlas#89/#92; KNA/KOW/AMAR entering the L0 matrix) adds
   butterflies and sharpens the estimate.
4. **Remove the containment warrants**, or split the gold into a bibliography-only variant,
   to close the mild circularity that favours the content tree in §4.
5. **Report GQD on the site.** Currently one sentence in a trust block; a small panel on
   `/tools/lexicographic-conventions` showing the ten trees against the null would carry it.

## Limitations to keep visible

- The gold's polytomies are a *choice* (conservative), not ignorance: resolving more of it
  would move the number in an untestable direction. Anyone tempted to "improve" the gold
  should add documented groups only, never plausible ones.
- `A_jaccard_upgma` beats the pre-registered canonical (0.1102 vs 0.1456). This must not be
  used to re-canonicalise — pre-registration is the reason the 0.1456 is credible.
- `canonical_consensus.newick` and `B_whamming_upgma.newick` are byte-identical in the
  committed data, so their rows are not independent evidence.

## Revision history

| date | change | by |
|---|---|---|
| 26-07-2026 | Created with the doc (H1578): method, two gold trees, 12 trees scored, permutation null, per-family recovery, quartet-distance matrix. | Fable 5 (`claude-fable-5`) |

_Dr. Mārcis Gasūns_
