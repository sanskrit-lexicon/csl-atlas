import fs from "node:fs/promises";
import path from "node:path";

const DICTS = ["mw", "pwg", "pwk"];
const DICT_LABEL = {
  mw: "Monier-Williams 1899",
  pwg: "Boehtlingk-Roth PWG",
  pwk: "Boehtlingk PWK"
};

const PROFILE_VERSION = "tei-archival-profile-v0.1";

function escapeXml(value) {
  return String(value ?? "").replace(/[<>&'"]/g, char => {
    switch (char) {
      case "<": return "&lt;";
      case ">": return "&gt;";
      case "&": return "&amp;";
      case "'": return "&apos;";
      case "\"": return "&quot;";
      default: return char;
    }
  });
}

function safeCaseId(id) {
  return id.replace(/:/g, "-");
}

function caseUrl(id) {
  return `https://sanskrit-lexicon.github.io/csl-atlas/case/${encodeURIComponent(id)}`;
}

function stripPseudoMarkup(raw) {
  return String(raw || "")
    .replace(/\{#([^#]+)#\}/g, "$1")
    .replace(/\{%([^%]+)%\}/g, "$1")
    .replace(/<ls\b[^>]*>([\s\S]*?)<\/ls>/g, " $1 ")
    .replace(/<[^>]+>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function extractDefinitions(raw, phenomena) {
  const plain = stripPseudoMarkup(raw);
  const defs = [];
  if (phenomena.includes("root")) {
    for (const match of plain.matchAll(/\bto\s+([^;:.]+?)(?=,?\s+(?:L\.|RV\.|TS\.|AV\.|VS\.|Dharma|See)|;|:|$)/g)) {
      const def = match[1].replace(/\s+/g, " ").trim();
      if (def && def.length <= 120 && !defs.includes(def)) defs.push(def);
      if (defs.length >= 8) break;
    }
  }
  if (defs.length === 0) {
    for (const match of String(raw || "").matchAll(/\{%([^%]+)%\}/g)) {
      const def = stripPseudoMarkup(match[1]);
      if (def && def.length <= 120 && !defs.includes(def)) defs.push(def);
      if (defs.length >= 6) break;
    }
  }
  return defs;
}

function extractCitations(raw, maxPerRecord = 40) {
  const citations = [];
  for (const match of String(raw || "").matchAll(/<ls\b([^>]*)>([\s\S]*?)<\/ls>/g)) {
    const attrs = match[1] || "";
    const source = stripPseudoMarkup(match[2]);
    const inherited = attrs.match(/\bn="([^"]+)"/)?.[1] || null;
    if (!source && !inherited) continue;
    citations.push({
      source: source || inherited,
      type: source === "L." ? "generic-lexicographer-hedge" : "named-source-citation",
      inheritedFrom: inherited
    });
    if (citations.length >= maxPerRecord) break;
  }
  return citations;
}

function entryType(model) {
  if (model.phenomena?.includes("root")) return "verbal-root";
  if (model.phenomena?.includes("compound")) return "compound";
  if (model.phenomena?.includes("continuation")) return "continuation";
  return model.forms?.[0]?.type || "lemma";
}

async function loadSourceIndexes(hardCases) {
  const indexes = {};
  for (const dict of DICTS) {
    const source = hardCases.sources?.[dict];
    if (!source) continue;
    const sourcePath = path.resolve(process.cwd(), source);
    const text = await fs.readFile(sourcePath, "utf8");
    const records = text.match(/<L>[\s\S]*?<LEND>/g) || [];
    indexes[dict] = new Map();
    for (const raw of records) {
      const L = raw.match(/^<L>([^<]+)/)?.[1];
      if (L) indexes[dict].set(L, raw.trim());
    }
  }
  return indexes;
}

function fullRaw(model, dict, indexes) {
  const L = model.records?.[dict]?.L;
  return indexes[dict]?.get(L) || model.records?.[dict]?.raw || "";
}

function formXml(model) {
  const form = model.forms?.[0] || {orth: model.key, type: entryType(model)};
  const grammar = form.grammar ? `      <gram type="category">${escapeXml(form.grammar)}</gram>\n` : "";
  const verbClass = form.verbClass ? `      <gram type="verb-class">${escapeXml(form.verbClass)}</gram>\n` : "";
  return [
    `    <form type="${escapeXml(form.type || "lemma")}">`,
    `      <orth notation="SLP1" xml:lang="sa-Latn-x-SLP1">${escapeXml(form.orth || model.key)}</orth>`,
    grammar || verbClass ? "      <gramGrp>" : "",
    grammar.trimEnd(),
    verbClass.trimEnd(),
    grammar || verbClass ? "      </gramGrp>" : "",
    "    </form>"
  ].filter(Boolean).join("\n");
}

function senseXml(model, rawMw) {
  const definitions = extractDefinitions(rawMw, model.phenomena || []);
  if (!definitions.length) {
    return `    <sense xml:id="${safeCaseId(model.id)}-sense-unparsed" n="unparsed"><note type="sense-status">No stable machine definition could be extracted; source record is preserved in cit/quote.</note></sense>`;
  }
  return definitions.map((def, index) => [
    `    <sense xml:id="${safeCaseId(model.id)}-sense-${index + 1}" n="${index + 1}">`,
    `      <def xml:lang="en">${escapeXml(def)}</def>`,
    "    </sense>"
  ].join("\n")).join("\n");
}

function relationXml(model) {
  const id = safeCaseId(model.id);
  const chunks = [];
  if (model.phenomena?.includes("root")) {
    const whitney = model.relations?.find(rel => rel.type === "whitney-root-association")?.target;
    chunks.push([
      `    <etym xml:id="${id}-root-relation" type="root">`,
      "      <lbl>verbal root</lbl>",
      whitney ? `      <ref type="whitney-root" target="urn:csl:whitney-root:${escapeXml(whitney)}">${escapeXml(whitney)}</ref>` : "      <note type=\"root-association\">No Whitney root pointer extracted.</note>",
      "    </etym>"
    ].join("\n"));
  }
  if (model.phenomena?.includes("compound")) {
    const decomp = model.relations?.find(rel => rel.type === "lexical-decomposition");
    const components = decomp?.components?.length
      ? decomp.components.map(component => `      <seg type="component">${escapeXml(component)}</seg>`).join("\n")
      : "      <note type=\"decomposition-status\">Component segmentation requires philological review.</note>";
    chunks.push([
      `    <etym xml:id="${id}-compound-relation" type="compound">`,
      components,
      "    </etym>"
    ].join("\n"));
  }
  if (model.phenomena?.includes("continuation")) {
    const eCode = model.relations?.find(rel => rel.type === "adjacency-continuation-parent")?.eCode || "unknown";
    chunks.push(`    <xr xml:id="${id}-continuation-relation" type="adjacency-continuation-parent" target="#e-${escapeXml(eCode)}"><ref>MW e=${escapeXml(eCode)}</ref></xr>`);
  }
  return chunks.join("\n");
}

function sourceRecordXml(model, dict, raw) {
  const id = safeCaseId(model.id);
  const rec = model.records?.[dict] || {};
  return [
    `    <cit xml:id="${id}-record-${dict}" type="source-entry" source="#dict-${dict}">`,
    "      <bibl type=\"cdsl-record\">",
    `        <title>${escapeXml(DICT_LABEL[dict])}</title>`,
    `        <idno type="L">${escapeXml(rec.L)}</idno>`,
    `        <idno type="line">${escapeXml(rec.line)}</idno>`,
    `        <idno type="pc">${escapeXml(rec.pc)}</idno>`,
    "      </bibl>",
    `      <quote xml:space="preserve">${escapeXml(raw)}</quote>`,
    "    </cit>"
  ].join("\n");
}

function citationIndexXml(model, rawByDict) {
  const id = safeCaseId(model.id);
  const rows = [];
  for (const dict of DICTS) {
    const citations = extractCitations(rawByDict[dict]);
    citations.forEach((citation, index) => {
      rows.push([
        `      <bibl xml:id="${id}-cite-${dict}-${index + 1}" type="${escapeXml(citation.type)}" corresp="#${id}-record-${dict}">`,
        `        <abbr>${escapeXml(citation.source)}</abbr>`,
        citation.inheritedFrom ? `        <ref type="inherited-siglum">${escapeXml(citation.inheritedFrom)}</ref>` : "",
        "      </bibl>"
      ].filter(Boolean).join("\n"));
    });
  }
  if (!rows.length) return "";
  return [
    "    <listBibl type=\"extracted-source-citations\">",
    "      <head>Machine-extracted citation index; source quotes preserve the archival text.</head>",
    rows.join("\n"),
    "    </listBibl>"
  ].join("\n");
}

function teiDocument(model, rawByDict, isReviewCase) {
  const id = safeCaseId(model.id);
  const phenomenaTerms = (model.phenomena || []).map(p => `          <term>${escapeXml(p)}</term>`).join("\n");
  const sourceRecords = DICTS.map(dict => sourceRecordXml(model, dict, rawByDict[dict])).join("\n");
  const relations = relationXml(model);
  const citationIndex = citationIndexXml(model, rawByDict);
  return `<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="${id}">
  <teiHeader>
    <fileDesc>
      <titleStmt>
        <title>MW-PWG-PWK interoperability case ${escapeXml(model.key)}</title>
        <respStmt>
          <resp>generated archival TEI profile</resp>
          <name>scripts/export-tei-stubs.mjs</name>
        </respStmt>
      </titleStmt>
      <publicationStmt>
        <publisher>CSL Atlas</publisher>
        <availability>
          <licence target="https://creativecommons.org/licenses/by-sa/4.0/">CC-BY-SA-4.0</licence>
        </availability>
      </publicationStmt>
      <sourceDesc>
        <p>Derived from CDSL MW, PWG, and PWK source records for interoperability analysis.</p>
      </sourceDesc>
    </fileDesc>
    <encodingDesc>
      <projectDesc>
        <p>${PROFILE_VERSION}; TEI is used as the archival/textual model. Raw CDSL records are preserved as escaped source-entry quotes, while selected lexical structures are promoted into TEI entry, form, sense, citation, and relation elements.</p>
      </projectDesc>
      <classDecl>
        <taxonomy xml:id="dicts">
          <category xml:id="dict-mw"><catDesc>Monier-Williams 1899</catDesc></category>
          <category xml:id="dict-pwg"><catDesc>Boehtlingk-Roth PWG</catDesc></category>
          <category xml:id="dict-pwk"><catDesc>Boehtlingk PWK</catDesc></category>
        </taxonomy>
      </classDecl>
    </encodingDesc>
    <profileDesc>
      <langUsage>
        <language ident="sa-Latn-x-SLP1">Sanskrit in SLP1 transliteration</language>
        <language ident="en">English</language>
        <language ident="de">German</language>
      </langUsage>
      <textClass>
        <keywords scheme="#phenomena">
${phenomenaTerms}
        </keywords>
      </textClass>
    </profileDesc>
    <revisionDesc>
      <change when="2026-05-29" who="#csl-atlas">${isReviewCase ? "Selected for the first 15-case validated TEI profile slice." : "Included in the full 50-case machine-reviewed TEI profile."}</change>
    </revisionDesc>
  </teiHeader>
  <text>
    <body>
      <entry xml:id="${id}-entry" type="${escapeXml(entryType(model))}" corresp="${escapeXml(caseUrl(model.id))}">
${formXml(model)}
${senseXml(model, rawByDict.mw)}
${relations}
${citationIndex}
${sourceRecords}
        <note type="profile-version">${PROFILE_VERSION}</note>
        <note type="review-status">${isReviewCase ? "validated-slice" : "full-50-machine-review"}</note>
        <note type="validation-scope">full-50-tei-odd-profile</note>
      </entry>
    </body>
  </text>
</TEI>
`;
}

async function main() {
  const modelPath = path.resolve(process.cwd(), "data", "pilot", "neutral-model.json");
  const hardPath = path.resolve(process.cwd(), "data", "pilot", "hard-cases.json");
  const reviewPath = path.resolve(process.cwd(), "data", "pilot", "review-cases.json");
  const outputDir = path.resolve(process.cwd(), "data", "pilot", "tei");

  await fs.rm(outputDir, {recursive: true, force: true});
  await fs.mkdir(outputDir, {recursive: true});

  const models = JSON.parse(await fs.readFile(modelPath, "utf8"));
  const hardCases = JSON.parse(await fs.readFile(hardPath, "utf8"));
  const review = JSON.parse(await fs.readFile(reviewPath, "utf8"));
  const reviewIds = new Set(review.items.map(item => item.id));
  const indexes = await loadSourceIndexes(hardCases);

  for (const model of models) {
    const rawByDict = Object.fromEntries(DICTS.map(dict => [dict, fullRaw(model, dict, indexes)]));
    const xml = teiDocument(model, rawByDict, reviewIds.has(model.id));
    await fs.writeFile(path.join(outputDir, `${safeCaseId(model.id)}.xml`), xml, "utf8");
  }

  console.log(`Exported ${models.length} TEI archival profile files to ${outputDir}; ${reviewIds.size} are in the validated review slice.`);
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
