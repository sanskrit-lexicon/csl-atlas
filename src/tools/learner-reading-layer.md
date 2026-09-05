_Created: 13-06-2026 · Last updated: 05-09-2026_

---
title: Learner's reading layer
toc: false
---

# ${t("learner.title")}
${t("learner.description")}

```js
import { normalizeLookupQuery, slp1ToIast } from "../lib/lookup-normalize.js";
```

```js
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
```

```js
const idx = FileAttachment("../data/learner/learner-index.json").json();
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
const bandByNum = Object.fromEntries(idx.bandLegend.map(b => [b.band, b]));
const grSet = new Set(idx.grammarReliableCodes);
const bandLabel = b => currentLanguage === "ru" ? bandByNum[b].ru : bandByNum[b].en;
const bandPriority = b => currentLanguage === "ru" ? bandByNum[b].priorityRu : bandByNum[b].priorityEn;
const sourceHref = src => src ? `${idx.hrefBase}/${src[0]}/${src[0]}.txt#L${src[1]}` : null;

function lowerBound(lemma) {
  let lo = 0, hi = idx.entries.length;
  while (lo < hi) { const mid = (lo + hi) >> 1; if (idx.entries[mid].l < lemma) lo = mid + 1; else hi = mid; }
  return lo;
}
function findLemma(lemma) { const i = lowerBound(lemma); return idx.entries[i]?.l === lemma ? idx.entries[i] : null; }
function findPrefix(prefix, limit = 60) {
  const out = [];
  for (let i = lowerBound(prefix); i < idx.entries.length && out.length < limit; i++) {
    if (!idx.entries[i].l.startsWith(prefix)) break;
    out.push(idx.entries[i]);
  }
  return out;
}
```

```js
display(html`<div class="learner-metrics">
  ${[
    [t("learner.metric.indexed"), idx.counts.recordCount.toLocaleString()],
    [t("learner.metric.with-frequency"), idx.counts.withFrequency.toLocaleString()],
    [t("learner.metric.grammar-reliable"), idx.grammarReliableCodes.length],
    [t("learner.metric.min-coverage"), `${idx.minDicts}/7`]
  ].map(([label, value]) => html`<div class="learner-metric"><strong>${value}</strong><span>${label}</span></div>`)}
</div>`);
```

```js
display(html`<section class="trust-block" aria-labelledby="learner-trust-title">
  <h2 id="learner-trust-title">${t("learner.trust-title")}</h2>
  <dl>
    ${[
      [t("learner.trust-evidence-label"), t("learner.trust-evidence")],
      [t("learner.trust-limitations-label"), t("learner.trust-limitations")],
      [t("learner.trust-validation-label"), t("learner.trust-validation")],
      [t("learner.trust-owner-label"), t("learner.trust-owner")],
      [t("learner.trust-next-use-label"), t("learner.trust-next-use")]
    ].map(([label, value]) => html`<div><dt>${label}</dt><dd>${value}</dd></div>`)}
  </dl>
</section>`);
```

```js
display(html`<div class="learner-legend">
  <h3>${t("learner.legend-title")}</h3>
  <div class="learner-bands">
    ${idx.bandLegend.filter(b => b.band >= 1).map(b => html`<div class="learner-band band-${b.band}">
      <strong>${bandLabel(b.band)}</strong>
      <span>${t("learner.legend-occurrences")}: ${b.range}</span>
      <small>${bandPriority(b.band)} · ${(idx.counts.byBand[b.band] ?? 0).toLocaleString()} ${t("learner.legend-lemmas")}</small>
    </div>`)}
  </div>
</div>`);
```

```js
const query = view(Inputs.text({ label: t("learner.query"), placeholder: t("learner.placeholder"), width: 360, submit: false }));
```

```js
const browseBand = view(Inputs.select([0, 5, 4, 3, 2, 1], {
  label: t("learner.browse-band"), value: 0,
  format: b => b === 0 ? t("learner.browse-none") : `${b} · ${bandLabel(b)}`
}));
```

```js
const normalizedQuery = normalizeLookupQuery(query);
const exact = normalizedQuery.candidates.map(c => findLemma(c)).find(Boolean) ?? null;
const prefixBase = normalizedQuery.candidates.find(c => c.length >= 2) ?? "";
const prefixMatches = prefixBase ? findPrefix(prefixBase) : [];
const bandSample = browseBand >= 1
  ? idx.entries.filter(e => e.fb === browseBand).slice(0, 120)
  : [];
const starter = ["agni", "deva", "Darma", "kAla", "gam"].map(findLemma).filter(Boolean);
const shown = exact ? [exact] : (query ? prefixMatches : (browseBand >= 1 ? bandSample : starter));
```

```js
display(html`<div class="learner-status">
  ${query
    ? html`<span>${t("learner.normalized")}: <code>${normalizedQuery.candidates.join(" / ") || "none"}</code></span>
        <span>${exact ? t("learner.exact-match") : `${prefixMatches.length.toLocaleString()} ${t("learner.prefix-matches")}`}</span>`
    : (browseBand >= 1
        ? html`<span>${t("learner.showing-band")}: <strong>${browseBand} · ${bandLabel(browseBand)}</strong> (${bandSample.length}/${(idx.counts.byBand[browseBand] ?? 0).toLocaleString()})</span>`
        : html`<span>${t("learner.showing-examples")}</span>`)}
</div>`);
```

```js
if (query && !exact && !prefixMatches.length) {
  display(html`<div class="learner-empty"><strong>${t("learner.no-result")}</strong><span>${t("learner.no-result-note")}</span></div>`);
}
```

```js
display(html`<div class="learner-cards">
  ${shown.map(e => html`<section class="learner-card">
    <div class="learner-card-head">
      <h2>${slp1ToIast(e.l)}${e.g ? html` <small class="learner-gender">${e.g}</small>` : ""} <code style="font-size:.6em;color:var(--theme-foreground-muted);font-weight:400">${e.l}</code></h2>
      <span class="learner-band-chip band-${e.fb}">${e.fb >= 1 ? html`${bandLabel(e.fb)} · ${bandPriority(e.fb)}` : t("learner.not-in-corpus")}</span>
    </div>
    <div class="learner-card-body">
      <div class="learner-coverage">
        <span>${t("learner.coverage")} <strong>${e.c}/7</strong> · ${t("learner.grammar-reliable")} <strong>${e.gr}</strong></span>
        <div class="learner-dict-chips">
          ${e.d.map(code => html`<span class="learner-dict-chip ${grSet.has(code) ? "gr" : ""}">${code}</span>`)}
        </div>
      </div>
      ${e.src ? html`<a class="learner-source" href=${sourceHref(e.src)} target="_blank" rel="noopener">${t("learner.open-source")} ${e.src[0].toUpperCase()}</a>` : ""}
    </div>
  </section>`)}
</div>`);
```

<div class="note">${t("learner.caveat")}</div>

<style>
.learner-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin: 12px 0 18px; }
.learner-metric { border: 1px solid var(--theme-foreground-faint); border-radius: 8px; padding: 10px 12px; background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 3%); }
.learner-metric strong { display: block; font-size: 1.35rem; line-height: 1.2; }
.learner-metric span { color: var(--theme-foreground-muted); }
.trust-block { border-left: 4px solid color-mix(in srgb, var(--theme-foreground), transparent 55%); padding: 4px 0 4px 14px; margin: 10px 0 18px; }
.trust-block h2 { font-size: 1rem; margin: 0 0 8px; }
.trust-block dl { display: grid; gap: 6px; margin: 0; }
.trust-block div { display: grid; grid-template-columns: minmax(120px, 0.24fr) 1fr; gap: 10px; }
.trust-block dt { font-weight: 700; }
.trust-block dd { margin: 0; color: var(--theme-foreground-muted); }
.learner-legend { margin: 8px 0 16px; }
.learner-legend h3 { font-size: 1rem; margin: 0 0 8px; }
.learner-bands { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; }
.learner-band { border: 1px solid var(--theme-foreground-faint); border-left-width: 6px; border-radius: 8px; padding: 8px 10px; }
.learner-band strong { display: block; }
.learner-band span, .learner-band small { color: var(--theme-foreground-muted); display: block; font-size: .82rem; }
.band-5 { border-left-color: #2ca02c; }
.band-4 { border-left-color: #66bd63; }
.band-3 { border-left-color: #d9b300; }
.band-2 { border-left-color: #f08c00; }
.band-1 { border-left-color: #d9544d; }
.band-0 { border-left-color: var(--theme-foreground-faint); }
.learner-status { display: flex; flex-wrap: wrap; gap: 10px 18px; margin: 12px 0; color: var(--theme-foreground-muted); }
.learner-empty { border: 1px solid var(--theme-foreground-faint); border-radius: 8px; padding: 12px; margin: 12px 0; }
.learner-empty strong, .learner-empty span { display: block; }
.learner-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 12px; margin: 14px 0 22px; }
.learner-card { border: 1px solid var(--theme-foreground-faint); border-radius: 8px; padding: 12px; background: color-mix(in srgb, var(--theme-background), var(--theme-foreground) 2%); }
.learner-card-head { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px 12px; align-items: baseline; margin-bottom: 8px; }
.learner-card h2 { font-size: 1.2rem; margin: 0; overflow-wrap: anywhere; }
.learner-gender { font-size: .8rem; color: var(--theme-foreground-muted); font-weight: 400; }
.learner-band-chip { font-size: .76rem; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--theme-foreground-faint); border-left-width: 5px; }
.learner-card-body { display: grid; gap: 8px; }
.learner-coverage span { color: var(--theme-foreground-muted); font-size: .9rem; }
.learner-dict-chips { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 6px; }
.learner-dict-chip { font-size: .72rem; padding: 1px 6px; border-radius: 4px; border: 1px solid var(--theme-foreground-faint); color: var(--theme-foreground-muted); }
.learner-dict-chip.gr { color: var(--theme-foreground); border-color: color-mix(in srgb, #2ca02c, transparent 40%); }
.learner-source { font-size: .82rem; text-decoration: none; }
@media (max-width: 640px) { .trust-block div { grid-template-columns: 1fr; gap: 2px; } }
</style>

---

Generated by `npm run build-learner-index`. Joins `lemma-lookup.json` (dictionary coverage) with the DCS corpus frequency band (`data/dcs/dcs_lemma_summary.json`). CC-BY-SA-4.0.

_Dr. Mārcis Gasūns_
