---
title: "Rules & Auto Memory"
image: /images/articles/cc-07-rules-auto-memory.webp
toc: true
date: 2026-09-05T16:00:00+00:00
description: "Two ways instructions persist without you retyping them: rules you scope to file paths so they cost nothing until they are relevant, and the notes Claude writes for itself between sessions."
tags: ["claude-code", "rules", "auto-memory", "context-engineering", "monorepo"]
categories: ["Fundamentals"]
url: /2026/09/rules-and-auto-memory/
series: "Part 2 — Context Engineering"
series_order: 3
---

## Overview

This chapter covers:

- Why splitting `CLAUDE.md` into rules only helps if the rules are **scoped**
- `paths:` frontmatter, when a scoped rule actually fires, and the glob edge cases that make one match nothing
- The four kinds of note Claude writes for itself, and the larger set it deliberately refuses to write
- The 200-line ceiling on `MEMORY.md` and what happens to everything past it
- Which of these reach a subagent, and which survive a compact

## Two systems, opposite authors

Both load at the start of every session. The difference is who writes them.

| | `CLAUDE.md` and rules | Auto memory |
|---|---|---|
| Written by | You | Claude |
| Holds | Instructions and conventions | Corrections you gave, and preferences it inferred |
| Scope | Project, user, or organisation | Per repository, on this machine |
| Good for | "Always do X" | "You told me last week that X" |

Neither is enforcement. Both are context Claude reads and tries to honour — the Chapter 6 point, and still the reason a guarantee needs a hook.

## Rules

Chapter 6 ended on a limitation: `@path` imports organise a large `CLAUDE.md` without reducing what loads. `.claude/rules/` is the mechanism that reduces it.

```text
your-project/
└── .claude/
    ├── CLAUDE.md
    └── rules/
        ├── code-style.md
        ├── testing.md
        └── frontend/
            └── components.md
```

Every `.md` file is discovered **recursively**, so subdirectories are for your benefit, not Claude's. A rule with no frontmatter loads at launch with the same priority as `.claude/CLAUDE.md` — which means splitting a 400-line `CLAUDE.md` into eight unscoped rule files has changed nothing except your file browser.

The payoff comes from the `paths` field:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API rules

- Validate input on every endpoint
- Return the standard error shape
```

That file is not in context when Claude is editing CSS. It enters when Claude **reads a file matching the pattern** — not on every tool call, and not because the conversation is about the API.

`~/.claude/rules/` works the same way for personal rules across every project. They load **before** project rules, which gives project rules the later, stronger position.

### Watch what loads

<div class="rl-box"> <div class="rl-cols"> <div class="rl-col"> <span class="rl-lbl">Claude reads a file</span> <div class="rl-files" id="rl-files"></div> <button type="button" class="rl-reset" id="rl-reset">Back to launch</button> </div> <div class="rl-col rl-wide"> <span class="rl-lbl">In context</span> <table class="rl-table"><tbody id="rl-rows"></tbody></table> <div class="rl-total" id="rl-total"></div> </div> </div> </div> <script> (function () { var RULES = [ { f: ".claude/CLAUDE.md", p: null, n: 90 }, { f: "rules/code-style.md", p: null, n: 40 }, { f: "rules/api.md", p: ["src/api/**/*.ts"], n: 55 }, { f: "rules/components.md", p: ["src/components/*.{tsx,jsx}"], n: 70 }, { f: "rules/typescript.md", p: ["**/*.{ts,tsx}"], n: 35 }, { f: "rules/testing.md", p: ["tests/**/*.test.ts"], n: 60 }, { f: "rules/docs.md", p: ["*.md"], n: 25 }, { f: "rules/photos.md", p: ["photos [2024/**"], n: 30, broken: "unescaped [ — this is an unterminated bracket expression, so it matches nothing" } ]; var FILES = [ "src/api/users.ts", "src/components/Button.tsx", "src/lib/format.ts", "tests/auth.test.ts", "README.md", "photos 2024/trip.jpg" ]; var open = null; var filesEl = document.getElementById("rl-files"), rowsEl = document.getElementById("rl-rows"), totEl = document.getElementById("rl-total"); function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; }); } function expand(p) { var m = p.match(/\{([^{}]*)\}/); if (!m) { return [p]; } var out = []; m[1].split(",").forEach(function (alt) { out = out.concat(expand(p.slice(0, m.index) + alt + p.slice(m.index + m[0].length))); }); return out; } function toRe(p) { var out = "", i = 0; while (i < p.length) { var c = p[i]; if (c === "*" && p[i + 1] === "*") { out += "[\\s\\S]*"; i += 2; if (p[i] === "/") { i++; } continue; } if (c === "*") { out += "[^/]*"; i++; continue; } if (c === "?") { out += "[^/]"; i++; continue; } if (c === "[") { return null; } out += c.replace(/[.+^${}()|\\\]]/g, "\\$&"); i++; } return new RegExp("^" + out + "$"); } function matches(rule, file) { if (!rule.p) { return true; } for (var i = 0; i < rule.p.length; i++) { var pats = expand(rule.p[i]); for (var j = 0; j < pats.length; j++) { var re = toRe(pats[j]); if (re && re.test(file)) { return true; } } } return false; } function render() { filesEl.innerHTML = FILES.map(function (f) { return "<button type=\"button\" class=\"rl-file" + (f === open ? " on" : "") + "\" data-f=\"" + esc(f) + "\"><code>" + esc(f) + "</code></button>"; }).join(""); var total = 0, extra = 0; rowsEl.innerHTML = RULES.map(function (r) { var always = !r.p, hit = open && matches(r, open); var inCtx = always || hit; if (inCtx) { total += r.n; if (!always) { extra += r.n; } } var state = always ? "at launch" : (hit ? "just loaded" : "not loaded"); var cls = always ? "rl-always" : (hit ? "rl-hit" : "rl-off"); return "<tr class=\"" + cls + "\"><td class=\"rl-f\"><code>" + esc(r.f) + "</code>" + (r.p ? "<span class=\"rl-pat\">" + esc(r.p.join(", ")) + "</span>" : "<span class=\"rl-pat\">no paths: field</span>") + (r.broken && open ? "<span class=\"rl-warn\">" + esc(r.broken) + "</span>" : "") + "</td><td class=\"rl-n\">" + r.n + " lines</td><td class=\"rl-st\">" + state + "</td></tr>"; }).join(""); totEl.innerHTML = open ? "<strong>" + total + " lines</strong> in context — " + (total - extra) + " loaded at launch, " + extra + " added by reading <code>" + esc(open) + "</code>" : "<strong>" + total + " lines</strong> in context at launch. Pick a file to see what a scoped rule adds."; Array.prototype.forEach.call(filesEl.querySelectorAll(".rl-file"), function (b) { b.addEventListener("click", function () { open = b.getAttribute("data-f"); render(); }); }); } document.getElementById("rl-reset").addEventListener("click", function () { open = null; render(); }); render(); })(); </script>

The lesson in the numbers: unscoped rules are `CLAUDE.md` with extra steps. Scoping is the entire feature.

### Glob syntax, and three ways to write one that matches nothing

Patterns are globs — `**/*.ts`, `src/**/*`, `*.md`, `src/components/*.tsx` — and brace expansion works:

```yaml
paths:
  - "src/**/*.{ts,tsx}"
  - "tests/**/*.test.ts"
```

Three edges are worth knowing, because each fails *silently*:

- **Brace expansion has a budget.** Each group multiplies: `{a,b}/{c,d}/*.{ts,tsx}` is eight patterns. A rule's whole `paths` list shares a budget of 1,000 expanded patterns and 4 MiB. Exceed it and the pattern is used **unexpanded**, so its literal braces match no file. Before v2.1.217 this stalled or crashed the CLI at startup instead.
- **`[` opens a bracket expression.** `photos [2024/**` is not a path with a bracket in it — it is an unterminated `[abc]` class, so it matches nothing. Escape it: `photos \[2024/**`. Before v2.1.207, one invalid pattern made the Read tool fail for *every* file the rule was checked against.
- **A rule that never matches looks identical to a rule that is being ignored.** There is no error either way.

That last point is why the `InstructionsLoaded` hook exists: it logs which instruction files loaded, when, and why. For debugging a scoped rule it is the only direct evidence.

### Sharing rules between projects

`.claude/rules/` follows symlinks, and circular links are detected rather than fatal:

```bash
ln -s ~/company-standards/security.md .claude/rules/security.md
ln -s ~/shared-claude-rules .claude/rules/shared
```

In a monorepo where other teams' instruction files get swept up, `claudeMdExcludes` skips them by glob — and it covers rules directories, not just `CLAUDE.md`:

```json
{
  "claudeMdExcludes": ["/home/me/monorepo/other-team/.claude/rules/**"]
}
```

Patterns match against **absolute** paths, arrays merge across settings layers, and for a symlinked rule a pattern matching *either* the link or its target excludes the file (v2.1.239+; before that, only the target worked).

## Auto memory

The other half needs no files from you. As you work, Claude writes notes for itself into a per-repository directory, and reads them back at the start of the next session.

It saves four kinds, tagged in each file's frontmatter:

| `type` | What it holds |
|---|---|
| `user` | Your role, expertise, working preferences |
| `feedback` | Corrections you gave, and approaches you confirmed |
| `project` | Ongoing work, deadlines, decisions not derivable from the code |
| `reference` | Where information lives outside the project — trackers, dashboards |

**What it refuses to save is the more interesting list.** Claude skips anything derivable from the codebase — architecture, file paths, how a bug was fixed — and anything your `CLAUDE.md` already says. It is the same heuristic `/doctor` applies when trimming `CLAUDE.md`, and for the same reason: a note that repeats the code is a note that costs context and pays nothing.

It also does not save every session. It writes when something looks useful later, which is why "Saved 2 memories" appears some turns and not others.

### Where it lives, and the ceiling

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md            # index, one line per memory
├── user_role.md
└── feedback_testing.md
```

`<project>` derives from the git repository, so **every worktree and subdirectory of one repo share a single memory directory.** It is machine-local: nothing syncs to another machine or to a cloud session.

The number that matters: **only the first 200 lines or 25 KB of `MEMORY.md`, whichever comes first, load at session start.** Everything past that is silently dropped on the next load. Topic files are not loaded at startup at all — Claude opens them on demand with its ordinary file tools.

That is why `MEMORY.md` is an *index*: one line per memory, detail pushed into topic files. Claude Code measures the file after each write, reminds Claude to shorten it near the limit, and returns an error telling it to rewrite the index once past. The limit applies only to `MEMORY.md` — a `CLAUDE.md` loads in full up to 4 MiB.

Memory files are also **exempt from the session-transcript retention sweep** that `cleanupPeriodDays` drives. They stay until you or Claude edits them.

### Controlling it

| What | How |
|---|---|
| Browse and edit | `/memory`, then open the auto memory folder — plain markdown, editable and deletable |
| Turn it off for one project | `"autoMemoryEnabled": false` in that project's settings |
| Turn it off everywhere | The `/memory` toggle, or `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` |
| Move the directory | `"autoMemoryDirectory": "~/my-memory"` — absolute or `~/` only |

Asking Claude to "remember that we use pnpm" writes to auto memory. Asking it to "add that to CLAUDE.md" writes to the file. The distinction is worth making deliberately: auto memory is yours and machine-local, `CLAUDE.md` is your team's and committed.

Since v2.1.214 each memory file with frontmatter gets a `modified` timestamp on write, so both you and Claude can see how stale a fact is. **A recalled memory reflects what was true when it was written** — if it names a flag or a file, that is a claim to verify, not a fact to act on.

## Where each mechanism reaches

The last question is which of this survives the events that clear context.

| | Reloads after `/compact` | Loaded into a subagent |
|---|---|---|
| Project-root `CLAUDE.md` | Yes — re-read from disk | Yes |
| Nested `CLAUDE.md`, path-scoped rules | When Claude next touches a matching file | On the same terms |
| Auto memory | Yes | **No** — except a fork, which inherits the parent conversation |
| An instruction given in chat | **No** | No |

A subagent gets its own auto memory directory if you enable the `memory` field on it; the main conversation's memory is not shared into it.

So the diagnostic from Chapter 6 sharpens: if something Claude knew is gone after a compact, it was said in conversation only. If something it knew is gone **inside a subagent**, it was probably auto memory.

## Summary

- Splitting `CLAUDE.md` into rules saves nothing unless the rules are **scoped**. An unscoped rule loads at launch like any other instruction.
- A `paths:` rule fires when Claude **reads a matching file**, not when the conversation is about that area.
- User rules load before project rules, so project rules land later and stronger.
- Three silent glob failures: an over-budget brace expansion is used unexpanded, an unescaped `[` matches nothing, and neither reports an error. `InstructionsLoaded` is the way to see what really loaded.
- Auto memory saves four kinds of note and **deliberately skips anything derivable from the code** or already in your `CLAUDE.md`.
- **Only the first 200 lines or 25 KB of `MEMORY.md` load.** It is an index; detail belongs in topic files, which load on demand.
- Auto memory is per-repository and machine-local, shared across worktrees, and exempt from the transcript retention sweep.
- **Auto memory does not reach a subagent**, but `CLAUDE.md` does.
- Full reference: [memory and rules](https://code.claude.com/docs/en/memory), [monorepos](https://code.claude.com/docs/en/large-codebases).

Chapter 8 is the budget all of this spends: the context window — what fills it, what `/compact` keeps, and the habits that stop you hitting the ceiling mid-task.
