# 0001 — Dictionary authority grouping for Patel census badges

The Patel 2016 convention census (`data/L0/patel2016_assignments.csv`) counts every
witness equally, so the Petersburg Grundlagen (PWG+PW) carry 2 votes beside 8 works that
are indices rather than dictionaries, and the review sheets display only an anonymous
"[N dicts use this]". Decided MG 21-11-2026: group all dictionaries into 4 authority
tiers — A Grundlagen (PWG, PW; SCH rides as A2 supplement), B major scholarly references,
C specialized/derived, D meta-indices — plus an orthogonal origin axis (IND vs EUR, EUR
covering the whole Western tradition). Review sheets render tiered census badges and,
where PWG+PW back a non-majority option within a Patel sub-rule, flag the card — never
flip the suggestion (the dict's own-practice evidence stays the deciding axis).
Membership lives in `data/L0/dict_authority_tiers.csv`; `patel2016_assignments.csv` is
untouched — the grouping is a view over it, not a correction of it.

## Considered Options

- 3-tier / binary Petersburg-vs-rest — rejected: lumps Benfey-class references with
  Wilson-derived reader vocabularies.
- Derivation-family grouping as the ranking axis — rejected: a family member is not
  necessarily authoritative; kept as rationale context instead.
- Weighted-score badge (e.g. A=8, B=4) — rejected: hides who voted what.
- Auto-flip to the Tier-A option — rejected: silently overrides the dict's own-practice
  corpus evidence, which is the sheet's deciding axis (e.g. LRV-3 bare `-at`).

## Consequences

- Every future Patel sheet inherits the grouping through the sheet generator.
- Enforced by [ADR-0002](0002-enforcement-layers-for-authority-grouping.md):
  verify.mjs validator gate, review-sheet standing rule, reminder hook.
- PWG/PW are marked "deprecated by Cologne" in the inventory — that is a hosting/
  digitization status, not a scholarly authority verdict, and does not demote them.
- Provenance facts encoded in the CSV: SHS = Biswanath Mukerji; PUI/PE = Vettam Mani;
  MCI = Pusalker; KRM = Bhattoji Dīkṣita tradition (from `dictionary_inventory.csv`).
