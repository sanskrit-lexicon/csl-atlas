_Created: 24-09-2026 · Last updated: 24-09-2026_

---
title: Methods — the kośa as a macrostructural type
---

# The versified synonymic kośa as a macrostructural type

The Amarakośa, Halāyudha's *Abhidhānaratnamālā* (ARMH) and Hemacandra's
*Abhidhānacintāmaṇi* (ABCH) are dictionaries whose meaning lives in their
*arrangement*: a concept-ordered hierarchy of books (*kāṇḍa*), sections (*varga*),
verses and synonym-sets, with liṅga (gender) marking riding on the words. The
atlas measured that arrangement in the [A06 kośa macrostructure paper](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/paper_kosha_macrostructure.md);
this page states it as a **model** — a schema every kośa instance must satisfy —
and separates what the sources *show* from what we *infer*.

## Trust Block

- Evidence: the Amarakośa in the sanskrit-kosha markup (`amar.txt`, GPL-3.0, revision `f5575c3`), and ABCH, ARMH and MW from `csl-orig` (revision `f4c08c5`). All counts come from [`m10_kosa_macrostructure_model.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/lexico/m10_kosa_macrostructure_model.py) → [`kosa_model_measures.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosa_model_measures.json).
- Model: [`kosa-macrostructure.schema.json`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/schema/kosa-macrostructure.schema.json), validated on the [Amarakośa sample](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/lexico/kosa_model_amar_sample.json) (40 verse-groups from all three kāṇḍas and all three section types), with ABCH and ARMH instances as generality checks.
- Limitations: the synonym-set boundaries and gender tags are the annotators' reading of the verse, not marks in the verse itself (§4); the liṅgādisaṅgraha-varga is not in this digitization; ARMH encodes neither sets nor gender.
- Validation: `npm run validate-kosa-model` (schema + semantic rules) and `node --test test/kosa-model.test.mjs`, which also mutates a valid instance nine ways and checks each defect is rejected.
- Owner repo: `csl-atlas` (handoff H5328, epic E014).

```js
import { csvDownloadButton } from "../lib/csv-download.js";
const measures = FileAttachment("../data/lexico/kosa_model_measures.json").json();
const amar = FileAttachment("../data/lexico/kosa_model_amar_sample.json").json();
```

## 1. Two macrostructural types

A European dictionary is **semasiological**: it starts from the word and has one
ordering device, the alphabetised headword; the lexicographic work is done in
the entry (senses, glosses, citations). A kośa is **onomasiological**: it starts
from the concept, and the lexicographic work is done by *placing* a word — which
book, which section, which verse, next to which synonyms, in which gender.

| Level | Kośa (onomasiological, versified) | European (semasiological, alphabetical) |
|---|---|---|
| Top division | *kāṇḍa* — region of the universe (Amara, Halāyudha) or hierarchy of beings (Hemacandra) | letter of the alphabet |
| Section | *varga* — a concept field (heaven, time, the body, …); *upavarga* in Hemacandra's animal book | none (letter ranges) |
| Unit of text | verse (*śloka*), numbered within its section | entry (article) |
| Unit of meaning | synonym-set: the names of one concept | sense within an entry |
| Homonymy | a dedicated *nānārtha* section, ordered by the word's **final** sound | homonym numbers or senses inside one entry |
| Grammar | liṅga stated by form, association or explicit word (*striyām*, *klībe*) | part-of-speech label in the entry |
| Findability | memorised verse; no alphabetical access | alphabetical lookup |

The schema encodes the left column as `kāṇḍa → varga → (upavarga) → verse-group →
set → member`, with four set kinds: `synonym-set`, `homonym-sense` (one headword +
a gloss naming one meaning), `indeclinable-set`, and `unsegmented-verse` for a
digitization that does not mark set boundaries (ARMH). Each instance also carries
an `orderingDevices` table in which every device is labelled **observed**,
**inferred** or **absent** and assigned to a layer: the source text, the
digitization markup, or our measurement.

## 2. The ordering devices, observed versus inferred

```js
const deviceRows = Object.entries(measures.devices).flatMap(([kosha, devs]) =>
  devs.map(d => ({kosha, device: d.device, evidence: d.evidence, layer: d.layer, level: d.level, note: d.note})));
display(Inputs.table(deviceRows, {rows: 30, layout: "auto"}));
display(csvDownloadButton(deviceRows, "kosa-ordering-devices.csv"));
```

**Observed in the source text** — present in the words of the kośa itself:

1. the *kāṇḍa* and *varga* divisions. Section headings name all 24 vargas of the
   Amarakośa; 23 open with *atha … vargaḥ* (once in sandhi, *athāvyayavargaḥ*) and
   23 close with *iti … vargaḥ* (the *bhūmi-varga* has no opening colophon, the
   *avyaya-varga* no closing one);
2. the verse and its number. Amara's numbers restart at every one of the 23
   varga boundaries and, in this digitization, run in steps of exactly one inside
   each varga: 1,432 full verses inside the verse-groups, 1,444 in the file, the
   other 12 standing outside any verse-group (the preface, for example).
   Hemacandra's numbers, by contrast, run on through all 14 section boundaries of
   ABCH without restarting;
3. the homonym section (*nānārtha-varga*), whose opening verse announces the
   arrangement by final sound (*kāntādi*);
4. the indeclinable section (*avyaya-varga*), the last varga of this digitization —
   the text itself (kāṇḍa 3, v. 1) names one more, the *liṅgādisaṅgraha-varga*,
   after it;
5. the *rule* of gender marking: Amara's *paribhāṣā* (vv. 3–5) says liṅga is known
   by form, by association with a neighbouring word, or by an explicit statement.

**Observed in the digitization markup** — explicit in the files, but supplied by
the annotators, not by the author:

1. the segmentation of a verse into synonym-sets (`<eid>`): 5,590 sets in 2,359
   verse-groups for the Amarakośa;
2. the per-word liṅga tag (`puM`, `strI`, `klI`, `tri`, `a`, with `dvi`/`ba` for
   number): 14 distinct tags, all parsed;
3. Hemacandra's upavarga tier in the animal book (e.g. *pañcendriya* →
   *sthalacara*).

**Inferred by measurement** — patterns we establish; the text states none of
them, or (for the homonym section) only the principle:

1. *No alphabetical device.* Adjacent synonyms are in alphabetical order no more
   often than chance.
2. *How strictly the a-tergo order of the homonym section holds.* The
   *kāntādi* verse announces the principle. That it holds almost perfectly, that
   it runs in two series, and that its exceptions are the traditional letter
   equivalences is what we measure.
3. *Gender contiguity* in the Amarakośa: words of one gender stand together.

**Absent**: an upavarga tier in the Amarakośa, the liṅgādisaṅgraha-varga in
this digitization, and, for ARMH, varga divisions, synonym-set boundaries and
gender tags.

## 3. Measurements

### 3.1 No alphabetical device

Share of adjacent words whose Sanskrit (varṇa) collation does not decrease. An
alphabetical dictionary sits near 1; an unordered list near 0.5.

```js
const alphaRows = Object.entries(measures.measures).map(([kosha, m]) => ({
  kosha, model: m.digitizationModel, pairs: m.alphabeticalAdjacency.pairs, nondecreasing: m.alphabeticalAdjacency.nondecreasing}));
display(Inputs.table(alphaRows, {layout: "auto"}));
display(csvDownloadButton(alphaRows, "kosa-alphabetical-adjacency.csv"));
```

MW scores 0.939 (not 1.0, because compounds are nested under their first member);
the three kośas score 0.49–0.50. Alphabetical order is not a kośa device, at any
level.

### 3.2 The homonym section is ordered by the final sound

```js
const nn = measures.measures.AMAR.nanarthaOrder;
const seriesRows = nn.series.map((s, i) => ({series: i + 1, starts: s.startIast, headwords: s.headwords,
  indeclinableShare: s.indeclinableShare, finalSoundInOrder: s.finalConsonantNondecreasing}));
display(Inputs.table(seriesRows, {layout: "auto"}));
display(csvDownloadButton(seriesRows, "amarakosa-nanartha-series.csv"));
const violationRows = nn.violations.map(v => ({series: v.series, from: v.fromIast, to: v.toIast, explainedBy: v.explainedBy ?? "—"}));
display(Inputs.table(violationRows, {layout: "auto"}));
display(csvDownloadButton(violationRows, "amarakosa-nanartha-order-exceptions.csv"));
```

Over the 861 homonym headwords (1,995 senses), the final consonant is in varṇa
order on 0.991 of adjacent steps; the *initial* letter only on 0.536, which is
chance. The section is sorted *a tergo*. It is also two series, not one: 802
nominal headwords run from *nāka* (final *-k-*) to the *-h-* finals, then a
second series of 59, 98% indeclinable, starts again from *āṅ*, *āḥ*, *ku*, *dhik*,
*ca* …. In the first series only five steps go backwards, and four of them fall
under the equivalences the grammatical tradition itself allows — *ḍ = l*
(*ilā → kṣveḍā*) and *b = v* (*gandharva → kambu*, *pūrva → kumbha*,
*sattva → klība*). One (*jihma → uṣṇa*) is unexplained.

The order is *measured*; that it was *intended* is supported by the section's own
opening verse, and its exceptions pattern with a known convention, but the
reading of the two series as a deliberate "nominal, then indeclinable" design is
an inference.

### 3.3 Gender contiguity

In a multi-gender synonym-set, does each gender form one unbroken run? The chance
baseline is exact: for a set of *n* words in *k* genders with counts c₁ … cₖ, a
random order keeps every gender together with probability k! · Π cᵢ! / n!.

```js
const gRows = ["AMAR", "ABCH"].map(k => ({kosha: k, ...measures.measures[k].genderContiguity}));
display(Inputs.table(gRows, {layout: "auto"}));
display(csvDownloadButton(gRows, "kosa-gender-contiguity.csv"));
```

In the Amarakośa 0.90 of 756 multi-gender sets keep each gender together, against
0.68 by chance. This is how the verse carries gender: a run of masculines, then
*dve striyām* ("the two [are] feminine"), then *klībe* ("in the neuter"). In
Hemacandra the effect nearly disappears (0.67 against 0.62). Why is not tested
here; one candidate is that Hemacandra treats gender in his separate
*Liṅgānuśāsana*, so his verse need not carry it. Masculine-first is at chance in both
(0.36 vs 0.35; 0.34 vs 0.34): the device is *grouping*, not a fixed gender order.

### 3.4 The model instance, one set of each kind

```js
const vargas = amar.kandas.flatMap(k => k.vargas.map(v => ({...v, kanda: k.labelIast})));
const pick = t => vargas.find(v => v.sectionType === t && v.groups.length);
const exampleRows = ["synonymic", "homonymic", "indeclinable"].flatMap(t => {
  const v = pick(t), g = v.groups[0], s = g.sets[0];
  return s.members.map(m => ({section: `${v.kanda} › ${v.labelIast}`, L: g.L, eid: s.eid, kind: s.kind,
    form: m.formIast, role: m.role, tag: m.gender?.tag ?? "—", genders: (m.gender?.genders ?? []).join("")}));
});
display(Inputs.table(exampleRows, {rows: 40, layout: "auto"}));
display(csvDownloadButton(exampleRows, "amarakosa-model-examples.csv"));
```

## 4. What the model does not claim

1. **The sets are editorial.** A verse such as *svar avyayaṃ svarga-nāka-tridiva-…*
   does not mark where one concept ends and the next begins; the `<eid>`
   segmentation is the annotators' reading (Shivja S. Nair's database for the
   Amarakośa, the CDSL markup for ABCH). The model records it as
   *digitization-markup*, not *source-text*.
2. **The gender tags are editorial too.** The text supplies gender by the three
   means of its *paribhāṣā*; the tag on each word is an annotator's resolution of
   them. The contiguity result (§3.3) is therefore a property of text plus
   annotation.
3. **Section types are read from labels.** *nānārtha* → homonymic and *avyaya* →
   indeclinable are read from the varga names; ARMH's fifth kāṇḍa is typed
   homonymic from its *…api…* verse formula (A06 §4.2), so its basis is
   `content`, not `section-label`.
4. **Counts are per digitization.** A "set" in AMAR/ABCH and a "verse" in ARMH are
   different units (A06 §4.3); the schema keeps them apart through
   `digitizationModel` and the `unsegmented-verse` kind.

## 5. Reproduce

The build needs the sibling checkouts `../AMAR` (sanskrit-kosha data) and
`../csl-orig`; the validator and tests need only the committed JSON.

```sh
python scripts/lexico/m10_kosa_macrostructure_model.py
npm run validate-kosa-model
node --test test/kosa-model.test.mjs
```

_Dr. Mārcis Gasūns_
