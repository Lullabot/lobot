#!/usr/bin/env python3
"""Validate a Project Brain risk tracker (docs/risks.yaml).

Usage: python3 validate.py [path/to/risks.yaml]

Checks each entry: ID (R-###, unique, in order), required fields, a short
one-line risk summary, scope, severity (High | Medium | Low | TBD), status
(Open | Monitoring | Closed), and dated updates. Warns about open risks still
at TBD severity.
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
DEFAULT_PATH = "docs/risks.yaml"
EXAMPLE_ID = "R-001"
REQUIRED = ["risk", "scope", "severity", "status", "source", "confirmed_by"]
ALLOWED = set(REQUIRED) | {"description", "raised", "next_step", "updates"}
TEXT_FIELDS = ["risk", "description", "source", "confirmed_by", "next_step"]
RISK_MAX = 80
SEVERITIES = ("High", "Medium", "Low", "TBD")
STATUSES = ("Open", "Monitoring", "Closed")

import datetime
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader that errors on duplicate mapping keys instead of overwriting."""


def _construct_mapping(loader, node, deep=False):
    seen = set()
    for key_node, _ in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in seen:
            raise yaml.constructor.ConstructorError(
                None, None, f"duplicate key: {key!r}", key_node.start_mark)
        seen.add(key)
    return loader.construct_mapping(node, deep)


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)

SCOPE_RE = re.compile(r"^(all|[a-z0-9]+(-[a-z0-9]+)*)$")


def as_date(value):
    """A YAML date, or an ISO date string; None otherwise."""
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value))
    except ValueError:
        return None


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.load(f, Loader=UniqueKeyLoader), None
    except OSError as e:
        return None, str(e)
    except yaml.YAMLError as e:
        return None, f"does not parse: {e}"


def check_common(key, entry, errors, warnings):
    """Checks shared by every record: allowed fields, required fields, scope, text fields."""
    where = f"[{key}]"
    if not isinstance(entry, dict):
        errors.append(f"{where} must be a mapping of fields")
        return False
    for field in REQUIRED:
        if entry.get(field) in (None, ""):
            errors.append(f"{where} missing '{field}'")
    for field in entry:
        if field not in ALLOWED:
            errors.append(f"{where} unknown field '{field}' (allowed: {', '.join(sorted(ALLOWED))})")
    if "scope" in entry and not SCOPE_RE.match(str(entry["scope"])):
        errors.append(f"{where} scope must be 'all' or a lowercase scope key")
    for field in TEXT_FIELDS:
        if field in entry and not isinstance(entry[field], str):
            errors.append(f"{where} '{field}' must be text (quote it)")
    return True


def run(path):
    data, problem = load(path)
    if problem:
        print(f"ERROR: {path} {problem}")
        return 1
    if data is None:
        print("OK: file is empty (no entries yet).")
        return 0
    if not isinstance(data, dict):
        print(f"ERROR: {path} must be a mapping of IDs to entries")
        return 1
    errors, warnings = [], []
    keys = list(data)
    nums = []
    for key in keys:
        m = KEY_RE.match(str(key))
        if not m:
            errors.append(f"[{key}] ID must look like {EXAMPLE_ID}")
        else:
            nums.append(int(m.group(1)))
        if check_common(key, data[key], errors, warnings):
            check_entry(key, data[key], errors, warnings)
    if nums != sorted(nums):
        warnings.append("entries are not ordered by ID")
    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    print(f"OK: {summary(data)}, {len(warnings)} warning(s).")
    return 0


KEY_RE = re.compile(r"^R-(\d{3,})$")


def check_entry(key, r, errors, warnings):
    where = f"[{key}]"
    risk = r.get("risk")
    if isinstance(risk, str) and (len(risk) > RISK_MAX or "\n" in risk):
        errors.append(f"{where} risk must be a one-line summary of at most {RISK_MAX} characters; put the detail in 'description' (the Lobot migrate step does this for older entries)")
    if r.get("severity") not in SEVERITIES:
        errors.append(f"{where} severity must be one of: {', '.join(SEVERITIES)}")
    if r.get("status") not in STATUSES:
        errors.append(f"{where} status must be one of: {', '.join(STATUSES)}")
    if "raised" in r and not as_date(r["raised"]):
        errors.append(f"{where} raised must be a date (YYYY-MM-DD)")
    if r.get("status") != "Closed" and r.get("severity") == "TBD":
        warnings.append(f"{where} open risk with severity TBD: ask the PM")
    if r.get("status") != "Closed" and not r.get("next_step"):
        warnings.append(f"{where} open risk with no next step")
    updates = r.get("updates", [])
    if not isinstance(updates, list):
        errors.append(f"{where} updates must be a list")
        return
    last = None
    for i, u in enumerate(updates, 1):
        if not isinstance(u, dict) or not u.get("note") or not isinstance(u.get("note"), str):
            errors.append(f"{where} update {i} needs a 'note' (quoted text)")
            continue
        extra = set(u) - {"date", "note", "source"}
        if extra:
            errors.append(f"{where} update {i} has unknown fields: {', '.join(sorted(extra))}")
        d = as_date(u.get("date"))
        if not d:
            errors.append(f"{where} update {i} needs a date (YYYY-MM-DD)")
        elif last and d < last:
            warnings.append(f"{where} updates are not in date order")
        last = d or last


def summary(data):
    open_n = sum(1 for r in data.values() if isinstance(r, dict) and r.get("status") != "Closed")
    return f"{len(data)} risks, {open_n} open"


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH))
