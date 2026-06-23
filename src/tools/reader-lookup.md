---
title: Reader lookup
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
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
```

```js
const coreLookupManifest = FileAttachment("../data/dicts/core-lookup/manifest.json").json();
const broadManifest = FileAttachment("../data/dicts/broad-headword/manifest.json").json();
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

const coreLookupShardLoaders = new Map([
  ["61", () => FileAttachment("../data/dicts/core-lookup/shards/61.json").json()],
  ["41", () => FileAttachment("../data/dicts/core-lookup/shards/41.json").json()],
  ["69", () => FileAttachment("../data/dicts/core-lookup/shards/69.json").json()],
  ["49", () => FileAttachment("../data/dicts/core-lookup/shards/49.json").json()],
  ["75", () => FileAttachment("../data/dicts/core-lookup/shards/75.json").json()],
  ["55", () => FileAttachment("../data/dicts/core-lookup/shards/55.json").json()],
  ["66", () => FileAttachment("../data/dicts/core-lookup/shards/66.json").json()],
  ["46", () => FileAttachment("../data/dicts/core-lookup/shards/46.json").json()],
  ["78", () => FileAttachment("../data/dicts/core-lookup/shards/78.json").json()],
  ["58", () => FileAttachment("../data/dicts/core-lookup/shards/58.json").json()],
  ["65", () => FileAttachment("../data/dicts/core-lookup/shards/65.json").json()],
  ["45", () => FileAttachment("../data/dicts/core-lookup/shards/45.json").json()],
  ["6f", () => FileAttachment("../data/dicts/core-lookup/shards/6f.json").json()],
  ["4f", () => FileAttachment("../data/dicts/core-lookup/shards/4f.json").json()],
  ["6b", () => FileAttachment("../data/dicts/core-lookup/shards/6b.json").json()],
  ["4b", () => FileAttachment("../data/dicts/core-lookup/shards/4b.json").json()],
  ["67", () => FileAttachment("../data/dicts/core-lookup/shards/67.json").json()],
  ["47", () => FileAttachment("../data/dicts/core-lookup/shards/47.json").json()],
  ["4e", () => FileAttachment("../data/dicts/core-lookup/shards/4e.json").json()],
  ["63", () => FileAttachment("../data/dicts/core-lookup/shards/63.json").json()],
  ["43", () => FileAttachment("../data/dicts/core-lookup/shards/43.json").json()],
  ["6a", () => FileAttachment("../data/dicts/core-lookup/shards/6a.json").json()],
  ["4a", () => FileAttachment("../data/dicts/core-lookup/shards/4a.json").json()],
  ["59", () => FileAttachment("../data/dicts/core-lookup/shards/59.json").json()],
  ["77", () => FileAttachment("../data/dicts/core-lookup/shards/77.json").json()],
  ["57", () => FileAttachment("../data/dicts/core-lookup/shards/57.json").json()],
  ["71", () => FileAttachment("../data/dicts/core-lookup/shards/71.json").json()],
  ["51", () => FileAttachment("../data/dicts/core-lookup/shards/51.json").json()],
  ["52", () => FileAttachment("../data/dicts/core-lookup/shards/52.json").json()],
  ["74", () => FileAttachment("../data/dicts/core-lookup/shards/74.json").json()],
  ["54", () => FileAttachment("../data/dicts/core-lookup/shards/54.json").json()],
  ["64", () => FileAttachment("../data/dicts/core-lookup/shards/64.json").json()],
  ["44", () => FileAttachment("../data/dicts/core-lookup/shards/44.json").json()],
  ["6e", () => FileAttachment("../data/dicts/core-lookup/shards/6e.json").json()],
  ["70", () => FileAttachment("../data/dicts/core-lookup/shards/70.json").json()],
  ["50", () => FileAttachment("../data/dicts/core-lookup/shards/50.json").json()],
  ["62", () => FileAttachment("../data/dicts/core-lookup/shards/62.json").json()],
  ["42", () => FileAttachment("../data/dicts/core-lookup/shards/42.json").json()],
  ["6d", () => FileAttachment("../data/dicts/core-lookup/shards/6d.json").json()],
  ["79", () => FileAttachment("../data/dicts/core-lookup/shards/79.json").json()],
  ["72", () => FileAttachment("../data/dicts/core-lookup/shards/72.json").json()],
  ["6c", () => FileAttachment("../data/dicts/core-lookup/shards/6c.json").json()],
  ["76", () => FileAttachment("../data/dicts/core-lookup/shards/76.json").json()],
  ["53", () => FileAttachment("../data/dicts/core-lookup/shards/53.json").json()],
  ["7a", () => FileAttachment("../data/dicts/core-lookup/shards/7a.json").json()],
  ["73", () => FileAttachment("../data/dicts/core-lookup/shards/73.json").json()],
  ["68", () => FileAttachment("../data/dicts/core-lookup/shards/68.json").json()],
  ["other", () => FileAttachment("../data/dicts/core-lookup/shards/other.json").json()]
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
display(html`<h1>${t("reader.lookup.title")}</h1>
<p>${t("reader.lookup.description")}</p>`);
```

```js
const rawLookupMode = view(Inputs.select(["core", "broad"], {
  label: t("reader.lookup.scope"),
  value: initialModeFromUrl(),
  format: value => value === "broad" ? t("reader.lookup.scope-broad") : t("reader.lookup.scope-core")
}));
const lookupMode = normalizeLookupMode(rawLookupMode);
```

```js
const activeManifest = lookupMode === "broad" ? broadManifest : coreLookupManifest;
const activeDictionaries = activeManifest.dictionaries;
const publicInputSchemes = (activeManifest.inputSchemes ?? []).filter(scheme => scheme !== "SLP1");
const scopeNote = lookupMode === "broad" ? t("reader.lookup.scope-note-broad") : t("reader.lookup.scope-note-core");
```

```js
function hrefOf(tuple, dictionaries = activeDictionaries, hrefBase = activeManifest.hrefBase) {
  const [dictIndex, , line] = tuple;
  const dict = dictionaries[dictIndex];
  return sourceHref(dict, line, hrefBase);
}
const coverageText = entry => `${entry[1].length}/${activeDictionaries.length}`;
function dictBadges(dict) {
  const badges = [];
  if (dict?.deprecated) badges.push(t("reader.lookup.deprecated"));
  if (dict?.sourceLinkMode === "local-only") badges.push(t("reader.lookup.local-only"));
  return badges;
}
```

```js
display(html`<p class="lookup-scope-note">${scopeNote}</p>
<div class="lookup-metrics">
  ${[
    [t("reader.lookup.indexed-lemmas"), activeManifest.count.toLocaleString()],
    [t("reader.lookup.dictionaries"), activeDictionaries.length],
    [t("reader.lookup.minimum-coverage"), `${activeManifest.minDicts}/${activeDictionaries.length}`],
    [t("reader.lookup.input-schemes"), publicInputSchemes.join(" + ")]
  ].map(([label, value]) => html`<div class="lookup-metric">
    <strong>${value}</strong>
    <span>${label}</span>
  </div>`)}
</div>`);
```

```js
display(html`<section class="trust-block" aria-labelledby="reader-lookup-trust-title">
  <h2 id="reader-lookup-trust-title">${t("reader.lookup.trust-title")}</h2>
  <dl>
    ${[
      [t("reader.lookup.trust-evidence-label"), t("reader.lookup.trust-evidence")],
      [t("reader.lookup.trust-limitations-label"), t("reader.lookup.trust-limitations")],
      [t("reader.lookup.trust-validation-label"), t("reader.lookup.trust-validation")],
      [t("reader.lookup.trust-owner-label"), t("reader.lookup.trust-owner")],
      [t("reader.lookup.trust-next-use-label"), t("reader.lookup.trust-next-use")]
    ].map(([label, value]) => html`<div>
      <dt>${label}</dt>
      <dd>${value}</dd>
    </div>`)}
  </dl>
</section>`);
```

```js
const query = view(Inputs.text({
  label: t("reader.lookup.query"),
  placeholder: t("reader.lookup.placeholder"),
  value: initialQueryFromUrl(),
  width: 360,
  submit: false
}));
```

```js
const normalizedQuery = normalizeLookupQuery(query);
const activeShardLoaders = lookupMode === "broad" ? broadShardLoaders : coreLookupShardLoaders;
const entriesByShard = await loadCandidateShards(normalizedQuery.candidates, activeShardLoaders);
const entriesForCandidate = candidate => entriesByShard.get(shardIdForLemma(candidate, activeShardLoaders)) ?? [];
const exact = normalizedQuery.candidates.map(candidate => findLemma(entriesForCandidate(candidate), candidate)).find(Boolean) ?? null;
const prefixMatches = normalizedQuery.candidates
  .filter(candidate => candidate.length >= 1)
  .map(candidate => findPrefix(entriesForCandidate(candidate), candidate))
  .find(matches => matches.length) ?? [];
const starterEntries = activeManifest.sampleEntries ?? [];
const shownEntries = exact ? [exact] : (query ? prefixMatches : starterEntries);
const displayQuery = slp1ToIast(normalizedQuery.normalized) || query;
```

```js
display(html`<div class="lookup-status">
  ${query
    ? html`<span>${t("reader.lookup.normalized")}: <code>${displayQuery || "none"}</code></span>
        <span>${exact ? t("reader.lookup.exact-match") : `${prefixMatches.length.toLocaleString()} ${t("reader.lookup.prefix-matches")}`}</span>`
    : html`<span>${lookupMode === "broad" ? t("reader.lookup.showing-broad-examples") : t("reader.lookup.showing-examples")}</span>`}
</div>`);
```

```js
if (query && !exact && !prefixMatches.length) {
  display(html`<div class="lookup-empty">
    <strong>${t("reader.lookup.no-result")}</strong>
    <span>${t("reader.lookup.no-result-note")}</span>
  </div>`);
}
```

```js
display(html`<div class="lookup-results">
  ${shownEntries.map(entry => html`<section class="lookup-entry">
    <div class="lookup-entry-head">
      <h2>${slp1ToIast(entry[0])}</h2>
      <span>${t("reader.lookup.coverage")} ${coverageText(entry)}</span>
    </div>
    <div class="lookup-dicts">
      ${entry[1].map(tuple => {
        const [dictIndex, records, , gender] = tuple;
        const dict = activeDictionaries[dictIndex];
        const link = hrefOf(tuple);
        const badges = dictBadges(dict);
        const content = html`<strong>${dict?.label ?? dict?.code ?? `#${dictIndex}`}</strong>
          <span>${records} ${records === 1 ? t("reader.lookup.record") : t("reader.lookup.records")}</span>
          ${lookupMode === "broad"
            ? html`<small>${t("reader.lookup.headword-only")}</small>`
            : gender ? html`<small>${t("reader.lookup.gender")}: ${gender}</small>` : html`<small>${t("reader.lookup.gender-unknown")}</small>`}
          ${badges.length ? html`<em>${badges.join(" · ")}</em>` : ""}`;
        return link
          ? html`<a class="lookup-dict" href=${link} target="_blank" rel="noopener">${content}</a>`
          : html`<span class="lookup-dict lookup-dict-muted">${content}</span>`;
      })}
    </div>
  </section>`)}
</div>`);
```

<div class="note">${lookupMode === "broad" ? t("reader.lookup.broad-caveat") : t("reader.lookup.caveat")}</div>

<style>
.lookup-scope-note {
  color: var(--theme-foreground-muted);
  margin: 8px 0 12px;
}
.lookup-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 12px 0 18px;
}
.lookup-metric {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 8px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%);
}
.lookup-metric strong {
  display: block;
  font-size: 1.35rem;
  line-height: 1.2;
}
.lookup-metric span,
.lookup-status,
.lookup-empty span,
.lookup-entry-head span,
.lookup-dict span,
.lookup-dict small,
.lookup-dict em {
  color: var(--theme-foreground-muted);
}
.lookup-status {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin: 12px 0;
}
.trust-block {
  border-left: 4px solid color-mix(in srgb, var(--theme-foreground), transparent 55%);
  padding: 4px 0 4px 14px;
  margin: 10px 0 18px;
}
.trust-block h2 {
  font-size: 1rem;
  margin: 0 0 8px;
}
.trust-block dl {
  display: grid;
  gap: 6px;
  margin: 0;
}
.trust-block div {
  display: grid;
  grid-template-columns: minmax(120px, 0.24fr) 1fr;
  gap: 10px;
}
.trust-block dt {
  font-weight: 700;
}
.trust-block dd {
  margin: 0;
  color: var(--theme-foreground-muted);
}
.lookup-empty {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 8px;
  padding: 12px;
  margin: 12px 0;
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%);
}
.lookup-empty strong,
.lookup-empty span {
  display: block;
}
.lookup-results {
  display: grid;
  gap: 14px;
  margin: 14px 0 22px;
}
.lookup-entry {
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 8px;
  padding: 12px;
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 2%);
}
.lookup-entry-head {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 8px 16px;
  align-items: baseline;
  margin-bottom: 10px;
}
.lookup-entry h2 {
  font-size: 1.25rem;
  margin: 0;
  overflow-wrap: anywhere;
}
.lookup-dicts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}
.lookup-dict {
  display: grid;
  gap: 2px;
  border: 1px solid var(--theme-foreground-faint);
  border-radius: 8px;
  padding: 8px 10px;
  text-decoration: none;
  min-height: 72px;
}
.lookup-dict-muted {
  background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 4%);
}
.lookup-dict strong {
  color: var(--theme-foreground);
}
.lookup-dict small,
.lookup-dict em {
  font-size: .8rem;
  font-style: normal;
}
@media (max-width: 640px) {
  .trust-block div {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>

---

Generated by `npm run build-dict-comparison` and `npm run build-broad-headword-lookup`. CC-BY-SA-4.0.
