import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import {
  buildCanonicalAliases,
  buildAbbreviationMap,
  expansionCandidates,
  foldText,
  gretilRvId,
  gretilRvUrl,
  parseTsv,
  resolveSourceLabel,
  SOURCE_OVERRIDES
} from "../scripts/build-citation-passage-index.mjs";

const ROOT = process.cwd();
const INDEX = JSON.parse(fs.readFileSync(path.join(ROOT, "data/citations/source-to-entries.json"), "utf8"));
const LINKS = JSON.parse(fs.readFileSync(path.join(ROOT, "data/citations/citation-passage-links.json"), "utf8"));

test("foldText folds anusvara and diacritics to one node key", () => {
  assert.equal(foldText("Rājataraṃgiṇī"), foldText("Rājataraṅgiṇī"));
  assert.equal(foldText("Ṛg-veda"), foldText("ṚGVEDA"));
  assert.equal(foldText("Mahābhārata"), "mahabharata");
});

test("canonical aliases include node labels, variants and bare parenthetical forms", () => {
  const nodes = parseTsv(fs.readFileSync(path.join(ROOT, "data/citations/ls_citation_nodes.tsv"), "utf8"));
  const aliases = buildCanonicalAliases(nodes);
  assert.equal(aliases.get(foldText("MAHĀBHĀRATA")), "Mahābhārata");
  assert.equal(aliases.get(foldText("Nirukta")), "Nirukta (Yāska)");
  assert.equal(aliases.get(foldText("Pāṇiniʼs Aṣṭādhyāyī")), "Pāṇini's Aṣṭādhyāyī");
});

test("MW abbreviation expansion candidates are literal substrings, never inferred", () => {
  const candidates = expansionCandidates("Varāha-mihira's Bṛhat-saṃhitā");
  assert.ok(candidates.includes("Varāha-mihira's Bṛhat-saṃhitā"));
  assert.ok(candidates.includes("Bṛhat-saṃhitā"));
  const map = buildAbbreviationMap(parseTsv("abbreviation\texpansion_iast\ttype\tcode\nRV.\tṚg-veda\tTitle\t07:18\n"));
  assert.deepEqual(resolveSourceLabel("RV", map, new Map([[foldText("Ṛgveda"), "Ṛgveda"]])), {
    canonical: "Ṛgveda",
    expansion: "Ṛg-veda",
    reason: "expansion-match"
  });
});

test("Pāṇ resolves to the cited work, not the author node", () => {
  const map = buildAbbreviationMap(parseTsv("abbreviation\texpansion_iast\ttype\tcode\nPāṇ.\tPāṇini\tTitle\tx\n"));
  const aliases = new Map([[foldText("Aṣṭādhyāyī (Pāṇini)"), "Aṣṭādhyāyī (Pāṇini)"], [foldText("Pāṇini"), "Pāṇini"]]);
  const resolved = resolveSourceLabel("Pāṇ", map, aliases);
  assert.equal(resolved.canonical, SOURCE_OVERRIDES["Pāṇ"]);
});

test("GRETIL RV ids use the edition's MMHHHVV anchor shape", () => {
  assert.equal(gretilRvId(5, 86, 5), "RV_5.086.05");
  assert.equal(gretilRvId(10, 191, 4), "RV_10.191.04");
  assert.equal(gretilRvUrl(5, 86, 5).split("#")[1], "RV_5.086.05");
});

test("source-to-entries covers the MW inventory with canonical node labels", () => {
  assert.equal(INDEX.counts.citations, 320828);
  assert.equal(INDEX.counts.mwRecordsScanned, 286560);
  assert.ok(INDEX.counts.canonicalSources >= 200);
  assert.ok(INDEX.counts.indexedCitations > 200000);
  for (const label of ["Mahābhārata", "Ṛgveda", "Rāmāyaṇa", "Rājataraṅgiṇī", "Aṣṭādhyāyī (Pāṇini)"]) {
    assert.ok(INDEX.sources[label], `missing canonical source ${label}`);
  }
  const mbh = INDEX.sources["Mahābhārata"];
  assert.equal(mbh.records.length, mbh.entryCount);
  assert.equal(new Set(mbh.records).size, mbh.records.length, "L records are deduplicated");
  assert.equal(mbh.dict, "MW");
  assert.equal(mbh.records[0], "37");
  assert.equal(mbh.lines["37"], 139);
});

test("editorial markers stay out of the text index", () => {
  assert.ok(!INDEX.sources["L"], "L. is not a text");
  assert.ok(!INDEX.sources["ib"], "ib. is not a text");
  assert.equal(INDEX.nontext["L"].citations, 40213);
  assert.equal(INDEX.nontext["ib"].citations, 10100);
  assert.equal(INDEX.counts.nontextCitations, 78014);
});

test("the RV passage pilot carries 100 HTTP-200 links with verified anchors", () => {
  assert.equal(LINKS.summary.pilotSize, 100);
  assert.equal(LINKS.summary.verified, 100);
  assert.equal(LINKS.summary.http200, 100);
  assert.equal(LINKS.summary.anchorVerified, 100);
  assert.equal(LINKS.items.length, 100);
  assert.equal(new Set(LINKS.items.map((item) => item.url)).size, 100);
  assert.equal(new Set(LINKS.items.map((item) => item.locus)).size, 100);
  for (const item of LINKS.items) {
    assert.equal(item.httpStatus, 200);
    assert.equal(item.anchorVerified, true);
    assert.match(item.url, /^https:\/\/gretil\.sub\.uni-goettingen\.de\/gretil\/corpustei\/transformations\/html\/sa_Rgveda-edAufrecht\.htm#RV_\d+\.\d{3}\.\d{2}$/);
    assert.equal(item.url.split("#")[1], item.gretilId);
    assert.ok(item.mwRecords.length >= 1);
    assert.ok(INDEX.sources["Ṛgveda"].records.includes(item.mwRecords[0]));
  }
});

test("pilot tables and provenance sidecar carry the 100 checked links", () => {
  const pilotTsv = fs.readFileSync(path.join(ROOT, "data/citations/passage_pilot.tsv"), "utf8").trim().split("\n");
  const checksTsv = fs.readFileSync(path.join(ROOT, "data/citations/passage_pilot_checks.tsv"), "utf8").trim().split("\n");
  const sidecar = JSON.parse(fs.readFileSync(path.join(ROOT, "data/citations/source-to-entries.source.json"), "utf8"));
  assert.equal(pilotTsv[0], "dict\tL\tcanonical_text\traw_locus\tdcs_id\tdcs_url\tgretil_url\tvedaweb_url\tstatus\tevidence");
  assert.equal(pilotTsv.length, 101);
  assert.equal(checksTsv.length, 101);
  assert.ok(pilotTsv.slice(1).every((row) => row.split("\t")[0] === "MW"));
  assert.ok(pilotTsv.slice(1).every((row) => row.split("\t")[8] === "200"));
  assert.ok(pilotTsv.slice(1).every((row) => row.split("\t")[9] === "observed"));
  assert.ok(checksTsv.slice(1).every((row) => row.split("\t")[1] === "200"));
  assert.ok(checksTsv.slice(1).every((row) => row.split("\t")[4] === "yes"));
  assert.equal(sidecar.cslOrig.revision.length, 40);
  assert.equal(Object.keys(sidecar.outputs).length, 5);
  const csv = fs.readFileSync(path.join(ROOT, "data/citations/passage_pilot.csv"), "utf8").trim().split("\n");
  assert.equal(csv.length, 101);
});

test("citation-tracer is no longer a placeholder and all three tools carry a cited-at panel", () => {
  const tracer = fs.readFileSync(path.join(ROOT, "src/tools/citation-tracer.md"), "utf8");
  const source = fs.readFileSync(path.join(ROOT, "src/tools/source.md"), "utf8");
  const dossier = fs.readFileSync(path.join(ROOT, "src/tools/dictionary-dossier.md"), "utf8");
  assert.doesNotMatch(tracer, /Tier 3 tool — placeholder|Data prerequisite:.*not yet exported/i);
  assert.match(tracer, /source-to-entries\.json/);
  assert.match(tracer, /passage pilot/i);
  assert.match(tracer, /download the 100-row pilot \(csv\)/i);
  assert.match(source, /## Cited at/);
  assert.match(dossier, /## Cited at/);
});
