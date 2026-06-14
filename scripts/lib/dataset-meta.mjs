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
