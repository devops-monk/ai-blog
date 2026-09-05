---
title: "The Claude Code Handbook"
author: Abhay
type: page
date: 2026-09-05T00:00:00+00:00
url: /guide/
description: "Twenty-three chapters that take you from installing Claude Code to running it like an expert — permissions, context, skills, hooks, MCP, agents and everything in between."
---

<!-- The layout renders .Title as the page heading, so do NOT repeat it as an
     H2 here. Chapters become links as they publish; unpublished ones stay
     as plain text so nobody lands on a 404. -->

Most people use Claude Code the way they'd use autocomplete: type a request, take what comes back, move on. That works, and it leaves most of the tool on the table.

This handbook is the other path. Twenty-three chapters, worked end to end, on how Claude Code actually behaves — what it's allowed to do and why, what it remembers and what it forgets, how to hand it new abilities, how to make it obey rules it cannot ignore, and how to run several of it at once without the whole thing collapsing into noise.

Every chapter stands alone. Read top to bottom and you'll finish an expert.

## Part 1 — Foundations

What the thing is, how you talk to it, and how to stop it doing something you'll regret.

1. [What Claude Code Actually Is](/2026/09/what-claude-code-actually-is/) — the execution model: a text-to-text model with no I/O, the harness that supplies tools, the gather/act/verify loop, the full tool table, and session state on disk.
2. [Three Ways to Talk to Claude Code](/2026/09/three-ways-to-talk-to-claude-code/) — the three input channels, a full flag and command reference, shell-mode semantics and its cost change in v2.1.186, input handling, and voice dictation.
3. Permission Modes
4. Permissions & Sandboxing

## Part 2 — Context Engineering

The context window is the budget everything else spends. This part is about spending it well.

5. Settings: the Control Panel
6. CLAUDE.md
7. Rules & Auto Memory
8. The Context Window
9. Sessions, Checkpoints & Rewind

## Part 3 — Teaching Claude New Tricks

Turning your preferences into capabilities, and your hopes into guarantees.

10. Output Styles
11. Skills
12. Hooks
13. Plugins & Marketplaces

## Part 4 — Connecting Claude to the World

Claude knows your code. This part is about everything else it needs to know.

14. MCP Fundamentals
15. MCP in Practice
16. GitHub, GitLab & CI

## Part 5 — Agents & Autonomy

One agent is a pair programmer. Several are a team.

17. Sub-Agents
18. Agent Teams & Parallel Work
19. Automation & Scheduling
20. Claude Code Everywhere

## Part 6 — Running It for Real

What it costs, how it's secured, and what to do at 2am when it won't behave.

21. Cost, Monitoring & Security
22. When It Goes Wrong

## Closing

23. Becoming an Expert

---

## How to read this handbook

Read the first section of a chapter, then stop and try the thing on your own project before continuing. Every chapter has something you can run in under a minute.

Every diagram opens full screen — click it, then scroll or pinch to zoom. Every chapter with an interactive piece is meant to be played with rather than read past; that's usually where the idea actually lands.

Chapters are verified against the [official documentation](https://code.claude.com/docs) as they're written. Where the docs and this handbook disagree, the docs win — and I'd like to know, so [tell me](mailto:abhaypratap3537@gmail.com).
