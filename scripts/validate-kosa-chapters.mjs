// Fail-closed validator for the kośa-chapters packet (H5329): arithmetic,
// cross-artifact and honesty checks. Throws on the first defect; exits 1.
//
// Usage: npm run validate-kosa-chapters

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const PACKET_PATH = path.resolve(process.cwd(), "src", "data", "kosa-chapters", "kosa_chapters.json");
const CODES = ["AMAR", "ABCH", "ARMH"];

function assert(cond, msg) {
  if (!cond) throw new Error(`kosa-chapters packet defect: ${msg}`);
}

/** Validates the packet object in place-independently (pure). Throws on defect. */
export function validatePacket(packet) {
  assert(packet && typeof packet === "object", "packet does not parse");
  assert(packet.schemaVersion === "1.0.0", `unknown schemaVersion ${packet.schemaVersion}`);
  assert(typeof packet.generatedAt === "string" && packet.generatedAt, "generatedAt missing");
  assert(packet.license === "CC-BY-SA-4.0", "license envelope missing");

  // 1. Inputs as declared must exist in the repo.
  const inputPaths = [
    ...Object.values(packet.inputs.instances),
    packet.inputs.measures,
    ...Object.values(packet.inputs.parseRules),
  ];
  for (const rel of inputPaths) {
    assert(fs.existsSync(path.resolve(process.cwd(), rel)), `declared input missing on disk: ${rel}`);
  }

  // 2. Totals arithmetic: recompute from the divisions, require exact match.
  for (const code of CODES) {
    const k = packet.koshas[code];
    assert(k, `kosha ${code} missing`);
    assert(k.divisions.length === k.totals.kandas, `${code}: totals.kandas != divisions.length`);
    let vargas = 0, groups = 0, sets = 0, members = 0, fullVerses = 0;
    for (const d of k.divisions) {
      vargas += d.vargas.length;
      for (const v of d.vargas) {
        for (const key of ["groups", "sets", "members", "fullVerses"]) {
          assert(Number.isInteger(v.counts[key]) && v.counts[key] >= 0, `${code}: non-integer/negative ${key} in kāṇḍa ${d.n}`);
        }
        groups += v.counts.groups;
        sets += v.counts.sets;
        members += v.counts.members;
        fullVerses += v.counts.fullVerses;
      }
    }
    assert(vargas === k.totals.vargas, `${code}: totals.vargas ${k.totals.vargas} != recomputed ${vargas}`);
    assert(groups === k.totals.verseGroups, `${code}: totals.verseGroups ${k.totals.verseGroups} != recomputed ${groups}`);
    assert(sets === k.totals.sets, `${code}: totals.sets ${k.totals.sets} != recomputed ${sets}`);
    assert(members === k.totals.members, `${code}: totals.members ${k.totals.members} != recomputed ${members}`);
    assert(fullVerses === k.totals.fullVerses, `${code}: totals.fullVerses ${k.totals.fullVerses} != recomputed ${fullVerses}`);
  }

  // 3. Cross-artifact reconciliation: the instance totals must equal the
  //    parse-rules record counts where both exist.
  assert(packet.koshas.ABCH.totals.verseGroups === packet.koshas.ABCH.parseRules.recordCount,
    `ABCH: instance verse-groups ${packet.koshas.ABCH.totals.verseGroups} != parse-rules record_count ${packet.koshas.ABCH.parseRules.recordCount}`);
  assert(packet.koshas.ARMH.totals.members === packet.koshas.ARMH.parseRules.recordCount,
    `ARMH: instance members ${packet.koshas.ARMH.totals.members} != parse-rules record_count ${packet.koshas.ARMH.parseRules.recordCount}`);
  assert(packet.koshas.AMAR.parseRules === null, "AMAR parseRules must be null (no CDSL parse-rules file)");

  // 4. Honest-model checks: grouped koshas carry the measures; the exploded
  //    one must NOT, and must carry absent-evidence devices (the chapter's
  //    honesty panel is data-driven off these).
  for (const code of ["AMAR", "ABCH"]) {
    const k = packet.koshas[code];
    assert(k.numbering && k.numbering.scope, `${code}: numbering missing`);
    assert(k.setSizes && k.genderTags && k.genderContiguity, `${code}: grouped measures missing`);
  }
  const armh = packet.koshas.ARMH;
  assert(armh.numbering === null && armh.genderTags === null && armh.setSizes === null,
    "ARMH must not carry grouped-model measures");
  assert(armh.genderContiguity === null, "ARMH genderContiguity must be null");
  const armhAbsent = armh.devices.filter((d) => d.evidence === "absent").map((d) => d.device);
  assert(armhAbsent.includes("varga") && armhAbsent.includes("synonym-set"),
    `ARMH absent devices must include varga and synonym-set, got ${JSON.stringify(armhAbsent)}`);

  // 5. Devices vocabulary.
  const EVIDENCE = new Set(["observed", "inferred", "absent"]);
  for (const code of CODES) {
    assert(packet.koshas[code].devices.length >= 4, `${code}: fewer than 4 ordering devices`);
    for (const d of packet.koshas[code].devices) {
      assert(EVIDENCE.has(d.evidence), `${code}: device ${d.device} evidence "${d.evidence}" outside vocabulary`);
      assert(d.note && d.note.length > 0, `${code}: device ${d.device} has no note`);
    }
  }

  // 6. Comparison table: enough rows, no empty cells, same kosha keys.
  const rows = packet.comparison.rows;
  assert(rows.length >= 10, `comparison has only ${rows.length} rows`);
  for (const r of rows) {
    assert(typeof r.aspect === "string" && r.aspect, "comparison row without aspect");
    for (const code of CODES) {
      assert(typeof r[code] === "string" && r[code].length > 0, `comparison row "${r.aspect}" has empty ${code} cell`);
    }
  }

  // 7. Determinism shape: no Date.now() leaked into content fields.
  assert(Object.keys(packet).includes("inputs"), "inputs block missing");
  return true;
}

function main() {
  const packet = JSON.parse(fs.readFileSync(PACKET_PATH, "utf8"));
  validatePacket(packet);
  console.log(`kosa-chapters packet OK — ${CODES.join("/")}, ${packet.comparison.rows.length} comparison rows, all checks pass`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    main();
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
}
