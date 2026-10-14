#!/usr/bin/env python3
"""Validate a Project Brain dossier (docs/overview/).

Usage: python3 validate.py [path/to/docs/overview]

Checks every Markdown file in the dossier:
- frontmatter parses and has title, status, updated (YYYY-MM-DD), and sources
  (a map of label to path or URL; local paths must exist, relative to the
  Project Brain root);
- relative Markdown links resolve;
- every file is linked from the index above it (a site index from the project
  index, a topic file from its folder's index, a reference file from any file
  in the folder above it);
- each site folder has an index.md naming its site and scope, and the scope is
  declared in docs/raci.yaml or docs/sources.yaml when the project declares any.
Exit code 0 = valid (warnings may print), 1 = errors found.
"""
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

REQUIRED = ("title", "status", "updated", "sources")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def frontmatter(text):
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---", 4)
    if end == -1:
        return None, text
    data = yaml.safe_load(text[4:end]) or {}
    return data, text[end + 4:]


def declared_scopes(root):
    scopes = set()
    for name in ("raci.yaml", "sources.yaml"):
        path = os.path.join(root, "docs", name)
        if os.path.exists(path):
            try:
                data = yaml.safe_load(open(path, encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            if isinstance(data, dict) and isinstance(data.get("scopes"), dict):
                scopes |= set(data["scopes"])
    return scopes


def local_links(body, here):
    out = set()
    for target in LINK_RE.findall(body):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        target = target.split("#", 1)[0]
        if target:
            out.add(os.path.normpath(os.path.join(here, target)))
    return out


def main(overview):
    overview = os.path.abspath(overview)
    root = os.path.dirname(os.path.dirname(overview))
    errors, warnings = [], []
    rel = lambda p: os.path.relpath(p, root)
    index = os.path.join(overview, "index.md")
    if not os.path.exists(index):
        print(f"ERROR: {rel(index)} is missing")
        return 1

    files = []
    for dirpath, dirnames, filenames in os.walk(overview):
        dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
        files += [os.path.join(dirpath, f) for f in sorted(filenames) if f.endswith(".md")]

    links_from = {}
    for path in files:
        text = open(path, encoding="utf-8").read()
        try:
            meta, body = frontmatter(text)
        except yaml.YAMLError as e:
            errors.append(f"{rel(path)}: frontmatter does not parse: {e}")
            continue
        if meta is None:
            errors.append(f"{rel(path)}: no frontmatter")
            meta, body = {}, text
        for key in REQUIRED:
            if key not in meta:
                errors.append(f"{rel(path)}: frontmatter is missing '{key}'")
        if "updated" in meta and not DATE_RE.match(str(meta["updated"])):
            errors.append(f"{rel(path)}: 'updated' must be YYYY-MM-DD")
        sources = meta.get("sources")
        if isinstance(sources, dict):
            for label, target in sources.items():
                target = str(target)
                if re.match(r"^[a-z]+:", target):
                    continue
                if not os.path.exists(os.path.join(root, target.split("#", 1)[0])):
                    errors.append(f"{rel(path)}: source '{label}' points to a missing file: {target}")
        elif sources not in (None, "none yet") and not isinstance(sources, str):
            errors.append(f"{rel(path)}: 'sources' must be a map of label to path or URL")
        elif isinstance(sources, str) and sources != "none yet":
            warnings.append(f"{rel(path)}: 'sources' is a string; use a map of label to path or URL")

        here = os.path.dirname(path)
        links = local_links(body, here)
        links_from[path] = links
        for target in sorted(links):
            if not os.path.exists(target):
                errors.append(f"{rel(path)}: broken link to {os.path.relpath(target, here)}")

        parts = os.path.relpath(path, overview).split(os.sep)
        if parts[0] == "sites" and len(parts) == 3 and parts[2] == "index.md":
            site = parts[1]
            if not SLUG_RE.match(site):
                errors.append(f"{rel(path)}: site folder '{site}' must be a lowercase slug")
            if meta.get("site") != site:
                errors.append(f"{rel(path)}: 'site' must be '{site}'")
            scope = meta.get("scope")
            scopes = declared_scopes(root)
            if not scope:
                errors.append(f"{rel(path)}: site index is missing 'scope'")
            elif scopes and scope != "all" and scope not in scopes:
                errors.append(f"{rel(path)}: scope '{scope}' is not declared in docs/raci.yaml or docs/sources.yaml")

    sites = os.path.join(overview, "sites")
    if os.path.isdir(sites):
        for site in sorted(os.listdir(sites)):
            folder = os.path.join(sites, site)
            if os.path.isdir(folder) and not site.startswith(".") and not os.path.exists(os.path.join(folder, "index.md")):
                errors.append(f"{rel(folder)}: site folder has no index.md")

    for path in files:
        if path == index:
            continue
        folder = os.path.dirname(path)
        if os.path.basename(path) == "index.md":
            parent_index = [os.path.join(overview, "index.md")] if os.path.dirname(folder) == sites else \
                [os.path.join(os.path.dirname(folder), "index.md")]
        elif os.path.basename(folder) == "reference":
            above = os.path.dirname(folder)
            parent_index = [p for p in files if os.path.dirname(p) == above]
        else:
            parent_index = [os.path.join(folder, "index.md")]
        if not any(path in links_from.get(p, ()) for p in parent_index):
            errors.append(f"{rel(path)}: not linked from {', '.join(rel(p) for p in parent_index) or 'any index'}")

    for w in warnings:
        print(f"WARN:  {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        return 1
    n_sites = len([d for d in os.listdir(sites) if os.path.isdir(os.path.join(sites, d))]) if os.path.isdir(sites) else 0
    print(f"OK: {len(files)} files, {n_sites} sites, {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "docs/overview"))
