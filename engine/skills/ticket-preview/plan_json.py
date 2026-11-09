#!/usr/bin/env python3
"""Turn a ticket plan (tickets skill, "Ticket plans") into the JSON document the ticket preview page shows.

Usage:
  python3 plan_json.py PLAN.yaml [--tracker-url URL] [--repo-url URL] [--name NAME] [-o OUT.json]

Prints a short check of the plan to stderr (duplicate refs, a parent or link that names a ref not in the plan,
an item with neither ref nor key) and writes the document to OUT.json, or stdout. Needs PyYAML.
"""
import argparse, json, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("plan_json.py needs PyYAML (pip install pyyaml), the same as jira.py.")

KEY = re.compile(r"^([A-Z][A-Z0-9]+-\d+|#\d+)$")


def plain(v):
    """YAML dates and other scalars into JSON-safe values."""
    if isinstance(v, dict):
        return {str(k): plain(x) for k, x in v.items()}
    if isinstance(v, list):
        return [plain(x) for x in v]
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    return str(v)


def name_from(path):
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", Path(path).stem)
    return stem.replace("-", " ").strip().capitalize() or Path(path).stem


def check(items):
    problems, ids = [], []
    for n, it in enumerate(items, 1):
        has_ref, has_key = "ref" in it, "key" in it
        if has_ref == has_key:
            problems.append(f"item {n}: needs exactly one of ref or key")
        ids.append(str(it.get("ref") or it.get("key") or ""))
    seen = set()
    for i in ids:
        if i in seen:
            problems.append(f"{i}: used twice")
        seen.add(i)
    known = set(ids)

    def target(owner, t):
        t = str(t)
        if t not in known and not KEY.match(t):
            problems.append(f"{owner}: names {t}, which isn't a ref in this plan or a ticket key")

    for it in items:
        owner = str(it.get("ref") or it.get("key"))
        if it.get("parent"):
            target(owner, it["parent"])
        for k in ("blocked_by", "blocks"):
            v = it.get(k) or []
            for t in v if isinstance(v, list) else [v]:
                target(owner, t)
        for link in it.get("links") or []:
            for v in (link or {}).values():
                for t in v if isinstance(v, list) else [v]:
                    target(owner, t)
    return problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--tracker-url", default="", help="Jira site (https://x.atlassian.net) or GitHub repo URL, for links to existing tickets")
    ap.add_argument("--repo-url", default="", help="the Project Brain repository's file base (https://github.com/OWNER/REPO/blob/main/), so the plan and its sources link to their files")
    ap.add_argument("--name", default="", help="the plan's display name; defaults to its file name without the date")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()

    path = Path(a.plan)
    posix = path.as_posix()
    plan = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    items = plain(plan.get("items") or [])
    problems = check(items)
    doc = {
        "file": ("docs/" + posix.split("docs/", 1)[1]) if "docs/" in posix else path.name,
        "repoUrl": a.repo_url,
        "name": a.name or name_from(path),
        "destination": plan.get("destination", ""),
        "status": plan.get("status", "draft"),
        "approved_by": plan.get("approved_by", ""),
        "approved_at": str(plan.get("approved_at", "") or ""),
        "tracker": str(plan.get("tracker", "")).lower(),
        "project": plan.get("project", ""),
        "trackerUrl": a.tracker_url,
        "sources": plain(plan.get("sources") or []),
        "items": items,
        "problems": problems,
    }
    text = json.dumps(doc, ensure_ascii=False, indent=1)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
    else:
        print(text)
    new = sum(1 for i in items if "ref" in i)
    print(f"{path.name}: {new} new, {len(items) - new} updates, {len(problems)} problems", file=sys.stderr)
    for p in problems:
        print("  - " + p, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
