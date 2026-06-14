const CSL_ORIG_GITHUB_BASE = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02";

export function localeTranslator(locale) {
  return key => {
    const parts = String(key).split(".");
    let result = locale;
    for (const part of parts) {
      if (result && result[part] !== undefined) result = result[part];
      else return key;
    }
    return result;
  };
}

export function normalizeLanguageChoice(value) {
  const raw = String(value ?? "").toLowerCase();
  return value === 1 || raw === "1" || raw === "ru" || raw === "russian" || raw === "русский" ? "ru" : "en";
}

export function normalizeLookupMode(value, fallback = "core") {
  const raw = String(value ?? "").toLowerCase();
  if (value === 1 || raw === "1" || raw === "broad" || raw === "broadheadword") return "broad";
  if (raw === "core" || raw === "corecomparison") return "core";
  return fallback;
}

export function queryParam(name, search = globalThis.location?.search ?? "") {
  return new URLSearchParams(search || "").get(name) ?? "";
}

export function initialQueryFromUrl(search = globalThis.location?.search ?? "") {
  return queryParam("q", search).trim();
}

export function initialModeFromUrl(search = globalThis.location?.search ?? "", fallback = "core") {
  return normalizeLookupMode(queryParam("scope", search) || queryParam("mode", search), fallback);
}

export function joinUrlPath(base, ...segments) {
  const trimmedBase = String(base ?? "").replace(/\/+$/g, "");
  const path = segments
    .map(segment => String(segment ?? "").trim().replace(/^\/+|\/+$/g, ""))
    .filter(Boolean)
    .join("/");
  return path ? `${trimmedBase}/${path}` : trimmedBase;
}

export function sourceHref(dict, line, hrefBase = CSL_ORIG_GITHUB_BASE) {
  const sourceMode = dict?.sourceLinkMode ?? (dict?.inGithub === false ? "local-only" : "github");
  if (!dict?.code || !line || sourceMode !== "github") return null;
  return `${joinUrlPath(hrefBase, dict.code, `${dict.code}.txt`)}#L${line}`;
}

export function shardIdForLemma(lemma, loaders) {
  const first = String(lemma ?? "")[0];
  if (!first) return "other";
  const id = first.charCodeAt(0).toString(16);
  return loaders.has(id) ? id : "other";
}

export function lowerBoundLemma(entries, lemma) {
  let lo = 0, hi = entries.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (entries[mid][0] < lemma) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}

export function findLemma(entries, lemma) {
  const i = lowerBoundLemma(entries, lemma);
  return entries[i]?.[0] === lemma ? entries[i] : null;
}

export function findPrefix(entries, prefix, limit = 80) {
  const out = [];
  for (let i = lowerBoundLemma(entries, prefix); i < entries.length && out.length < limit; i++) {
    const entry = entries[i];
    if (!entry[0].startsWith(prefix)) break;
    out.push(entry);
  }
  return out;
}

export async function loadCandidateShards(candidates, loaders) {
  const shardIds = [...new Set(candidates.filter(candidate => candidate.length >= 1).map(candidate => shardIdForLemma(candidate, loaders)))];
  const shards = shardIds.length
    ? await Promise.all(shardIds.map(id => loaders.get(id)?.()).filter(Boolean))
    : [];
  return new Map(shards.map(shard => [shard.shard, shard.entries]));
}
