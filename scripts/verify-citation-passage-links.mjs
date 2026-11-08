// Verify the GRETIL passage-link pilot (H7100).
//
// The committed pilot (data/citations/citation-passage-links.json) is a
// deterministic candidate list. This script is the non-deterministic half:
// it performs the HTTP checks, confirms the per-verse anchor is present in the
// edition page, and writes a provenance snapshot. The builder merges that
// snapshot back into the pilot on the next run, so the committed JSON carries
// the last verification result without making the build depend on the network.
//
// Usage: npm run verify-citation-passage-links

import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const LINKS_PATH = path.resolve(process.cwd(), "data", "citations", "citation-passage-links.json");
const OUT_PATH = path.resolve(process.cwd(), "data", "citations", "citation-passage-link-verification.json");
const RETRIES = 3;
const CONCURRENCY = 6;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function pageUrl(url) {
  const parsed = new URL(url);
  parsed.hash = "";
  return parsed.toString();
}

async function headStatus(url) {
  let lastError = null;
  for (let attempt = 1; attempt <= RETRIES; attempt++) {
    try {
      const response = await fetch(url, { method: "HEAD", redirect: "follow" });
      if (response.ok) return { status: response.status, method: "HEAD" };
      if (response.status !== 405 && response.status !== 403) return { status: response.status, method: "HEAD" };
    } catch (error) {
      lastError = error;
    }
    await sleep(300 * attempt);
  }
  // Some servers refuse HEAD; a one-byte ranged GET still proves the URL.
  for (let attempt = 1; attempt <= RETRIES; attempt++) {
    try {
      const response = await fetch(url, { method: "GET", headers: { Range: "bytes=0-0" }, redirect: "follow" });
      return { status: response.status, method: "GET-range" };
    } catch (error) {
      lastError = error;
    }
    await sleep(300 * attempt);
  }
  throw lastError ?? new Error(`could not check ${url}`);
}

async function fetchAnchorSet(url) {
  const response = await fetch(url, { redirect: "follow" });
  if (!response.ok) throw new Error(`HTTP ${response.status} downloading ${url}`);
  const html = await response.text();
  const anchors = new Set();
  for (const match of html.matchAll(/\bid="([^"]+)"/g)) anchors.add(match[1]);
  return anchors;
}

async function mapLimit(items, limit, fn) {
  const results = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (cursor < items.length) {
      const index = cursor++;
      results[index] = await fn(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return results;
}

async function main() {
  const pilot = JSON.parse(fs.readFileSync(LINKS_PATH, "utf8"));
  const items = pilot.items || [];
  if (!items.length) throw new Error("pilot has no items; run npm run build-citation-passage-index first");

  const pages = new Map();
  for (const item of items) {
    const page = pageUrl(item.url);
    if (!pages.has(page)) pages.set(page, item.gretilId);
  }

  const anchorSets = new Map();
  for (const page of pages.keys()) {
    process.stdout.write(`Fetching ${page} ... `);
    anchorSets.set(page, await fetchAnchorSet(page));
    console.log(`${anchorSets.get(page).size} ids`);
  }

  const results = await mapLimit(items, CONCURRENCY, async (item) => {
    const { status, method } = await headStatus(item.url);
    const anchorVerified = anchorSets.get(pageUrl(item.url))?.has(item.gretilId) ?? false;
    return {
      url: item.url,
      gretilId: item.gretilId,
      httpStatus: status,
      anchorVerified,
      method,
      ok: status === 200 && anchorVerified
    };
  });

  const snapshot = {
    schemaVersion: "1.0.0",
    generatedBy: "npm run verify-citation-passage-links",
    checkedAt: new Date().toISOString(),
    method: "HTTP HEAD (one-byte ranged GET fallback) per URL + per-verse anchor presence in the fetched GRETIL edition page.",
    summary: {
      checked: results.length,
      http200: results.filter((r) => r.httpStatus === 200).length,
      anchorVerified: results.filter((r) => r.anchorVerified).length,
      ok: results.filter((r) => r.ok).length
    },
    results
  };
  fs.writeFileSync(OUT_PATH, `${JSON.stringify(snapshot, null, 2)}\n`);
  console.log(`Checked ${results.length} links: HTTP 200 ${snapshot.summary.http200}, anchors ${snapshot.summary.anchorVerified}, ok ${snapshot.summary.ok}`);
  console.log(`- ${path.relative(process.cwd(), OUT_PATH)}`);
  if (snapshot.summary.ok !== results.length) process.exitCode = 1;
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  main().catch((error) => {
    console.error(error);
    process.exit(1);
  });
}
