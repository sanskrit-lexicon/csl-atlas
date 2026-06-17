# Measuring the Dictionary Family: A Traceable Measurement Framework for Computational Lexicography (P1)

**Status:** scope + working scaffold (2026-06-16). The foundational methods paper of the atlas P-series; P2–P6 each instantiate one or two of its metrics. This file defines the paper's scope, contribution, evidence base, and section plan — it is not yet a full draft.

**Target venue (proposed):** *Digital Scholarship in the Humanities* (DSH/LLC, Oxford) primary; *International Journal of Lexicography* methods note as alternate. (P3 *Three Axes of Descent* targets the same DH/lexicography-methods family; P1 sits one level above it.)

---

## 1. Why this paper, and why here

The Cologne Digital Sanskrit Lexicons are 40+ dictionaries that quote, copy, condense, and reorganise one another across 1822–1957. The atlas measures those relationships with a recurring toolkit — lemma overlap, sense-granularity ratios, citation-register resolvability, structural-register coordinates, cross-reference graph overlap, root-parser agreement, redundancy collapse — and surfaces every result under a fixed evidence discipline (claim → evidence → source).

P2–P6 each *use* that toolkit but none *defines* it. P1 is the missing spine: it states the measurement framework once, as a reusable methodology for any DH project with a family of related sources, with CDSL as the worked case.

**Boundary (decisive).** This is **not** the legacy "Quantifying digital lexicography / Paper M" KPI-catalog paper. That paper "quantifies the *project*" (repository health, contributor/issue/PR/workflow KPIs) and belongs to [`csl-observatory`](../BOUNDARY_RULES.md); its cross-repo draft was retired to [`article_1_methods_LEGACY_CROSS_REPO_METHODS.md`](article_1_methods_LEGACY_CROSS_REPO_METHODS.md) precisely because it mixed scopes. P1 quantifies the **dictionaries**, never the project. The L0–L10 data-richness typology (which conditions every measurement) is cross-referenced, not absorbed.

## 2. Contribution

A three-layer measurement framework for a digital dictionary family:

1. **Metric layer** — operational definitions of the atlas's dictionary metrics, each defined once and reused by the finding papers (see the catalog in §4).
2. **Traceability/epistemics layer** — the discipline that makes each metric citable and falsifiable: the dataset envelope, evidence levels, page-level trust blocks, the deterministic-build rule, and the human review gate (§5).
3. **Routing/boundary layer** — one-owner hypothesis routing and the containment-is-a-floor / negative-results-retained rules that prevent overclaiming (§6).

The claim is methodological: *given a family of related digital dictionaries, these metrics + this traceability discipline yield reproducible, falsifiable descent and structure evidence* — demonstrated, not asserted, by the P2–P6 results.

## 3. Related work (to populate)

- Computational/quantitative lexicography and metalexicography (Wiegand HSK; Atkins & Rundell); Zgusta on dictionary copying.
- Stemmatics / phylogenetic methods for textual descent (shared with P3/P5 — reuse those references).
- FAIR data + provenance (PROV-O) and reproducibility in DH; the trust-block / evidence-label idea vs. existing data-statement practice.
- `[author to add]` a measurement-framework / KPI-in-DH reference to position against (without crossing into the observatory's project-KPI scope).

## 4. Metric layer — the catalog (each row already implemented)

Every metric below has a generator, a data artifact, and at least one finding in [`HYPOTHESIS_INDEX.md`](../HYPOTHESIS_INDEX.md). P1 formalises the definition; the cited paper supplies the worked result.

| Metric | Definition (one-line) | Generator / artifact | Finding · companion paper |
|---|---|---|---|
| Lemma overlap (Jaccard, directed containment) | shared-headword fraction between two dicts; containment as a descent *floor* | `data/sanhw1_jaccard.csv`; `scripts/obs/headword_multiplicity.py` | OBS-R · P-Redundancy |
| Redundancy / entry→lemma collapse | corpus entry count ÷ distinct lemmas; per-dict unique% | `CORPUS_REDUNDANCY_GENEALOGY.md` | OBS-R · P-Redundancy |
| Sense granularity & survival | senses per lemma; cited-vs-uncited ancestor-sense survival under controls | `r2_h1*.json`, `r2_h2h3.json`; `scripts/build-r2-*.mjs` | H1R/H2/H3R · P2 |
| Citation registers & `<ls>` resolvability | European `<ls>` vs indigenous `iti`; % resolvable to a source | `CITATION_REGISTERS.md`; `scripts/lib/source-siglum.mjs` | OBS-C/INDIG-CITE · P-Registers |
| Structural register | citation-style × grammar-marking coordinates that separate families | `data/lexico/structural_register*.json`; `/tools/structural-register` | H6 · P3 |
| Cross-reference graph overlap | shared directed `<ls>`/xref edges; hubs as convention artifacts | `xref_lineage.json`, `xref_edges.csv`; `/tools/xref-lineage` | XREF-CORE · P5 |
| Microstructure fingerprint | macro/micro trade-off (headword promotion vs nesting) | `microstructure_fingerprint.json`; `MICROSTRUCTURE_M1_M2_RESULTS.md` | M1-M2-MACRO · P3/P4 |
| Root-parser agreement | independent indigenous-root parsers agreeing on gaṇa/pada/transitivity | `root_agreement.json`; `MICROSTRUCTURE_ROOT_AGREEMENT.md` | M7-ROOT-AGREE · P4 |
| Semantic-field coverage | Amarakośa-native varga coverage per dictionary | `data/lexico/semantic_field_family_profiles.json`; `/tools/semantic-fields` | H4 · P-Semantic |
| Citation-link resolvability | explicit-locus citations → stable digital-edition URL (DTB) | `scripts/build-citation-link-pilot.mjs`; `rv-verse-counts.json` | DTB pilot · Dharmamitra layer |

## 5. Traceability / epistemics layer

The mechanisms that make each metric above publishable and re-checkable — all already enforced in the repo:

- **Dataset envelope** — every generated dataset carries `schemaVersion`, `generatedAt`, `license`, `assumptions`, `warnings` ([`scripts/lib/review-report.mjs`](../../scripts/lib/review-report.mjs), [`scripts/lib/dataset-meta.mjs`](../../scripts/lib/dataset-meta.mjs); [`ARCHITECTURE.md`](../../ARCHITECTURE.md)).
- **Evidence levels** — `derived` (deterministic parse) vs `model-pending` (NLP cross-check, never a build input) vs `reviewed` (human-ratified). Demonstrates the rule that *no model inference runs in `npm run build`*.
- **Trust blocks** — every Observable page states what the number is, its panel/threshold limits, and what it is *not*.
- **Human review gate** — proposals are written to review queues conforming to [`data/schema/review-report.schema.json`](../../data/schema/review-report.schema.json), preserved by `reviewId` across rebuilds; the atlas proposes, a human ratifies before anything is written back to `csl-orig`.

This layer is the paper's most transferable contribution: a concrete, low-ceremony alternative to ad-hoc DH data releases.

## 6. Routing / boundary layer

- **One-owner routing** — [`HYPOTHESIS_INDEX.md`](../HYPOTHESIS_INDEX.md) assigns each claim exactly one repo; [`BOUNDARY_RULES.md`](../BOUNDARY_RULES.md) keeps corpus/standards/project claims out.
- **Anti-overclaim rules** — containment is a *floor* for relatedness, not proof of copying; refuted hypotheses (H1→H1R, H3→H3R) stay visible as findings; thresholds and panels are stated as bounds.

## 7. Worked example (structure)

One end-to-end trace through the framework: pick a single inheritance edge (e.g. AP90→AP, the edition-continuity positive control) and show every layer firing — overlap floor → sense survival → citation register → xref control → trust block → review row — producing one falsifiable, fully sourced descent statement.

## 8. Relationship to the P-series

P1 is the methods spine; P3 (*Three Axes of Descent*) is its closest companion but is a **subset** (three specific descent axes). P2/P4/P5/P6 are single-metric or single-structure instantiations. The paper should forward-reference each as the worked demonstration of a framework component, and avoid re-deriving their results.

## 9. Open author decisions

- Title and venue (DSH primary vs IJL methods note).
- Byline (consistent with P2–P6).
- How much to formalise each metric in-paper vs delegate to the companion paper (recommend: define + give the estimator, delegate the full result).
- Related-work `[author to add]` items in §3.
- Whether the worked example (§7) is AP90→AP or a cross-tradition edge (MW×PWG shared core) for a harder demonstration.

## 10. What's needed to move from scope to draft

1. Lift each §4 metric's exact estimator from its generator into a uniform "Definition / Input / Estimator / Output / Limits" box.
2. Write §5 from the envelope + schema as-built (no new code).
3. Draft §7 by running the existing builders for the chosen edge and transcribing the trace.
4. Fill §3 related work; reuse P3/P5 stemmatics references.
5. Register in [`PUBLICATIONS.md`](../PUBLICATIONS.md) (done) and add a P1 row to [`HYPOTHESIS_INDEX.md`](../HYPOTHESIS_INDEX.md) as the methods anchor.

No new data or external dependency is required to draft P1 — every input already exists in the repo.
