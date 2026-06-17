import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { buildH4Worksheet, buildXrefWorksheet } from "../scripts/build-review-worksheets.mjs";

const root = process.cwd();
const h4 = JSON.parse(fs.readFileSync(path.join(root, "data", "lexico", "h4_semantic_field_review_packet.json"), "utf8"));
const xref = JSON.parse(fs.readFileSync(path.join(root, "data", "lexico", "xref_source_check_packet.json"), "utf8"));
const lf = s => s.replace(/\r\n/g, "\n");
const countRows = md => (md.match(/^\*\*\d+\. `/gm) ?? []).length;

test("H4 worksheet lists exactly the needs-human-review rows and regenerates stably", () => {
  const md = buildH4Worksheet(h4);
  assert.equal(lf(fs.readFileSync(path.join(root, "docs", "H4_REVIEW_WORKSHEET.md"), "utf8")), lf(md));
  assert.equal(countRows(md), h4.counts.needsHumanReview);
  assert.ok(md.includes(`**${h4.counts.needsHumanReview} rows need human review**`));
});

test("Xref worksheet lists exactly the needs-source-check rows and flags missing edges", () => {
  const md = buildXrefWorksheet(xref);
  assert.equal(lf(fs.readFileSync(path.join(root, "docs", "XREF_REVIEW_WORKSHEET.md"), "utf8")), lf(md));
  assert.equal(countRows(md), xref.counts.needsHumanReview);
  assert.equal((md.match(/Exact edge missing in:/g) ?? []).length, xref.counts.sharedCoreRowsWithMissingExactEdge);
});
