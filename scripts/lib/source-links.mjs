export const CSL_ORIG_GITHUB_BASE = "https://github.com/sanskrit-lexicon/csl-orig/blob/master/v02";

function cleanSegment(value) {
  return String(value ?? "").trim().replace(/^\/+|\/+$/g, "");
}

export function joinUrlPath(base, ...segments) {
  const trimmedBase = String(base ?? "").replace(/\/+$/g, "");
  const path = segments.map(cleanSegment).filter(Boolean).join("/");
  return path ? `${trimmedBase}/${path}` : trimmedBase;
}

export function dictSourcePath(code) {
  const cleanCode = cleanSegment(code).toLowerCase();
  return `../csl-orig/v02/${cleanCode}/${cleanCode}.txt`;
}

export function dictGithubHref(code, line, hrefBase = CSL_ORIG_GITHUB_BASE) {
  const cleanCode = cleanSegment(code).toLowerCase();
  if (!cleanCode || !line) return null;
  return `${joinUrlPath(hrefBase, cleanCode, `${cleanCode}.txt`)}#L${line}`;
}

export function sourceHrefForDict(dict, line, hrefBase = CSL_ORIG_GITHUB_BASE) {
  const sourceMode = dict?.sourceLinkMode ?? (dict?.inGithub === false ? "local-only" : "github");
  return sourceMode === "github" ? dictGithubHref(dict?.code, line, hrefBase) : null;
}
