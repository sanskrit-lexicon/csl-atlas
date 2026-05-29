---
title: MW-PWG-PWK Interoperability Hard Cases
toc: false
---

```js
const data = FileAttachment("../data/pilot/hard-cases.json").json();
const neutralData = FileAttachment("../data/pilot/neutral-model.json").json();
const lossData = FileAttachment("../data/pilot/loss-reports.json").json();
const reviewData = FileAttachment("../data/pilot/review-cases.json").json();
const teiReviewData = FileAttachment("../data/pilot/tei-review.json").json();
const ontolexReviewData = FileAttachment("../data/pilot/ontolex-review.json").json();
const externalReviewData = FileAttachment("../data/pilot/external-validation-review.json").json();
const localesEn = FileAttachment("../locales-en.json").json();
const localesRu = FileAttachment("../locales-ru.json").json();
```

```js
const items = data.items;
const neutralMap = new Map(neutralData.map(d => [d.id, d]));
const reviewMap = new Map((reviewData.items || []).map(d => [d.id, d]));
const teiReviewMap = new Map((teiReviewData.items || []).map(d => [d.id, d]));
const ontolexReviewMap = new Map((ontolexReviewData.items || []).map(d => [d.id, d]));
const repoBase = "https://github.com/sanskrit-lexicon/csl-atlas/blob/interoperability-handoff/data/pilot";
```

```js
const lang = view(Inputs.radio(["en", "ru"], {
  label: "Language",
  value: "en",
  format: d => d === "ru" ? "Russian" : "English"
}));
```

```js
const currentLanguage = lang === "ru" || lang === 1 || lang === "1" ? "ru" : "en";
const t = (key) => {
  const currentLocale = currentLanguage === "ru" ? localesRu : localesEn;
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

# ${t("interop.title")}

${t("interop.description")}

```js
const lossByCase = new Map();
for (const report of lossData) {
  if (!lossByCase.has(report.caseId)) lossByCase.set(report.caseId, []);
  lossByCase.get(report.caseId).push(report);
}

const phenomena = Array.from(new Set(items.flatMap(d => d.phenomena || []))).sort();
const statusOrder = ["lossy", "partial", "clean"];
const worstStatus = reports => statusOrder.find(status => reports.some(report => report.status === status)) || "none";
const statusText = status => status === "none" ? "none" : t(`status.${status}`);
const reviewText = row => row.review ? `${row.review.bucket} #${row.review.reviewRank}` : "full-50 machine";
```

```js
const caseRows = items.map(item => {
  const id = item.id || `mw-pwg-pwk:${item.key}`;
  const neutral = neutralMap.get(id);
  const reports = lossByCase.get(id) || [];
  const teiReview = teiReviewMap.get(id);
  const ontolexReview = ontolexReviewMap.get(id);
  const review = reviewMap.get(id);
  const recordsText = Object.values(item.records || {}).map(record => record?.raw || "").join(" ");
  const lossStatus = worstStatus(reports);

  return {
    id,
    stem: id.replace(/:/g, "-"),
    rank: item.rank,
    key: item.key,
    entryType: teiReview?.entryType || neutral?.forms?.[0]?.type || "lemma",
    phenomena: item.phenomena || [],
    phenomenaText: (item.phenomena || []).join(", "),
    lossStatus,
    lossStatusText: statusText(lossStatus),
    reviewStatus: review ? "validated-slice" : "full-50-machine-review",
    reviewLabel: reviewText({review}),
    teiStatus: teiReview?.status || "missing",
    rdfStatus: ontolexReview?.status || "missing",
    item,
    neutral,
    review,
    reports,
    searchText: `${id} ${item.key} ${(item.phenomena || []).join(" ")} ${recordsText}`.toLowerCase()
  };
});
```

```html
<style>
.summary-band {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
  margin: 18px 0;
  padding: 14px 0;
  border-top: 1px solid #d8dee4;
  border-bottom: 1px solid #d8dee4;
}
.metric {
  min-width: 0;
}
.metric-value {
  font-size: 1.45rem;
  font-weight: 700;
  line-height: 1.2;
}
.metric-label {
  color: #5f6b7a;
  font-size: 0.86rem;
}
.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin: 18px 0;
  align-items: end;
}
.case-count {
  color: #5f6b7a;
  font-size: 0.92rem;
  margin: 4px 0 14px;
}
.case-card {
  border: 1px solid #d8dee4;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 14px;
  background: #fff;
}
.case-card summary {
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  list-style: none;
}
.case-card summary::-webkit-details-marker {
  display: none;
}
.case-card summary::before {
  content: ">";
  display: inline-block;
  margin-right: 8px;
  font-size: 0.9em;
  transition: transform 0.2s;
}
.case-card[open] summary::before {
  transform: rotate(90deg);
}
.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0;
}
.phenomenon-badge,
.review-badge,
.validation-badge,
.loss-badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.82rem;
  line-height: 1.2;
}
.phenomenon-badge {
  background: #f0f2f4;
  color: #24292f;
}
.review-badge {
  border: 1px solid #9bc89b;
  background: #edf8ed;
  color: #285a28;
  font-weight: 600;
}
.validation-badge {
  border: 1px solid #8db4d8;
  background: #edf5fb;
  color: #1f4f78;
  font-weight: 600;
}
.loss-badge {
  border: 1px solid #ebc169;
  background: #fff7df;
  color: #6f4d00;
  font-weight: 600;
}
.case-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  margin: 12px 0;
  font-size: 0.9rem;
}
.case-links a {
  color: #0969da;
  text-decoration: none;
}
.case-section {
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid #eaeef2;
}
.loss-list {
  margin: 6px 0 0;
  padding-left: 20px;
}
.report-row {
  display: grid;
  grid-template-columns: minmax(70px, 0.5fr) minmax(80px, 0.6fr) minmax(110px, 1fr) minmax(120px, 1fr);
  gap: 8px;
  align-items: start;
  border-bottom: 1px solid #eaeef2;
  padding: 7px 0;
  font-size: 0.9rem;
}
.report-row:last-child {
  border-bottom: none;
}
.status-partial { color: #a15c00; font-weight: 600; }
.status-lossy { color: #b42318; font-weight: 600; }
.status-clean { color: #1a7f37; font-weight: 600; }
.dictionary-record {
  margin-top: 10px;
  padding: 10px;
  background: #f6f8fa;
  border-left: 4px solid #0969da;
}
.dictionary-record pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 0.87rem;
  margin: 6px 0 0;
  background: transparent;
  padding: 0;
  border: 0;
}
@media (max-width: 680px) {
  .report-row {
    grid-template-columns: 1fr;
  }
}
</style>
```

```js
display(html`
<div class="summary-band">
  <div class="metric">
    <div class="metric-value">${items.length}</div>
    <div class="metric-label">hard cases</div>
  </div>
  <div class="metric">
    <div class="metric-value">${reviewData.items.length}</div>
    <div class="metric-label">validated-slice cases</div>
  </div>
  <div class="metric">
    <div class="metric-value">${teiReviewData.totals.passed}/${teiReviewData.totals.cases}</div>
    <div class="metric-label">${t("interop.tei-status")}</div>
  </div>
  <div class="metric">
    <div class="metric-value">${ontolexReviewData.totals.passed}/${ontolexReviewData.totals.cases}</div>
    <div class="metric-label">${t("interop.rdf-status")}</div>
  </div>
  <div class="metric">
    <div class="metric-value">${externalReviewData.totals.passed}/${externalReviewData.totals.checks}</div>
    <div class="metric-label">external checks (${externalReviewData.totals.skipped} skipped)</div>
  </div>
</div>
`);
```

## Filter cases

```js
const query = view(Inputs.text({
  label: "Search key, id, or raw text",
  placeholder: "ac, root, L., kosha..."
}));
```

```js
const phenomenonFilter = view(Inputs.select(["all", ...phenomena], {
  label: "Phenomenon",
  value: "all",
  format: d => d === "all" ? "All phenomena" : d
}));
```

```js
const reviewFilter = view(Inputs.select(["all", "validated-slice", "full-50-machine-review"], {
  label: "Review layer",
  value: "all",
  format: d => d === "all" ? "All cases" : d
}));
```

```js
const lossFilter = view(Inputs.select(["all", "lossy", "partial", "clean", "none"], {
  label: "Loss status",
  value: "all",
  format: d => d === "all" ? "All statuses" : d
}));
```

```js
const visibleRows = caseRows.filter(row => {
  const q = String(query || "").trim().toLowerCase();
  const matchesQuery = !q || row.searchText.includes(q);
  const matchesPhenomenon = phenomenonFilter === "all" || row.phenomena.includes(phenomenonFilter);
  const matchesReview = reviewFilter === "all" || row.reviewStatus === reviewFilter;
  const matchesLoss = lossFilter === "all" || row.lossStatus === lossFilter;
  return matchesQuery && matchesPhenomenon && matchesReview && matchesLoss;
});
```

```js
display(html`<div class="case-count">Showing ${visibleRows.length} of ${caseRows.length} cases.</div>`);
```

```js
display(Inputs.table(visibleRows, {
  columns: ["rank", "key", "entryType", "phenomenaText", "lossStatusText", "reviewLabel", "teiStatus", "rdfStatus"],
  header: {
    rank: "#",
    key: "Key",
    entryType: "Entry type",
    phenomenaText: "Phenomena",
    lossStatusText: "Worst loss",
    reviewLabel: "Review",
    teiStatus: "TEI",
    rdfStatus: "RDF"
  },
  sort: "rank"
}));
```

```js
display(html`
<div>
  ${visibleRows.map(row => {
    const item = row.item;
    const review = row.review;
    return html`<details class="case-card">
      <summary>${t("interop.case-label")} ${row.rank}: <strong>${row.key}</strong> <span style="color:#5f6b7a;">(${row.entryType})</span></summary>
      <div>
        <div class="badge-row">
          ${row.phenomena.map(p => html`<span class="phenomenon-badge">${p}</span>`)}
          ${review ? html`<span class="review-badge">${t("interop.review-slice")}: ${review.bucket}, ${t("interop.review-rank")} #${review.reviewRank}</span>` : ""}
          <span class="validation-badge">${t("interop.tei-status")}: ${row.teiStatus}</span>
          <span class="validation-badge">${t("interop.rdf-status")}: ${row.rdfStatus}</span>
          <span class="loss-badge">worst loss: ${row.lossStatusText}</span>
        </div>

        <div class="case-links">
          <a href="${repoBase}/neutral-model.json" target="_blank">${t("interop.links.neutral")}</a>
          <a href="${repoBase}/tei/${row.stem}.xml" target="_blank">${t("interop.links.tei")}</a>
          <a href="${repoBase}/ontolex/${row.stem}.json" target="_blank">${t("interop.links.ontolex")}</a>
          <a href="${repoBase}/rdf/${row.stem}.ttl" target="_blank">${t("interop.links.rdf")}</a>
          <a href="${repoBase}/tei-review.json" target="_blank">${t("interop.links.teiReview")}</a>
          <a href="${repoBase}/ontolex-review.json" target="_blank">${t("interop.links.ontolexReview")}</a>
          <a href="${repoBase}/external-validation-review.json" target="_blank">External validation JSON</a>
          <a href="${repoBase}/loss-reports.json" target="_blank">${t("interop.links.loss")}</a>
        </div>

        <div class="case-section">
          <strong>${t("interop.loss-hints")}:</strong>
          <ul class="loss-list">
            ${(item.lossHints || []).map(hint => html`<li>${hint}</li>`)}
          </ul>
        </div>

        ${row.reports.length ? html`
        <div class="case-section">
          <strong>${t("interop.machine-loss-reports")}:</strong>
          <div>
            ${row.reports.map(r => html`
              <div class="report-row">
                <div>${r.target.toUpperCase()}</div>
                <div class="status-${r.status}">${statusText(r.status)}</div>
                <div>${r.failureClassification || "none"}</div>
                <div>${r.reviewStatus}: ${t("phenomenon." + r.phenomenon)}</div>
              </div>
            `)}
          </div>
        </div>
        ` : ""}

        <div class="case-section">
          <strong>${t("interop.source-records")}:</strong>
          ${["mw", "pwg", "pwk"].map(dict => {
            const rec = item.records[dict];
            if (!rec) return "";
            return html`
              <div class="dictionary-record">
                <strong>${dict.toUpperCase()}</strong>
                <span style="font-size:0.88rem; color:#5f6b7a; margin-left: 8px;">
                  L: ${rec.L}, line: ${rec.line}, pc: ${rec.pc}
                </span>
                <pre>${rec.raw}</pre>
              </div>
            `;
          })}
        </div>
      </div>
    </details>`;
  })}
</div>
`);
```
