---
title: MW-PWG-PWK Interoperability Hard Cases
toc: false
---

```js
const data = FileAttachment("../data/pilot/hard-cases.json").json();
const neutralData = FileAttachment("../data/pilot/neutral-model.json").json();
const lossData = FileAttachment("../data/pilot/loss-reports.json").json();
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
```

```js
const items = data.items;
const neutralMap = new Map(neutralData.map(d => [d.key, d]));
```

```js
// Define active language state
const langVar = Mutable("en");
const setLanguage = (lang) => { langVar.value = lang; };
const lang = langVar;
```

```js
const t = (key) => {
  const currentLocale = lang === "ru" ? localesRu : localesEn;
  const parts = key.split(".");
  let result = currentLocale;
  for (const part of parts) {
    if (result && result[part] !== undefined) {
      result = result[part];
    } else {
      return key;
    }
  }
  return result;
};
```

```js
// Group loss reports by caseId
const lossByCase = new Map();
for (const report of lossData) {
  if (!lossByCase.has(report.caseId)) {
    lossByCase.set(report.caseId, []);
  }
  lossByCase.get(report.caseId).push(report);
}
```

# ${t("interop.title")}

${t("interop.description")}

```js
// Render language selector
const langInput = Inputs.button([
  ["English (EN)", () => setLanguage("en")],
  ["Русский (RU)", () => setLanguage("ru")]
], {label: t("interop.select-language")});
display(langInput);
```

```html
<style>
.case-card {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 16px;
  background: white;
}
.case-card summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 1.1em;
  list-style: none;
}
.case-card summary::-webkit-details-marker {
  display: none;
}
.case-card summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 8px;
  font-size: 0.8em;
  transition: transform 0.2s;
}
.case-card[open] summary::before {
  transform: rotate(90deg);
}
.phenomenon-badge {
  display: inline-block;
  background: #eee;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  margin-right: 6px;
  margin-bottom: 6px;
}
.dictionary-record {
  margin-top: 12px;
  padding: 10px;
  background: #f8f9fa;
  border-left: 4px solid #0366d6;
}
.dictionary-record pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: monospace;
  font-size: 0.9em;
  margin: 6px 0 0 0;
  background: none;
  padding: 0;
  border: none;
}
.loss-hints {
  margin-top: 12px;
  padding: 10px;
  background: #fff3cd;
  border: 1px solid #ffeeba;
  border-radius: 4px;
}
.machine-reports {
  margin-top: 12px;
  padding: 10px;
  background: #fdfdfd;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.report-row {
  display: flex;
  font-size: 0.9em;
  border-bottom: 1px solid #eee;
  padding: 4px 0;
}
.report-row:last-child {
  border-bottom: none;
}
.report-target {
  font-weight: bold;
  width: 70px;
}
.report-status {
  width: 70px;
}
.status-partial { color: #d08000; }
.status-lossy { color: #d73a49; }
.status-clean { color: #28a745; }
.link-bar {
  margin-top: 12px;
  font-size: 0.9em;
}
.link-bar a {
  margin-right: 12px;
  text-decoration: none;
  color: #0366d6;
}
</style>
```

```js
display(html`
<div>
  ${items.map(item => {
    // Determine the stable ID based on neutral model
    const nModel = neutralMap.get(item.key);
    const stableId = nModel ? nModel.id : `mw-pwg-pwk:${item.key}`;
    const safeId = stableId.replace(/:/g, "-");
    const reports = lossByCase.get(stableId) || [];

    const isHumanReviewed = reports.some(r => r.reviewStatus === 'human-reviewed');
    const curatedPath = isHumanReviewed ? "/curated" : "";
    const repoBase = "https://github.com/sanskrit-lexicon/csl-atlas/blob/main/data/pilot";

    return html`<details class="case-card">
      <summary>${t("interop.case-label")} ${item.rank}: <strong>${item.key}</strong></summary>
      <div style="margin-top: 16px;">
        
        <div>
          <strong>${t("interop.phenomena")}:</strong>
          <div style="margin-top: 6px;">
            ${item.phenomena.map(p => html`<span class="phenomenon-badge">${p}</span>`)}
          </div>
        </div>
        
        <div class="link-bar">
          <a href="${repoBase}/neutral-model.json" target="_blank">📄 ${t("interop.links.neutral")}</a>
          <a href="${repoBase}${curatedPath}/tei/${safeId}.xml" target="_blank">📄 ${t("interop.links.tei")}</a>
          <a href="${repoBase}${curatedPath}/ontolex/${safeId}.json" target="_blank">📄 ${t("interop.links.ontolex")}</a>
          <a href="${repoBase}/loss-reports.json" target="_blank">📄 ${t("interop.links.loss")}</a>
        </div>

        <div class="loss-hints">
          <strong>${t("interop.loss-hints")}:</strong>
          <ul style="margin: 6px 0 0 0; padding-left: 20px;">
            ${item.lossHints.map(hint => html`<li>${hint}</li>`)}
          </ul>
        </div>
        
        ${reports.length > 0 ? html`
        <div class="machine-reports">
          <strong>${t("interop.machine-loss-reports")}:</strong>
          <div style="margin-top: 6px;">
            ${reports.map(r => html`
              <div class="report-row" style="flex-wrap: wrap; gap: 8px; align-items: center;">
                <div class="report-target">[${r.target.toUpperCase()}]</div>
                <div class="report-status status-${r.status}">${t("status." + r.status)}</div>
                <div style="font-size: 0.85em; background: #e6f6ff; padding: 2px 6px; border-radius: 4px; color: #005080;">${t("failure." + (r.failureClassification || "none"))}</div>
                <div style="font-size: 0.85em; background: ${r.reviewStatus === 'human-reviewed' ? '#e2fbe8' : '#f1f1f1'}; padding: 2px 6px; border-radius: 4px; color: ${r.reviewStatus === 'human-reviewed' ? '#0e6220' : '#444'};">${t("review." + r.reviewStatus)}</div>
                <div style="flex-basis: 100%; margin-top: 2px; padding-left: 8px; border-left: 2px solid #ccc; color: #555;">${t("phenomenon." + r.phenomenon)}: ${r.loss || r.claim}</div>
              </div>
            `)}
          </div>
        </div>
        ` : ''}
        
        <div style="margin-top: 12px;">
          <strong>${t("interop.source-records")}:</strong>
        </div>
        
        ${['mw', 'pwg', 'pwk'].map(dict => {
          const rec = item.records[dict];
          if (!rec) return '';
          return html`
            <div class="dictionary-record">
              <strong>${dict.toUpperCase()}</strong> 
              <span style="font-size:0.9em; color:#666; margin-left: 8px;">
                (L: ${rec.L}, line: ${rec.line}, pc: ${rec.pc})
              </span>
              <pre>${rec.raw}</pre>
            </div>
          `;
        })}
      </div>
    </details>`;
  })}
</div>
`);
```
