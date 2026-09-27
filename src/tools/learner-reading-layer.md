_Created: 13-06-2026 · Last updated: 25-09-2026_

---
title: Learner's reading layer
toc: false
---

# ${t("learner.title")}
${t("learner.description")}

```js
import { normalizeLookupQuery, slp1ToIast } from "../lib/lookup-normalize.js";
import { csvDownloadButton } from "../lib/csv-download.js";
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
const L = (en, ru) => currentLanguage === "ru" ? ru : en;
const tierByCode = Object.fromEntries((idx.tierLegend ?? []).map(t => [t.tier, t]));
const senseText = s => s.t ?? L(`sense ${s.pos + 1} of the ancestor article`, `смысл ${s.pos + 1} статьи-источника`);
const vdcsStableId = p => p.k === "nominal" ? `vdcs:v1:nominal:${p.id}` : `vdcs:v1:verb:${p.id}`;
const cardCsvRow = e => ({
  lemma_iast: slp1ToIast(e.l),
  lemma_slp1: e.l,
  gender: e.g ?? "",
  band: e.fb,
  band_label_en: bandByNum[e.fb]?.en ?? "",
  tier: e.tier,
  dict_coverage: e.c,
  dict_grammar_reliable: e.gr,
  dictionaries: e.d.join(" "),
  senses_survival: e.s?.length ?? 0,
  senses_survived: e.s?.filter(s => s.sv).length ?? 0,
  survival_threshold: e.s ? idx.survivalThreshold : "",
  paradigm_id: e.p ? vdcsStableId(e.p) : "",
  paradigm_cells: e.p?.cells ?? "",
  roots_whitney: e.w?.map(r => r.iast).join(" ") ?? "",
  root_ganas: e.w?.map(r => r.gana ?? "-").join(" ") ?? "",
  homonyms_max: e.hm?.mx ?? "",
  absences: absences(e).map(([code]) => code).join(" ")
});
const cardCsvColumns = Object.keys(cardCsvRow(idx.entries[0]));
function absences(e) {
  const out = [];
  if (e.fb === 0) out.push([idx.absenceCodes.frequency, idx.absenceNotes.frequency]);
  if (!e.p) out.push([idx.absenceCodes.paradigm, idx.absenceNotes.paradigm]);
  if (!e.w) out.push([idx.absenceCodes.root, idx.absenceNotes.root]);
  if (!e.s) out.push([idx.absenceCodes.senses, idx.absenceNotes.senses]);
  if (!e.hm) out.push([idx.absenceCodes.homonyms, idx.absenceNotes.homonyms]);
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
display(html`<div class="learner-tiers">
  <h3>${L("Card completeness", "Полнота карточки")}</h3>
  <div class="learner-tier-row">
    ${(idx.tierLegend ?? []).map(t => html`<span class="learner-tier-chip tier-${t.tier}" title=${t.note}>
      <strong>${t.tier}</strong> ${currentLanguage === "ru" ? t.ru : t.en}
      <small>· ${(idx.counts.tiers?.[t.tier] ?? 0).toLocaleString()}</small>
    </span>`)}
  </div>
  <p class="learner-tier-note">${L(
    "Every missing layer is named with a reason code — an empty slot is a statement about the evidence, never a silent gap.",
    "Каждый отсутствующий слой назван кодом причины — пустой слот говорит о состоянии источников, а не молчит.")}</p>
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
      <span>
        ${tierByCode[e.tier] ? html`<span class="learner-tier-chip tier-${e.tier}" title=${tierByCode[e.tier].note}><strong>${e.tier}</strong> ${currentLanguage === "ru" ? tierByCode[e.tier].ru : tierByCode[e.tier].en}</span>` : ""}
        <span class="learner-band-chip band-${e.fb}">${e.fb >= 1 ? html`${bandLabel(e.fb)} · ${bandPriority(e.fb)}` : t("learner.not-in-corpus")}</span>
      </span>
    </div>
    <div class="learner-card-body">
      <div class="learner-coverage">
        <span>${t("learner.coverage")} <strong>${e.c}/7</strong> · ${t("learner.grammar-reliable")} <strong>${e.gr}</strong></span>
        <div class="learner-dict-chips">
          ${e.d.map(code => html`<span class="learner-dict-chip ${grSet.has(code) ? "gr" : ""}">${code}</span>`)}
        </div>
      </div>
      ${e.hm ? html`<div class="learner-homonym">⚠️ ${L("homonyms", "омонимия")}: ≤ ${e.hm.mx} ${L("in some dictionaries", "в части словарей")} — ${L("advisory and incomplete (400 of 9,839 candidates shipped); check the source links before trusting one merged card", "предупреждение неполно по построению (400 из 9 839 кандидатов); сверяйтесь с источником, прежде чем читать карточку как одно слово")}</div>` : ""}
      ${e.s ? html`<details class="learner-evidence" open=${e.tier === "A"}>
        <summary>${L("Survival-ranked senses", "Смыслы по выживаемости")} (${e.s.length}) · ${L("threshold", "порог")} ≥ ${idx.survivalThreshold}</summary>
        <ol class="learner-senses">
          ${e.s.slice(0, 5).map(s => html`<li>
            <span class="learner-sv ${s.sv ? "yes" : "no"}">${s.sv ? "✓" : "✗"}</span>
            ${senseText(s)}
            <small>· ${L("overlap", "пересечение")} ${s.ov} · ${s.e}${s.ci ? ` · ${L("cited", "с цитатой")}` : ""}</small>
          </li>`)}
        </ol>
        <p class="learner-caveat">${idx.survivalCaveat}</p>
      </details>` : ""}
      ${e.p || e.w ? html`<details class="learner-evidence">
        <summary>${L("Grammar evidence", "Грамматика")}</summary>
        <dl class="learner-grammar">
          ${e.p ? html`<div><dt>${L("Paradigm", "Парадигма")}</dt><dd>
            <code>${vdcsStableId(e.p)}</code> · ${e.p.cells} ${L("attested cells", "аттестованных форм")}
            ${e.p.alt ? html`<small> · ${L("alternatives disclosed", "показаны альтернативы")}: ${e.p.alt.map(a => html`<code>${vdcsStableId(a)}</code>`)} (${L("resolved by corpus tokens; an ID change here is visible, not silent", "выбран по корпусной частоте; смена ID здесь видима, а не тиха")})</small>` : ""}
          </dd></div>` : ""}
          ${e.w ? html`<div><dt>${L("Whitney root(s)", "Корни Уитни")}</dt><dd>
            ${e.w.map(r => html`<span class="learner-root"><code>${r.iast}</code> #${r.no}${r.gana ? html` · ${L("gaṇa", "гана")} ${r.gana}${r.clsUnc ? ` (${L("class uncertain", "класс не вполне надёжен")})` : ""}` : html` · ${L("gaṇa not recorded — never inferred", "гана не записана — не домысливается")}`}${e.w.length > 1 ? html` <small>(${L("homonym", "омоним")} ${r.hom})</small>` : ""}</span>`)}
            ${e.w.length > 1 ? html`<small>${L("All matching roots are shown — none is picked for you.", "Показаны все подходящие корни — выбор за вами.")}</small>` : ""}
          </dd></div>` : ""}
        </dl>
      </details>` : ""}
      ${absences(e).length ? html`<details class="learner-absences">
        <summary>${L("What this card does not have — and why", "Чего в карточке нет — и почему")} (${absences(e).length})</summary>
        <ul>${absences(e).map(([code, note]) => html`<li><code>${code}</code> — ${note}</li>`)}</ul>
      </details>` : ""}
      ${e.src ? html`<a class="learner-source" href=${sourceHref(e.src)} target="_blank" rel="noopener">${t("learner.open-source")} ${e.src[0].toUpperCase()}</a>` : ""}
    </div>
  </section>`)}
</div>`);
```

```js
display(html`<div class="learner-csv">${csvDownloadButton(
  () => shown.map(cardCsvRow),
  () => `learner-cards${browseBand >= 1 ? `-band${browseBand}` : ""}${query ? `-q-${normalizedQuery.candidates[0] ?? "search"}` : ""}.csv`,
  cardCsvColumns
)} <small>${L("Downloads the cards currently shown — the lookup/band-filter view, not the whole index.", "Выгружает показанные карточки — текущий вид поиска/фильтра, не весь указатель.")}</small></div>`);
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
.learner-tiers { margin: 8px 0 16px; }
.learner-tiers h3 { font-size: 1rem; margin: 0 0 8px; }
.learner-tier-row { display: flex; flex-wrap: wrap; gap: 8px; }
.learner-tier-chip { display: inline-flex; align-items: baseline; gap: 4px; font-size: .76rem; padding: 2px 8px; border-radius: 999px; border: 1px solid var(--theme-foreground-faint); border-left-width: 5px; }
.learner-tier-chip small { color: var(--theme-foreground-muted); }
.tier-A { border-left-color: #2ca02c; }
.tier-B { border-left-color: #66bd63; }
.tier-C { border-left-color: #d9b300; }
.tier-D { border-left-color: var(--theme-foreground-faint); }
.learner-tier-note { font-size: .8rem; color: var(--theme-foreground-muted); margin: 6px 0 0; }
.learner-evidence, .learner-absences { font-size: .88rem; border: 1px dashed var(--theme-foreground-faint); border-radius: 6px; padding: 6px 10px; }
.learner-evidence summary, .learner-absences summary { cursor: pointer; color: var(--theme-foreground-muted); }
.learner-senses { margin: 8px 0 4px; padding-left: 1.2rem; display: grid; gap: 4px; }
.learner-sv { font-weight: 700; }
.learner-sv.yes { color: #2ca02c; }
.learner-sv.no { color: #d9544d; }
.learner-caveat { font-size: .76rem; color: var(--theme-foreground-muted); margin: 6px 0 2px; }
.learner-grammar { display: grid; gap: 6px; margin: 8px 0 2px; }
.learner-grammar div { display: grid; grid-template-columns: minmax(90px, 0.3fr) 1fr; gap: 8px; }
.learner-grammar dt { font-weight: 700; }
.learner-grammar dd { margin: 0; overflow-wrap: anywhere; }
.learner-root { display: inline-block; margin-right: 10px; }
.learner-homonym { font-size: .8rem; border: 1px solid color-mix(in srgb, #d9b300, transparent 40%); border-radius: 6px; padding: 4px 8px; background: color-mix(in srgb, #d9b300, transparent 92%); }
.learner-csv { display: flex; align-items: center; gap: 10px; margin: 4px 0 18px; }
.learner-csv small { color: var(--theme-foreground-muted); }
@media (max-width: 640px) { .trust-block div { grid-template-columns: 1fr; gap: 2px; } .learner-grammar div { grid-template-columns: 1fr; gap: 2px; } }
</style>

---

Generated by `npm run build-learner-index` (v1). Joins `lemma-lookup.json` (dictionary coverage) with the DCS corpus frequency band, the P2 survival-ranked senses (28-lemma panel, threshold ≥ 0.15), WhitneyRoots roots + gaṇa, and the VisualDCS learner-contracts-v1 paradigm links pinned at `vdcs-learner-v1-20260809`. Every missing layer carries a reason code; survival is per-sense only — the within-edge effect is not significant and no population claim is made. CC-BY-SA-4.0.

_Dr. Mārcis Gasūns_
