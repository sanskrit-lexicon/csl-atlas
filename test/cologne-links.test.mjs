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

test("scanPageFromPc: AP90 page-column-digit drops the trailing digit marker (H2368-A11 follow-up gap fix)", () => {
  assert.equal(scanPageFromPc("ap90", "0351-1"), "0351", "column marker resets to numeric at a new-letter section break");
  assert.equal(scanPageFromPc("ap90", "0220-1"), "0220");
  assert.equal(scanPageFromPc("ap90", "0351-2"), "0351");
});

test("scanPageFromPc: unresolvable shapes stay null (no invented links)", () => {
  assert.equal(scanPageFromPc("ap90", ""), null);
  assert.equal(scanPageFromPc("ap90", "abc"), null);
  assert.equal(scanPageFromPc("mw", "abc,1"), null);
  assert.equal(scanPageFromPc("ap90", "0001-x0"), null, "trailing chunk must be letters only, not alnum");
});

test("scanUrl: null dict or unparseable pc yields no URL; ap90 now resolves (H2368 gap fix)", () => {
  assert.equal(scanUrl("nmmb", "1"), null, "nmmb spot-check failed live (A11) — deliberately not in COLOGNE_SCAN_DIR");
  assert.equal(scanUrl("ap90", "0001-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/webtc/servepdf.php?page=0001");
});

test("scanUrl: A11 dicts resolve with their verified scan dir and year", () => {
  assert.equal(scanUrl("wil", "001"), "https://sanskrit-lexicon.uni-koeln.de/scans/WILScan/2020/web/webtc/servepdf.php?page=001");
  assert.equal(scanUrl("fri", "011"), "https://sanskrit-lexicon.uni-koeln.de/scans/FRIScan/2025/web/webtc/servepdf.php?page=011");
  assert.equal(scanUrl("abch", "5"), "https://sanskrit-lexicon.uni-koeln.de/scans/ABCHScan/2023/web/webtc/servepdf.php?page=5");
  assert.equal(scanUrl("acsj", "1"), "https://sanskrit-lexicon.uni-koeln.de/scans/ACSJScan/2023/web/webtc/servepdf.php?page=1");
  assert.equal(scanUrl("acph", "1"), "https://sanskrit-lexicon.uni-koeln.de/scans/ACPHScan/2023/web/webtc/servepdf.php?page=1");
});

test("scanUrl: A12 dicts resolve with their verified scan dir and year (bur/stc/vcp/ae/bhs/gra)", () => {
  assert.equal(scanUrl("bur", "066,2"), "https://sanskrit-lexicon.uni-koeln.de/scans/BURScan/2020/web/webtc/servepdf.php?page=066");
  assert.equal(scanUrl("stc", "42,1"), "https://sanskrit-lexicon.uni-koeln.de/scans/STCScan/2020/web/webtc/servepdf.php?page=42");
  assert.equal(scanUrl("vcp", "0180,b"), "https://sanskrit-lexicon.uni-koeln.de/scans/VCPScan/2020/web/webtc/servepdf.php?page=0180");
  assert.equal(scanUrl("vcp", "001-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/VCPScan/2020/web/webtc/servepdf.php?page=001", "vcp also carries the page-column-letter dash shape");
  assert.equal(scanUrl("ae", "068"), "https://sanskrit-lexicon.uni-koeln.de/scans/AEScan/2020/web/webtc/servepdf.php?page=068");
  assert.equal(scanUrl("bhs", "068,1"), "https://sanskrit-lexicon.uni-koeln.de/scans/BHSScan/2020/web/webtc/servepdf.php?page=068");
  assert.equal(scanUrl("gra", "0247"), "https://sanskrit-lexicon.uni-koeln.de/scans/GRAScan/2020/web/webtc/servepdf.php?page=0247");
});

test("COLOGNE_SCAN_DIR names the twenty-one live-verified dicts (H2368 + A11 + A12)", () => {
  assert.deepEqual(COLOGNE_SCAN_DIR, {
    mw: "MW",
    pwg: "PWG",
    ap90: "AP90",
    wil: "WIL",
    cae: "CAE",
    bor: "BOR",
    fri: "FRI",
    ieg: "IEG",
    armh: "ARMH",
    krm: "KRM",
    abch: "ABCH",
    pgn: "PGN",
    snp: "SNP",
    acsj: "ACSJ",
    acph: "ACPH",
    bur: "BUR",
    stc: "STC",
    vcp: "VCP",
    ae: "AE",
    bhs: "BHS",
    gra: "GRA"
  });
});

test("entryUrl is unaffected by the scanPageFromPc fix", () => {
  assert.equal(
    entryUrl("ap90", "aRin"),
    "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/webtc/indexcaller.php?key=aRin&transLit=slp1&filter=roman"
  );
});
