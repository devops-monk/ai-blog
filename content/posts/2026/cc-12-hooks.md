---
title: "Hooks"
image: /images/articles/cc-12-hooks.webp
toc: true
date: 2026-09-05T21:00:00+00:00
description: "The layer that turns an instruction into a guarantee. Where each event fires in a turn, which ones can block, the exit-code contract, and the asymmetry that lets a hook tighten your permissions but never loosen them."
tags: ["claude-code", "hooks", "automation", "permissions", "lifecycle"]
categories: ["Fundamentals"]
url: /2026/09/claude-code-hooks/
series: "Part 3 — Teaching Claude New Tricks"
series_order: 3
---

## Overview

This chapter covers:

- Why a hook is the answer whenever "usually" is not good enough
- Where each event fires in a turn, and the subset that can actually **block**
- The exit-code contract — and why exit `2` beats any JSON you also print
- The asymmetry that makes hooks safe to hand to an organisation: they tighten, never loosen
- The three failure modes that account for most hooks that "don't fire"

## Instructions versus guarantees

Chapter 6 kept deferring to this chapter, and Chapter 11 did too. Both for the same reason: `CLAUDE.md` and skills are **context**. Claude reads them and tries to comply. That is usually enough, and occasionally it is not.

A hook is a command Claude Code runs at a fixed point in its lifecycle, **regardless of what Claude decides**. "Run the formatter after every edit" as a `CLAUDE.md` line is a suggestion followed most of the time. As a `PostToolUse` hook it is a fact.

The test from Chapter 6, restated: *does this need to happen every time, or usually?* Every time is a hook.

## Where hooks fire

There are 33 events. Rather than list them, here is a turn with the main ones in place:

<div class="hk-box"> <div class="hk-cols"> <div class="hk-left" id="hk-left"></div> <div class="hk-right" id="hk-right"></div> </div> </div> <script> (function () { var PHASES = [ { p: "Session", events: [ { n: "SessionStart", b: false, m: "startup, resume, clear, compact, fork", w: "A session begins or resumes.", u: "Load environment context, or re-inject what compaction dropped by matching <code>compact</code>." }, { n: "InstructionsLoaded", b: false, m: "session_start, path_glob_match, compact", w: "A CLAUDE.md or rule file enters context — at startup and lazily during the session.", u: "The only direct evidence of which instruction files actually loaded. Chapter 7's debugging tool." } ] }, { p: "Your prompt", events: [ { n: "UserPromptSubmit", b: true, m: "none", w: "You submit a prompt, before Claude sees it.", u: "Add context to every prompt, or refuse one outright. Timeout drops to 30s here." }, { n: "UserPromptExpansion", b: true, m: "command name", w: "A typed command expands into a prompt.", u: "Gate a specific slash command." } ] }, { p: "Each tool call", events: [ { n: "PreToolUse", b: true, m: "tool name", w: "Before a tool call runs — ahead of every permission-mode check.", u: "The enforcement point. A deny here holds even under bypassPermissions." }, { n: "PermissionRequest", b: false, m: "tool name", w: "Claude Code is about to prompt you.", u: "Auto-answer prompts. Needs an actual prompt to exist, so not plain -p runs." }, { n: "PermissionDenied", b: false, m: "tool name", w: "Auto mode denied a call.", u: "Log denials, or return retry: true to let the model try again." }, { n: "PostToolUse", b: false, m: "tool name", w: "After a tool call succeeds.", u: "Format, lint, regenerate. Cannot undo anything — the tool already ran." }, { n: "PostToolUseFailure", b: false, m: "tool name", w: "After a tool call fails.", u: "Capture failures for triage." }, { n: "PostToolBatch", b: true, m: "none", w: "After a batch of parallel tool calls resolves, before the next model call.", u: "Check the combined result of a parallel batch." } ] }, { p: "End of turn", events: [ { n: "Stop", b: true, m: "none", w: "Claude finishes responding. Not only at task completion, and never on your interrupt.", u: "Keep Claude working until a condition holds. Overridden after 8 consecutive blocks — check stop_hook_active." }, { n: "StopFailure", b: false, m: "rate_limit, overloaded, ...", w: "The turn ended on an API error.", u: "Alert or retry on a specific error class." }, { n: "MessageDisplay", b: false, m: "none", w: "Assistant text is being displayed. 10s timeout.", u: "Mirror output somewhere else." } ] }, { p: "Around the session", events: [ { n: "PreCompact", b: false, m: "manual, auto", w: "Before compaction.", u: "Snapshot state you are about to lose." }, { n: "PostCompact", b: false, m: "manual, auto", w: "After compaction completes.", u: "Pairs with SessionStart matching compact." }, { n: "PreModelSwitch", b: true, m: "model name", w: "Before a requested model switch.", u: "Require confirmation, or refuse the switch. A timeout here does block." }, { n: "SubagentStart", b: false, m: "agent type", w: "A subagent spawns.", u: "Tag or log subagent work." }, { n: "SubagentStop", b: true, m: "agent type", w: "A subagent finishes.", u: "Validate what it produced before accepting it." }, { n: "ConfigChange", b: true, m: "user_settings, project_settings, skills, ...", w: "A configuration file changes mid-session.", u: "Audit or veto configuration changes." }, { n: "CwdChanged", b: false, m: "none", w: "The working directory changes, including from a cd Claude ran.", u: "Reactive environment management — direnv and friends." }, { n: "SessionEnd", b: false, m: "clear, resume, logout, ...", w: "The session terminates.", u: "Archive the transcript. All SessionEnd hooks share a 1.5s budget." } ] } ]; var flat = []; PHASES.forEach(function (ph) { ph.events.forEach(function (e) { e.phase = ph.p; flat.push(e); }); }); var sel = "PreToolUse"; var lEl = document.getElementById("hk-left"), rEl = document.getElementById("hk-right"); function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); } function render() { lEl.innerHTML = PHASES.map(function (ph) { return "<div class=\"hk-ph\"><span class=\"hk-phn\">" + esc(ph.p) + "</span>" + ph.events.map(function (e) { return "<button type=\"button\" class=\"hk-ev" + (e.n === sel ? " on" : "") + (e.b ? " blk" : "") + "\" data-n=\"" + e.n + "\">" + esc(e.n) + (e.b ? "<i>blocks</i>" : "") + "</button>"; }).join("") + "</div>"; }).join(""); var e = flat.filter(function (x) { return x.n === sel; })[0]; rEl.innerHTML = "<span class=\"hk-name\">" + esc(e.n) + "</span>" + "<div class=\"hk-tags\"><span class=\"hk-tag " + (e.b ? "hk-yes" : "hk-no") + "\">" + (e.b ? "can block" : "observational") + "</span>" + "<span class=\"hk-tag hk-m\">matcher: " + esc(e.m) + "</span></div>" + "<p class=\"hk-w\"><strong>Fires:</strong> " + esc(e.w) + "</p>" + "<p class=\"hk-u\"><strong>Good for:</strong> " + e.u + "</p>"; Array.prototype.forEach.call(lEl.querySelectorAll(".hk-ev"), function (b) { b.addEventListener("click", function () { sel = b.getAttribute("data-n"); render(); }); }); } render(); })(); </script>

The distinction that matters is the **Blocks** column. Most events are observational — `PostToolUse` cannot undo anything, because the tool already ran. The blocking set is small, and it is where enforcement lives: `PreToolUse`, `UserPromptSubmit`, `Stop`, `PreModelSwitch`, `SubagentStop`, `PostToolBatch`, `ConfigChange`, and a few others.

## Configuration

Hooks are a `hooks` block in any settings file, so Chapter 5's precedence and scopes apply unchanged:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/format.sh",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

`${CLAUDE_PROJECT_DIR}` resolves to the project root and stays constant across worktrees — use it rather than a relative path, which resolves against wherever Claude happens to have `cd`'d.

### Matchers are three syntaxes wearing one hat

The characters in a matcher decide how it is interpreted, which is not obvious and is a common source of "my hook never fires":

| Matcher contains | Treated as |
|---|---|
| `*`, empty, or omitted | Match everything |
| Letters, digits, `_`, `-`, spaces, `,`, `|` | Exact string or list — `Bash`, `Edit\|Write` |
| **Anything else** | An unanchored JavaScript regex — `^Notebook`, `mcp__memory__.*` |

Matchers are **case-sensitive**, and what they match against depends on the event: a tool name for the tool events, but `startup|resume|clear|compact|fork` for `SessionStart`, `manual|auto` for `PreCompact`, and a model name for the model-switch events. Several events — `Stop`, `UserPromptSubmit`, `PostToolBatch`, `CwdChanged` — take no matcher at all.

### Five handler types

`command` is the one you will write. The others exist for cases a shell script handles badly:

| Type | Runs |
|---|---|
| `command` | A shell command; JSON on stdin, JSON or text on stdout |
| `http` | A POST to a URL, event as the body |
| `mcp_tool` | A tool on a connected MCP server |
| `prompt` | A single-turn LLM evaluation |
| `agent` | A multi-turn subagent with tools — experimental |

`prompt` and `agent` are the interesting pair: they exist for decisions that need **judgment rather than a rule**, which is otherwise the gap between a hook and a permission rule.

## The contract

Your hook gets JSON on stdin — `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, plus event-specific fields like `tool_name` and `tool_input`. It answers through its exit code and stdout.

| Exit | Meaning |
|---|---|
| `0` | Success. Stdout is parsed as JSON if it looks like an object, otherwise treated as text |
| **`2`** | **Blocking error.** Blocks the action where the event supports it; the reason comes from stderr |
| Anything else | Non-blocking. Valid JSON decision fields are still honoured |

> **Exit 2 wins over JSON on the same invocation.** If your script exits 2, whatever it printed to stdout cannot override that. Pick one mechanism per hook.

The JSON form is more expressive:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Migrations run through the CLI, not psql",
    "additionalContext": "Use `npm run migrate` instead."
  }
}
```

`additionalContext` is how a hook talks to Claude — it arrives as a system reminder Claude reads as plain text. Hooks cannot call tools or trigger slash commands; stdout, stderr and the exit code are the whole interface.

When several hooks match one event they **all run in parallel, to completion**. One returning `deny` does not stop the others — so never rely on a sibling's `deny` to suppress your side effects. Results are merged most-restrictive-first: `deny`, `defer`, `ask`, `allow`.

## Hooks tighten; they never loosen

This is the property that makes hooks deployable as organisation policy, and it is worth stating precisely.

**`PreToolUse` hooks fire before any permission-mode check, in every mode — including `dontAsk` and `bypassPermissions`.** A hook returning `permissionDecision: "deny"` blocks the tool even under `--dangerously-skip-permissions`. Users cannot escape it by changing their permission mode.

**The reverse does not hold.** A hook returning `"allow"` does not bypass a deny rule from settings, and cannot suppress the prompt for MCP tools marked `requiresUserInteraction`. This is Chapter 3's evaluation order holding: deny still wins from anywhere.

Which puts hooks precisely one notch above modes and one notch below deny rules — and explains `allowManagedHooksOnly`, which lets an administrator run managed hooks while blocking everyone else's.

## Three that earn their keep

**Format after every edit.** The canonical one, and the reason `PostToolUse` exists:

```json
{ "matcher": "Edit|Write",
  "hooks": [{ "type": "command", "command": "prettier --write \"$CLAUDE_FILE_PATH\"" }] }
```

**Block edits to files nothing should touch.** A `PreToolUse` hook exiting 2 with a reason on stderr, which holds regardless of permission mode — the enforcement `CLAUDE.md` cannot give you.

**Re-inject context after a compact.** Chapter 8's compaction table has a row for this: a `SessionStart` hook matching `compact` runs and its output is added to the compacted context. It is the supported way to make something survive compaction that otherwise would not.

## Where they can live

Beyond settings files, two scopes are worth knowing because they are bounded:

- **Skill frontmatter** — registered when the skill is invoked, and they stay for the rest of the session. `once: true` removes the hook after its first success.
- **Subagent frontmatter** — run only while that subagent runs, then are removed. A `Stop` hook there becomes `SubagentStop`.

Plugins ship hooks in `hooks/hooks.json` (Chapter 13). `disableAllHooks` turns everything off, except managed hooks.

## When a hook doesn't fire

Three causes account for most of it:

1. **The matcher.** Run `/hooks` and check the hook appears under the right event. Matchers are case-sensitive, and a stray character turns your exact string into a regex.
2. **The path.** "command not found" means a relative path resolved somewhere unexpected. Use `${CLAUDE_PROJECT_DIR}`, or add `"args": []` to switch to exec form, which spawns the script directly with no shell quoting at all.
3. **It ran and failed quietly.** Test it by hand — that is the whole interface, so it is easy:

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"ls"}}' | ./my-hook.sh; echo $?
```

Two subtler ones. Stdout that *looks* like JSON but is malformed reports a parse error **even on exit 0** — build payloads with `jq` rather than string concatenation. And a `Stop` hook that keeps blocking is overridden after **eight consecutive blocks**; check the `stop_hook_active` field in your input and exit early when it is true.

## Summary

- A hook runs **regardless of what Claude decides**. That is the entire difference from `CLAUDE.md` and skills.
- 33 events, but only a small subset can **block** — `PreToolUse`, `UserPromptSubmit`, `Stop`, `PreModelSwitch` and a few more. `PostToolUse` cannot undo anything.
- Matcher syntax is decided by its characters: an unexpected one silently makes it a regex. Case-sensitive.
- **Exit `2` blocks and beats any JSON you also printed.** Exit `0` plus JSON is the expressive path.
- Matching hooks all run **in parallel to completion**; results merge most-restrictive-first.
- **A `PreToolUse` deny holds even under `bypassPermissions`. An allow never overrides a deny rule.** Hooks tighten, never loosen.
- A `SessionStart` hook matching `compact` is the supported way to re-inject context after compaction.
- Full reference: [hooks guide](https://code.claude.com/docs/en/hooks-guide), [event and schema reference](https://code.claude.com/docs/en/hooks).

Chapter 13 is Plugins — the wrapper that packages skills, hooks, subagents and MCP servers into one installable thing, and the marketplaces that distribute them.
