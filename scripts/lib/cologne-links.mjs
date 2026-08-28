// Cologne (CDSL) deep-link builder — entry-display and scan-page URLs.
//
// Why this exists: every source pointer in the atlas xref packets carried only a
// csl-orig GitHub blob link, i.e. the *digitised source line*. A human source-checking
// an edge needs to read the entry as the dictionary presents it (H1646 review feedback:
// "you give Предложение, but do not give links to Cologne, to check what the entries
// actually contain"). These two URL shapes are that link.
//
// ---------------------------------------------------------------------------
// 1. entryUrl() — the readable entry display
//
//   https://www.sanskrit-lexicon.uni-koeln.de/scans/{DICT}Scan/2020/web/webtc/
//     indexcaller.php?key={slp1}&transLit=slp1&filter=roman
//
//   Param contract read from the upstream template
//   (csl-websanlexicon/v02/makotemplates/web/webtc/): `Parm` (parm.php) maps
//   `key`|`word`|`citation` -> the headword, `transLit`|`input` -> the INPUT scheme,
//   `filter`|`output` -> the OUTPUT scheme. indexcaller.php pre-fills those inputs
//   from the query string (init_inputs_key(), indexcaller.php:156-168) and
//   main_webtc.js:118 fires `getWord()` on ready when the key is non-empty — the
//   comment there calls it "respond to RESTFUL requests". So the URL auto-searches
//   and lands on the entry; it is a real deep link, not just a pre-filled form.
//
//   Live-verified 25-07-2026 (H1646) against the underlying getword.php for both
//   dicts: MW `key=ARi` -> "the pin of the axle of a cart" (RV. i, 35, 6);
//   PWG `key=ARi` -> "der Zapfen der Achse" (ṚV. 1,35,6). Probes went through
//   WebFetch's egress deliberately — this host 429s a local IP on bursts
//   (Uprava SERVER_OUTAGES.md, the www.sanskrit-lexicon.uni-koeln.de row).
//
//   `filter=roman` (Roman Unicode / IAST) is the output default here because the
//   sheet's reviewer reads IAST; `deva` and `slp1` are the other accepted values.
//
// ---------------------------------------------------------------------------
// 2. scanUrl() — the printed page behind the entry
//
//   https://sanskrit-lexicon.uni-koeln.de/scans/{DICT}Scan/2020/web/webtc/
//     servepdf.php?page={page}
//
//   Semantics are kosha's `app/scan_resolver.py` scan_url(), reused rather than
//   re-derived (SHARED_CODE §8: consume, don't rebuild). The load-bearing trap it
//   documents (H839, live-verified): servepdf.php has NO vol=/volume= parameter —
//   for the multi-volume PWG the volume lives INSIDE the page value as
//   "{vol}-{page:04d}". A bare page silently defaults to volume 1, so a wrong link
//   returns 200 rather than failing.
//
//   That format is exactly PWG's own <pc> "vol-Spalte" field (e.g. "1-0614"), so for
//   PWG we pass <pc> through verbatim. MW's <pc> is "page,column" (e.g. "134,1") and
//   is single-volume, so we take the page half and drop the column.
//
// Emitting no link is always preferable to emitting a silently-wrong one: every
// function here returns null when it cannot build a URL it can stand behind.

const ENTRY_BASE = "https://www.sanskrit-lexicon.uni-koeln.de/scans";
const SCAN_BASE = "https://sanskrit-lexicon.uni-koeln.de/scans";

/**
 * csl-orig dict code -> Cologne scan-directory prefix. Extend as dicts are added.
 *
 * wil/cae/bor/fri/ieg/armh/krm/abch/pgn/snp/acsj/acph added A11 (H2368 roadmap
 * follow-on): dict-> {DIR}Scan/{year} verified against the production deploy
 * script `csl-websanlexicon/v02/redo_cologne_all.sh` (the source that builds
 * the live site), then spot-checked live via servepdf.php for every one of
 * the twelve before trusting it (WebFetch, single sequential requests — this
 * host 429s on bursts, Uprava SERVER_OUTAGES.md). `nmmb` was tried the same
 * way (NMMBScan/2026, per SanskritLexicography FINDINGS.md §50) and the probe
 * came back a broken/error response, not a scan page — left OUT rather than
 * guessed at; emitting no link beats emitting a silently-wrong one.
 *
 * bur/stc/vcp/ae/bhs/gra added A12 (H2368 roadmap follow-on, 28-08-2026),
 * same two-step verification: `redo_cologne_all.sh` maps all six to
 * `{DIR}Scan/2020`, and each dict's own `<dict>-meta2.txt` in csl-orig
 * documents `<pc>` as "page-col reference to scanned image" with continuous
 * page numbering and NO volume component (only PWG carries a volume prefix,
 * kosha scan_resolver MULTI_VOLUME_DICTS = {pwg}, H839) — so the existing
 * single-volume scanPageFromPc paths (bare page, page,column, page-marker)
 * apply verbatim, page = first comma-field. Live spot-checks: one
 * servepdf.php fetch per dict against a real mid-dict <pc> page (ae and gra
 * needed one retry each after transient transport errors — the endpoint
 * answered correctly on the second attempt; no dict left out).
 *
 * ben/gst/inm/lan/mci/mw72/mwe/nybj/pe/shs/yat added A07 (H2368 roadmap
 * follow-on, 28-08-2026), same two-step bar: `redo_cologne_all.sh` maps all
 * eleven to `{DIR}Scan/2020`, and each `<pc>` first comma-field grows like a
 * real continuous page number (hundreds of distinct values per dict; the
 * `<pc>`-documenting `-meta2.txt` files describe page-col references with no
 * volume component). One sequential servepdf.php live probe per dict on a
 * real mid-dict `<pc>` page. Two guarded exclusions discovered the same way:
 * `pui`/`vei`/`acc` `<pc>` values lead with a volume-like field (pui "1-001"
 * with first field ∈ {1,2,3}; vei ∈ {1,2}; acc ∈ {1,2,3}) — structurally
 * PWG's vol-Spalte (H839), so the single-volume rule would emit "?page=1..3"
 * for every entry; left OUT pending their own multi-volume rule + spot-check.
 * `nybj` needed `COLOGNE_SCAN_YEAR` = 2026 (`csl-websanlexicon/v02/
 * dictparms.py` dictyear, live-verified; its redo_cologne_all.sh "2020" path
 * 404s). gra's 23 unseparated "NNNa" `<pc>` stragglers resolved by the new
 * unseparated page-column rule in scanPageFromPc (see below), live-verified
 * at "0307a" -> page=0307.
 */
export const COLOGNE_SCAN_DIR = Object.freeze({
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
  yat: "YAT"
});

/**
 * Cologne scan-site year for dicts whose deployed folder isn't .../2020/ —
 * mirrors the year each dict was (re)published with in redo_cologne_all.sh /
 * dictparms.py. Absent codes default to 2020.
 */
const COLOGNE_SCAN_YEAR = Object.freeze({
  fri: "2025",
  abch: "2023",
  acsj: "2023",
  acph: "2023",
  nybj: "2026"
});

/** Dicts whose Cologne page keys are "{vol}-{page:04d}" rather than a bare page. */
const MULTI_VOLUME_DICTS = new Set(["pwg"]);

function scanDir(dictCode) {
  return COLOGNE_SCAN_DIR[String(dictCode ?? "").toLowerCase()] ?? null;
}

function scanYear(dictCode) {
  return COLOGNE_SCAN_YEAR[String(dictCode ?? "").toLowerCase()] ?? "2020";
}

/**
 * Cologne entry-display deep link for a headword.
 * @param {string} dictCode csl-orig dict code (mw, pwg, ap90)
 * @param {string} slp1Key  the <k1> SLP1 headword key
 * @param {{filter?: string}} [options] output scheme: roman (default) | deva | slp1
 * @returns {string|null} URL, or null when the dict has no known Cologne scan dir
 */
export function entryUrl(dictCode, slp1Key, options = {}) {
  const dir = scanDir(dictCode);
  const key = String(slp1Key ?? "").trim();
  if (!dir || !key) return null;
  const filter = options.filter ?? "roman";
  const year = scanYear(dictCode);
  return `${ENTRY_BASE}/${dir}Scan/${year}/web/webtc/indexcaller.php`
    + `?key=${encodeURIComponent(key)}&transLit=slp1&filter=${encodeURIComponent(filter)}`;
}

/**
 * Normalise a csl-orig <pc> field into the page value servepdf.php honours.
 * MW "134,1" (page,column) -> "134"; PWG "1-0614" (vol-Spalte) -> "1-0614";
 * AP90 "0001-a" (page-column-letter) -> "0001"; AP90 "0351-1" (page-column-digit,
 * seen at a new-letter section break where the column marker itself resets to
 * numeric — H2368-A11 follow-up) -> "0351"; GRA "0307a" (unseparated
 * page-column, a digitisation slip for "0307-a" — H2368-A07; the shape exists
 * in no other local dict) -> "0307".
 * @returns {string|null} null when <pc> is absent or not in a shape we trust
 */
export function scanPageFromPc(dictCode, pc) {
  const raw = String(pc ?? "").trim();
  if (!raw) return null;
  if (MULTI_VOLUME_DICTS.has(String(dictCode ?? "").toLowerCase())) {
    // Require the explicit "{vol}-{page}" shape: a bare page here would silently
    // resolve to volume 1 (H839), which is the failure mode worth refusing.
    return /^\d+-\d+$/.test(raw) ? raw : null;
  }
  const page = raw.split(",")[0].trim();
  if (/^\d+$/.test(page)) return page;
  // Single-volume "page-<column marker>" shape (observed for ap90, e.g. "0001-a"
  // or, at a new-letter section break, "0351-1"): the trailing chunk is a column
  // marker, not a volume — drop it and keep the page digits (with any leading
  // zeros, verbatim). The marker itself is either all letters or all digits, never
  // mixed (a mixed chunk like "x0" is not a marker shape we've verified).
  const columnMatch = page.match(/^(\d+)-([a-zA-Z]+|\d+)$/);
  if (columnMatch) return columnMatch[1];
  // Unseparated "page<column-letter>" shape (observed for gra, e.g. "0307a" —
  // a digitisation slip for "0307-a"): same semantics as the dash marker, just
  // missing the separator. Digits followed only by trailing letters; a mixed
  // chunk like "0117-a1" still does not match. A census of every local dict
  // confirmed this shape exists in no other dictionary, so the rule only ever
  // bites on verified page-col data (gra's -meta2.txt documents <pc> as a
  // page-col reference with continuous numbering, no volume component).
  const unseparatedMatch = page.match(/^(\d+)[a-zA-Z]+$/);
  return unseparatedMatch ? unseparatedMatch[1] : null;
}

/**
 * Cologne scan-page (PDF) link for a record's <pc>.
 * @returns {string|null} URL, or null when dict or <pc> cannot be resolved safely
 */
export function scanUrl(dictCode, pc) {
  const dir = scanDir(dictCode);
  const page = scanPageFromPc(dictCode, pc);
  if (!dir || !page) return null;
  const year = scanYear(dictCode);
  return `${SCAN_BASE}/${dir}Scan/${year}/web/webtc/servepdf.php?page=${encodeURIComponent(page)}`;
}

/**
 * Both Cologne links for one source record, as a flat object ready to spread
 * onto a packet source pointer. Keys are omitted when unresolvable.
 */
export function cologneLinksFor(dictCode, slp1Key, pc) {
  const entry = entryUrl(dictCode, slp1Key);
  const scan = scanUrl(dictCode, pc);
  return {
    ...(entry ? { cologneEntryHref: entry } : {}),
    ...(scan ? { cologneScanHref: scan } : {})
  };
}
