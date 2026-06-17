// sanskrit_util — shared Sanskrit string helpers for the CDSL / Sanskrit-Lexicon repos.
//
// Behaviour-identical port of py/sanskrit_util/__init__.py (proved by ../vectors/vectors.json).
// Consolidated from WhitneyRoots reader.js (deva2iast/norm/nfold), linguistics.js
// (normalizeSanskrit/iastToDevanagari) and scripts/sanskrit_util.py (to_slp1/from_slp1/
// to_roman/form_key). See README for which key to use when.

// ---- IAST -> SLP1 (longest-key-first; aspirates + diphthongs are digraphs) ----
const SLP1 = {
  ai: 'E', au: 'O', kh: 'K', gh: 'G', ch: 'C', jh: 'J', 'ṭh': 'W', 'ḍh': 'Q',
  th: 'T', dh: 'D', ph: 'P', bh: 'B',
  'ā': 'A', 'ī': 'I', 'ū': 'U', 'ṛ': 'f', 'ṝ': 'F', 'ḷ': 'x', 'ḹ': 'X',
  'ṃ': 'M', 'ṁ': 'M', 'ḥ': 'H', 'ṅ': 'N', 'ñ': 'Y', 'ṭ': 'w', 'ḍ': 'q', 'ṇ': 'R',
  'ś': 'S', 'ṣ': 'z', 'ḻ': 'L',
  a: 'a', i: 'i', u: 'u', e: 'e', o: 'o', k: 'k', g: 'g', c: 'c', j: 'j',
  t: 't', d: 'd', n: 'n', p: 'p', b: 'b', m: 'm', y: 'y', r: 'r', l: 'l',
  v: 'v', s: 's', h: 'h',
};

export function to_slp1(iast) {
  const s = iast || '';
  let out = '', i = 0;
  while (i < s.length) {
    const two = s.slice(i, i + 2);
    if (SLP1[two] !== undefined) { out += SLP1[two]; i += 2; continue; }
    const one = s[i];
    out += (SLP1[one] !== undefined ? SLP1[one] : one); i += 1;
  }
  return out;
}

const ROMAN = { 1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V', 6: 'VI', 7: 'VII', 8: 'VIII', 9: 'IX', 10: 'X' };

export function to_roman(nums) {
  return (nums || []).filter((n) => ROMAN[n] !== undefined).map((n) => ROMAN[n]);
}

// ---- SLP1 -> IAST ----
const FROM_SLP1 = {
  A: 'ā', I: 'ī', U: 'ū', f: 'ṛ', F: 'ṝ', x: 'ḷ', X: 'ḹ',
  E: 'ai', O: 'au', M: 'ṃ', H: 'ḥ',
  K: 'kh', G: 'gh', N: 'ṅ', C: 'ch', J: 'jh', Y: 'ñ',
  w: 'ṭ', W: 'ṭh', q: 'ḍ', Q: 'ḍh', R: 'ṇ',
  T: 'th', D: 'dh', P: 'ph', B: 'bh',
  S: 'ś', z: 'ṣ', L: 'ḻ',
};

export function from_slp1(slp1) {
  let out = '';
  for (const ch of (slp1 || '')) out += (FROM_SLP1[ch] !== undefined ? FROM_SLP1[ch] : ch);
  return out;
}

// ---- Devanāgarī -> IAST (inherent-'a' + virāma aware) ----
const DV_VOWEL = { 'अ': 'a', 'आ': 'ā', 'इ': 'i', 'ई': 'ī', 'उ': 'u', 'ऊ': 'ū', 'ऋ': 'ṛ', 'ॠ': 'ṝ', 'ऌ': 'ḷ', 'ॡ': 'ḹ', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au' };
const DV_MATRA = { 'ा': 'ā', 'ि': 'i', 'ी': 'ī', 'ु': 'u', 'ू': 'ū', 'ृ': 'ṛ', 'ॄ': 'ṝ', 'ॢ': 'ḷ', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au' };
const DV_CONS = { 'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ṅ', 'च': 'c', 'छ': 'ch', 'ज': 'j', 'झ': 'jh', 'ञ': 'ñ', 'ट': 'ṭ', 'ठ': 'ṭh', 'ड': 'ḍ', 'ढ': 'ḍh', 'ण': 'ṇ', 'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n', 'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm', 'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'ś', 'ष': 'ṣ', 'स': 's', 'ह': 'h', 'ळ': 'ḷ' };
const DV_MARK = { 'ं': 'ṃ', 'ः': 'ḥ', 'ँ': 'ṃ' };
const VIRAMA = '्';

export function deva_to_iast(s) {
  s = s || '';
  let out = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (DV_CONS[ch] != null) {
      out += DV_CONS[ch];
      const nx = s[i + 1];
      if (nx === VIRAMA) { i++; }
      else if (DV_MATRA[nx] != null) { out += DV_MATRA[nx]; i++; }
      else { out += 'a'; }
    } else if (DV_VOWEL[ch] != null) { out += DV_VOWEL[ch]; }
    else if (DV_MARK[ch] != null) { out += DV_MARK[ch]; }
    else if (ch === 'ऽ') { /* avagraha — drop */ }
    else { out += ch; }
  }
  return out;
}

// ---- IAST -> Devanāgarī (approximate display transcode) ----
const IAST_TO_DEVA = {
  a: 'अ', 'ā': 'आ', i: 'इ', 'ī': 'ई', u: 'उ', 'ū': 'ऊ', 'ṛ': 'ऋ', 'ṝ': 'ॠ', 'ḷ': 'ऌ', 'ḹ': 'ॡ',
  e: 'ए', ai: 'ऐ', o: 'ओ', au: 'औ', 'ṃ': 'ं', 'ḥ': 'ः',
  k: 'क', kh: 'ख', g: 'ग', gh: 'घ', 'ṅ': 'ङ',
  c: 'च', ch: 'छ', j: 'ज', jh: 'झ', 'ñ': 'ञ',
  'ṭ': 'ट', 'ṭh': 'ठ', 'ḍ': 'ड', 'ḍh': 'ढ', 'ṇ': 'ण',
  t: 'त', th: 'थ', d: 'द', dh: 'ध', n: 'न',
  p: 'प', ph: 'फ', b: 'ब', bh: 'भ', m: 'म',
  y: 'य', r: 'र', l: 'ल', v: 'व',
  'ś': 'श', 'ṣ': 'ष', s: 'स', h: 'ह',
};
const IAST_TO_DEVA_KEYS = Object.keys(IAST_TO_DEVA).sort((a, b) => b.length - a.length);

export function iast_to_devanagari(text) {
  let result = (text || '').toLowerCase();
  for (const key of IAST_TO_DEVA_KEYS) {
    result = result.split(key).join(IAST_TO_DEVA[key]);
  }
  return result;
}

// ---- normalization keys ----
const DEVA_RE = /[ऀ-ॿ]/;

// Whitespace pinned to match the Python port's _WS_CHARS exactly. JS String.trim()/\s strip the
// BOM/ZWNBSP U+FEFF (which sneaks in when a file is read without a BOM-aware decoder) while Python
// str.strip()/\s do not (and conversely Python strips U+0085 NEL) — list the class explicitly so
// norm()/form_key()/slp1_norm() yield identical keys in both languages.
const WS = '\\t\\n\\x0b\\f\\r \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000\\ufeff';
const WS_TRIM_RE = new RegExp('^[' + WS + ']+|[' + WS + ']+$', 'g');
const WS_RUN_RE = new RegExp('[' + WS + ']+', 'g');
const wstrim = (s) => s.replace(WS_TRIM_RE, '');

export function norm(s) {
  s = s || '';
  if (DEVA_RE.test(s)) s = deva_to_iast(s);
  return wstrim(s.normalize('NFD').replace(/\p{Mn}/gu, '').normalize('NFC').toLowerCase());
}

export function nfold(s) {
  return norm(s).replace(/[mn]/g, 'n');
}

// ---- length-preserving comparison key ----
const FK_ACCENT = new Set(['́', '̀', '॑', '॒']); // acute, grave, Vedic svarita/anudātta
const FK_VOWELS = new Set([...'aāiīuūṛṝḷḹeēoō']);
const COMBINING_RE = /\p{Mn}/u;

export function form_key(s) {
  s = wstrim(s || '').toLowerCase();
  if (s === '-' || s === '–' || s === '—') return '';
  s = s.replace(/ḥ$/, '');
  s = s.replace(/[ṃṁṅñṇ]/g, 'n');
  const out = [];
  for (const ch of s.normalize('NFD')) {
    if (FK_ACCENT.has(ch)) {
      let j = out.length - 1;
      while (j >= 0 && COMBINING_RE.test(out[j])) j -= 1;
      const base = j >= 0 ? out.slice(j).join('').normalize('NFC') : '';
      if (FK_VOWELS.has(base)) continue;
    }
    out.push(ch);
  }
  return out.join('').normalize('NFC');
}

// ---- lossy ASCII-folding search key (v3-explorer normalizeSanskrit) ----
const NS_MAP = {
  'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṛ': 'r', 'ṝ': 'r', 'ḷ': 'l', 'ḹ': 'l',
  'ṅ': 'n', 'ñ': 'n', 'ṭ': 't', 'ḍ': 'd', 'ṇ': 'n', 'ś': 's', 'ṣ': 's',
  'ḥ': 'h', 'ṃ': 'm',
};

export function normalize_sanskrit(text) {
  if (!text) return '';
  return text.normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[āīūṛṝḷḹṅñṭḍṇśṣḥṃ]/g, (m) => NS_MAP[m] || m)
    .toLowerCase();
}

// ---- SLP1-side API ----
// The CDSL dictionaries store headwords in SLP1, where case is PHONEMIC (S=ś≠s) — so the
// IAST helpers above can't key them without a transcode, and every CDSL repo re-rolled its own
// SLP1 alphabet + headword normalizer. Behaviour-identical port of the Python additions.
export const SLP1_VOWELS = 'aAiIuUfFxXeEoO';                          // f/F=ṛ/ṝ, x/X=ḷ/ḹ, E=ai, O=au
export const SLP1_MARKS = 'MH~';                                     // anusvāra, visarga, candrabindu
export const SLP1_CONSONANTS = 'kKgGNcCjJYwWqQRtTdDnpPbBmyrlvSzshL'; // L = Vedic retroflex ḻa
export const SLP1_ALPHABET = SLP1_VOWELS + SLP1_MARKS + SLP1_CONSONANTS; // valid SLP1 letters (no avagraha)

const SLP1_ACCENTS_RE = /[/\\^~]/g; // udātta / anudātta / svarita / candrabindu

export function strip_slp1_accents(slp1) {
  return (slp1 ?? '').replace(SLP1_ACCENTS_RE, '');
}

export function slp1_norm(slp1) {
  let s = strip_slp1_accents(slp1 ?? '');
  s = s.replace(/\d+$/, '');
  return wstrim(s.replace(WS_RUN_RE, ' '));
}

export function slp1_form_key(slp1) {
  return form_key(from_slp1(strip_slp1_accents(slp1 ?? '')));
}

export default {
  to_slp1, from_slp1, to_roman, deva_to_iast, iast_to_devanagari,
  norm, nfold, form_key, normalize_sanskrit,
  SLP1_VOWELS, SLP1_MARKS, SLP1_CONSONANTS, SLP1_ALPHABET,
  strip_slp1_accents, slp1_norm, slp1_form_key,
};
