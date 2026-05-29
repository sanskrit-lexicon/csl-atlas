import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import {spawnSync} from "node:child_process";

const root = process.cwd();
const strict = process.argv.includes("--strict");
const checks = [];
const tempDirs = [];

function rel(file) {
  return path.relative(root, file).replace(/\\/g, "/");
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(path.join(root, relativePath), "utf8"));
}

function writeJson(relativePath, value) {
  const file = path.join(root, relativePath);
  fs.mkdirSync(path.dirname(file), {recursive: true});
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`, "utf8");
}

function safeCaseId(id) {
  return id.replace(/:/g, "-");
}

function firstLine(text = "") {
  return String(text).split(/\r?\n/).find(Boolean) || "";
}

function commandPath(command) {
  const probe = process.platform === "win32" ? "where" : "which";
  const result = spawnSync(probe, [command], {cwd: root, encoding: "utf8"});
  return result.status === 0 ? firstLine(result.stdout).trim() : "";
}

function run(command, args, options = {}) {
  return spawnSync(command, args, {
    cwd: root,
    encoding: "utf8",
    shell: process.platform === "win32",
    maxBuffer: 1024 * 1024 * 16,
    ...options
  });
}

function addCheck(check) {
  checks.push({
    ...check,
    status: check.status || "fail"
  });
}

function skipped(type, message, extra = {}) {
  addCheck({type, status: "skipped", message, ...extra});
}

function failed(type, message, extra = {}) {
  addCheck({type, status: "fail", message, ...extra});
}

function passed(type, message, extra = {}) {
  addCheck({type, status: "pass", message, ...extra});
}

function tail(text = "") {
  const lines = String(text).trim().split(/\r?\n/).filter(Boolean);
  return lines.slice(-8).join("\n");
}

function makeTempDir() {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "csl-atlas-external-"));
  tempDirs.push(dir);
  return dir;
}

function tryTeiOddCompile(compiler, oddPath, rngPath) {
  const candidates = [
    {args: [oddPath, rngPath], stdoutToFile: false},
    {args: ["--odd", oddPath, rngPath], stdoutToFile: false},
    {args: [oddPath], stdoutToFile: true}
  ];

  const attempts = [];
  for (const candidate of candidates) {
    const result = run(compiler, candidate.args);
    attempts.push({
      command: `${compiler} ${candidate.args.map(arg => arg.includes(" ") ? `"${arg}"` : arg).join(" ")}`,
      status: result.status,
      stdout: tail(result.stdout),
      stderr: tail(result.stderr)
    });

    if (result.status === 0) {
      if (candidate.stdoutToFile && result.stdout?.trim()) {
        fs.writeFileSync(rngPath, result.stdout, "utf8");
      }
      if (fs.existsSync(rngPath) && fs.statSync(rngPath).size > 0) {
        return {ok: true, attempts};
      }
    }
  }

  return {ok: false, attempts};
}

function resolveTeiRng() {
  const oddPath = path.join(root, "data/schema/tei-archival-profile.odd.xml");
  const envRng = process.env.CSL_ATLAS_TEI_RNG;
  if (envRng) {
    const resolved = path.resolve(root, envRng);
    if (!fs.existsSync(resolved)) {
      failed("tei-rng", `CSL_ATLAS_TEI_RNG points to a missing file: ${resolved}`);
      return "";
    }
    passed("tei-rng", "Using precompiled RELAX NG schema from CSL_ATLAS_TEI_RNG.", {
      schema: rel(resolved)
    });
    return resolved;
  }

  const compiler = commandPath("teitorelaxng");
  if (!compiler) {
    skipped(
      "tei-odd-compile",
      "TEI Stylesheets command teitorelaxng is not available; install TEI Stylesheets or set CSL_ATLAS_TEI_RNG to a precompiled RELAX NG schema."
    );
    return "";
  }

  const outDir = makeTempDir();
  const rngPath = path.join(outDir, "csl-tei-archival-profile.rng");
  const result = tryTeiOddCompile(compiler, oddPath, rngPath);
  if (!result.ok) {
    failed("tei-odd-compile", "TEI ODD to RELAX NG compilation failed.", {
      attempts: result.attempts
    });
    return "";
  }

  passed("tei-odd-compile", "TEI ODD compiled to RELAX NG with teitorelaxng.", {
    compiler,
    source: rel(oddPath)
  });
  return rngPath;
}

function teiValidator() {
  const jing = commandPath("jing");
  if (jing) return {tool: "jing", command: jing};

  const xmllint = commandPath("xmllint");
  if (xmllint) return {tool: "xmllint", command: xmllint};

  skipped("tei-xml-validator", "No external RELAX NG validator found; install jing or xmllint.");
  return null;
}

function runTeiValidation(models) {
  const rngPath = resolveTeiRng();
  const validator = rngPath ? teiValidator() : null;
  if (!rngPath || !validator) return;

  for (const model of models) {
    const xmlPath = path.join(root, "data/pilot/tei", `${safeCaseId(model.id)}.xml`);
    if (!fs.existsSync(xmlPath)) {
      failed("tei-xml", `Missing TEI XML file for ${model.id}.`, {id: model.id, file: rel(xmlPath)});
      continue;
    }

    const args = validator.tool === "jing"
      ? [rngPath, xmlPath]
      : ["--noout", "--relaxng", rngPath, xmlPath];
    const result = run(validator.command, args);
    if (result.status === 0) {
      passed("tei-xml", `External TEI XML validation passed for ${model.id}.`, {
        id: model.id,
        tool: validator.tool,
        file: rel(xmlPath)
      });
    } else {
      failed("tei-xml", `External TEI XML validation failed for ${model.id}.`, {
        id: model.id,
        tool: validator.tool,
        file: rel(xmlPath),
        stdout: tail(result.stdout),
        stderr: tail(result.stderr)
      });
    }
  }
}

function runShaclValidation(models) {
  const pyshacl = commandPath("pyshacl");
  const shapesPath = path.join(root, "data/schema/ontolex-frac-profile.shacl.ttl");
  if (!pyshacl) {
    skipped("shacl-engine", "pySHACL is not available; install pyshacl to run an external SHACL engine.");
    return;
  }

  for (const model of models) {
    const ttlPath = path.join(root, "data/pilot/rdf", `${safeCaseId(model.id)}.ttl`);
    if (!fs.existsSync(ttlPath)) {
      failed("shacl", `Missing RDF/Turtle file for ${model.id}.`, {id: model.id, file: rel(ttlPath)});
      continue;
    }

    const result = run(pyshacl, ["-s", shapesPath, "-f", "human", ttlPath]);
    if (result.status === 0) {
      passed("shacl", `External SHACL validation passed for ${model.id}.`, {
        id: model.id,
        tool: "pyshacl",
        file: rel(ttlPath)
      });
    } else {
      failed("shacl", `External SHACL validation failed for ${model.id}.`, {
        id: model.id,
        tool: "pyshacl",
        file: rel(ttlPath),
        stdout: tail(result.stdout),
        stderr: tail(result.stderr)
      });
    }
  }
}

const models = readJson("data/pilot/neutral-model.json");
runTeiValidation(models);
runShaclValidation(models);

const failedChecks = checks.filter(check => check.status === "fail");
const skippedChecks = checks.filter(check => check.status === "skipped");
const report = {
  generatedAt: new Date().toISOString(),
  generator: "scripts/validate-external-profiles.mjs",
  strict,
  caveat: "External validation depends on locally installed TEI and SHACL tooling. Skipped checks are recorded explicitly and fail only in --strict mode.",
  tools: {
    teiOddCompiler: commandPath("teitorelaxng") || null,
    teiXmlValidator: commandPath("jing") || commandPath("xmllint") || null,
    shaclValidator: commandPath("pyshacl") || null
  },
  totals: {
    checks: checks.length,
    passed: checks.filter(check => check.status === "pass").length,
    failed: failedChecks.length,
    skipped: skippedChecks.length
  },
  checks
};

writeJson("data/pilot/external-validation-review.json", report);
writeJson("src/data/pilot/external-validation-review.json", report);

for (const dir of tempDirs) {
  fs.rmSync(dir, {recursive: true, force: true});
}

if (failedChecks.length || (strict && skippedChecks.length)) {
  console.error(`External validation incomplete: ${failedChecks.length} failed, ${skippedChecks.length} skipped.`);
  process.exit(1);
}

console.log(`External validation report written: ${report.totals.passed} passed, ${report.totals.skipped} skipped.`);
