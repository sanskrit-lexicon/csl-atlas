# csl-atlas — Atlas of the Cologne Digital Sanskrit Lexicons

An interactive companion to the [CDSL](https://www.sanskrit-lexicon.uni-koeln.de/) — comparative microstructural analysis of nine Sanskrit dictionaries.

**Status:** scaffold (2026-05-23). Built locally by Claude during a 4-hour autonomous session. Awaiting [@gasyoun](https://github.com/gasyoun) review before push to `github.com/sanskrit-lexicon/csl-atlas`.

---

## What this is

Companion microsite to the [MW microanalysis paper(s)](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis). Static + interactive. Two reader paths:

- **Paper tour:** read along with each of the four framework papers ([Wiegand](src/papers/wiegand.md) · [Atkins-Rundell](src/papers/atkins-rundell.md) · [Hausmann](src/papers/hausmann.md) · [Grounded](src/papers/grounded.md))
- **Tools:** explore standalone visualisations — [Matrix Explorer](src/tools/matrix-explorer.md), [Lineage Sankey](src/tools/lineage-sankey.md), [Typology Treemap](src/tools/typology-treemap.md), [Lexicographic Timeline](src/tools/timeline.md), [Type Comparator](src/tools/type-comparator.md), [Citation Tracer](src/tools/citation-tracer.md).

URL structure (Decision 25): English at root, Russian under `/ru/`.

```
/                        landing (EN)
/tools/heatmap           18×14 matrix explorer (EN)
/tools/lineage-sankey    PWG→MW Sankey (EN)
/papers/wiegand          Wiegand paper page (EN)
/ru/                     landing (RU)
/ru/tools/heatmap        Matrix explorer (RU)
...
```

---

## Coverage (Phase 4 atlas — 9 dicts)

| Repo | Title | Date | Status |
|---|---|---|---|
| [MW](https://github.com/sanskrit-lexicon/MWS) | Monier-Williams Sanskrit-English Dictionary | 1899 | ✅ ready (this scaffold targets MW data) |
| [PWG](https://github.com/sanskrit-lexicon/PWG) | Petersburg Sanskrit-Wörterbuch | 1855–75 | data ingested; chapter TODO |
| [PWK](https://github.com/sanskrit-lexicon/PWK) | Petersburg *Kürzerer Fassung* | 1879–89 | data ingested; chapter TODO |
| [AP](https://github.com/sanskrit-lexicon/AP) | Apte *Practical* Sanskrit-English | 1957 | data ingested; chapter TODO |
| [WIL](https://github.com/sanskrit-lexicon/WIL) | Wilson Sanskrit-English | 1832 | data ingested; chapter TODO |
| [SKD](https://github.com/sanskrit-lexicon/SKD) | *Śabdakalpadruma* (Sanskrit-Sanskrit) | 1822–58 | data ingested; chapter TODO |
| [VCP](https://github.com/sanskrit-lexicon/vcp) | *Vācaspatya* (Sanskrit-Sanskrit) | 1873–84 | data ingested; chapter TODO |
| [ARMH](https://github.com/sanskrit-lexicon/armh) | Halāyudha's *Abhidhānaratnamālā* | ~10th c. | data ingested; chapter TODO |
| [ABCH](https://github.com/sanskrit-lexicon/abch) | Hemacandra's *Abhidhānacintāmaṇi* | ~12th c. | data ingested; chapter TODO |

Each dictionary gets a chapter; each Tier-1 figure has a per-dictionary variant and a cross-dictionary comparative variant.

---

## Tech stack

- [**Observable Framework**](https://observablehq.com/framework) (per [Decision 10](https://github.com/sanskrit-lexicon/MWS/blob/docs-pass/papers/microanalysis/VISUALISATIONS.md#decision-10--microsite-stack-observable-framework))
- Data: copies of the JSON exports from `MWS/papers/microanalysis/figures/data/` (regenerable via `scripts/sync-data.sh`)
- Palette: copied from `MWS/papers/microanalysis/figures/palette-tokens.json`; rebuilt via `scripts/build-palette.sh`
- i18n: locale-prefixed routes (`/`, `/ru/`); strings in `src/locales/{en,ru}.json`
- Deployment: GitHub Pages on push to `main` (workflow in `.github/workflows/build-and-deploy.yml`)

---

## Local development

```bash
npm install
npm run dev      # starts dev server on http://localhost:3000
npm run build    # produces dist/ for GitHub Pages
```

(See [Observable Framework docs](https://observablehq.com/framework/getting-started) for full reference.)

---

## Status checklist

- [x] Repo scaffolded
- [ ] `npm init` + `npm install @observablehq/framework`
- [ ] Landing page (EN + RU)
- [ ] Paper-tour pages (4 papers × 2 locales = 8 pages)
- [ ] Tool pages: matrix-explorer (Tier 1), lineage-sankey (Tier 1), typology-treemap (Tier 1), timeline (Tier 1), type-comparator (Tier 3), citation-tracer (Tier 3)
- [ ] Data sync from MWS
- [ ] Palette + Mermaid theme
- [ ] CI/CD: GitHub Actions
- [ ] Push to `sanskrit-lexicon/csl-atlas` after [@gasyoun](https://github.com/gasyoun) approval

---

## License

CC-BY-SA-4.0, matching [MWS](https://github.com/sanskrit-lexicon/MWS).

Source data: [CDSL csl-orig](https://github.com/sanskrit-lexicon/csl-orig), `mw.txt` 2026-05-23 and sibling dict files. All figures regenerate from JSON data via Python scripts in [MWS papers/microanalysis/figures/scripts/](https://github.com/sanskrit-lexicon/MWS/tree/docs-pass/papers/microanalysis/figures/scripts).
