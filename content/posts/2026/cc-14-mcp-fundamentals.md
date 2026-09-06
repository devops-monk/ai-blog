---
title: "MCP Fundamentals"
image: /images/articles/cc-14-mcp-fundamentals.webp
toc: true
date: 2026-09-05T23:00:00+00:00
description: "The protocol that connects Claude Code to systems it has no tool for. Four transports, three scopes, and the deferral mechanism that stops ten servers from filling your context window before you type."
tags: ["claude-code", "mcp", "integrations", "tool-search", "oauth"]
categories: ["Fundamentals"]
url: /2026/09/mcp-fundamentals/
series: "Part 4 — Connecting Claude to the World"
series_order: 1
---

## Overview

This chapter covers:

- What MCP adds that a Bash command does not
- Four transports and three configuration scopes — and which scope your teammates get
- **Tool search**: why connecting ten servers costs almost nothing until Claude needs one
- The trust boundary around a project's `.mcp.json`, and where it does not apply
- The two tool annotations that make a prompt unavoidable in every permission mode

## What it adds

Claude Code can already run any command you can. So what does connecting a server buy?

Structure. Asking Claude to query Postgres via `psql` means it constructs a shell command, parses text output, and guesses at the schema. An MCP server exposes **typed tools with described inputs** — `query`, `list_tables`, `describe_table` — so Claude picks a tool and fills in parameters rather than composing a string and hoping.

The protocol is an open standard, so the same integration works across clients. Practically: issue trackers, databases, design tools, monitoring, and anything else with an API someone has wrapped.

## Four transports

| Transport | For |
|---|---|
| **stdio** | A local process on your machine — custom scripts, anything needing direct system access |
| **HTTP** | Remote servers. **The recommended one**, with OAuth 2.0 support |
| SSE | Deprecated. Use HTTP where the service offers it |
| WebSocket | Remote servers that push events unprompted |

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub --dsn "postgresql://readonly:pass@host/db"
```

The `--` matters: everything after it is the server's own command line, not Claude Code's.

> **A `url` with no `type` is read as a stdio server.** It is the most common configuration error, and the message it produces does not obviously point at the missing field. Always set `"type": "http"`.

## Three scopes

Chapter 5's precedence pattern again, with a different set of files:

| Scope | Lives in | Shared |
|---|---|---|
| **Local** (default) | `~/.claude.json`, under the project path | No |
| **Project** | `.mcp.json` at the repository root | **Yes, via git** |
| **User** | `~/.claude.json` | No — but every project |

Precedence when a name appears more than once: local → project → user → plugin-provided → claude.ai connectors. Claude connects once, using the highest.

`.mcp.json` supports environment expansion — `${API_KEY}` and `${API_BASE_URL:-https://default}` — across `command`, `args`, `env`, `url` and `headers`. That is what makes a committed file workable for a team.

> **An unset variable with no default does not fail loudly.** The server loads with the literal `${VAR}` text still in place, and shows `! Missing environment variable` in `/mcp` and `claude mcp list`. Give every variable a `:-default` unless its absence should be visible.

## Why ten servers don't flood your window

Chapter 8 noted that MCP tool schemas are **deferred** by default. This is the mechanism, and it is the single most important thing about running more than one server.

With tool search on — the default — Claude Code loads tool *names* and issues a `ToolSearch` request when it needs something. **Servers stay unconnected until Claude actually calls one of their tools.** With it off, every schema from every server is loaded into the system prompt at startup.

<div class="mc-box"> <div class="mc-ctls" id="mc-ctls"></div> <div class="mc-rows"> <div class="mc-row"><span class="mc-rl">Tool search on <em>(default)</em></span><div class="mc-track"><span class="mc-fill mc-on" id="mc-bar-on"></span></div><span class="mc-v" id="mc-v-on"></span></div> <div class="mc-row"><span class="mc-rl">Tool search off</span><div class="mc-track"><span class="mc-fill mc-off" id="mc-bar-off"></span><span class="mc-thresh" id="mc-thresh"></span></div><span class="mc-v" id="mc-v-off"></span></div> </div> <div class="mc-read" id="mc-read"></div> <p class="mc-note">Bars are drawn against a 200K window. Schema size varies a lot between servers, so the slider is there to try your own figure — the shape of the answer holds at any plausible value.</p> </div> <script> (function () { var MAX = 200000, NAME_COST = 12; var S = [ { k: "servers", n: "Servers connected", min: 1, max: 20, step: 1, val: 8, unit: "" }, { k: "tools", n: "Tools per server", min: 1, max: 60, step: 1, val: 14, unit: "" }, { k: "schema", n: "Tokens per tool schema", min: 100, max: 1200, step: 50, val: 450, unit: "" } ]; var st = {}; S.forEach(function (s) { st[s.k] = s.val; }); var cEl = document.getElementById("mc-ctls"), rEl = document.getElementById("mc-read"); function fmt(n) { return n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + "K" : String(Math.round(n)); } function render() { cEl.innerHTML = S.map(function (s) { return "<label class=\"mc-c\"><span>" + s.n + "<b>" + st[s.k] + "</b></span>" + "<input type=\"range\" data-k=\"" + s.k + "\" min=\"" + s.min + "\" max=\"" + s.max + "\" step=\"" + s.step + "\" value=\"" + st[s.k] + "\" /></label>"; }).join(""); var tools = st.servers * st.tools; var on = tools * NAME_COST, off = tools * st.schema; var pOn = Math.min(on / MAX, 1) * 100, pOff = Math.min(off / MAX, 1) * 100; document.getElementById("mc-bar-on").style.width = pOn + "%"; document.getElementById("mc-bar-off").style.width = pOff + "%"; document.getElementById("mc-thresh").style.left = "10%"; document.getElementById("mc-v-on").textContent = fmt(on); document.getElementById("mc-v-off").textContent = fmt(off) + (off > MAX ? " (over)" : ""); var ratio = on > 0 ? Math.round(off / on) : 0; var pct = Math.round(off / MAX * 100); rEl.className = "mc-read " + (off > MAX * 0.1 ? "mc-hot" : ""); rEl.innerHTML = "<strong>" + tools + " tool" + (tools === 1 ? "" : "s") + "</strong> across " + st.servers + " server" + (st.servers === 1 ? "" : "s") + ". " + "Deferred, that is <strong>" + fmt(on) + "</strong>; loaded upfront it is <strong>" + fmt(off) + "</strong> — " + ratio + "&times; more, or " + pct + "% of the window before you type anything. " + (off > MAX * 0.1 ? "Past 10% of the window, <code>ENABLE_TOOL_SEARCH=auto</code> would stop loading them upfront." : "Under 10% of the window, so <code>ENABLE_TOOL_SEARCH=auto</code> would still load these upfront."); Array.prototype.forEach.call(cEl.querySelectorAll("input"), function (i) { i.addEventListener("input", function () { st[i.getAttribute("data-k")] = +i.value; render(); }); }); } render(); })(); </script>

Tool search is unavailable or off in a few situations worth knowing, because the cost reappears: a custom `ANTHROPIC_BASE_URL`, `ENABLE_TOOL_SEARCH=false`, pre-4.5-generation models on Google Cloud's Agent Platform, and some Microsoft Foundry deployments. A server or tool marked `alwaysLoad` also stays in the prefix by choice.

And from Chapter 8's caching rules, the corollary: **a deferred server connecting or disconnecting mid-session costs you nothing**, because its definitions were never in the cached prefix. When tools *are* loaded into the prefix, the same event triggers a full re-read.

## Connecting and authenticating

`/mcp` is the manager: status, authentication, and toggling a server off without deleting it. `claude mcp list` gives the same statuses from the shell.

For OAuth servers, Claude Code flags anything answering `401` or `403`. Authenticate from inside a session with `/mcp`, or from the shell:

```bash
claude mcp login sentry
claude mcp login sentry --no-browser   # SSH, or a machine with no display
```

Tokens are stored securely and refreshed automatically. For servers without dynamic client registration you can supply a pre-registered client ID, secret and callback port.

For anything that is not OAuth — Kerberos, internal SSO, short-lived tokens — `headersHelper` runs a command that prints a JSON object of headers, re-run on every connection with a 10-second timeout:

```json
{ "mcpServers": { "internal": {
  "type": "http",
  "url": "https://mcp.internal.example.com",
  "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
} } }
```

## Trust

A project-scoped server is code someone committed that will run on your machine, so it needs approval before connecting. From Chapter 4, the pattern is familiar — and so is the exception:

> **Interactive sessions show the approval dialog. `claude -p`, the Agent SDK and cloud sessions load project servers without prompting.** If you are about to run `-p` in a repository you did not write, `--strict-mcp-config` loads only the servers you passed, and `disabledMcpjsonServers` rejects one by name.

Since v2.1.238 a `headersHelper` on a project or local server also waits for workspace trust. And credential-shaped environment variables — anything matching `TOKEN`, `SECRET`, `PASSWORD`, `KEY`, `AUTH` — are **stripped** from the environment of servers defined in a project `.mcp.json`, a plugin, or an `--add-dir` directory. User-scope servers keep them.

### Organisation controls

If you sign in with a claude.ai account, connectors configured there appear automatically. Administrators get two levers, and both outrank your permission mode:

| Setting | Effect |
|---|---|
| `ask` | Prompts on **every** call — including in `acceptEdits`, `auto` and `bypassPermissions`. Never offers "don't ask again". Denied outright in `dontAsk` |
| `blocked` | The tool is filtered out before Claude sees it |

A server author can request the same treatment per tool with the `requiresUserInteraction` annotation (v2.1.199+). **Allow rules do not skip that prompt** — this is the Chapter 3 list of actions no mode auto-approves, seen from the server's side.

`disableClaudeAiConnectors: true` switches off connectors Claude Code fetches itself.

## Limits worth knowing

Four defaults that explain most surprising MCP behaviour:

- **Output is capped at 25,000 tokens** (`MAX_MCP_OUTPUT_TOKENS`), with a warning at 10,000. A tool can raise its own ceiling to 500,000 characters with the `maxResultSizeChars` annotation. Results over roughly 10k tokens are written to disk and replaced with a file reference.
- **A call running over two minutes moves to a background task** (v2.1.212+). Claude gets a task ID and keeps working; the result arrives as a notification and shows in `/tasks`.
- **Remote servers reconnect automatically** — up to five attempts with exponential backoff. **Stdio servers do not**, because they are local processes.
- **Failures are only reported to Claude when tool search is on.** Without it, Claude is not told a server failed to connect; it simply has fewer tools than you expect.

## Summary

- MCP gives Claude **typed tools with described inputs** rather than a shell command and text to parse.
- Four transports; **HTTP is the recommended one**. A `url` with no `"type"` is read as stdio — the most common config error.
- Three scopes: local (default, private), **project (`.mcp.json`, committed)**, user (everywhere, private). Local wins.
- **Tool search defers schemas by default**, so ten servers cost tool names rather than tool schemas — and a deferred server connecting mid-session does not disturb the prompt cache.
- Project servers prompt for approval interactively but **load without prompting under `-p`, the SDK and cloud sessions**. Use `--strict-mcp-config` in a repository you do not trust.
- Credential-shaped environment variables are stripped from project, plugin and `--add-dir` servers.
- `ask` connector tools and `requiresUserInteraction` prompt in **every** mode, and allow rules do not skip them.
- Output caps at 25,000 tokens; calls over two minutes background themselves.
- Full reference: [MCP](https://code.claude.com/docs/en/mcp), [quickstart](https://code.claude.com/docs/en/mcp-quickstart), [managed MCP](https://code.claude.com/docs/en/managed-mcp).

Chapter 15 puts this to work: the servers worth connecting first, the native Chrome integration, and the prompts that actually get useful results out of them.
