# H6411 — ABCH f-series rework after verifier round 2 (H5325 FAIL)

H5325's ABCH record mis-mapped the f-series. Verifier round 2 (session 0G4, DeepSeek,
25-09-2026) read all 14 f-pages and found the front matter belonged to other pages; H6411
(10-10-2026) re-read the key pages live and corrected the record:

- `abch.fm.title-sa` moves f02 -> f03 (f02 is the registration notice, read live:
  "Registered according to act XXV of 1867"; "All rights reserved by the publisher.").
- The four-page `prastavana` preface never existed: f03 is the Devanagari title, f04 a
  blank leaf (now `excludedScans`), f05-f06 the introduction's pages 1-2. The component is
  deleted.
- `abch.fm.introduction` moves f07-f11 (5 pp., "unnumbered") -> f05-f10, six pages: the
  first unnumbered, then printed 2-6 (number bands read on f06 = 2, f10 = 6, f12 = 2);
  f10 carries the works list (8. Abhidhanacintamanisilonchhah, 9. Linganusasanam) and
  closes with the editors' signature "Pandit-Sivadatta-Kasinathah".
- f11 re-homed as printed page 1 of the kosa (division title + opening verses 1-3) in
  `excludedScans`; the false `knownGaps` entry "printed page 1 in neither series" is
  removed - printed pages 1-4 sit in the f series (f11-f14), the numbered series runs
  pg05-pg58 = printed 5-58.
- Colophon notes re-checked on the scans: pg57's head reads "6 Samanyakandah" (the kanda
  OPENS at printed 57) and pg58's foot closes the work ("...samaptah || 6 ||") with the
  final verses to 9542 - H5325's "5 Samanyakandah", "colophon closes the kanda at printed
  page 57" and "verses to 1542" were all misreadings (the 1542 drops the leading 9).
- New component `abch.fm.registration` (f02); inventory captions f02-f11 and the guide's
  ABCH row rewritten; the guide's "15 scan sets" count corrected to 13 (3 pilot + 10 new).

Validation unchanged: `validate-megastructure` -> OK - 9 dictionaries, 91 components
(5 ABCH parts: title-en, registration, title-sa, introduction, colophon);
`node --test test/megastructure.test.mjs` -> 9/9.
