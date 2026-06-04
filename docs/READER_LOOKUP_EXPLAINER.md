# Reader Lookup Explainer

Date: 2026-06-04

Audience: readers, students, translators, and scholars who use Reader Lookup v1
to move from a Sanskrit word to dictionary evidence.

## Trust Block

- Evidence: dictionary headwords, normalized lemma forms, dictionary coverage
  data, source links, and evidence labels.
- Limitations: Reader Lookup v1 is dictionary-first. It is not corpus search,
  sandhi splitting, compound analysis, or a backend search engine.
- Validation: lookup tests must cover exact SLP1, IAST normalization, no-result
  messaging, ambiguous-result messaging, source-link construction, and mobile
  rendering.
- Owner repo: `csl-atlas`.

## What Reader Lookup Answers

Reader Lookup answers a modest but important question:

```text
Which dictionaries have evidence for this headword, and how should I read that evidence?
```

It does not answer whether the word is common in literature, whether it occurs
in a specific passage, or how an inflected form should be analyzed. Those are
corpus or grammar questions and belong outside the current atlas path.

## Result Anatomy

Each lookup result should expose these parts:

| Part | Meaning | Evidence label |
|---|---|---|
| Original query | What the user typed. | `observed` user input |
| Normalized query | The deterministic form used for matching. | `derived` |
| Dictionary coverage | Which dictionaries have a matching headword. | `derived` from dictionary indexes |
| Entry count | How many entries or homonym blocks matched. | `derived` |
| POS/gender | Grammar metadata when reliable. | `observed` or `derived` |
| Source links | Links back to dictionary records. | `observed` source pointer |
| Caveats | Warnings about weak evidence, ambiguity, or missing coverage. | mixed |

## Query States

| State | Reader message | What to do next |
|---|---|---|
| Exact match | The normalized headword exists in one or more dictionaries. | Compare coverage, then open source entries. |
| Multiple matches | More than one entry or normalized candidate is plausible. | Show all candidates and keep the original query visible. |
| Prefix or near match | No exact match, but nearby headwords exist. | Show candidates without pretending they are confirmed. |
| No result | No current dictionary-headword match. | Explain that inflection, sandhi, compounds, or unsupported transliteration may be involved. |

## How It Relates To Dictionary Choice

Use [`DICTIONARY_USER_GUIDE.md`](DICTIONARY_USER_GUIDE.md) first when the
question is "which dictionary should I use?" Use Reader Lookup when the question
is "what evidence exists for this word?"

For a quick lookup:

- start with MW/AP if an English meaning is needed;
- add PWG/PW/PWK for philological depth and citation apparatus;
- add SKD/VCP when traditional Sanskrit-Sanskrit evidence matters;
- treat specialized dictionaries as task-specific evidence, not as general
  absence/presence tests.

## What Not To Infer

Do not infer these claims from Reader Lookup v1:

- a word is absent from Sanskrit because lookup found no result;
- a dictionary has no evidence because one parser missed a convention;
- a word is common because many dictionaries include it;
- a dictionary source citation is a corpus attestation unless the dictionary
  actually cites a source;
- a lexicographer-only entry is equivalent to textual attestation.

## External Boundaries

- Corpus frequency and passage evidence: [VisualDCS](https://github.com/gasyoun/VisualDCS)
- Grammar analysis and inflected-form interpretation: future grammar repo
- TEI/OntoLex/FrAC export: [csl-standards](https://github.com/sanskrit-lexicon/csl-standards)
- GitHub/org activity: [csl-observatory](https://github.com/sanskrit-lexicon/csl-observatory)

## Related Docs

- [`DICTIONARY_USER_GUIDE.md`](DICTIONARY_USER_GUIDE.md)
- [`EVIDENCE_LABELS.md`](EVIDENCE_LABELS.md)
- [`USE_CASES.md`](USE_CASES.md)
- [`CHART_TRUST_TEMPLATE.md`](CHART_TRUST_TEMPLATE.md)
