#!/usr/bin/env bash
# Reports where this Project Brain stands with version control and GitHub, so the project-setup
# skill can pick the next step. Changes nothing in the Project Brain or on GitHub, and never prints a
# token (like gh-env.sh, it may install gh into ~/.local/gh if it's missing).
#   bash .ai/general/skills/project-setup/brain-state.sh
# Run it in the shell that runs git and gh. Prints one "key: value" line per fact; the last line is
#   state: no-git | no-remote | no-login | no-access | behind | unsaved | saved
set -u
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../../.." && pwd)"
# In a Lobot checkout (maintainers), this script sits one level shallower, in engine/skills/project-setup.
[ -f "$here/../../../tools/lobot.js" ] && root="$(cd "$here/../../.." && pwd)"
cd "$root" || exit 1
say() { printf '%s: %s\n' "$1" "$2"; }
redact() { sed 's#://[^@/]*@#://***@#; s#gh[pousr]_[A-Za-z0-9_]*#***#g; s#github_pat_[A-Za-z0-9_]*#***#g'; }
days_left() { # YYYY-MM-DD -> whole days from now (GNU or BSD date)
  local t n
  t="$(date -d "$1" +%s 2>/dev/null || date -j -f %Y-%m-%d "$1" +%s 2>/dev/null)" || return 1
  n="$(date -d "$(date +%F)" +%s 2>/dev/null || date -j -f %Y-%m-%d "$(date +%F)" +%s 2>/dev/null)" || return 1
  echo $(( (t - n) / 86400 ))
}
ORG="Lullabot"

# Lobot, and the repository name the convention gives this project: the code repository's name plus
# -pm, or the project key in lowercase plus -pm when no code repository can be found.
ver="$(sed -n 's/.*"lobot_version": *"\([^"]*\)".*/\1/p' .ai/general/.lobot-version 2>/dev/null | head -1)"
say lobot "${ver:-not installed}"
slugify() { printf '%s' "$1" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9._-' '-' | sed 's/^-*//;s/-*$//'; }
# The code repository: repo/'s own remote first, then the first GitHub link in the project's GitHub config.
code="$(git -C repo remote get-url origin 2>/dev/null | sed -n 's#.*github\.com[:/]\([^/]*/[^/]*\)$#\1#p' | sed 's#\.git$##')"
from="repo/"
if [ -z "$code" ]; then
  code="$(grep -oE 'github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+' .ai/project/github.md 2>/dev/null | sed 's#^github\.com/##; s#\.git$##' | grep -vE '^(orgs|users|enterprises)/|-pm$' | head -1)"
  from=".ai/project/github.md"
fi
name=""
if [ -n "$code" ]; then
  say code-repo "$code (from $from)"
  name="$(slugify "${code#*/}")-pm"; basis="code repository"
else
  say code-repo "not found in repo/ or .ai/project/github.md"
  key="$(sed -n '1s/^# \(.*\) Project Brain.*/\1/p' CLAUDE.md 2>/dev/null)"
  [ -n "$key" ] && name="$(slugify "$key")-pm"; basis="project key, since no code repository was found"
fi

# Git.
state="no-git"; origin=""; commits=no; dirty=0
top="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [ -n "$top" ] && [ "$top" -ef "$root" ]; then
  say git "repository, branch $(git symbolic-ref --short -q HEAD || echo '(none)')"
  git rev-parse --verify -q HEAD >/dev/null 2>&1 && commits=yes
  say commits "$commits"
  dirty="$(git status --porcelain | wc -l | tr -d ' ')"
  say uncommitted-changes "$dirty"
  if git check-ignore -q --no-index .env; then say env-ignored yes; else say env-ignored "NO: .env would be committed"; fi
  origin="$(git remote get-url origin 2>/dev/null || true)"
  say origin "$(printf '%s' "${origin:-none}" | redact)"
  if [ -z "$origin" ]; then state="no-remote"; else state="no-login"; fi
else
  say git "not a repository (or inside another one)"
fi
if [ -z "$origin" ]; then
  if [ -n "$name" ]; then say suggested-repo "$ORG/$name (from the $basis)"; else say suggested-repo "unknown (no code repository or project key found; ask the PM)"; fi
fi

# The token's expiry, if the PM recorded it beside the token. Only that line of .env is read.
exp="$(sed -n 's/^GH_TOKEN_EXPIRES=//p' .env 2>/dev/null | tail -1 | tr -d '"'"'"' \r')"
if [ -n "$exp" ]; then
  left="$(days_left "$exp" || true)"
  say token-expires "$exp${left:+ (in $left days)}"
fi

# GitHub.
# shellcheck source=/dev/null
source "$here/../github/gh-env.sh" 2>/dev/null
if ! command -v gh >/dev/null 2>&1; then
  say gh "not installed"
elif ! gh auth status >/dev/null 2>&1; then
  say gh "no working login"
else
  login="$(gh api user --jq .login 2>/dev/null || true)"
  say gh "ok as ${login:-?}"
  case "${GH_TOKEN:-}" in
    ghp_*) kind="classic token" ;;
    github_pat_*) kind="fine-grained token" ;;
    "") kind="gh login (no token variable)" ;;
    *) kind="other" ;;
  esac
  say token-kind "$kind"
  say org-role "$(gh api "user/memberships/orgs/$ORG" --jq '.role + " (" + .state + ")"' 2>/dev/null || echo 'unknown (not a member, or the token cannot see it)')"

  if [ -z "$origin" ] && [ -n "$name" ]; then
    out="$(gh api "repos/$ORG/$name" --jq '.private' 2>&1 || true)"
    case "$out" in
      true) say suggested-repo-exists "yes, private" ;;
      false) say suggested-repo-exists "yes, PUBLIC" ;;
      *"Not Found"*) say suggested-repo-exists "no (or not visible to this token)" ;;
      *) say suggested-repo-exists "unknown: $(printf '%s' "$out" | head -1 | redact)" ;;
    esac
  fi

  # Compare with GitHub without changing anything: ls-remote only reads, and a dry-run push sends nothing.
  if [ -n "$origin" ]; then
    https="$(printf '%s' "$origin" | sed 's#^git@github.com:#https://github.com/#; s#^ssh://git@github.com/#https://github.com/#')"
    g() { git -c credential.helper= -c credential.helper='!gh auth git-credential' "$@"; }
    if out="$(g ls-remote "$https" refs/heads/main 2>&1)"; then
      rsha="${out%%[[:space:]]*}"
      if [ -z "$rsha" ]; then remote="empty"
      elif [ "$commits" = yes ] && [ "$rsha" = "$(git rev-parse HEAD)" ]; then remote="same as this copy"
      elif [ "$commits" = yes ] && git merge-base --is-ancestor "$rsha" HEAD 2>/dev/null; then remote="behind this copy (unpushed saves here)"
      else remote="has saves this copy doesn't"; fi
    else
      remote="unreachable: $(printf '%s' "$out" | grep -iE 'denied|403|404|not found|forbidden|fatal|error' | head -1 | redact)"
    fi
    say remote "$remote"
    # Write access, checked against a branch that doesn't exist so the answer is about access only.
    if [ "$commits" = yes ] && [ "${remote#unreachable}" = "$remote" ]; then
      if out="$(g push --dry-run "$https" HEAD:refs/heads/brain-state-check 2>&1)"; then push=ok
      else push="failed: $(printf '%s' "$out" | grep -iE 'denied|403|forbidden|not found|fatal|error' | head -1 | redact)"; fi
      say push-check "$push"
    fi
    case "$remote" in
      unreachable*) state="no-access" ;;
      *) if [ "${push:-ok}" != ok ]; then state="no-access"
         elif [ "$remote" = "has saves this copy doesn't" ]; then state="behind"
         elif [ "$remote" = "empty" ] || [ "$dirty" != 0 ] || [ "${remote#behind}" != "$remote" ]; then state="unsaved"
         else state="saved"; fi ;;
    esac
  fi
fi
say state "$state"
