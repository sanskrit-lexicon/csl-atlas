# Handoff: mitra-aligner → DTB link-targets

**Status:** specification / handoff. Not implemented. This document is a complete brief for
the next agent or contributor to build the `mitra-aligner` integration (Opportunity 1 in
[DHARMAMITRA_INTEGRATION.md](DHARMAMITRA_INTEGRATION.md)). It deliberately stops at the point
where the work needs assets and decisions outside this repo (digital source corpora, a remote
alignment API, Cologne-wide `csl-corrections` policy).

---

## 1. Goal

Turn `<ls>` citations in the dictionaries into **click-through links to the cited source
passage** — the org-wide **Dictionary-to-Book (DTB)** milestone (`link-target` /
`link-splitting`). Today a citation like `<ls>ŚAT. BR. 5,3,1,11.</ls>` is dead text plus a
locus string; the goal is a verified link from that citation to the exact place in a digital
or scanned edition of the Śatapatha-Brāhmaṇa.

Two sub-problems, both of which alignment helps with:

- **link-target** — locate the cited passage in the source text.
- **link-splitting** — split combined refs (`SOURCE N,N; M,M`) into one link per locus.

This is **Cologne-wide**, not atlas-specific. Outputs feed the `csl-corrections` audit-trail
workflow and are reviewed before any source file changes. The atlas's role is to *propose and
review* link candidates, never to rewrite `csl-orig` directly.

---

## 2. What mitra-aligner is — and the honest fit

- [mitra-aligner](https://github.com/dharmamitra/mitra-aligner): BERT-based parallel-text
  sentence alignment (`bertalign-buddhist`). CLI: `python align-texts.py texta.txt textb.txt`,
  inputs in **clean one-sentence-per-line** form. GPU locally.
- [mitra-aligner-client](https://github.com/dharmamitra/mitra-aligner-client): **GPU-free**
  client to a remote API. `python align.py --input-a A --input-b B --output out.tsv`. Splits
  both files into sentences, calls the API, writes aligned pairs as TSV. Languages: Sanskrit,
  Tibetan, Chinese, English. Slow (minutes per hundreds of lines).

**Fit caveat — read this before designing.** mitra-aligner aligns two *parallel running
texts* sentence-by-sentence. The DTB task is **passage location / retrieval**: finding where a
short dictionary quote sits inside a long source text. These are not the same problem. Two
viable framings:

- **(A) Retrieval framing (recommended first).** Treat each dictionary quote as a query and the
  source text's sentences as a corpus; find the best-matching source sentence(s) by the
  aligner's multilingual sentence embeddings. This is what actually produces a locus.
- **(B) Alignment framing.** When a whole dictionary *article* quotes a contiguous run of a
  source (rare), align article-quotes against the source as two parallel sequences.

Prefer (A). If the remote API only exposes pairwise alignment, you can still use it by aligning
`[quote]` against a windowed slice of the source and taking the highest-scoring pair — but a
direct embedding/retrieval endpoint (or `mitra-parallel`) would be cleaner. **Open question
for the maintainers: does Dharmamitra expose a sentence-embedding / retrieval endpoint, or only
pairwise bertalign?** Resolve this first; it determines the importer design.

---

## 3. Inputs and dependencies

| Input | Where it is / where to get it | Notes |
|---|---|---|
| Dictionary quotes + citation + locus | parse `csl-orig` (`<ls>` tags + adjacent `{#...#}` quote) | [`extractCitations`](../scripts/lib/mw-classifiers.mjs) already pulls `<ls>` strings |
| Canonical source identity per siglum | [`src/data/dict-source-aliases.json`](../src/data/dict-source-aliases.json), [`source-siglum.mjs`](../scripts/lib/source-siglum.mjs), the reviewed [`source-siglum-review.json`](../src/data/review/source-siglum-review.json) | siglum→canonical-source folding is **already started** |
| Per-source citation inventory | [`src/data/dicts/citation-apparatus.json`](../src/data/dicts/citation-apparatus.json) (built by [`build-citation-apparatus.mjs`](../scripts/build-citation-apparatus.mjs)) | use to pick the highest-yield source for the first slice |
| **Digital source texts** | **NOT in this repo** — GRETIL, DCS, SARIT, or the scanned-edition OCR | the hard external dependency; see §6 |
| Alignment engine | mitra-aligner-client (remote API) or local mitra-aligner | GPU-free path preferred for reproducibility-of-process |

The **blocking dependency is the digital source corpus**. Link-target alignment is impossible
without a machine-readable text of the cited work to align against. Securing GRETIL/DCS texts
(and a siglum→source-file map) is the real first task — the alignment is the easy half.

---

## 4. Architecture (follow the established two-step pattern)

Mirror every other Dharmamitra integration ([DHARMAMITRA_INTEGRATION.md](DHARMAMITRA_INTEGRATION.md)):
a networked **import** step writing a snapshot under `src/data/external/`, and a **deterministic
build** step that joins it into a schema-conforming review queue via
[`review-report.mjs`](../scripts/lib/review-report.mjs). The model/alignment output is **review
evidence only** — it never edits `csl-orig`.

```
build-citation-link-candidates.mjs        # deterministic
  parse csl-orig <ls> + {#quote#} + locus, resolve siglum -> canonical source,
  keep only sources with a known digital text, write candidates:
  src/data/external/citation-link-candidates.json
        |
        v
import-dharmamitra-alignment.py           # networked / model
  for each (quote, source) pair, retrieve/align against the source text,
  write best locus + score:
  src/data/external/dharmamitra-alignment.json   (gitignored if large)
        |
        v
build-citation-link-review.mjs            # deterministic
  join, emit review queue `citation-link-target` with a proposed link + confidence;
  human ratifies before any link is written to csl-orig / csl-corrections
```

### Data contracts

**`citation-link-candidates.json`** — `{ candidates: [{ key, dict, lemma, line, siglum, canonicalSource, sourceFile, quoteSlp1, quoteIast, locus }] }`. `key` is a stable id (`dict:line:siglumIndex`).

**`dharmamitra-alignment.json`** — `{ byKey: { <key>: { matchedSourceLocus, matchedText, score, method } } }`. Record the model/API revision and `method` (retrieval vs pairwise) in `source`.

**`citation-link-review.json`** — queue `"citation-link-target"`, `subject.kind` a new
`"citation"`, `machineValue: { siglum, canonicalSource, locus, proposedLink, matchedText,
score, verdict }`. Verdicts: `link-proposed` / `low-confidence` / `no-source-text` /
`needs-review`. Add the `citation-link-target` queue value and `citation` subject kind to
[`review-report.schema.json`](../data/schema/review-report.schema.json) (one line each).

---

## 5. Recommended first slice

Do **not** attempt all sources at once. Pick **one** high-yield, digitally-available source and
prove the pipeline end-to-end:

1. From [`citation-apparatus.json`](../src/data/dicts/citation-apparatus.json), choose the
   densest source that also has a clean GRETIL/DCS text — e.g. **Ṛgveda** (RV) or
   **Mahābhārata** (MBh): high citation counts, well-digitized, stable locus schemes.
2. Resolve its siglum via the existing alias table; collect all `(quote, locus)` pairs in MW
   (start with one dictionary).
3. Align/retrieve each quote against the source text; emit a `citation-link-target` review
   queue of proposed loci with confidence.
4. Manually score precision on the first ~100. If precision is usable (say ≥80% at the top
   confidence band), widen to more sources; if not, tune retrieval (windowing, SLP1↔IAST
   normalization, sandhi-insensitive matching) before scaling.

A successful first slice = a committed `citation-link-target` review queue for one source, with
a measured precision number and a documented locus-link format ready for `csl-corrections`.

---

## 6. Risks and open questions

- **Source-text availability is the gate.** No GRETIL/DCS text → no link-target. Inventory which
  cited sources have machine-readable editions before committing to scope.
- **Encoding/sandhi.** Dictionary quotes are SLP1, often sandhi-joined fragments; source texts
  may be IAST/Devanāgari/HK with different sandhi/segmentation. Normalize both sides (reuse
  [`lookup-normalize.js`](../src/lib/lookup-normalize.js) and `dharmamitra_infer.slp1_to_iast`)
  and consider sandhi-insensitive matching. This is where most precision is won or lost.
- **Locus schemes differ** between the dictionary's citation convention and the digital edition's
  (book/hymn/verse vs line offset). A per-source locus-mapping table is likely needed.
- **Throughput.** The client is slow; batch and cache. The alignment snapshot may be large →
  gitignore it like the detect-language intermediates, commit only the review queue.
- **API exposure** (see §2): retrieval vs pairwise-only changes everything. Confirm first.
- **Governance.** Links ultimately modify `csl-orig`; that goes through `csl-corrections` with
  human review, per the org CLAUDE.md correction workflow. The atlas only proposes.

---

## 7. Definition of done (for the first slice)

- [ ] Confirmed alignment/retrieval API shape with Dharmamitra (retrieval endpoint or pairwise).
- [ ] Source-text inventory: ≥1 cited source with a committed/linked digital text + siglum map.
- [ ] `build-citation-link-candidates.mjs` emits candidates for that source from `csl-orig`.
- [ ] `import-dharmamitra-alignment.py` produces a snapshot of proposed loci + scores.
- [ ] `build-citation-link-review.mjs` emits a schema-valid `citation-link-target` queue.
- [ ] Schema gains `citation-link-target` queue + `citation` subject kind; `validate-review-reports` green.
- [ ] Measured top-band precision on a 100-item manual sample, written into the queue's trust block.
- [ ] Handoff note on widening to more sources and the `csl-corrections` link-write step.

---

## 8. Pointers

- Org DTB taxonomy + `csl-corrections` workflow: `../CLAUDE.md` (org-level).
- Existing citation/siglum machinery: [`build-citation-apparatus.mjs`](../scripts/build-citation-apparatus.mjs),
  [`source-siglum.mjs`](../scripts/lib/source-siglum.mjs), [`CITATION_REGISTERS.md`](CITATION_REGISTERS.md).
- Review-layer contract: [`REVIEW_REPORTS.md`](REVIEW_REPORTS.md), [`review-report.mjs`](../scripts/lib/review-report.mjs).
- Repos: [mitra-aligner](https://github.com/dharmamitra/mitra-aligner) ·
  [mitra-aligner-client](https://github.com/dharmamitra/mitra-aligner-client) ·
  [mitra-parallel](https://github.com/dharmamitra/mitra-parallel).
