#!/usr/bin/env python3
"""Validate a Project Brain questions log (docs/questions.yaml).

Usage: python3 validate.py [path/to/questions.yaml]

Checks each entry: ID (Q-###, unique, in order), required fields, scope,
raised date, status (open | answered), that answered questions have an answer,
and about (project | product; project when left out).
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
DEFAULT_PATH = "docs/questions.yaml"
EXAMPLE_ID = "Q-001"
REQUIRED = ["question", "scope", "raised", "source", "status"]
ALLOWED = set(REQUIRED) | {"answer", "about", "ask", "link"}
TEXT_FIELDS = ["question", "source", "answer", "ask", "link"]
STATUSES = ("open", "answered")
ABOUT = ("project", "product")

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


KEY_RE = re.compile(r"^Q-(\d{3,})$")


def check_entry(key, q, errors, warnings):
    where = f"[{key}]"
    if "raised" in q and not as_date(q["raised"]):
        errors.append(f"{where} raised must be a date (YYYY-MM-DD)")
    if q.get("status") not in STATUSES:
        errors.append(f"{where} status must be one of: {', '.join(STATUSES)}")
    elif q["status"] == "answered" and not q.get("answer"):
        errors.append(f"{where} answered but the answer is empty")
    if "about" in q and q["about"] not in ABOUT:
        errors.append(f"{where} about must be one of: {', '.join(ABOUT)}")
    if q.get("about") != "product":
        for field in ("ask", "link"):
            if field in q:
                warnings.append(f"{where} '{field}' is only used on product questions (about: product)")


def summary(data):
    open_q = [q for q in data.values() if isinstance(q, dict) and q.get("status") == "open"]
    product = sum(1 for q in open_q if q.get("about") == "product")
    return f"{len(data)} questions, {len(open_q)} open ({len(open_q) - product} project, {product} product)"


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH))
