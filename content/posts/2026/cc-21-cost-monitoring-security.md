---
title: "Cost, Monitoring & Security"
image: /images/articles/cc-21-cost-monitoring-security.webp
toc: true
date: 2026-09-06T01:10:00+00:00
description: "What it actually costs, why an idle session keeps spending, and the security model underneath every permission prompt — including the sentence about what it does not protect you from."
tags: ["claude-code", "costs", "monitoring", "security", "prompt-injection"]
categories: ["Fundamentals"]
url: /2026/09/cost-monitoring-and-security/
series: "Part 6 — Running It for Real"
series_order: 1
---

## Overview

This chapter covers:

- Real cost anchors, and why a coding seat is not a chat seat
- The six reasons a session that has been open all day costs more than the work in it
- Which lever actually moves spend, in rough order of effect
- The safeguards against prompt injection — and the sentence that says what they do not cover
- What an organisation can see and cap, per plan

## What it costs

The published anchors, which are worth having before you argue about a plan:

| Measure | Figure |
|---|---|
| Average | **~$13 per developer per active day** |
| Typical month | **$150–250 per developer** |
| 90% of users | Under **$30 per active day** |

The framing that explains the spread: **budget more for a coding seat than a chat seat.** Every turn carries file contents, tool calls and multi-step reasoning, so one debugging session can consume more than a day of chat.

If you are rolling this out, the advice is to pilot small and measure rather than model it — the variance between developers is larger than any estimate you would build.

## Where to look

| Command | Shows |
|---|---|
| `/usage` | Session tokens and cost, plan usage bars, and **attribution** — how much went to which skill, subagent, plugin or MCP server |
| `/insights` | An HTML report on *how you work* — friction points, misunderstood requests — rather than what you spent |
| **OpenTelemetry** | Per-user tokens and cost streamed into your own stack. **The only option that works on every setup** |

Two details on `/usage` worth knowing. Its **behaviour flags** call out anything accounting for 10% or more of recent usage — long context, cache misses — which is a diagnosis rather than a number. And on a subscription the dollar figure is not your bill: usage is included, so the figure is there for API users.

> If your organisation pays contracted rates, every figure Claude Code shows is **list price** unless an administrator sets `modelPricing` in managed settings. Then `/usage` notes it is reporting *at your organization's configured rates*.

## Why an idle session keeps spending

The most common surprise, and the answer is structural: **your full conversation is sent with every request.** A one-line question in a session that has been open all day still draws usage for the whole conversation — at the cached rate, but not free.

Six causes, and several fire while you are not typing:

| Cause | Why |
|---|---|
| **A long conversation** | The whole thing is re-sent every turn |
| **Cache misses** | A five-minute gap, or an edit near the top of the context, and the discount is gone |
| **Compaction** | Summarising the conversation is itself a paid call over the whole conversation |
| **Scheduled tasks and loops** | Chapter 19's crons fire whether or not you are at the keyboard |
| **Cross-session messages and goal check-ins** | Another session, or a background goal, starts a turn in this one |
| **Teammates** | Every agent in a team is running its own loop |

Drag the turn count and toggle the levers:

<div class="cs-est"> <div class="cs-head"> <span class="cs-title">Session spend, illustrated</span> <span class="cs-sub">Rough arithmetic, not a bill</span> </div> <div class="cs-row"> <label class="cs-lab" for="cs-turns">Turns in the session</label> <input type="range" id="cs-turns" min="5" max="60" step="5" value="30" class="cs-range"> <output class="cs-out" id="cs-turns-v">30</output> </div> <div class="cs-opts"> <label class="cs-opt"><input type="checkbox" id="cs-clear"> <span><code>/clear</code> between tasks</span></label> <label class="cs-opt"><input type="checkbox" id="cs-md" checked> <span>800-line <code>CLAUDE.md</code></span></label> <label class="cs-opt"><input type="checkbox" id="cs-mcp" checked> <span>3 MCP servers connected</span></label> <label class="cs-opt"><input type="checkbox" id="cs-hook"> <span><code>PreToolUse</code> hook filters test output</span></label> <label class="cs-opt"><input type="checkbox" id="cs-team"> <span>Agent team, teammates in plan mode</span></label> </div> <div class="cs-bars" id="cs-bars"></div> <div class="cs-tot"> <div class="cs-tot-cell"><span class="cs-tot-n" id="cs-tokens">—</span><span class="cs-tot-l">tokens sent</span></div> <div class="cs-tot-cell"><span class="cs-tot-n" id="cs-final">—</span><span class="cs-tot-l">context on the last turn</span></div> <div class="cs-tot-cell cs-tot-cost"><span class="cs-tot-n" id="cs-cost">—</span><span class="cs-tot-l">at list API rates</span></div> </div> <p class="cs-note" id="cs-note"></p> </div> <script> (function () { var el = function (id) { return document.getElementById(id); }; var turns = el("cs-turns"), turnsV = el("cs-turns-v"), bars = el("cs-bars"); var opts = { clear: el("cs-clear"), md: el("cs-md"), mcp: el("cs-mcp"), hook: el("cs-hook"), team: el("cs-team") }; var K = function (n) { return n >= 1000000 ? (n / 1000000).toFixed(1) + "M" : Math.round(n / 1000) + "K"; }; function model() { var n = parseInt(turns.value, 10); var base = 12000; var md = opts.md.checked ? 8000 : 2000; var mcp = opts.mcp.checked ? 9000 : 0; var start = base + md + mcp; var ctx = start, sent = 0, peak = start, compactions = 0; for (var i = 1; i <= n; i++) { if (opts.clear.checked && i % 10 === 1 && i > 1) ctx = start; var grow = 3000; if (i % 5 === 0) grow += opts.hook.checked ? 1200 : 16000; ctx += grow; if (ctx > 180000) { compactions++; sent += ctx; ctx = start + 45000; } sent += ctx; if (ctx > peak) peak = ctx; } var factor = opts.team.checked ? 7 : 1; sent *= factor; var cost = (sent / 1000000) * 0.30 + (n * factor * 900 / 1000000) * 15; return { n: n, sent: sent, ctx: ctx, peak: peak, start: start, cost: cost, md: md, mcp: mcp, base: base, compactions: compactions }; } function render() { var m = model(); turnsV.textContent = m.n; el("cs-tokens").textContent = K(m.sent); el("cs-final").textContent = K(m.ctx); el("cs-cost").textContent = "$" + (m.cost < 10 ? m.cost.toFixed(2) : m.cost.toFixed(0)); var parts = [ { k: "Harness and tools", v: m.base }, { k: "CLAUDE.md", v: m.md }, { k: "MCP tool listings", v: m.mcp }, { k: "Conversation so far", v: Math.max(0, m.ctx - m.start) } ]; var max = parts.reduce(function (a, p) { return Math.max(a, p.v); }, 1); bars.innerHTML = parts.map(function (p) { var w = Math.max(2, Math.round(p.v / max * 100)); return '<div class="cs-bar"><span class="cs-bar-k">' + p.k + '</span>' + '<span class="cs-bar-t"><span class="cs-bar-f" style="width:' + w + '%"></span></span>' + '<span class="cs-bar-v">' + K(p.v) + '</span></div>'; }).join(""); var note; if (m.compactions > 0) { note = "The window filled " + m.compactions + (m.compactions === 1 ? " time" : " times") + ". Each compaction is itself a paid call that re-reads the whole conversation to summarise it — and everything after it is working from that summary rather than the original."; } else if (opts.team.checked) { note = "Teammates in plan mode multiply the whole session by about seven. Everything else on this panel is noise next to that."; } else if (!opts.clear.checked && m.ctx > 90000) { note = "Every one of those " + m.n + " turns re-sent the whole conversation. By the last one a single yes/no question was carrying " + K(m.ctx) + " of context."; } else if (opts.clear.checked && !opts.hook.checked) { note = "Clearing caps the growth, but the test runs still dump their full output into the window each time. A hook that greps for failures is the cheaper fix."; } else if (opts.clear.checked && opts.hook.checked && m.md === 2000 && m.mcp === 0) { note = "Small starting context, cleared between tasks, output filtered before it lands. This is what the levers add up to."; } else { note = "The starting context is paid again on every single turn — it is the one number worth shrinking first."; } el("cs-note").textContent = note; } turns.addEventListener("input", render); Object.keys(opts).forEach(function (k) { opts[k].addEventListener("change", render); }); render(); })(); </script>

## Cutting it

Roughly in order of effect:

1. **`/clear` between unrelated tasks.** Stale context is re-sent on every message. `/rename` first so you can find it again.
2. **Match the model to the job.** Sonnet handles most coding; keep Opus for architecture and multi-step reasoning. `model: haiku` on a simple subagent is free money.
3. **Delegate verbose work to subagents** (Chapter 17) — test output and doc fetches stay in their window.
4. **Move workflow instructions out of `CLAUDE.md` into skills** (Chapters 6 and 11). Under 200 lines.
5. **Lower effort for simple work.** Thinking tokens bill as output, and the default budget can be tens of thousands of tokens per request.
6. **Prefer CLI tools to MCP servers where both exist.** `gh` and `aws` add no per-tool listing at all.

And two habits that save money by avoiding waste rather than trimming context: **plan mode before anything complex** (Chapter 3 — planning is cheaper than rework), and **`Esc` early** when Claude heads the wrong way.

The most interesting technique is the one that sounds like plumbing: **preprocess with a hook** (Chapter 12). A `PreToolUse` hook that rewrites `npm test` to grep for failures turns tens of thousands of tokens of test output into hundreds — and because hooks run outside the context window, the filtering itself is free.

> **Agent teams use roughly 7× the tokens of a standard session** when teammates run in plan mode. Chapter 18's "start with 3–5" is a cost statement as much as a coordination one.

## The security model

Everything in Part 1 was one idea from this page: **Claude Code has only the permissions you grant it.** In Manual mode it starts read-only and asks before editing, executing, or reaching the network.

The built-in protections, most of which now have a chapter behind them:

| Protection | Covered in |
|---|---|
| Working directory boundary | Chapter 4 |
| Sandboxed Bash — OS-level filesystem and network isolation | Chapter 4 |
| Trust verification for new codebases and MCP servers | Chapters 4 and 14 |
| Auto mode's classifier | Chapter 3 |
| Credentials in the macOS Keychain, or file permissions elsewhere | — |

### Against prompt injection

Injection is the attack that matters for an agent that reads your files and the web. The layered defences:

- **Isolated context windows for web fetch**, so a fetched page cannot inject into your main conversation.
- **Network commands are not auto-approved.** `curl` and `wget` prompt like any other non-read-only command.
- **The classifier never sees tool results** (Chapter 3), so hostile file content cannot address it directly.
- **Command injection detection** — a suspicious Bash command prompts even if previously allowlisted.
- **Fail-closed matching.** An unmatched command needs approval; it does not fall through.

Then the sentence that should be quoted rather than paraphrased:

> **While these protections significantly reduce risk, no system is completely immune to all attacks.**

Which is why the practical advice is behavioural, not configurational: review commands before approving, **do not pipe untrusted content directly into Claude**, verify changes to critical files, and run anything touching external services in a VM or container.

Two gaps worth naming because they are easy to walk into. **`-p` runs disable trust verification entirely** — Chapter 16's argument for `--bare`. And **starting in your home directory never persists trust**; the prompt returns every launch, with no setting to change it. Start from a project directory.

### For teams

`ConfigChange` hooks (Chapter 12) can audit or block settings changes mid-session — the answer to "how do I know nobody widened their own permissions". Managed settings enforce the rest, and `/security-review` runs an on-demand pass over the current branch.

Vulnerabilities go to Anthropic's HackerOne programme, not a public issue.

## What an organisation can see

| Setup | See spend | Cap it | Per-user |
|---|---|---|---|
| **Team / Enterprise** | Spend report in org analytics | Seat allowance, then usage-credit limits | CSV, or the Enterprise Analytics API |
| **Console (API)** | Console usage page | Workspace spend limits | Console dashboard, Analytics API |
| **Cloud providers** | Your cloud billing console | Your cloud's budgets | **OpenTelemetry only** |

Cloud-provider usage never reaches Anthropic, so the dashboards do not cover it — OTel, a Claude apps gateway, or an LLM gateway are the options.

One thing worth doing before rollout: **set a rate limit on the auto-created "Claude Code" workspace** if you are on the Console. Otherwise Claude Code traffic competes with your production workloads for the same organisation limits.

## Summary

- **~$13 per developer per active day**, $150–250 a month, under $30/day for 90%. Budget a coding seat above a chat seat.
- `/usage` for tokens and **attribution**, `/insights` for how you work, **OpenTelemetry for anything cross-setup**.
- Cost figures are **list price** unless `modelPricing` is set in managed settings.
- An idle session still spends, because **the full conversation goes with every request** — and loops, goals, teammates and cross-session messages all start turns while you are away.
- Biggest levers: **`/clear` between tasks**, match the model, delegate verbose work, keep `CLAUDE.md` small.
- A **`PreToolUse` hook that filters output** is the cheapest saving available, because hooks cost no context.
- Injection defences are layered — isolated fetch context, no auto-approved network commands, fail-closed matching — and the docs say plainly that **no system is completely immune.**
- **`-p` disables trust verification**, and **home-directory trust never persists.**
- Full reference: [costs](https://code.claude.com/docs/en/costs), [monitoring](https://code.claude.com/docs/en/monitoring-usage), [security](https://code.claude.com/docs/en/security), [analytics](https://code.claude.com/docs/en/analytics).

Chapter 22 is the other half of running it for real: what to do when it goes wrong.
