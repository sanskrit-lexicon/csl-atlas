// Reusable CSV download for any table or list on the atlas.
//
// The site is static with no backend, so "download this table" is a client-side
// Blob. `csvDownloadButton` returns a ready-to-place <button>; `toCsv` /
// `downloadCsv` are the pieces if a page wants its own trigger.
//
// Values are stringified; nested objects/arrays are JSON-encoded so a column of
// source pointers survives the round-trip. A UTF-8 BOM is prepended so Excel
// renders IAST diacritics (ā, ī, ṛ, ṣ, ś) correctly. Export IAST, not SLP1 —
// SLP1 is a machine key, not for human reading.

/** Serialize rows (array of objects) to RFC-4180 CSV text. `columns` fixes header order. */
export function toCsv(rows, columns) {
  const cols = columns ?? [...rows.reduce((s, r) => {
    for (const k of Object.keys(r)) s.add(k);
    return s;
  }, new Set())];
  const esc = (v) => {
    if (v == null) return "";
    const s = typeof v === "object" ? JSON.stringify(v) : String(v);
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const head = cols.map(esc).join(",");
  const body = rows.map(r => cols.map(c => esc(r[c])).join(",")).join("\r\n");
  return body ? `${head}\r\n${body}` : head;
}

/** Trigger a browser download of `rows` as `filename`. */
export function downloadCsv(rows, filename = "data.csv", columns) {
  const blob = new Blob(["﻿" + toCsv(rows, columns)], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

/**
 * A styled download button. `rows`/`filename` may be values or zero-arg
 * functions, so the export always reflects the current filtered view at click
 * time. `columns` optionally fixes the column order.
 */
export function csvDownloadButton(rows, filename = "data.csv", columns) {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "csv-download";
  btn.textContent = "⬇ Download CSV";
  btn.style.cssText =
    "cursor:pointer;font-size:.85rem;padding:4px 12px;border:1px solid var(--theme-foreground-faint,#ccc);" +
    "border-radius:6px;background:var(--theme-background-alt,#f6f6f6);color:inherit";
  btn.addEventListener("click", () => {
    const r = typeof rows === "function" ? rows() : rows;
    const f = typeof filename === "function" ? filename() : filename;
    downloadCsv(r, f, columns);
  });
  return btn;
}
