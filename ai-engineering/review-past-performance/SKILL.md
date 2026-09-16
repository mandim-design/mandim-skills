---
name: review-past-performance
description: Audits recent Claude Code sessions from the local transcripts and produces a concrete plan to make the next ones faster and less frustrating. Use whenever the user wants to review how Claude Code has been performing, find what went wrong or got repeated, cut wasted tool calls, diagnose why a session went in circles, or decide what should be written into a CLAUDE.md, a settings file, or a skill so the agent gets it right up front. Triggers on "review the last sessions", "revê as últimas conversas", "o que correu mal ontem", "why does Claude keep doing X", "optimize my Claude Code flow", "what should go in my CLAUDE.md", and on any retrospective of agent behaviour across one or several repositories.
---

# Review Past Performance

## What this is

A retrospective on the agent, not on the user's code. The evidence is the local
transcript store: `~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`, one JSON
record per event, holding every prompt, reply, tool call, tool result, and token
count. `scripts/scan_transcripts.py` reads it.

The output is a **plan with named fixes in named files**, not a list of
observations. A finding that does not end in "add this line to that file",
"remove this rule", "grant this permission", or "build this skill" is not a
finding, it is a complaint.

## Non-negotiables

- **Evidence before conclusion.** The counters say where it hurt. Only the
  replay says why. Never write a finding from a counter alone.
- **Two instances or it is not a pattern.** One bad session is an anecdote. Say
  so and move on. Recommending a permanent rule from a single event is how
  instruction files rot.
- **Never propose adding a rule that already exists.** Grep the repo's
  `CLAUDE.md` first. If the rule is there and was still broken, the fix is
  wording, placement, or a hook — not a second copy.
- **NDA repos stay local.** Some repos (e.g. `fisbu/`) are under NDA. Transcript
  excerpts from them never go into an artifact, a shared page, or another repo's
  files. Quote them only in the reply and in files inside that same repo.
- **No new files without the user's approval.** Propose the diff, name the file,
  wait. This applies to the report itself: deliver it in the reply by default.
- Reply in European Portuguese. Anything written into a file follows that repo's
  own language convention.

## Workflow

### 1. Scan

The script sits next to this file. The session cwd is the user's repo, not the
skill folder, so run it by its own path:

```bash
python3 ~/.claude/skills/review-past-performance/scripts/scan_transcripts.py --hours 24
```

Flags: `--hours N` (widen when 24h is thin), `--project <substring>` (one repo),
`--session <id>`, `--json` (machine-readable), `--dump` (chronological replay).

Read the digest end to end before touching anything. The sessions table is
sorted by friction; the sections below it are the raw signals.

Then read the config surface before drawing any conclusion. It is evidence,
not just where fixes land:

```bash
cat ~/.claude/CLAUDE.md ~/.claude/settings.json
cat <repo>/CLAUDE.md <repo>/.claude/settings*.json
ls ~/.claude/commands/ <repo>/.claude/commands/ 2>/dev/null
```

Two failure modes this catches, both seen in practice: proposing a line for a
file the user has edited since the last review, and anchoring a new rule to a
rule that does not exist in the file it cites. It is also what makes the
"never propose a rule that already exists" non-negotiable checkable instead
of aspirational.

### 2. Get the evidence

For each candidate finding, replay the session around it:

```bash
python3 ~/.claude/skills/review-past-performance/scripts/scan_transcripts.py \
  --session <id> --dump | sed -n '40,120p'
```

Read the user turn *before* the friction and the two agent turns *after* it.
That triplet is what tells you whether the agent misread the request, missed
context it could have had, or was blocked by something outside its control.

Budget: replay the top three-to-five friction sessions. Do not replay all of
them; this skill should not itself be an example of waste.

### 3. Classify each signal

| Signal in the digest | Usually means | Fix lands in |
|---|---|---|
| Interruption (user hit stop) | Agent went down a path the user could already see was wrong | Wording of the task; a plan-first rule |
| Correction after a tool run | Agent acted before it understood | "Plan before executing" threshold in `CLAUDE.md` |
| User re-stating a rule | The rule exists but is not being read or is buried | Move it up, sharpen it, or make it a hook |
| Tool error | Environment, wrong assumption, or a tool used blind | A gotcha line in `CLAUDE.md`; sometimes a script |
| Permission rejection | Command the user did not want run | `settings.json` allowlist, or a narrower default |
| Repeated identical tool call | Agent lost its own result | Batching; reading once and holding it |
| File read 3+ times | The file is load-bearing and being rediscovered | Name it in `CLAUDE.md` as required reading |
| Sessions restarted on the same prompt | The first session failed or lost context | The real cause is in that first session — replay it |
| Repos worked in parallel | Cross-repo confusion risk | A shared fact in the parent-folder `CLAUDE.md` |
| Heavy MCP fan-out (many `get_issue`) | No cheap way to get the same context | A batched call, a list query, or a skill |

Separate **agent faults** from **setup faults**. An agent that could not have
known something needs a file changed, not a scolding. An agent that had the
information and ignored it needs the instruction sharpened or moved.

### 4. Route every fix

Do not put everything in `CLAUDE.md`. That is the failure mode this review
exists to prevent.

| Kind of fix | Where it goes |
|---|---|
| Rule about how to work in this repo | that repo's `CLAUDE.md` |
| Fact that changes (dates, status, names, palette) | that repo's `CONTEXT.md` or equivalent |
| Rule that holds across every repo | `~/.claude/CLAUDE.md` |
| Fact shared by sibling repos | the parent folder's `CLAUDE.md` |
| Repeated multi-step workflow | a skill in `~/Dev/claude/mandim-skills/` |
| Command approvals, env, automated behaviour | `settings.json` / hooks (use the `update-config` skill) |
| Something learned about the user, not the code | a memory file |

Before proposing a `CLAUDE.md` line, check what it displaces. Every instruction
file has a working length; adding always costs.

### 5. Deliver

Reply with these five sections, in this order, nothing else:

1. **O que aconteceu** — volume and friction in three or four lines. Numbers from
   the scan, no prose padding.
2. **Padrões** — one block per pattern, and only patterns seen twice or more.
   Each block: what happened, the sessions it happened in, one quoted line of
   evidence, and the cause.
3. **Correções por repositório** — grouped by repo. Each item: exact file, the
   exact line to add or remove, and which pattern it kills.
4. **Correções transversais** — the same, for global config, parent-folder files,
   skills, and settings.
5. **O que o agente devia saber antes de entrar** — the pre-flight briefing. Two
   lists: what to know *before opening a repo* (its source of truth, what it must
   never invent, its one hard trap), and what to know *when several repos are
   open at once* (which facts are repo-local and must not travel, which naming
   or language conventions differ, which repo is under NDA).

Then ask which fixes to apply. Apply only what is approved, one file at a time,
showing each diff.

## Anti-patterns of this review

- Reporting the token count as if it were a problem. It is context, not a
  finding. A 20M-token session that got the work done was fine.
- Turning a one-off environment error into a permanent rule.
- Proposing a new `.md` "process" file. The fix belongs in an existing file.
- Recommending "be more careful" or "read the context first" in any wording.
  That is not a fix, it is a wish. If the agent missed context, say which file
  it should have read and make that file findable.
- Reviewing the user's judgement. The subject is the agent and the setup.
