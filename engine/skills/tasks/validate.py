#!/usr/bin/env python3
"""Validate a Project Brain task list (docs/tasks.md).

Usage: python3 validate.py [path/to/tasks.md]

Checks the frontmatter and the tasks table: IDs (T-###, unique), owner,
scope, due date, status (open | waiting | done | dropped), and source.
Open and waiting rows should come before done and dropped ones.
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
import datetime
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

HEADER = ["ID", "Task", "Owner", "Scope", "Due", "Status", "Source", "Link"]
ID_RE = re.compile(r"^T-\d{3,}$")
SCOPE_RE = re.compile(r"^(all|[a-z0-9]+(-[a-z0-9]+)*)$")
ACTIVE = ("open", "waiting")
CLOSED = ("done", "dropped")


def cells(line):
    line = line.strip()
    if not (line.startswith("|") and line.endswith("|")):
        return None
    return [c.strip() for c in line[1:-1].split("|")]


def is_date(value):
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def main(path):
    errors, warnings = [], []
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"ERROR: {e}")
        return 1
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append("missing frontmatter (title, status, updated)")
        body = text
    else:
        body = text[m.end():]
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError as e:
            fm = {}
            errors.append(f"frontmatter does not parse: {e}")
        for field in ("title", "status", "updated"):
            if field not in fm:
                errors.append(f"frontmatter missing '{field}'")
        if "updated" in fm and not is_date(str(fm["updated"])):
            errors.append("frontmatter 'updated' must be a date (YYYY-MM-DD)")

    lines = body.splitlines()
    start = next((i for i, l in enumerate(lines) if cells(l) == HEADER), None)
    rows = []
    if start is None:
        errors.append("no tasks table with header: | " + " | ".join(HEADER) + " |")
    else:
        for n, line in enumerate(lines[start + 2:], start + 3):
            c = cells(line)
            if c is None:
                break
            rows.append((n, c))

    seen, closed_seen, active = set(), False, 0
    today = datetime.date.today()
    overdue = 0
    for n, c in rows:
        where = f"[row {c[0] if c else '?'}]"
        if len(c) != len(HEADER):
            errors.append(f"{where} has {len(c)} cells, expected {len(HEADER)} (a '|' inside a cell breaks the table)")
            continue
        tid, task, owner, scope, due, status, source, link = c
        if not ID_RE.match(tid):
            errors.append(f"{where} ID must look like T-001")
        elif tid in seen:
            errors.append(f"{where} duplicate ID")
        seen.add(tid)
        if not task:
            errors.append(f"{where} task is empty")
        if not owner:
            errors.append(f"{where} owner is empty (use a name, a team, or 'tbd')")
        if not SCOPE_RE.match(scope):
            errors.append(f"{where} scope must be 'all' or a lowercase scope key")
        if due and not is_date(due):
            errors.append(f"{where} due must be a date (YYYY-MM-DD) or blank")
        if not source:
            warnings.append(f"{where} no source: say where the action item came from")
        if link and not link.startswith("http"):
            warnings.append(f"{where} link should be a URL")
        if status in ACTIVE:
            active += 1
            if closed_seen:
                warnings.append(f"{where} {status} row listed after a closed one (open and waiting first)")
            if due and is_date(due) and datetime.date.fromisoformat(due) < today:
                overdue += 1
        elif status in CLOSED:
            closed_seen = True
        else:
            errors.append(f"{where} status must be one of: {', '.join(ACTIVE + CLOSED)}")

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"{len(errors)} error(s) in {path}")
        return 1
    print(f"OK: {len(rows)} tasks, {active} open or waiting, {overdue} overdue, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs/tasks.md"))
