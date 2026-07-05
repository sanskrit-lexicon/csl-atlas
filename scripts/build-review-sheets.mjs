// Build interactive HTML review sheets for the two human-gated backlogs
// (H4 semantic-field: 89 needs-review rows; Xref shared-core: 40 rows), per
// the org /review-sheet rule: voting artifacts are interactive HTML with a
// decisions.json export — never markdown checkboxes. The committed markdown
// worksheets (docs/H4_REVIEW_WORKSHEET.md, docs/XREF_REVIEW_WORKSHEET.md)
// remain as the read-only evidence view; these sheets are the voting surface.
//
// Output goes to review/ (gitignored — personal working artifacts), named
// per the org sheet-naming convention (<repo>-<topic>_<scope>_review.html —
// see Uprava/REVIEW_SHEETS_INDEX.md, FINDINGS.md §34):
//   review/csl-atlas-h4-semantic-field_89rows_review.html
//   review/csl-atlas-xref-shared-core_v1_review.html
// Each exports decisions.json as <same stem>_decisions.json, with schema
//   { sheet_id, generated, decided, items: [{ id, decision, note }] }
// with unvoted items included as decision: null. Consumer: /decisions-apply
// (drop the file at review/<stem>_decisions.json and run the skill).
//
// Run: node scripts/build-review-sheets.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.normalize(path.join(path.dirname(fileURLToPath(import.meta.url)), ".."));
const OUT_DIR = path.join(ROOT, "review");

const esc = (s) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function pointerHtml(p) {
  const bits = [];
  if (p.dictionary) bits.push(`<b>${esc(p.dictionary)}</b>`);
  if (p.role) bits.push(esc(p.role));
  if (p.L) bits.push(`L=${esc(p.L)}`);
  const label = bits.join(" · ") || "source";
  const link = p.href ? `<a href="${esc(p.href)}" target="_blank" rel="noopener">${label}</a>` : label;
  const excerpt = p.bodyExcerpt ? `<div class="excerpt">${esc(p.bodyExcerpt)}</div>` : "";
  return `<div class="pointer">${link}${excerpt}</div>`;
}

function sheetHtml({ sheetId, title, sourceDesc, items }) {
  const generated = new Date().toISOString().slice(0, 10);
  const itemsJson = JSON.stringify(items.map((i) => ({ id: i.id, options: i.options })));
  const body = items
    .map(
      (i, n) => `
<section class="item" data-id="${esc(i.id)}" id="item-${n}">
  <h3>${n + 1}. ${esc(i.title)} <span class="status" data-status></span></h3>
  ${i.contextHtml}
  <div class="buttons">
    ${i.options.map((o) => `<button data-vote="${esc(o)}">${esc(o)}</button>`).join("\n    ")}
    <button data-vote="defer" class="defer">⏸ defer</button>
  </div>
  <input type="text" class="note" placeholder="note (optional)">
</section>`
    )
    .join("\n");

  return `<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<style>
  body { font: 15px/1.5 system-ui, sans-serif; margin: 0 auto; max-width: 900px; padding: 1rem 1rem 6rem; }
  h1 { font-size: 1.3rem; } h3 { margin: 0 0 .4rem; font-size: 1.02rem; }
  .item { border: 1px solid #d0d7de; border-radius: 8px; padding: .8rem 1rem; margin: .8rem 0; }
  .item.voted { border-color: #1a7f37; background: #f6fff8; }
  .item.deferred { border-color: #bf8700; background: #fffdf5; }
  .pointer { margin: .3rem 0; font-size: .92em; }
  .excerpt { font-family: ui-monospace, monospace; font-size: .85em; background: #f6f8fa;
             padding: .3rem .5rem; border-radius: 4px; margin-top: .15rem;
             overflow-x: auto; white-space: pre-wrap; }
  .q { font-style: italic; margin: .4rem 0; }
  .meta { color: #57606a; font-size: .9em; }
  .buttons { margin: .5rem 0 .3rem; display: flex; flex-wrap: wrap; gap: .4rem; }
  button { padding: .35rem .7rem; border: 1px solid #d0d7de; border-radius: 6px;
           background: #f6f8fa; cursor: pointer; font-size: .9em; }
  button.active { background: #1a7f37; color: #fff; border-color: #1a7f37; }
  button.defer.active { background: #bf8700; border-color: #bf8700; }
  .note { width: 100%; box-sizing: border-box; padding: .3rem .5rem;
          border: 1px solid #d0d7de; border-radius: 6px; font-size: .9em; }
  .status { font-size: .8em; color: #1a7f37; }
  #tally { position: fixed; bottom: 0; left: 0; right: 0; background: #24292f; color: #fff;
           padding: .55rem 1rem; display: flex; gap: 1.2rem; align-items: center;
           font-size: .92em; flex-wrap: wrap; }
  #tally button { background: #2da44e; color: #fff; border: none; font-weight: 600; }
  @media (prefers-color-scheme: dark) {
    body { background: #0d1117; color: #e6edf3; }
    .item { border-color: #30363d; } .item.voted { background: #0f1c14; }
    .item.deferred { background: #1c1708; }
    .excerpt { background: #161b22; } button { background: #21262d; color: #e6edf3; border-color: #30363d; }
    .note { background: #0d1117; color: #e6edf3; border-color: #30363d; }
  }
</style></head><body>
<h1>${esc(title)}</h1>
<p class="meta">Generated ${generated} · ${items.length} items · ${esc(sourceDesc)}<br>
Votes persist in this browser (localStorage). Keys: <b>1–9</b> pick the nth label,
<b>d</b> defer, <b>j/k</b> next/prev item. When done, click <b>Download decisions.json</b>.</p>
${body}
<div id="tally"><span id="counts"></span>
  <button id="dl">Download decisions.json</button>
</div>
<script>
const SHEET_ID = ${JSON.stringify(sheetId)};
const ITEMS = ${itemsJson};
const store = () => JSON.parse(localStorage.getItem(SHEET_ID) || "{}");
const save = (s) => localStorage.setItem(SHEET_ID, JSON.stringify(s));
const secs = [...document.querySelectorAll(".item")];
let cursor = 0;
function paint() {
  const s = store();
  let voted = 0, deferred = 0;
  secs.forEach((sec) => {
    const rec = s[sec.dataset.id] || {};
    sec.classList.toggle("voted", !!rec.decision && rec.decision !== "defer");
    sec.classList.toggle("deferred", rec.decision === "defer");
    sec.querySelector("[data-status]").textContent = rec.decision ? "→ " + rec.decision : "";
    sec.querySelectorAll("button[data-vote]").forEach((b) =>
      b.classList.toggle("active", b.dataset.vote === rec.decision));
    const note = sec.querySelector(".note");
    if (document.activeElement !== note) note.value = rec.note || "";
    if (rec.decision === "defer") deferred++; else if (rec.decision) voted++;
  });
  document.getElementById("counts").textContent =
    \`\${voted} decided · \${deferred} deferred · \${secs.length - voted - deferred} unvoted / \${secs.length}\`;
}
secs.forEach((sec) => {
  sec.addEventListener("click", (e) => {
    cursor = secs.indexOf(sec);
    const b = e.target.closest("button[data-vote]");
    if (!b) return;
    const s = store();
    const rec = s[sec.dataset.id] || {};
    rec.decision = rec.decision === b.dataset.vote ? null : b.dataset.vote;
    s[sec.dataset.id] = rec; save(s); paint();
  });
  sec.querySelector(".note").addEventListener("input", (e) => {
    const s = store();
    (s[sec.dataset.id] = s[sec.dataset.id] || {}).note = e.target.value; save(s);
  });
});
document.addEventListener("keydown", (e) => {
  if (e.target.tagName === "INPUT") return;
  const sec = secs[cursor];
  if (e.key === "j") { cursor = Math.min(cursor + 1, secs.length - 1); secs[cursor].scrollIntoView({ block: "center" }); }
  else if (e.key === "k") { cursor = Math.max(cursor - 1, 0); secs[cursor].scrollIntoView({ block: "center" }); }
  else if (e.key === "d") sec.querySelector('button[data-vote="defer"]').click();
  else if (/^[1-9]$/.test(e.key)) {
    const b = sec.querySelectorAll("button[data-vote]")[+e.key - 1];
    if (b) b.click();
  } else return;
  e.preventDefault();
});
document.getElementById("dl").addEventListener("click", () => {
  const s = store();
  const out = {
    sheet_id: SHEET_ID, generated: ${JSON.stringify(generated)},
    decided: new Date().toISOString(),
    items: ITEMS.map((i) => ({ id: i.id, decision: (s[i.id] || {}).decision || null, note: (s[i.id] || {}).note || "" })),
  };
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 2)], { type: "application/json" }));
  a.download = SHEET_ID + "_decisions.json"; a.click();
});
paint();
</script></body></html>\n`;
}

function buildH4() {
  const packet = JSON.parse(fs.readFileSync(path.join(ROOT, "data/lexico/h4_semantic_field_review_packet.json"), "utf8"));
  const vocab = packet.decisionVocabulary;
  const rows = packet.sampleRows.filter((r) => r.reviewStatus === "needs-review");
  const items = rows.map((r) => ({
    id: r.reviewId,
    title: `${r.sampleLabel} — ${r.lemma} (${r.dictionary.label}${r.comparisonDictionary ? " vs " + r.comparisonDictionary.label : ""})`,
    options: vocab[r.sampleType] || ["confirm", "reject"],
    contextHtml: [
      `<div class="q">${esc(r.reviewQuestion)}</div>`,
      `<div class="meta">field: ${esc(r.field?.label || "")} · machine state: ${esc(r.machineState)} · proposed: ${esc(r.proposedLabel)}` +
        (r.coverageDeltaPct != null ? ` · Δ ${esc(r.coverageDeltaPct)}%` : "") + `</div>`,
      ...(r.sourcePointers || []).map(pointerHtml),
    ].join("\n"),
  }));
  return sheetHtml({
    sheetId: "csl-atlas-h4-semantic-field_89rows",
    title: "H4 semantic-field review — 89 needs-review rows",
    sourceDesc: "data/lexico/h4_semantic_field_review_packet.json (auto-resolved rows excluded)",
    items,
  });
}

function buildXref() {
  const packet = JSON.parse(fs.readFileSync(path.join(ROOT, "data/lexico/xref_source_check_packet.json"), "utf8"));
  const options = packet.packetLabelVocabulary.map((v) => v.label);
  const items = packet.sharedCoreRows.map((r) => ({
    id: r.sampleId,
    title: `${r.sourceLemma} → ${r.target} (${(r.matchedDictionaries || []).join("+") || "MW/PWG"})`,
    options,
    contextHtml: [
      `<div class="q">${esc(r.reviewQuestion)}</div>`,
      `<div class="meta">${esc(r.machineInterpretation)}${
        r.missingExactEdgeDictionaries?.length ? " · missing edge in: " + esc(r.missingExactEdgeDictionaries.join(", ")) : ""
      }</div>`,
      ...(r.sourcePointers || []).map(pointerHtml),
    ].join("\n"),
  }));
  return sheetHtml({
    sheetId: "csl-atlas-xref-shared-core_v1",
    title: "Xref shared-core review — 40 MW/PWG edges",
    sourceDesc: "data/lexico/xref_source_check_packet.json (10 prefix-controls auto-resolved, excluded)",
    items,
  });
}

fs.mkdirSync(OUT_DIR, { recursive: true });
const H4_FILE = "csl-atlas-h4-semantic-field_89rows_review.html";
const XREF_FILE = "csl-atlas-xref-shared-core_v1_review.html";
const h4 = buildH4();
fs.writeFileSync(path.join(OUT_DIR, H4_FILE), h4);
const xref = buildXref();
fs.writeFileSync(path.join(OUT_DIR, XREF_FILE), xref);
console.log(`wrote review/${H4_FILE} (${(h4.length / 1024).toFixed(0)} kB)`);
console.log(`wrote review/${XREF_FILE} (${(xref.length / 1024).toFixed(0)} kB)`);
