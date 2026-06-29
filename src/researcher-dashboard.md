---
title: Researcher dashboard
toc: false
---

# Researcher Dashboard

This is the atlas working surface for M. Gasuns as researcher-builder. It does
not replace `.ai_state.md`; it turns the current journal into a compact public
map of what is actionable, what is blocked, and which adjacent Sanskrit research
repos currently matter to the atlas.

## Trust Block

- Evidence: `.ai_state.md` current queue, atlas review worksheets, generated
  review packets, and cross-repo session journals inspected during planning.
- Limitations: manually summarized v1 dashboard; it does not parse the journal,
  compute queue counts, or import external repo data.
- Validation: linked atlas pages are checked by `npm run build`; status text
  should be refreshed whenever `.ai_state.md` changes materially.
- Owner repo: `csl-atlas`.
- Next use: pick one row, open its source worksheet or repo, and keep the
  resulting decision in `.ai_state.md`.

## Action Surface

| Lane | Current work | Source | Good next move |
|---|---|---|---|
| Human Sanskrit judgment | H4 semantic-field rows left after deterministic auto-triage | [H4 worksheet](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H4_REVIEW_WORKSHEET.md) | Review a small batch by sample type; record decisions before changing generators. |
| Human Sanskrit judgment | Xref shared-core source-check rows left after prefix-control auto-triage | [Xref worksheet](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/XREF_REVIEW_WORKSHEET.md) | Confirm whether exact MW/PWG edges are meaningful or only mechanical overlap. |
| Human action | H5 maker correction `divaraTa -> diviraTa` | [Correction proposal](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/H5_MAKER_CORRECTION_PROPOSAL.md) | Submit to makers; keep source-supported distinct rows out of correction flow. |
| External dependency | Dharmamitra gender and lemma cross-checks are model-pending | [GPU runbook](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DHARMAMITRA_GPU_RUNBOOK.md) | Run pinned local GPU workflow, then rebuild affected queues. |
| Publication tail | P1-P6 are drafted but held for author decisions | [Publications](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/PUBLICATIONS.md) | Decide byline, venue, and missing secondary references before submission work. |

## Cross-Repo Evidence To Watch

<div class="watch-grid">
  <a class="watch-card primary" href="https://github.com/gasyoun/WhitneyRoots">
    <span>Grammar bridge</span>
    <strong>WhitneyRoots</strong>
    <small>Root/class, Whitney grammar sections, MW/Apte senses, DCS frequency, and paradigms can become lemma-dossier context later.</small>
  </a>
  <a class="watch-card" href="https://github.com/gasyoun/VisualDCS">
    <span>Corpus context</span>
    <strong>VisualDCS</strong>
    <small>The 2026 CoNLL-U import and corpus dashboard are relevant only as dictionary-facing lemma context in this atlas.</small>
  </a>
  <a class="watch-card" href="https://github.com/gasyoun/SanskritSpellCheck">
    <span>Correction caution</span>
    <strong>SanskritSpellCheck</strong>
    <small>Typo, wrong-reading, and orthographic-drift findings are ideal teaching material for "do not correct too quickly."</small>
  </a>
  <a class="watch-card" href="https://github.com/sanskrit-lexicon/MWS">
    <span>Source authority</span>
    <strong>MWS</strong>
    <small>Authority records, `ib.`, Register B, and source-link candidates feed atlas citation-trust questions.</small>
  </a>
  <a class="watch-card" href="https://github.com/gasyoun/CommentaryStrategies">
    <span>Teaching contrast</span>
    <strong>CommentaryStrategies</strong>
    <small>Use as examples of how commentary explains differently from dictionaries; do not merge its pipeline into the atlas.</small>
  </a>
  <a class="watch-card" href="https://github.com/sanskrit-lexicon/csl-standards">
    <span>Interoperability</span>
    <strong>csl-standards</strong>
    <small>Keep TEI/OntoLex/loss-report work linked as a research appendix, not as the student front door.</small>
  </a>
</div>

## Working Rules

| Rule | Why it matters |
|---|---|
| Keep `.ai_state.md` authoritative | The dashboard is a readable surface, not a second source of truth. |
| Link out before importing | Adjacent repos stay autonomous unless a dictionary-facing artifact is explicitly contracted. |
| Preserve evidence labels | Student-facing simplification must not hide observed, derived, inferred, or reviewed status. |
| Prefer small review batches | Human Sanskrit judgment is the scarce resource; batch size should make decisions easy to finish. |

## Related Atlas Pages

- [Student Research Desk](research-desk)
- [Student Lesson Track](student-lessons)
- [Evidence Bridges](evidence-bridges)
- [Reader Lookup](tools/reader-lookup)
- [Lemma dossier](tools/dictionary-dossier)
- [H4 semantic fields](tools/h4-review)
- [Cross-reference lineage](tools/xref-lineage)
- [Source-siglum aliases](tools/review-source-siglum)

<style>
.watch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 12px;
  margin: 16px 0 22px;
}
.watch-card {
  display: grid;
  gap: 7px;
  min-height: 142px;
  border: 1px solid color-mix(in srgb, var(--theme-foreground), transparent 82%);
  border-radius: 8px;
  padding: 14px;
  text-decoration: none;
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%);
}
.watch-card:hover {
  border-color: color-mix(in srgb, var(--theme-foreground), transparent 55%);
}
.watch-card.primary {
  background: color-mix(in srgb, var(--theme-background), #2f6f9f 11%);
}
.watch-card span {
  color: var(--theme-foreground-muted);
  font-size: .82rem;
  text-transform: uppercase;
}
.watch-card strong {
  color: var(--theme-foreground);
  font-size: 1.05rem;
}
.watch-card small {
  color: var(--theme-foreground-muted);
  line-height: 1.35;
}
</style>
