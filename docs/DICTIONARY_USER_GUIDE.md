# Dictionary User Guide

Date: 2026-05-29

Audience: readers, students, and translators who want to look up a Sanskrit word and understand which dictionary evidence to trust. No knowledge of TEI, OntoLex, Observable, or CDSL internals is required.

This guide answers the question the architecture documents do not answer for a newcomer: **which dictionary should I use, and how do I read what it tells me?**

## Trust Block

- Evidence: dictionary metadata, dictionary records, source links, and the
  comparison outputs used by reader-facing atlas pages.
- Limitations: this guide chooses a first dictionary for a task; it does not
  rank every dictionary globally or use corpus frequency.
- Validation: reader lookup and dictionary-comparison outputs must keep source
  links, evidence labels, and no-result messaging visible.
- Owner repo: `csl-atlas`.

## Start Here

The atlas exposes two entry modes:

- **Reader mode** — look up a word and read dictionary evidence.
- **Research mode** — compare dictionaries, inspect quantitative patterns, and review uncertain data.

If you only want a meaning, stay in reader mode. The research dashboards are linked from there but are never required to read an entry.

A typical lookup moves through this path:

```text
your word -> normalized form -> dictionary entries -> source link -> certainty label
```

You always end at a real dictionary record you can inspect, not at a summary you have to trust blindly.

## Which Dictionary First

There is no single "best" Sanskrit dictionary. Each was built for a different purpose. Use this table as a starting point, not a verdict.

| Dictionary | Language of definitions | Best for | Watch out for |
|---|---|---|---|
| **MW** (Monier-Williams) | English | Broad Sanskrit-English lookup, rich citations, classical and epic vocabulary | Some entries rest only on older lexicons (see "lexicographer-only" below) |
| **AP** (Apte) | English | Practical Sanskrit-English lookup, classical literature, clear glosses | Narrower citation apparatus than MW |
| **PWG** (Großes Petersburger Wörterbuch) | German | The deepest structured lexicographic tradition, dense source citations | Definitions are in German; seven volumes of detail |
| **PWK** (Kürzere Fassung) | German | A compact counterpart to PWG when you want less apparatus | Compresses PWG; German |
| **WIL** (Wilson) | English | Older lexicographic perspective, complementary coverage | Dated scholarship |
| **VCP** | Sanskrit | Traditional Sanskrit-Sanskrit (`iti`-style) definitions | Prose citations, not tagged like MW |
| **SKD** (Śabdakalpadruma) | Sanskrit | Traditional encyclopedic Sanskrit-Sanskrit treatment | Boundary case for the structured model; prose |

Quick rule of thumb:

- **Just need an English meaning?** Start with MW, then check AP.
- **Doing philology or chasing a source citation?** Use MW and PWG together.
- **Working inside the traditional Indian lexicographic frame?** Use VCP and SKD.
- **Comparing how a word is treated across traditions?** Use the multi-dictionary lemma view (research mode).

## Task-Based Starting Points

| Task | Start with | Add next | Why |
|---|---|---|---|
| Fast English meaning | MW | AP | MW is broad; AP is often clearer for practical reading. |
| Citation-heavy philology | PWG + MW | PW/PWK | PWG gives deep apparatus; MW is easier to navigate in English. |
| Traditional Sanskrit-Sanskrit reading | VCP | SKD | These preserve indigenous glossing and citation conventions. |
| Source-citation follow-through | PWG | MW, VCP, SKD | Start where source apparatus is densest, then compare traditions. |
| Grammar or gender check | MW/AP | VCP/SKD when visible | Use visible grammar labels, but watch convention gaps and review status. |
| Historical lexicography | PWG, PWK, WIL | SHS, KOW, AP/MW families | Compare lineage, condensation, and translation/copying patterns. |
| Specialized topic | relevant specialized dictionary | general dictionaries | A specialized dictionary is strong evidence inside its domain, not a general baseline. |

## Dictionary Personalities

The atlas should present dictionaries as different instruments, not as a single
ranked ladder:

- **MW** is the broad English starting point and a major citation hub.
- **AP** is often the most convenient English reader companion.
- **PWG** is the deep apparatus dictionary, especially for source-heavy work.
- **PW/PWK** help distinguish Petersburg depth from later condensation.
- **WIL/SHS/KOW** matter for older English and translation-lineage questions.
- **VCP/SKD** matter when Sanskrit-Sanskrit lexicography is the evidence, not
  merely a supplement.
- **Indexes and specialized dictionaries** answer narrower questions and should
  not be treated as failed general dictionaries.

## What A Dictionary Choice Does Not Prove

A good first dictionary does not settle the word. It only gives a reliable
starting point. Do not infer:

- that no lookup result means the word is absent from Sanskrit;
- that a dictionary with fewer visible tags has weaker content;
- that English definitions are more authoritative than German or Sanskrit
  definitions;
- that `L.` or lexicographer-only evidence is the same as a textual citation;
- that corpus frequency is part of the atlas unless a VisualDCS summary is
  explicitly linked.

## The German Layer Is Evidence, Not Noise

PWG and PWK are written in German because the Petersburg dictionaries are the backbone of modern Sanskrit lexicography. The atlas keeps their German wording intact rather than flattening it into English. If you do not read German, you can still use them for:

- which sources a word is attested in;
- how a word is split into senses;
- grammar information (gender, part of speech).

The interface explanation is bilingual English/Russian; the dictionary content stays in its original language. Do not treat a German entry as lower-quality evidence — it is often the most detailed evidence available.

## How To Read An Entry

A dictionary record carries several kinds of information. The atlas surfaces them consistently:

- **Headword** — the lemma as the dictionary lists it.
- **Grammar** — part of speech and gender (e.g. `m.`, `f.`, `n.`, `mfn.`, `ind.`).
- **Senses** — the numbered or segmented meanings.
- **Citations** — the sources that attest the word (shown as abbreviations such as `RV.`, `MBh.`, or `L.`).
- **Source link** — a link to the exact line in the original `csl-orig` file so you can verify everything yourself.

When you see an abbreviation you do not recognize, the atlas links it to a glossary entry. The most important one to learn early is `L.` — see below.

## The Most Important Caution: `L.` and Lexicographer-Only Words

In MW (and similar dictionaries), a citation of `L.` means **"lexicographers"** — the word is recorded only because earlier dictionaries recorded it, not because it appears in a known text. The atlas calls these **lexicographer-only** entries.

These words are real lexicographic data, but they are *weaker evidence* than a word attested in the Rigveda or the Mahabharata. The atlas marks them visibly so you do not over-trust them. When you see a lexicographer-only warning, treat the word as "attested in the dictionary tradition" rather than "attested in the literature."

## Transliteration

Reader Lookup v1 supports SLP1 and IAST headword input. The atlas normalizes your input, shows the normalized candidate it used, and keeps your original query visible. Harvard-Kyoto, Devanagari, compound splitting, and sandhi recovery are later lookup improvements, not current guarantees.

## When A Lookup Fails

If a word is not found, the current lookup keeps the failure explicit and shows the normalized candidate. Later versions should add:

- suggests transliteration variants;
- suggests a normalized headword;
- suggests likely compound splits or sandhi resolutions;
- shows nearby dictionary forms.

A failed lookup is often a compound or an inflected form, not a missing word.

## Reading Certainty

Every claim in the atlas carries a certainty label. In plain terms:

- **In the source** — printed in the dictionary itself.
- **Computed** — derived by a fixed rule from the source.
- **Probable** — a useful guess that has not been verified.
- **Checked** — confirmed or corrected by a human reviewer.

For the full explanation, see [`docs/EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md).

## Citing What You Find

Each entry has a stable record ID and a source link. When you cite a word in your own work, cite the dictionary, the headword, and the source link rather than the atlas summary, so your reader can verify the original record.

## Related Documents

- [`docs/EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md) — what the certainty labels mean.
- [`docs/READER_LOOKUP_EXPLAINER.md`](READER_LOOKUP_EXPLAINER.md) - what a
  lookup result means and what it does not prove.
- [`docs/USE_CASE_PAGE_ROADMAP.md`](USE_CASE_PAGE_ROADMAP.md) - how reader and
  analysis pages are sequenced.
- [`docs/CHART_TRUST_TEMPLATE.md`](CHART_TRUST_TEMPLATE.md) - the required trust
  block for public pages and charts.
- [`docs/DICTIONARY_COMPARISON_PLAN.md`](DICTIONARY_COMPARISON_PLAN.md) — how cross-dictionary comparison works (research mode).
- `docs/USE_CASES.md` — the reader use cases this guide supports (UC-RD-01 through UC-RD-07).
- `ARCHITECTURE.md` — the overall design and audience policy.
