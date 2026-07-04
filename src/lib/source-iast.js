// CDSL raw source line → readable IAST — now owned by the shared toolkit.
//
// The implementation was upstreamed into sanskrit-util (v0.4.0) as
// source_line_to_iast / source_text_to_iast so every CDSL reader/frontend
// renders source entries the same way. This module is a thin, camelCase-named
// re-export over the vendored copy, kept so existing page imports stay stable.
// Do not re-implement the markup rules here — change them in sanskrit-util.

export {
  source_line_to_iast as sourceLineToIast,
  source_text_to_iast as sourceTextToIast
} from "./sanskrit-util.js";
