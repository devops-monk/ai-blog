---
title: "Sub-Agents"
image: /images/articles/cc-17-subagents.webp
toc: true
date: 2026-09-05T23:50:00+00:00
description: "Delegation as context management. What a subagent starts with, what it deliberately does not inherit, when Claude picks one on its own, and the difference between a subagent and a fork."
tags: ["claude-code", "subagents", "context-engineering", "delegation", "agents"]
categories: ["Fundamentals"]
url: /2026/09/subagents/
series: "Part 5 — Agents & Autonomy"
series_order: 1
---

## Overview

This chapter covers:

- Why one prompt with four tasks in it drowns your context window
- What a subagent starts with — and the four things it deliberately does not inherit
- The three built-ins, and which of them skips your `CLAUDE.md` on purpose
- `memory`, which gives an agent the one thing a fresh context window cannot have
- Foreground, background, and the fork — three ways to delegate that behave differently

## The problem is not capability

Ask for four things at once:

```text
Run the full test suite, explore the authentication module, fetch the
latest API docs, then fix the failing tests.
```

Claude will do it. But within minutes your window holds hundreds of lines of test output, a wall of documentation, and the contents of files nobody will look at again — all of it crowding out the part you actually care about, which is the fix.

Chapter 8 gave the arithmetic. This is the mechanism that fixes it: **hand the noisy work to something with its own context window, and take back only the summary.**

## A subagent is a blank slate

That phrase is the whole design. A subagent starts fresh, cut off from your conversation, holding only what you handed it.

What it **does** get:

| | |
|---|---|
| **Its own system prompt** | The Markdown body of its definition file — not Claude Code's |
| **A task message** | The handoff Claude writes when delegating |
| **`CLAUDE.md`** | The full hierarchy — with an exception below |
| **Git status** | A snapshot from when the parent session started |
| **Preloaded skills** | Whole content of anything in its `skills` field |

What it **does not** get, and each omission is deliberate:

- **Your conversation history.** It has no idea what you have been discussing. For a generic subagent you must re-explain the situation — that is the cost of the isolation, not a bug in it.
- **Your output style** (Chapter 10). It runs its own system prompt.
- **Your auto memory** (Chapter 7). It gets its own, if you enable it.
- **`AskUserQuestion`.** It cannot stop and ask you something. Ambiguity has to be resolved in its instructions, before it starts.

Chapter 12 put hooks *outside* the context window. Subagents belong in the same column, for a different reason: a hook never enters your window, and a subagent has **a window of its own**.

## The three built-ins

You get three without writing anything:

| Agent | Tools | Model |
|---|---|---|
| **Explore** | Read-only | Inherits, capped at Opus on the Claude API |
| **Plan** | Read-only | Inherits — this is what plan mode uses to research |
| **general-purpose** | Everything a subagent can have | Inherits |

> **Explore and Plan skip your `CLAUDE.md` and git status on purpose.** Their job is to look things up and report back, and loading your whole instruction set into a lookup would defeat the point of delegating it. If you want an Explore agent that behaves differently, define your own named `Explore` — a user or project definition overrides the built-in.

## Watch the window

<div class="sa-box"> <p class="sa-task">Task: <strong>run the full test suite, explore the auth module, fetch the API docs, then fix the failing tests</strong></p> <div class="sa-items" id="sa-items"></div> <div class="sa-bars"> <div class="sa-row"><span class="sa-rl">Your window</span><div class="sa-track"><span class="sa-fill sa-main" id="sa-bar-main"></span></div><span class="sa-v" id="sa-v-main"></span></div> <div class="sa-row"><span class="sa-rl">Delegated elsewhere</span><div class="sa-track"><span class="sa-fill sa-sub" id="sa-bar-sub"></span></div><span class="sa-v" id="sa-v-sub"></span></div> </div> <div class="sa-read" id="sa-read"></div> </div> <script> (function () { var MAX = 200000, SUMMARY = 400, HANDOFF = 150; var W = [ { k: "tests", n: "Run the test suite", t: 18000, d: true, why: "Hundreds of lines of output, and you need three of them." }, { k: "explore", n: "Explore the auth module", t: 24000, d: true, why: "Eleven files read to answer one question about token refresh." }, { k: "docs", n: "Fetch the API docs", t: 15000, d: true, why: "A wall of reference text, relevant for one paragraph." }, { k: "fix", n: "Fix the failing tests", t: 6000, d: false, why: "The actual work. Needs your conversation, so keep it here." } ]; var state = {}; W.forEach(function (w) { state[w.k] = w.d; }); var iEl = document.getElementById("sa-items"), rEl = document.getElementById("sa-read"); function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); } function fmt(n) { return n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "K" : String(Math.round(n)); } function render() { iEl.innerHTML = W.map(function (w) { var on = state[w.k]; return "<label class=\"sa-item" + (on ? " on" : "") + "\"><input type=\"checkbox\" data-k=\"" + w.k + "\"" + (on ? " checked" : "") + " /><span class=\"sa-n\">" + esc(w.n) + "</span>" + "<span class=\"sa-t\">" + fmt(w.t) + "</span>" + "<span class=\"sa-why\">" + esc(w.why) + "</span></label>"; }).join(""); var main = 8000, sub = 0, delegated = 0; W.forEach(function (w) { if (state[w.k]) { sub += w.t; main += SUMMARY + HANDOFF; delegated++; } else { main += w.t; } }); document.getElementById("sa-bar-main").style.width = Math.min(main / MAX, 1) * 100 + "%"; document.getElementById("sa-bar-sub").style.width = Math.min(sub / MAX, 1) * 100 + "%"; document.getElementById("sa-v-main").textContent = fmt(main); document.getElementById("sa-v-sub").textContent = fmt(sub); var none = 8000 + W.reduce(function (a, w) { return a + w.t; }, 0); var saved = none - main; rEl.className = "sa-read " + (delegated ? "sa-good" : "sa-hot"); rEl.innerHTML = delegated === 0 ? "<strong>" + fmt(main) + "</strong> in your window, and " + Math.round(main / MAX * 100) + "% of it is output you will read once. Nothing is delegated — this is the shape the chapter opens on." : "<strong>" + fmt(main) + "</strong> in your window instead of <strong>" + fmt(none) + "</strong> — " + fmt(saved) + " saved across " + delegated + " subagent" + (delegated === 1 ? "" : "s") + ". " + "Each one costs a handoff in and a summary back, about " + fmt(SUMMARY + HANDOFF) + ", however much it reads." + (state.fix ? " <em>Delegating the fix is the questionable one: it needs your conversation, and a subagent does not have it.</em>" : ""); Array.prototype.forEach.call(iEl.querySelectorAll("input"), function (i) { i.addEventListener("change", function () { state[i.getAttribute("data-k")] = i.checked; render(); }); }); } render(); })(); </script>

## Writing one

A subagent is a Markdown file in `.claude/agents/` or `~/.claude/agents/` — YAML frontmatter, then a system prompt:

```markdown
---
name: test-runner
description: Runs the test suite and reports only what failed. Use proactively after code changes.
tools: Bash, Read, Grep
model: sonnet
---

Run the project's test suite. Report only failures: the test name, the
assertion, and the file and line. Do not summarise passing tests, and do
not attempt fixes unless asked.
```

> **The deck's `/agents` wizard is gone.** It created agents interactively up to v2.1.197; from v2.1.198 the command just points you at the directory. The replacement is better anyway — describe what you want and Claude writes the file, frontmatter and all.

### The fields that change behaviour

There are around eighteen. These five do the work:

| Field | Why |
|---|---|
| `description` | **The delegation trigger.** Claude reads this to decide whether to hand work over |
| `tools` / `disallowedTools` | An allowlist and a denylist. Denylist applies first |
| `model` | Route cheap work to a cheap model — the lever people forget |
| `memory` | `user`, `project` or `local` |
| `isolation: worktree` | Its own checkout, with Chapter 9's enforcement |

**Keep `description` short.** Every agent's description sits in your context, and past a 15,000-token total you get a startup warning. Detail belongs in the system prompt, which only loads when the agent actually runs — the same progressive-disclosure argument as skills.

`model` is where the cost saving is. A test-runner that reads output and reports failures does not need your main model; `model: haiku` on that one agent changes what a busy session costs. `CLAUDE_CODE_SUBAGENT_MODEL` sets a default for all of them.

### Restricting tools is the point, not a precaution

```yaml
tools: Read, Grep, Glob
```

A research agent that *cannot* write is a different thing from one you asked not to. This is Chapter 12's distinction — instruction versus guarantee — applied to delegation.

Two mechanics worth knowing: `disallowedTools: mcp__*` strips every MCP tool, and **if `tools` resolves to nothing the agent fails to start** with an error naming the entries it could not resolve. Before v2.1.208 it launched with no tools at all and simply failed at the first step, which was much harder to diagnose.

## Memory gives it a past

A fresh context window every time is the point — and the limitation. `memory` is the exception:

```yaml
memory: project
```

| Value | Lives in | For |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` | Learning that should follow you between projects |
| `project` | `.claude/agent-memory/<name>/` | Project knowledge, committed with the repo |
| `local` | `.claude/agent-memory-local/<name>/` | Project knowledge, kept off git |

With it on, the agent's system prompt gains memory instructions, **the first 200 lines of its `MEMORY.md` load automatically** — Chapter 7's ceiling, applied per agent — and `Read`, `Write` and `Edit` are enabled so it can maintain the file.

The habit that makes it pay: tell it when to look and when to write. *"Check your memory for similar issues before analysing this code"* at the start; *"save what you learned"* at the end. A reviewer that has seen your codebase fifty times is worth more than one seeing it fresh.

It depends on `autoMemoryEnabled`. Turn auto memory off and the `memory` field does nothing.

## How work reaches an agent

**Automatically.** Claude decides from your wording, the agent's `description`, and the current context. Adding *"use proactively"* to a description pushes it towards delegating without being asked.

**Explicitly**, in plain language — *"use the test-runner subagent to fix the failing tests"* — or with `@` for a guarantee: `@"code-reviewer (agent)"`.

**For the whole session**, with `claude --agent code-reviewer` or an `agent` key in settings. The session runs as that agent.

## Foreground, background, fork

Three shapes, and the differences are not cosmetic:

| | Foreground | Background |
|---|---|---|
| Your session | Blocked until it finishes | Keeps going |
| Tools | The full set | **A reduced set** |
| Permission prompts | Passed straight to you | Surfaced in your session; `Esc` denies one call |
| Results | Immediately | A later turn, after a notification |

In an interactive session **fork mode is on by default, so spawned subagents run in the background.** That is why Chapter 11 warned that a background forked skill's edits fall outside your checkpoints — it is the same mechanism.

A **fork** is the exception to everything above. It inherits the parent conversation entirely: system prompt, tools, model, full history. So it needs no re-explaining, and its tool calls stay out of your window — you get only the result.

```text
/subtask draft unit tests for the parser changes so far
```

The rule of thumb: **a subagent for work that needs no context, a fork for work that needs all of it.**

## The bill

Delegation is not free, and three limits are worth knowing before you fan out:

- **20 concurrent subagents** by default. `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` raises it.
- **Three layers of nesting.** A subagent can spawn subagents, three deep from your conversation; at the limit the `Agent` tool is withheld. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` set to `1` disables nesting.
- **Its own cache.** From Chapter 8: a subagent starts a fresh prompt cache, and subagents sit outside the main-conversation TTL bucket — five minutes even on a subscription, unless you set `subagentPromptCacheTtl`.

Which is the honest summary of when to delegate: **when the output would be verbose and the input is small.** A subagent that needs three paragraphs of context to do one file read has cost you more than it saved.

## Summary

- A subagent is a **blank slate with its own context window**. Verbose work goes in, a summary comes out.
- It does not inherit your history, output style, auto memory, or the ability to ask you a question.
- **Explore and Plan skip `CLAUDE.md` deliberately.** Define your own `Explore` to change that.
- `description` is the **delegation trigger** and lives in your context — keep it short, put detail in the system prompt.
- **`model` is the cost lever.** Route noisy, simple work to a cheap model.
- Restricting `tools` is a guarantee, not a request. An empty resolved list fails at startup rather than silently.
- `memory` gives an agent a past: `user`, `project` or `local`, with the same 200-line ceiling as Chapter 7.
- **Fork mode is on by default in interactive sessions**, so spawned agents run in the background with a reduced tool set.
- **Subagent for work needing no context; fork for work needing all of it.**
- Full reference: [subagents](https://code.claude.com/docs/en/sub-agents).

Chapter 18 takes this further: several agents working at once, on the same repository, without colliding.
