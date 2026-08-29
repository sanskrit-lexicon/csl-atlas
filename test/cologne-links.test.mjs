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

test("scanPageFromPc: GRA unseparated page-column drops the trailing letters (H2368-A07 gap fix)", () => {
  assert.equal(scanPageFromPc("gra", "0307a"), "0307", "digitisation slip for the separated '0307-a' shape; live-verified servepdf page=0307");
  assert.equal(scanPageFromPc("gra", "1365a"), "1365");
  assert.equal(scanPageFromPc("ap90", "0117-a1"), null, "mixed marker chunk (digits+letters) is still not trusted");
  assert.equal(scanPageFromPc("gra", "12x0"), null, "digits must come first, letters only after");
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

test("scanUrl: A07 dicts resolve with their verified scan dir and year (11-dict extension)", () => {
  // Real mid-dict <pc> values, each live-verified via servepdf.php 28-08-2026.
  assert.equal(scanUrl("ben", "0556-b"), "https://sanskrit-lexicon.uni-koeln.de/scans/BENScan/2020/web/webtc/servepdf.php?page=0556");
  assert.equal(scanUrl("gst", "105-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/GSTScan/2020/web/webtc/servepdf.php?page=105");
  assert.equal(scanUrl("inm", "443-1"), "https://sanskrit-lexicon.uni-koeln.de/scans/INMScan/2020/web/webtc/servepdf.php?page=443", "inm page-column-digit shape");
  assert.equal(scanUrl("lan", "187-b"), "https://sanskrit-lexicon.uni-koeln.de/scans/LANScan/2020/web/webtc/servepdf.php?page=187");
  assert.equal(scanUrl("mci", "363-b"), "https://sanskrit-lexicon.uni-koeln.de/scans/MCIScan/2020/web/webtc/servepdf.php?page=363");
  assert.equal(scanUrl("mw72", "0545-c"), "https://sanskrit-lexicon.uni-koeln.de/scans/MW72Scan/2020/web/webtc/servepdf.php?page=0545");
  assert.equal(scanUrl("mwe", "398-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/MWEScan/2020/web/webtc/servepdf.php?page=398");
  assert.equal(scanUrl("nybj", "0498"), "https://sanskrit-lexicon.uni-koeln.de/scans/NYBJScan/2026/web/webtc/servepdf.php?page=0498", "nybj deploys at year 2026 per csl-websanlexicon dictparms.py — its 2020 path 404s live");
  assert.equal(scanUrl("pe", "488-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/PEScan/2020/web/webtc/servepdf.php?page=488");
  assert.equal(scanUrl("shs", "429-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/SHSScan/2020/web/webtc/servepdf.php?page=429");
  assert.equal(scanUrl("yat", "446-b"), "https://sanskrit-lexicon.uni-koeln.de/scans/YATScan/2020/web/webtc/servepdf.php?page=446");
  assert.equal(scanUrl("gra", "0307a"), "https://sanskrit-lexicon.uni-koeln.de/scans/GRAScan/2020/web/webtc/servepdf.php?page=0307", "gra unseparated straggler, live-verified");
});

test("scanPageFromPc: BOP letter-break marker drops the trailing digit+letters (H2368-A08 gap fix)", () => {
  assert.equal(scanPageFromPc("bop", "027-1a"), "027", "bop-meta2.txt [PagePPP-zC+ NN] letter-break shape");
  assert.equal(scanPageFromPc("bop", "099-3b"), "099");
  assert.equal(scanPageFromPc("bop", "001-a"), "001", "plain dash-letter marker still resolves");
  assert.equal(scanPageFromPc("bop", "0117-a1"), null, "letters-then-digit order is still not trusted (matches the ap90 exclusion)");
});

test("scanUrl: A08 dict resolves with its verified scan dir and year (bop)", () => {
  assert.equal(scanUrl("bop", "322-b"), "https://sanskrit-lexicon.uni-koeln.de/scans/BOPScan/2020/web/webtc/servepdf.php?page=322", "live-verified servepdf page=322");
  assert.equal(scanUrl("bop", "027-1a"), "https://sanskrit-lexicon.uni-koeln.de/scans/BOPScan/2020/web/webtc/servepdf.php?page=027", "letter-break shape");
});

test("scanUrl: volume-prefixed pc dicts stay OUT (pui/vei/acc) — no silently-wrong links", () => {
  // Their <pc> leads with a volume-like field (pui ∈ {1,2,3}, vei ∈ {1,2},
  // acc ∈ {1,2,3}) — structurally PWG's vol-Spalte (H839). The single-volume
  // rule would emit "?page=1..3" for every entry; emitting no link beats that.
  assert.equal(scanUrl("pui", "1-001"), null);
  assert.equal(scanUrl("vei", "1-005"), null);
  assert.equal(scanUrl("acc", "1-001,1"), null);
});

test("COLOGNE_SCAN_DIR names the thirty-three live-verified dicts (H2368 + A11 + A12 + A07 + A08)", () => {
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
    gra: "GRA",
    ben: "BEN",
    gst: "GST",
    inm: "INM",
    lan: "LAN",
    mci: "MCI",
    mw72: "MW72",
    mwe: "MWE",
    nybj: "NYBJ",
    pe: "PE",
    shs: "SHS",
    yat: "YAT",
    bop: "BOP"
  });
});

test("entryUrl is unaffected by the scanPageFromPc fix", () => {
  assert.equal(
    entryUrl("ap90", "aRin"),
    "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/webtc/indexcaller.php?key=aRin&transLit=slp1&filter=roman"
  );
});
