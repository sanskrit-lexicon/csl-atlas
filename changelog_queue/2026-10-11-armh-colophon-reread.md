# ARMH colophon re-read (H5325 record, adversarial pass 11-10-2026)

The H5325 ARMH record mistranscribed two akṣaras of the closing colophon on
printed page 101 (`ARMH_0101.pdf`). A fresh 400 dpi render of a newly fetched
byte-identical PDF shows:

- `भट्ट` for `भद्र` — the author is styled Bhaṭṭa ("Śrī Bhaṭṭa Halāyudha");
- `[अ]नेकार्थ` for `मनोहरा` — e-kāra not o-kāra, क not ह: the kośa-final
  homonym section, not a proper name. The initial अ is faint on the scan;
  the reading is fixed by the unambiguous `नेकार्थ` and the genre.

`armh.bm.colophon` now reads
"इति श्रीभट्टहलायुधकृतायामभिधानरत्नमालायां [अ]नेकार्थकाण्डे पञ्चमं समाप्तम् ॥ ५ ॥"
("Thus ends the fifth, the Anekārtha-kāṇḍa, in the Abhidhānaratnamālā composed
by Śrī Bhaṭṭa Halāyudha"), and the catalogue notes' "fifth, manohara-kāṇḍa"
becomes "fifth, anekārtha-kāṇḍa". Same pass re-derived the ABCH f12-f14 =
printed 2-4 mapping from verse continuity (4-9, 10-15, 16-23, then 24+ on
printed 5) and re-confirmed AP90 `tit_0012` as a blank leaf — all consistent
with the H6411 rework; no ABCH/AP90 record changes.

Validation unchanged: `validate-megastructure` -> OK - 9 dictionaries,
91 components; `node --test test/megastructure.test.mjs` -> 9/9.
