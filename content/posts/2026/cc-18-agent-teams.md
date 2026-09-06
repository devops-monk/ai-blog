---
title: "Agent Teams & Parallel Work"
image: /images/articles/cc-18-agent-teams.webp
toc: true
date: 2026-09-06T00:10:00+00:00
description: "Four ways to run Claude sessions at once, and the questions that pick between them. Agent view, agent teams and their experimental sharp edges, cross-session messaging, and when parallelism actually pays for itself."
tags: ["claude-code", "agent-teams", "parallel", "agent-view", "orchestration"]
categories: ["Fundamentals"]
url: /2026/09/agent-teams-and-parallel-work/
series: "Part 5 — Agents & Autonomy"
series_order: 2
---

## Overview

This chapter covers:

- Four ways to parallelise, and the three questions that choose between them
- Agent view — handing off work and checking back, rather than watching it
- Agent teams: what a lead, a task list and a mailbox actually are — and why enabling them changes ordinary delegation
- The file-conflict problem teams have that subagents don't
- When parallelism costs more than it saves

## Four shapes, not one

Chapter 17 was delegation *inside* one conversation. This is the rest of the family, and they differ by **who coordinates**:

| Approach | What it gives you | Coordinator |
|---|---|---|
| **Subagents** | Workers in your session that do a side task and return a summary | Claude, in your conversation |
| **Agent view** | One screen to dispatch and monitor background sessions — `claude agents` | **You**, checking back |
| **Agent teams** | Coordinated sessions with a shared task list and messaging | Claude, as a lead |
| **Dynamic workflows** | A script that runs many subagents and cross-checks their results | **A script**, not turn-by-turn judgment |

Two are research preview or experimental — agent view and agent teams respectively — which is worth knowing before you build a habit on either.

Three more things support this work without being ways to run agents. **Worktrees** (Chapter 9) give each session its own checkout. **Cross-session messaging** lets Claude talk to your other sessions. And **`/batch`** is a skill that splits one change into 5–30 worktree-isolated subagents, each opening a PR — a packaged use of the first two, not a fifth approach.

## Which one?

<div class="pk-box"> <div class="pk-qs" id="pk-qs"></div> <div class="pk-out" id="pk-out"></div> </div> <script> (function () { var Q = [ { k: "who", n: "Who should coordinate?", opts: [ { v: "claude", l: "Claude, in my conversation" }, { v: "me", l: "Me — hand off, check back" }, { v: "lead", l: "Claude, as a lead over workers" }, { v: "script", l: "A script, not turn-by-turn judgment" } ] }, { k: "talk", n: "Do the workers need to talk to each other?", opts: [ { v: "no", l: "No — each reports back" }, { v: "yes", l: "Yes — they need to disagree" } ] }, { k: "files", n: "Do the tasks touch the same files?", opts: [ { v: "no", l: "No — separate areas" }, { v: "yes", l: "Yes, or I am not sure" } ] } ]; var A = { who: "claude", talk: "no", files: "no" }; var qEl = document.getElementById("pk-qs"), oEl = document.getElementById("pk-out"); function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); } function verdict() { var notes = []; var pick, why; if (A.who === "script") { pick = "Dynamic workflows"; why = "A script holds the plan, so the work survives being bigger than one turn of Claude's judgment — a codebase-wide audit, a large migration, or findings that must be cross-checked against each other."; } else if (A.who === "me") { pick = "Agent view"; why = "<code>claude agents</code> dispatches sessions and shows you their state on one screen. Research preview."; notes.push({ c: "ok", t: "Each dispatched session gets its own worktree automatically, so file conflicts are handled for you." }); } else if (A.who === "lead" || A.talk === "yes") { pick = "Agent teams"; why = "Teammates are full sessions that message each other directly and share a task list, so they can challenge each other rather than each reporting up."; notes.push({ c: "warn", t: "Experimental and off by default — set CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1. Enabling it also makes named subagents launch as teammates, so teams form during delegation you did not ask for." }); notes.push({ c: "warn", t: "Tokens scale linearly: every teammate is a separate Claude instance. Start with 3 to 5." }); if (A.files === "yes") { notes.push({ c: "bad", t: "Teams do NOT isolate teammates in worktrees. Two teammates editing one file overwrite each other — partition the work by file owner before you start, or pick a different approach." }); } } else { pick = "Subagents"; why = "A worker inside your session absorbs the verbose part and returns a summary. The cheapest option, and usually the right one."; if (A.files === "yes") { notes.push({ c: "ok", t: "Add isolation: worktree to the subagent so its edits land in a separate checkout." }); } notes.push({ c: "ok", t: "If the task needs your conversation rather than a fresh start, use a fork — /subtask — instead." }); } return { pick: pick, why: why, notes: notes }; } function render() { qEl.innerHTML = Q.map(function (q) { return "<div class=\"pk-q\"><span class=\"pk-qn\">" + esc(q.n) + "</span><div class=\"pk-opts\">" + q.opts.map(function (o) { return "<button type=\"button\" class=\"pk-o" + (A[q.k] === o.v ? " on" : "") + "\" data-k=\"" + q.k + "\" data-v=\"" + o.v + "\">" + esc(o.l) + "</button>"; }).join("") + "</div></div>"; }).join(""); var r = verdict(); oEl.innerHTML = "<span class=\"pk-pick\">" + esc(r.pick) + "</span><p class=\"pk-why\">" + r.why + "</p>" + r.notes.map(function (n) { return "<p class=\"pk-n pk-" + n.c + "\">" + esc(n.t) + "</p>"; }).join(""); Array.prototype.forEach.call(qEl.querySelectorAll(".pk-o"), function (b) { b.addEventListener("click", function () { A[b.getAttribute("data-k")] = b.getAttribute("data-v"); render(); }); }); } render(); })(); </script>

## Agent view

`claude agents` opens one screen showing every background session, its state, and which ones need you. Start work, leave, come back.

The property that makes it usable: **agent view moves each dispatched session into its own worktree automatically.** Chapter 9's isolation, applied without you asking for it — which is exactly the difference between "several sessions" and "several sessions that overwrite each other".

## Agent teams

A team is **several full Claude Code sessions** with one acting as lead. Not subagents — each teammate is an independent session with its own context window that you can talk to directly.

> **Experimental and off by default.** Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` to enable. Without it no team is set up, no directories are written, and Claude will not spawn teammates.

Four parts:

| Part | Is |
|---|---|
| **Lead** | Your main session — spawns teammates, assigns work, synthesises results |
| **Teammates** | Separate Claude Code instances, each with its own context window |
| **Task list** | Shared work items that teammates claim, with dependencies |
| **Mailbox** | A JSON file per agent at `~/.claude/teams/{team}/inboxes/{agent}.json` |

Teammates **message each other directly** rather than reporting up. That is the real difference from subagents: a subagent returns a result to whoever spawned it, while teammates can disagree with each other.

### Enabling it changes ordinary delegation

This is the sharp edge, and it is not obvious:

> Claude names subagents on its own so it can message them later. **While agent teams are enabled, a named subagent launches as a teammate.** Teams can form during delegation you never framed as team work.

If you wanted subagents, set the variable to `0`. You do not need a new session — the value is re-read each time Claude spawns one.

### Talking to them

Two display modes. **In-process** (the default) runs every teammate in your terminal: arrow keys to select in the agent panel, `Enter` to open a transcript and type to it directly, `x` to stop one. **Split panes** gives each its own pane and needs tmux or iTerm2 with the `it2` CLI.

One mechanic worth knowing while viewing a teammate: plain text and skills go to *that teammate*, but built-in commands still run in the lead's session. A teammate's model is fixed at spawn, so `/model` there changes the lead's.

### Permissions

**Teammates start with the lead's permission settings**, including `--dangerously-skip-permissions` if the lead has it. Their permission prompts surface in the lead's session for you to answer.

The safeguard that matters is Chapter 14's, generalised: when one agent messages another, **Claude Code tells the recipient the message came from another Claude session, not from you.** A teammate cannot approve a prompt on your behalf, and a teammate denied an action cannot relay it to another to get it through. In auto mode the classifier reviews every inter-agent message and treats a relayed approval claim as untrusted input.

### Teams do not isolate teammates

Subagents can each get a worktree. **Agent teams do not** — every teammate works in the same checkout. So the guidance is manual and unavoidable: **partition the work so each teammate owns a different set of files.** Two teammates editing one file overwrite each other.

That single fact does more to decide whether a team fits your task than anything else on this page.

### Limitations worth reading first

Experimental means experimental:

- **`/resume` and `/rewind` do not restore in-process teammates.** The lead may try to message agents that no longer exist; tell it to spawn new ones.
- **Task status lags.** Teammates sometimes fail to mark work complete, which blocks dependent tasks.
- **One team per session, no nesting.** Teammates cannot spawn teammates, and the lead is fixed for the session's lifetime.
- **Shutdown is slow** — a teammate finishes its current tool call first.

## Cross-session messaging

Between "one session" and "a team" sits the option most people miss: **Claude can list and message your other Claude Code sessions** — on this machine, another machine, or the web — so sessions you started yourself can pass findings to each other.

No lead, no shared task list, no experimental flag. If you already run three sessions in three worktrees, this connects them.

## When it actually pays

Parallelism has a real cost: **each teammate is a separate Claude instance, so tokens scale linearly with the team**. And in-process teammates fall outside the main-conversation cache bucket, so they get the five-minute TTL even on a subscription unless you set `subagentPromptCacheTtl`.

It pays when the work is genuinely independent:

- **Review from several angles** — security, performance, test coverage, each with its own lens.
- **Competing hypotheses.** The strongest case on the list, because it fixes a failure mode rather than just going faster: one investigator finds a plausible explanation and stops. Several actively trying to disprove each other defeats that anchoring, and the theory that survives is more likely to be right.
- **Separate modules**, one owner each.
- **Cross-layer work** — frontend, backend, tests.

It does not pay for sequential work, same-file edits, or anything with many dependencies. **Start with 3–5 teammates**; three focused ones beat five scattered ones, and if you have fifteen independent tasks, three teammates is still the right starting point.

And start with **research and review** rather than parallel implementation — clear boundaries, no file conflicts, and you see whether the coordination overhead is worth it before you bet a refactor on it.

## Summary

- Four approaches, chosen by **who coordinates**: Claude in one conversation (subagents), you (agent view), Claude as a lead (teams), or a script (workflows).
- **Agent view puts each dispatched session in its own worktree automatically.**
- Agent teams are **experimental and off by default** — `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
- **Enabling them makes named subagents launch as teammates**, so teams form during delegation you did not ask for.
- Teammates **message each other** rather than reporting up, and inherit the lead's permission mode.
- **A message from another agent is never treated as your approval.**
- **Teams do not isolate teammates in worktrees** — partition the files yourself.
- `/resume` does not restore in-process teammates.
- Tokens scale linearly with the team. **Start at 3–5, with research and review.**
- Full reference: [running agents in parallel](https://code.claude.com/docs/en/agents), [agent teams](https://code.claude.com/docs/en/agent-teams), [agent view](https://code.claude.com/docs/en/agent-view), [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging).

Chapter 19 is the other kind of autonomy: work that runs when you are not there at all.
