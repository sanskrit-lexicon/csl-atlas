# The sense-order test — Böhtlingk's item #4, measured

_Created: 13-07-2026 · Last updated: 13-07-2026_

**What this is.** A measured test of the **fourth and last** clause of Böhtlingk's 1883
plagiarism charge against Monier-Williams — the **order of the meanings** — which A10
([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md))
had only *proxied* (with F5's citation-order, 0.811) but never measured directly. Script:
[`scripts/forensic/f10_sense_order.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f10_sense_order.py);
data: [`sense_order_test.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/sense_order_test.csv),
[`sense_order_examples.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/sense_order_examples.csv).

## The historical claim

In the Böhtlingk↔Max-Müller correspondence, reconstructed by Agnes Stache-Weiske (2015), Müller's
letter of 11 June 1881 states the charge verbatim:

> „Was in Ihrem Werk ausgelaßen u[nd] versehen ist, ist bei ihm ausgelaßen und versehen u[nd] die
> **Reihenfolge der Bedeutungen einfach abgeschrieben**.“

— *and the **order of the meanings simply copied out**.* A10 already ran the other three clauses:
**omission** (§3.5 / F9, ≈8× coupling), **error** (§4 / F4a-b, F7 — a measured null), and false
**citation** (§6 / F1, F7 — a measured null). It measured sense-order only *indirectly*, through
the order in which the two works cite their **sources** (F5, 0.811 concordance — a strong,
Petersburg-specific signal). The literal claim — does MW list its **glosses/senses** in PWG's
order? — was never tested. This does.

## The test

For every headword both dictionaries carry with **≥3 senses each**, extract MW's ordered sense
sequence and PWG's, align them **cross-lingually by meaning** (not by citation, so the result is
independent of F5), and score whether the two orders agree.

- **Segmentation.** MW: senses across consecutive sub-`<L>` records sharing `k1` plus `<div n="to|P|1">`
  divisions; the leading declension/paradigm chunk (no gloss) drops out. PWG: `<div>`-marked
  Bedeutungen; the pre-first-`<div>` grammar/etymology head drops out. AP (control): U+2219 bullets.
- **Cross-lingual alignment.** Each sense → a bag of {English gloss tokens} ∪ {Sanskrit referent
  tokens}. PWG's German gloss is rendered to English **offline** (argos `de→en`, cached — the same
  MT channel as F6, **not** a live LLM). MW sense *i* is matched one-to-one (greedy, descending
  token-Jaccard, **position-blind**) to the PWG sense it most resembles. Concordance = the fraction
  of matched sense-pairs whose relative order agrees (0.50 = random, 1.00 = identical sequence).
  Citations are **deliberately excluded** from the token bags so this cannot re-measure F5.
- **Controls (mandatory, per A10 method).** (i) the independent **Apte** (AP, 1890), whose senses
  are already English (no MT) — MW-vs-PWG counts as *copying* only if it **exceeds** MW-vs-Apte,
  because senses carry a partly-forced canonical order (literal → figurative → technical) that any
  competent lexicographer shares; (ii) a **shuffled-sense null** — re-score with the other dict's
  sense positions permuted, isolating the matching/forced-order floor.

## Result

| MW vs | cand. (≥3 senses both) | scored | mean sense-order concordance | % perfectly identical | shuffle floor | mean matched pairs | mean match-sim |
|---|--:|--:|--:|--:|--:|--:|--:|
| **PWG** | 5,179 | 2,451 | **0.767** | **41.9 %** | 0.500 | 4.63 | 0.217 |
| **Apte** (control) | 3,686 | 2,507 | **0.751** | 34.3 % | 0.499 | 4.55 | 0.396 |

**The gradient is the answer, and here it is nearly flat.** Both dictionaries order their senses far
above chance (0.75–0.77 vs a 0.50 shuffle floor) — sense order is *structured*, not random. But
MW-vs-PWG (**0.767**) barely exceeds the **independent** Apte control (**0.751**): a differential of
just **+0.016**. Set this beside the citation-order sibling F5, where MW-vs-PWG **0.811** towered over
the same independent Apte at **0.42** (a +0.39 gap): the sense-order Petersburg-specificity is roughly
**an order of magnitude smaller** than the citation-order signal.

The one place a faint Petersburg-specific residue survives is the **strict** metric: MW reproduces
PWG's sense sequence *perfectly* in **41.9 %** of entries versus **34.3 %** for the independent Apte
(+7.6 pts) — the metric least sensitive to the matching-noise caveat below. High-concordance cases
are real and, unsurprisingly, exist for *both* comparators: *dāman* (9 MW / 10 PWG senses, 7 matched,
identical order), *śītala*, *āsura*, *āvarta*, *ka* — all conventional literal→figurative→technical
runs a competent compiler orders the same way independently.

## Reading

**Item #4 is a measured near-null: MW's sense *order* is shared lexicographic convention, not copied
from Böhtlingk.** Where the citation apparatus (F5) showed a decisive, Petersburg-*specific* copy
signal — MW assembled each entry *following PWG's article* — the order of the **meanings** does not.
MW sequences its senses barely more like PWG than like the wholly independent Apte; both track the
canonical literal→figurative→technical convention, and that convention, not transcription, explains
the 0.77. **On this clause Böhtlingk overreached:** "die Reihenfolge der Bedeutungen einfach
abgeschrieben" is not borne out — MW is the *author* of its sense-sequencing, exactly as §4 shows it
is the author of its prose, while remaining the *heir* of the citation apparatus (§3.4) and the
inventory backbone (§3.1, §3.5). The F5 citation-order proxy, read alone, would have over-attributed
this clause; the direct test corrects it.

Like the shared-omission and shared-citation results, this does **not** deliver an airtight
Lachmann-style proof in either direction — a shared *convention* is not a conjunctive error — but it
converts the last unmeasured clause from "asserted" to "measured," and it lands on the **prose/author**
side of A10's ledger, not the **apparatus/heir** side. That bulk near-null has one important
refinement, though — a faint Petersburg-specific residue survives in the most closely-derived entries;
the *Robustness* section pins it down.

## Robustness — the paired test and the noise-control sweep

Two checks answer the obvious objections to a near-null: is the +0.016 a **subset** artefact (the PWG
and Apte arms score different headwords), and is it **masked** by the noisier cross-lingual matching?

**Paired, same headwords.** Restricting to the **660** headwords scored in *both* arms, MW-vs-PWG is
**0.7161** and MW-vs-Apte **0.7129** — a within-headword difference of **+0.0032**, with PWG beating
Apte on 293 headwords, Apte on 284, tied on 83 (sign-test *z* = 0.37, n.s.). The near-parity is real,
not a subset accident: head-to-head on the same words, MW sequences its senses **no more like PWG than
like the independent Apte**.

**Similarity-floor sweep.** The matching-noise caveat is testable directly: raise the minimum
match-similarity that a sense-pair must clear to count, which *equalises* the noisier PWG arm against
the clean-English Apte arm, and watch the paired gap.

| min match-sim | n paired | MW-vs-PWG | MW-vs-Apte | PWG − Apte |
|---|--:|--:|--:|--:|
| > 0.00 (all) | 660 | 0.716 | 0.713 | **+0.003** |
| > 0.05 | 560 | 0.721 | 0.724 | −0.003 |
| > 0.10 | 373 | 0.733 | 0.738 | −0.006 |
| > 0.15 | 214 | 0.764 | 0.736 | +0.028 |
| > 0.20 | 76 | 0.835 | 0.730 | **+0.104** |
| > 0.30 | 22 | 0.894 | 0.714 | **+0.180** |

The Apte arm stays flat (~0.71–0.74) at every floor — its order-agreement is the same however
confidently senses are matched, exactly what a fixed *convention* predicts. The PWG arm does **not**:
as the matches get cleaner the Petersburg-specific excess **emerges and grows**, to +0.10 at sim > 0.20
and +0.18 at sim > 0.30. Because a high cross-lingual match-similarity means MW's English gloss closely
echoes the argos-rendered German — i.e. the entry where MW followed PWG's *definition* most closely —
this says the sense-order **is** copied, but chiefly in the entries MW derived most directly, and there
the residue is real (n shrinks to 22–76, so read it as *direction*, not a precise coefficient). Across
the bulk of entries, translation noise dilutes it and the shared literal→figurative→technical
convention dominates, so the population signal is the near-null above.

**Net refinement.** Sense order is *predominantly convergent* — Böhtlingk's "die Reihenfolge der
Bedeutungen einfach abgeschrieben" overstates as a general claim — **with a genuine copying residue
concentrated in the most closely-derived entries**, an order of magnitude weaker than, but pointing the
same way as, the citation-order signal (§3.4/F5). Sweep data:
[`sense_order_robustness.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/sense_order_robustness.csv);
paired counts + sweep also in `f10_report.json` under `robustness`.

## Limits

- **The cross-lingual channel handicaps the PWG comparison.** MW-vs-PWG matches on MT-rendered German
  (mean match-similarity **0.217**) are noisier than the within-English MW-vs-Apte matches (**0.396**).
  Mis-paired senses score ~random (0.5), pulling the PWG concordance **down** toward the floor — so
  0.767 is a **conservative** estimate relative to Apte, and it means a **modest** Petersburg-specific
  signal could be masked by matching noise. The *Robustness* sweep tests exactly this by equalising the
  arms at higher match-similarity floors: it confirms a real but small residue emerges only in the
  most closely-derived entries, leaving the population near-null intact. A cleaner (embedding-based)
  cross-lingual matcher — unavailable offline in this environment — is the obvious extension to
  quantify that residue more precisely than the small high-floor subsets (n = 22–76) allow.
- **Scored ⊂ candidate.** Only headwords with ≥3 *confidently matched* sense-pairs are scored (2,451 of
  5,179 PWG candidates); low-overlap entries drop out symmetrically across the PWG and Apte arms.
- **Segmentation is convention-based**, not gold-annotated — MW `<div n="to|P|1">` + sub-`<L>`, PWG
  `<div>` Bedeutungen. Systematic mis-segmentation would add order noise, again pushing toward the null.
- **Position-blind greedy 1:1 matching** can mis-assign near-synonymous senses; this is the intended
  design (it must be blind to order to test order) but is the main source of the match-similarity gap.

## Reproduce

```sh
python scripts/forensic/f10_sense_order.py            # full run (uses cached de→en MT)
python scripts/forensic/f10_sense_order.py --census   # population sizes only, no MT
```

Reads `../csl-orig/v02/{mw,pwg,ap}`; segments senses; translates PWG German glosses `de→en` offline
(argos, cached in `data/forensic/_f10_sense_tcache.json` — one-time model install via
[`_setup_argos.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/_setup_argos.py);
bulk cache-fill parallelised by
[`_f10_pretranslate.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/_f10_pretranslate.py)).
Writes [`sense_order_test.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/sense_order_test.csv)
+ its `.source.json` provenance sidecar,
[`sense_order_examples.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/sense_order_examples.csv),
[`sense_order_robustness.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/sense_order_robustness.csv)
(the paired similarity-floor sweep), and `f10_report.json` (with the `robustness` block). Deterministic
(seed 17, sorted iteration); the MT cache is gitignored (rebuildable).

## Sources

- Stache-Weiske, Agnes. 2015. „Man muß zuweilen Insekten mit Kanonen schießen." Max Müllers Rolle im
  Streit zwischen Böhtlingk und Monier-Williams. In: *„In ihrer rechten Hand hielt sie ein silbernes
  Messer mit Glöckchen…" — Studies in Indian Culture and Literature*, 323–336. Wiesbaden: Harrassowitz.
- Zgusta, Ladislav. 1988. Copying in lexicography: Monier-Williams, Sanskrit Dictionary and other cases
  (Dvaikośyam). *Lexicographica* 4, 145–164.

_Dr. Mārcis Gasūns_
