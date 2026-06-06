---
title: Reader lookup
toc: false
---

# ${t("reader.lookup.title")}
${t("reader.lookup.description")}

```js
import { normalizeLookupQuery } from "../lib/lookup-normalize.js";
```

```js
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
```

```js
const lookup = FileAttachment("../data/dicts/lemma-lookup.json").json();
```

```js
const lang = view(Inputs.radio(["en", "ru"], { label: "Language", value: "en", format: d => d === "ru" ? "Russian" : "English" }));
const currentLanguage = lang === "ru" || lang === 1 || lang === "1" ? "ru" : "en";
const t = (key) => {
  const currentLocale = currentLanguage === "ru" ? localesRu : localesEn;
  const parts = key.split(".");
  let result = currentLocale;
  for (const part of parts) { if (result && result[part] !== undefined) result = result[part]; else return key; }
  return result;
};
```

```js
const hrefOf = ([dictIndex, records, line]) => {
  const code = lookup.dictionaries[dictIndex].code;
  return `${lookup.hrefBase}/${code}/${code}.txt#L${line}`;
};
const coverageText = entry => `${entry[1].length}/7`;
function lowerBoundLemma(lemma) {
  let lo = 0, hi = lookup.entries.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (lookup.entries[mid][0] < lemma) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
function findLemma(lemma) {
  const i = lowerBoundLemma(lemma);
  return lookup.entries[i]?.[0] === lemma ? lookup.entries[i] : null;
}
function findPrefix(prefix, limit = 80) {
  const out = [];
  for (let i = lowerBoundLemma(prefix); i < lookup.entries.length && out.length < limit; i++) {
    const entry = lookup.entries[i];
    if (!entry[0].startsWith(prefix)) break;
    out.push(entry);
  }
  return out;
}
```

```js
display(html`<div class="lookup-metrics">
  ${[
    [t("reader.lookup.indexed-lemmas"), lookup.count.toLocaleString()],
    [t("reader.lookup.dictionaries"), lookup.dictionaries.length],
    [t("reader.lookup.minimum-coverage"), `${lookup.minDicts}/7`],
    [t("reader.lookup.input-schemes"), lookup.inputSchemes.join(" + ")]
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
  width: 360,
  submit: false
}));
```

```js
const normalizedQuery = normalizeLookupQuery(query);
const exact = normalizedQuery.candidates.map(candidate => findLemma(candidate)).find(Boolean) ?? null;
const prefixBase = normalizedQuery.candidates.find(candidate => candidate.length >= 2) ?? "";
const prefixMatches = prefixBase ? findPrefix(prefixBase) : [];
const starterLemmas = ["agni", "Siva", "deva", "aMSa", "akza"];
const starterEntries = starterLemmas.map(lemma => findLemma(lemma)).filter(Boolean);
const shownEntries = exact ? [exact] : (query ? prefixMatches : starterEntries);
```

```js
display(html`<div class="lookup-status">
  ${query
    ? html`<span>${t("reader.lookup.normalized")}: <code>${normalizedQuery.candidates.join(" / ") || "none"}</code></span>
        <span>${exact ? t("reader.lookup.exact-match") : `${prefixMatches.length.toLocaleString()} ${t("reader.lookup.prefix-matches")}`}</span>`
    : html`<span>${t("reader.lookup.showing-examples")}</span>`}
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
      <h2>${entry[0]}</h2>
      <span>${t("reader.lookup.coverage")} ${coverageText(entry)}</span>
    </div>
    <div class="lookup-dicts">
      ${entry[1].map(tuple => {
        const [dictIndex, records, line, gender] = tuple;
        const dict = lookup.dictionaries[dictIndex];
        return html`<a class="lookup-dict" href=${hrefOf(tuple)} target="_blank" rel="noopener">
          <strong>${dict.label}</strong>
          <span>${records} ${records === 1 ? t("reader.lookup.record") : t("reader.lookup.records")}</span>
          ${gender ? html`<small>${t("reader.lookup.gender")}: ${gender}</small>` : html`<small>${t("reader.lookup.gender-unknown")}</small>`}
        </a>`;
      })}
    </div>
  </section>`)}
</div>`);
```

<div class="note">${t("reader.lookup.caveat")}</div>

<style>
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
.lookup-dict small {
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
.lookup-dict strong {
  color: var(--theme-foreground);
}
.lookup-dict small {
  font-size: .8rem;
}
@media (max-width: 640px) {
  .trust-block div {
    grid-template-columns: 1fr;
    gap: 2px;
  }
}
</style>

---

Generated by `npm run build-dict-comparison`. CC-BY-SA-4.0.
