"""Python mirror of scripts/lib/dataset-meta.mjs — dataset envelope provenance.

Single source of truth for the licence and the stable-`generatedAt` discipline
(`generatedAtForPayload`) used by every csl-atlas data product, for builders
written in Python. Keep the semantics in lockstep with the .mjs original:
the timestamp is preserved from the previous committed artifact whenever the
payload (minus the top-level `generatedAt`) is byte-identical, so re-runs do
not churn the diff; `CSL_ATLAS_GENERATED_AT` / `SOURCE_DATE_EPOCH` override
the clock for reproducible builds.

Usage:
    sys.path.insert(0, os.path.abspath("scripts/lib"))
    from dataset_meta import license_fields, generated_at_for_payload, read_json_if_exists
"""

import json
import os
from datetime import datetime, timezone

DATASET_LICENSE = "CC-BY-SA-4.0"
DATASET_LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"


def license_fields():
    """The licence fields every dataset envelope carries, in canonical order."""
    return {"license": DATASET_LICENSE, "licenseUrl": DATASET_LICENSE_URL}


def generated_at_now():
    explicit = os.environ.get("CSL_ATLAS_GENERATED_AT")
    if explicit:
        return explicit
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch:
        try:
            seconds = float(source_date_epoch)
        except ValueError:
            seconds = None
        if seconds is not None:
            return _iso(datetime.fromtimestamp(seconds, tz=timezone.utc))
    return _iso(datetime.now(timezone.utc))


def _iso(dt):
    return dt.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _canonical_without_top_level_generated_at(value, depth=0):
    if isinstance(value, list):
        return [_canonical_without_top_level_generated_at(v, depth + 1) for v in value]
    if isinstance(value, dict):
        return {
            key: _canonical_without_top_level_generated_at(value[key], depth + 1)
            for key in sorted(value)
            if depth > 0 or key != "generatedAt"
        }
    return value


def generated_at_for_payload(previous_payload, next_payload):
    if previous_payload and previous_payload.get("generatedAt"):
        prev = json.dumps(_canonical_without_top_level_generated_at(previous_payload),
                          sort_keys=True, ensure_ascii=False)
        nxt = json.dumps(_canonical_without_top_level_generated_at(next_payload),
                         sort_keys=True, ensure_ascii=False)
        if prev == nxt:
            return previous_payload["generatedAt"]
    return generated_at_now()


def read_json_if_exists(file_path):
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None
