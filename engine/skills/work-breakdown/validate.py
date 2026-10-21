#!/usr/bin/env python3
"""Validate the work breakdown: every area file under docs/work/ (not index.md).

Usage: python3 .ai/general/skills/work-breakdown/validate.py [docs/work]
"""
import pathlib
import re
import sys

STATUSES = ["idea", "draft", "ready", "ticketed"]
ITEM = re.compile(r"^### (W-\d{3,}): (.+)$")
META = re.compile(r"^`(.+)`$")


def main():
    if len(sys.argv) > 1:
        work = pathlib.Path(sys.argv[1])
    else:
        work = pathlib.Path(__file__).resolve().parents[4] / "docs" / "work"
    if not work.exists():
        print("OK: no docs/work yet.")
        return 0

    errors, items = [], {}
    for md in sorted(work.rglob("*.md")):
        if md.name == "index.md":
            continue
        lines = md.read_text().splitlines()
        for i, line in enumerate(lines):
            m = ITEM.match(line)
            if not m:
                continue
            wid = m.group(1)
            where = f"{md.relative_to(work.parent)}"
            if wid in items:
                errors.append(f"[{wid}] {where}: duplicate ID (also in {items[wid]['file']})")
            meta = {}
            nxt = next((l.strip() for l in lines[i + 1:] if l.strip()), "")
            mm = META.match(nxt)
            if not mm:
                errors.append(f"[{wid}] {where}: missing meta line after the heading")
            else:
                for part in mm.group(1).split("·"):
                    if ":" in part:
                        k, v = part.split(":", 1)
                        meta[k.strip()] = v.strip()
            status = meta.get("status")
            if status not in STATUSES:
                errors.append(f"[{wid}] {where}: status '{status}' is not one of {', '.join(STATUSES)}")
            if not meta.get("scope"):
                errors.append(f"[{wid}] {where}: no scope in the meta line")
            end = next((j for j in range(i + 1, len(lines))
                        if ITEM.match(lines[j]) or lines[j].startswith("## ")), len(lines))
            body = "\n".join(lines[i:end])
            if "**Sources.**" not in body:
                errors.append(f"[{wid}] {where}: no Sources")
            if status == "ticketed" and not re.search(r"\*\*Tickets\.\*\*[ \t]*\S", body):
                errors.append(f"[{wid}] {where}: ticketed but no ticket keys")
            items[wid] = {"file": where, "status": status}

    for e in errors:
        print("ERROR:", e)
    counts = ", ".join(f"{sum(1 for v in items.values() if v['status'] == s)} {s}"
                       for s in STATUSES if any(v["status"] == s for v in items.values()))
    if errors:
        print(f"{len(errors)} error(s).")
        return 1
    print(f"OK: {len(items)} items ({counts or 'none'}), 0 error(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
