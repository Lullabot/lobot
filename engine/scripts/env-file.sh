#!/usr/bin/env bash
# Where this Project Brain lives, and where the PM's token file is. Source it, then:
#   lobot_brain_home ROOT   prints "shared-drive", "synced" (another synced folder), or "local"
#   lobot_env_file ROOT     prints the token file's path
#   lobot_env_note ROOT     prints a warning line when tokens are where they shouldn't be (or nothing)
# A Project Brain kept in a synced shared drive has no .gitignore to keep tokens out: Drive copies
# every file to everyone who can open the drive. So its tokens live in the PM's own
# ~/.lobot/<key>.env instead of .env at the root. Kept in step with env_file.py beside it.

lobot_brain_home() {
  local root="$1"
  if grep -qiE '^- *Home: *shared drive' "$root/.ai/project/brain-home.md" 2>/dev/null; then echo shared-drive; return; fi
  case "$root" in
    *"/Shared drives/"*) echo shared-drive ;;
    */Library/CloudStorage/*|*"Google Drive"*|*/Dropbox/*|*/OneDrive*|*/iCloud*) echo synced ;;
    *) echo local ;;
  esac
}

lobot_key() { # the project key from the root CLAUDE.md ("# KEY Project Brain"), else the folder name
  local root="$1" key
  key="$(sed -n '1s/^# \(.*\) Project Brain.*/\1/p' "$root/CLAUDE.md" 2>/dev/null)"
  [ -z "$key" ] && key="$(basename "$root" | sed 's/^\.//; s/-lobot$//')"
  printf '%s' "$key" | tr 'A-Z' 'a-z' | tr -c 'a-z0-9._-' '-' | sed 's/^-*//;s/-*$//'
}

lobot_home() { # the PM's ~/.lobot; in Cowork it is the connected folder under ~/mnt/
  if [ -d "$HOME/.lobot" ]; then echo "$HOME/.lobot"
  elif [ -d "$HOME/mnt/.lobot" ]; then echo "$HOME/mnt/.lobot"
  else echo "$HOME/.lobot"; fi
}

lobot_env_file() {
  local root="$1"
  if [ -n "${LOBOT_ENV_FILE:-}" ]; then echo "$LOBOT_ENV_FILE"; return; fi
  if [ "$(lobot_brain_home "$root")" != local ]; then
    echo "$(lobot_home)/$(lobot_key "$root").env"
  else
    echo "$root/.env"
  fi
}

lobot_env_note() {
  local root="$1" f
  [ "$(lobot_brain_home "$root")" != local ] || return 0
  f="$(lobot_env_file "$root")"
  if [ -L "$root/.env" ]; then
    echo "The .env link in the Project Brain isn't needed (tokens are read from $f) and Drive may copy what it points to: remove the link."
  elif [ -f "$root/.env" ] && [ "$f" != "$root/.env" ]; then
    echo "STOP: $root/.env is in a synced folder, where everyone with access can read it. Move it to $f and replace the tokens in it (Drive keeps old versions)."
  elif [ -d "$HOME/mnt" ] && [ ! -d "$HOME/mnt/.lobot" ] && [ ! -d "$HOME/.lobot" ]; then
    echo "~/.lobot isn't connected to this session, so the token file can't be kept on the PM's computer. Connect it first (guided-setup skill)."
  fi
}
