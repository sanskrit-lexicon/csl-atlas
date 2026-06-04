const SLP1_ACCENTS = /[\/\\^~]/g;
const IAST_MARKS = /[āīūṛṝḷḹṅñṭḍṇśṣṃṁḥĀĪŪṚṜḶḸṄÑṬḌṆŚṢṂṀḤ]/;

const IAST_TO_SLP1 = [
  ["kh", "K"],
  ["gh", "G"],
  ["ch", "C"],
  ["jh", "J"],
  ["ṭh", "W"],
  ["ḍh", "Q"],
  ["th", "T"],
  ["dh", "D"],
  ["ph", "P"],
  ["bh", "B"],
  ["ai", "E"],
  ["au", "O"],
  ["ā", "A"],
  ["ī", "I"],
  ["ū", "U"],
  ["ṛ", "f"],
  ["ṝ", "F"],
  ["ḷ", "x"],
  ["ḹ", "X"],
  ["ṅ", "N"],
  ["ñ", "Y"],
  ["ṭ", "w"],
  ["ḍ", "q"],
  ["ṇ", "R"],
  ["ś", "S"],
  ["ṣ", "z"],
  ["ṃ", "M"],
  ["ṁ", "M"],
  ["ḥ", "H"]
];

export function normalizeSlp1Lemma(value) {
  const raw = (value ?? "").trim();
  let normalized = raw.replace(SLP1_ACCENTS, "");
  normalized = normalized.replace(/\d+$/, "");
  normalized = normalized.replace(/\s+/g, " ").trim();
  return { normalized, changed: normalized !== raw };
}

export function iastToSlp1(value) {
  let out = (value ?? "").normalize("NFC").trim().toLowerCase();
  for (const [from, to] of IAST_TO_SLP1) out = out.replaceAll(from, to);
  return out;
}

export function normalizeLookupQuery(value) {
  const raw = (value ?? "").trim();
  const hasIast = IAST_MARKS.test(raw);
  const primary = hasIast ? iastToSlp1(raw) : raw;
  const normalized = normalizeSlp1Lemma(primary).normalized;
  const candidates = new Set();
  if (normalized) candidates.add(normalized);

  if (!hasIast && /^[a-z][a-z-]*$/.test(raw)) {
    const asciiIast = normalizeSlp1Lemma(iastToSlp1(raw)).normalized;
    if (asciiIast) candidates.add(asciiIast);
  }

  // A reader may type an IAST-looking ASCII word with an initial capital.
  // Preserve SLP1 as the primary candidate, but try the lower-case form too.
  if (!hasIast && /^[A-Z][a-z][A-Za-z-]*$/.test(raw)) {
    const lower = normalizeSlp1Lemma(raw.toLowerCase()).normalized;
    if (lower) candidates.add(lower);
    const lowerIast = normalizeSlp1Lemma(iastToSlp1(raw.toLowerCase())).normalized;
    if (lowerIast) candidates.add(lowerIast);
  }

  return {
    raw,
    normalized,
    candidates: [...candidates],
    inputScheme: hasIast ? "iast" : "slp1"
  };
}
