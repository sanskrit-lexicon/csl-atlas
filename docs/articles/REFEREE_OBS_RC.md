# Pre-submission referee reports — OBS-R and OBS-C

Date: 2026-06-13

Status: internal adversarial review of the two IJL-targeted companion papers,
[`paper_redundancy_and_descent.md`](articles/paper_redundancy_and_descent.md) (OBS-R)
and [`paper_citation_registers.md`](articles/paper_citation_registers.md) (OBS-C),
in the voice of an *IJL* referee. **[fixed]** points were applied in the same change;
**[author]** points need a decision or new number. Not part of either manuscript.

Both papers share a real strength a referee will credit: they state their central
quantity as a *bound* — headword overlap is a floor for relatedness, locator/​*iti*
presence an upper bound for resolvability/citation. The objections below are mostly
about keeping the headline language inside those bounds, plus one or two sensitivity
numbers each.

---

## A. OBS-R — *Redundancy and Descent*

**Recommendation: minor-to-major revision.** A clean, novel, self-validating
measurement. The fixes are framing precision and two missing numbers; the core
results (3.65 : 1 collapse, 57.9 % redundancy, MW-absorber stemma) are sound.

**R-M1. The stemma's direction is heuristic, not derived. [author]**
Edge direction comes from year + set size, not from the data; high `a_in_b` with low
`b_in_a` is equally consistent with "B absorbed A" and "B is comprehensive and A is a
standard wordlist, both recording the common core." The paper says this (§3.2, §6) —
good — but the abstract's "near-total absorber / documentary sink" reads as proven
descent. **The cheapest strengthening is to show the asymmetry that justifies the
arrow:** add the reverse containment `b_in_a` as a column in Table 2, so the reader
sees that (e.g.) BOP ⊂ MW = 0.94 while MW ⊂ BOP is small. Without the reverse number
the directional claim is asserted, not shown.

**R-M2. Unique-% indexes independence, not value. [fixed]**
A comprehensive general dictionary scores low unique-% *by design* (it records the
shared core); that is a service, not a defect. The "documentary value" wording was
softened to "independent contribution / irreplaceability."

**R-M3. The variant-folding sensitivity is asserted but not quantified. [author]**
"An anusvāra/visarga fold lowers independence by a few points" needs the actual
number: does the 42.1 % unique become 39 %? 35 %? State the sensitivity bound, since
the unique-core headline rests on the conservative fold.

**R-M4. Containment table lacks denominators and CIs. [author]**
With set sizes in the hundred-thousands the point estimates are stable, but a referee
will want |A|, |B|, |A ∩ B| (or at least |A|) beside each ratio so the reader can see
that 0.94 is 0.94 of a large set, not a small one.

**R-M5. "Independently attested" relabelled to "dictionary-unique." [fixed]**
A shared headword may be independent attestation in each dictionary, not a copy, so
the 170,000 figure is a floor for novelty, not a count of independent attestation.
The §4.2 wording now says this explicitly.

*Minor:* references `[TODO]`; consider one sentence placing the 3.65 : 1 figure
against a comparator aggregate (another portal's entry-to-lemma ratio) if one exists.

| Point | Action |
|---|---|
| R-M1 stemma direction | pending — add reverse-containment column to Table 2 |
| R-M2 value vs independence | **applied** |
| R-M3 fold sensitivity | pending — state the number |
| R-M4 denominators | pending — add set sizes to Table 2 |
| R-M5 unique vs attested | **applied** |

---

## B. OBS-C — *Two Citation Registers*

**Recommendation: minor-to-major revision.** The two-registers finding is the
paper's real contribution and it is important and correct. The exposure is that the
*symmetry* of the framing ("the kośas cite as densely again") rests on an unbounded
proxy.

**C-M1. The *iti* count is an upper-bound proxy; the symmetric framing needs a
validation sample. [fixed, partially]**
The headline contrast invites the reader to compare SKD's 69,215 *iti* against the
European per-entry densities as if commensurable, but *iti* includes grammatical and
quotative uses, so the indigenous rate is bounded only from above. "Cite as densely
again" was softened to "cite densely … bounded from above." **[author]** The proper
fix is a small hand-validation — exactly the gold-standard method now built for the
MW block detector: classify ~100 *iti* occurrences in SKD as citational vs
grammatical and report the citational fraction, converting the indicator into "≥ X %
of *iti* are citations." That single number would let the two registers be compared
on equal footing.

**C-M2. Table 1 is incomplete. [author]**
BEN, BHS and AP show a per-entry rate but "—" for the total. Fill the totals from the
generator (or drop the rows); an incomplete headline table is an easy referee target.

**C-M3. "Resolvable" hedged to the locator-bearing upper bound. [fixed]**
The conclusion now reports "up to 59.1–59.8 %, the locator-bearing upper bound," and
the gap as "at least 496,000," matching the §3.1/§4.2 caveat that a locator is
necessary but not sufficient.

**C-M4. No comparator for the 59 % figure. [author]**
Is 60 % locator-presence high or low for a historical dictionary apparatus? One
sentence of context (another corpus, or the pre-digital expectation) would let the
reader judge whether the dictionary-to-book gap is large or small.

**C-M5. Quantify the mis-ranking. [author]**
"An `<ls>`-only measure mis-ranks the kośas as citation-poor" — show it: by *iti*
density SKD would rank where among the 43 dictionaries, versus dead last by `<ls>`?
The concrete rank-swap makes the methodological warning land.

*Minor:* references `[TODO]`.

| Point | Action |
|---|---|
| C-M1 *iti* proxy / symmetry | **applied** (softened) + pending (hand-validation %) |
| C-M2 incomplete Table 1 | pending — fill totals |
| C-M3 resolvability bound | **applied** |
| C-M4 comparator | pending — one sentence of context |
| C-M5 rank-swap | pending — give the number |

---

## Shared next pass

For both papers the pending items are one short revision each: OBS-R needs the
reverse-containment column + the fold-sensitivity number; OBS-C needs the *iti*
hand-validation fraction + the completed Table 1. Neither requires new method — only
numbers already latent in the committed generators — and both bring the headline
language fully inside the bounds the papers already, to their credit, declare.
