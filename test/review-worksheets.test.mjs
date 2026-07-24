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

test("H4 worksheet lists open or agent-adjudicated rows and regenerates stably", () => {
  const md = buildH4Worksheet(h4);
  assert.equal(lf(fs.readFileSync(path.join(root, "docs", "H4_REVIEW_WORKSHEET.md"), "utf8")), lf(md));
  const open = h4.counts.needsHumanReview ?? 0;
  const agent = h4.counts.agentReviewed ?? h4.sampleRows.filter(r => r.reviewStatus === "reviewed-ok").length;
  if (open > 0) {
    assert.equal(countRows(md), open);
    assert.ok(md.includes(`**${open} rows need human review**`));
  } else {
    // H1621: agent stage closed the human vote; worksheet is a decision ledger.
    assert.equal(countRows(md), agent);
    assert.ok(md.includes(`**${agent} rows agent-adjudicated`));
    assert.ok(md.includes("IAST"));
  }
});

test("Xref worksheet lists exactly the needs-source-check rows and flags missing edges", () => {
  const md = buildXrefWorksheet(xref);
  assert.equal(lf(fs.readFileSync(path.join(root, "docs", "XREF_REVIEW_WORKSHEET.md"), "utf8")), lf(md));
  assert.equal(countRows(md), xref.counts.needsHumanReview);
  assert.equal((md.match(/Exact edge missing in:/g) ?? []).length, xref.counts.sharedCoreRowsWithMissingExactEdge);
});
