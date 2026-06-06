---
title: Which dictionary should I use?
toc: false
---

# Which Dictionary Should I Use?

Start with **MW** unless you already know why another dictionary fits your
task better. MW is the public default because it is broad, English-facing,
well linked in the atlas, and usually the fastest path from a headword to a
usable dictionary record.

## Trust Block

- Evidence: dictionary metadata, Reader Lookup v1 coverage, public dictionary
  pages, source links, and documented comparison outputs.
- Limitations: this page chooses a first stop for dictionary evidence. It does
  not rank dictionaries globally, translate entries, or use corpus frequency.
- Validation: kept consistent with Reader Lookup v1, dictionary pages, and
  `docs/UC_RD_02_DICTIONARY_CHOOSER.md`; checked by `npm run build`.
- Owner repo: `csl-atlas`.
- Next use: open MW first, then use the task table below to decide whether a
  second dictionary should verify, clarify, or challenge the MW result.

## Default Path

```text
word -> MW -> source link -> second dictionary if the task needs one
```

Use MW first for ordinary lookup, translation support, and public reading. Then
choose the second dictionary by the job you are doing:

<div class="decision-cards">
  <a class="decision-card primary" href="/dicts/mw">
    <span>Default</span>
    <strong>Open MW first</strong>
    <small>Broad English lookup, source links, and the fastest public route from headword to record.</small>
  </a>
  <a class="decision-card" href="/dicts/ap">
    <span>Meaning</span>
    <strong>Then AP</strong>
    <small>Use AP when the MW entry is long and you need a compact reader-facing English gloss.</small>
  </a>
  <a class="decision-card" href="/dicts/pwg">
    <span>Source trail</span>
    <strong>Then PWG/PWK</strong>
    <small>Use the Petersburg dictionaries when MW compresses citations, variants, or nested structure.</small>
  </a>
  <a class="decision-card" href="/dicts/vcp">
    <span>Sanskrit frame</span>
    <strong>Then VCP/SKD</strong>
    <small>Use Sanskrit-Sanskrit dictionaries when indigenous glossing and authority conventions matter.</small>
  </a>
  <a class="decision-card" href="/dicts/wil">
    <span>Older wording</span>
    <strong>Then WIL</strong>
    <small>Use Wilson-line evidence when older English wording or translation inheritance matters.</small>
  </a>
  <a class="decision-card" href="/tools/reader-lookup">
    <span>Compare</span>
    <strong>Then Reader Lookup</strong>
    <small>Use coverage and source links when you need to compare dictionary records side by side.</small>
  </a>
</div>

| Your task | Start | Then open | Why the second step matters |
|---|---|---|---|
| I need a quick English meaning. | MW | AP | AP is often shorter and clearer for reading after MW gives breadth. |
| I need the source trail behind a word. | MW | PWG or PWK | PWG/PWK can show dense citations, variants, and nested detail that MW may compress. |
| I need a traditional Sanskrit explanation. | MW | VCP or SKD | VCP/SKD preserve Sanskrit-Sanskrit glossing and authority conventions. |
| I need to check grammar or gender. | MW | AP, VCP, or SKD | Grammar labels differ by convention; compare before trusting one label. |
| I am studying older English dictionary wording. | MW | WIL | WIL helps reveal older English translation choices and Wilson-line inheritance. |
| I am working in a narrow domain. | MW | The specialized dictionary for that domain | Specialized dictionaries are strong inside their scope, weak as general baselines. |
| I need to compare several dictionaries. | Reader Lookup | Lemma dossier | Start with coverage, then inspect exact source-linked records. |

## Why Not Say "Use PWG For Lineage"?

For a reader who does not know Sanskrit lexicographic history, "Petersburg
lineage" is not an action. The useful reason to open PWG or PWK is practical:
they often keep a fuller source apparatus, more nested preverb/derivative
structure, and German definitions that preserve distinctions flattened by a
later English lookup path.

So the public instruction is:

```text
Use PWG/PWK when you need evidence trail, variants, or structural detail.
```

That is different from asking the reader to care about lineage before they know
what problem they are solving.

## What A First Dictionary Does Not Prove

- A missing result is not proof that a word is absent from Sanskrit.
- MW being the default does not make English evidence stronger than German or
  Sanskrit evidence.
- A low-tag dictionary can still contain rich prose evidence.
- Dictionary evidence is not corpus attestation.
- Machine-derived labels remain machine-derived unless a review page says
  otherwise.

## Next Actions

| If you see this | Do next |
|---|---|
| MW has a clear result and source link. | Use it, then cite the dictionary record rather than the atlas summary. |
| MW has only `L.` or lexicographer-only evidence. | Treat it as dictionary-tradition evidence and compare PWG/VCP/SKD. |
| MW has many senses. | Open PWG/PWK or the lemma dossier before choosing one sense. |
| MW has no result. | Try Reader Lookup prefix matches, AP, WIL, or a specialized dictionary. |
| VCP/SKD disagree with MW/AP. | Keep both conventions visible; this is not automatically an error. |

## Boundary

This page belongs to `csl-atlas` because every route starts from dictionary
choice, dictionary records, and dictionary source links.

It does not own DCS passage frequency, standards export, GitHub activity, or
grammar analysis outside dictionary records.

## Related

- [Reader Lookup](/tools/reader-lookup)
- [MW](/dicts/mw)
- [AP](/dicts/ap)
- [PWG](/dicts/pwg)
- [PWK](/dicts/pwk)
- [VCP](/dicts/vcp)
- [SKD](/dicts/skd)

<style>
.decision-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin: 16px 0 22px;
}
.decision-card {
  display: grid;
  gap: 6px;
  min-height: 132px;
  border: 1px solid color-mix(in srgb, var(--theme-foreground), transparent 82%);
  border-radius: 8px;
  padding: 14px;
  text-decoration: none;
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%);
}
.decision-card:hover {
  border-color: color-mix(in srgb, var(--theme-foreground), transparent 55%);
}
.decision-card.primary {
  background: color-mix(in srgb, var(--theme-background), #2f6f9f 11%);
}
.decision-card span {
  color: var(--theme-foreground-muted);
  font-size: .82rem;
  text-transform: uppercase;
}
.decision-card strong {
  color: var(--theme-foreground);
  font-size: 1.06rem;
}
.decision-card small {
  color: var(--theme-foreground-muted);
  line-height: 1.35;
}
</style>
