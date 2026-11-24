#!/usr/bin/env python3
"""Tell whether a newer Lobot release is out, without changing anything.

The lobot skill runs this on the PM's first session of the day, when the
review desk (the dashboard) is refreshed, and in the scheduled cleanup.
It is deliberately much lighter than `npx github:Lullabot/lobot status`,
which downloads the whole package: it reads the installed version from
`.ai/general/.lobot-version` and asks GitHub for the release tags with one
`git ls-remote` call. That needs no login, no Node, and no PyYAML, and it
sends nothing about the project.

Run it from the Project Brain root:

    python3 .ai/general/skills/lobot/version_check.py

It always exits 0 and prints `key: value` lines for the assistant to read:

    installed: 0.42.2
    updated: 2026-11-12 (12 days ago)
    latest: 0.43.0
    state: behind

`state` is one of:
    behind   a newer release is out; tell the PM
    current  nothing to say
    ahead    the installed copy is newer than any release (a test checkout)
    unknown  the check couldn't be made (`reason:` says why); say nothing
             and try again next time
"""

import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/Lullabot/lobot.git"
TIMEOUT_SECONDS = 15

# This file lives at .ai/general/skills/lobot/version_check.py, so the
# stamp is two folders up, at .ai/general/.lobot-version.
STAMP = Path(__file__).resolve().parents[2] / ".lobot-version"


def main():
    installed, updated, problem = read_stamp(STAMP)
    if problem:
        report(installed, updated, None, "unknown", problem)
        return
    latest, problem = latest_release(REPO_URL)
    if problem:
        report(installed, updated, None, "unknown", problem)
        return
    report(installed, updated, latest, compare(installed, latest), None)


def read_stamp(path):
    """Return (installed version, update date, problem) from the stamp file.

    The stamp is JSON written by the Lobot tool on install and update.
    """
    try:
        stamp = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, None, f"no {path.name} (is Lobot installed here?)"
    except (OSError, ValueError) as err:
        return None, None, f"can't read {path.name}: {err}"
    version = stamp.get("lobot_version")
    if not parse_version(version):
        return None, None, f"{path.name} has no usable lobot_version"
    return version, stamp.get("updated"), None


def latest_release(url):
    """Return (highest released version, problem) from the repository's tags.

    Every release is tagged vX.Y.Z by the release pipeline, so the highest
    such tag is the latest release.
    """
    # GIT_TERMINAL_PROMPT=0 makes git fail instead of stopping to ask for a
    # username if GitHub ever answers as though a login were needed; an
    # unattended run (the scheduled cleanup) must never hang on a prompt.
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    try:
        result = subprocess.run(
            ["git", "ls-remote", "--tags", "--refs", url, "v*"],
            capture_output=True, text=True, timeout=TIMEOUT_SECONDS, env=env,
        )
    except FileNotFoundError:
        return None, "git isn't installed here"
    except subprocess.TimeoutExpired:
        return None, f"GitHub didn't answer within {TIMEOUT_SECONDS} seconds"
    if result.returncode != 0:
        lines = result.stderr.strip().splitlines()
        return None, "git ls-remote failed: " + (lines[-1] if lines else "no message")

    # Each output line is "<sha>\trefs/tags/vX.Y.Z"; keep only the version.
    versions = [line.rsplit("/v", 1)[-1] for line in result.stdout.splitlines()]
    versions = [v for v in versions if parse_version(v)]
    if not versions:
        return None, "no release tags found"
    return max(versions, key=parse_version), None


def parse_version(text):
    """Turn "0.43.0" into (0, 43, 0) so versions compare numerically.

    Comparing the strings would put "0.9.0" after "0.43.0". Anything that
    isn't plain X.Y.Z (a pre-release tag, a missing value) gives None.
    """
    match = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", str(text or ""))
    return tuple(int(part) for part in match.groups()) if match else None


def compare(installed, latest):
    mine, theirs = parse_version(installed), parse_version(latest)
    if mine < theirs:
        return "behind"
    return "ahead" if mine > theirs else "current"


def describe_updated(updated):
    """Render the update date with its age, e.g. "2026-11-12 (12 days ago)"."""
    try:
        day = datetime.date.fromisoformat(str(updated))
    except ValueError:
        return str(updated) if updated else "unknown"
    days = (datetime.date.today() - day).days
    age = "today" if days == 0 else ("1 day ago" if days == 1 else f"{days} days ago")
    return f"{day.isoformat()} ({age})"


def report(installed, updated, latest, state, reason):
    print(f"installed: {installed or 'unknown'}")
    print(f"updated: {describe_updated(updated)}")
    print(f"latest: {latest or 'unknown'}")
    print(f"state: {state}")
    if reason:
        print(f"reason: {reason}")


if __name__ == "__main__":
    main()
    sys.exit(0)
