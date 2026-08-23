import test from "node:test";
import assert from "node:assert/strict";
import { scanPageFromPc, scanUrl, entryUrl, COLOGNE_SCAN_DIR } from "../scripts/lib/cologne-links.mjs";

test("scanPageFromPc: MW page,column drops the column", () => {
  assert.equal(scanPageFromPc("mw", "134,1"), "134");
});

test("scanPageFromPc: PWG requires the explicit vol-page shape (H839)", () => {
  assert.equal(scanPageFromPc("pwg", "1-0614"), "1-0614");
  assert.equal(scanPageFromPc("pwg", "614"), null, "bare page must not silently default to volume 1");
});

test("scanPageFromPc: AP90 page-column-letter drops the trailing letter (H2368 gap fix)", () => {
  assert.equal(scanPageFromPc("ap90", "0001-a"), "0001");
  assert.equal(scanPageFromPc("ap90", "0001-c"), "0001");
  assert.equal(scanPageFromPc("ap90", "42-b"), "42");
});

test("scanPageFromPc: unresolvable shapes stay null (no invented links)", () => {
  assert.equal(scanPageFromPc("ap90", ""), null);
  assert.equal(scanPageFromPc("ap90", "abc"), null);
  assert.equal(scanPageFromPc("mw", "abc,1"), null);
  assert.equal(scanPageFromPc("ap90", "0001-x0"), null, "trailing chunk must be letters only, not alnum");
});

test("scanUrl: null dict or unparseable pc yields no URL; ap90 now resolves (H2368 gap fix)", () => {
  assert.equal(scanUrl("wil", "1"), null, "wil is not in COLOGNE_SCAN_DIR");
  assert.equal(scanUrl("ap90", "0001-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/webtc/servepdf.php?page=0001");
});

test("COLOGNE_SCAN_DIR still names only the three verified dicts", () => {
  assert.deepEqual(COLOGNE_SCAN_DIR, { mw: "MW", pwg: "PWG", ap90: "AP90" });
});

test("entryUrl is unaffected by the scanPageFromPc fix", () => {
  assert.equal(
    entryUrl("ap90", "aRin"),
    "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/webtc/indexcaller.php?key=aRin&transLit=slp1&filter=roman"
  );
});
