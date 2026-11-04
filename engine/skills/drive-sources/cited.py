#!/usr/bin/env python3
"""List what the Project Brain built from Drive files: run it for each file the
check reports as changed, so the facts drawn from the earlier version get rechecked.

Usage (from the Project Brain root):
  python3 .ai/general/skills/drive-sources/cited.py ID_OR_URL [ID_OR_URL ...]

For each file it lists:
- Built from it: the `result` of each of its entries in docs/sources.yaml
  `processed` (skipped entries are left out).
- Cited in the dossier: every docs/overview/ file whose `sources` frontmatter
  points at it, by its Drive ID or URL, by one of those results, or by a local
  file whose frontmatter `drive_id` is the file (a snapshot or cleaned
  transcript), with the label and the lines that cite that label.

Exit code 0 = listed (possibly nothing), 1 = usage or data error.
"""
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

SOURCES = "docs/sources.yaml"
OVERVIEW = "docs/overview"
ID_RE = re.compile(r"(?:/d/|/folders/|[?&]id=)([A-Za-z0-9_-]{10,})")
BARE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,}$")
UNREADABLE = []  # files whose frontmatter doesn't parse, so their citations can't be checked


def file_id(arg):
    m = ID_RE.search(arg)
    if m:
        return m.group(1)
    if BARE_ID_RE.match(arg):
        return arg
    sys.exit(f"ERROR: {arg!r} is not a Drive file ID or URL")


def frontmatter(path):
    """(frontmatter map or None, body, line number the body starts on)."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return None, "", 1
    if not text.startswith("---\n"):
        return None, text, 1
    end = text.find("\n---", 4)
    if end == -1:
        return None, text, 1
    try:
        meta = yaml.safe_load(text[4:end])
    except yaml.YAMLError:
        if path not in UNREADABLE:
            UNREADABLE.append(path)
        return None, text, 1
    return (meta if isinstance(meta, dict) else None), text[end + 4:], text[:end + 4].count("\n") + 1


def norm(path):
    return os.path.normpath(str(path).strip()) if path else ""


def entries_for(fid, processed):
    return [p for p in processed if isinstance(p, dict) and str(p.get("id", "")) == fid]


def built_from(entries):
    out = []
    for p in entries:
        result = str(p.get("result", ""))
        if result and not result.startswith("skipped"):
            out.append((norm(result), p.get("processed"), p.get("modified")))
    return out


def snapshot_id(value, cache):
    """drive_id from a local file's frontmatter, for sources that cite a snapshot."""
    path = norm(value)
    if "://" in str(value) or not path.endswith(".md") or not os.path.isfile(path):
        return None
    if path not in cache:
        meta, _, _ = frontmatter(path)
        cache[path] = str(meta.get("drive_id", "")) if meta else ""
    return cache[path]


def dossier_citations(fid, results, cache):
    has_id = re.compile(r"(?<![A-Za-z0-9_-])" + re.escape(fid) + r"(?![A-Za-z0-9_-])")
    hits = []
    if not os.path.isdir(OVERVIEW):
        return hits
    for dirpath, _, files in sorted(os.walk(OVERVIEW)):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            meta, body, start = frontmatter(path)
            sources = (meta or {}).get("sources")
            if not isinstance(sources, dict):
                continue
            for label, value in sources.items():
                value = str(value or "")
                if not (has_id.search(value) or norm(value) in results or snapshot_id(value, cache) == fid):
                    continue
                # The label as a whole token at the start of a citation, which may hold several: (a 00:12; b §2)
                cite = re.compile(r"\((?:[^()]*?[;,]\s*)?" + re.escape(str(label)) + r"(?=[\s;,)])")
                lines = [start + i for i, line in enumerate(body.split("\n")) if cite.search(line)]
                hits.append((path, label, lines))
    return hits


def main(args):
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0 if args else 1
    if not os.path.isfile(SOURCES):
        print(f"ERROR: no {SOURCES} here ({os.getcwd()}). Run this from the Project Brain root.")
        return 1
    try:
        with open(SOURCES, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        print(f"ERROR: {SOURCES} does not parse: {e}")
        return 1
    processed = (data.get("processed") or []) if isinstance(data, dict) else []
    cache = {}
    for arg in args:
        fid = file_id(arg)
        entries = entries_for(fid, processed)
        title = entries[-1].get("title") if entries else None
        print(f"{title or fid} ({fid})" + ("" if entries else ": not in processed"))
        built = built_from(entries)
        results = {r for r, _, _ in built}
        if built:
            print("  Built from it:")
            for result, when, modified in built:
                print(f"    {result} (processed {when}, from the version of {modified})")
        hits = dossier_citations(fid, results, cache)
        if hits:
            print("  Cited in the dossier:")
            for path, label, lines in hits:
                facts = f"{len(lines)} fact(s), line(s) {', '.join(map(str, lines))}" if lines else "no facts cite this label"
                print(f"    {path}: source '{label}', {facts}")
        if not built and not hits:
            print("  Nothing in the Project Brain is built from it.")
    for path in UNREADABLE:
        print(f"WARN: {path}: frontmatter does not parse, so its sources weren't checked")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
