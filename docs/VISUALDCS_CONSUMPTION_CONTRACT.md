_Created: 09-06-2026 · Last updated: 05-09-2026_

# VisualDCS Consumption Contract

Date: 2026-06-09

Status: input requirement for VisualDCS. Defines the single, stable,
dictionary-facing summary that `csl-atlas` may consume from
[`VisualDCS`](https://github.com/gasyoun/VisualDCS) without importing corpus
scope. This is a **specification of what the atlas needs**, not an
implementation; VisualDCS owns production of the file.

## Why this document exists

[`BOUNDARY_RULES.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/BOUNDARY_RULES.md) keeps DCS corpus data, passage
evidence, corpus grammar, and dictionary-vs-corpus joins **out** of the atlas
and assigns them to VisualDCS. The same rules allow the atlas to *consume* a
stable dictionary-facing summary later
([`RESEARCH_LAYER_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/RESEARCH_LAYER_ROADMAP.md) §7, phase R5).

Today no such summary exists: VisualDCS's published JSON
(`morph_pn.json`, `tense_case_data.json`, …) is keyed by grammatical **category
codes** (`tc24`, person/number/voice tallies), not by SLP1 **headword**. There
is therefore nothing the atlas can join against. This contract specifies the
missing file so VisualDCS can produce it and the atlas can wire to it under a
clear boundary.

## Direction of dependency (one way, lossy on purpose)

```
VisualDCS  ──(emits)──>  dcs_lemma_summary.json  ──(atlas consumes, read-only)──>  csl-atlas
   owns corpus,              compact, headword-keyed,        joins on SLP1 headword;
   passages, grammar         frequency bands only            never stores passages
```

The atlas **consumes** the summary as an optional enrichment column on
dictionary headword/lemma pages. The atlas **never**:

- ingests DCS passages, concordances, or token rows;
- recomputes corpus frequencies;
- builds corpus dashboards, chronology, or grammar tables;
- treats absence of the file as an error (the file is an optional enrichment).

If a page would need any of the above, it belongs in VisualDCS, not here.

## Join key

The atlas keys every dictionary entry on the **SLP1 `<k1>` headword**,
normalized by `scripts/lib/dict-normalize.mjs` `normalizeLemma()`:

- accents stripped (`/`, `\`, `^`, `~`);
- trailing homonym digits stripped;
- SLP1 **case preserved** (phonemic — never lowercase, never transliterate).

VisualDCS must key the summary on the **same normalized SLP1 form**.

**Patel-convention variants are the atlas's responsibility, not VisualDCS's.**
The atlas already resolves doubled-`r`, inflected-visarga, and homonym variants
(e.g. `Darma` / `Darmma` / `DarmaH` / `DarmmaH`) onto one canonical lemma in its
anchor/resolver layer. VisualDCS should emit **one row per canonical normalized
SLP1 lemma**; the atlas maps its own variants onto that key. If a lemma is
genuinely ambiguous in SLP1, VisualDCS may suffix a homonym index and document
it, but should prefer the bare normalized form.

## Required summary schema

A single JSON object keyed by normalized SLP1 headword. Each value is a compact,
**band-level** record — no raw counts that would re-import corpus scope, no
passage text.

```jsonc
{
  "schemaVersion": "1.0.0",
  "generatedBy": "VisualDCS",          // provenance string
  "corpusRelease": "DCS-2021",         // which DCS dump this summarizes
  "generatedAt": "2026-06-09",
  "lemmas": {
    "gam": {
      "freqBand": 5,                   // 1..5 coarse frequency band (see below)
      "attested": true,               // appears in DCS at all
      "formCount": 144,               // distinct attested morphological forms (optional)
      "firstAttestationEra": "vedic"  // coarse era label, optional, enum below
    },
    "Darma": { "freqBand": 5, "attested": true, "formCount": 61 },
    "boDisattva": { "freqBand": 2, "attested": true, "formCount": 7 }
    // ... one row per canonical normalized SLP1 lemma that is attested ...
  }
}
```

| Field | Type | Required | Meaning |
|---|---|---|---|
| `freqBand` | int 1–5 | yes | Coarse corpus-frequency band (1 = rare … 5 = very common). Bands, not raw counts, keep corpus scope out of the atlas. |
| `attested` | bool | yes | Whether the lemma appears in the DCS corpus at all. Lemmas absent from the corpus may be omitted entirely (treated as `attested:false`). |
| `formCount` | int | optional | Number of distinct attested morphological forms; a learner-facing "how varied is this lemma in use" signal. |
| `firstAttestationEra` | enum | optional | Coarse era: `vedic`, `epic`, `classical`, `late`, `unknown`. Era, not date — chronology detail stays in VisualDCS. |

**Banding rule (VisualDCS-side, documented in VisualDCS):** map raw corpus
frequency to 1–5 by a fixed, published rule (e.g. log-quantile). The atlas
displays the band and links to VisualDCS for the underlying numbers; it does not
store or recompute them.

## Format and size budget

- **One file**, UTF-8, no BOM, committed in VisualDCS and fetchable by URL.
- **Headword-keyed object** (above), so the atlas can `O(1)` look up a lemma.
- **Size budget: ≤ ~10 MB uncompressed**, matching the existing client-side
  `sanhw1` index that already loads in-browser
  ([`RESEARCH_LAYER_ROADMAP.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/RESEARCH_LAYER_ROADMAP.md) §7). Band-level
  records for ~55k attested lemmas fit comfortably. If it grows past budget,
  shard by first letter and publish a manifest.
- **Versioned**: bump `schemaVersion` on any breaking field change; the atlas
  pins a compatible major version.

## Out of scope (must NOT appear in the summary)

- Passage text, citations, concordance rows, or token-level data.
- Per-text or per-century frequency breakdowns (chronology lives in VisualDCS).
- Grammar paradigms, tense/case/voice tallies (those are VisualDCS dashboards).
- Any GitHub/repo/tooling metric.
- Raw corpus counts beyond the optional `formCount` (use bands).

## Atlas-side adapter (when the file exists)

When VisualDCS publishes `dcs_lemma_summary.json`, the atlas wires it as an
**optional, read-only enrichment** behind a feature flag:

1. A loader (`scripts/lib/dcs-summary.mjs`) fetches/reads the pinned file, or
   returns an empty map if absent — never throws, never blocks a build.
2. Entry/lemma pages show a small "corpus frequency: band N · _N_ forms ·
   _era_ — see VisualDCS" chip that **links out** to the VisualDCS dashboard for
   the underlying numbers.
3. A unit test asserts: missing file → empty map (graceful); present file →
   join hits known anchors (`gam`, `Darma`, `boDisattva`); no passage/grammar
   field is ever read.

Until the file exists, the atlas keeps a **plain external hyperlink** to
VisualDCS (allowed today by `BOUNDARY_RULES.md` "External Links Are Allowed").

## Acceptance gates (before the atlas wires the join)

| Gate | Expected evidence |
|---|---|
| Contract published | VisualDCS emits `dcs_lemma_summary.json` matching this schema, with a documented banding rule. |
| Join key matches | Keys are normalized SLP1; anchor lemmas `gam`, `Darma`, `rAma`, `iti`, `boDisattva` resolve from the atlas side. |
| Boundary preserved | No passage/chronology/grammar/raw-count field present; atlas reads only band-level fields. |
| Graceful absence | Atlas builds and pages render with the file missing (enrichment is optional). |
| Size budget | File ≤ ~10 MB or sharded with a manifest. |

## Next actions

1. **VisualDCS** (external): produce `dcs_lemma_summary.json` per this schema
   and document the banding rule. Tracked outside this repo.
2. **csl-atlas** (here, deferred until 1 lands): add the optional read-only
   adapter + feature-flagged chip + tests; keep the external hyperlink in the
   meantime.

This document is the handoff. It is in-bounds for the atlas because it describes
a **dictionary-headword join requirement**, not corpus scope; the corpus work it
asks for stays in VisualDCS.

_Dr. Mārcis Gasūns_
