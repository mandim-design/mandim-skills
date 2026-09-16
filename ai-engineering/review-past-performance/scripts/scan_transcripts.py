#!/usr/bin/env python3
"""Scan Claude Code transcripts for friction and waste signals.

Reads ~/.claude/projects/<encoded-cwd>/<session>.jsonl (JSON Lines, one record
per event) and emits a markdown digest of what went wrong and what was wasted.

Stdlib only. Streams line by line; never loads a whole transcript into memory.

Usage:
  scan_transcripts.py                     # last 24h, all repos, markdown
  scan_transcripts.py --hours 72
  scan_transcripts.py --project fisbu     # substring match on the repo path
  scan_transcripts.py --json              # machine-readable, for further slicing
  scan_transcripts.py --session <uuid>    # one session only
  scan_transcripts.py --session <uuid> --dump   # chronological replay, for evidence
"""

import argparse
import glob
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

PROJECTS = os.path.expanduser("~/.claude/projects")

# Cues that a user message is fixing something Claude got wrong. Portuguese
# first: that is the language these sessions are actually driven in.
CORRECTION_CUES = [
    "não é isso", "nao e isso", "não era isso", "isso está errado", "esta errado",
    "está errado", "erraste", "erro teu", "volta atrás", "volta atras", "reverte",
    "desfaz", "outra vez", "de novo", "já te disse", "ja te disse", "eu disse",
    "não faças", "nao facas", "para com", "pára", "não era", "nao era",
    "that's wrong", "thats wrong", "no, ", "not what i", "revert", "undo",
    "again", "you broke", "stop ", "i already said", "actually no",
]

# Cues that the user is repeating an instruction that lives in a CLAUDE.md.
RULE_CUES = [
    "já está no claude.md", "esta no claude.md", "claude.md", "context.md",
    "em português", "portugues europeu", "não inventes", "nao inventes",
    "não cries", "nao cries", "sem ficheiros", "não commites", "nao commites",
    "lê o", "le o ", "read the",
]

REJECTION_RE = re.compile(
    r"doesn't want to proceed|tool use was rejected|requested permissions|"
    r"User rejected|permission to use", re.I)

INTERRUPT_MARK = "[Request interrupted by user"

READ_TOOLS = {"Read", "NotebookEdit"}
WRITE_TOOLS = {"Edit", "Write", "NotebookEdit"}
SEARCH_TOOLS = {"Grep", "Glob"}

TRUNC = 160


def truncate(s, n=TRUNC):
    s = " ".join(str(s).split())
    return s if len(s) <= n else s[: n - 1] + "…"


def parse_ts(rec):
    ts = rec.get("timestamp")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def blocks(rec):
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict)]
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    return []


def text_of(rec):
    return " ".join(b.get("text", "") for b in blocks(rec) if b.get("type") == "text").strip()


def repo_of(path):
    """Fallback repo label from the project directory name.

    The directory name encodes the cwd with every "/" turned into "-", which is
    lossy for paths that already contain hyphens. Real `cwd` values from the
    records override this whenever they are present.
    """
    base = os.path.basename(path)
    return "~" + base.lstrip("-").replace("-", "/")


def target_path(name, inp):
    if not isinstance(inp, dict):
        return None
    for k in ("file_path", "path", "notebook_path"):
        if inp.get(k):
            return inp[k]
    if name == "Bash":
        m = re.search(r"\b(?:cat|head|tail|less|sed -n)\b[^|;]*?(\S+\.\w+)", inp.get("command", ""))
        if m:
            return m.group(1)
    return None


class Session:
    def __init__(self, sid, repo):
        self.sid = sid
        self.sids = set()   # branches that actually contributed records
        self.seen = set()
        self.fallback_repo = repo
        self.cwds = set()
        self.start = None
        self.end = None
        self.human_turns = 0
        self.assistant_turns = 0
        self.sidechain_turns = 0
        self.tools = Counter()
        self.tool_calls = {}          # tool_use_id -> (name, input)
        self.call_fingerprints = Counter()
        self.file_touches = Counter()
        self.tokens = Counter()
        self.interrupts = []
        self.errors = []
        self.denials = []
        self.corrections = []
        self.rule_reminders = []
        self.skills = Counter()
        self.first_prompt = ""

    @property
    def forks(self):
        return len(self.sids)

    @property
    def repo(self):
        return sorted(self.cwds)[0] if self.cwds else self.fallback_repo

    def note_interrupt(self, ts, text):
        """Record a stop.

        A real stop is a user text block that *is* the marker and nothing else
        ("[Request interrupted by user]", or the "for tool use" variant). Any
        session that reads transcripts quotes that string inside tool output,
        so a substring match anywhere would flag this very scan as friction.
        """
        if not text.strip().startswith(INTERRUPT_MARK):
            return
        if "for tool use]" in text:
            tool = list(self.tool_calls.values())[-1][0] if self.tool_calls else "?"
            note = "parou a meio de " + tool
        else:
            note = "parou a resposta"
        self.interrupts.append({"ts": ts.isoformat(), "note": note})

    def note_time(self, ts):
        if ts is None:
            return
        if self.start is None or ts < self.start:
            self.start = ts
        if self.end is None or ts > self.end:
            self.end = ts

    @property
    def total_tokens(self):
        return (self.tokens["input"] + self.tokens["output"]
                + self.tokens["cache_read"] + self.tokens["cache_write"])

    @property
    def friction(self):
        return (len(self.interrupts) + len(self.errors) + len(self.denials)
                + len(self.corrections))


def fork_canon(paths):
    """Map every sessionId in a project dir to one id per fork lineage.

    A fork writes a new file with a new sessionId but copies the prefix
    verbatim, record uuids included — so files whose first record shares a
    uuid are branches of one conversation. A sidechain (subagent) transcript
    is a separate file that keeps its parent's sessionId, so keying on the
    sid is what keeps it attached to the parent; that is why the grouping
    unions sids rather than replacing them with the root uuid.
    """
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    by_root = defaultdict(set)
    for path in paths:
        sid = root = None
        try:
            with open(path, errors="replace") as fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if sid is None and rec.get("sessionId"):
                        sid = rec["sessionId"]
                    if root is None and rec.get("uuid"):
                        root = rec["uuid"]
                    if sid and root:
                        break
        except OSError:
            continue
        if not sid:
            continue
        find(sid)
        if root:
            by_root[root].add(sid)

    for sids in by_root.values():
        sids = sorted(sids)
        for other in sids[1:]:
            a, b = find(sids[0]), find(other)
            if a != b:
                parent[max(a, b)] = min(a, b)

    return {sid: find(sid) for sid in parent}


def scan(hours, project_filter, session_filter):
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    sessions = {}

    for proj_dir in sorted(glob.glob(os.path.join(PROJECTS, "*"))):
        if not os.path.isdir(proj_dir):
            continue
        if project_filter and project_filter.lower() not in os.path.basename(proj_dir).lower():
            continue
        repo = repo_of(proj_dir)
        paths = sorted(glob.glob(os.path.join(proj_dir, "*.jsonl")))
        canon = fork_canon(paths)

        for path in paths:
            # Cheap pre-filter: an untouched file cannot hold recent records.
            try:
                if datetime.fromtimestamp(os.path.getmtime(path), timezone.utc) < cutoff:
                    continue
            except OSError:
                continue

            last_assistant_had_tools = False
            try:
                fh = open(path, errors="replace")
            except OSError:
                continue
            with fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    ts = parse_ts(rec)
                    if ts is None or ts < cutoff:
                        continue

                    sid = rec.get("sessionId") or os.path.basename(path)[:-6]
                    if session_filter and session_filter not in sid:
                        continue
                    key = canon.get(sid, sid)
                    s = sessions.get(key)
                    if s is None:
                        s = sessions[key] = Session(key, repo)
                    s.sids.add(sid)
                    # Union, not sum: counting every fork counts the shared
                    # prefix once per branch and inflates friction.
                    uid = rec.get("uuid")
                    if uid is not None:
                        if uid in s.seen:
                            continue
                        s.seen.add(uid)
                    s.note_time(ts)
                    if rec.get("cwd"):
                        s.cwds.add(rec["cwd"])

                    rtype = rec.get("type")

                    if rtype == "assistant":
                        if rec.get("isSidechain"):
                            s.sidechain_turns += 1
                        else:
                            s.assistant_turns += 1
                        usage = (rec.get("message") or {}).get("usage") or {}
                        s.tokens["input"] += usage.get("input_tokens", 0)
                        s.tokens["output"] += usage.get("output_tokens", 0)
                        s.tokens["cache_read"] += usage.get("cache_read_input_tokens", 0)
                        s.tokens["cache_write"] += usage.get("cache_creation_input_tokens", 0)

                        had_tools = False
                        for b in blocks(rec):
                            if b.get("type") != "tool_use":
                                continue
                            had_tools = True
                            name = b.get("name", "?")
                            inp = b.get("input") or {}
                            s.tools[name] += 1
                            s.tool_calls[b.get("id")] = (name, inp)
                            s.call_fingerprints[
                                (name, truncate(json.dumps(inp, sort_keys=True), 300))
                            ] += 1
                            if name == "Skill":
                                s.skills[inp.get("skill", "?")] += 1
                            tgt = target_path(name, inp)
                            if tgt:
                                s.file_touches[(name, tgt)] += 1
                        last_assistant_had_tools = had_tools

                    elif rtype == "user":
                        bs = blocks(rec)
                        results = [b for b in bs if b.get("type") == "tool_result"]

                        # Must run before the early-continue below, and before
                        # the system-reminder stripping: a stop is its own user
                        # record and never reaches the prompt bookkeeping.
                        s.note_interrupt(ts, text_of(rec))
                        for b in results:
                            if not b.get("is_error"):
                                continue
                            name, inp = s.tool_calls.get(b.get("tool_use_id"), ("?", {}))
                            content = b.get("content")
                            if isinstance(content, list):
                                content = " ".join(
                                    x.get("text", "") for x in content if isinstance(x, dict)
                                )
                            item = {
                                "ts": ts.isoformat(),
                                "tool": name,
                                "input": truncate(json.dumps(inp, ensure_ascii=False), 200),
                                "error": truncate(content, 220),
                            }
                            if REJECTION_RE.search(content or ""):
                                s.denials.append(item)
                            else:
                                s.errors.append(item)

                        if results or rec.get("isMeta"):
                            continue

                        txt = text_of(rec)
                        if not txt or txt.startswith("<system-reminder>"):
                            continue
                        txt = re.sub(r"<system-reminder>.*?</system-reminder>", "", txt,
                                     flags=re.S).strip()
                        if not txt:
                            continue

                        s.human_turns += 1
                        if not s.first_prompt:
                            s.first_prompt = truncate(txt, 200)

                        low = txt.lower()
                        # A correction is a short reaction, not a pasted document.
                        if (last_assistant_had_tools and len(txt) < 400
                                and any(c in low for c in CORRECTION_CUES)):
                            s.corrections.append({"ts": ts.isoformat(), "text": truncate(txt)})
                        if any(c in low for c in RULE_CUES):
                            s.rule_reminders.append({"ts": ts.isoformat(), "text": truncate(txt)})

    return sessions


def build_report(sessions, hours):
    by_repo = defaultdict(list)
    for s in sessions.values():
        by_repo[s.repo].append(s)

    tools_all = Counter()
    for s in sessions.values():
        tools_all.update(s.tools)

    repeats = []
    rereads = []
    for s in sessions.values():
        for (name, inp), n in s.call_fingerprints.items():
            if n >= 2:
                repeats.append((n, s.repo, s.sid, name, inp))
        for (name, path), n in s.file_touches.items():
            if n >= 3 and name in READ_TOOLS | {"Bash"}:
                rereads.append((n, s.repo, s.sid, name, path))
    repeats.sort(reverse=True, key=lambda x: x[0])
    rereads.sort(reverse=True, key=lambda x: x[0])

    return {
        "window_hours": hours,
        "sessions": sessions,
        "by_repo": by_repo,
        "tools_all": tools_all,
        "repeats": repeats,
        "rereads": rereads,
    }


def to_markdown(r):
    out = []
    w = out.append
    sessions = r["sessions"]
    total_friction = sum(s.friction for s in sessions.values())
    total_tools = sum(r["tools_all"].values())

    w(f"# Transcript scan — last {r['window_hours']}h\n")
    if not sessions:
        w("No sessions in window.\n")
        return "\n".join(out)

    forked = sum(s.forks - 1 for s in sessions.values())
    w(f"- Sessions: **{len(sessions)}** across **{len(r['by_repo'])}** repos"
      + (f" (+{forked} forks, merged into their origin)" if forked else ""))
    w(f"- Tool calls: **{total_tools}**  |  Friction events: **{total_friction}**")
    w(f"- Tokens (in+out+cache): **{sum(s.total_tokens for s in sessions.values()):,}**\n")

    w("## Sessions\n")
    w("| Repo | Session | Forks | Turns | Tools | Fric | Tokens | Opened with |")
    w("|---|---|---:|---:|---:|---:|---:|---|")
    for s in sorted(sessions.values(), key=lambda x: -x.friction):
        w(f"| `{s.repo}` | `{s.sid[:8]}` | {s.forks} | {s.human_turns}/{s.assistant_turns} "
          f"| {sum(s.tools.values())} | {s.friction} | {s.total_tokens:,} "
          f"| {s.first_prompt or '—'} |")
    w("")

    w("## Tool usage\n")
    for name, n in r["tools_all"].most_common(25):
        w(f"- `{name}` — {n}")
    w("")

    def section(title, rows, fmt):
        w(f"## {title}\n")
        if not rows:
            w("_none_\n")
            return
        for row in rows:
            w(fmt(row))
        w("")

    section(
        "Repeated identical tool calls (same tool, same input)",
        r["repeats"][:25],
        lambda x: f"- **{x[0]}×** `{x[3]}` in `{x[1]}` ({x[2][:8]}) — {x[4]}",
    )
    section(
        "Files read 3+ times in one session",
        r["rereads"][:25],
        lambda x: f"- **{x[0]}×** `{x[4]}` via `{x[3]}` in `{x[1]}` ({x[2][:8]})",
    )

    for label, attr in [
        ("Interruptions (user hit stop)", "interrupts"),
        ("Tool errors", "errors"),
        ("Permission friction", "denials"),
        ("User corrections after a tool run", "corrections"),
        ("User re-stating a rule that lives in a CLAUDE.md", "rule_reminders"),
    ]:
        w(f"## {label}\n")
        any_row = False
        for s in sessions.values():
            for item in getattr(s, attr):
                any_row = True
                if attr in ("errors", "denials"):
                    w(f"- `{s.repo}` `{s.sid[:8]}` **{item['tool']}** — {item['error']}")
                    w(f"    - input: {item['input']}")
                else:
                    w(f"- `{s.repo}` `{s.sid[:8]}` {item['ts'][11:16]} — "
                      f"{item.get('text') or item.get('note')}")
        if not any_row:
            w("_none_")
        w("")

    w("## Skills invoked\n")
    sk = Counter()
    for s in sessions.values():
        sk.update(s.skills)
    if sk:
        for name, n in sk.most_common():
            w(f"- `{name}` — {n}")
    else:
        w("_none_")
    w("")

    # Forks are already merged above, so what is left here is a genuine
    # re-run: the same opening typed again in a new session.
    w("## Sessions re-run from the same opening (forks excluded)\n")
    openings = defaultdict(list)
    for s_ in sessions.values():
        if s_.first_prompt:
            openings[s_.first_prompt[:120]].append(s_)
    dupes = {k: v for k, v in openings.items() if len(v) > 1}
    if dupes:
        for k, group in dupes.items():
            w(f"- {len(group)}× — {k}")
            for s_ in group:
                w(f"    - `{s_.sid[:8]}` in `{s_.repo}`, {sum(s_.tools.values())} tool calls")
    else:
        w("_none_")
    w("")

    w("## Repos worked in parallel\n")
    spans = [(s.start, s.end, s.repo, s.sid) for s in sessions.values() if s.start and s.end]
    spans.sort()
    overlaps = set()
    for i, a in enumerate(spans):
        for b in spans[i + 1:]:
            if b[0] <= a[1] and a[2] != b[2]:
                overlaps.add(tuple(sorted((a[2], b[2]))))
    if overlaps:
        for a, b in sorted(overlaps):
            w(f"- `{a}` ↔ `{b}`")
    else:
        w("_no overlapping sessions across repos_")
    w("")
    return "\n".join(out)


def to_json(r):
    payload = {"window_hours": r["window_hours"], "sessions": []}
    for s in r["sessions"].values():
        payload["sessions"].append({
            "session": s.sid,
            "forks": sorted(s.sids),
            "repo": s.repo,
            "cwds": sorted(s.cwds),
            "start": s.start.isoformat() if s.start else None,
            "end": s.end.isoformat() if s.end else None,
            "human_turns": s.human_turns,
            "assistant_turns": s.assistant_turns,
            "sidechain_turns": s.sidechain_turns,
            "tools": dict(s.tools),
            "skills": dict(s.skills),
            "tokens": dict(s.tokens),
            "first_prompt": s.first_prompt,
            "interrupts": s.interrupts,
            "errors": s.errors,
            "denials": s.denials,
            "corrections": s.corrections,
            "rule_reminders": s.rule_reminders,
        })
    return json.dumps(payload, ensure_ascii=False, indent=2)


def dump(hours, project_filter, session_filter, width):
    """Chronological replay of a session: prompts, replies, tool calls.

    The counters say where it hurt; this says why. Always read the replay
    around a friction event before drawing a conclusion from it.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    rows = []
    for proj_dir in sorted(glob.glob(os.path.join(PROJECTS, "*"))):
        if not os.path.isdir(proj_dir):
            continue
        if project_filter and project_filter.lower() not in os.path.basename(proj_dir).lower():
            continue
        for path in glob.glob(os.path.join(proj_dir, "*.jsonl")):
            if session_filter and session_filter not in os.path.basename(path):
                continue
            try:
                fh = open(path, errors="replace")
            except OSError:
                continue
            with fh:
                for line in fh:
                    try:
                        rec = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    ts = parse_ts(rec)
                    if ts is None or ts < cutoff:
                        continue
                    if session_filter and session_filter not in (rec.get("sessionId") or ""):
                        continue
                    tag = None
                    body = ""
                    if rec.get("type") == "user":
                        bs = blocks(rec)
                        if any(b.get("type") == "tool_result" for b in bs):
                            for b in bs:
                                if b.get("type") == "tool_result" and b.get("is_error"):
                                    c = b.get("content")
                                    if isinstance(c, list):
                                        c = " ".join(x.get("text", "") for x in c
                                                     if isinstance(x, dict))
                                    tag, body = "ERR ", truncate(c, width)
                            if tag is None:
                                continue
                        elif not rec.get("isMeta"):
                            t = re.sub(r"<system-reminder>.*?</system-reminder>", "",
                                       text_of(rec), flags=re.S).strip()
                            if t:
                                tag, body = "USER", truncate(t, width)
                    elif rec.get("type") == "assistant":
                        pre = "SUB " if rec.get("isSidechain") else "ASST"
                        t = text_of(rec)
                        calls = [f"{b.get('name')}({truncate(json.dumps(b.get('input') or {}, ensure_ascii=False), 90)})"
                                 for b in blocks(rec) if b.get("type") == "tool_use"]
                        parts = []
                        if t:
                            parts.append(truncate(t, width))
                        parts += ["→ " + c for c in calls]
                        if parts:
                            tag, body = pre, "  ".join(parts)
                    if tag:
                        rows.append((ts, tag, body))
    rows.sort(key=lambda r: r[0])
    return "\n".join(f"{ts.isoformat()[11:19]} {tag} {body}" for ts, tag, body in rows)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hours", type=float, default=24)
    ap.add_argument("--project", default=None, help="substring of the repo path")
    ap.add_argument("--session", default=None, help="substring of a session id")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dump", action="store_true",
                    help="chronological replay instead of the digest")
    ap.add_argument("--width", type=int, default=220, help="dump truncation width")
    args = ap.parse_args()

    if args.dump:
        print(dump(args.hours, args.project, args.session, args.width))
        return

    sessions = scan(args.hours, args.project, args.session)
    report = build_report(sessions, args.hours)
    print(to_json(report) if args.json else to_markdown(report))


if __name__ == "__main__":
    main()
