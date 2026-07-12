# The shared-omission test — Böhtlingk's item #1, measured

_Created: 12-07-2026 · Last updated: 12-07-2026_

**What this is.** A measured test of the *other half* of Böhtlingk's 1883 plagiarism charge
against Monier-Williams — the **shared-omission** half — which A10
([`article_21_apparatus_not_errors.md`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/docs/articles/article_21_apparatus_not_errors.md))
had not run. Script: [`scripts/forensic/f9_shared_omission.py`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/scripts/forensic/f9_shared_omission.py);
data: [`shared_omission_test.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_omission_test.csv).

## The historical claim

In the Böhtlingk↔Max-Müller correspondence, reconstructed by Agnes Stache-Weiske (2015), Müller's
letter of 11 June 1881 states the charge verbatim:

> „Was in Ihrem Werk ausgelaßen u[nd] versehen ist, ist bei ihm ausgelaßen und versehen u[nd] die
> Reihenfolge der Bedeutungen einfach abgeschrieben.“

— *what is **omitted** and erroneous in your work [PW] is omitted and erroneous in his [MW], and the
order of the meanings simply copied out.* Böhtlingk repeated it to the Clarendon Press (28 Nov 1881):
MW reproduces "Versehen mannigfacher Art, Druckfehler und falsche Citate" — errors of every kind,
misprints, false citations. A10 already ran the **error** clause three ways — F4b Ahlborn
misspellings (≈0 %), F4a print errors (0 shared), F7 Harivaṃśa shared-erroneous citations (a measured
null) — and the sense-**order** clause once (F5 citation-order 0.811). It never ran the **omission**
clause. This does.

## The test

The negative-space complement of A10 §3.1 (shared *presence*). Take real Sanskrit words that lie
**wholly outside the European Petersburg lineage** — headwords attested in **both** major indigenous
dictionaries, Śabdakalpadruma (SKD) and Vācaspatyam (VCP). A word both list is unquestionably real and
enterable. Anchor **R = SKD ∩ VCP = 6,941** headwords (SLP1 `key1` join, `now-2026` CDSL exports).

Among R, partition by whether **PWG** (Böhtlingk-Roth) has the word. PWG's **blind spots** = real
indigenous words PWG lacks. Question: does **MW** disproportionately share those blind spots — beyond
what word-rarity alone forces? The confound is identical to A10 §4.2's "same hard words" trap: a word
rare enough for PWG to miss is rare enough for anyone to miss. The control is the independent **Apte**
(AP, 1890), A10's citation null. If MW tracks PWG's omissions **more than Apte does**, that differential
is the copy signal net of rarity.

## Result

| within R (n=6,941) | PWG has & _D_ has | PWG has & _D_ **lacks** | PWG **lacks** & _D_ has | PWG **lacks** & _D_ **lacks** | P(_D_ lacks \| PWG has) | P(_D_ lacks \| PWG lacks) | gap-sensitivity |
|---|--:|--:|--:|--:|--:|--:|--:|
| _D_ = **MW** | 4,134 | 158 | 1,446 | **1,203** | **3.7 %** | **45.4 %** | **12.3×** |
| _D_ = **AP** (control) | 2,696 | 1,596 | 1,162 | 1,487 | 37.2 % | 56.1 % | 1.5× |

**gap-sensitivity** = P(_D_ lacks | PWG lacks) ÷ P(_D_ lacks | PWG has): how much more often _D_ omits a
word when PWG omits it. MW's inclusion of a real indigenous word is **12.3×** more likely when PWG has
it than when PWG lacks it; for the independent Apte the same coupling is only **1.5×**. **Differential
MW ÷ AP = 8.2×**: whether MW enters a word is ~8× more predicted by PWG's decision than it is for an
independent compiler.

**But MW is not a mechanical copy of PWG's gaps.** On the 2,649 real indigenous words PWG omits, MW
independently **supplies 54.6 %** — *more* than the independent Apte's 43.9 %. MW repaired the majority
of PWG's blind spots from its own (Pandit-sourced) material.

## Reading

Two facts, both true, and together exactly A10's thesis seen from the omission side:

1. **Inventory descent, corroborated independently.** MW's entry/omission decisions are coupled to
   PWG's ~8× more tightly than an independent dictionary's — a negative-space confirmation of §3.1's
   shared-presence containment (0.70–0.82), on a set restricted to words *independently* attested, with
   an *independent* rarity control. This is new evidence, not a restatement: §3.1 could not see gaps.
2. **Not mechanical shared-blindness.** MW filled >half of PWG's indigenous gaps — more than Apte —
   so Böhtlingk's rhetorical "what PW omits, MW omits" **overstates**. MW inherited PWG's inventory
   *backbone*, then extended it.

So item #1 is **confirmed as a descent/coupling signal, refuted as literal carbon-copy blindness.**
Crucially, like the shared-citation result in A10 §6, it does **not** deliver the airtight
Lachmann-style proof: an omission is not a conjunctive error — two compilers can independently drop the
same rare word — so a shared gap corroborates common descent without proving it. It strengthens the
**apparatus** (inventory) side of A10, not the **error** side, which stays null. "Heir of the
scholarship, author of the prose" now has an omission-side witness.

## Limits

- **Anchor is a single cut** (SKD ∩ VCP). A word absent from one indigenous dict but real is excluded;
  the 6,941 anchor is conservative, not exhaustive. Widening to SKD ∪ VCP or adding a third indigenous
  witness is a straightforward robustness extension.
- **The confound runs the safe way.** MW drew on Pandit knowledge and Indian sources, so it may share
  indigenous vocabulary with SKD/VCP for reasons *independent* of PWG-copying — which would push MW to
  *fill* PWG's gaps and *weaken* the coupling. The 8.2× differential survives that adverse pull, so it
  is a floor, not a ceiling.
- **`key1` join.** Cross-dict matching is on the normalised computational key; minor per-dict
  normalisation differences add noise symmetrically across MW and the Apte control, so they cannot
  manufacture the MW-vs-AP differential.
- **An omission is not an error.** This corroborates descent; it is not the airtight shared-mistake the
  common-error principle would require (A10 §6). It moves item #1 from "asserted" to "measured," on the
  apparatus side.

## Reproduce

```sh
python scripts/forensic/f9_shared_omission.py
```

Reads the five `now-2026` `key1` exports from
`../SanskritLexicography/HeadwordLists/now-2026/` (themselves derived from `csl-orig`); writes
[`shared_omission_test.csv`](https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/forensic/shared_omission_test.csv)
+ its `.source.json` provenance sidecar.

## Sources

- Stache-Weiske, Agnes. 2015. „Man muß zuweilen Insekten mit Kanonen schießen." Max Müllers Rolle im
  Streit zwischen Böhtlingk und Monier-Williams. In: *„In ihrer rechten Hand hielt sie ein silbernes
  Messer mit Glöckchen…" — Studies in Indian Culture and Literature*, 323–336. Wiesbaden: Harrassowitz.
- Zgusta, Ladislav. 1988. Copying in lexicography: Monier-Williams, Sanskrit Dictionary and other cases
  (Dvaikośyam). *Lexicographica* 4, 145–164.

_Dr. Mārcis Gasūns_
