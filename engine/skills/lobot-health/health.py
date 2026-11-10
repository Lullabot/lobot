#!/usr/bin/env python3
"""Lobot health check: how much context Lobot's instruction files cost, and
where rules are likely to slip (oversized files, long skill descriptions,
broken references, duplicated text, overgrown corrections logs).

Standard library only. Works on a Project Brain or on the Lobot repository:

    python3 .ai/general/skills/lobot-health/health.py            # Project Brain root
    python3 engine/skills/lobot-health/health.py --strict        # Lobot repository (CI)

Exit status: 1 when there are errors (or warnings, with --strict), else 0.
--json prints the findings and measurements as JSON for the assistant.
"""
import argparse
import json
import os
import re
import sys
from itertools import combinations

# Budgets. Token counts are estimates: characters / CHARS_PER_TOKEN.
CHARS_PER_TOKEN = 3.8
BUDGET = {
    # Root CLAUDE.md plus everything it @-imports loads in every session,
    # and again in every agent that reads CLAUDE.md. Includes lobot.md's
    # skill table, which is how assistants without a skill listing find skills.
    "always_loaded_tokens": 3500,
    # A top-level rule file in .ai/general/ or .ai/project/.
    "rule_file_tokens": 2500,
    # An agent definition (its whole system prompt).
    "agent_tokens": 2500,
    # Anthropic's limit for a skill description, and Lobot's target. Claude
    # Code keeps the skill listing to ~1% of the context window and drops the
    # descriptions of the least-used skills first when it overflows.
    "description_max_chars": 1024,
    "description_chars": 300,
    "descriptions_total_chars": 8000,
    # Anthropic: keep SKILL.md under 500 lines; split detail into reference files.
    "skill_lines_max": 500,
    "skill_tokens": 4000,
    # Reference files longer than this need a contents list at the top.
    "reference_toc_lines": 100,
    # A paragraph this long buries the rules inside it.
    "long_line_chars": 700,
    # Rows in an agent's corrections log before its lessons should be folded
    # into the agent or skill they correct.
    "corrections_rows": 30,
    # Shared 12-word runs between two files before they count as duplicates.
    "duplicate_runs": 40,
}
SHINGLE = 12
# Files the tool writes on install, so they exist only in a Project Brain.
INSTALLED_ONLY = {".ai/general/.lobot-version"}
NOT_SKILL_NAMES = {
    "this", "that", "the", "a", "an", "each", "every", "any", "one", "new", "same",
    "full", "general", "project", "named", "own", "its", "their", "record", "other",
    "matching", "relevant", "right", "tracker", "loaded", "whole", "first", "next",
}


def tokens(text):
    return round(len(text) / CHARS_PER_TOKEN)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}, text
    fields, key = {}, None
    for line in m.group(1).split("\n"):
        km = re.match(r"([A-Za-z_-]+):\s*(.*)", line)
        if km:
            key = km.group(1)
            fields[key] = km.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            fields[key] += " " + line.strip()
    for k, v in fields.items():
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            fields[k] = v[1:-1]
    return fields, text[m.end():]


class Check:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        if os.path.isfile(os.path.join(self.root, "engine", "lobot.md")):
            self.mode = "engine"
            self.general = os.path.join(self.root, "engine")
            self.project = None
            self.entry = os.path.join(self.root, "scaffold", "CLAUDE.md")
        elif os.path.isfile(os.path.join(self.root, ".ai", "general", "lobot.md")):
            self.mode = "project"
            self.general = os.path.join(self.root, ".ai", "general")
            self.project = os.path.join(self.root, ".ai", "project")
            self.entry = os.path.join(self.root, "CLAUDE.md")
        else:
            sys.exit("lobot-health: run from a Project Brain root or the Lobot repository")
        self.findings = []
        self.measures = {}

    def rel(self, path):
        return os.path.relpath(path, self.root)

    def add(self, level, area, path, message):
        self.findings.append({"level": level, "area": area,
                              "file": self.rel(path) if path else "", "message": message})

    def resolve(self, ref):
        """Map a path as written inside Lobot's files to a file on disk."""
        if ref.startswith(".ai/general/"):
            return os.path.join(self.general, ref[len(".ai/general/"):])
        return os.path.join(self.root, ref)

    def skill_dirs(self):
        out = {}
        for base in (self.general, self.project):
            d = base and os.path.join(base, "skills")
            if d and os.path.isdir(d):
                for name in sorted(os.listdir(d)):
                    if os.path.isfile(os.path.join(d, name, "SKILL.md")):
                        out[name] = os.path.join(d, name)
        return out

    def md_files(self):
        out = []
        for base in (self.general, self.project):
            if base and os.path.isdir(base):
                for dirpath, _, files in os.walk(base):
                    out += [os.path.join(dirpath, f) for f in files if f.endswith(".md")]
        return sorted(out)

    # Context budget -------------------------------------------------------

    def always_loaded(self):
        seen, total = [], 0

        def load(path, depth=0):
            nonlocal total
            if depth > 4 or path in seen or not os.path.isfile(path):
                return
            seen.append(path)
            text = read(path)
            text_no_comments = re.sub(r"<!--.*?-->", "", text, flags=re.S)
            total += tokens(text_no_comments)
            for ref in re.findall(r"^@(\S+)", text, re.M):
                load(self.resolve(ref) if ref.startswith(".ai/") else
                     os.path.normpath(os.path.join(os.path.dirname(path), ref)), depth + 1)

        load(self.entry)
        self.measures["always_loaded_tokens"] = total
        self.measures["always_loaded_files"] = [self.rel(p) for p in seen]
        if total > BUDGET["always_loaded_tokens"]:
            self.add("warn", "budget", self.entry,
                     f"loads ~{total:,} tokens in every session with its imports "
                     f"(budget {BUDGET['always_loaded_tokens']:,}); move detail to skills or "
                     "reference files read when needed")

    def rule_files(self):
        sizes = {}
        for base in (self.general, self.project):
            if not base or not os.path.isdir(base):
                continue
            for f in sorted(os.listdir(base)):
                p = os.path.join(base, f)
                if f.endswith(".md") and os.path.isfile(p) and f != "lobot.md":
                    t = tokens(read(p))
                    sizes[self.rel(p)] = t
                    if t > BUDGET["rule_file_tokens"]:
                        self.add("warn", "budget", p, f"rule file is ~{t:,} tokens "
                                 f"(budget {BUDGET['rule_file_tokens']:,})")
        self.measures["rule_files_tokens"] = sizes

    # Skills ------------------------------------------------------------------

    def skills(self):
        total_desc = 0
        listing = {}
        for name, d in self.skill_dirs().items():
            path = os.path.join(d, "SKILL.md")
            fm, body = frontmatter(read(path))
            if fm.get("name") != name:
                self.add("error", "skills", path, f"frontmatter name is '{fm.get('name')}', folder is '{name}'")
            desc = fm.get("description", "")
            total_desc += len(desc) + len(name)
            listing[name] = len(desc)
            if not desc:
                self.add("error", "skills", path, "has no description, so it can't be matched to a request")
            elif len(desc) > BUDGET["description_max_chars"]:
                self.add("error", "skills", path, f"description is {len(desc)} chars (limit {BUDGET['description_max_chars']})")
            elif len(desc) > BUDGET["description_chars"]:
                self.add("warn", "skills", path, f"description is {len(desc)} chars (target {BUDGET['description_chars']}); "
                         "lead with what it does and the words a PM would say")
            lines = body.count("\n")
            if lines > BUDGET["skill_lines_max"]:
                self.add("error", "skills", path, f"body is {lines} lines (limit {BUDGET['skill_lines_max']}); split into reference files")
            t = tokens(body)
            if t > BUDGET["skill_tokens"]:
                self.add("warn", "skills", path, f"body is ~{t:,} tokens (budget {BUDGET['skill_tokens']:,}); "
                         "keep the steps and rules, move detail to reference files")
            for dirpath, _, files in os.walk(d):
                for f in files:
                    p = os.path.join(dirpath, f)
                    if f.endswith(".md") and f != "SKILL.md":
                        text = read(p)
                        if text.count("\n") > BUDGET["reference_toc_lines"] and not re.search(r"^#+\s*Contents", text, re.M | re.I):
                            self.add("warn", "skills", p, f"reference file is {text.count(chr(10))} lines with no 'Contents' list at the top")
        self.measures["skill_descriptions_chars"] = listing
        self.measures["skill_listing_chars"] = total_desc
        if total_desc > BUDGET["descriptions_total_chars"]:
            self.add("warn", "budget", None,
                     f"skill names and descriptions total {total_desc:,} chars (budget "
                     f"{BUDGET['descriptions_total_chars']:,}); where the listing has a budget, "
                     "the least-used skills lose their descriptions first")

    def agents(self):
        d = os.path.join(self.general, "agents")
        if not os.path.isdir(d):
            return
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if not f.endswith(".md") or not os.path.isfile(p):
                continue
            fm, _ = frontmatter(read(p))
            if fm.get("name") != f[:-3]:
                self.add("error", "agents", p, f"frontmatter name is '{fm.get('name')}', file is '{f[:-3]}'")
            if not fm.get("description"):
                self.add("error", "agents", p, "has no description, so work can't be routed to it")
            t = tokens(read(p))
            if t > BUDGET["agent_tokens"]:
                self.add("warn", "agents", p, f"definition is ~{t:,} tokens (budget {BUDGET['agent_tokens']:,})")
        for base in (self.general, self.project):
            ad = base and os.path.join(base, "agents")
            if not ad or not os.path.isdir(ad):
                continue
            for name in sorted(os.listdir(ad)):
                p = os.path.join(ad, name, "corrections.md")
                if os.path.isfile(p):
                    rows = len(re.findall(r"^\|\s*\d{4}-\d{2}-\d{2}", read(p), re.M))
                    if rows > BUDGET["corrections_rows"]:
                        self.add("warn", "agents", p, f"{rows} corrections; fold the settled ones into the "
                                 "agent or skill they correct and remove them here")

    # References and wording --------------------------------------------------

    def references(self):
        skills = set(self.skill_dirs())
        for p in self.md_files():
            text = read(p)
            for ref in set(re.findall(r"\.ai/general/[A-Za-z0-9_./-]+", text)):
                ref = ref.rstrip(".")
                if self.mode == "engine" and ref in INSTALLED_ONLY:
                    continue
                if not os.path.exists(self.resolve(ref)):
                    self.add("error", "references", p, f"points to {ref}, which doesn't exist")
            for name in set(re.findall(r"\bthe ([a-z][a-z0-9]*(?:-[a-z0-9]+)*) skill\b", text)):
                if name not in skills and name not in NOT_SKILL_NAMES:
                    self.add("error", "references", p, f"names the {name} skill, which doesn't exist")
            long_lines = [l for l in text.split("\n") if len(l) > BUDGET["long_line_chars"]]
            if long_lines:
                self.add("warn", "wording", p, f"{len(long_lines)} paragraph(s) over {BUDGET['long_line_chars']} chars; "
                         "one rule per line or bullet is easier to follow")
        # Every skill should be reachable from lobot.md, the file loaded every session.
        lobot = read(os.path.join(self.general, "lobot.md"))
        for name in sorted(skills):
            if not re.search(rf"\b{re.escape(name)}\b", lobot):
                self.add("warn", "references", os.path.join(self.general, "lobot.md"),
                         f"doesn't mention the {name} skill, so nothing loaded at start points to it")

    def duplicates(self):
        runs = {}
        for p in self.md_files():
            words = re.findall(r"[a-z0-9'-]+", read(p).lower())
            runs[p] = {" ".join(words[i:i + SHINGLE]) for i in range(len(words) - SHINGLE + 1)}
        pairs = []
        for a, b in combinations(runs, 2):
            n = len(runs[a] & runs[b])
            if n > BUDGET["duplicate_runs"]:
                pairs.append((n, a, b))
        for n, a, b in sorted(pairs, reverse=True):
            self.add("warn", "duplicates", a, f"shares {n} 12-word runs with {self.rel(b)}; "
                     "keep the text in one place and point to it, or the copies will drift apart")

    def project_links(self):
        if self.mode != "project":
            return
        links = os.path.join(self.root, ".claude", "skills")
        for name in self.skill_dirs():
            if not os.path.exists(os.path.join(links, name)):
                self.add("warn", "skills", None, f".claude/skills/{name} is missing; run the lobot skill's link step")

    def run(self):
        for step in (self.always_loaded, self.rule_files, self.skills, self.agents,
                     self.references, self.duplicates, self.project_links):
            step()
        return self


def report(c):
    errors = [f for f in c.findings if f["level"] == "error"]
    warns = [f for f in c.findings if f["level"] == "warn"]
    m = c.measures
    out = [f"lobot-health ({c.mode}): {len(errors)} errors, {len(warns)} warnings",
           f"  always loaded: ~{m['always_loaded_tokens']:,} tokens ({', '.join(m['always_loaded_files'])})",
           f"  rule files: ~{sum(m['rule_files_tokens'].values()):,} tokens in {len(m['rule_files_tokens'])} files",
           f"  skill listing: {m['skill_listing_chars']:,} chars for {len(m['skill_descriptions_chars'])} skills"]
    for level, items in (("ERROR", errors), ("WARN", warns)):
        area = None
        for f in sorted(items, key=lambda x: (x["area"], x["file"])):
            if f["area"] != area:
                area = f["area"]
                out.append(f"{level} {area}")
            out.append(f"  - {f['file'] + ': ' if f['file'] else ''}{f['message']}")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--json", action="store_true", help="print findings and measurements as JSON")
    ap.add_argument("--strict", action="store_true", help="fail on warnings too")
    args = ap.parse_args()
    c = Check(args.root).run()
    if args.json:
        print(json.dumps({"mode": c.mode, "budget": BUDGET, "measures": c.measures,
                          "findings": c.findings}, indent=2))
    else:
        print(report(c))
    levels = {f["level"] for f in c.findings}
    sys.exit(1 if "error" in levels or (args.strict and levels) else 0)


if __name__ == "__main__":
    main()
