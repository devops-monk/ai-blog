---
title: "MCP in Practice"
image: /images/articles/cc-15-mcp-in-practice.webp
toc: true
date: 2026-09-06T09:00:00+00:00
description: "When a server earns its place and when Bash already does the job, the native Chrome integration and its safety model, and the prompt shapes that actually get useful work out of both."
tags: ["claude-code", "mcp", "chrome", "browser-automation", "workflows"]
categories: ["Fundamentals"]
url: /2026/09/mcp-in-practice/
series: "Part 4 — Connecting Claude to the World"
series_order: 2
---

## Overview

This chapter covers:

- The three questions that decide whether a task needs a server at all
- The native Chrome integration — what it does that an API connector cannot
- Plan mode's read/write split for browser tools, and the flags that turn a read into a write
- Prompt shapes taken from the documented recipes, and what makes each one work
- The one Chrome capability worth a second thought before you use it

## Before you reach for a server

Chapter 14 was the mechanism. The practical question is narrower: **does this task need a server?** Three checks, in order:

1. **Can Bash already do it?** `gh`, `psql`, `aws`, `kubectl` are all installed and Claude can run them. A server earns its place when you want *typed tools* rather than a command whose output has to be parsed — or when there is no CLI at all.
2. **Is the problem context, not capability?** "Explore how auth works" does not need a server. It needs a subagent, so the file reads land somewhere other than your window.
3. **Are you already signed in to it in a browser?** Then Chrome is often the shorter path than an API integration, because it inherits the session you already have.

That third one is what the rest of this chapter is mostly about.

## The native Chrome integration

`claude --chrome`, with the Claude in Chrome extension installed, gives Claude your actual browser. Not a headless one — a visible window, running in real time, **sharing your login state**.

That last property is the whole point. It is why Google Docs, Gmail, Notion and your internal admin panel all work without an API connector, an OAuth app, or a token:

```text
Draft a project update based on the recent commits and add it to my
Google Doc at docs.google.com/document/d/abc123
```

Claude opens the document, clicks into the editor, and types. Chrome, Edge and other Chromium browsers all work; **WSL does not**.

Two prerequisites catch people. You need a **direct Anthropic plan** — Pro, Max, Team or Enterprise — and you must be signed in with `/login`. Authenticate with an API key or a `claude setup-token` token and Chrome integration stays off even if you pass `--chrome`, because the extension cannot authenticate with those credentials.

### What it is good at

The pattern that makes it more than automation is **chaining browser work to code work in one turn**:

- **Live debugging** — read console errors and DOM state, then fix the code that produced them.
- **Design verification** — build the UI, open it, check it against the mock.
- **Data extraction** — read a page, write a CSV locally.
- **Uploads** — attach a local file to a form field.

When Claude hits a login page or a CAPTCHA it **stops and asks you to handle it**, which is the right behaviour and worth knowing before you leave it unattended.

### Plan mode splits reads from writes

Chapter 3 said plan mode blocks edits but runs classifier-approved commands. Browser tools get a cleaner version of that rule: **read-only calls run without a prompt, state-changing calls ask.**

| Runs in plan mode | Prompts |
|---|---|
| `read_page`, `get_page_text`, `find` | Clicks, typing, navigation |
| Reading console messages and network requests | Tab and window management |
| Taking a screenshot | Recording a GIF |

The subtlety is that **a flag can turn a read into a write**: `createIfEmpty` on the tabs tool, `clear` on the console and network readers, `save_to_disk` on a screenshot. And a `browser_batch` runs unprompted only if *every* action inside it is read-only.

### Uploads, and their three limits

Claude can attach local files to a page (v2.1.211+), and the restrictions are all sensible once stated:

- **A `Read` deny rule blocks the upload.** Chapter 4's rules cover this path too — Claude can only upload a file the session may read.
- **10 MB total** per upload.
- **Files with multiple hard links are refused** — common inside `node_modules` and pnpm stores. Copy it and upload the copy.

### The one to think about

> **A recorded GIF captures everything visible in the browser**, including account details on pages you are logged into. Claude Code says so explicitly, and it is worth repeating: review a recording before it leaves your team.

Two smaller notes. Enabling Chrome by default loads browser tools every session, which costs context — Chapter 8's argument, so prefer `--chrome` when you need it. And the extension's service worker goes idle in long sessions; `/chrome` → **Reconnect extension** is the fix when browser tools stop responding.

## Prompts that work

The recipes below are the documented ones. What they have in common is worth naming before you read them: **they specify the target and the symptom, and leave the procedure alone** — Chapter 1's advice, applied.

<div class="pr-box"> <div class="pr-tabs" id="pr-tabs"></div> <div class="pr-body" id="pr-body"></div> </div> <script> (function () { var R = [ { k: "explore", n: "Understand a codebase", why: "Broad first, then narrow. Each answer tells you what to ask next — the Chapter 1 loop, driven by you.", steps: ["give me an overview of this codebase", "explain the main architecture patterns used here", "what are the key data models?", "how is authentication handled?"], tip: "Use the project's own domain language. Asking about “accounts” in a codebase that says “tenants” makes Claude search for the wrong word." }, { k: "find", n: "Find relevant code", why: "Locate, then relate, then trace. Three different questions, and asking them separately keeps each answer checkable.", steps: ["find the files that handle user authentication", "how do these authentication files work together?", "trace the login process from front-end to database"], tip: "A code intelligence plugin gives Claude real go-to-definition instead of grep, which changes the quality of the third step in particular." }, { k: "bug", n: "Fix a bug", why: "You give the symptom and the command. You do not name the file — that is the assumption most likely to be wrong.", steps: ["I'm seeing an error when I run npm test", "suggest a few ways to fix the @ts-ignore in user.ts", "update user.ts to add the null check you suggested"], tip: "Say whether the failure is intermittent or consistent. It changes what is worth investigating first, and Claude cannot tell from one run." }, { k: "refactor", n: "Refactor", why: "Find, propose, apply, verify. The last step is not optional — it is what makes the change a fact rather than a claim.", steps: ["find deprecated API usage in our codebase", "suggest how to refactor utils.js to use modern JavaScript features", "refactor utils.js to use ES2024 features while maintaining the same behavior", "run tests for the refactored code"], tip: "“while maintaining the same behavior” is doing real work in step three. Without it, a refactor prompt invites redesign." }, { k: "tests", n: "Write tests", why: "Coverage gap first, scaffolding second, edge cases third. Asking for “tests” in one step gets you the easy half.", steps: ["find functions in NotificationsService.swift that are not covered by tests", "add tests for the notification service", "add test cases for edge conditions in the notification service", "run the new tests and fix any failures"], tip: "Claude reads your existing test files to match framework, style and assertion patterns, so you rarely need to specify them." }, { k: "pr", n: "Open a PR", why: "Summarise before generating. The summary is your chance to catch a wrong mental model before it becomes the PR description.", steps: ["summarize the changes I've made to the authentication module", "create a pr", "enhance the PR description with more context about the security improvements"], tip: "claude --from-pr 1234 reopens the session that created a PR — the picker filtered to sessions linked to it." }, { k: "browser", n: "Test in the browser", why: "Name the page, the action and what you expect to see. Claude cannot tell a rendering bug from a correct render of wrong data.", steps: ["I just updated the login form validation. Can you open localhost:3000, try submitting the form with invalid data, and check if the error messages appear correctly?", "Open the dashboard page and check the console for any errors when the page loads."], tip: "Tell Claude which console patterns matter. “Any errors” on a chatty page returns mostly noise." }, { k: "image", n: "Work from a screenshot", why: "An image carries what a description would fumble — a layout, an error dialog, a schema.", steps: ["Here's a screenshot of the error. What's causing it?", "Generate CSS to match this design mockup", "This is our current database schema. How should we modify it for the new feature?"], tip: "Drag and drop, or Ctrl+V to paste from the clipboard — Alt+V on Windows and WSL." } ]; var sel = "bug"; var tEl = document.getElementById("pr-tabs"), bEl = document.getElementById("pr-body"); function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c]; }); } function render() { tEl.innerHTML = R.map(function (r) { return "<button type=\"button\" class=\"pr-tab" + (r.k === sel ? " on" : "") + "\" data-k=\"" + r.k + "\">" + esc(r.n) + "</button>"; }).join(""); var r = R.filter(function (x) { return x.k === sel; })[0]; bEl.innerHTML = "<p class=\"pr-why\">" + esc(r.why) + "</p>" + "<ol class=\"pr-steps\">" + r.steps.map(function (s) { return "<li><code>" + esc(s) + "</code></li>"; }).join("") + "</ol>" + "<div class=\"pr-tip\"><span class=\"pr-th\">Worth adding</span>" + esc(r.tip) + "</div>"; Array.prototype.forEach.call(tEl.querySelectorAll(".pr-tab"), function (b) { b.addEventListener("click", function () { sel = b.getAttribute("data-k"); render(); }); }); } render(); })(); </script>

## Choosing the mechanism

Four ways to get information into a session, and they are not interchangeable:

| You want | Use | Because |
|---|---|---|
| Typed operations against a system with an API | An **MCP server** | Claude picks a tool and fills parameters instead of composing a string |
| Something you are already logged into | **Chrome** | It inherits your session — no connector, no token |
| To understand code without filling your window | A **subagent** | The file reads land in its context, not yours |
| A one-off command whose output you will read | **`!` shell mode** | No round trip, no permission check — Chapter 2 |

The failure mode this avoids is reaching for a server when the answer is a subagent, which is common because "connect a tool" feels like the more powerful move. It is usually the more expensive one.

## Summary

- Ask whether **Bash already does it** before adding a server. A server earns its place through *typed tools*, not access.
- If the problem is context rather than capability, the answer is a **subagent**.
- **Chrome shares your login state**, which is why it reaches authenticated apps with no connector or token. It needs a direct Anthropic plan and `/login` — an API key or setup token disables it.
- In plan mode, browser **reads run and writes prompt** — but `save_to_disk`, `clear` and `createIfEmpty` turn a read into a write.
- Uploads respect `Read` deny rules, cap at **10 MB**, and refuse hard-linked files.
- **A recorded GIF captures logged-in page content.** Review before sharing.
- Enabling Chrome by default loads browser tools into every session; prefer `--chrome`.
- Full reference: [Chrome](https://code.claude.com/docs/en/chrome), [common workflows](https://code.claude.com/docs/en/common-workflows), [best practices](https://code.claude.com/docs/en/best-practices).

Chapter 16 takes this off your machine: GitHub and GitLab integration, and Claude Code as a step in CI.
