#!/usr/bin/env python3
"""Gather a Project Brain's setup for the project overview page.

Usage (from the Project Brain root):
  python3 .ai/general/skills/project-overview/overview.py [--out FILE]

Reads only local files and prints JSON (or writes it to FILE): the project's
name and key, the Lobot version, its repositories, ticket tracker, task
manager, its library (the Project Brain's own records and folders, the Google
Drive map with every standard layout item mapped, not used, or not yet mapped,
and what lives only on this computer), tracker pages, its agents, and which
connections are set up.
For connections it reports only whether each .env value is filled in, never
the value itself. `gaps` lists what isn't set up yet, with what the PM can say
to set it up. The project-overview skill fills its page template from this.

Exit code 0 = gathered, 1 = not a Project Brain root.
"""
import datetime
import json
import os
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
LAYOUT = os.path.join(HERE, "..", "drive-sources", "layout.yaml")
# Values from .env reported only as set or not set. GH_TOKEN_EXPIRES is a date, so it is shown.
ENV_CONNECTIONS = {
    "github": ["GH_TOKEN"],
    "jira": ["JIRA_SITE", "JIRA_EMAIL", "JIRA_API_TOKEN"],
}
# The Project Brain's own library: what lives in docs/, in the order a PM thinks of it.
BRAIN_LIBRARY = [
    ("Project dossier", "docs/overview/"),
    ("Meeting notes", "docs/meetings/"),
    ("Transcripts", "docs/transcripts/"),
    ("Journal", "docs/journals/"),
    ("Reports", "docs/reports/"),
    ("Work breakdown", "docs/work/"),
    ("Ticket plans", "docs/work/tickets/"),
    ("People", "docs/people.yaml"),
    ("RACI matrix", "docs/raci.yaml"),
    ("Glossary", "docs/glossary.yaml"),
    ("Decision log", "docs/decisions.yaml"),
    ("Risk tracker", "docs/risks.yaml"),
    ("Questions log", "docs/questions.yaml"),
    ("Task list", "docs/tasks.yaml"),
    ("Drive map", "docs/sources.yaml"),
]
# A plain job for each named agent; an agent not listed here gets its definition's first sentence.
AGENT_JOBS = {
    "lucy": ("Lucy the Librarian", "Files what you hand her (transcripts, notes, documents) and keeps the project's records."),
    "pepper": ("Pepper the Process Wrangler", "Writes and tidies tickets, and reports on boards and sprints."),
}
LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
URL_RE = re.compile(r"https?://[^\s)|>]+")


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def load_yaml(path):
    text = read(path)
    if text is None:
        return None
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError:
        return None


def first_line(path):
    text = read(path)
    if not text:
        return None
    for line in text.splitlines():
        if line.strip():
            return line.strip()
    return None


def env_values():
    """Names of .env keys that have a value, plus GH_TOKEN_EXPIRES. Values are never kept."""
    filled, expires = set(), None
    for line in (read(".env") or "").splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.*)$", line)
        if not m or line.lstrip().startswith("#"):
            continue
        key, value = m.group(1), m.group(2).strip().strip("'\"")
        if value:
            filled.add(key)
            if key == "GH_TOKEN_EXPIRES":
                expires = value
            if key == "JIRA_SITE":
                filled.add("JIRA_SITE=" + value)  # the site name isn't a secret; it makes the Jira link
    return filled, expires


def git_url(path):
    """The repository at `path` as a browser link (SSH remotes converted), or None."""
    try:
        out = subprocess.run(["git", "-C", path, "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
    url = out.stdout.strip()
    if out.returncode or not url:
        return None
    url = re.sub(r"^git@([^:]+):", r"https://\1/", url)
    url = re.sub(r"^ssh://git@([^/]+)/", r"https://\1/", url)
    url = re.sub(r"https://[^@/]+@", "https://", url)  # drop any credentials in the address
    return re.sub(r"\.git$", "", url)


def repo_name(url):
    m = re.match(r"https://github\.com/([^/]+/[^/]+)", url or "")
    return m.group(1) if m else url


def project_identity():
    text = read("CLAUDE.md") or ""
    name = key = None
    m = re.search(r"Lullabot's (.+?) \(([A-Z0-9]+)\) engagement", text)
    if m:
        name, key = m.group(1), m.group(2)
    else:
        m = re.search(r"^# (\S+) Project Brain", text, re.M)
        key = m.group(1) if m else None
    return name, key


def claude_md_rows():
    """Rows of the root CLAUDE.md "This project" table: (first cell, second cell)."""
    text = read("CLAUDE.md") or ""
    m = re.search(r"^## This project\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    rows = []
    for line in (m.group(1) if m else "").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and not set(cells[0]) <= set("-: ") and cells[0] not in ("Path", "Record", "Page"):
            rows.append(cells[:2])
    return rows


def pages(rows):
    out = []
    for first, second in rows:
        for cell in (second, first):
            hit = LINK_RE.search(cell) or URL_RE.search(cell)
            if hit and "claude.ai" in hit.group(0):
                url = hit.group(2) if hit.re is LINK_RE else hit.group(0)
                out.append({"name": re.sub(r"[`*]", "", first), "url": url})
                break
    return out


def code_repo(rows):
    url = git_url("repo") if os.path.isdir(os.path.join("repo", ".git")) else None
    note = next((second for first, second in rows if first.strip("`") in ("repo/", "repo")), "")
    if not url:
        m = re.search(r"\b([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\b", note) if "TODO" not in note else None
        if m and "/" in m.group(1) and not m.group(1).startswith("."):
            url = "https://github.com/" + m.group(1)
    return {"name": repo_name(url) if url else None, "url": url, "cloned": os.path.isdir("repo"),
            "note": None if "TODO" in note else (note or None)}


def brain_repo():
    text = read(".ai/project/github.md") or ""
    m = re.search(r"^- Repository:\s*([^\s(]+)", text, re.M)
    pending = re.search(r"^- Pending:\s*(.+)$", text, re.M)
    url = git_url(".")
    if not url and m:
        url = "https://github.com/" + m.group(1)
    return {"name": m.group(1) if m else repo_name(url), "url": url,
            "pending": None if not pending or pending.group(1).strip().lower() == "none" else pending.group(1).strip()}


def tracker(env):
    line = first_line(".ai/project/tickets.md")
    if not line or not line.lower().startswith("tracker:"):
        return {"set": False}
    value = line.split(":", 1)[1].strip()
    out = {"set": True, "value": value, "url": None}
    gh = re.search(r"GitHub,\s*repo\s+([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", value, re.I)
    board = re.search(r"board\s+(\d+)", value, re.I)
    jira = re.search(r"Jira,\s*space\s+([A-Z][A-Z0-9_]+)", value, re.I)
    if gh:
        out["url"] = "https://github.com/" + gh.group(1) + "/issues"
        if board:
            owner = gh.group(1).split("/")[0]
            out["board_url"] = f"https://github.com/orgs/{owner}/projects/{board.group(1)}"
    elif jira:
        site = next((k.split("=", 1)[1] for k in env if k.startswith("JIRA_SITE=")), None)
        if not site:
            m = re.search(r"\b([a-z0-9-]+\.atlassian\.net)\b", read(".ai/project/jira.md") or "")
            site = m.group(1) if m else None
        if site:
            site = re.sub(r"^https?://", "", site).rstrip("/")
            out["url"] = f"https://{site}/browse/{jira.group(1)}"
    return out


def agents():
    out = []
    folder = ".ai/general/agents"
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if not name.endswith(".md"):
            continue
        key = name[:-3]
        title, job = AGENT_JOBS.get(key, (key.capitalize(), None))
        if not job:
            m = re.search(r"^description:\s*(.+)$", read(os.path.join(folder, name)) or "", re.M)
            first = re.split(r"(?<=\.)\s", m.group(1))[0] if m else ""
            job = re.sub(r"\s*\([^)]*\)", "", first).strip()
        out.append({"key": key, "name": title, "job": job,
                    "configured": os.path.isfile(f".ai/project/agents/{key}/config.md")})
    return out


def brain_library(brain_url, sheets):
    """docs/ records and folders, linked to the Project Brain repository on GitHub when there is one."""
    out = []
    github = brain_url if (brain_url or "").startswith("https://github.com/") else None
    for name, path in BRAIN_LIBRARY:
        item = {"name": name, "path": path, "exists": os.path.exists(path.rstrip("/"))}
        if path in sheets:
            item["sheets"] = sheets[path]
        if github and item["exists"]:
            item["url"] = f"{github}/{'tree' if path.endswith('/') else 'blob'}/main/{path.rstrip('/')}"
        out.append(item)
    return out


def sheets_holding(sources):
    """docs/ record file -> [{name, url}] for records that live in Google Sheets (holds_record: true)."""
    out = {}
    for key, src in ((sources or {}).get("sources") or {}).items():
        if isinstance(src, dict) and src.get("holds_record"):
            records = src.get("record") or []
            for rec in records if isinstance(records, list) else [records]:
                out.setdefault(str(rec), []).append({"name": key, "url": src.get("url")})
    return out


def local_library(code):
    # In Cowork the PM connects ~/.lobot to the session, and it appears under ~/mnt/.
    profile = next((p for p in (os.path.expanduser("~/.lobot"), os.path.expanduser("~/mnt/.lobot")) if os.path.isdir(p)),
                   os.path.expanduser("~/.lobot"))
    return [
        {"name": "Code repository clone", "path": "repo/", "exists": os.path.isdir("repo"), "url": code.get("url")},
        {"name": "Your personal profile", "path": "~/.lobot/", "exists": os.path.isdir(profile)},
        {"name": "Your tokens", "path": ".env", "exists": os.path.isfile(".env"), "note": "never shared or committed"},
    ]


def drive(sources):
    sources = sources if isinstance(sources, dict) else {}
    layout = (load_yaml(LAYOUT) or {}).get("items", {})
    scopes = sources.get("scopes") or {}
    roots = sources.get("shared_drive") or {}
    if isinstance(roots, dict) and "url" in roots:
        roots = {"all": roots}
    mapped = sources.get("sources") or {}
    not_used = sources.get("not_used") or {}
    items, seen = [], set()

    def entry(key, src, scope, std):
        seen.add(key)
        base = key.split("@")[0]
        return {"key": key, "scope": scope, "name": (std or {}).get("name") or base.replace("-", " ").capitalize(),
                "parent": (std or {}).get("parent"), "standard": bool(std),
                "status": "mapped", "url": src.get("url"), "kind": src.get("kind"),
                "purpose": src.get("purpose"), "edit": src.get("edit"), "notes": src.get("notes")}

    scope_keys = list(scopes) or ["all"]
    for base, std in layout.items():
        for scope in scope_keys:
            for key in ([f"{base}@{scope}", base] if scope != "all" else [base]):
                if key in mapped:
                    if key not in seen:
                        items.append(entry(key, mapped[key], scope if "@" in key else "all", std))
                    break
                if key in not_used:
                    if key not in seen:
                        seen.add(key)
                        items.append({"key": key, "scope": scope if "@" in key else "all", "name": std.get("name"),
                                      "parent": std.get("parent"), "standard": True, "status": "not used",
                                      "reason": not_used[key]})
                    break
            else:
                items.append({"key": f"{base}@{scope}" if scope != "all" else base, "scope": scope,
                              "name": std.get("name"), "parent": std.get("parent"), "standard": True,
                              "status": "not mapped"})
    for key, src in mapped.items():
        if key not in seen and isinstance(src, dict):
            items.append(entry(key, src, key.split("@")[1] if "@" in key else "all", None))
    return {"scopes": scopes, "roots": {k: (v or {}).get("url") for k, v in roots.items() if isinstance(v, dict)},
            "items": items}


def main(args):
    out_path = args[args.index("--out") + 1] if "--out" in args and args.index("--out") + 1 < len(args) else None
    if not os.path.isfile("CLAUDE.md") or not os.path.isdir(".ai/general"):
        print(f"ERROR: run this from the Project Brain root (no CLAUDE.md and .ai/general/ in {os.getcwd()})")
        return 1
    env, expires = env_values()
    name, key = project_identity()
    stamp = load_yaml(".ai/general/.lobot-version") or {}
    rows = claude_md_rows()
    sources = load_yaml("docs/sources.yaml")
    task_line = first_line(".ai/project/task-management.md") or ""
    brain = brain_repo()
    code = code_repo(rows)
    data = {
        "gathered": datetime.date.today().isoformat(),
        "project": {"name": name, "key": key, "lobot_version": stamp.get("lobot_version"),
                    "lobot_updated": stamp.get("updated")},
        "repositories": {"brain": brain, "code": code},
        "tickets": tracker(env),
        "task_manager": task_line.split(":", 1)[1].strip() if task_line.lower().startswith("task manager:") else "Lobot",
        "library": {"brain": brain_library(brain["url"], sheets_holding(sources)),
                    "drive": drive(sources), "local": local_library(code)},
        "pages": pages(rows),
        "agents": agents(),
        "connections": {
            "github": {"set": all(k in env for k in ENV_CONNECTIONS["github"]), "expires": expires},
            "jira": {"set": all(k in env for k in ENV_CONNECTIONS["jira"]),
                     "missing": [k for k in ENV_CONNECTIONS["jira"] if k not in env]},
            "env_file": os.path.isfile(".env"),
        },
    }
    data["gaps"] = gaps(data)
    text = json.dumps(data, indent=2, default=str)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"OK: wrote {out_path} ({len(data['gaps'])} gap(s))")
    else:
        print(text)
    return 0


def gaps(d):
    """What isn't set up yet, each with what the PM can say to the assistant to set it up."""
    out = []
    add = lambda what, say: out.append({"what": what, "say": say})
    repos = d["repositories"]
    if not repos["brain"]["url"]:
        add("This Project Brain isn't saved to GitHub yet.", "Set up the Project Brain repository.")
    elif repos["brain"]["pending"]:
        add(f"Project Brain repository: {repos['brain']['pending']}", "Pick up the Project Brain repository setup.")
    if not repos["code"]["url"]:
        add("The code repository isn't recorded.", "The code repository is OWNER/REPO.")
    if not d["tickets"]["set"]:
        add("No tracker chosen for tickets.", "Our tickets go in Jira, space ABC (or GitHub, repo OWNER/REPO).")
    drive_ = d["library"]["drive"]
    if not drive_["roots"]:
        add("The project's shared Google Drive isn't mapped.", "Map the project's Google Drive.")
    else:
        missing = [i for i in drive_["items"] if i["status"] == "not mapped"]
        if missing:
            add(f"{len(missing)} standard Drive item(s) not mapped yet.", "Finish mapping the project's Google Drive.")
    if not d["pages"]:
        add("No review desk or tracker pages yet.", "Show me the review desk.")
    conn = d["connections"]
    if not conn["github"]["set"]:
        add("GitHub isn't connected on this computer.", "Connect GitHub.")
    if "jira" in (d["tickets"].get("value") or "").lower() and not conn["jira"]["set"]:
        add("Jira isn't connected on this computer.", "Connect to Jira.")
    for agent in d["agents"]:
        if not agent["configured"]:
            add(f"{agent['name']} has no settings for this project yet.", f"Set up {agent['name'].split()[0]}'s settings.")
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
