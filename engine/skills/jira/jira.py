#!/usr/bin/env python3
"""Read and write Jira Cloud work items through the REST API.

Usage (from the Project Brain root):
  python3 .ai/general/skills/jira/jira.py check
  python3 .ai/general/skills/jira/jira.py setup [--site SITE] [--email EMAIL]
  python3 .ai/general/skills/jira/jira.py spaces
  python3 .ai/general/skills/jira/jira.py types SPACE
  python3 .ai/general/skills/jira/jira.py fields SPACE TYPE
  python3 .ai/general/skills/jira/jira.py structure SPACE [--out FILE|-]
  python3 .ai/general/skills/jira/jira.py link-types
  python3 .ai/general/skills/jira/jira.py users QUERY
  python3 .ai/general/skills/jira/jira.py search JQL [--limit N] [--fields a,b]
  python3 .ai/general/skills/jira/jira.py view KEY [--comments]
  python3 .ai/general/skills/jira/jira.py transitions KEY
  python3 .ai/general/skills/jira/jira.py validate PLAN.yaml
  python3 .ai/general/skills/jira/jira.py apply PLAN.yaml [--dry-run]
  python3 .ai/general/skills/jira/jira.py link KEY "blocks" KEY [--dry-run]
  python3 .ai/general/skills/jira/jira.py transition KEY "STATUS" [--dry-run]
  python3 .ai/general/skills/jira/jira.py comment KEY FILE.md [--dry-run]
Add --json to any read for Jira's raw response.

Reads JIRA_SITE (yoursite.atlassian.net), JIRA_EMAIL, and JIRA_API_TOKEN from
the environment or the Project Brain's .env. Never prints the token.

Descriptions and comments are written in markdown and converted to Jira's
document format (ADF); `view` converts them back. `@key` in markdown becomes a
Jira mention when `key` is in docs/people.yaml with an `ids.jira` account ID.

`structure` writes a space's work types, the fields a plan can set (by their
names in Jira, with kinds and allowed values), statuses, link types, sprints,
and open epics to .ai/project/jira/SPACE.yaml, for writing plans without Jira.

`validate` and `apply` read a plan file (YAML or JSON; format in SKILL.md).
Fields are named as people see them in Jira and given human values; they are
matched to field IDs and converted to what the API expects (options, people,
sprints, markdown). Every problem is listed before anything is sent. Items
without a `key` are created, in order; items with one are updated. Created keys are
recorded in PLAN.created.json next to the plan, so running it again after a
failure skips what already exists. `apply` refuses a plan without
`approved_by` and `approved_at` (.ai/general/human-review.md).

Exit codes: 0 ok, 1 usage or data error, 2 Jira unreachable or refused.
"""
import base64
import datetime
import difflib
import hashlib
import html
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

PEOPLE = "docs/people.yaml"


# ---------------------------------------------------------------- basics

def fail(msg, code=1):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def load_env(path=".env"):
    """Values from .env, without overriding the environment."""
    env = {}
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                if k.startswith("export "):
                    k = k[len("export "):].strip()
                env[k] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    except OSError as e:
        # A sandbox or file permissions can hide .env; say so rather than
        # reporting its values as missing.
        fail(f"can't read {path}: {e.strerror}. It exists but this shell isn't "
             "allowed to read it; run the command from a shell that can.")
    for k in ("JIRA_SITE", "JIRA_EMAIL", "JIRA_API_TOKEN"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def load_data(path):
    """A YAML or JSON file. JSON needs nothing extra; YAML needs PyYAML."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        fail(f"can't read {path}: {e.strerror}")
    if path.endswith(".json"):
        try:
            return json.loads(text)
        except ValueError as e:
            fail(f"{path} is not valid JSON: {e}")
    try:
        import yaml
    except ImportError:
        fail("PyYAML is required for YAML plans (pip install pyyaml), or write the plan as .json")
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as e:
        fail(f"{path} is not valid YAML: {e}")


_people = None


def people():
    """people-key -> Jira account ID, from docs/people.yaml (ids.jira)."""
    global _people
    if _people is None:
        _people = {}
        if os.path.exists(PEOPLE):
            try:
                import yaml
            except ImportError:
                fail(f"PyYAML is required to read {PEOPLE} (pip install pyyaml)")
            try:
                with open(PEOPLE, encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            except (OSError, yaml.YAMLError) as e:
                fail(f"can't read {PEOPLE}: {e}")
            rows = data.get("people", data) if isinstance(data, dict) else data
            if isinstance(rows, dict):
                rows = [dict(v, key=k) if isinstance(v, dict) else {} for k, v in rows.items()]
            for p in rows or []:
                if isinstance(p, dict) and p.get("key"):
                    jid = (p.get("ids") or {}).get("jira")
                    if jid:
                        _people[str(p["key"])] = {"id": str(jid), "name": str(p.get("name") or p["key"])}
    return _people


# ---------------------------------------------------------------- HTTP

class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Never follow a redirect: it could carry the token to another host."""

    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


class Jira:
    def __init__(self, dry=False):
        env = load_env()
        site = env.get("JIRA_SITE", "")
        site = re.sub(r"^https?://", "", site).strip("/")
        if "/" in site:
            fail("JIRA_SITE is the site's host name only (yoursite.atlassian.net), with no path")
        if site and not site.endswith(".atlassian.net"):
            print(f"note: {site} isn't an atlassian.net address; the token will be sent there", file=sys.stderr)
        self.site, self.dry = site, dry
        email, token = env.get("JIRA_EMAIL"), env.get("JIRA_API_TOKEN")
        if not site:
            fail("JIRA_SITE is not set. Add it to the Project Brain's .env (yoursite.atlassian.net); see .env.example.")
        if not email or not token:
            fail("JIRA_EMAIL and JIRA_API_TOKEN must be set in the Project Brain's .env (see .env.example); never paste a token in chat.")
        self.base = f"https://{site}/rest/api/3"
        self.agile = f"https://{site}/rest/agile/1.0"
        self.auth = "Basic " + base64.b64encode(f"{email}:{token}".encode()).decode()
        self._fields = None

    def url(self, key):
        return f"https://{self.site}/browse/{key}"

    def call(self, method, path, body=None, query=None, api="core"):
        url = (self.agile if api == "agile" else self.base) + path
        if query:
            url += "?" + urllib.parse.urlencode(query, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Authorization": self.auth, "Accept": "application/json"}
        if data is not None:
            headers["Content-Type"] = "application/json"
        for attempt in range(4):
            req = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with OPENER.open(req, timeout=60) as resp:
                    raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
            except urllib.error.HTTPError as e:
                if e.code == 429 and attempt < 3:
                    try:
                        wait = int(e.headers.get("Retry-After") or 5)
                    except ValueError:
                        wait = 5
                    time.sleep(min(max(wait, 1), 30))
                    continue
                if 300 <= e.code < 400:
                    fail(f"{self.site} redirected to {e.headers.get('Location', 'another address')}; not following it. "
                         "Check JIRA_SITE is the site's own atlassian.net address.", 2)
                raise JiraError(e.code, e.read().decode("utf-8", "replace"))
            except urllib.error.URLError as e:
                reason = str(e.reason)
                if "403" in reason or "Tunnel" in reason or "proxy" in reason.lower():
                    raise Unreachable(f"{self.site} is blocked by this shell's network allowlist. Ask the organization's admin "
                                      "to allow it (in Claude: Admin settings > Capabilities), or use Claude Code on this computer "
                                      "(jira skill, \"Connecting to Jira\").", blocked=True)
                raise Unreachable(f"could not reach {self.site}: {reason}")
            except (OSError, ValueError, http.client.HTTPException) as e:
                fail(f"the connection to {self.site} failed mid-request ({e.__class__.__name__}). If this was a write, "
                     "check Jira before retrying; `apply` skips what its record shows was done.", 2)

    def get(self, path, **query):
        return self.call("GET", path, query=query or None)

    def write(self, method, path, body, label):
        """A change. With --dry-run, print it instead of sending."""
        if self.dry:
            print(f"--- {label}\n{method} {path}")
            if body is not None:
                print(json.dumps(brief(body), indent=2, ensure_ascii=False))
            return None
        return self.call(method, path, body)


def brief(data):
    """A request body for --dry-run, with documents shown as the markdown they came from."""
    if isinstance(data, dict):
        if data.get("type") == "doc" and "content" in data:
            return adf_to_md(data).split("\n")
        return {k: brief(v) for k, v in data.items()}
    if isinstance(data, list):
        return [brief(v) for v in data]
    return data


class Unreachable(Exception):
    def __init__(self, msg, blocked=False):
        super().__init__(msg)
        self.blocked = blocked


class JiraError(Exception):
    def __init__(self, code, body):
        self.code = code
        try:
            data = json.loads(body)
        except ValueError:
            data = {}
        msgs = list(data.get("errorMessages") or [])
        msgs += [f"{k}: {v}" for k, v in (data.get("errors") or {}).items()]
        hints = {401: "the email or API token was refused; check JIRA_EMAIL and JIRA_API_TOKEN",
                 403: "your account doesn't have permission for this",
                 404: "not found, or your account can't see it"}
        self.detail = "; ".join(msgs) or hints.get(code, body[:300] or "unexpected response")
        super().__init__(f"Jira returned HTTP {code}: {self.detail}")


def run(fn):
    try:
        fn()
    except (JiraError, Unreachable) as e:
        fail(str(e), 2)


# ---------------------------------------------------------------- markdown -> ADF

INLINE = re.compile(
    r"(?P<esc>\\[\\`*_{}\[\]()#+\-.!~>|@])"
    r"|(?P<code>`+)(?P<codebody>.+?)(?P=code)"
    r"|\[(?P<ltext>[^\]]+)\]\((?P<lurl>[^)\s]+)\)"
    r"|<(?P<aurl>https?://[^>\s]+)>"
    r"|(?P<burl>https?://[^\s<>()]+[^\s<>().,;:!?'\"])"
    r"|\*\*(?P<b1>.+?)\*\*|__(?P<b2>.+?)__"
    r"|~~(?P<s>.+?)~~"
    r"|\*(?P<i1>[^*\s](?:.*?[^*\s])?)\*"
    r"|(?<![\w])_(?P<i2>[^_\s](?:.*?[^_\s])?)_(?![\w])"
    r"|(?<![\w@])@(?P<who>[a-z0-9][a-z0-9._-]*[a-z0-9])"
)


def _mark(nodes, mark):
    for n in nodes:
        if n["type"] == "text":
            n.setdefault("marks", [])
            kinds = {m["type"] for m in n["marks"]}
            if mark["type"] in kinds or ("code" in kinds and mark["type"] != "link"):
                continue
            n["marks"].append(mark)
    return nodes


def inline(text):
    out, pos = [], 0

    def txt(s):
        if s:
            if out and out[-1]["type"] == "text" and not out[-1].get("marks"):
                out[-1]["text"] += s
            else:
                out.append({"type": "text", "text": s})

    for m in INLINE.finditer(text):
        txt(text[pos:m.start()])
        pos = m.end()
        g = m.groupdict()
        if g["esc"]:
            txt(g["esc"][1])
        elif g["code"]:
            out.append({"type": "text", "text": g["codebody"].strip(" ") or g["codebody"], "marks": [{"type": "code"}]})
        elif g["ltext"]:
            out.extend(_mark(inline(g["ltext"]), {"type": "link", "attrs": {"href": g["lurl"]}}))
        elif g["aurl"] or g["burl"]:
            u = g["aurl"] or g["burl"]
            out.append({"type": "text", "text": u, "marks": [{"type": "link", "attrs": {"href": u}}]})
        elif g["b1"] or g["b2"]:
            out.extend(_mark(inline(g["b1"] or g["b2"]), {"type": "strong"}))
        elif g["s"]:
            out.extend(_mark(inline(g["s"]), {"type": "strike"}))
        elif g["i1"] or g["i2"]:
            out.extend(_mark(inline(g["i1"] or g["i2"]), {"type": "em"}))
        elif g["who"]:
            p = people().get(g["who"])
            if p:
                out.append({"type": "mention", "attrs": {"id": p["id"], "text": "@" + p["name"]}})
            else:
                txt(m.group(0))
    txt(text[pos:])
    for n in out:
        if not n.get("marks"):
            n.pop("marks", None)
    return out


def para_lines(lines):
    """Inline content for consecutive lines: soft breaks become spaces, hard breaks stay."""
    content = []
    for i, line in enumerate(lines):
        hard = line.endswith("  ") or line.endswith("\\")
        line = line.rstrip()
        if line.endswith("\\"):
            line = line[:-1]
        if i and not (content and content[-1]["type"] == "hardBreak"):
            content.extend(inline(" "))
        content.extend(inline(line.strip()))
        if hard and i < len(lines) - 1:
            content.append({"type": "hardBreak"})
    # merge adjacent plain text
    merged = []
    for n in content:
        if merged and n["type"] == "text" and merged[-1]["type"] == "text" and not n.get("marks") and not merged[-1].get("marks"):
            merged[-1]["text"] += n["text"]
        else:
            merged.append(n)
    return merged


LIST = re.compile(r"^(?P<ind>\s*)(?P<mark>[-*+]|\d+[.)])\s+(?P<rest>.*)$")
TASK = re.compile(r"^\[(?P<x>[ xX])\]\s+(?P<text>.*)$")
FENCE = re.compile(r"^\s*(```+|~~~+)\s*([\w+-]*)\s*$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)(?:\s+#+)?\s*$")
RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")


def indent_of(line):
    return len(line.expandtabs(4)) - len(line.expandtabs(4).lstrip())


def is_block_start(lines, i):
    line = lines[i]
    return bool(FENCE.match(line) or HEADING.match(line) or RULE.match(line) or line.lstrip().startswith(">")
                or LIST.match(line) or (line.lstrip().startswith("|") and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1])))


def cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def blocks(lines):
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = FENCE.match(line)
        if m:
            fence, lang, body = m.group(1), m.group(2), []
            i += 1
            close = re.compile(r"^\s*" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*$")
            while i < len(lines) and not close.match(lines[i]):
                body.append(lines[i])
                i += 1
            i += 1
            code = "\n".join(body)
            node = {"type": "codeBlock", "content": [{"type": "text", "text": code}] if code else []}
            if lang:
                node["attrs"] = {"language": lang}
            out.append(node)
            continue
        m = HEADING.match(line)
        if m:
            out.append({"type": "heading", "attrs": {"level": len(m.group(1))}, "content": inline(m.group(2))})
            i += 1
            continue
        if RULE.match(line):
            out.append({"type": "rule"})
            i += 1
            continue
        if line.lstrip().startswith(">"):
            inner = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                inner.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            out.append({"type": "blockquote", "content": nestable(blocks(inner)) or [{"type": "paragraph", "content": []}]})
            continue
        if line.lstrip().startswith("|") and i + 1 < len(lines) and TABLE_SEP.match(lines[i + 1]):
            head = cells(line)
            rows = []
            i += 2
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1

            def row(cs, kind):
                cs = (cs + [""] * len(head))[:len(head)]
                return {"type": "tableRow", "content": [
                    {"type": kind, "content": [{"type": "paragraph", "content": inline(c)}]} for c in cs]}
            out.append({"type": "table", "content": [row(head, "tableHeader")] + [row(r, "tableCell") for r in rows]})
            continue
        if LIST.match(line):
            node, i = parse_list(lines, i)
            out.extend(node)
            continue
        para = []
        while i < len(lines) and lines[i].strip() and not (para and is_block_start(lines, i)):
            para.append(lines[i])
            i += 1
        out.append({"type": "paragraph", "content": para_lines(para)})
    return out


def parse_list(lines, i):
    """Consecutive list items at one indent -> one or more lists (a change of kind starts a new list)."""
    base = indent_of(lines[i])
    lists = []
    while i < len(lines):
        m = LIST.match(lines[i]) if lines[i].strip() else None
        if not m or indent_of(lines[i]) != base:
            if m and indent_of(lines[i]) > base:
                i += 1  # stray deeper item with no parent; keep going
                continue
            if not lines[i].strip() and i + 1 < len(lines) and LIST.match(lines[i + 1]) and indent_of(lines[i + 1]) == base:
                i += 1
                continue
            break
        mark, rest = m.group("mark"), m.group("rest")
        t = TASK.match(rest) if mark in "-*+" else None
        kind = "taskList" if t else ("bulletList" if mark in "-*+" else "orderedList")
        text = [t.group("text") if t else rest]
        i += 1
        child = []
        while i < len(lines):
            if not lines[i].strip():
                if i + 1 < len(lines) and lines[i + 1].strip() and indent_of(lines[i + 1]) > base:
                    child.append("")
                    i += 1
                    continue
                break
            if indent_of(lines[i]) <= base:
                break
            if not child and not LIST.match(lines[i]):
                text.append(lines[i])
            else:
                child.append(lines[i])
            i += 1
        sub = blocks(dedent(child)) if child else []
        if not lists or lists[-1]["type"] != kind:
            node = {"type": kind, "content": []}
            if kind == "orderedList":
                node["attrs"] = {"order": int(re.match(r"\d+", mark).group())}
            if kind == "taskList":
                node["attrs"] = {"localId": str(uuid.uuid4())}
            lists.append(node)
        if kind == "taskList":
            lists[-1]["content"].append({"type": "taskItem", "attrs": {"localId": str(uuid.uuid4()),
                                         "state": "TODO" if t.group("x") == " " else "DONE"},
                                         "content": para_lines(text)})
            item = lists[-1]["content"][-1]
            for s in sub:  # nested tasks nest; anything else joins the task's own text on a new line
                if s["type"] == "taskList":
                    lists[-1]["content"].append(s)
                    continue
                for p in nestable([s]):
                    for line in flat_text(p):
                        if line:
                            item["content"] += [{"type": "hardBreak"}] + line
        else:
            content = [{"type": "paragraph", "content": para_lines(text)}]
            for s in sub:  # a list item can't hold tasks, quotes, headings, or tables: nestable() rewrites them
                content.extend(nestable([s]))
            lists[-1]["content"].append({"type": "listItem", "content": content})
    return lists, i


def nestable(nodes):
    """Blocks a list item or quote may hold: paragraphs, lists, and code. Others are turned into paragraphs."""
    out = []
    for n in nodes:
        t = n["type"]
        if t in ("paragraph", "bulletList", "orderedList", "codeBlock"):
            out.append(n)
        elif t == "heading":
            out.append({"type": "paragraph", "content": _mark(n.get("content", []), {"type": "strong"})})
        elif t == "blockquote":
            out.extend(nestable(n.get("content", [])))
        elif t == "table":
            for row in n.get("content", []):
                cells_ = [c for cell in row.get("content", []) for c in cell.get("content", [])]
                para = []
                for k, c in enumerate(cells_):
                    para += ([{"type": "text", "text": " | "}] if k else []) + c.get("content", [])
                out.append({"type": "paragraph", "content": para})
        elif t == "taskList":
            out.append({"type": "bulletList", "content": [
                {"type": "listItem", "content": [{"type": "paragraph", "content":
                    [{"type": "text", "text": ("☑ " if ti["attrs"]["state"] == "DONE" else "☐ ")}] + ti.get("content", [])}]}
                for ti in n["content"] if ti["type"] == "taskItem"]})
        # rules are dropped
    return out


def flat_text(node):
    """Inline lines of a paragraph, list, or code block, for content a task item can't nest."""
    t = node["type"]
    if t == "paragraph":
        return [node.get("content", [])]
    if t == "codeBlock":
        return [[{"type": "text", "text": l, "marks": [{"type": "code"}]}] for l in adf_inline(node.get("content")).split("\n") if l]
    lines = []
    for k, item in enumerate(node.get("content", []), 1):
        for b in item.get("content", []):
            for line in flat_text(b):
                bullet = f"{k}. " if t == "orderedList" else "• "
                lines.append([{"type": "text", "text": bullet}] + line)
    return lines


def dedent(lines):
    ind = min((indent_of(l) for l in lines if l.strip()), default=0)
    return [l.expandtabs(4)[ind:] if l.strip() else "" for l in lines]


def md_to_adf(text):
    return {"type": "doc", "version": 1, "content": blocks(str(text or "").replace("\r\n", "\n").split("\n"))}


# ---------------------------------------------------------------- ADF -> markdown

def adf_inline(nodes):
    out = []
    for n in nodes or []:
        t = n.get("type")
        if t == "text":
            s = n.get("text", "")
            marks = {m["type"]: m for m in n.get("marks", [])}
            if "code" in marks:
                s = f"`{s}`"
            if "strong" in marks:
                s = f"**{s}**"
            if "em" in marks:
                s = f"_{s}_"
            if "strike" in marks:
                s = f"~~{s}~~"
            if "link" in marks:
                href = marks["link"].get("attrs", {}).get("href", "")
                s = href if s == href else f"[{s}]({href})"
            out.append(s)
        elif t == "hardBreak":
            out.append("  \n")
        elif t == "mention":
            out.append(n.get("attrs", {}).get("text") or "@" + n.get("attrs", {}).get("id", ""))
        elif t in ("inlineCard", "blockCard"):
            out.append(n.get("attrs", {}).get("url", ""))
        elif t == "emoji":
            out.append(n.get("attrs", {}).get("text") or n.get("attrs", {}).get("shortName", ""))
        elif t == "status":
            out.append(f"[{n.get('attrs', {}).get('text', '')}]")
        elif t == "date":
            ts = n.get("attrs", {}).get("timestamp")
            out.append(time.strftime("%Y-%m-%d", time.gmtime(int(ts) / 1000)) if ts else "")
        else:
            out.append(adf_inline(n.get("content")))
    return "".join(out)


def adf_blocks(nodes, ind="", sep="\n\n"):
    out = []
    for n in nodes or []:
        t = n.get("type")
        c = n.get("content")
        if t == "paragraph":
            out.append(ind + adf_inline(c).replace("\n", "\n" + ind))
        elif t == "heading":
            out.append(ind + "#" * n.get("attrs", {}).get("level", 1) + " " + adf_inline(c))
        elif t in ("bulletList", "orderedList"):
            num = n.get("attrs", {}).get("order", 1)
            items = []
            for k, item in enumerate(c or []):
                marker = f"{num + k}." if t == "orderedList" else "-"
                body = adf_blocks(item.get("content"), ind + " " * (len(marker) + 1), "\n").lstrip()
                items.append(ind + marker + " " + body)
            out.append("\n".join(items))
        elif t == "taskList":
            items = []
            for item in c or []:
                if item.get("type") == "taskList":
                    items.append(adf_blocks([item], ind + "  "))
                else:
                    box = "x" if item.get("attrs", {}).get("state") == "DONE" else " "
                    items.append(f"{ind}- [{box}] " + adf_inline(item.get("content")))
            out.append("\n".join(items))
        elif t == "codeBlock":
            lang = n.get("attrs", {}).get("language") or ""
            code = adf_inline(c)
            fence = "`" * max(3, max((len(r) for r in re.findall(r"`+", code)), default=0) + 1)
            out.append(f"{ind}{fence}{lang}\n" + code + f"\n{ind}{fence}")
        elif t in ("blockquote", "panel"):
            inner = adf_blocks(c)
            out.append("\n".join(ind + "> " + l if l else ind + ">" for l in inner.split("\n")))
        elif t == "rule":
            out.append(ind + "---")
        elif t == "table":
            rows = [[adf_blocks(cell.get("content")).replace("\n", " ") for cell in r.get("content", [])] for r in c or []]
            if rows:
                lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * len(rows[0])]
                lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
                out.append("\n".join(ind + l for l in lines))
        elif t in ("mediaSingle", "mediaGroup", "media"):
            out.append(ind + "[attachment]")
        elif t in ("expand", "nestedExpand"):
            out.append(ind + "**" + n.get("attrs", {}).get("title", "") + "**\n\n" + adf_blocks(c, ind))
        elif c:
            out.append(adf_blocks(c, ind) if c and c[0].get("type") not in ("text",) else ind + adf_inline(c))
    return sep.join(x for x in out if x is not None)


def adf_to_md(doc):
    if not doc:
        return ""
    if isinstance(doc, str):
        return doc
    return adf_blocks(doc.get("content")).strip()


# ---------------------------------------------------------------- reads

def as_json(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))


ENV_KEYS = ("JIRA_SITE", "JIRA_EMAIL", "JIRA_API_TOKEN")


def cmd_check(args):
    """Is Jira reachable from here? The last line is one of:
    jira: ok as NAME | jira: missing KEYS | jira: blocked | jira: refused | jira: unreachable"""
    env = load_env()
    missing = [k for k in ENV_KEYS if not env.get(k)]
    if missing:
        print(f"jira: missing {', '.join(missing)} in .env (run `setup`, then the PM pastes the token)")
        sys.exit(3)
    j = Jira()
    try:
        me = j.get("/myself")
    except Unreachable as e:
        print(f"jira: {'blocked' if e.blocked else 'unreachable'}: {e}")
        sys.exit(4 if e.blocked else 2)
    except JiraError as e:
        print(f"jira: refused: {e.detail}" + (" (check the email, or make a new token: it may have expired)" if e.code == 401 else ""))
        sys.exit(5)
    print(f"jira: ok as {me.get('displayName')} (account ID {me.get('accountId')}) on {j.site}")


def cmd_setup(args):
    """Get .env ready for the PM's token: git-ignored, with the three lines, and site and email filled in when given.
    Never reads out or changes the token."""
    import subprocess

    def git(*a):
        try:
            return subprocess.run(["git", *a], capture_output=True, text=True).returncode
        except OSError:
            return None

    if git("rev-parse", "--is-inside-work-tree") == 0:
        if git("ls-files", "--error-unmatch", ".env") == 0:
            print("ignore: STOP: .env is committed to this repository. Untrack it, and revoke any token it held.")
            sys.exit(4)
        if git("check-ignore", "-q", "--no-index", ".env") == 0:
            print("ignore: yes")
        else:
            with open(".gitignore", "a", encoding="utf-8") as f:
                f.write("\n# Local secrets (per-PM tokens). Never commit.\n.env\n")
            print("ignore: added .env to .gitignore (commit this change)")
    else:
        print("ignore: not a git repository; skipped")

    exists = os.path.exists(".env")
    try:
        lines = open(".env", encoding="utf-8").read().splitlines() if exists else []
    except OSError as e:
        fail(f"can't read .env: {e.strerror}")
    want = {"JIRA_SITE": re.sub(r"^https?://", "", args.site or "").strip("/"), "JIRA_EMAIL": (args.email or "").strip()}
    found = {}
    for i, line in enumerate(lines):
        m = re.match(r"\s*(?:export\s+)?(JIRA_SITE|JIRA_EMAIL|JIRA_API_TOKEN)\s*=(.*)$", line)
        if m:
            found[m.group(1)] = (i, m.group(2).strip().strip('"').strip("'"))
    changed = False
    for k in ("JIRA_SITE", "JIRA_EMAIL"):
        if k in found and want[k] and not found[k][1]:
            lines[found[k][0]] = f"{k}={want[k]}"
            found[k] = (found[k][0], want[k])
            changed = True
    new = [k for k in ENV_KEYS if k not in found]
    if new:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append("# Jira Cloud, for the jira skill: the site, your Atlassian login email, and your own API token. Never commit.")
        for k in new:
            lines.append(f"{k}={want.get(k, '')}")
            found[k] = (len(lines) - 1, want.get(k, ""))
        changed = True
    if changed:
        fd = os.open(".env", os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    try:
        os.chmod(".env", 0o600)
    except OSError:
        pass
    print(f"env: {'created' if not exists else 'updated' if changed else 'ready'} ({os.path.abspath('.env')})")
    for k, label_ in (("JIRA_SITE", "site"), ("JIRA_EMAIL", "email")):
        print(f"{label_}: {found[k][1] or 'missing'}")
    print(f"token: {'present' if found['JIRA_API_TOKEN'][1] else 'missing'}")


def cmd_spaces(args):
    j = Jira()
    rows, start = [], 0
    while True:
        page = j.get("/project/search", startAt=start, maxResults=50, expand="lead")
        rows += page.get("values", [])
        if page.get("isLast", True) or not page.get("values"):
            break
        start += len(page["values"])
    if args.json:
        return as_json(rows)
    for p in rows:
        style = {"classic": "company-managed", "next-gen": "team-managed"}.get(p.get("style"), p.get("style", ""))
        # Jira returns some space names HTML-escaped ("&amp;").
        print(f"{p['key']}\t{html.unescape(p['name'])}\t{style}\t{p.get('projectTypeKey', '')}")


def paged(j, path, keys):
    """Every row of a createmeta-style list, page by page."""
    rows, start = [], 0
    while True:
        data = j.get(path, startAt=start, maxResults=200)
        page = next((data[k] for k in keys if isinstance(data.get(k), list)), [])
        rows += page
        start += len(page)
        if not page or data.get("isLast") or start >= int(data.get("total") or 0):
            return rows


def issue_types(j, space):
    return paged(j, f"/issue/createmeta/{urllib.parse.quote(space)}/issuetypes", ("issueTypes", "createMetaIssueType", "values"))


def cmd_types(args):
    j = Jira()
    types = issue_types(j, args.space)
    if args.json:
        return as_json(types)
    for t in types:
        lvl = t.get("hierarchyLevel", -1 if t.get("subtask") else 0)
        print(f"{t['id']}\t{t['name']}\tlevel {lvl}" + ("\tsubtask" if t.get("subtask") else ""))


def cmd_fields(args):
    j = Jira()
    M = Meta(j)
    t = M.type(args.space, args.type)
    if not t:
        fail(f"no work type '{args.type}' in {args.space}; it has: " + ", ".join(x["name"] for x in M.types(args.space)))
    avail = M.create_fields(args.space, t)
    if args.json:
        return as_json(avail.list)
    for m in sorted(avail.list, key=lambda m: (not (m["required"] and not m["default"]), m["name"].lower())):
        if m["id"] in NOT_FIELDS:
            continue
        vals = [label(a) for a in m["allowed"] or []]
        line = f"{m['name']}\t{kind(m)}\t{'required' if m['required'] and not m['default'] else 'optional'}\t{m['id']}"
        if vals:
            line += "\t" + ", ".join(vals[:15]) + (f" (+{len(vals) - 15} more)" if len(vals) > 15 else "")
        print(line)


def cmd_link_types(args):
    j = Jira()
    types = j.get("/issueLinkType").get("issueLinkTypes", [])
    if args.json:
        return as_json(types)
    for t in types:
        print(f"{t['name']}\tA {t['outward']} B\tB {t['inward']} A")


def cmd_users(args):
    j = Jira()
    users = j.get("/user/search", query=args.query, maxResults=20)
    if args.json:
        return as_json(users)
    for u in users:
        if u.get("accountType") == "atlassian":
            print(f"{u['accountId']}\t{u.get('displayName', '')}" + ("" if u.get("active", True) else "\tinactive"))


def fmt_issue(i):
    f = i.get("fields", {})
    bits = [i["key"], f"[{(f.get('issuetype') or {}).get('name', '?')}]", (f.get("status") or {}).get("name", "?"),
            f.get("summary", "")]
    if f.get("parent"):
        bits.append(f"(parent {f['parent']['key']})")
    if f.get("assignee"):
        bits.append("@" + (f["assignee"].get("displayName") or f["assignee"].get("accountId", "?")))
    return "\t".join(bits)


def cmd_search(args):
    j = Jira()
    fields = args.fields.split(",") if args.fields else ["summary", "status", "issuetype", "parent", "assignee"]
    issues, more = search(j, args.jql, fields, args.limit)
    if args.json:
        return as_json(issues)
    for i in issues:
        print(fmt_issue(i))
    if more:
        print(f"(stopped at {args.limit}; use --limit for more)")


def cmd_view(args):
    j = Jira()
    i = j.get(f"/issue/{urllib.parse.quote(args.key)}")
    comments = j.get(f"/issue/{urllib.parse.quote(args.key)}/comment", maxResults=100).get("comments", []) if args.comments else []
    if args.json:
        return as_json({"issue": i, "comments": comments} if args.comments else i)
    f = i["fields"]
    print(f"{i['key']}: {f.get('summary')}\n{j.url(i['key'])}")
    rows = [("Type", (f.get("issuetype") or {}).get("name")), ("Status", (f.get("status") or {}).get("name")),
            ("Space", (f.get("project") or {}).get("key")),
            ("Parent", f"{f['parent']['key']} {f['parent'].get('fields', {}).get('summary', '')}" if f.get("parent") else None),
            ("Assignee", (f.get("assignee") or {}).get("displayName")),
            ("Reporter", (f.get("reporter") or {}).get("displayName")),
            ("Priority", (f.get("priority") or {}).get("name")),
            ("Labels", ", ".join(f.get("labels") or []) or None),
            ("Components", ", ".join(c["name"] for c in f.get("components") or []) or None),
            ("Sprint", ", ".join(s.get("name", "") for k, v in f.items() if k.startswith("customfield_") and isinstance(v, list)
                                 for s in v if isinstance(s, dict) and "boardId" in s) or None),
            ("Created", (f.get("created") or "")[:10]), ("Updated", (f.get("updated") or "")[:10])]
    for k, v in rows:
        if v:
            print(f"{k}: {v}")
    for l in f.get("issuelinks") or []:
        if l.get("outwardIssue"):
            print(f"Link: {l['type']['outward']} {l['outwardIssue']['key']}")
        elif l.get("inwardIssue"):
            print(f"Link: {l['type']['inward']} {l['inwardIssue']['key']}")
    for s in f.get("subtasks") or []:
        print(f"Child: {s['key']} {s['fields'].get('summary', '')}")
    print("\n" + (adf_to_md(f.get("description")) or "(no description)"))
    for c in comments:
        print(f"\n--- {c.get('author', {}).get('displayName')} {c.get('created', '')[:16].replace('T', ' ')}\n{adf_to_md(c.get('body'))}")


def get_transitions(j, key):
    return j.get(f"/issue/{urllib.parse.quote(key)}/transitions").get("transitions", [])


def cmd_transitions(args):
    j = Jira()
    ts = get_transitions(j, args.key)
    if args.json:
        return as_json(ts)
    for t in ts:
        print(f"{t['id']}\t{t['name']}\t-> {t['to']['name']}")


# ---------------------------------------------------------------- space structure

PLAN_KEYS = {"ref", "key", "type", "space", "parent", "links", "transition", "comment", "fields"}
NOT_FIELDS = {"project", "issuetype", "parent", "issuelinks", "attachment"}  # set by the plan's own keys, or not at all
KEY_RE = re.compile(r"[A-Z][A-Z0-9_]*-\d+")


def level(t):
    """A work type's hierarchy level: 1 epic, 0 standard, -1 subtask (2+ above epic, Premium)."""
    if t.get("hierarchyLevel") is not None:
        return int(t["hierarchyLevel"])
    return -1 if t.get("subtask") else 0


def field_meta(f, fid=None):
    return {"id": str(fid or f.get("fieldId") or f.get("key") or f.get("id")), "name": str(f.get("name") or fid),
            "required": bool(f.get("required")), "schema": f.get("schema") or {},
            "allowed": f.get("allowedValues"), "default": bool(f.get("hasDefaultValue"))}


def kind(m):
    """A field's kind, in the words plan files and the structure file use."""
    s = m["schema"]
    t, custom, system = s.get("type", ""), s.get("custom", ""), s.get("system", "")
    if system in ("description", "environment") or custom.endswith(":textarea"):
        return "long text"
    if custom.endswith(":gh-sprint"):
        return "sprint"
    if custom.endswith(":atlassian-team") or t == "team":
        return "team"
    if t == "array":
        return {"option": "options", "user": "people", "version": "versions", "component": "components",
                "string": "labels", "group": "groups"}.get(s.get("items"), "other")
    if t == "string":
        return "url" if custom.endswith(":url") else "text"
    return {"number": "number", "date": "date", "datetime": "datetime", "option": "option", "priority": "option",
            "resolution": "option", "securitylevel": "option", "option-with-child": "option / child",
            "user": "person", "version": "version", "group": "group"}.get(t, "other")


def label(av):
    return str(av.get("value") or av.get("name") or av.get("key") or av.get("id"))


class Fields:
    """A set of fields, found by ID or by name, ignoring case."""

    def __init__(self, metas):
        self.list = list(metas)
        self.by = {}
        for m in self.list:
            self.by.setdefault(m["id"].lower(), []).append(m)
            if m["name"].lower() != m["id"].lower():
                self.by.setdefault(m["name"].lower(), []).append(m)

    def find(self, name):
        return self.by.get(str(name).strip().lower(), [])

    def names(self):
        return [m["name"] for m in self.list]


class Meta:
    """Cached reads of a site's structure."""

    def __init__(self, j):
        self.j = j
        self._types, self._create, self._edit, self._issues, self._sprints, self._statuses = {}, {}, {}, {}, {}, {}
        self._all = self._links = None

    def types(self, space):
        if space not in self._types:
            self._types[space] = issue_types(self.j, space)
        return self._types[space]

    def type(self, space, name):
        name = str(name or "").strip().lower()
        return next((t for t in self.types(space) if t["name"].lower() == name or t["id"] == name), None)

    def create_fields(self, space, t):
        k = (space, t["id"])
        if k not in self._create:
            rows = paged(self.j, f"/issue/createmeta/{urllib.parse.quote(space)}/issuetypes/{t['id']}", ("fields", "results", "values"))
            self._create[k] = Fields(field_meta(f) for f in rows)
        return self._create[k]

    def edit_fields(self, key):
        if key not in self._edit:
            rows = self.j.get(f"/issue/{urllib.parse.quote(key)}/editmeta").get("fields", {})
            self._edit[key] = Fields(field_meta(f, fid) for fid, f in rows.items())
        return self._edit[key]

    def all_fields(self):
        if self._all is None:
            self._all = Fields(field_meta(f) for f in self.j.get("/field"))
        return self._all

    def issue(self, key):
        if key not in self._issues:
            self._issues[key] = self.j.get(f"/issue/{urllib.parse.quote(key)}", fields="issuetype,project,summary,status")
        return self._issues[key]

    def link_types(self):
        if self._links is None:
            self._links = self.j.get("/issueLinkType").get("issueLinkTypes", [])
        return self._links

    def link_type(self, phrase):
        """'blocks' -> (link type, outward?), from a link type's outward or inward wording, or its name."""
        phrase = str(phrase).strip().lower()
        for t in self.link_types():
            if t["outward"].lower() == phrase:
                return t, True
            if t["inward"].lower() == phrase:
                return t, False
        for t in self.link_types():
            if t["name"].lower() == phrase:
                return t, True
        return None, None

    def statuses(self, space):
        """Work type name (lowercase) -> its workflow's status names."""
        if space not in self._statuses:
            try:
                rows = self.j.get(f"/project/{urllib.parse.quote(space)}/statuses")
            except JiraError:
                rows = []
            self._statuses[space] = {r["name"].lower(): [s["name"] for s in r.get("statuses", [])] for r in rows}
        return self._statuses[space]

    def sprints(self, space):
        """Active and future sprints on the space's Scrum boards, by lowercase name."""
        if space not in self._sprints:
            found = {}
            try:
                boards = self.j.call("GET", "/board", query={"projectKeyOrId": space, "maxResults": 50}, api="agile").get("values", [])
            except JiraError:
                boards = []
            for b in boards:
                if b.get("type") != "scrum":
                    continue
                try:
                    page = self.j.call("GET", f"/board/{b['id']}/sprint", query={"state": "active,future", "maxResults": 50}, api="agile")
                except JiraError:
                    continue
                for s in page.get("values", []):
                    found.setdefault(s["name"].lower(), s)
            self._sprints[space] = found
        return self._sprints[space]


def person_id(who):
    """A people-directory key, or an account ID as is; None when neither."""
    who = str(who).strip().lstrip("@")
    p = people().get(who)
    if p:
        return p["id"]
    if re.fullmatch(r"[0-9a-f]{24}|\d+:[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", who):
        return who
    return None


def match_allowed(m, value):
    want = str(value).strip().lower()
    for av in m["allowed"] or []:
        if want in {str(av.get(k)).lower() for k in ("value", "name", "key", "id") if av.get(k) is not None}:
            return av
    return None


def as_list(value):
    return value if isinstance(value, list) else [v.strip() for v in str(value).split(",") if v.strip()]


def convert(M, m, value, where, P, space):
    """A plan value in human terms -> what Jira's API expects for this field. Problems go in P."""
    k, name = kind(m), m["name"]

    def bad(msg):
        P.add(where, f"{name}: {msg}")
        return None

    def pick(v):
        av = match_allowed(m, v)
        if av:
            return {"id": str(av["id"])}
        if m["allowed"]:
            vals = [label(a) for a in m["allowed"]]
            return bad(f"'{v}' isn't one of: " + ", ".join(vals[:30]) + (" …" if len(vals) > 30 else ""))
        by = "value" if m["schema"].get("type") == "option" or m["schema"].get("items") == "option" else "name"
        return {by: str(v)}

    def who(v):
        a = person_id(v)
        return {"accountId": a} if a else bad(f"'{v}' isn't in {PEOPLE} with an ids.jira account ID (find it with `users`)")

    if k == "long text":
        return md_to_adf(value)
    if k in ("text", "url"):
        if isinstance(value, (dict, list)):
            return bad("expects plain text")
        s = str(value).strip()
        if m["id"] == "summary" and len(s) > 255:
            return bad(f"is {len(s)} characters; Jira allows 255")
        return s
    if k == "number":
        try:
            n = float(value)
        except (TypeError, ValueError):
            n = float("nan")
        if isinstance(value, bool) or n != n or n in (float("inf"), float("-inf")):
            return bad(f"expects a number, not '{value}'")
        return int(n) if n.is_integer() else n
    if k == "date":
        s = str(value)[:10]
        return s if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s) else bad(f"expects a date as YYYY-MM-DD, not '{value}'")
    if k == "datetime":
        if isinstance(value, datetime.datetime):
            d = value
        else:
            try:
                d = datetime.datetime.fromisoformat(re.sub(r"Z$", "+00:00", str(value).strip()))
            except ValueError:
                return bad(f"expects a date and time as YYYY-MM-DD HH:MM, not '{value}'")
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        return d.strftime("%Y-%m-%dT%H:%M:%S.000%z")
    if k in ("option", "version"):
        return pick(value)
    if k in ("options", "versions", "components"):
        out = [pick(v) for v in as_list(value)]
        return None if None in out else out
    if k == "option / child":
        parts = value if isinstance(value, list) else [p.strip() for p in str(value).split("/", 1)]
        if not m["allowed"]:
            res = {"value": str(parts[0])}
            if len(parts) > 1:
                res["child"] = {"value": str(parts[1])}
            return res
        parent = match_allowed(m, parts[0])
        if not parent:
            return bad(f"'{parts[0]}' isn't one of: " + ", ".join(label(a) for a in m["allowed"] or []))
        res = {"id": str(parent["id"])}
        if len(parts) > 1:
            child = match_allowed({"allowed": parent.get("children")}, parts[1])
            if not child:
                return bad(f"'{parts[1]}' isn't under '{label(parent)}': " + ", ".join(label(c) for c in parent.get("children") or []))
            res["child"] = {"id": str(child["id"])}
        return res
    if k == "person":
        return who(value)
    if k == "people":
        out = [who(v) for v in as_list(value)]
        return None if None in out else out
    if k == "labels":
        vals = [str(v) for v in as_list(value)]
        spaced = [v for v in vals if re.search(r"\s", v)]
        return bad(f"labels can't contain spaces: {spaced}") if spaced else vals
    if k == "sprint":
        s = M.sprints(space).get(str(value).strip().lower())
        if not s and not isinstance(value, bool) and str(value).strip().isdigit():
            return int(value)  # a sprint ID
        if not s:
            names = [x["name"] for x in M.sprints(space).values()]
            return bad(f"no active or future sprint named '{value}'" + (f"; there are: {', '.join(names)}" if names else ""))
        return s["id"]
    if k == "group":
        return {"name": str(value).strip()}
    if k == "groups":
        return [{"name": v} for v in as_list(value)]
    if k == "team":
        v = str(value).strip()
        return v if re.fullmatch(r"[0-9a-fA-F-]{36}", v) else bad(f"expects the team's ID from Jira, not '{v}'")
    return value  # anything else goes to Jira as written


def describe(m):
    vals = [label(a) for a in m["allowed"] or []]
    return f"{m['name']} ({kind(m)}" + (f": {', '.join(vals[:15])}" if vals else "") + ")"


class Problems(list):
    def add(self, where, msg):
        self.append((where, msg))


# ---------------------------------------------------------------- writes

class Record:
    """PLAN.created.json: what a plan has already done, so a rerun skips it."""

    def __init__(self, plan_path, dry):
        self.path = re.sub(r"\.(ya?ml|json)$", "", plan_path) + ".created.json"
        self.dry = dry
        self.data = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, encoding="utf-8") as f:
                    self.data = json.load(f)
            except (OSError, ValueError) as e:
                fail(f"{self.path} can't be read ({e}). It records what this plan already created; fix or restore it "
                     "before running again, or items will be created twice.")
        self.data.setdefault("items", {})
        self.data.setdefault("done", [])

    def save(self):
        if not self.dry:
            tmp = self.path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
                f.write("\n")
            os.replace(tmp, self.path)


def load_plan(path):
    plan = load_data(path)
    if isinstance(plan, list):
        plan = {"items": plan}
    if not isinstance(plan, dict) or not isinstance(plan.get("items"), list):
        fail(f"{path} needs an `items:` list (format in SKILL.md)")
    return plan


def prepare(plan, M, rec):
    """Check every item against Jira and turn it into API fields. Returns (items, problems); sends nothing."""
    P = Problems()
    items = plan["items"]
    refs = [str(it["ref"]) for it in items if isinstance(it, dict) and it.get("ref")]
    for r in sorted({r for r in refs if refs.count(r) > 1}):
        P.add(r, "this ref is used by more than one item")
    known = set(refs) | set(rec.data["items"])
    levels, out = {}, []

    for n, it in enumerate(items, 1):
        if not isinstance(it, dict):
            P.add(f"item {n}", "isn't a mapping of keys and values")
            continue
        name = str(it.get("ref") or it.get("key") or f"item {n}")
        x = {"it": it, "name": name, "creating": not it.get("key"), "fields": {}, "after": {}, "shown": []}
        if it.get("key") and it.get("ref"):
            P.add(name, "has both `key` (update an item) and `ref` (create one); keep one")
            continue
        if x["creating"] and not it.get("ref"):
            P.add(name, "a new item needs a `ref`, so a rerun knows it was already created")
            continue
        if it.get("ref"):
            levels[str(it["ref"])] = None  # replaced by its level once its type is known

        if x["creating"]:
            space = str(it.get("space") or plan.get("space") or "")
            if not space:
                P.add(name, "has no space: set `space:` on the plan or the item")
                continue
            try:
                t = M.type(space, it.get("type"))
            except JiraError as e:
                P.add(name, f"space {space} can't be read: {e.detail}")
                continue
            if not t:
                P.add(name, f"work type '{it.get('type')}' isn't in {space}; it has " + ", ".join(x2["name"] for x2 in M.types(space)))
                continue
            avail = M.create_fields(space, t)
            x["fields"].update(project={"key": space}, issuetype={"id": str(t["id"])})
        else:
            key = str(it["key"])
            if not KEY_RE.fullmatch(key):
                P.add(name, "`key` should be a work item key like SPACE-12")
                continue
            try:
                issue = M.issue(key)
                avail = M.edit_fields(key)
            except JiraError as e:
                P.add(name, f"can't be read in Jira: {e.detail}")
                continue
            space, t = issue["fields"]["project"]["key"], issue["fields"]["issuetype"]
            if it.get("type") and str(it["type"]).strip().lower() != t["name"].lower():
                P.add(name, f"is a {t['name']}; changing a work type isn't supported here, so change it in Jira")
        x.update(space=space, type=t, level=level(t))

        values = {k: v for k, v in it.items() if k not in PLAN_KEYS}
        extra = it.get("fields") or {}
        if not isinstance(extra, dict):
            P.add(name, "`fields:` should be a mapping of field names to values")
            extra = {}
        values.update(extra)
        given = set()
        for k, v in values.items():
            target, found = x["fields"], avail.find(k)
            if not found and x["creating"]:
                found, target = M.all_fields().find(k), x["after"]  # not on the create screen: set right after creating
            if len(found) > 1:
                P.add(name, f"more than one field is named '{k}' ({', '.join(m['id'] for m in found)}); use the field ID")
                continue
            if not found and not x["creating"] and M.all_fields().find(k):
                P.add(name, f"'{k}' can't be edited on {it['key']} (it isn't on the edit screen)")
                continue
            if not found:
                close = difflib.get_close_matches(str(k), avail.names(), 3, 0.6)
                P.add(name, f"{t['name']} in {space} has no field '{k}'" + (f"; did you mean {' or '.join(close)}?" if close else ""))
                continue
            m = found[0]
            if m["id"] in NOT_FIELDS:
                P.add(name, f"'{k}' is set with the plan's own keys (type, parent, links), not as a field")
                continue
            if v is None or v == "" or v == []:
                if not x["creating"] and m["required"]:
                    P.add(name, f"{m['name']} is required, so it can't be cleared")
                elif not x["creating"]:
                    target[m["id"]] = [] if kind(m) in ("options", "people", "versions", "components", "labels", "groups") else None
                    x["shown"].append(f"{m['name']} cleared")
                continue
            given.add(m["id"])  # even if its value is wrong: that problem is reported on its own
            before = len(P)
            val = convert(M, m, v, name, P, space)
            if len(P) == before:
                target[m["id"]] = val
                if target is x["after"]:
                    x["shown"].append(f"{m['name']}={v} (not on the create screen: set after creating, checked by Jira then)")
                elif m["id"] != "summary":
                    x["shown"].append(m["name"] if kind(m) == "long text" else f"{m['name']}={v}")

        if x["creating"]:
            for m in avail.list:
                if m["required"] and not m["default"] and m["id"] not in given and m["id"] not in NOT_FIELDS:
                    P.add(name, f"{t['name']} in {space} requires {describe(m)}; what should it be?")

        p = it.get("parent")
        if p:
            p, plevel = str(p), None
            if p in levels:
                plevel = levels[p]
                if plevel is None:
                    P.add(name, f"parent '{p}' has problems of its own (above); its level can't be checked yet")
            elif p in known and p not in rec.data["items"]:
                P.add(name, f"parent '{p}' comes later in the plan; move it above this item")
            elif p in rec.data["items"] or KEY_RE.fullmatch(p):
                pkey = rec.data["items"][p]["key"] if p in rec.data["items"] else p
                try:
                    plevel = level(M.issue(pkey)["fields"]["issuetype"])
                except JiraError as e:
                    P.add(name, f"parent {pkey} can't be read in Jira: {e.detail}")
            else:
                P.add(name, f"parent '{p}' is neither a work item key nor the ref of an earlier item")
            if plevel is not None and plevel != x["level"] + 1:
                P.add(name, f"{article(t['name'])} {t['name']} (level {x['level']}) belongs under a level {x['level'] + 1} item, "
                            f"but parent '{p}' is level {plevel}")
        elif x["creating"] and x["level"] < 0:
            P.add(name, f"{article(t['name'])} {t['name']} needs a `parent`")

        for link in it.get("links") or []:
            if not isinstance(link, dict) or len(link) != 1:
                P.add(name, "each link is one `phrase: target` pair, such as `blocks: other-ref`")
                continue
            (phrase, target), = link.items()
            if not M.link_type(phrase)[0]:
                P.add(name, f"no link type reads '{phrase}'; Jira has: "
                            + "; ".join(f"{lt['outward']} / {lt['inward']}" for lt in M.link_types()))
            if not (str(target) in known or KEY_RE.fullmatch(str(target))):
                P.add(name, f"link target '{target}' is neither a work item key nor a ref in this plan")

        tr = it.get("transition")
        if tr:
            want = str(tr).strip().lower()
            if x["creating"]:
                names = M.statuses(space).get(t["name"].lower())
                if names and want not in [s.lower() for s in names]:
                    P.add(name, f"{t['name']}'s workflow has no status '{tr}'; it has: {', '.join(names)}")
            elif f"{it['key']} -> {tr}" not in rec.data["done"]:
                ts = get_transitions(M.j, it["key"])
                if not any(want in (x2["name"].lower(), x2["to"]["name"].lower()) for x2 in ts):
                    P.add(name, f"can't move to '{tr}' from its current status; it can move to: "
                                + ", ".join(x2["to"]["name"] for x2 in ts))
        if it.get("ref"):
            levels[str(it["ref"])] = x["level"]
        out.append(x)
    return out, P


def article(word):
    return "an" if word[:1].lower() in "aeiou" else "a"


def report_problems(P):
    print(f"Questions to settle before anything goes to Jira ({len(P)}):")
    for n, (where, msg) in enumerate(P, 1):
        print(f"{n}. {where}: {msg}")
    print("Fix the plan (asking the PM where only they can answer), then run validate again.")
    sys.exit(1)


def summarize(prepared, rec):
    counts = {"create": 0, "update": 0, "links": 0, "moves": 0, "comments": 0}
    for x in prepared:
        it, f = x["it"], x["fields"]
        extras = x["shown"]
        if x["creating"] and str(it["ref"]) in rec.data["items"]:
            line = f"done {x['name']}: already created as {rec.data['items'][str(it['ref'])]['key']}"
        elif x["creating"]:
            counts["create"] += 1
            line = f"create {x['name']}: {x['type']['name']} \"{f.get('summary', '')}\""
        else:
            counts["update"] += 1
            line = f"update {x['name']}: {x['type']['name']}"
        if it.get("parent"):
            line += f", under {it['parent']}"
        if extras:
            line += "; " + ", ".join(extras)
        for link in it.get("links") or []:
            (phrase, target), = link.items()
            line += f"; {phrase} {target}"
            counts["links"] += 1
        if it.get("transition"):
            line += f"; move to {it['transition']}"
            counts["moves"] += 1
        if it.get("comment"):
            line += "; comment"
            counts["comments"] += 1
        print(line)
    print("ok: " + ", ".join(f"{v} {k}" if k not in ("create", "update") else f"{v} to {k}" for k, v in counts.items() if v))


def make_link(j, M, a, phrase, b):
    """Create 'a <phrase> b' and confirm Jira reads it the same way."""
    t, outward = M.link_type(phrase)
    if not t:
        fail(f"no link type reads '{phrase}'; Jira has: " + "; ".join(f"{x['outward']} / {x['inward']}" for x in M.link_types()))
    src, dst = (a, b) if outward else (b, a)
    text = f"{src} {t['outward']} {dst}"
    # Jira reads a link as "inwardIssue <outward wording> outwardIssue": inwardIssue blocks outwardIssue.
    body = {"type": {"name": t["name"]}, "inwardIssue": {"key": src}, "outwardIssue": {"key": dst}}
    if j.write("POST", "/issueLink", body, f"link: {text}") is None and j.dry:
        return
    links = j.get(f"/issue/{urllib.parse.quote(src)}", fields="issuelinks")["fields"].get("issuelinks", [])
    for l in links:
        if l["type"]["name"] == t["name"] and (l.get("outwardIssue") or {}).get("key") == dst:
            print(f"linked: {text}")
            return
    for l in links:
        if l["type"]["name"] == t["name"] and (l.get("inwardIssue") or {}).get("key") == dst:
            print(f"WARNING: Jira shows {src} {t['inward']} {dst}, the reverse of what was asked. Fix the link in Jira "
                  "and report this to Lobot.", file=sys.stderr)
            return
    print(f"linked: {text} (not yet visible on {src}; check it in Jira)")


def link_text(M, a, phrase, b):
    t, outward = M.link_type(phrase)
    src, dst = (a, b) if outward else (b, a)
    return f"{src} {t['outward']} {dst}"


def do_transition(j, key, target):
    if j.dry and key.startswith("<"):
        print(f"--- transition: {key} -> {target}")
        return
    ts = get_transitions(j, key)
    want = str(target).strip().lower()
    t = next((x for x in ts if x["to"]["name"].lower() == want), None) or next((x for x in ts if x["name"].lower() == want), None)
    if not t:
        fail(f"{key} can't move to '{target}' from its current status; available: "
             + ", ".join(f"{x['name']} (-> {x['to']['name']})" for x in ts))
    if j.write("POST", f"/issue/{urllib.parse.quote(key)}/transitions", {"transition": {"id": t["id"]}},
               f"transition: {key} -> {t['to']['name']}") is None and j.dry:
        return
    print(f"moved: {key} -> {t['to']['name']}")


def do_comment(j, key, markdown):
    res = j.write("POST", f"/issue/{urllib.parse.quote(key)}/comment", {"body": md_to_adf(markdown)}, f"comment on {key}")
    if res is not None:
        print(f"commented: {j.url(key)}?focusedCommentId={res.get('id')}")


def check_stamp(plan, path):
    if not (plan.get("approved_by") and plan.get("approved_at")):
        fail(f"{path} has no approval stamp (approved_by, approved_at). "
             "Show it to the PM and stamp it on their approval (.ai/general/human-review.md), or run with --dry-run.")


def cmd_validate(args):
    plan = load_plan(args.plan)
    j = Jira()
    M = Meta(j)
    prepared, P = prepare(plan, M, Record(args.plan, True))
    if P:
        report_problems(P)
    summarize(prepared, Record(args.plan, True))


def cmd_apply(args):
    plan = load_plan(args.plan)
    if not args.dry_run:
        check_stamp(plan, args.plan)
    j = Jira(dry=args.dry_run)
    M = Meta(j)
    rec = Record(args.plan, args.dry_run)
    prepared, P = prepare(plan, M, rec)
    if P:
        report_problems(P)
    try:
        apply_items(j, M, rec, prepared)
    except JiraError as e:
        fail(f"{e} (at {current[0]}). Nothing after it was sent. Fix the plan and run apply again: "
             f"what {rec.path} records as done is skipped.", 2)


current = ["start"]


def apply_items(j, M, rec, prepared):
    def resolve(x):
        x = str(x)
        if x in rec.data["items"]:
            return rec.data["items"][x]["key"]
        return x if KEY_RE.fullmatch(x) else f"<{x}>"  # a placeholder only happens in a dry run

    created = updated = 0
    for x in prepared:
        it, fields = x["it"], x["fields"]
        current[0] = x["name"]
        if it.get("parent"):
            fields["parent"] = {"key": resolve(it["parent"])}
        if x["creating"]:
            ref = str(it["ref"])
            if ref in rec.data["items"]:
                key = rec.data["items"][ref]["key"]
                print(f"skip: {ref} already created as {key}")
            else:
                res = j.write("POST", "/issue", {"fields": fields}, f"create {ref}")
                key = f"<{ref}>" if res is None else res["key"]
                if res is not None:
                    rec.data["items"][ref] = {"key": key, "url": j.url(key)}
                    rec.save()
                    print(f"created: {key} {fields['summary']}  {j.url(key)}")
                    created += 1
            done = f"{ref}: fields set after creating"
            if x["after"] and done not in rec.data["done"]:  # fields that aren't on the create screen
                j.write("PUT", f"/issue/{urllib.parse.quote(key)}", {"fields": x["after"]}, f"set on {ref} after creating it")
                rec.data["done"].append(done)
                rec.save()
        else:
            key = it["key"]
            if fields:
                j.write("PUT", f"/issue/{urllib.parse.quote(key)}", {"fields": fields}, f"update {key}")
                if not j.dry:
                    print(f"updated: {key}  {j.url(key)}")
                    updated += 1
        x["key"] = key

    # Links, moves, and comments after every item exists, so links can point forward.
    for x in prepared:
        it, key = x["it"], x["key"]
        current[0] = x["name"]
        for link in it.get("links") or []:
            (phrase, target), = link.items()
            other = resolve(target)
            done = link_text(M, key, phrase, other)
            if done in rec.data["done"]:
                print(f"skip: {done}")
                continue
            make_link(j, M, key, phrase, other)
            rec.data["done"].append(done)
            rec.save()
        if it.get("transition"):
            done = f"{key} -> {it['transition']}"
            if done in rec.data["done"]:
                print(f"skip: {done}")
            else:
                do_transition(j, key, it["transition"])
                rec.data["done"].append(done)
                rec.save()
        if it.get("comment"):
            done = f"comment {key} " + hashlib.sha1(str(it["comment"]).encode()).hexdigest()[:10]
            if done in rec.data["done"]:
                print(f"skip: comment on {key}")
            else:
                do_comment(j, key, it["comment"])
                rec.data["done"].append(done)
                rec.save()
    if not j.dry:
        print(f"done: {created} created, {updated} updated. Record: {rec.path}")


def search(j, jql, fields, limit):
    issues, token = [], None
    while len(issues) < limit:
        body = {"jql": jql, "fields": fields, "maxResults": min(100, limit - len(issues))}
        if token:
            body["nextPageToken"] = token
        page = j.call("POST", "/search/jql", body)
        issues += page.get("issues", [])
        token = page.get("nextPageToken")
        if page.get("isLast", True) or not token or not page.get("issues"):
            break
    return issues, bool(token)


def cmd_structure(args):
    """Write the space's structure for Pepper: work types, the fields a plan can set and their values, and more."""
    try:
        import yaml
    except ImportError:
        fail("PyYAML is required to write the structure file (pip install pyyaml)")
    j = Jira()
    M = Meta(j)
    space = args.space
    proj = j.get(f"/project/{urllib.parse.quote(space)}")
    statuses = M.statuses(space)
    types_out, fields = [], {}
    for t in sorted(M.types(space), key=lambda t: (-level(t), t["name"])):
        avail = M.create_fields(space, t)
        required, optional = [], []
        for m in sorted(avail.list, key=lambda m: (m["name"] != "Summary", m["name"].lower())):
            if m["id"] in NOT_FIELDS:
                continue
            name = m["name"] if len(avail.find(m["name"])) == 1 else f"{m['name']} ({m['id']})"
            (required if m["required"] and not m["default"] else optional).append(name)
            k = kind(m)
            if k == "option / child":
                vals = [f"{label(a)} / {label(c)}" for a in m["allowed"] or [] for c in a.get("children") or []] \
                    or [label(a) for a in m["allowed"] or []]
            elif k in ("person", "people"):
                vals = []
            else:
                vals = [label(a) for a in m["allowed"] or []]
            f = fields.setdefault(name, {"kind": k})
            if name != m["name"] or k == "other":
                f["id"] = m["id"]  # a shared name, or a value written as Jira expects: name it by ID
            if vals:
                if "values" not in f:
                    f["values"] = vals
                elif f["values"] != vals:  # a field configured differently for this work type
                    f.setdefault("values_by_type", {})[t["name"]] = vals
        row = {"name": t["name"], "level": level(t)}
        if statuses.get(t["name"].lower()):
            row["statuses"] = statuses[t["name"].lower()]
        row["required"], row["optional"] = required, optional
        types_out.append(row)

    parents = [t["name"] for t in M.types(space) if level(t) >= 1]
    open_parents = []
    if parents:
        jql = (f'project = "{space}" AND issuetype in ({", ".join(json.dumps(p) for p in parents)}) '
               "AND statusCategory != Done ORDER BY created DESC")
        found, more = search(j, jql, ["summary", "issuetype"], 200)
        open_parents = [{"key": i["key"], "type": i["fields"]["issuetype"]["name"], "summary": i["fields"]["summary"]} for i in found]

    data = {
        "space": space,
        "name": html.unescape(proj.get("name") or ""),
        "managed": {"classic": "company-managed", "next-gen": "team-managed"}.get(proj.get("style"), proj.get("style")),
        "site": j.site,
        "work_types": types_out,
        "fields": dict(sorted(fields.items(), key=lambda kv: kv[0].lower())),
        "links": [f"{lt['outward']} / {lt['inward']}" for lt in M.link_types()],
        "sprints": [{"name": s["name"], "state": s.get("state")} for s in M.sprints(space).values()],
        "open_parents": open_parents,
    }
    header = (f"# Jira structure of {space}, generated {time.strftime('%Y-%m-%d')} by jira.py from {j.site}. Don't edit; regenerate:\n"
              f"#   python3 .ai/general/skills/jira/jira.py structure {space}\n"
              "# Plan files name fields and values exactly as they appear here (jira skill, \"Writing work items\").\n"
              "# level: 1 epic, 0 standard, -1 subtask; an item's parent is one level up. Kinds and values for every field are under fields.\n")
    text = header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=120, default_flow_style=None)
    if args.out == "-":
        print(text)
        return
    out = args.out or f".ai/project/jira/{space}.yaml"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"wrote {out}: {len(types_out)} work types, {len(open_parents)} open epics or parents, {len(data['sprints'])} sprints")


def cmd_link(args):
    j = Jira(dry=args.dry_run)
    make_link(j, Meta(j), args.a, args.phrase, args.b)


def cmd_transition(args):
    j = Jira(dry=args.dry_run)
    do_transition(j, args.key, args.status)


def cmd_comment(args):
    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        fail(f"can't read {args.file}: {e.strerror}")
    text = re.sub(r"\A---\n.*?\n---\n", "", text, flags=re.S)  # drop a draft's frontmatter
    j = Jira(dry=args.dry_run)
    do_comment(j, args.key, text)


def cmd_adf(args):
    """Offline: show the ADF a markdown file becomes, or (with --back) the markdown it reads back as."""
    try:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        fail(f"can't read {args.file}: {e.strerror}")
    doc = md_to_adf(text)
    print(adf_to_md(doc) if args.back else json.dumps(doc, indent=2, ensure_ascii=False))


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Read and write Jira Cloud work items.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, *params, json_flag=True, dry=False):
        p = sub.add_parser(name)
        for spec in params:
            p.add_argument(*spec[0], **spec[1])
        if json_flag:
            p.add_argument("--json", action="store_true")
        if dry:
            p.add_argument("--dry-run", action="store_true")
        p.set_defaults(fn=fn)
        return p

    add("check", cmd_check, json_flag=False)
    add("setup", cmd_setup, (["--site"], {}), (["--email"], {}), json_flag=False)
    add("spaces", cmd_spaces)
    add("types", cmd_types, (["space"], {}))
    add("fields", cmd_fields, (["space"], {}), (["type"], {}))
    add("structure", cmd_structure, (["space"], {}), (["--out"], {}), json_flag=False)
    add("validate", cmd_validate, (["plan"], {}), json_flag=False)
    add("link-types", cmd_link_types)
    add("users", cmd_users, (["query"], {}))
    add("search", cmd_search, (["jql"], {}), (["--limit"], {"type": int, "default": 50}), (["--fields"], {}))
    add("view", cmd_view, (["key"], {}), (["--comments"], {"action": "store_true"}))
    add("transitions", cmd_transitions, (["key"], {}))
    add("apply", cmd_apply, (["plan"], {}), json_flag=False, dry=True)
    add("link", cmd_link, (["a"], {}), (["phrase"], {}), (["b"], {}), json_flag=False, dry=True)
    add("transition", cmd_transition, (["key"], {}), (["status"], {}), json_flag=False, dry=True)
    add("comment", cmd_comment, (["key"], {}), (["file"], {}), json_flag=False, dry=True)
    add("adf", cmd_adf, (["file"], {}), (["--back"], {"action": "store_true"}), json_flag=False)
    args = ap.parse_args()
    run(lambda: args.fn(args))


if __name__ == "__main__":
    main()
