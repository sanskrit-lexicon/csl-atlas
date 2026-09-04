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
  assert.equal(scanPageFromPc("ap90", "0001-a1b"), null, "letters-digit-letters trailing chunk is not a verified marker");
});

test("scanPageFromPc: GRA unseparated page-column drops the trailing letters (H2368-A07 gap fix)", () => {
  assert.equal(scanPageFromPc("gra", "0307a"), "0307", "digitisation slip for the separated '0307-a' shape; live-verified servepdf page=0307");
  assert.equal(scanPageFromPc("gra", "1365a"), "1365");
  assert.equal(scanPageFromPc("gra", "12x0"), null, "digits must come first, letters only after");
});

test("scanUrl: null dict or unparseable pc yields no URL; ap90 now resolves (H2368 gap fix)", () => {
  assert.equal(scanUrl("nmmb", "1"), null, "nmmb viewer shell answers but every scan pdf it names 404s (re-tried H3725) — deliberately not in COLOGNE_SCAN_DIR");
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
});

test("scanPageFromPc: AP/MD letter-then-digit marker (H2368-A08 follow-up)", () => {
  assert.equal(scanPageFromPc("ap", "0379-a1"), "0379", "ap-meta2.txt [PagePPPP-UC] letter-break; live-verified servepdf page=0379");
  assert.equal(scanPageFromPc("ap", "1321-a2"), "1321");
  assert.equal(scanPageFromPc("md", "036-a1"), "036", "md-meta2.txt [PageUY-C]; live-verified servepdf page=036");
  assert.equal(scanPageFromPc("md", "060-a3"), "060");
  assert.equal(scanPageFromPc("ap90", "0117-a1"), "0117", "same shape now trusted after ap/md live verification");
});

test("scanPageFromPc: SCH unseparated-page then column (H2368-A08 follow-up)", () => {
  assert.equal(scanPageFromPc("sch", "104a-1"), "104", "sch-meta2.txt PPPa.C; live-verified servepdf page=104");
  assert.equal(scanPageFromPc("sch", "186a-3"), "186");
  assert.equal(scanPageFromPc("sch", "198-1"), "198", "plain page-column-digit still resolves");
});

test("scanPageFromPc: LRV dotted-column (H2368-A08 follow-up)", () => {
  assert.equal(scanPageFromPc("lrv", "120-12.1"), "120", "live-verified servepdf page=120");
  assert.equal(scanPageFromPc("lrv", "839-22.1"), "839");
  assert.equal(scanPageFromPc("lrv", "425-32"), "425", "plain two-digit column still resolves");
});

test("scanPageFromPc: pw/pwkvn three-part vol-page-col keeps the vol-page value (H3695, H839)", () => {
  assert.equal(scanPageFromPc("pw", "7-385-d"), "7-385", "dominant page-column-letter marker drops; live-verified servepdf page=7-385");
  assert.equal(scanPageFromPc("pw", "1-001-b"), "1-001");
  assert.equal(scanPageFromPc("pwkvn", "2-288-a"), "2-288", "live-verified servepdf page=2-288");
  assert.equal(scanPageFromPc("pw", "7-384-1a"), "7-384", "bop-class digit-then-letters letter-break marker drops");
  assert.equal(scanPageFromPc("pwkvn", "7-366-1"), "7-366", "ap90-class digit-only section-break marker drops");
  assert.equal(scanPageFromPc("pw", "1-0614"), "1-0614", "two-part vol-page passes through verbatim (H839 PWG contract)");
  assert.equal(scanPageFromPc("pw", "385"), null, "bare page must not silently default to volume 1");
  assert.equal(scanPageFromPc("pw", "7-385-1a2"), null, "mixed trailing chunk is not a verified marker shape");
  assert.equal(scanPageFromPc("pwkvn", "x-288-a"), null);
});

test("scanUrl: A08 dict resolves with its verified scan dir and year (bop)", () => {
  assert.equal(scanUrl("bop", "322-b"), "https://sanskrit-lexicon.uni-koeln.de/scans/BOPScan/2020/web/webtc/servepdf.php?page=322", "live-verified servepdf page=322");
  assert.equal(scanUrl("bop", "027-1a"), "https://sanskrit-lexicon.uni-koeln.de/scans/BOPScan/2020/web/webtc/servepdf.php?page=027", "letter-break shape");
});

test("scanUrl: A08 follow-up dicts resolve with verified scan dir and year (ap/ccs/lrv/md/sch)", () => {
  assert.equal(scanUrl("ap", "0923-2"), "https://sanskrit-lexicon.uni-koeln.de/scans/APScan/2020/web/webtc/servepdf.php?page=0923", "live-verified servepdf page=0923");
  assert.equal(scanUrl("ap", "0379-a1"), "https://sanskrit-lexicon.uni-koeln.de/scans/APScan/2020/web/webtc/servepdf.php?page=0379", "letter-then-digit residual");
  assert.equal(scanUrl("ccs", "264-2"), "https://sanskrit-lexicon.uni-koeln.de/scans/CCSScan/2020/web/webtc/servepdf.php?page=264", "live-verified servepdf page=264");
  assert.equal(scanUrl("ccs", "038-1a"), "https://sanskrit-lexicon.uni-koeln.de/scans/CCSScan/2020/web/webtc/servepdf.php?page=038", "bop letter-break shape");
  assert.equal(scanUrl("lrv", "425-32"), "https://sanskrit-lexicon.uni-koeln.de/scans/LRVScan/2022/web/webtc/servepdf.php?page=425", "lrv deploys at year 2022 per redo_cologne_all.sh");
  assert.equal(scanUrl("lrv", "120-12.1"), "https://sanskrit-lexicon.uni-koeln.de/scans/LRVScan/2022/web/webtc/servepdf.php?page=120", "dotted-column residual");
  assert.equal(scanUrl("md", "137-3"), "https://sanskrit-lexicon.uni-koeln.de/scans/MDScan/2020/web/webtc/servepdf.php?page=137", "live-verified servepdf page=137");
  assert.equal(scanUrl("md", "036-a1"), "https://sanskrit-lexicon.uni-koeln.de/scans/MDScan/2020/web/webtc/servepdf.php?page=036", "letter-then-digit residual");
  assert.equal(scanUrl("sch", "198-1"), "https://sanskrit-lexicon.uni-koeln.de/scans/SCHScan/2020/web/webtc/servepdf.php?page=198", "live-verified servepdf page=198");
  assert.equal(scanUrl("sch", "104a-1"), "https://sanskrit-lexicon.uni-koeln.de/scans/SCHScan/2020/web/webtc/servepdf.php?page=104", "unseparated-page-then-column residual");
});

test("scanUrl: H3695 pw/pwkvn resolve to their vol-page servepdf URLs", () => {
  assert.equal(scanUrl("pw", "7-385-d"), "https://sanskrit-lexicon.uni-koeln.de/scans/PWScan/2020/web/webtc/servepdf.php?page=7-385", "live-verified servepdf page=7-385 (api=1 named the pdf)");
  assert.equal(scanUrl("pwkvn", "2-288-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/PWKVNScan/2020/web/webtc/servepdf.php?page=2-288", "live-verified servepdf page=2-288 (api=1 named the pdf)");
});

test("scanPageFromPc: pui/vei/acc/skd join the multi-volume family (H3725, H839)", () => {
  // pui/vei: pwg's verbatim "{vol}-{page}" contract.
  assert.equal(scanPageFromPc("pui", "2-444"), "2-444", "live-verified servepdf page=2-444");
  assert.equal(scanPageFromPc("vei", "2-015"), "2-015", "live-verified servepdf page=2-015");
  // acc: "{vol}-{page},{col}" — first comma-field is the vol-page, trailing
  // comma-chunk the column. A single-volume read would return "1" here
  // (volume-as-page for every entry) — the exact H839 failure mode.
  assert.equal(scanPageFromPc("acc", "1-618,1"), "1-618", "live-verified servepdf page=1-618; column after the comma drops");
  assert.equal(scanPageFromPc("acc", "2-003,2"), "2-003");
  // skd: pw/pwkvn's three-part family, vol 1..5.
  assert.equal(scanPageFromPc("skd", "3-122-a"), "3-122", "live-verified servepdf page=3-122");
  assert.equal(scanPageFromPc("skd", "2-486-a1"), "2-486", "letters-then-digit tail (ap/md letterThenDigit class on the MV tail); live-verified servepdf page=2-486");
  assert.equal(scanPageFromPc("skd", "1-001"), "1-001", "two-part vol-page passes through verbatim (H839 PWG contract)");
  // H839 guards: a bare page must not silently default to volume 1; mixed
  // trailing chunks stay untrusted.
  assert.equal(scanPageFromPc("pui", "444"), null);
  assert.equal(scanPageFromPc("acc", "618"), null);
  assert.equal(scanPageFromPc("skd", "937"), null);
  assert.equal(scanPageFromPc("skd", "2-486-1a2"), null);
  assert.equal(scanPageFromPc("acc", "1-618,a"), null, "non-digit comma-chunk is not a verified column shape");
});

test("scanUrl: H3725 pui/vei/acc/skd resolve to their vol-page servepdf URLs", () => {
  assert.equal(scanUrl("pui", "2-444"), "https://sanskrit-lexicon.uni-koeln.de/scans/PUIScan/2020/web/webtc/servepdf.php?page=2-444", "live-verified 03-09-2026");
  assert.equal(scanUrl("vei", "2-015"), "https://sanskrit-lexicon.uni-koeln.de/scans/VEIScan/2020/web/webtc/servepdf.php?page=2-015", "live-verified 03-09-2026");
  assert.equal(scanUrl("acc", "1-618,1"), "https://sanskrit-lexicon.uni-koeln.de/scans/ACCScan/2020/web/webtc/servepdf.php?page=1-618", "live-verified 03-09-2026");
  assert.equal(scanUrl("skd", "3-122-a"), "https://sanskrit-lexicon.uni-koeln.de/scans/SKDScan/2020/web/webtc/servepdf.php?page=3-122", "live-verified 03-09-2026");
  assert.equal(scanUrl("skd", "2-486-a1"), "https://sanskrit-lexicon.uni-koeln.de/scans/SKDScan/2020/web/webtc/servepdf.php?page=2-486", "letters-then-digit straggler");
});

test("COLOGNE_SCAN_DIR names the forty-four live-verified dicts (H2368 + A11 + A12 + A07 + A08 + A08 follow-up + H3695 + H3725)", () => {
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
    bop: "BOP",
    ap: "AP",
    ccs: "CCS",
    lrv: "LRV",
    md: "MD",
    sch: "SCH",
    pw: "PW",
    pwkvn: "PWKVN",
    pui: "PUI",
    vei: "VEI",
    acc: "ACC",
    skd: "SKD"
  });
});

test("entryUrl is unaffected by the scanPageFromPc fix", () => {
  assert.equal(
    entryUrl("ap90", "aRin"),
    "https://www.sanskrit-lexicon.uni-koeln.de/scans/AP90Scan/2020/web/webtc/indexcaller.php?key=aRin&transLit=slp1&filter=roman"
  );
});
