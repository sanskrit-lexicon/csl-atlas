---
title: Source line viewer
toc: false
---

# Source line viewer

Opens **exactly the line you need** in a Cologne source file — not the whole document. GitHub refuses to render the multi-MB `csl-orig` `.txt` files (it only offers "View raw", and `#L…` anchors never fire), so this page streams the raw text, stops as soon as it has reached your line plus a little context, and highlights it.

Link here from any review queue, or set the dictionary and line below. URL parameters: `?dict=pw&line=26745`.

```js
import { sourceLineToIast } from "../lib/source-iast.js";
```

```js
// code -> label for the seven comparison dictionaries (PWK lives at code "pw").
const DICT_LABELS = { mw: "MW", ap: "AP", pwg: "PWG", pw: "PWK", wil: "WIL", vcp: "VCP", skd: "SKD" };
const CODES = Object.keys(DICT_LABELS);
const RAW_BASE = "https://raw.githubusercontent.com/sanskrit-lexicon/csl-orig/master/v02";
const rawUrl = (code) => `${RAW_BASE}/${code}/${code}.txt`;

const params = new URLSearchParams(typeof location !== "undefined" ? location.search : "");
const initialCode = CODES.includes((params.get("dict") || "").toLowerCase()) ? params.get("dict").toLowerCase() : "mw";
const initialLine = Math.max(1, parseInt(params.get("line"), 10) || 1);
const initialLabel = params.get("label");
```

```js
const code = view(Inputs.select(CODES, { label: "Dictionary", value: initialCode, format: c => DICT_LABELS[c] }));
const line = view(Inputs.number({ label: "Line", value: initialLine, min: 1, step: 1, submit: true }));
const context = view(Inputs.select([25, 60, 150, 400], { label: "Context lines", value: 60 }));
const scriptMode = view(Inputs.radio(["IAST", "Raw"], { label: "Script", value: "IAST" }));
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
  display(html`<div>
    <div style="margin:6px 0;color:var(--theme-foreground-muted)">
      ${initialLabel ? html`<b>${initialLabel}</b> · ` : ""}${DICT_LABELS[code]} <code>${code}.txt</code> ·
      lines ${ctx.from.toLocaleString()}–${Math.min(ctx.until, ctx.lastLine).toLocaleString()} ·
      streamed ${kb.toLocaleString()} KB ·
      <a href=${rawUrl(code)} target="_blank" rel="noopener">raw file</a>${ctx.capped ? " · stream capped for size" : ""}
    </div>
    <pre style="overflow-x:auto;background:var(--theme-background-alt,#f6f6f6);border-radius:8px;padding:10px 4px;font-size:.85rem;line-height:1.5">${ctx.lines.map(l => html`<div style=${l.n === line
        ? "display:flex;background:var(--theme-foreground-focus,#ffe08a);color:#000"
        : "display:flex"}><span style="user-select:none;width:5.5em;flex:none;text-align:right;padding-right:1em;color:var(--theme-foreground-muted)">${l.n}</span><span style="white-space:pre-wrap">${(scriptMode === "IAST" ? sourceLineToIast(l.text, code) : l.text) || " "}</span></div>`)}</pre>
  </div>`);
}
```

---

Streams from [`sanskrit-lexicon/csl-orig`](https://github.com/sanskrit-lexicon/csl-orig) `master`. CC-BY-SA-4.0.
