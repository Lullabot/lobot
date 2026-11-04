"""Where this Project Brain lives, and where the PM's token file is.

A Project Brain kept in a synced shared drive has no .gitignore to keep tokens
out: Drive copies every file to everyone who can open the drive. So its tokens
live in the PM's own ~/.lobot/<key>.env instead of .env at the root.
Kept in step with env-file.sh beside it.
"""
import os
import re


def brain_home(root):
    """'shared-drive', 'synced' (another synced folder), or 'local'."""
    try:
        with open(os.path.join(root, ".ai", "project", "brain-home.md"), encoding="utf-8") as f:
            if re.search(r"(?im)^- *Home: *shared drive", f.read()):
                return "shared-drive"
    except OSError:
        pass
    path = os.path.abspath(root)
    if "/Shared drives/" in path or "\\Shared drives\\" in path:
        return "shared-drive"
    if re.search(r"/Library/CloudStorage/|Google Drive|[/\\]Dropbox[/\\]|[/\\]OneDrive|[/\\]iCloud", path):
        return "synced"
    return "local"


def project_key(root):
    key = ""
    try:
        with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8") as f:
            m = re.match(r"# (.*) Project Brain", f.readline())
            key = m.group(1) if m else ""
    except OSError:
        pass
    if not key:
        key = re.sub(r"-lobot$", "", os.path.basename(os.path.abspath(root)).lstrip("."))
    return re.sub(r"[^a-z0-9._-]", "-", key.lower()).strip("-")


def lobot_home():
    """The PM's ~/.lobot; in Cowork it is the connected folder under ~/mnt/."""
    for p in (os.path.expanduser("~/.lobot"), os.path.expanduser("~/mnt/.lobot")):
        if os.path.isdir(p):
            return p
    return os.path.expanduser("~/.lobot")


def env_file(root="."):
    if os.environ.get("LOBOT_ENV_FILE"):
        return os.environ["LOBOT_ENV_FILE"]
    if brain_home(root) != "local":
        return os.path.join(lobot_home(), project_key(root) + ".env")
    return os.path.join(os.path.abspath(root), ".env")


def env_note(root="."):
    """A warning when tokens are where they shouldn't be, or ''."""
    if brain_home(root) == "local":
        return ""
    f, stray = env_file(root), os.path.join(os.path.abspath(root), ".env")
    if os.path.islink(stray):
        return (f"The .env link in the Project Brain isn't needed (tokens are read from {f}) and Drive "
                "may copy what it points to: remove the link.")
    if os.path.isfile(stray) and os.path.abspath(f) != stray:
        return (f"STOP: {stray} is in a synced folder, where everyone with access can read it. "
                f"Move it to {f} and replace the tokens in it (Drive keeps old versions).")
    home = os.path.expanduser("~")
    if os.path.isdir(os.path.join(home, "mnt")) and not any(
            os.path.isdir(p) for p in (os.path.join(home, ".lobot"), os.path.join(home, "mnt", ".lobot"))):
        return ("~/.lobot isn't connected to this session, so the token file can't be kept on the PM's "
                "computer. Connect it first (guided-setup skill).")
    return ""
