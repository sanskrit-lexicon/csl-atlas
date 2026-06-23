---
title: Lemma dossier
toc: false
---

```js
import { normalizeLookupQuery, slp1ToIast } from "../lib/lookup-normalize.js";
import {
  findLemma,
  findPrefix,
  initialModeFromUrl,
  initialQueryFromUrl,
  loadCandidateShards,
  localeTranslator,
  normalizeLanguageChoice,
  normalizeLookupMode,
  shardIdForLemma,
  sourceHref
} from "../lib/lookup-ui.js";
```

```js
const coreDossierManifest = FileAttachment("../data/dicts/core-dossier/manifest.json").json();
const broadManifest = FileAttachment("../data/dicts/broad-headword/manifest.json").json();
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
const dcsSummaryManifest = FileAttachment("../data/dcs/lemma-summary/manifest.json").json();
```

```js
const broadShardLoaders = new Map([
  ["61", () => FileAttachment("../data/dicts/broad-headword/shards/61.json").json()],
  ["41", () => FileAttachment("../data/dicts/broad-headword/shards/41.json").json()],
  ["69", () => FileAttachment("../data/dicts/broad-headword/shards/69.json").json()],
  ["49", () => FileAttachment("../data/dicts/broad-headword/shards/49.json").json()],
  ["75", () => FileAttachment("../data/dicts/broad-headword/shards/75.json").json()],
  ["55", () => FileAttachment("../data/dicts/broad-headword/shards/55.json").json()],
  ["66", () => FileAttachment("../data/dicts/broad-headword/shards/66.json").json()],
  ["46", () => FileAttachment("../data/dicts/broad-headword/shards/46.json").json()],
  ["78", () => FileAttachment("../data/dicts/broad-headword/shards/78.json").json()],
  ["58", () => FileAttachment("../data/dicts/broad-headword/shards/58.json").json()],
  ["65", () => FileAttachment("../data/dicts/broad-headword/shards/65.json").json()],
  ["45", () => FileAttachment("../data/dicts/broad-headword/shards/45.json").json()],
  ["6f", () => FileAttachment("../data/dicts/broad-headword/shards/6f.json").json()],
  ["4f", () => FileAttachment("../data/dicts/broad-headword/shards/4f.json").json()],
  ["6b", () => FileAttachment("../data/dicts/broad-headword/shards/6b.json").json()],
  ["4b", () => FileAttachment("../data/dicts/broad-headword/shards/4b.json").json()],
  ["67", () => FileAttachment("../data/dicts/broad-headword/shards/67.json").json()],
  ["47", () => FileAttachment("../data/dicts/broad-headword/shards/47.json").json()],
  ["4e", () => FileAttachment("../data/dicts/broad-headword/shards/4e.json").json()],
  ["63", () => FileAttachment("../data/dicts/broad-headword/shards/63.json").json()],
  ["43", () => FileAttachment("../data/dicts/broad-headword/shards/43.json").json()],
  ["6a", () => FileAttachment("../data/dicts/broad-headword/shards/6a.json").json()],
  ["4a", () => FileAttachment("../data/dicts/broad-headword/shards/4a.json").json()],
  ["59", () => FileAttachment("../data/dicts/broad-headword/shards/59.json").json()],
  ["77", () => FileAttachment("../data/dicts/broad-headword/shards/77.json").json()],
  ["57", () => FileAttachment("../data/dicts/broad-headword/shards/57.json").json()],
  ["71", () => FileAttachment("../data/dicts/broad-headword/shards/71.json").json()],
  ["51", () => FileAttachment("../data/dicts/broad-headword/shards/51.json").json()],
  ["52", () => FileAttachment("../data/dicts/broad-headword/shards/52.json").json()],
  ["74", () => FileAttachment("../data/dicts/broad-headword/shards/74.json").json()],
  ["54", () => FileAttachment("../data/dicts/broad-headword/shards/54.json").json()],
  ["64", () => FileAttachment("../data/dicts/broad-headword/shards/64.json").json()],
  ["44", () => FileAttachment("../data/dicts/broad-headword/shards/44.json").json()],
  ["6e", () => FileAttachment("../data/dicts/broad-headword/shards/6e.json").json()],
  ["70", () => FileAttachment("../data/dicts/broad-headword/shards/70.json").json()],
  ["50", () => FileAttachment("../data/dicts/broad-headword/shards/50.json").json()],
  ["62", () => FileAttachment("../data/dicts/broad-headword/shards/62.json").json()],
  ["42", () => FileAttachment("../data/dicts/broad-headword/shards/42.json").json()],
  ["6d", () => FileAttachment("../data/dicts/broad-headword/shards/6d.json").json()],
  ["79", () => FileAttachment("../data/dicts/broad-headword/shards/79.json").json()],
  ["72", () => FileAttachment("../data/dicts/broad-headword/shards/72.json").json()],
  ["6c", () => FileAttachment("../data/dicts/broad-headword/shards/6c.json").json()],
  ["76", () => FileAttachment("../data/dicts/broad-headword/shards/76.json").json()],
  ["53", () => FileAttachment("../data/dicts/broad-headword/shards/53.json").json()],
  ["7a", () => FileAttachment("../data/dicts/broad-headword/shards/7a.json").json()],
  ["73", () => FileAttachment("../data/dicts/broad-headword/shards/73.json").json()],
  ["68", () => FileAttachment("../data/dicts/broad-headword/shards/68.json").json()],
  ["other", () => FileAttachment("../data/dicts/broad-headword/shards/other.json").json()]
]);

const coreDossierShardLoaders = new Map([
  ["61", () => FileAttachment("../data/dicts/core-dossier/shards/61.json").json()],
  ["41", () => FileAttachment("../data/dicts/core-dossier/shards/41.json").json()],
  ["69", () => FileAttachment("../data/dicts/core-dossier/shards/69.json").json()],
  ["49", () => FileAttachment("../data/dicts/core-dossier/shards/49.json").json()],
  ["75", () => FileAttachment("../data/dicts/core-dossier/shards/75.json").json()],
  ["55", () => FileAttachment("../data/dicts/core-dossier/shards/55.json").json()],
  ["66", () => FileAttachment("../data/dicts/core-dossier/shards/66.json").json()],
  ["46", () => FileAttachment("../data/dicts/core-dossier/shards/46.json").json()],
  ["78", () => FileAttachment("../data/dicts/core-dossier/shards/78.json").json()],
  ["58", () => FileAttachment("../data/dicts/core-dossier/shards/58.json").json()],
  ["65", () => FileAttachment("../data/dicts/core-dossier/shards/65.json").json()],
  ["45", () => FileAttachment("../data/dicts/core-dossier/shards/45.json").json()],
  ["6f", () => FileAttachment("../data/dicts/core-dossier/shards/6f.json").json()],
  ["4f", () => FileAttachment("../data/dicts/core-dossier/shards/4f.json").json()],
  ["6b", () => FileAttachment("../data/dicts/core-dossier/shards/6b.json").json()],
  ["4b", () => FileAttachment("../data/dicts/core-dossier/shards/4b.json").json()],
  ["67", () => FileAttachment("../data/dicts/core-dossier/shards/67.json").json()],
  ["47", () => FileAttachment("../data/dicts/core-dossier/shards/47.json").json()],
  ["4e", () => FileAttachment("../data/dicts/core-dossier/shards/4e.json").json()],
  ["63", () => FileAttachment("../data/dicts/core-dossier/shards/63.json").json()],
  ["43", () => FileAttachment("../data/dicts/core-dossier/shards/43.json").json()],
  ["6a", () => FileAttachment("../data/dicts/core-dossier/shards/6a.json").json()],
  ["4a", () => FileAttachment("../data/dicts/core-dossier/shards/4a.json").json()],
  ["59", () => FileAttachment("../data/dicts/core-dossier/shards/59.json").json()],
  ["77", () => FileAttachment("../data/dicts/core-dossier/shards/77.json").json()],
  ["57", () => FileAttachment("../data/dicts/core-dossier/shards/57.json").json()],
  ["71", () => FileAttachment("../data/dicts/core-dossier/shards/71.json").json()],
  ["51", () => FileAttachment("../data/dicts/core-dossier/shards/51.json").json()],
  ["52", () => FileAttachment("../data/dicts/core-dossier/shards/52.json").json()],
  ["74", () => FileAttachment("../data/dicts/core-dossier/shards/74.json").json()],
  ["54", () => FileAttachment("../data/dicts/core-dossier/shards/54.json").json()],
  ["64", () => FileAttachment("../data/dicts/core-dossier/shards/64.json").json()],
  ["44", () => FileAttachment("../data/dicts/core-dossier/shards/44.json").json()],
  ["6e", () => FileAttachment("../data/dicts/core-dossier/shards/6e.json").json()],
  ["70", () => FileAttachment("../data/dicts/core-dossier/shards/70.json").json()],
  ["50", () => FileAttachment("../data/dicts/core-dossier/shards/50.json").json()],
  ["62", () => FileAttachment("../data/dicts/core-dossier/shards/62.json").json()],
  ["42", () => FileAttachment("../data/dicts/core-dossier/shards/42.json").json()],
  ["6d", () => FileAttachment("../data/dicts/core-dossier/shards/6d.json").json()],
  ["79", () => FileAttachment("../data/dicts/core-dossier/shards/79.json").json()],
  ["72", () => FileAttachment("../data/dicts/core-dossier/shards/72.json").json()],
  ["6c", () => FileAttachment("../data/dicts/core-dossier/shards/6c.json").json()],
  ["76", () => FileAttachment("../data/dicts/core-dossier/shards/76.json").json()],
  ["53", () => FileAttachment("../data/dicts/core-dossier/shards/53.json").json()],
  ["7a", () => FileAttachment("../data/dicts/core-dossier/shards/7a.json").json()],
  ["73", () => FileAttachment("../data/dicts/core-dossier/shards/73.json").json()],
  ["68", () => FileAttachment("../data/dicts/core-dossier/shards/68.json").json()],
  ["other", () => FileAttachment("../data/dicts/core-dossier/shards/other.json").json()]
]);

const dcsSummaryShardLoaders = new Map([
  ["61", () => FileAttachment("../data/dcs/lemma-summary/shards/61.json").json()],
  ["41", () => FileAttachment("../data/dcs/lemma-summary/shards/41.json").json()],
  ["69", () => FileAttachment("../data/dcs/lemma-summary/shards/69.json").json()],
  ["49", () => FileAttachment("../data/dcs/lemma-summary/shards/49.json").json()],
  ["75", () => FileAttachment("../data/dcs/lemma-summary/shards/75.json").json()],
  ["55", () => FileAttachment("../data/dcs/lemma-summary/shards/55.json").json()],
  ["66", () => FileAttachment("../data/dcs/lemma-summary/shards/66.json").json()],
  ["46", () => FileAttachment("../data/dcs/lemma-summary/shards/46.json").json()],
  ["78", () => FileAttachment("../data/dcs/lemma-summary/shards/78.json").json()],
  ["58", () => FileAttachment("../data/dcs/lemma-summary/shards/58.json").json()],
  ["65", () => FileAttachment("../data/dcs/lemma-summary/shards/65.json").json()],
  ["45", () => FileAttachment("../data/dcs/lemma-summary/shards/45.json").json()],
  ["6f", () => FileAttachment("../data/dcs/lemma-summary/shards/6f.json").json()],
  ["4f", () => FileAttachment("../data/dcs/lemma-summary/shards/4f.json").json()],
  ["6b", () => FileAttachment("../data/dcs/lemma-summary/shards/6b.json").json()],
  ["4b", () => FileAttachment("../data/dcs/lemma-summary/shards/4b.json").json()],
  ["67", () => FileAttachment("../data/dcs/lemma-summary/shards/67.json").json()],
  ["47", () => FileAttachment("../data/dcs/lemma-summary/shards/47.json").json()],
  ["4e", () => FileAttachment("../data/dcs/lemma-summary/shards/4e.json").json()],
  ["63", () => FileAttachment("../data/dcs/lemma-summary/shards/63.json").json()],
  ["43", () => FileAttachment("../data/dcs/lemma-summary/shards/43.json").json()],
  ["6a", () => FileAttachment("../data/dcs/lemma-summary/shards/6a.json").json()],
  ["4a", () => FileAttachment("../data/dcs/lemma-summary/shards/4a.json").json()],
  ["59", () => FileAttachment("../data/dcs/lemma-summary/shards/59.json").json()],
  ["77", () => FileAttachment("../data/dcs/lemma-summary/shards/77.json").json()],
  ["57", () => FileAttachment("../data/dcs/lemma-summary/shards/57.json").json()],
  ["71", () => FileAttachment("../data/dcs/lemma-summary/shards/71.json").json()],
  ["51", () => FileAttachment("../data/dcs/lemma-summary/shards/51.json").json()],
  ["52", () => FileAttachment("../data/dcs/lemma-summary/shards/52.json").json()],
  ["74", () => FileAttachment("../data/dcs/lemma-summary/shards/74.json").json()],
  ["54", () => FileAttachment("../data/dcs/lemma-summary/shards/54.json").json()],
  ["64", () => FileAttachment("../data/dcs/lemma-summary/shards/64.json").json()],
  ["44", () => FileAttachment("../data/dcs/lemma-summary/shards/44.json").json()],
  ["6e", () => FileAttachment("../data/dcs/lemma-summary/shards/6e.json").json()],
  ["70", () => FileAttachment("../data/dcs/lemma-summary/shards/70.json").json()],
  ["50", () => FileAttachment("../data/dcs/lemma-summary/shards/50.json").json()],
  ["62", () => FileAttachment("../data/dcs/lemma-summary/shards/62.json").json()],
  ["42", () => FileAttachment("../data/dcs/lemma-summary/shards/42.json").json()],
  ["6d", () => FileAttachment("../data/dcs/lemma-summary/shards/6d.json").json()],
  ["79", () => FileAttachment("../data/dcs/lemma-summary/shards/79.json").json()],
  ["72", () => FileAttachment("../data/dcs/lemma-summary/shards/72.json").json()],
  ["6c", () => FileAttachment("../data/dcs/lemma-summary/shards/6c.json").json()],
  ["76", () => FileAttachment("../data/dcs/lemma-summary/shards/76.json").json()],
  ["53", () => FileAttachment("../data/dcs/lemma-summary/shards/53.json").json()],
  ["7a", () => FileAttachment("../data/dcs/lemma-summary/shards/7a.json").json()],
  ["73", () => FileAttachment("../data/dcs/lemma-summary/shards/73.json").json()],
  ["68", () => FileAttachment("../data/dcs/lemma-summary/shards/68.json").json()],
  ["other", () => FileAttachment("../data/dcs/lemma-summary/shards/other.json").json()]
]);
```

```js
const lang = view(Inputs.select(["en", "ru"], {
  label: "Language",
  value: "en",
  format: value => value === "ru" ? "Russian" : "English"
}));
```

```js
const currentLanguage = normalizeLanguageChoice(lang);
const currentLocale = currentLanguage === "ru" ? localesRu : localesEn;
const t = localeTranslator(currentLocale);
```

```js
display(html`<h1>${t("phase2.dossier.title")}</h1>
<p>${t("phase2.dossier.description")}</p>`);
```

```js
const rawLookupMode = view(Inputs.select(["core", "broad"], {
  label: t("phase2.dossier.scope"),
  value: initialModeFromUrl(),
  format: value => value === "broad" ? t("phase2.dossier.scope-broad") : t("phase2.dossier.scope-core")
}));
const lookupMode = normalizeLookupMode(rawLookupMode);
```

```js
const activeManifest = lookupMode === "broad" ? broadManifest : coreDossierManifest;
const activeDictionaries = activeManifest.dictionaries;
const activeDictionaryCount = activeDictionaries.length;
const coreDictByCode = new Map(coreDossierManifest.dictionaries.map(d => [d.code, { sourceLinkMode: "github", ...d }]));
const broadDictByIndex = new Map(broadManifest.dictionaries.map((d, i) => [i, d]));
```

```js
display(html`<section class="trust-block" aria-labelledby="dossier-trust-title">
  <h2 id="dossier-trust-title">${t("phase2.dossier.trust-title")}</h2>
  <dl>
    ${[
      [t("phase2.dossier.trust-evidence-label"), t("phase2.dossier.trust-evidence")],
      [t("phase2.dossier.trust-limitations-label"), t("phase2.dossier.trust-limitations")],
      [t("phase2.dossier.trust-validation-label"), t("phase2.dossier.trust-validation")],
      [t("phase2.dossier.trust-owner-label"), t("phase2.dossier.trust-owner")],
      [t("phase2.dossier.trust-next-use-label"), t("phase2.dossier.trust-next-use")]
    ].map(([label, value]) => html`<div>
      <dt>${label}</dt>
      <dd>${value}</dd>
    </div>`)}
  </dl>
</section>`);
```

```js
const dictionaryLabels = activeDictionaries.map(d => d.label).join(", ");
display(html`<div class="note">
  ${lookupMode === "broad"
    ? html`${t("phase2.dossier.broad-note")} <b>${broadManifest.count.toLocaleString()}</b> ${t("phase2.dossier.lemmas")} ${t("phase2.dossier.across")} <b>${activeDictionaryCount}</b> ${t("phase2.dossier.dictionaries")}.`
    : html`${t("phase2.dossier.core-note")} <b>${coreDossierManifest.count.toLocaleString()}</b> ${t("phase2.dossier.lemmas")} ${t("phase2.dossier.in-at-least")} <b>${coreDossierManifest.minDicts}</b> ${t("phase2.dossier.of")} <b>${activeDictionaryCount}</b> ${t("phase2.dossier.dictionaries")} (${dictionaryLabels}).`}
</div>`);
```

```js
function hrefOf(dict, line) {
  return sourceHref(dict, line, activeManifest.hrefBase);
}
function dictBadges(dict, line) {
  const badges = [];
  if (dict?.deprecated) badges.push(t("phase2.dossier.deprecated"));
  if (dict?.sourceLinkMode === "local-only") badges.push(t("phase2.dossier.local-only"));
  if (!hrefOf(dict, line)) badges.push(t("phase2.dossier.no-source-link"));
  return [...new Set(badges)];
}
function coreEntry(e) {
  return {
    l: e.l,
    c: e.c,
    dicts: e.d.map(([code, records, line, gender]) => ({
      dict: coreDictByCode.get(code) ?? { code, label: code.toUpperCase(), sourceLinkMode: "github" },
      records,
      line,
      gender
    }))
  };
}
function broadEntry(entry) {
  const dicts = entry[1].map(([dictIndex, records, line]) => ({
    dictIndex,
    dict: broadDictByIndex.get(dictIndex),
    records,
    line,
    gender: null
  }));
  return {
    l: entry[0],
    c: dicts.length,
    dicts: dicts.sort((a, b) => {
      const ay = a.dict?.startYear ?? a.dict?.year ?? 9999;
      const by = b.dict?.startYear ?? b.dict?.year ?? 9999;
      return ay - by || String(a.dict?.code).localeCompare(String(b.dict?.code));
    })
  };
}
```

```js
const query = view(Inputs.text({
  label: t("phase2.dossier.lemma"),
  placeholder: t("phase2.dossier.placeholder"),
  value: initialQueryFromUrl(),
  width: 320,
  submit: false
}));
```

```js
const q = (query ?? "").trim();
const normalizedQuery = normalizeLookupQuery(q);
const internalQueries = normalizedQuery.candidates;
const displayQuery = slp1ToIast(normalizedQuery.normalized) || q;
const activeShardLoaders = lookupMode === "broad" ? broadShardLoaders : coreDossierShardLoaders;
const entriesByShard = await loadCandidateShards(internalQueries, activeShardLoaders);
const entriesForCandidate = candidate => entriesByShard.get(shardIdForLemma(candidate, activeShardLoaders)) ?? [];
const exact = internalQueries.map(candidate => findLemma(entriesForCandidate(candidate), candidate)).find(Boolean) ?? null;
const prefixMatches = internalQueries
  .filter(candidate => candidate.length >= 1)
  .map(candidate => findPrefix(entriesForCandidate(candidate), candidate, 200))
  .find(entries => entries.length) ?? [];
const matchedEntries = q
  ? (exact ? [exact] : prefixMatches)
  : activeManifest.sampleEntries ?? [];
const matches = lookupMode === "broad" ? matchedEntries.map(broadEntry) : matchedEntries.map(coreEntry);
const shown = matches.slice(0, 200);
const dcsEntriesByShard = await loadCandidateShards(shown.map(entry => entry.l), dcsSummaryShardLoaders);
const dcsMap = new Map([...dcsEntriesByShard.values()].flat());
```

```js
display(html`<p class="dossier-status">
  ${q
    ? lookupMode === "broad"
      ? `${matches.length.toLocaleString()} ${t("phase2.dossier.broad-matches")} “${displayQuery}”`
      : `${matches.length.toLocaleString()} ${t("phase2.dossier.matches")} “${displayQuery}”`
    : lookupMode === "broad"
      ? t("phase2.dossier.showing-broad-examples")
      : t("phase2.dossier.showing-core-examples")}
  ${matches.length > shown.length ? html` · ${t("phase2.dossier.showing-first")} ${shown.length}` : ""}
</p>`);
```

```js
display(html`<div class="dossier-grid">
  ${shown.map(e => {
    const dcs = dcsMap.get(e.l);
    return html`<section class="lemma-card">
      <h3>${slp1ToIast(e.l)} <span class="cov">${t("phase2.dossier.in")} ${e.c}/${activeDictionaryCount}</span></h3>
      <div class="chips">
        ${e.dicts.map(({ dictIndex, dict, records, line, gender }) => {
          const link = hrefOf(dict, line);
          const badges = dictBadges(dict, line);
          const content = html`<b>${dict?.label ?? dict?.code ?? `#${dictIndex}`}</b>
            <span>${records}×${gender ? " · " + gender : lookupMode === "broad" ? " · " + t("phase2.dossier.headword-only") : ""}</span>
            ${badges.length ? html`<em>${badges.join(" · ")}</em>` : ""}`;
          return link
            ? html`<a class="chip" href=${link} target="_blank" rel="noopener">${content}</a>`
            : html`<span class="chip chip-muted">${content}</span>`;
        })}
        ${dcs ? html`<a class="chip chip-dcs" href="https://github.com/gasyoun/VisualDCS" target="_blank" rel="noopener"><b>DCS</b><span>band ${dcs.freqBand}/5</span></a>` : ""}
      </div>
    </section>`;
  })}
</div>`);
```

<style>
.trust-block { border-left: 4px solid color-mix(in srgb, var(--theme-foreground), transparent 55%); padding: 4px 0 4px 14px; margin: 10px 0 18px; }
.trust-block h2 { font-size: 1rem; margin: 0 0 8px; }
.trust-block dl { display: grid; gap: 6px; margin: 0; }
.trust-block div { display: grid; grid-template-columns: minmax(120px, 0.24fr) 1fr; gap: 10px; }
.trust-block dt { font-weight: 700; }
.trust-block dd, .dossier-status, .chip span, .chip em { color: var(--theme-foreground-muted); }
.trust-block dd { margin: 0; }
.dossier-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 12px; margin: 12px 0 24px; }
.lemma-card { border: 1px solid var(--theme-foreground-faint); border-radius: 8px; padding: 12px; background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%); }
.lemma-card h3 { margin: 0 0 8px; font-size: 1.05rem; overflow-wrap: anywhere; }
.lemma-card .cov { color: var(--theme-foreground-muted); font-size: .8rem; font-weight: 400; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { display: inline-flex; flex-wrap: wrap; gap: 5px; align-items: baseline; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--theme-foreground-faint); text-decoration: none; font-size: .82rem; }
.chip em { font-size: .74rem; font-style: normal; }
.chip-muted { background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 4%); }
.chip-dcs { border-color: #2ca02c; }
.chip-dcs b { color: #2ca02c; }
.chip-dcs span { color: #2ca02c; opacity: .75; }
@media (max-width: 640px) {
  .trust-block div { grid-template-columns: 1fr; gap: 2px; }
}
</style>

---

Generated by `npm run build-dict-comparison` and `npm run build-broad-headword-lookup`. CC-BY-SA-4.0.
