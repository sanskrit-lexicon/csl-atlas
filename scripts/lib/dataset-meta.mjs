// Shared dataset provenance metadata.
//
// Single source of truth for the licence every csl-atlas data product declares
// in its envelope (FAIR Reusable). The licence matches the repository LICENSE,
// package.json, and the csl-orig source data (all CC-BY-SA-4.0), so derived
// datasets inherit it cleanly with no per-dataset exception. The envelope
// `license` field maps to `dct:license` in the standards crosswalk
// (csl-standards/docs/EVIDENCE_LABEL_CROSSWALK.md §C).
//
// New builders should spread `licenseFields()` into their envelope right after
// `schemaVersion`.

export const DATASET_LICENSE = "CC-BY-SA-4.0";
export const DATASET_LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/";

/** The licence fields every dataset envelope carries, in canonical order. */
export function licenseFields() {
  return { license: DATASET_LICENSE, licenseUrl: DATASET_LICENSE_URL };
}

export function generatedAtNow() {
  const explicit = process.env.CSL_ATLAS_GENERATED_AT;
  if (explicit) return explicit;
  const sourceDateEpoch = process.env.SOURCE_DATE_EPOCH;
  if (sourceDateEpoch) {
    const seconds = Number(sourceDateEpoch);
    if (Number.isFinite(seconds)) return new Date(seconds * 1000).toISOString();
  }
  return new Date().toISOString();
}

function canonicalWithoutTopLevelGeneratedAt(value, depth = 0) {
  if (!value || typeof value !== "object") return value;
  if (Array.isArray(value)) return value.map(item => canonicalWithoutTopLevelGeneratedAt(item, depth + 1));
  const out = {};
  for (const key of Object.keys(value).filter(key => depth > 0 || key !== "generatedAt").sort()) {
    out[key] = canonicalWithoutTopLevelGeneratedAt(value[key], depth + 1);
  }
  return out;
}

export function generatedAtForPayload(previousPayload, nextPayload) {
  if (
    previousPayload?.generatedAt &&
    JSON.stringify(canonicalWithoutTopLevelGeneratedAt(previousPayload)) ===
      JSON.stringify(canonicalWithoutTopLevelGeneratedAt(nextPayload))
  ) {
    return previousPayload.generatedAt;
  }
  return generatedAtNow();
}

export function readJsonIfExists(filePath, fsModule) {
  if (!fsModule.existsSync(filePath)) return null;
  try {
    return JSON.parse(fsModule.readFileSync(filePath, "utf8"));
  } catch {
    return null;
  }
}
