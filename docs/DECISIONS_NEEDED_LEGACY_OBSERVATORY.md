# Decisions needed from the maintainer

Consolidated list of items that are **blocked on a human** (a decision, a credential, or an action only you can take). Maintained so an agent can resurface it at the start of a session. Last updated 2026-06-03 (all A-decisions closed; B1/B3/D2/D3 cleared; C deferred). **Only B2, C1–C3, D1 remain open.**

> Agent note: when M.G. asks "what's next?" or resumes, **surface this list first**.

---

## A. Decisions (pick an option)

**All A-decisions (A1–A8) are resolved — see "Recently resolved" below.** ✅

## B. Identifications / facts only you can confirm

| # | Item | Source |
|---|---|---|
| B2 | Verify **bibliography** I filled for the 6 documented repos — esp. BUR (Leupol / Maisonneuve) and BOP (1847 edition) | Handoff full-runbook gaps |

*(B1, B3, B4, B5 resolved — see "Recently resolved" below.)*

## C. Credentials / access needed — ⏸ deferred (none available now, per M.G. 2026-05-31)

| # | Need | For |
|---|---|---|
| C1 | **GitHub token** (workflow + read:project scope) as a repo secret | Automate observatory refresh (M4 / csl-observatory#12); Tooling Roadmap audit |
| C2 | **Cologne server / analytics access** (Matomo/GA/logs; ability to run `redo_xampp_selective.sh`) | Public-artefact refresh; OBSERVATORY_DESIGN Phase 12 |
| C3 | **DNS** for `observatory.sanskrit-lexicon.org` + Cologne `uni-koeln.de/observatory` handover | Observatory mirrors |

## D. Confirmations

| # | Item | Status |
|---|---|---|
| D1 | A Cologne admin will run / let the cron run `redo_xampp_selective.sh` so the 2026-05 csl-orig fixes propagate to Stardict/JSON/homepage. | ⏳ awaiting Cologne admin (not M.G.'s action) |

*(D2, D3 confirmed YES — see "Recently resolved" below.)*

---

## ✅ Recently resolved (2026-05-31)

| # | Resolution | Documented in |
|---|---|---|
| A2 | Taxonomy rollout done — 24 dict repos (786 issues) + 4 tooling repos (153 issues), all verified all-clean. | SESSION_HANDOFF.md; csl-corrections `.ai_state.md` |
| A6 | Cross-language sense alignment **anchors on Sanskrit** (SLP1 fingerprints) — no gloss translation. | RESEARCH_LAYER_ROADMAP §5.1 |
| A7 | **Full-corpus** measurement; anchor lemmas `gam`/`dharma`/`rāma`/`iti`/`bodhisattva`. | RESEARCH_LAYER_ROADMAP §5.1 |
| A8 | R2 sense-splitter = **heuristic per-dict**, deterministic, no LLM. | RESEARCH_LAYER_ROADMAP §5.1 |
| A1 | KRM license → **CC-BY-SA-4.0** (full legalcode replaced the GPL text). | KRM/LICENSE |
| A3 | **Full CC-BY-SA-4.0 legalcode** applied to 21 repos (6 documented + 15 M3) — GitHub now auto-detects the license. | */LICENSE |
| A4 | Not-yet-on-GitHub dicts (IEG/MWE/PE/PGN/SNP/YAT) **deferred to future work**; the "scan-only" framing was flagged inaccurate (re-check status before ingest). | LEXICOGRAPHY_ROADMAP §11 |
| A5 | **PD included** — its `a-` volumes are the whole practical dictionary; ingestion underway in `csl-pywork`. | LEXICOGRAPHY_ROADMAP §11 |
| B1 | Dict codes identified: **FRI** = Frish (Sanskrit Reader) · **KNA** = Knauer · **KOW** = Kossowich · **LRV** = Vaidya *Sanskrit-English Dictionary*. | LEXICOGRAPHY_ROADMAP §11.5; memory |
| B3 | `.github/ISSUE_TEMPLATE/*.yml` + PULL_REQUEST_TEMPLATE.md pushed to BOR/BUR/INM/KRM/BOP/MW72 (48 files). | csl-corrections `.ai_state.md`; SESSION_HANDOFF.md |
| B4 | SHS author = **Kulapati Jibananda Vidyāsāgara**. | SHS README/CLAUDE; M3 docs |
| B5 | ApteES = reverse-direction English→Sanskrit docs built (`{@en@}`/`<s>skt</s>`/Ⓐ-Ⓑ). | ApteES README/CLAUDE; M3 docs |
| D2 | **YES** — do the M1 refresh-script modernization as a backward-compatible refactor. | ROADMAP M1 / csl-pywork#53 |
| D3 | **YES** — wire the full `make_xml` XML-parse check into CI. | csl-pywork#51 |
| Research round-2 | Frequency join = **DCS** (local dump `GitHub/DCS`); practitioner hosting = **main dashboard page**; first hypothesis = **H1**; semantic fields = **Amarakośa-native**. | RESEARCH_LAYER_ROADMAP §7 |

### ✅ Post-L0 decisions (2026-06-03)

| # | Resolution | Documented in |
|---|---|---|
| L0-next | Next build = **Phase L0.7** content↔convention reformatting residual. | LEXICOGRAPHY_ROADMAP §10 |
| L0-patel-open | Patel's undone conventions (mahat-type/sakārānta/rephānta/ṛ-nipātita) → dims 31+ **and contribute back to `hwnorm1`** (Phase L0.9; one substantive PR, comment-noise-aware). | LEXICOGRAPHY_ROADMAP §10 |
| L0-paper | Convention-vs-content finding → **both** standalone methods note (PUBLICATIONS article 20) **and** Paper H §5. | PUBLICATIONS §6.2; articles/paper_H_*.md |
| L0-rigor | Paper-final tree → **add full Bayesian MCMC + NJ-posterior** (Phase L0-rigor), not just bootstrap-consensus UPGMA. | LEXICOGRAPHY_ROADMAP §10 |

---

*Engineering items trace to [`ROADMAP.md`](ROADMAP.md) + the [csl-corrections handoff](https://github.com/sanskrit-lexicon/csl-corrections/blob/master/.ai_state.md). Research items trace to [`LEXICOGRAPHY_ROADMAP.md`](LEXICOGRAPHY_ROADMAP.md) §11 and [`MICROSTRUCTURE-MACROSTRUCTURE.md`](MICROSTRUCTURE-MACROSTRUCTURE.md) §6.*
