#!/usr/bin/env python3
"""Run transcript.py prepare on each sample in .github/fixtures/transcript-cleanup/
and compare the turns with its .expected file (turn lines only; the header holds paths).

Usage: python3 .github/scripts/test-transcript.py
Add a case: drop NAME.md (a raw transcript, with made-up names) and NAME.expected
(the T001... lines prepare should write) into the fixtures folder.
"""
import glob
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRIPT = os.path.join(ROOT, "engine", "skills", "transcript-cleanup", "transcript.py")
FIXTURES = os.path.join(ROOT, ".github", "fixtures", "transcript-cleanup")

failed = 0
cases = sorted(glob.glob(os.path.join(FIXTURES, "*.md")))
for raw in cases:
    name = os.path.splitext(os.path.basename(raw))[0]
    with open(os.path.splitext(raw)[0] + ".expected", encoding="utf-8") as f:
        expected = [l for l in f.read().splitlines() if l.strip()]
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "turns.txt")
        run = subprocess.run([sys.executable, SCRIPT, "prepare", raw, "--out", out, "--title", name,
                              "--date", "2026-01-01"], capture_output=True, text=True)
        got = []
        if os.path.exists(out):
            with open(out, encoding="utf-8") as f:
                got = [l for l in f.read().splitlines() if l.startswith("T")]
    if run.returncode == 0 and got == expected and "WARNING" not in run.stdout:
        print("ok    %s" % name)
        continue
    failed += 1
    print("FAIL  %s (exit %d)" % (name, run.returncode))
    print("  output: " + (run.stdout + run.stderr).strip().replace("\n", "\n          "))
    for label, lines in (("expected", expected), ("got", got)):
        print("  %s:" % label)
        for l in lines:
            print("    " + l)

print("%d of %d passed" % (len(cases) - failed, len(cases)))
sys.exit(1 if failed or not cases else 0)
