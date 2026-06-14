---
title: Lemma dossier
toc: false
---

```js
import { normalizeLookupQuery, slp1ToIast } from "../lib/lookup-normalize.js";
```

```js
const dossier = FileAttachment("../data/dicts/lemma-dossier.json").json();
const broadManifest = FileAttachment("../data/dicts/broad-headword/manifest.json").json();
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
const dcsSummary = FileAttachment("../data/dcs/dcs_lemma_summary.json").json();
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
```

```js
const lang = view(Inputs.select(["en", "ru"], {
  label: "Language",
  value: "en",
  format: value => value === "ru" ? "Russian" : "English"
}));
```

```js
const languageValue = String(lang ?? "").toLowerCase();
const currentLanguage = lang === 1 || languageValue === "1" || languageValue === "ru" || languageValue === "russian" || languageValue === "русский" ? "ru" : "en";
const currentLocale = currentLanguage === "ru" ? localesRu : localesEn;
const t = ((locale) => (key) => {
  const parts = key.split(".");
  let result = locale;
  for (const part of parts) { if (result && result[part] !== undefined) result = result[part]; else return key; }
  return result;
})(currentLocale);
```

```js
display(html`<h1>${t("phase2.dossier.title")}</h1>
<p>${t("phase2.dossier.description")}</p>`);
```

```js
const rawLookupMode = view(Inputs.select(["core", "broad"], {
  label: t("phase2.dossier.scope"),
  value: "core",
  format: value => value === "broad" ? t("phase2.dossier.scope-broad") : t("phase2.dossier.scope-core")
}));
const lookupModeValue = String(rawLookupMode ?? "").toLowerCase();
const lookupMode = rawLookupMode === 1 || lookupModeValue === "1" || lookupModeValue === "broad" ? "broad" : "core";
```

```js
const activeManifest = lookupMode === "broad" ? broadManifest : dossier;
const activeDictionaries = activeManifest.dictionaries;
const activeDictionaryCount = activeDictionaries.length;
const dcsMap = dcsSummary?.lemmas ?? {};
const coreDictByCode = new Map(dossier.dictionaries.map(d => [d.code, { sourceLinkMode: "github", ...d }]));
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
    : html`${t("phase2.dossier.core-note")} <b>${dossier.count.toLocaleString()}</b> ${t("phase2.dossier.lemmas")} ${t("phase2.dossier.in-at-least")} <b>${dossier.minDicts}</b> ${t("phase2.dossier.of")} <b>${activeDictionaryCount}</b> ${t("phase2.dossier.dictionaries")} (${dictionaryLabels}).`}
</div>`);
```

```js
function shardIdForLemma(lemma) {
  const first = String(lemma ?? "")[0];
  if (!first) return "other";
  const id = first.charCodeAt(0).toString(16);
  return broadShardLoaders.has(id) ? id : "other";
}
function lowerBoundLemma(entries, lemma) {
  let lo = 0, hi = entries.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (entries[mid][0] < lemma) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
function findLemma(entries, lemma) {
  const i = lowerBoundLemma(entries, lemma);
  return entries[i]?.[0] === lemma ? entries[i] : null;
}
function findPrefix(entries, prefix, limit = 200) {
  const out = [];
  for (let i = lowerBoundLemma(entries, prefix); i < entries.length && out.length < limit; i++) {
    const entry = entries[i];
    if (!entry[0].startsWith(prefix)) break;
    out.push(entry);
  }
  return out;
}
function hrefOf(dict, line) {
  const sourceMode = dict?.sourceLinkMode ?? "github";
  return dict && line && sourceMode === "github" ? `${activeManifest.hrefBase}/${dict.code}/${dict.code}.txt#L${line}` : null;
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
const initialQuery = new URLSearchParams(globalThis.location?.search ?? "").get("q") ?? "";
const query = view(Inputs.text({
  label: t("phase2.dossier.lemma"),
  placeholder: t("phase2.dossier.placeholder"),
  value: initialQuery,
  width: 320,
  submit: false
}));
```

```js
const q = (query ?? "").trim();
const normalizedQuery = normalizeLookupQuery(q);
const internalQueries = normalizedQuery.candidates;
const displayQuery = slp1ToIast(normalizedQuery.normalized) || q;
const broadShardIdsForQuery = lookupMode === "broad"
  ? [...new Set(internalQueries.filter(candidate => candidate.length >= 1).map(shardIdForLemma))]
  : [];
const broadShards = broadShardIdsForQuery.length
  ? await Promise.all(broadShardIdsForQuery.map(id => broadShardLoaders.get(id)?.()).filter(Boolean))
  : [];
const broadEntriesByShard = new Map(broadShards.map(shard => [shard.shard, shard.entries]));
const broadEntriesForCandidate = candidate => broadEntriesByShard.get(shardIdForLemma(candidate)) ?? [];
const broadExact = internalQueries.map(candidate => findLemma(broadEntriesForCandidate(candidate), candidate)).find(Boolean) ?? null;
const broadPrefixBase = internalQueries.find(candidate => candidate.length >= 1) ?? "";
const broadMatches = q
  ? (broadExact ? [broadExact] : broadPrefixBase ? findPrefix(broadEntriesForCandidate(broadPrefixBase), broadPrefixBase) : [])
  : broadManifest.sampleEntries;
const coreMatches = q
  ? dossier.entries.filter(e => internalQueries.some(candidate => e.l.includes(candidate)))
  : dossier.entries.slice(0, 30);
const matches = lookupMode === "broad" ? broadMatches.map(broadEntry) : coreMatches.map(coreEntry);
const shown = matches.slice(0, 200);
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
    const dcs = dcsMap[e.l];
    return html`<section class="lemma-card">
      <h3>${slp1ToIast(e.l)} <span class="cov">${t("phase2.dossier.in")} ${e.c}/${activeDictionaryCount}</span></h3>
      <div class="chips">
        ${e.dicts.map(({ dict, records, line, gender }) => {
          const link = hrefOf(dict, line);
          const badges = dictBadges(dict, line);
          const content = html`<b>${dict?.label ?? dict?.code}</b>
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
