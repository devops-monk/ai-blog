---
title: "Output Styles"
image: /images/articles/cc-10-output-styles.webp
toc: true
date: 2026-09-05T19:00:00+00:00
description: "The one extension point that edits the system prompt itself. Five built-in styles, the single frontmatter field that decides whether Claude still behaves like an engineer, and how output styles differ from the four mechanisms they get confused with."
tags: ["claude-code", "output-styles", "system-prompt", "customisation"]
categories: ["Fundamentals"]
url: /2026/09/output-styles/
series: "Part 3 — Teaching Claude New Tricks"
series_order: 1
---

## Overview

This chapter covers:

- The one thing output styles change that no other mechanism touches — the system prompt itself
- The five built-in styles, including two added recently that most material misses
- Why `keep-coding-instructions` is the field that actually matters, and what happens when you omit it
- Where a style file lives, and which of the five scopes wins
- The comparison that stops you reaching for the wrong mechanism

## They change how Claude responds, not what it knows

Every mechanism so far has added *context*. `CLAUDE.md` arrives as a user message after the system prompt. Rules arrive when a file matches. Skills arrive when invoked.

**An output style modifies the system prompt.** That is the whole distinction, and everything else follows from it.

Reach for one when you keep re-prompting for the same voice or format every turn, or when you want Claude to act as something other than a software engineer. For facts about your project, `CLAUDE.md` is still the answer.

## The five built-ins

| Style | Behaviour |
|---|---|
| **Default** | The standard software-engineering system prompt |
| **Proactive** | Executes immediately, makes reasonable assumptions instead of pausing on routine decisions, prefers action over planning |
| **Concise** | Leads with the result, skips preamble and narration, keeps responses short — while doing the same engineering work |
| **Explanatory** | Adds educational "Insights" about implementation choices and codebase patterns |
| **Learning** | Asks *you* to write strategic pieces, leaving `TODO(human)` markers in the code |

Two are worth a sentence each.

**Proactive is not auto mode.** It is stronger autonomous-execution guidance than auto mode applies, and it works **without changing your permission mode** — so what actually runs without asking you is still Chapter 3's business. Use it when you want Claude to stop asking clarifying questions in a mode that still prompts.

**Concise (v2.1.237+) keeps the important things long.** It shortens by default but preserves the full content of error reports, security warnings, and confirmations for destructive actions. And asking for detail still gets you detail.

> The standalone `/output-style` command was **deprecated in v2.1.73 and removed in v2.1.91.** Older material still recommends it. Use `/config` → **Output style**, or set the `outputStyle` key.

`/config` writes your choice to `.claude/settings.local.json` — project-local, not user-level, which surprises people expecting a personal preference to follow them between repositories.

## Writing your own

A custom style is a Markdown file: frontmatter, then the instructions to add to the system prompt.

| Field | Purpose | Default |
|---|---|---|
| `name` | The style's name | The file name |
| `description` | Shown in the `/config` picker | None |
| `keep-coding-instructions` | Keep the built-in software-engineering instructions | **`false`** |
| `force-for-plugin` | Plugin styles only: apply automatically while the plugin is enabled | `false` |

### The field that matters

`keep-coding-instructions` defaults to **`false`**, and that default is the single most consequential thing on this page.

Leave it out and your style **replaces** Claude Code's built-in engineering instructions — how to scope a change, when to write comments, how to verify work. That is correct for a writing assistant or a data analyst. It is quietly wrong for "answer with a diagram first", where you wanted a formatting change and instead removed the instructions that make Claude a competent engineer.

**The test:** is Claude still doing software engineering? Then set it to `true`.

### Build one

<div class="os-box"> <div class="os-presets" id="os-presets"></div> <div class="os-grid"> <label class="os-f"><span>Name</span><input type="text" id="os-name" class="os-in" spellcheck="false" /></label> <label class="os-f"><span>Description</span><input type="text" id="os-desc" class="os-in" spellcheck="false" /></label> <label class="os-f"><span>Scope</span><select id="os-scope" class="os-in"><option value="user">User — every project</option><option value="project">Project — committed</option></select></label> <label class="os-f os-check"><input type="checkbox" id="os-keep" /><span>keep-coding-instructions</span></label> </div> <label class="os-f os-body"><span>Instructions</span><textarea id="os-body" class="os-in" rows="4" spellcheck="false"></textarea></label> <div class="os-warn" id="os-warn"></div> <span class="os-path" id="os-path"></span> <pre class="os-out" id="os-out"></pre> </div> <script> (function () { var PRESETS = [ { id: "diagram", label: "Diagrams first", keep: true, scope: "project", desc: "Lead every explanation with a diagram", body: "When explaining code, architecture, or data flow, start with a Mermaid diagram showing the structure, then explain in prose.\n\n## Diagram conventions\n\nUse `flowchart TD` for control flow and `sequenceDiagram` for request paths. Keep diagrams under 15 nodes." }, { id: "review", label: "Review voice", keep: true, scope: "user", desc: "Answer like a code reviewer, not a narrator", body: "Lead with the verdict, then the reasoning. Name the file and line for every claim.\n\nDo not narrate what you are about to do. Do not restate the question." }, { id: "writer", label: "Writing assistant", keep: false, scope: "user", desc: "Editing prose, not code", body: "You are an editor working on long-form technical prose.\n\nPreserve the author's voice. Cut hedging and filler. Flag any claim that would need a source, rather than inventing one." }, { id: "analyst", label: "Data analyst", keep: false, scope: "project", desc: "Exploratory data analysis, not software engineering", body: "You are a data analyst. Start from the question, not the data.\n\nState the assumption behind every aggregate. Show the query or the code that produced a number, and never present an estimate as a measurement." } ]; var state = { keep: true, scope: "project" }; var els = { name: document.getElementById("os-name"), desc: document.getElementById("os-desc"), scope: document.getElementById("os-scope"), keep: document.getElementById("os-keep"), body: document.getElementById("os-body"), out: document.getElementById("os-out"), path: document.getElementById("os-path"), warn: document.getElementById("os-warn"), pre: document.getElementById("os-presets") }; function slug(s) { return (s || "my-style").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "") || "my-style"; } function load(p) { els.name.value = p.label; els.desc.value = p.desc; els.body.value = p.body; els.keep.checked = p.keep; els.scope.value = p.scope; Array.prototype.forEach.call(els.pre.querySelectorAll(".os-preset"), function (b) { b.classList.toggle("on", b.getAttribute("data-id") === p.id); }); render(); } function render() { var name = els.name.value.trim(), desc = els.desc.value.trim(); var keep = els.keep.checked, body = els.body.value.replace(/\s+$/, ""); var lines = ["---"]; if (name) { lines.push("name: " + name); } if (desc) { lines.push("description: " + desc); } if (keep) { lines.push("keep-coding-instructions: true"); } lines.push("---", "", body || "Your instructions go here."); els.out.textContent = lines.join("\n"); var dir = els.scope.value === "user" ? "~/.claude/output-styles/" : ".claude/output-styles/"; els.path.textContent = dir + slug(name) + ".md"; els.warn.className = "os-warn " + (keep ? "os-ok" : "os-alert"); els.warn.innerHTML = keep ? "<strong>Coding instructions kept.</strong> Claude still scopes changes, comments and verifies the way it does by default. Your instructions sit on top." : "<strong>Coding instructions dropped.</strong> The field is absent, so it defaults to false and your style <em>replaces</em> the built-in software-engineering instructions. Right for a non-engineering role — wrong if you only wanted a format change."; } els.pre.innerHTML = PRESETS.map(function (p) { return "<button type=\"button\" class=\"os-preset\" data-id=\"" + p.id + "\">" + p.label + "</button>"; }).join(""); Array.prototype.forEach.call(els.pre.querySelectorAll(".os-preset"), function (b) { b.addEventListener("click", function () { load(PRESETS.filter(function (p) { return p.id === b.getAttribute("data-id"); })[0]); }); }); ["name", "desc", "body"].forEach(function (k) { els[k].addEventListener("input", render); }); els.keep.addEventListener("change", render); els.scope.addEventListener("change", render); load(PRESETS[0]); })(); </script>

### Where the file goes

| Scope | Path |
|---|---|
| User | `~/.claude/output-styles/` |
| Project | `.claude/output-styles/` |
| Managed policy | `.claude/output-styles/` inside the managed settings directory |

Project styles load from **every** `.claude/output-styles/` between your working directory and the repository root. Two of them defining the same name is resolved by proximity: the one closest to your working directory wins. Plugins can ship styles too, in an `output-styles/` directory.

## When it takes effect

Output style is part of the system prompt, and Chapter 8 established what that means: **Claude Code reads it once at session start.** Changing it mid-session does nothing until `/clear` or a restart — and, for the same reason, the change is cache-safe.

Two more scope limits worth knowing:

- **Subagents ignore your output style.** A subagent runs its own system prompt. The exception is a fork, which inherits the parent's system prompt wholesale.
- **Token cost cuts both ways.** The added instructions raise input tokens, largely absorbed by the cache after the first request. Output tokens are the real variable: Explanatory and Learning produce longer responses by design, Concise shorter ones.

## Which mechanism, again

Five things now customise Claude's behaviour, and the failure mode is reaching for the wrong one. Chapter 6's router asked where an *instruction* belongs; this is the layer above it:

| Mechanism | How it works | Use when |
|---|---|---|
| **Output style** | Modifies the system prompt | You want a different role, tone or default format **every turn** |
| `CLAUDE.md` | A user message after the system prompt | Claude should know your conventions and codebase |
| `--append-system-prompt` | Appends to the system prompt, removing nothing | A one-off addition for a single invocation |
| Subagents | A separate system prompt, model and tools | A separately scoped helper for a focused task |
| Skills | Task instructions loaded on invocation | A reusable workflow |

The row that most often gets mistaken for an output style is `--append-system-prompt`: it reaches the same place, but **adds without removing**, and must be passed every invocation. That makes it right for scripts and wrong for daily use — where a style file you select once is the same idea, persisted.

## Summary

- An output style **modifies the system prompt**. Every other mechanism adds context around it.
- Five built-ins: Default, **Proactive**, **Concise** (v2.1.237+), Explanatory, Learning.
- Proactive is stronger than auto mode's nudge and **does not change your permission mode**.
- **`keep-coding-instructions` defaults to `false`**, so a custom style silently drops the built-in engineering instructions unless you set it. Set it whenever Claude is still writing code.
- `/output-style` was removed in v2.1.91 — use `/config` or the `outputStyle` key, which `/config` writes to `.claude/settings.local.json`.
- Project styles resolve by **proximity to the working directory**, not by depth in the tree.
- The style is read **once at session start**; changes need `/clear`. Subagents do not inherit it, forks do.
- Full reference: [output styles](https://code.claude.com/docs/en/output-styles).

Chapter 11 is Skills — the extension point that carries the most weight in practice, and the one built entirely around *not* being in context until it is needed.
