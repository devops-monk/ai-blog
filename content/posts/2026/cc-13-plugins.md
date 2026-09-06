---
title: "Plugins & Marketplaces"
image: /images/articles/cc-13-plugins.webp
toc: true
date: 2026-09-05T22:00:00+00:00
description: "One installable directory that bundles skills, hooks, subagents, MCP servers and settings. The layout, the one directory mistake everyone makes, what a plugin change costs your cache, and how marketplaces distribute them."
tags: ["claude-code", "plugins", "marketplaces", "distribution", "packaging"]
categories: ["Fundamentals"]
url: /2026/09/plugins-and-marketplaces/
series: "Part 3 — Teaching Claude New Tricks"
series_order: 4
---

## Overview

This chapter covers:

- Why a plugin adds no new capability, and what it adds instead
- The directory layout — and the single mistake that silently breaks most first plugins
- `userConfig`, and the two places its values are deliberately **not** substituted
- What enabling a plugin costs your prompt cache, and which component types are free
- Marketplaces, namespacing, and the trust boundary you cross when you install one

## A wrapper, not a mechanism

Everything Part 3 has covered is already available in `.claude/`. A plugin invents nothing. What it adds is **one installable, versioned, shareable unit**:

| | Standalone `.claude/` | Plugin |
|---|---|---|
| Invocation | `/hello` | `/my-plugin:hello` |
| Reach | This project | Anywhere it is installed |
| Sharing | Copy the files | `/plugin install` |
| Versioning | Whatever git gives you | A `version` field people upgrade to |

The advice in the docs is the right order of operations: **build it in `.claude/` first, convert when you want to share it.** Iterating on a plugin is slower, because changes need a reload.

## Anatomy

<div class="pl-box"> <div class="pl-cols"> <div class="pl-tree" id="pl-tree"></div> <div class="pl-panel" id="pl-panel"></div> </div> </div> <script> (function () { var NODES = [ { id: "root", d: 0, l: "release-tools/", k: "dir", t: "The plugin root", p: "The directory you pass to --plugin-dir, or the one containing .claude-plugin/plugin.json. Every component directory sits here, at the top level.", g: "This is never ~/.claude/. A .mcp.json placed there is read by nothing." }, { id: "cp", d: 1, l: ".claude-plugin/", k: "dir", t: "Manifest directory", p: "Holds plugin.json and nothing else.", g: "The mistake everyone makes: putting skills/ or hooks/ in here. They are silently not discovered." }, { id: "man", d: 2, l: "plugin.json", k: "file", t: "The manifest", p: "name is the only required field, and it is the namespace. version controls when users get updates; omit it and the version falls back to the source.", g: "Unrecognised fields are tolerated so one file can double as an npm or VS Code manifest. --strict turns that into an error." }, { id: "skills", d: 1, l: "skills/", k: "dir", t: "Skills", p: "One directory per skill, each with a SKILL.md. Invoked as /release-tools:bump.", g: "The only component path that ADDS to the default rather than replacing it — skills/ is always scanned even if the manifest names another path." }, { id: "skill", d: 2, l: "bump/SKILL.md", k: "file", t: "A skill", p: "Chapter 11's frontmatter, unchanged. Edits here reload live, with no /reload-plugins.", g: "In a plugin, the frontmatter name field sets the command name — unlike a personal skill, where the directory name does." }, { id: "agents", d: 1, l: "agents/", k: "dir", t: "Subagents", p: "Markdown definitions, referenced as release-tools:reviewer.", g: "A project or user .claude/agents/ file with the same name SHADOWS the plugin's. Delete the original or the plugin version never runs." }, { id: "hooks", d: 1, l: "hooks/hooks.json", k: "file", t: "Hooks", p: "The same hooks object as a settings file. Multiple hook files merge.", g: "Needs /reload-plugins to take effect — unlike SKILL.md. And allowManagedHooksOnly stops plugin hooks running at all." }, { id: "mcp", d: 1, l: ".mcp.json", k: "file", t: "MCP servers", p: "Server definitions, scoped as mcp__plugin_<plugin>_<server>__<tool>.", g: "The only component that can cost you the prompt cache — and only when its tools load into the prefix rather than being deferred." }, { id: "styles", d: 1, l: "output-styles/", k: "dir", t: "Output styles", p: "Chapter 10's style files. force-for-plugin applies one automatically while the plugin is enabled.", g: "force-for-plugin overrides the user's own outputStyle setting. If several plugins set it, the first loaded wins." }, { id: "bin", d: 1, l: "bin/", k: "dir", t: "Executables", p: "Added to the Bash tool's PATH while the plugin is enabled.", g: "A real capability, which is why a plugin distributed through claude.ai organisation settings cannot include one." }, { id: "settings", d: 1, l: "settings.json", k: "file", t: "Default settings", p: "Applied when the plugin is enabled. Only agent and subagentStatusLine are supported.", g: "Setting agent activates one of the plugin's own subagents as the main thread — a plugin that changes how Claude Code behaves by default." }, { id: "scripts", d: 1, l: "scripts/", k: "dir", t: "Supporting scripts", p: "Referenced from hooks and skills via ${CLAUDE_PLUGIN_ROOT}.", g: "Use ${CLAUDE_PLUGIN_DATA} instead for anything that must survive an update — the root is a per-version cache directory." } ]; var sel = "cp"; var tEl = document.getElementById("pl-tree"), pEl = document.getElementById("pl-panel"); function esc(s) { return String(s).replace(/[&<>]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]; }); } function render() { tEl.innerHTML = NODES.map(function (n) { return "<button type=\"button\" class=\"pl-n pl-" + n.k + (n.id === sel ? " on" : "") + "\" data-id=\"" + n.id + "\" style=\"padding-left:" + (0.5 + n.d * 1.1) + "rem\">" + esc(n.l) + "</button>"; }).join(""); var n = NODES.filter(function (x) { return x.id === sel; })[0]; pEl.innerHTML = "<span class=\"pl-t\">" + esc(n.t) + "</span>" + "<p class=\"pl-p\">" + esc(n.p) + "</p>" + "<div class=\"pl-g\"><span class=\"pl-gh\">Worth knowing</span>" + esc(n.g) + "</div>"; Array.prototype.forEach.call(tEl.querySelectorAll(".pl-n"), function (b) { b.addEventListener("click", function () { sel = b.getAttribute("data-id"); render(); }); }); } render(); })(); </script>

### The mistake everyone makes

> **Only `plugin.json` goes inside `.claude-plugin/`.** Every component directory — `skills/`, `agents/`, `hooks/`, `commands/` — lives at the **plugin root**. Put them inside `.claude-plugin/` and they are silently not discovered.

The plugin root is the plugin's own directory: the one you pass to `--plugin-dir`, or the one containing `.claude-plugin/plugin.json`. **It is never `~/.claude/`** — a `.mcp.json` at `~/.claude/.mcp.json` is not read by anything.

A plugin shipping exactly one skill can skip the `skills/` directory and put `SKILL.md` at the root. Use `skills/` for anything that might grow.

## The manifest

`name` is the only required field, and it is the namespace:

```json
{
  "name": "release-tools",
  "description": "Version bumping, changelog and publish workflow",
  "version": "1.2.0",
  "author": { "name": "Your Name" }
}
```

Setting `version` means users only get updates when you bump it. Omit it and the version falls back to the source.

Component paths can be overridden, and the override rule is not uniform: `commands`, `agents`, `outputStyles` and `workflows` **replace** the default directory, while `skills` **adds to** it — `skills/` is always scanned. `hooks`, `mcpServers` and `lspServers` **merge** across sources.

### `userConfig`

A plugin can declare configuration it prompts the user for:

```json
{
  "userConfig": {
    "api_endpoint": { "type": "string", "title": "API endpoint", "description": "Your endpoint", "required": true },
    "api_token":    { "type": "string", "title": "API token",   "description": "Auth token", "sensitive": true }
  }
}
```

Values arrive as `${user_config.KEY}` inside MCP, LSP, skill and agent content, and as `CLAUDE_PLUGIN_OPTION_<KEY>` environment variables in hook processes. `sensitive: true` masks the input and stores it in secure storage.

Two deliberate exclusions, both for the same reason:

> **`${user_config.*}` is not substituted into shell-form hook commands, or into monitor commands.** Interpolating a user-supplied string into a shell command is a command-injection hole. Use **exec form** — supply `args` — where each argument is passed literally with no shell involved.

## Installing, enabling, reloading

`/plugin` is the manager. Under the hood, marketplace plugins are **copied into `~/.claude/plugins/cache/`**, one directory per version, while `--plugin-dir` and skills-directory plugins are used in place.

For development, `--plugin-dir` loads a directory (or a `.zip`) without installing, and can be repeated. **A `--plugin-dir` plugin outranks an installed one of the same name for that session**, so you can test changes to something already installed. The exception is a plugin managed settings force-enable or force-disable.

### What a change costs

Chapter 8 said enabling a plugin can invalidate the prompt cache. The precise version is worth knowing, because most of it is free:

| The plugin provides | Cost on enable |
|---|---|
| Skills, commands, agents, hooks, monitors, themes | **Free** — appended after the conversation |
| MCP servers, tools deferred (the default) | **Free** — never in the cached prefix |
| MCP servers, tools loaded into the prefix | **A full re-read** of the conversation |

And the timing is not when you run `/plugin enable` — the cost lands **on the first turn after the change applies**, which means `/reload-plugins` or a new session. If a reload would trigger a full re-read, Claude Code warns and refuses; `--force` applies it anyway.

One live-reload asymmetry carried over from Chapter 11: **a `SKILL.md` edit takes effect immediately**, but hooks, `.mcp.json`, agents and output styles need `/reload-plugins`.

## Marketplaces

A marketplace is a catalogue of plugins — most usefully, a git repository:

```bash
claude plugin marketplace add anthropics/claude-plugins-community
```

Anthropic runs two: **`claude-plugins-official`**, curated and registered automatically on your first interactive launch, and **`claude-community`**, where third-party submissions land after review. Approved community plugins are pinned to a commit SHA, with CI bumping the pin as you push.

For a team, a private repository as a marketplace is the whole distribution story. `extraKnownMarketplaces` in project settings declares it — and, per Chapter 5, that key **waits for workspace trust**, which is exactly right for something that can install code.

`claude plugin validate ./my-plugin` runs the same check the review pipeline does. `--strict` turns warnings into errors.

## Namespacing

Plugin components are namespaced by plugin name, which is how two plugins can both ship a `deploy`:

| Component | Named |
|---|---|
| Skill | `/plugin-name:skill-name` |
| Agent | `plugin-name:agent-name` |
| MCP tool matcher | `mcp__plugin_<plugin>_<server>__<tool>` |

One asymmetry to know when migrating: **a project or user `.claude/agents/` definition overrides a same-named plugin agent**, so the plugin's version does nothing until you delete the original. Skills do not work that way — they are namespaced, so `/deploy` and `/my-plugin:deploy` coexist.

## The trust boundary

Installing a plugin runs someone else's hooks, MCP servers and executables on your machine. Claude Code does block path escapes, and skips symlinks pointing outside the marketplace when caching. But the substantive control is organisational:

| Setting | Effect |
|---|---|
| `allowManagedHooksOnly` | Only managed hooks run — plugin hooks do not |
| `strictKnownMarketplaces` | Only approved marketplaces |
| `blockedMarketplaces` | Deny a list |
| `strictPluginOnlyCustomization` | Customisation only through approved plugins |

`bin/` is worth singling out: a plugin's `bin/` is added to the Bash tool's `PATH` while it is enabled. That is a real capability, and it is why it cannot be included in a plugin distributed through claude.ai organisation settings.

## Summary

- A plugin adds **no new capability** — it packages skills, agents, hooks, MCP and LSP servers into one versioned, installable unit. Build in `.claude/` first.
- **Only `plugin.json` goes in `.claude-plugin/`.** Everything else sits at the plugin root, and the root is never `~/.claude/`.
- Manifest path overrides are not uniform: `commands` and `agents` **replace**, `skills` **adds**, `hooks` and `mcpServers` **merge**.
- `${user_config.*}` is deliberately **not substituted into shell-form hook commands or monitor commands** — use exec form with `args`.
- Enabling a plugin is **free for skills, agents and hooks**; only MCP tools loaded into the prefix cost a full cache re-read, and the cost lands on the first turn after `/reload-plugins`.
- `SKILL.md` edits reload live; hooks, MCP and agents need `/reload-plugins`.
- **A local `.claude/agents/` definition shadows a plugin agent of the same name.** Skills namespace instead, so both stay available.
- Full reference: [creating plugins](https://code.claude.com/docs/en/plugins), [structure and schema](https://code.claude.com/docs/en/plugins-reference), [marketplaces](https://code.claude.com/docs/en/plugin-marketplaces).

That closes Part 3. Part 4 connects Claude Code to systems outside your machine, starting with MCP — what the protocol actually is, and why ten servers do not flood your context window.
