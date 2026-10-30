#!/usr/bin/env python3
"""Clean a meeting transcript for the Project Brain (transcript-cleanup skill).

Usage:
  python3 transcript.py prepare RAW --out TURNS [--from TEXT]
      Parse a raw transcript into numbered turns: merges back-to-back lines by the same
      speaker, keeps one timestamp per turn, and removes standalone fillers (um, uh, er, ah).
  python3 transcript.py check TURNS EDITS [--show]
      Validate the edits file and print the review list for the PM, the share of words
      removed, and anything in the kept text that looks sensitive.
  python3 transcript.py write TURNS EDITS --out FILE [--reviewed-by NAME] [--force]
      Write the cleaned transcript. Without --reviewed-by it is marked `status: draft`.
  python3 transcript.py verify PATH [PATH...]
      Check cleaned transcripts, or a transcripts folder, before committing.

The model never rewrites the transcript: it only says which turns (or exact passages
inside a turn) to remove, and this script removes them, so every kept word is as recorded.
Exit code 0 = ok (warnings may print), 1 = errors found.
"""
import datetime
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

BANTER = {"small-talk": "small talk", "audio": "audio and setup", "off-topic": "off topic"}
SENSITIVE = {
    "personal": "personal", "health": "health", "hr": "HR", "other-client": "other client",
    "credential": "credential", "internal": "internal",
}
KINDS = {**BANTER, **SENSITIVE}
CARRY = ["title", "date", "drive_id", "drive_url", "modified", "retrieved"]
MARK_EVERY = 120  # seconds: a merged turn gets an inline timestamp at least this often

TS = r"(\d{1,2}:\d{2}(?::\d{2})?)(?:[.,]\d+)?"
NAME = r"([^\W\d_][\w.'’-]*(?: [\w.'’()/-]+){0,4})"
RE_VTT_TIME = re.compile(r"^\s*" + TS + r"\s+-->")
RE_TS_LINE = re.compile(r"^[#*\s]*\[?" + TS + r"\]?[*\s]*$")
RE_BRACKET_HEADER = re.compile(r"^\[" + NAME + r"\]\s+" + TS + r"\s*$")          # [Jane Doe] 00:01:02
RE_NAME_TIME_HEADER = re.compile(r"^" + NAME + r"\s+" + TS + r"\s*$")            # Jane Doe  0:03
RE_TS_SPEAKER = re.compile(r"^\[?" + TS + r"\]?\s*[-–]?\s*\*{0,2}" + NAME + r"\*{0,2}\s*:\s*\*{0,2}\s*(.*)$")
RE_SPEAKER = re.compile(r"^\*{0,2}" + NAME + r"\*{0,2}\s*:\s*\*{0,2}\s*(.*)$")   # Jane Doe: / **Jane Doe:**
# Lines transcription tools add that nobody said (Gemini and Meet footers)
RE_SKIP = re.compile(r"(?i)^\W*(this editable transcript was computer generated|transcription ended after|"
                     r"meeting ended after|you should review gemini's notes)")
# A transcript heading in a file that has a summary or notes first (Gemini notes Docs)
# The prefix allows an emoji, including one Drive turned into stray characters ("ð").
RE_TRANSCRIPT_HEADING = re.compile(r"(?i)^(?:#{1,4}\s*)?[*_]*\s*(?:\S{1,8}\s+)?[*_]*\s*transcript\s*[*_]*\s*$")
# Signs that a file starts with notes or a summary before its transcript
RE_NOTES_HINT = re.compile(r"(?im)^(?:#{1,4}\s.*|.*\bnotes by gemini\b.*|.*\bsuggested next steps\b.*)$")
# Something that looks like another speaker's label inside a turn: two to four capitalized
# words (or a pronoun note) followed by a colon
RE_EMBEDDED_LABEL = re.compile(r"(?<=\s)([A-Z][\w.'\u2019-]*(?: (?:[A-Z][\w.'\u2019-]*|\([^)\s]{1,12}\))){1,3}):\s")
RE_VOICE = re.compile(r"^<v\s+([^>]+)>(.*)$")
RE_TAG = re.compile(r"</?[^>]+>")
RE_TURN = re.compile(r"^(T\d{3,}) \[([0-9:]{8}|--:--:--)\] (.+?): (.*)$")

FILLER = r"(?:u+m+|u+h+|e+r+m*|a+h+)"
RE_FILLER_COMMAS = re.compile(r"(?i),\s*(?<![\w'-])" + FILLER + r"(?![\w'-]|\s+huh\b)\s*,\s*")
RE_FILLER = re.compile(r"(?i)(?<![\w'-])" + FILLER + r"(?![\w'-]|\s+huh\b)[,\u2026]*\s*")

PATTERNS = [
    ("email address", re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")),
    ("phone number", re.compile(r"(?<!\d)(?:\+?\d{1,2}[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}(?!\d)")),
    ("password or key", re.compile(r"(?i)\b(password|passcode|api[ _-]?key|private key|secret key|access token)\b")),
    ("long token-like string", re.compile(r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{32,}\b")),
    ("money amount", re.compile(r"\$\s?\d[\d,]*(?:\.\d+)?(?:\s?[kKmM]\b)?|\b\d[\d,]*\s?(?:dollars|bucks)\b")),
    ("pay or HR", re.compile(r"(?i)\b(salary|salaries|pay raise|bonus|compensation|fired|layoffs?|laid off|performance review|resign(?:ed|ing|ation)?)\b")),
    ("health", re.compile(r"(?i)\b(doctor|hospital|surgery|diagnos\w*|pregnan\w*|therapy|therapist|sick leave|medical leave|illness|cancer)\b")),
]


# ---------------------------------------------------------------- helpers

def seconds(ts):
    parts = [int(p) for p in ts.split(":")]
    if len(parts) == 2:
        parts = [0] + parts
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def hms(sec):
    return "%02d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)


def split_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            try:
                meta = yaml.safe_load(text[4:end]) or {}
            except yaml.YAMLError:
                meta = {}
            rest = text[end + 4:]
            return (meta if isinstance(meta, dict) else {}), rest.lstrip("\n")
    return {}, text


def words(text):
    """Words spoken: leaves out inline timestamps and cut markers."""
    text = re.sub(r"\[\d\d:\d\d:\d\d\]|\[\u2026\]|\[removed: [^\]]+\]", " ", text)
    return len(re.findall(r"\w\S*", text))


def strip_fillers(text):
    """Remove standalone um/uh/er/ah, tidy the punctuation left behind, and capitalize a
    sentence that now starts where a filler was."""
    mark = "\x00"
    out = RE_FILLER_COMMAS.sub(", " + mark, text)
    out = RE_FILLER.sub(mark, out)
    if mark not in out:
        return text.strip()
    out = re.sub(r"^[\s,.;:\u2026\x00-]+", mark, out)
    out = re.sub(r"(^|[.?!]\s)\x00+\s*([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)
    out = out.replace(mark, "")
    out = re.sub(r"\s+([,.?!;:])", r"\1", out)
    out = re.sub(r",\s*([.?!])", r"\1", out)
    out = re.sub(r",\s*,", ",", out)
    return re.sub(r"\s{2,}", " ", out).strip()


def good_name(name, rest):
    if rest.startswith("//"):
        return False  # a URL, not a speaker
    return len(name) <= 60


# ---------------------------------------------------------------- prepare

def parse_vtt(lines):
    chunks, t, speaker = [], None, None
    for line in lines:
        s = line.strip()
        m = RE_VTT_TIME.match(s)
        if m:
            t = seconds(m.group(1))
            continue
        if not s or s == "WEBVTT" or s.isdigit() or s.startswith("NOTE") or RE_SKIP.match(s):
            continue
        v = RE_VOICE.match(s)
        if v:
            speaker, s = v.group(1).strip(), v.group(2)
        else:
            m = RE_SPEAKER.match(RE_TAG.sub("", s))
            if m and good_name(m.group(1), m.group(2)):
                speaker, s = m.group(1).strip(), m.group(2)
        s = RE_TAG.sub("", s).strip()
        if s:
            chunks.append((t, speaker or "Unknown", s))
    return chunks


def parse_lines(lines):
    chunks, t, speaker = [], None, None
    for line in lines:
        s = line.strip().replace(" ", " ")
        if not s or s.startswith("#") and not RE_TS_LINE.match(s) or re.fullmatch(r"[-*_=]{3,}", s) or RE_SKIP.match(s):
            continue
        m = RE_TS_LINE.match(s)
        if m:
            t = seconds(m.group(1))
            continue
        m = RE_BRACKET_HEADER.match(s) or RE_NAME_TIME_HEADER.match(s)
        if m:
            speaker, t = m.group(1).strip(), seconds(m.group(2))
            continue
        m = RE_TS_SPEAKER.match(s)
        if m and good_name(m.group(2), m.group(3)):
            t, speaker = seconds(m.group(1)), m.group(2).strip()
            if m.group(3).strip():
                chunks.append((t, speaker, m.group(3).strip()))
            continue
        m = RE_SPEAKER.match(s)
        if m and good_name(m.group(1), m.group(2)):
            speaker = m.group(1).strip()
            if m.group(2).strip():
                chunks.append((t, speaker, m.group(2).strip()))
            continue
        if speaker:  # continuation of the current speaker
            chunks.append((t, speaker, s))
    return chunks


def build_turns(chunks):
    turns = []
    for t, speaker, text in chunks:
        text = strip_fillers(text)
        if not re.search(r"\w", text):
            continue
        if turns and turns[-1]["speaker"] == speaker:
            turn = turns[-1]
            if t is not None and turn["mark"] is not None and t - turn["mark"] >= MARK_EVERY:
                turn["text"] += " [%s]" % hms(t)
                turn["mark"] = t
            turn["text"] += " " + text
        else:
            turns.append({"t": t, "mark": t, "speaker": speaker, "text": text})
    return turns


def cmd_prepare(args):
    raw = opt(args, "--out", required=True)
    start = opt(args, "--from")
    title = opt(args, "--title")
    date = opt(args, "--date")
    src = args[0] if args else usage()
    with open(src, encoding="utf-8") as f:
        meta, body = split_frontmatter(f.read())
    lines = body.splitlines()
    if start:
        idx = next((i for i, l in enumerate(lines) if start in l), None)
        if idx is None:
            return fail("--from text not found in %s: %r" % (src, start))
        lines = lines[idx + 1:]
    else:
        idx = next((i for i, l in enumerate(lines) if RE_TRANSCRIPT_HEADING.match(l.strip())), None)
        if idx:  # a heading with something above it: start after it
            print("Started after the heading %r on line %d (pass --from to choose another)." % (lines[idx].strip(), idx + 1))
            lines = lines[idx + 1:]
        elif len(RE_NOTES_HINT.findall(body)) >= 2 or "drive_id" in meta and "gemini" in body.lower():
            print("WARNING: this looks like a notes Doc (headings or a Gemini summary), but no Transcript heading "
                  "was found, so the whole file is parsed as speech. Pass --from \"<text of the transcript heading>\".")
    is_vtt = any(RE_VTT_TIME.match(l) for l in lines[:200])
    chunks = parse_vtt(lines) if is_vtt else parse_lines(lines)
    turns = build_turns(chunks)
    if not turns:
        return fail("no speaker turns found in %s. Check the format (and --from for a file with a summary first)." % src)
    timed = any(c[0] is not None for c in chunks)
    head = {k: meta[k] for k in CARRY if k in meta}
    if title:
        head["title"] = title
    if date:
        head["date"] = datetime.date.fromisoformat(date)
    spoken = sum(words(c[2]) for c in chunks)
    head.update({"raw": src, "format": "vtt" if is_vtt else ("timed text" if timed else "text"),
                 "spoken_words": spoken})
    out = ["---", yaml.safe_dump(head, sort_keys=False, allow_unicode=True).strip(), "---"]
    for i, turn in enumerate(turns, 1):
        ts = hms(turn["t"]) if turn["t"] is not None else "--:--:--"
        out.append("T%03d [%s] %s: %s" % (i, ts, turn["speaker"], turn["text"]))
    os.makedirs(os.path.dirname(os.path.abspath(raw)), exist_ok=True)
    with open(raw, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    speakers = sorted({t["speaker"] for t in turns})
    kept = sum(words(t["text"]) for t in turns)
    print("Wrote %s: %d turns, %d speakers (%s). %d words spoken, %d after dropping fillers."
          % (raw, len(turns), len(speakers), ", ".join(speakers), spoken, kept))
    if not timed:
        print("WARNING: no timestamps found; the cleaned transcript will have none to cite.")
    if "title" not in head:
        print("WARNING: no title; pass --title (the file name will be used otherwise).")
    labels = {}
    for i, turn in enumerate(turns, 1):
        for m in RE_EMBEDDED_LABEL.finditer(turn["text"]):
            label = re.split(r"[.?!]\s+", m.group(1))[-1]  # "Okay. Jane Roe" -> "Jane Roe"
            if " " not in label:
                continue
            ids = labels.setdefault(label, [])
            if "T%03d" % i not in ids:
                ids.append("T%03d" % i)
    for label, ids in sorted(labels.items(), key=lambda kv: -len(kv[1])):
        known = " It is also a speaker's name in this transcript." if label in speakers else ""
        print("WARNING: %r looks like a speaker label inside %d turn%s (%s).%s If it's a speaker the parser "
              "missed, their lines were merged into someone else's: don't clean this parse; report it."
              % (label, len(ids), "" if len(ids) == 1 else "s", ", ".join(ids[:5]) + (" ..." if len(ids) > 5 else ""), known))
    return 0


# ---------------------------------------------------------------- check / write

def load_turns(path):
    with open(path, encoding="utf-8") as f:
        meta, body = split_frontmatter(f.read())
    turns = []
    for n, line in enumerate(body.splitlines(), 1):
        if not line.strip():
            continue
        m = RE_TURN.match(line)
        if not m:
            raise ValueError("%s line %d is not a turn: %r" % (path, n, line[:80]))
        turns.append({"id": m.group(1), "ts": None if m.group(2).startswith("-") else m.group(2),
                      "speaker": m.group(3), "text": m.group(4)})
    return meta, turns


def load_edits(path, turns):
    """Return (cuts, topics, errors). Each cut: ids, kind, why, text, fact."""
    errors = []
    with open(path, encoding="utf-8") as f:
        try:
            data = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            return [], [], ["edits file does not parse: %s" % e]
    if not isinstance(data, dict) or set(data) - {"cuts", "topics"}:
        return [], [], ["edits file must be a mapping with `cuts` and optional `topics`"]
    index = {t["id"]: i for i, t in enumerate(turns)}
    cuts, whole, parts = [], set(), {}
    for n, c in enumerate(data.get("cuts") or [], 1):
        where = "cut %d" % n
        if not isinstance(c, dict):
            errors.append("%s must be a mapping" % where)
            continue
        extra = set(c) - {"turns", "kind", "why", "text", "fact"}
        if extra:
            errors.append("%s has unknown fields: %s" % (where, ", ".join(sorted(extra))))
        m = re.fullmatch(r"(T\d{3,})(?:-(T\d{3,}))?", str(c.get("turns", "")))
        if not m or m.group(1) not in index or (m.group(2) and m.group(2) not in index):
            errors.append("%s: `turns` must be a turn ID or range that exists (e.g. T004 or T004-T009)" % where)
            continue
        a, b = index[m.group(1)], index[m.group(2) or m.group(1)]
        if b < a:
            errors.append("%s: range runs backwards" % where)
            continue
        if c.get("kind") not in KINDS:
            errors.append("%s: `kind` must be one of %s" % (where, ", ".join(KINDS)))
        if not str(c.get("why") or "").strip():
            errors.append("%s: `why` is required" % where)
        text = c.get("text")
        ids = list(range(a, b + 1))
        if text is not None:
            if a != b:
                errors.append("%s: `text` cuts work on one turn, not a range" % where)
                continue
            count = turns[a]["text"].count(str(text))
            if count != 1:
                errors.append("%s: `text` must appear exactly once in %s, copied exactly (found %d)"
                              % (where, turns[a]["id"], count))
                continue
            if a in whole:
                errors.append("%s: %s is already cut whole" % (where, turns[a]["id"]))
            parts.setdefault(a, []).append(str(text))
        else:
            clash = [turns[i]["id"] for i in ids if i in whole or i in parts]
            if clash:
                errors.append("%s overlaps another cut at %s" % (where, ", ".join(clash)))
            whole.update(ids)
        cuts.append({"n": n, "ids": ids, "kind": c.get("kind"), "why": str(c.get("why") or "").strip(),
                     "text": None if text is None else str(text), "fact": c.get("fact")})
    for a, texts in parts.items():
        if a in whole:
            errors.append("%s has a passage cut and is also cut whole" % turns[a]["id"])
    topics, last = {}, -1
    for n, tp in enumerate(data.get("topics") or [], 1):
        where = "topic %d" % n
        if not isinstance(tp, dict) or tp.get("at") not in index or not str(tp.get("title") or "").strip():
            errors.append("%s needs `at` (an existing turn ID) and `title`" % where)
            continue
        i = index[tp["at"]]
        if i <= last:
            errors.append("%s is out of order" % where)
        if i in whole:
            errors.append("%s starts at a turn that is cut" % where)
        if len(str(tp["title"])) > 60:
            errors.append("%s: keep titles under 60 characters" % where)
        topics[i], last = str(tp["title"]).strip(), i
    return cuts, topics, errors


def kept_text(turns, cuts):
    """Turn index -> text after cuts (None when cut whole), and the markers used."""
    out = {i: t["text"] for i, t in enumerate(turns)}
    for c in cuts:
        if c["text"] is None:
            for i in c["ids"]:
                out[i] = None
        else:
            i = c["ids"][0]
            mark = "[…]" if c["kind"] in BANTER else "[removed: %s]" % SENSITIVE[c["kind"]]
            out[i] = re.sub(r"\s{2,}", " ", out[i].replace(c["text"], " %s " % mark, 1)).strip()
    return out


def scan(turns, texts):
    hits = []
    for i, text in texts.items():
        if not text:
            continue
        for label, rx in PATTERNS:
            for m in rx.finditer(re.sub(r"\[removed: [^\]]+\]", "", text)):
                hits.append((turns[i], label, m.group(0)))
    return hits


def span(turns, ids):
    a, b = turns[ids[0]], turns[ids[-1]]
    if not a["ts"]:
        return ""
    return a["ts"] if a["ts"] == b["ts"] or not b["ts"] else "%s–%s" % (a["ts"], b["ts"])


def clip(text, n=110):
    text = re.sub(r"\s+", " ", text)
    return text if len(text) <= n else text[:n].rstrip() + "…"


def cmd_check(args):
    show = flag(args, "--show")
    if len(args) != 2:
        usage()
    try:
        meta, turns = load_turns(args[0])
    except ValueError as e:
        return fail(str(e))
    cuts, topics, errors = load_edits(args[1], turns)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        return 1
    texts = kept_text(turns, cuts)
    before = sum(words(t["text"]) for t in turns)
    after = sum(words(t) for t in texts.values() if t)
    spoken = meta.get("spoken_words") or before
    pct = lambda n: round(100.0 * n / spoken, 1) if spoken else 0
    print("Proposed cuts: %d (%d of %d turns cut whole)." % (len(cuts), sum(1 for t in texts.values() if t is None), len(turns)))
    print("Words spoken: %d. Fillers dropped: %d (%s%%). Cuts remove: %d (%s%%). Cleaned: %d (%s%% of spoken)."
          % (spoken, spoken - before, pct(spoken - before), before - after, pct(before - after), after, pct(after)))
    for c in sorted(cuts, key=lambda c: c["ids"][0]):
        ids = [turns[i]["id"] for i in c["ids"]]
        ref = ids[0] if len(ids) == 1 else "%s-%s" % (ids[0], ids[-1])
        where = " ".join(x for x in [span(turns, c["ids"]), "(%s%s)" % (ref, ", part" if c["text"] else "")] if x)
        print("%d. [%s] %s %s" % (c["n"], KINDS[c["kind"]], where, c["why"]))
        if c["fact"]:
            print("     Holds a project fact for the PM to file or drop: %s" % c["fact"])
        if c["kind"] in BANTER or show:
            body = c["text"] or " / ".join("%s: %s" % (turns[i]["speaker"], turns[i]["text"]) for i in c["ids"])
            print('     "%s"' % clip(body))
    hits = scan(turns, texts)
    if hits:
        print("\nCheck these in the kept text before writing (cut them or confirm they stay):")
        for turn, label, match in hits:
            print("  %s [%s] %s: %s: %s" % (turn["id"], turn["ts"] or "--", turn["speaker"], label, clip(match, 60)))
    return 0


def cmd_write(args):
    out_path = opt(args, "--out", required=True)
    reviewer = opt(args, "--reviewed-by")
    force = flag(args, "--force")
    if len(args) != 2:
        usage()
    if os.path.exists(out_path) and not force:
        return fail("%s already exists; pass --force to replace it." % out_path)
    try:
        meta, turns = load_turns(args[0])
    except ValueError as e:
        return fail(str(e))
    cuts, topics, errors = load_edits(args[1], turns)
    if errors:
        for e in errors:
            print("ERROR: " + e)
        return 1
    texts = kept_text(turns, cuts)
    kind_of = {}
    for c in cuts:
        if c["text"] is None:
            for i in c["ids"]:
                kind_of[i] = c["kind"]
    lines, group = [], []

    def flush():
        if not group:
            return
        kinds = []
        for i in group:
            if kind_of[i] not in kinds:
                kinds.append(kind_of[i])
        when = span(turns, group)
        if kinds[0] in SENSITIVE:
            label = "removed: " + SENSITIVE[kinds[0]]
        else:
            label = ", ".join(BANTER[k] for k in kinds)
        lines.append("*[%s%s]*" % (label, ", " + when if when else ""))
        lines.append("")
        del group[:]

    for i, turn in enumerate(turns):
        if texts[i] is None:
            sensitive = kind_of[i] in SENSITIVE
            if group and (sensitive or kind_of[group[-1]] in SENSITIVE) and kind_of[group[-1]] != kind_of[i]:
                flush()
            group.append(i)
            continue
        flush()
        if i in topics:
            lines.append("## %s%s" % ("[%s] " % turn["ts"] if turn["ts"] else "", topics[i]))
            lines.append("")
        lines.append("**%s%s:** %s" % ("[%s] " % turn["ts"] if turn["ts"] else "", turn["speaker"], texts[i]))
        lines.append("")
    flush()

    speakers = []
    for i, turn in enumerate(turns):
        if texts[i] is not None and turn["speaker"] not in speakers:
            speakers.append(turn["speaker"])
    removed = {}
    for c in cuts:
        removed[c["kind"]] = removed.get(c["kind"], 0) + 1
    head = {k: meta[k] for k in ["title", "date"] if k in meta}
    if "date" not in head:
        m = re.search(r"\d{4}-\d{2}-\d{2}", "%s %s" % (os.path.basename(str(meta.get("raw") or "")), meta.get("title") or ""))
        if m:
            head["date"] = datetime.date.fromisoformat(m.group(0))
    head["cleaned"] = datetime.date.today()
    head["reviewed_by"] = reviewer
    if not reviewer:
        head["status"] = "draft"
    head["raw"] = meta.get("raw")
    for k in ["drive_url", "format"]:
        if k in meta:
            head[k] = meta[k]
    head["speakers"] = speakers
    head["removed"] = removed
    head.update(project_settings(out_path))
    head["words"] = {"spoken": meta.get("spoken_words"), "cleaned": sum(words(t) for t in texts.values() if t)}
    title = meta.get("title") or os.path.splitext(os.path.basename(out_path))[0]
    doc = ["---", yaml.safe_dump(head, sort_keys=False, allow_unicode=True, default_flow_style=None).strip(), "---",
           "# %s" % title, "",
           "*Cleaned transcript: small talk and sensitive passages are removed and marked in place, and filler "
           "words are dropped. Everything else is as recorded. The raw transcript is kept outside git.*", ""]
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(doc + lines).rstrip() + "\n")
    print("Wrote %s (%s): %d turns kept, %d cuts." % (out_path, "draft" if not reviewer else "reviewed by " + reviewer,
                                                    sum(1 for t in texts.values() if t), len(cuts)))
    return 0


# ---------------------------------------------------------------- verify

def project_root(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isdir(os.path.join(d, ".ai")) or os.path.isdir(os.path.join(d, ".git")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def project_settings(path):
    """Readers and Internal from .ai/project/transcript-cleanup.md, as frontmatter fields."""
    root = project_root(os.path.dirname(os.path.abspath(path)))
    file = os.path.join(root, ".ai", "project", "transcript-cleanup.md") if root else None
    out = {}
    if file and os.path.exists(file):
        for line in open(file, encoding="utf-8"):
            m = re.match(r"^\s*(Readers|Internal):\s*([^#]+?)\s*(?:#.*)?$", line)
            if m and m.group(1).lower() not in out:
                out[m.group(1).lower()] = m.group(2)
    return out


def verify_file(path, errors, warnings):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if not text.strip():
        return
    meta, body = split_frontmatter(text)
    if "cleaned" not in meta:
        warnings.append("%s: raw transcript (no `cleaned` in its frontmatter). Raw transcripts belong in "
                        "docs/transcripts/raw/." % path)
        return
    for key in ["reviewed_by", "raw", "speakers"]:
        if not meta.get(key):
            errors.append("%s: missing `%s`" % (path, key))
    if meta.get("status") == "draft":
        errors.append("%s: still a draft; the PM hasn't approved its cuts" % path)
    now = project_settings(path)
    if now and any(str(meta.get(k)) != now[k] for k in now):
        warnings.append("%s: cleaned for readers %r, internal %r; the project now says readers %r, internal %r. "
                        "Ask the PM whether to reclean it from the raw transcript."
                        % (path, meta.get("readers"), meta.get("internal"), now.get("readers"), now.get("internal")))
    for line in body.splitlines():
        if line.startswith("**"):
            for label, rx in PATTERNS:
                for m in rx.finditer(re.sub(r"\[removed: [^\]]+\]", "", line)):
                    warnings.append("%s: %s: %s" % (path, label, clip(line, 90)))


def cmd_verify(args):
    if not args:
        usage()
    errors, warnings = [], []
    for target in args:
        if os.path.isdir(target):
            for name in sorted(os.listdir(target)):
                p = os.path.join(target, name)
                if os.path.isfile(p) and not name.startswith("."):
                    verify_file(p, errors, warnings)
            root = project_root(target)
            if root:
                ignore = os.path.join(root, ".gitignore")
                lines = open(ignore, encoding="utf-8").read().splitlines() if os.path.exists(ignore) else []
                if not any(l.strip().rstrip("/").lstrip("/") == "docs/transcripts/raw" for l in lines):
                    warnings.append("docs/transcripts/raw/ is not in .gitignore, so raw transcripts would be committed.")
        elif os.path.isfile(target):
            verify_file(target, errors, warnings)
        else:
            errors.append("%s: not found" % target)
    for w in warnings:
        print("WARNING: " + w)
    for e in errors:
        print("ERROR: " + e)
    if not errors:
        print("OK" + (" (with warnings)" if warnings else ""))
    return 1 if errors else 0


# ---------------------------------------------------------------- cli

def opt(args, name, required=False):
    if name in args:
        i = args.index(name)
        if i + 1 >= len(args):
            usage()
        value = args[i + 1]
        del args[i:i + 2]
        return value
    if required:
        usage()
    return None


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


def fail(msg):
    print("ERROR: " + msg)
    return 1


def usage():
    sys.exit(__doc__)


def main(argv):
    if not argv:
        usage()
    commands = {"prepare": cmd_prepare, "check": cmd_check, "write": cmd_write, "verify": cmd_verify}
    if argv[0] not in commands:
        usage()
    return commands[argv[0]](list(argv[1:]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
