---
title: Source line viewer
toc: false
---

# Source line viewer

```js
import { sourceLineToIast } from "../lib/source-iast.js";
import { from_slp1 } from "../lib/sanskrit-util.js";
```

```js
// code -> label for the seven comparison dictionaries (PWK lives at code "pw").
const DICT_LABELS = { mw: "MW", ap: "AP", pwg: "PWG", pw: "PWK", wil: "WIL", vcp: "VCP", skd: "SKD" };
const CODES = Object.keys(DICT_LABELS);
const RAW_BASE = "https://raw.githubusercontent.com/sanskrit-lexicon/csl-orig/master/v02";
const rawUrl = (code) => `${RAW_BASE}/${code}/${code}.txt`;

// Clean form: /tools/source#pw/570764 (the ?dict=&line=&label= query is still
// read for back-compat with older shared links); the label is derived from the
// dict code, so it need not appear in the URL.
const params = new URLSearchParams(typeof location !== "undefined" ? location.search : "");
const hash = (typeof location !== "undefined" ? location.hash : "").replace(/^#\/?/, "");
const [hDict, hLine] = hash ? hash.split("/") : [];
const rawDict = (hDict || params.get("dict") || "").toLowerCase();
const initialCode = CODES.includes(rawDict) ? rawDict : "mw";
const initialLine = Math.max(1, parseInt(hLine || params.get("line"), 10) || 1);
const initialLabel = params.get("label");
```

```js
const code = view(Inputs.select(CODES, { label: "Dictionary", value: initialCode, format: c => DICT_LABELS[c] }));
const line = view(Inputs.number({ label: "Line", value: initialLine, min: 1, step: 1, submit: true }));
const context = view(Inputs.select([5, 15, 40, 120, 400], { label: "Context lines", value: 5 }));
const scriptMode = view(Inputs.radio(["IAST", "SLP1"], { label: "Script", value: "IAST", format: m => m === "SLP1" ? "SLP1 (raw source)" : "IAST" }));
```

```js
// Stream the raw file, counting newlines, and stop once we're `context` lines
// past the target — so a line early in a 54 MB file costs ~1 MB, not 54.
async function fetchContext(code, target, ctx, { maxBytes = 35_000_000 } = {}) {
  const before = Math.max(1, target - ctx);
  const until = target + ctx;
  const res = await fetch(rawUrl(code));
  if (!res.ok || !res.body) throw new Error(`HTTP ${res.status} fetching ${code}.txt`);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let lineNo = 0;
  let bytes = 0;
  const lines = [];
  let complete = false;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    bytes += value.byteLength;
    buf += decoder.decode(value, { stream: true });
    let idx;
    while ((idx = buf.indexOf("\n")) >= 0) {
      const text = buf.slice(0, idx).replace(/\r$/, "");
      buf = buf.slice(idx + 1);
      lineNo += 1;
      if (lineNo >= before && lineNo <= until) lines.push({ n: lineNo, text });
      if (lineNo >= until) { complete = true; break; }
    }
    if (complete || bytes > maxBytes) break;
  }
  reader.cancel().catch(() => {});
  return { lines, from: before, until, lastLine: lineNo, bytes, reachedTarget: lineNo >= target, capped: !complete && bytes > maxBytes };
}
```

```js
const ctx = await fetchContext(code, line, context).catch(err => ({ error: err.message }));
```

```js
if (ctx.error) {
  display(html`<div class="warning" label="Could not stream the source">
    ${ctx.error}. Open the raw file directly: <a href=${rawUrl(code)} target="_blank" rel="noopener">${code}.txt</a> (large — your browser may be slow to render it).
  </div>`);
} else if (!ctx.reachedTarget) {
  display(html`<div class="warning" label="Line out of range">
    ${DICT_LABELS[code]} (${code}.txt) has only ${ctx.lastLine.toLocaleString()} lines; line ${line.toLocaleString()} does not exist.
  </div>`);
} else {
  const kb = Math.round(ctx.bytes / 1024);
  const byN = new Map(ctx.lines.map(l => [l.n, l]));
  // The entry the target line belongs to: from its <L> header down to <LEND>.
  let entryStart = line;
  while (entryStart > ctx.from && !byN.get(entryStart)?.text.startsWith("<L>")) entryStart--;
  let entryEnd = line;
  while (entryEnd < ctx.until && byN.get(entryEnd) && !byN.get(entryEnd).text.startsWith("<LEND>")) entryEnd++;
  // The headword we are hunting, from <k1> on the entry's <L> line.
  const k1 = (byN.get(entryStart)?.text.match(/<k1>([^<]*)/) || [])[1] || "";
  const hw = scriptMode === "SLP1" ? k1 : from_slp1(k1);

  // <L>/<H> header lines are id/page/k1/k2 metadata, not markup-wrapped SLP1 —
  // space the fields and transcode so the headword reads, not "2010511-292-b…".
  const displayLine = (l) => {
    if (scriptMode === "SLP1") return l.text;
    if (/^<[LH]>/.test(l.text)) return from_slp1(l.text.replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
    return sourceLineToIast(l.text, code);
  };
  // Wrap each occurrence of the headword in a yellow mark.
  const markWord = (text) => {
    if (!hw || !text.includes(hw)) return text;
    const out = [];
    text.split(hw).forEach((p, i) => {
      if (i > 0) out.push(html`<span style="background:#ffe08a;color:#000;border-radius:2px;padding:0 1px">${hw}</span>`);
      if (p) out.push(p);
    });
    return out;
  };

  display(html`<div>
    <div style="margin:6px 0;color:var(--theme-foreground-muted)">
      ${initialLabel ? html`<b>${initialLabel}</b> · ` : ""}${DICT_LABELS[code]} <code>${code}.txt</code> ·
      entry <b>${hw || "?"}</b> at line ${line.toLocaleString()} · lines ${ctx.from.toLocaleString()}–${Math.min(ctx.until, ctx.lastLine).toLocaleString()} ·
      streamed ${kb.toLocaleString()} KB ·
      <a href=${rawUrl(code)} target="_blank" rel="noopener">raw file</a>${ctx.capped ? " · stream capped for size" : ""}
    </div>
    <pre style="overflow-x:auto;background:var(--theme-background-alt,#f6f6f6);border-radius:8px;padding:10px 4px;font-size:.85rem;line-height:1.5">${ctx.lines.map(l => {
      const inEntry = l.n >= entryStart && l.n <= entryEnd;
      const disp = displayLine(l) || " ";
      return html`<div style=${inEntry ? "display:flex;background:rgba(127,127,127,.28);box-shadow:inset 3px 0 0 #ffe08a" : "display:flex"}><span style="user-select:none;width:5.5em;flex:none;text-align:right;padding-right:1em;color:var(--theme-foreground-muted)">${l.n}</span><span style="white-space:pre-wrap">${inEntry ? markWord(disp) : disp}</span></div>`;
    })}</pre>
  </div>`);
}
```

---

Opens **exactly the line you need** in a Cologne source file — not the whole document. GitHub refuses to render the multi-MB `csl-orig` `.txt` files (it only offers "View raw", and `#L…` anchors never fire), so this page streams the raw text, stops as soon as it has reached your line plus a little context, and highlights the entry. Link here from any review queue, or set the dictionary and line above — e.g. [`/tools/source#pw/26745`](./source#pw/26745).

Streams from [`sanskrit-lexicon/csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) `master`. CC-BY-SA-4.0.
