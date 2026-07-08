// Build the interactive HTML review sheet for the tradition-tag map (H340,
// agenda backlog #9), per the org /review-sheet rule: voting artifacts are
// interactive HTML with a decisions.json export — never markdown checkboxes.
//
// Each item is a candidate text with its INFERRED tradition proposal; the
// reviewer confirms it (click the proposed tradition) or reclassifies (click a
// different one from the closed vocabulary), with an optional note. The proposed
// tradition is highlighted; confidence + citation context aid the call.
//
// Output goes to review/ (gitignored — personal working artifact), named per the
// org sheet-naming convention (<repo>-<topic>_<scope>_review.html — see
// Uprava/REVIEW_SHEETS_INDEX.md, FINDINGS.md §34):
//   review/csl-atlas-tradition-tags_119texts_review.html
// It exports decisions.json as <stem>_decisions.json with schema
//   { sheet_id, generated, decided, items: [{ id, decision, note }] }
// (unvoted items included as decision: null). Consumer: /decisions-apply —
// each decision is the reviewer's chosen tradition (or "reject"/defer); apply by
// setting tradition_tags.tsv's `tradition` to the vote and `reviewed` to yes,
// then rebuild `npm run build-tradition-tags`.
//
// Run: node scripts/build-tradition-review-sheet.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { TRADITION_VOCAB } from "./build-tradition-tags.mjs";

const ROOT = path.normalize(path.join(path.dirname(fileURLToPath(import.meta.url)), ".."));
const OUT_DIR = path.join(ROOT, "review");
const TAGS_PATH = path.join(ROOT, "data/citations/tradition_tags.tsv");
const EDGES_PATH = path.join(ROOT, "data/citations/ls_citation_edges.tsv");
const SHEET_STEM = "csl-atlas-tradition-tags_119texts";

const esc = (s) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function parseTsv(text) {
  const lines = text.replace(/\r\n/g, "\n").split("\n").filter((l) => l.length > 0);
  const header = lines[0].split("\t");
  return lines.slice(1).map((line) => {
    const cells = line.split("\t");
    const row = {};
    header.forEach((h, i) => (row[h] = cells[i] ?? ""));
    return row;
  });
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
    ${i.options.map((o) => `<button data-vote="${esc(o)}"${o === i.proposed ? ' class="proposed"' : ""}>${esc(o)}${o === i.proposed ? " ★" : ""}</button>`).join("\n    ")}
    <button data-vote="reject" class="reject">✗ reject (not a text)</button>
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
  .meta { color: #57606a; font-size: .9em; }
  .buttons { margin: .5rem 0 .3rem; display: flex; flex-wrap: wrap; gap: .4rem; }
  button { padding: .35rem .7rem; border: 1px solid #d0d7de; border-radius: 6px;
           background: #f6f8fa; cursor: pointer; font-size: .9em; }
  button.proposed { border-color: #0969da; font-weight: 600; }
  button.active { background: #1a7f37; color: #fff; border-color: #1a7f37; }
  button.reject.active { background: #cf222e; border-color: #cf222e; }
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
    button { background: #21262d; color: #e6edf3; border-color: #30363d; }
    .note { background: #0d1117; color: #e6edf3; border-color: #30363d; }
  }
</style></head><body>
<h1>${esc(title)}</h1>
<p class="meta">Generated ${generated} · ${items.length} items · ${esc(sourceDesc)}<br>
★ marks the inferred proposal — click it to confirm, or click a different tradition to reclassify.
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

function main() {
  const tagRows = parseTsv(fs.readFileSync(TAGS_PATH, "utf8"));
  const edgeRows = parseTsv(fs.readFileSync(EDGES_PATH, "utf8"));
  // Which dicts cite each text (for review context).
  const citedBy = new Map();
  for (const e of edgeRows) {
    if (!citedBy.has(e.canonical_text)) citedBy.set(e.canonical_text, []);
    citedBy.get(e.canonical_text).push(`${e.dict} (${Number(e.count).toLocaleString()})`);
  }
  // Sort items by total cites desc (heaviest first).
  const rows = tagRows
    .map((r) => ({ ...r, cites: Number(r._cites) || 0 }));
  // Rebuild total cites from nodes for ordering.
  const nodes = parseTsv(fs.readFileSync(path.join(ROOT, "data/citations/ls_citation_nodes.tsv"), "utf8"));
  const totalByText = new Map(nodes.map((n) => [n.canonical_text, Number(n.total_cites) || 0]));
  const nDictsByText = new Map(nodes.map((n) => [n.canonical_text, Number(n.n_dicts) || 0]));
  tagRows.sort((a, b) => (totalByText.get(b.canonical_text) || 0) - (totalByText.get(a.canonical_text) || 0));

  const items = tagRows.map((r) => {
    const text = r.canonical_text;
    const dictsList = (citedBy.get(text) || []).slice(0, 8).join(", ");
    return {
      id: text,
      proposed: r.tradition,
      title: `${text} — proposed: ${r.tradition} (${r.confidence})`,
      options: TRADITION_VOCAB,
      contextHtml: [
        `<div class="meta">${(totalByText.get(text) || 0).toLocaleString()} citations · in ${nDictsByText.get(text) || 0} dictionaries${r.note ? " · " + esc(r.note) : ""}</div>`,
        `<div class="meta">cited by: ${esc(dictsList)}</div>`
      ].join("\n")
    };
  });

  const html = sheetHtml({
    sheetId: SHEET_STEM,
    title: "Tradition-tag map review — 119 <ls> citation texts (A50 §4)",
    sourceDesc: "data/citations/tradition_tags.tsv (inferred proposals, agenda backlog #9)",
    items
  });
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const file = `${SHEET_STEM}_review.html`;
  fs.writeFileSync(path.join(OUT_DIR, file), html);
  console.log(`wrote review/${file} (${(html.length / 1024).toFixed(0)} kB, ${items.length} items)`);
}

main();
