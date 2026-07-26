// Validate the committed L0 GQD packet (H1578).
//
// CI-safe: every check runs from the committed artifacts alone. The generator
// (scripts/L0/s7_gqd.py) needs numpy and is therefore not re-run here; what is
// checked is that the committed numbers are internally consistent, that the
// gold trees match the taxa they claim, and that the metric was not silently
// redefined.
//
// Fails (exit 1) when:
// - data/L0/gqd_report.json, gqd_validation.csv, gqd_clade_recovery.csv,
//   gqd_tree_matrix.csv or either gold newick is missing/unparseable;
// - any GQD is outside [0,1], or gqd != n_disagree / n_gold_butterflies;
// - n_quartets != C(n_taxa,4), or butterflies exceed quartets;
// - a permutation block is incomplete (null_mean/sd/z/p out of range);
// - the CSV rows and the JSON rows disagree;
// - a clade-recovery row has n_recovered > n_quartets or a mis-stated rate;
// - the tree matrix is not square/symmetric with a zero diagonal in [0,1];
// - a gold newick's leaf set differs from taxa.full, or the documented groups
//   named in the report are not clades of gold_stemma.newick;
// - the metric citation or the limitations list has been emptied out.
//
// Usage: node scripts/validate-l0-gqd.mjs   (also runs inside npm run verify)

import fs from "node:fs";
import path from "node:path";

const L0 = path.resolve(process.cwd(), "data", "L0");
const REPORT = path.join(L0, "gqd_report.json");
const VALIDATION_CSV = path.join(L0, "gqd_validation.csv");
const RECOVERY_CSV = path.join(L0, "gqd_clade_recovery.csv");
const MATRIX_CSV = path.join(L0, "gqd_tree_matrix.csv");
const GOLD_STEMMA = path.join(L0, "gold", "gold_stemma.newick");
const GOLD_TRADITION = path.join(L0, "gold", "gold_tradition.newick");

const errors = [];
const notes = [];
const EPS = 1e-4;

function readText(file) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing required output: ${path.relative(process.cwd(), file)}`);
    return null;
  }
  return fs.readFileSync(file, "utf8");
}

function readJson(file) {
  const text = readText(file);
  if (text === null) return null;
  try {
    return JSON.parse(text);
  } catch (e) {
    errors.push(`Unparseable JSON: ${path.relative(process.cwd(), file)} (${e.message})`);
    return null;
  }
}

function readCsv(file) {
  const text = readText(file);
  if (text === null) return null;
  const lines = text.trim().split(/\r?\n/);
  const header = lines[0].split(",");
  return lines.slice(1).map((line) => {
    // No quoted commas are emitted in these files; assert that rather than parse.
    const cells = line.split(",");
    if (cells.length !== header.length) errors.push(`${path.basename(file)}: ragged row ${line.slice(0, 60)}`);
    return Object.fromEntries(header.map((h, i) => [h, cells[i]]));
  });
}

function choose4(n) {
  return (n * (n - 1) * (n - 2) * (n - 3)) / 24;
}

/** Parse a (label-only) newick into every clade it asserts, as sorted joined keys. */
function cladesOf(newick) {
  const s = newick.trim().replace(/;\s*$/, "");
  const clades = new Set();
  let pos = 0;
  function node() {
    if (s[pos] === "(") {
      pos += 1;
      let members = [];
      for (;;) {
        members = members.concat(node());
        if (s[pos] === ",") { pos += 1; continue; }
        if (s[pos] === ")") { pos += 1; break; }
        throw new Error(`unexpected ${s[pos]} at ${pos}`);
      }
      clades.add([...members].sort().join(","));
      return members;
    }
    const start = pos;
    while (pos < s.length && !"(),".includes(s[pos])) pos += 1;
    return [s.slice(start, pos).trim()];
  }
  const all = node();
  if (pos !== s.length) throw new Error(`trailing input at ${pos}`);
  return { leaves: [...all].sort(), clades };
}

const report = readJson(REPORT);
const rowsCsv = readCsv(VALIDATION_CSV);
const recovery = readCsv(RECOVERY_CSV);
const matrix = readCsv(MATRIX_CSV);
const stemma = readText(GOLD_STEMMA);
const tradition = readText(GOLD_TRADITION);

if (report) {
  const source = report.metric?.source ?? "";
  if (!/Pompei/.test(source) || !/Rama/.test(source)) {
    errors.push("metric.source no longer cites both Pompei et al. (2011) and Rama et al. (2018)");
  }
  if (!/butterflies/.test(report.metric?.definition ?? "")) {
    errors.push("metric.definition no longer states the butterfly/star normalisation");
  }
  if (!(report.limitations?.length >= 4)) {
    errors.push(`limitations list has ${report.limitations?.length ?? 0} entries — the honest-caveat block was gutted`);
  }
  if (!(report.metric?.n_perm >= 99) || !Number.isInteger(report.metric?.seed)) {
    errors.push("metric.n_perm / metric.seed missing — the run is not reproducible");
  }

  const allRows = [...(report.gqd ?? []), ...(report.head_to_head ?? [])];
  if (allRows.length === 0) errors.push("report contains no GQD rows");
  for (const r of allRows) {
    const label = `${r.tree} vs ${r.gold}`;
    if (!(r.gqd >= 0 && r.gqd <= 1)) errors.push(`${label}: gqd ${r.gqd} outside [0,1]`);
    if (r.gqd_pompei !== null && r.gqd_pompei !== undefined && !(r.gqd_pompei >= 0 && r.gqd_pompei <= 1)) {
      errors.push(`${label}: gqd_pompei ${r.gqd_pompei} outside [0,1]`);
    }
    if (Math.abs(r.gqd - r.n_disagree / r.n_gold_butterflies) > EPS) {
      errors.push(`${label}: gqd ${r.gqd} != n_disagree/n_gold_butterflies (${r.n_disagree}/${r.n_gold_butterflies})`);
    }
    if (r.n_quartets !== choose4(r.n_taxa)) {
      errors.push(`${label}: n_quartets ${r.n_quartets} != C(${r.n_taxa},4) = ${choose4(r.n_taxa)}`);
    }
    if (r.n_gold_butterflies > r.n_quartets) errors.push(`${label}: more butterflies than quartets`);
    if (r.n_disagree > r.n_gold_butterflies) errors.push(`${label}: n_disagree exceeds the butterfly count`);
    if (r.n_inferred_star > r.n_gold_butterflies) errors.push(`${label}: n_inferred_star exceeds the butterfly count`);
    if (r.n_inferred_star === 0 && r.gqd_pompei !== null && Math.abs(r.gqd - r.gqd_pompei) > EPS) {
      errors.push(`${label}: binary tree but gqd ${r.gqd} != gqd_pompei ${r.gqd_pompei}`);
    }
    if (r.n_perm !== undefined) {
      if (!(r.null_mean >= 0 && r.null_mean <= 1)) errors.push(`${label}: null_mean ${r.null_mean} outside [0,1]`);
      if (!(r.null_sd >= 0)) errors.push(`${label}: null_sd ${r.null_sd} negative`);
      if (!(r.p_perm > 0 && r.p_perm <= 1)) errors.push(`${label}: p_perm ${r.p_perm} outside (0,1]`);
      if (r.p_perm < 1 / (1 + r.n_perm) - EPS) errors.push(`${label}: p_perm ${r.p_perm} below the 1/(1+n_perm) floor`);
      if (r.null_min < 0 || r.null_min > 1) errors.push(`${label}: null_min ${r.null_min} outside [0,1]`);
    }
  }

  const taxa = [...(report.taxa?.full ?? [])].sort();
  if (taxa.length < 4) errors.push("taxa.full is missing or too small");
  const parsed = {};
  for (const [name, newick] of [["gold_stemma", stemma], ["gold_tradition", tradition]]) {
    if (!newick) continue;
    try {
      parsed[name] = cladesOf(newick);
    } catch (e) {
      errors.push(`${name}.newick does not parse: ${e.message}`);
      continue;
    }
    if (JSON.stringify(parsed[name].leaves) !== JSON.stringify(taxa)) {
      errors.push(`${name}.newick leaf set differs from taxa.full (${parsed[name].leaves.length} vs ${taxa.length})`);
    }
  }
  // Every documented group the report scores must actually be a clade of its gold.
  for (const row of report.clade_recovery ?? []) {
    const [goldName, groupName] = row.group.split(":");
    const gold = parsed[`gold_${goldName}`];
    if (!gold) continue;
    const key = row.members.split(" ").sort().join(",");
    if (!gold.clades.has(key)) {
      errors.push(`${row.group}: {${key}} is not a clade of gold_${goldName}.newick (group ${groupName})`);
    }
  }
  for (const row of report.clade_recovery ?? []) {
    if (row.n_recovered > row.n_quartets) errors.push(`${row.group}/${row.tree}: n_recovered > n_quartets`);
    if (row.recovery !== null && Math.abs(row.recovery - row.n_recovered / row.n_quartets) > EPS) {
      errors.push(`${row.group}/${row.tree}: recovery ${row.recovery} != ${row.n_recovered}/${row.n_quartets}`);
    }
  }
}

if (report && rowsCsv) {
  if (rowsCsv.length !== (report.gqd ?? []).length) {
    errors.push(`gqd_validation.csv has ${rowsCsv.length} rows, report.gqd has ${(report.gqd ?? []).length}`);
  } else {
    for (let i = 0; i < rowsCsv.length; i += 1) {
      const csvRow = rowsCsv[i];
      const jsonRow = report.gqd[i];
      if (csvRow.tree !== jsonRow.tree || csvRow.gold !== jsonRow.gold) {
        errors.push(`row ${i}: CSV (${csvRow.tree}/${csvRow.gold}) != JSON (${jsonRow.tree}/${jsonRow.gold})`);
      } else if (Math.abs(Number(csvRow.gqd) - jsonRow.gqd) > EPS) {
        errors.push(`row ${i} (${jsonRow.tree}/${jsonRow.gold}): CSV gqd ${csvRow.gqd} != JSON ${jsonRow.gqd}`);
      }
    }
  }
}

if (matrix) {
  const names = matrix.map((r) => r[""]);
  const cell = (a, b) => Number(matrix[a][names[b]]);
  for (let i = 0; i < names.length; i += 1) {
    if (Object.keys(matrix[i]).length !== names.length + 1) {
      errors.push(`gqd_tree_matrix.csv: row ${names[i]} is not square`);
      continue;
    }
    if (Math.abs(cell(i, i)) > EPS) errors.push(`gqd_tree_matrix.csv: diagonal ${names[i]} is ${cell(i, i)}, not 0`);
    for (let j = 0; j < names.length; j += 1) {
      const v = cell(i, j);
      if (!(v >= 0 && v <= 1)) errors.push(`gqd_tree_matrix.csv: ${names[i]}/${names[j]} = ${v} outside [0,1]`);
      if (Math.abs(v - cell(j, i)) > EPS) errors.push(`gqd_tree_matrix.csv: not symmetric at ${names[i]}/${names[j]}`);
    }
  }
  notes.push(`tree matrix: ${names.length} trees, symmetric, zero diagonal`);
}

if (recovery) {
  notes.push(`clade recovery: ${recovery.length} group x tree rows`);
}

for (const note of notes) console.log(`note: ${note}`);
if (errors.length > 0) {
  console.error(`validate-l0-gqd: ${errors.length} error(s)`);
  for (const e of errors) console.error(`- ${e}`);
  process.exit(1);
}
console.log("validate-l0-gqd: OK");
