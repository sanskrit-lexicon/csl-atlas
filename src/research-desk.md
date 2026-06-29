---
title: Student research desk
toc: false
---

# Student Research Desk

Use this page when you have a Sanskrit word and want a reliable path from
lookup to evidence. The goal is not to pick one dictionary forever; it is to
learn which record answers today's question, what the record proves, and what
still needs checking.

## Trust Block

- Evidence: public atlas lookup pages, dictionary chooser guidance, source-linked
  dossier data, and reader-facing evidence-label documentation.
- Limitations: route map and lesson surface only; it does not add new dictionary
  data, grammar analysis, corpus counts, or translations.
- Validation: all linked atlas routes are checked by `npm run build`; page text
  is kept aligned with Reader Lookup and the dictionary chooser.
- Owner repo: `csl-atlas`.
- Next use: choose a word, follow the five-step path, then cite the dictionary
  record rather than this page.

## One-Word Workflow

<div class="path-grid">
  <a class="path-card primary" href="dictionary-chooser">
    <span>1</span>
    <strong>Choose the first dictionary</strong>
    <small>Start with MW unless your task needs compact English, source trails, or Sanskrit-Sanskrit explanation.</small>
  </a>
  <a class="path-card" href="tools/reader-lookup">
    <span>2</span>
    <strong>Look up the headword</strong>
    <small>Try IAST or SLP1. If exact lookup fails, inspect prefix matches before deciding the word is absent.</small>
  </a>
  <a class="path-card" href="tools/dictionary-dossier">
    <span>3</span>
    <strong>Open the lemma dossier</strong>
    <small>Compare coverage, source links, gender/POS signals, and DCS frequency chips where available.</small>
  </a>
  <a class="path-card" href="tools/dictionary-citations">
    <span>4</span>
    <strong>Check the evidence trail</strong>
    <small>Use citation apparatus and dictionary pages when the question depends on sources, not only glosses.</small>
  </a>
  <a class="path-card" href="https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/EVIDENCE_LABELS.md">
    <span>5</span>
    <strong>Name the certainty</strong>
    <small>Keep observed, derived, inferred, and reviewed evidence visibly separate in your notes.</small>
  </a>
</div>

## What To Do Next

| If your lookup shows... | Do this | Why |
|---|---|---|
| A clear MW result with a source link | Read MW, then compare AP if you need a shorter English gloss | MW gives breadth; AP often helps students choose a usable first sense. |
| Many senses or nested compounds | Open the dossier and compare PWG/PWK | Petersburg records often preserve distinctions hidden by a quick English lookup. |
| `L.` or lexicographer-only evidence | Compare PWG, VCP, SKD, or the citation apparatus | This is dictionary-tradition evidence, not direct corpus attestation. |
| Sanskrit-Sanskrit disagreement | Keep both conventions visible | VCP/SKD may organize meaning differently from English dictionaries. |
| No exact hit | Try prefix lookup, variant spelling, and a broader dictionary | Absence from one index is not absence from Sanskrit. |

## Short Exercises

Use these as 10-minute classroom or self-study prompts. Each exercise should end
with one cited dictionary record and one sentence about evidence level.

| Word | Task | Route |
|---|---|---|
| `dharma` | Compare a familiar word across English and Sanskrit-Sanskrit dictionaries. | Reader Lookup -> Lemma dossier -> VCP/SKD. |
| `agni` | Find a quick reading gloss, then inspect whether source evidence changes your confidence. | Dictionary chooser -> MW -> AP -> citation tools. |
| `gam` | Notice why verbal/root evidence is not the same as a simple noun lookup. | Reader Lookup -> dossier -> R2 sense explorer. |
| `rAma` | Compare coverage and source links without assuming all dictionaries use the same scope. | Reader Lookup -> dossier -> dictionary pages. |
| `mokza` | Practice input schemes and spelling discipline by comparing SLP1 and IAST. | Reader Lookup -> evidence labels -> source record. |

## Related Study Paths

- [Student Lesson Track](student-lessons)
- [Evidence Bridges](evidence-bridges)
- [Which dictionary should I use?](dictionary-chooser)
- [Reader Lookup](tools/reader-lookup)
- [Lemma dossier](tools/dictionary-dossier)
- [Learner's reading layer](tools/learner-reading-layer)
- [Dictionary user guide](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/DICTIONARY_USER_GUIDE.md)
- [csl-guides learning track](https://sanskrit-lexicon.github.io/csl-guides/)

<style>
.path-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 12px;
  margin: 16px 0 22px;
}
.path-card {
  display: grid;
  grid-template-rows: auto auto 1fr;
  gap: 7px;
  min-height: 150px;
  border: 1px solid color-mix(in srgb, var(--theme-foreground), transparent 82%);
  border-radius: 8px;
  padding: 14px;
  text-decoration: none;
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%);
}
.path-card:hover {
  border-color: color-mix(in srgb, var(--theme-foreground), transparent 55%);
}
.path-card.primary {
  background: color-mix(in srgb, var(--theme-background), #2f6f9f 11%);
}
.path-card span {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: var(--theme-background);
  background: color-mix(in srgb, var(--theme-foreground), transparent 18%);
  font-weight: 700;
}
.path-card strong {
  color: var(--theme-foreground);
  font-size: 1.05rem;
}
.path-card small {
  color: var(--theme-foreground-muted);
  line-height: 1.35;
}
</style>
