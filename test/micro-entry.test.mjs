import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { featureCounts, buildLemmaMatrix } from "../scripts/build-micro-entry.mjs";

test("featureCounts tallies the structural markers in an entry body", () => {
  const body = '<ls>RV. 1</ls> gacchati <lex>cl.1</lex> iti <ls>MBh</ls> <div n="1"> <k2>gamana</k2>';
  const f = featureCounts(body);
  assert.equal(f.ls, 2);
  assert.equal(f.iti, 1);
  assert.equal(f.gram, 1);
  assert.equal(f.div, 1);
  assert.equal(f.subentry, 1);
  assert.equal(f.chars, body.length);
});

test("buildLemmaMatrix aggregates a lemma's entries per dictionary, ordered by size", () => {
  const fakeDicts = {
    big: [{ k1: "gam", body: "x".repeat(50) + "<ls>a</ls><ls>b</ls>", href: "h1", L: "1" }, { k1: "other", body: "skip" }],
    small: [{ k1: "gam/", body: "iti only", href: "h2", L: "2" }]
  };
  const rows = buildLemmaMatrix("gam", {
    iterate: code => fakeDicts[code] ?? [],
    exists: code => code in fakeDicts,
    codes: ["small", "big"]
  });
  assert.equal(rows.length, 2);
  assert.equal(rows[0].dict, "big");                 // bigger chars first
  assert.equal(rows[0].ls, 2);
  assert.equal(rows[0].citationRegister, "tagged");
  assert.equal(rows[1].dict, "small");
  assert.equal(rows[1].citationRegister, "iti");     // "iti" matched as a word
});

test("committed micro-gam.json shows the PWG citation-dense / MW etymology signature", () => {
  const p = path.join(process.cwd(), "data", "lexico", "micro-gam.json");
  const d = JSON.parse(fs.readFileSync(p, "utf8"));
  assert.equal(d.lemma, "gam");
  const by = Object.fromEntries(d.dictionaries.map(r => [r.dict, r]));
  assert.ok(by.pwg.ls > by.mw.ls * 5, "PWG is far more <ls>-dense than MW on gam");
  assert.ok(by.pwg.chars === Math.max(...d.dictionaries.map(r => r.chars)), "PWG is the largest gam entry");
  assert.ok(by.mw.etym > 0, "MW carries etymology on gam");
});
