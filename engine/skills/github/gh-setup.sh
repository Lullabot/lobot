#!/usr/bin/env bash
# Connects this Project Brain to GitHub for the gh CLI. Safe to run again.
#   bash .ai/general/skills/github/gh-setup.sh
# - Makes sure .env is git-ignored (adds it to .gitignore if not).
# - Installs gh if missing (through gh-env.sh) and checks for a working login.
# - Without a login, creates .env from .env.example (owner-only) with a GH_TOKEN= line.
# Never prints the token. The last line is the result:
#   auth: ok as <login>   token: missing   auth: failed   gh: not installed   ignore: STOP
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../../.." && pwd)"
# In a Lobot checkout (maintainers), this script sits one level shallower, in engine/skills/github.
[ -f "$here/../../../tools/lobot.js" ] && root="$(cd "$here/../../.." && pwd)"
cd "$root" || exit 1
say() { printf '%s: %s\n' "$1" "$2"; }

# 1. Keep .env out of git.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    say ignore "STOP: .env is committed to this repository. Untrack it, and revoke any token it held."
    exit 4
  elif git check-ignore -q --no-index .env; then
    say ignore "yes"
  else
    printf '\n# Local secrets (per-PM tokens). Never commit.\n.env\n' >> .gitignore
    say ignore "added .env to .gitignore (commit this change)"
  fi
else
  say ignore "not a git repository; skipped"
fi

# 2. Install gh if needed and load any existing login or token.
# shellcheck source=/dev/null
source "$here/gh-env.sh" 2>/dev/null
if ! command -v gh >/dev/null 2>&1; then
  say gh "not installed (the download or checksum check failed; run gh-env.sh to see why)"
  exit 1
fi
say gh "$(gh --version | head -1)"

if gh auth status >/dev/null 2>&1; then
  say auth "ok as $(gh api user --jq .login 2>/dev/null || echo '?')"
  exit 0
fi

# 3. No working login: make sure .env is ready for a token.
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
  else
    printf '%s\n' '# Local only; never commit. Each PM uses their own values.' \
      '# GitHub personal access token for gh (classic; scopes: repo, project, read:org).' 'GH_TOKEN=' > .env
  fi
  say env "created .env"
fi
chmod 600 .env 2>/dev/null
grep -q '^GH_TOKEN=' .env || { printf 'GH_TOKEN=\n' >> .env; say env "added a GH_TOKEN= line"; }

if [ -z "${GH_TOKEN:-}" ]; then
  say token "missing: paste it after GH_TOKEN= in $root/.env"
  exit 2
fi
say auth "failed: GitHub rejected the token in .env (expired, missing a scope, or not authorized for the org's SSO)"
exit 3
