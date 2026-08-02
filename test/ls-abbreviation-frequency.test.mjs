// Correctness gate for data/obs/ls_abbreviation_frequency.json (csl-atlas#222).
//
// The artifact splits each dictionary's <ls> total into per-abbreviation
// occurrence counts, so the load-bearing property is conservation: every <ls>
// citation contributes exactly one token, hence each dictionary's token counts
// must sum to the <ls> total already committed in data/obs/citation_registers.json.
// A drift in either builder (a changed <ls> pattern, a changed token splitter,
// a stale re-run of only one of the two) breaks that sum and fails here.

import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const readJson = file => JSON.parse(fs.readFileSync(path.join(ROOT, "data", "obs", file), "utf8"));

const freq = readJson("ls_abbreviation_frequency.json");
const registers = readJson("citation_registers.json");

const sumCounts = counts => Object.values(counts).reduce((a, b) => a + b, 0);

test("envelope carries the shared provenance/schema block", () => {
  assert.equal(freq.schemaVersion, "1.0.0");
  assert.equal(freq.license, "CC-BY-SA-4.0");
  assert.equal(freq.licenseUrl, "https://creativecommons.org/licenses/by-sa/4.0/");
  assert.equal(freq.generatedBy, "scripts/obs/ls_abbreviation_frequency.py");
  assert.equal(freq.sourceRoot, registers.sourceRoot);
  assert.match(freq.generatedAt, /^\d{4}-\d{2}-\d{2}T/);
  for (const key of ["extraction", "token", "form", "invariant", "ordering"]) {
    assert.equal(typeof freq.method[key], "string", `method.${key} must document the pipeline`);
  }
  assert.equal(freq.dictionaryCount, Object.keys(freq.dicts).length);
});

test("covers exactly the dictionaries the register artifact covers", () => {
  assert.deepEqual(Object.keys(freq.dicts).sort(), Object.keys(registers.dicts).sort());
  assert.equal(freq.dictionaryCount, registers.dictionaryCount);
});

test("per-dictionary token counts sum to that dictionary's <ls> total", () => {
  for (const [code, counts] of Object.entries(freq.dicts)) {
    assert.equal(
      sumCounts(counts),
      registers.dicts[code].ls,
      `${code}: token counts must sum to the committed <ls> total`
    );
  }
  // Dictionaries with no <ls> apparatus are present with an empty map rather
  // than omitted — "0 <ls>" is a finding (indigenous iti citers), not absence.
  const empty = Object.entries(freq.dicts).filter(([, c]) => Object.keys(c).length === 0);
  assert.equal(empty.length, Object.keys(freq.dicts).length - freq.totals.dictsWithLs);
  assert.ok(empty.every(([code]) => registers.dicts[code].ls === 0));
});

test("corpus totals agree with both the per-dict maps and the register artifact", () => {
  const perDictSum = Object.values(freq.dicts).reduce((acc, c) => acc + sumCounts(c), 0);
  assert.equal(freq.totals.ls, perDictSum);
  assert.equal(freq.totals.ls, registers.totals.ls);
  assert.equal(
    freq.totals.distinctTokenDictPairs,
    Object.values(freq.dicts).reduce((acc, c) => acc + Object.keys(c).length, 0)
  );
  const corpusTokens = new Set(Object.values(freq.dicts).flatMap(c => Object.keys(c)));
  assert.equal(freq.totals.distinctTokensCorpus, corpusTokens.size);
  // Tokens are raw per-dictionary forms, so the corpus set is smaller than the
  // dict×token pair count only because dictionaries share abbreviations.
  assert.ok(freq.totals.distinctTokensCorpus <= freq.totals.distinctTokenDictPairs);
});

test("every token is a non-empty string with a positive integer count", () => {
  for (const [code, counts] of Object.entries(freq.dicts)) {
    for (const [token, n] of Object.entries(counts)) {
      assert.ok(token.length > 0, `${code}: empty token key`);
      assert.equal(token, token.trim(), `${code}: token "${token}" is not trimmed`);
      assert.ok(Number.isInteger(n) && n > 0, `${code}/${token}: count must be a positive integer`);
    }
  }
});

// A locator-only citation (`<ls>78</ls>`, no siglum at all) yields an
// integer-like token, and every JS engine hoists integer-like object keys to
// the front in numeric order regardless of the order they were written in. So
// the artifact's count-descending write order survives only for the remaining
// keys, and no consumer may rely on key order — hence method.ordering says
// "sort by value". These two tests pin both halves of that.
const INTEGER_LIKE = /^(0|[1-9][0-9]*)$/;

test("non-numeric tokens keep the written count-descending order", () => {
  for (const [code, counts] of Object.entries(freq.dicts)) {
    const entries = Object.entries(counts).filter(([token]) => !INTEGER_LIKE.test(token));
    for (let i = 1; i < entries.length; i += 1) {
      const [prevToken, prevN] = entries[i - 1];
      const [token, n] = entries[i];
      assert.ok(
        prevN > n || (prevN === n && prevToken < token),
        `${code}: ${prevToken}×${prevN} must not precede ${token}×${n}`
      );
    }
  }
});

test("integer-like tokens are locator-only citations, hoisted by JS key order", () => {
  const numeric = Object.entries(freq.dicts).flatMap(([code, counts]) =>
    Object.keys(counts).filter(t => INTEGER_LIKE.test(t)).map(t => [code, t, counts[t]])
  );
  assert.ok(numeric.length > 0, "the corpus does contain locator-only <ls> citations");
  // Rare enough that they are a documented curiosity, not a parsing failure.
  const share = numeric.reduce((acc, [, , n]) => acc + n, 0) / freq.totals.ls;
  assert.ok(share < 0.001, `locator-only citations are ${(share * 100).toFixed(4)}% of the apparatus`);
  // …and they are exactly the keys that break naive "first key = most cited".
  for (const [code] of numeric) {
    const first = Object.keys(freq.dicts[code])[0];
    assert.ok(INTEGER_LIKE.test(first), `${code}: JS hoists numeric keys, so "${first}" leads`);
  }
});

test("the attributed <ls n=…> shape is counted (H1086 regression guard)", () => {
  // MW writes most of its apparatus as <ls n="RV.">…</ls>; a literal `<ls>`
  // matcher undercounted MW by 28.6%, which would show up here as a missing
  // or badly deflated RV token.
  assert.ok(freq.dicts.mw.RV > 10000, "MW's attributed RV citations must be counted");
  assert.equal(sumCounts(freq.dicts.mw), registers.dicts.mw.ls);
});
