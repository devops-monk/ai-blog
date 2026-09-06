# The Claude Code Handbook — Series Plan

A 23-chapter tutorial that takes a reader from "I installed it" to genuine expertise with Claude Code.

**Method — deck first, docs to enrich.** The 136-slide bootcamp deck is the **base**: it decides what each chapter covers and which points get made. The official documentation at `code.claude.com/docs` then **enriches and verifies** — it supplies exact flags, thresholds, version numbers and edge cases the deck does not have, and it overrules the deck wherever the two disagree (see [Known corrections](#known-corrections)).

Write **from the deck's coverage, in our own words**. The deck is a paid third-party course, watermarked on every slide: take the topics and the points, never the prose, the analogies, or the section labels.

**Reading it:** the pages are images, so `pdftotext` returns nothing. Use the Read tool's `pages` parameter, ~14 pages per call.

**Home:** [ai.devops-monk.com](https://ai.devops-monk.com/) · index at [/guide/](https://ai.devops-monk.com/guide/)

---

## Status

| # | Chapter | Part | Status |
|---|---|---|---|
| 1 | What Claude Code Actually Is | Foundations | ✅ [Published](https://ai.devops-monk.com/2026/09/what-claude-code-actually-is/) |
| 2 | Three Ways to Talk to It | Foundations | ✅ [Published](https://ai.devops-monk.com/2026/09/three-ways-to-talk-to-claude-code/) |
| 3 | Permission Modes | Foundations | ✅ [Published](https://ai.devops-monk.com/2026/09/permission-modes/) |
| 4 | Permissions & Sandboxing | Foundations | ✅ [Published](https://ai.devops-monk.com/2026/09/permissions-and-sandboxing/) |
| 5 | Settings: the Control Panel | Context Engineering | ✅ [Published](https://ai.devops-monk.com/2026/09/claude-code-settings/) |
| 6 | CLAUDE.md | Context Engineering | ✅ [Published](https://ai.devops-monk.com/2026/09/claude-md/) |
| 7 | Rules & Auto Memory | Context Engineering | ✅ [Published](https://ai.devops-monk.com/2026/09/rules-and-auto-memory/) |
| 8 | The Context Window | Context Engineering | ✅ [Published](https://ai.devops-monk.com/2026/09/context-window/) |
| 9 | Sessions, Checkpoints & Rewind | Context Engineering | ✅ [Published](https://ai.devops-monk.com/2026/09/sessions-checkpoints-rewind/) |
| 10 | Output Styles | Teaching New Tricks | ✅ [Published](https://ai.devops-monk.com/2026/09/output-styles/) |
| 11 | Skills | Teaching New Tricks | ✅ [Published](https://ai.devops-monk.com/2026/09/claude-code-skills/) |
| 12 | Hooks | Teaching New Tricks | ✅ [Published](https://ai.devops-monk.com/2026/09/claude-code-hooks/) |
| 13 | Plugins & Marketplaces | Teaching New Tricks | ✅ [Published](https://ai.devops-monk.com/2026/09/plugins-and-marketplaces/) |
| 14 | MCP Fundamentals | Connecting to the World | ✅ [Published](https://ai.devops-monk.com/2026/09/mcp-fundamentals/) |
| 15 | MCP in Practice | Connecting to the World | ✅ [Published](https://ai.devops-monk.com/2026/09/mcp-in-practice/) |
| 16 | GitHub, GitLab & CI | Connecting to the World | ✅ [Published](https://ai.devops-monk.com/2026/09/github-gitlab-and-ci/) |
| 17 | Sub-Agents | Agents & Autonomy | ⬜ Not started |
| 18 | Agent Teams & Parallel Work | Agents & Autonomy | ⬜ Not started |
| 19 | Automation & Scheduling | Agents & Autonomy | ⬜ Not started |
| 20 | Claude Code Everywhere | Agents & Autonomy | ⬜ Not started |
| 21 | Cost, Monitoring & Security | Running It for Real | ⬜ Not started |
| 22 | When It Goes Wrong | Running It for Real | ⬜ Not started |
| 23 | Becoming an Expert | Closing | ⬜ Not started |

---

## Chapters

`P` = source slide numbers · `D` = documentation pages to fetch and verify against.

### Part 1 — Foundations

**1. What Claude Code Actually Is**
LLM vs coding assistant, the agentic loop (gather context → take action → verify), the built-in tools, every surface it runs on, install paths, login, prerequisites, a first real session.
`P1–13, 110–114` · `D overview, how-claude-code-works, quickstart, setup, authentication, glossary`
*Interactive:* agentic-loop walkthrough

**2. Three Ways to Talk to It**
CLI flags before the session, slash commands during it, the `@` `!` `#` notations, bash mode, interactive shortcuts, `/help` `/doctor` `/status`, terminal config, voice dictation.
`P13–15, 63–64` · `D cli-reference, commands, interactive-mode, terminal-config, keybindings, voice-dictation`
*Interactive:* command-type sorter

**3. Permission Modes**
All six modes and what each auto-approves, the real `Shift+Tab` cycle, the plan-mode workflow, auto mode and its classifier — what gets waved through, what gets escalated, the 3-in-a-row / 20-total pause — stating boundaries in plain English, and bypass mode.
`P16–26` · `D permission-modes, auto-mode-config`
*Interactive:* **permission-mode simulator** — pick a mode and an action, see approve / ask / deny / classifier

**4. Permissions & Sandboxing**
The three-tier model, allow/ask/deny and evaluation order, `Tool(specifier)` syntax and wildcards, `/permissions`, working directories and `--add-dir`, protected and critical paths, the Bash sandbox, sandbox environments.
`P41–45` · `D permissions, sandboxing, sandbox-environments`
*Interactive:* **rule matcher** — type a rule and a command, see whether it matches and why

### Part 2 — Context Engineering

**5. Settings: the Control Panel**
`/config`, CLI arguments, `settings.json` at four scopes, precedence, `/status` as the debugger, environment variables, model config, fast mode, the advisor tool.
`P34–40` · `D settings, settings-reference, settings-example, env-vars, model-config, fast-mode, advisor`
*Interactive:* **precedence resolver** — set one key at five scopes, see which wins

**6. CLAUDE.md**
The onboarding problem, `/init`, `@path` imports, every location it can live, what to include and what never to, treating it like code, emphasis that actually lands.
`P27–33, 66` · `D memory, claude-directory`
*Interactive:* before/after prompt comparison

**7. Rules & Auto Memory**
`.claude/rules/`, always-loaded vs `paths`-scoped, priority saturation, `MEMORY.md`, the three memory layers, `/memory`, configuration and opt-out.
`P79–89` · `D memory#auto-memory, claude-directory`
*Interactive:* rule-loading visualiser

**8. The Context Window**
What fills it, `/context`, `/compact` and compact instructions, auto-compact, prompt caching, the five session habits, the status line as a fuel gauge, monorepos and large codebases.
`P48–50, 56, 74–75` · `D context-window, prompt-caching, costs, statusline, large-codebases, troubleshooting`
*Interactive:* **context-window visualiser** — sliders for history, files and skills; watch it fill

**9. Sessions, Checkpoints & Rewind**
Sessions are per-directory, `/rename`, `--continue` / `--resume`, `--fork-session`, two terminals on one session, git branches, checkpoints, `/rewind` and its four restore options, what checkpoints don't track, git as the real backstop.
`P51–62` · `D sessions, checkpointing`
*Interactive:* resume-vs-fork timeline

### Part 3 — Teaching Claude New Tricks

**10. Output Styles**
The four built-ins, writing a custom style, user vs project level, worked examples.
`P46–48` · `D output-styles`
*Interactive:* style comparison on one prompt

**11. Skills**
Progressive disclosure, the full frontmatter reference, the canonical layout, dynamic context injection, `context: fork`, bundled skills, `skillOverrides`, permissions, legacy commands and migration.
`P90–100` · `D skills`
*Interactive:* **frontmatter builder** — toggle fields, see the resulting SKILL.md and who can invoke it

**12. Hooks**
Suggestions vs guarantees, all 33 events, config structure and matchers, all five hook types, exit codes and the JSON contract, language choice and startup cost, three worked hooks.
`P101–109` · `D hooks-guide, hooks`
*Interactive:* **lifecycle timeline** — pick an event, see where it fires and what it can block

**13. Plugins & Marketplaces**
`/plugin`, what a plugin bundles, the commit-commands plugin, building one, marketplaces and distribution, the security plugins.
`P67` · `D discover-plugins, plugins, plugins-reference, plugin-marketplaces, security-guidance, claude-security`
*Interactive:* plugin anatomy explorer

### Part 4 — Connecting Claude to the World

**14. MCP Fundamentals**
Life without MCP, what the protocol is, transports and scopes, `/mcp`, tool search and why ten servers don't blow up your context, authentication, organisation controls.
`P110–114, 123–124` · `D mcp, mcp-quickstart, managed-mcp`
*Interactive:* **context-cost calculator** — servers × tools, with and without tool search

**15. MCP in Practice**
Chrome DevTools, Playwright, Context7, the native Chrome integration, the four-scenario table, prompts that actually work.
`P115–122` · `D chrome, prompt-library, common-workflows`
*Interactive:* prompt picker by scenario

**16. GitHub, GitLab & CI**
The three levels, git in plain English, how Claude really builds a PR, `/install-github-app` and `claude.yml`, the `@claude` bot, automated code review and ultrareview, GitLab CI/CD, headless `-p`.
`P65–73` · `D github-actions, code-review, ultrareview, gitlab-ci-cd, headless`
*Interactive:* PR-creation flow diagram

### Part 5 — Agents & Autonomy

**17. Sub-Agents**
Context drowning, what a subagent is, the built-ins, `/agents`, frontmatter, persistent memory, automatic delegation, foreground vs background.
`P128–135` · `D sub-agents`
*Interactive:* **context-isolation visualiser** — the same task with and without delegation

**18. Agent Teams & Parallel Work**
Agent view, agent teams, cross-session messaging, dynamic workflows, worktrees end to end, when parallelism actually pays.
`P68–70` · `D agents, agent-view, agent-teams, cross-session-messaging, workflows, worktrees`
*Interactive:* worktree layout diagram

**19. Automation & Scheduling**
`/loop` in all three forms plus `loop.md` and its limits, `/goal`, cloud routines, desktop scheduled tasks, channels, deep links.
`P125–127` · `D scheduled-tasks, goal, routines, desktop-scheduled-tasks, channels, deep-links`
*Interactive:* scheduling decision tree

**20. Claude Code Everywhere**
VS Code, JetBrains, desktop, web, mobile, Remote Control, `--cloud` / `--teleport`, Slack and Claude Tag, computer use, artifacts.
`D platforms, vs-code, jetbrains, desktop, claude-code-on-the-web, mobile, remote-control, slack, computer-use, artifacts`
*Interactive:* surface chooser

### Part 6 — Running It for Real

**21. Cost, Monitoring & Security**
`/usage` and `/cost`, cutting token spend, OpenTelemetry, team analytics and spend limits, the security model, prompt injection, data usage and ZDR, managed settings, dev containers, cloud providers.
`D costs, monitoring-usage, analytics, security, data-usage, zero-data-retention, managed-settings, devcontainer, third-party-integrations`
*Interactive:* cost estimator

**22. When It Goes Wrong**
`/doctor`, debugging why configuration isn't taking effect, the error reference, high CPU and memory, auto-compact thrashing, search problems, install and login failures.
`D troubleshooting, debug-your-config, errors, troubleshoot-install`
*Interactive:* symptom → cause lookup

### Closing

**23. Becoming an Expert**
A capstone: configure one repository end to end — CLAUDE.md, rules, skills, hooks, permissions, MCP, subagents, CI — then a self-audit checklist, the Agent SDK as the next frontier, and where to keep reading.
*Interactive:* setup checklist

---

## Known corrections

The source deck predates the current documentation. These must be written correctly, not repeated:

| Deck says | Actually |
|---|---|
| Sessions start in Manual mode | On Pro, Max and Team plans in a terminal or VS Code, `auto` is the built-in starting mode (v2.1.228+). Manual is the fallback when auto is unavailable |
| Cycle is `Manual → Accept Edits → Plan → Auto → Manual` | From `auto`, the first `Shift+Tab` goes to `default`; the cycle is then `default → acceptEdits → plan → default`. Optional modes slot in after `plan`, `bypassPermissions` first and `auto` last |
| `acceptEdits` allows "common file operations" | Specifically `mkdir`, `touch`, `rm`, `rmdir`, `mv`, `cp` and `sed`, only inside working directories. Protected and critical paths still prompt |
| Roughly 16 hook events | 33, including `Setup`, `UserPromptExpansion`, `PermissionDenied`, `PostToolBatch`, `MessageDisplay`, `TaskCreated`, `StopFailure`, `InstructionsLoaded`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`, `Elicitation`, `ElicitationResult` |
| Hook types: `command`, `http`, `prompt`, `agent` | Five — `mcp_tool` is missing. So are `if`, `timeout`, `statusMessage`, `once`, exit-code semantics and the whole `hookSpecificOutput` contract |
| Skill frontmatter is `name`, `description`, `tools`, `model` | Around twenty fields, including `allowed-tools`, `disallowed-tools`, `disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `background`, `paths`, `arguments` and `hooks`, plus dynamic context injection |
| Custom commands are deprecated | Legacy but fully supported. Skills are recommended and win on a name conflict — the nuance matters if you already have `.claude/commands/` |
| Context window: 1,000,000 tokens, 100k system prompt, 400k history | An illustration, not real figures. Present as a schematic or use verified numbers; never assert those totals |
| Shell mode (`!`) is free and consumes no tokens | Not since v2.1.186. Claude responds to `!` output automatically and that response costs a normal prompt. `respondToBashCommands: false` restores the silent behaviour |
| `#` adds a note to Claude's memory | No longer in the documentation. Say "remember that…" in plain language; auto memory picks it up |
| Voice dictation is hold-`Space` | Two modes, hold and tap, and `voice:pushToTalk` is rebindable |
| `/output-style` switches the style | The standalone command was deprecated in v2.1.73 and removed in v2.1.91. Use `/config` → **Output style**, or the `outputStyle` key, which `/config` writes to `.claude/settings.local.json` |
| Plan mode cannot run bash commands | It runs them. When auto mode is available and `useAutoModeDuringPlan` is on (the default), the classifier reviews shell commands during planning and approved ones run |

Unverified deck claims to confirm while writing the relevant chapter: `/loop` task expiry. **Resolved:** voice dictation has hold and tap modes (Ch 2); `MEMORY.md` lives at `~/.claude/projects/<project>/memory/` and only its first 200 lines or 25KB load (Ch 7); checkpoints keep snapshots for the 100 most recent per session and are swept with transcripts after `cleanupPeriodDays`, 30 days by default (Ch 9); `claude --worktree <name>` exists and needs at least one commit in the repository (Ch 15).

Areas the deck never mentions, all in scope: plugins and marketplaces, agent teams, agent view, cross-session messaging, dynamic workflows, routines, artifacts, channels, `/goal`, sandboxing, sandbox environments, GitLab CI/CD, code review, model configuration, fast mode, the advisor tool, cost and monitoring, security and enterprise deployment, large codebases, and the Agent SDK.

---

## Voice

Written for a software engineer who wants the mechanism, in detail. Specifically:

- **Open on the mechanism, not a story.** No "picture this", no "imagine you're…", no analogies standing in for an explanation. State what the thing is and how it works.
- **No coaching register.** Drop rhetorical questions, second-person pep talk, and "here's the thing" asides. Describe behaviour; let the reader draw the conclusion.
- **Specify rather than gesture.** Exact flags, file paths, version numbers, defaults, thresholds and the conditions under which behaviour changes. "Shell mode costs a normal prompt as of v2.1.186" beats "shell mode isn't free any more".
- **Tables and diagrams over prose** wherever the content is a set of options, a sequence, or a mapping.
- **Teach the concept; link out for the catalogue.** A chapter explains the mechanism and the handful of cases a reader actually hits. Exhaustive lists — every CLI flag, every slash command, every classifier rule — belong behind a link to the Claude Code docs, which stay current in a way a chapter cannot. Give the *shape* of a long list (grouped themes, the trap in it) rather than transcribing it.
- **Target 8 to 12 minutes.** Past that the chapter is a reference document, not a chapter. Chapter 3 shipped at 22 minutes and had to be cut in half.
- **Keep the corrections and the traps.** These are the parts no doc page gives the reader — deck errors, silently-ignored settings, defaults that surprise. They earn their length; reference tables do not.
- An analogy is acceptable only when it carries technical weight that plain description cannot — and never as an opener.

## Chapter shape

Every chapter follows the same skeleton, so a reader who has read one knows where to look in the next:

1. **`## Overview`** — first section, before anything else. One line ("This chapter covers:") then four or five bullets stating what the chapter *establishes*, not what its headings are called. A bullet should be readable as a claim, so the overview is worth reading even if you already know the section titles.
2. **The topic sections** — the body, opening on the mechanism.
3. **`## Summary`** — the load-bearing points as a bulleted list, then one line pointing at the next chapter.

Chapters 1 to 3 are the reference for this standard: technical register, concept-first, exhaustive detail delegated to docs links.

## Deck audit and gap register

Every published chapter re-checked against the slides mapped to it. **Open gaps are work to do**; each is a
point the deck makes that the chapter does not.

| Slides | Ch | Gaps to close |
|---|---|---|
| 1–12 | — | ✅ front matter, nothing technical |
| 13–15 | 2 | ✅ none |
| 16–26 | 3 | ✅ fixed — plan mode's three-step workflow, and planning costing fewer tokens than execution |
| 27–33 | 6 | ✅ fixed — emphasis for adherence, no secrets, no linter-enforced rules, two diagnostic symptoms |
| 34–40 | 5 | ✅ none |
| 41–45 | 4 | ✅ fixed — the approval-lifetime table, and the shapes that need `--add-dir` |
| 46–48 | 10 | ✅ none |
| 49–50 | 8 | ⬜ a **Compact Instructions section in `CLAUDE.md`** as an alternative to `/compact <instructions>` |
| 51–57 | 9 | ⬜ **session-scoped permission grants reset on resume and on fork** — both need re-approval. ⬜ sessions are tied to a directory, **not a branch**: switching branches keeps the conversation and swaps the files. ⬜ the five session habits, especially **document-and-clear** (write plan to a `.md`, `/clear`, new session reads it) |
| 58–62 | 9 | ✅ none |
| 63–64 | 2 | ✅ none |
| 65–69 | 16 | ⬜ **how Claude builds a PR** — gather context, prepare the branch, analyse the commits, `gh pr create`. ⬜ the `commit-commands` plugin (`/commit`, `/commit-push-pr`, `/clean_gone`) |
| 70–72 | 9 | ⬜ **git worktrees** — `claude --worktree <name>` / `-w`, stored at `<repo>/.claude/worktrees/<name>` on branch `worktree-<name>`, or just ask Claude to start one mid-session |
| 73–76 | 16 | ✅ none |
| 77–78 | 8 | ⬜ **the status line** — JSON in on stdin, text out on stdout; `/statusline <description>` writes the script for you |
| 79–81 | 7 | ⬜ **priority saturation** as the framing for why rules exist. ⬜ a **rules vs CLAUDE.md** placement table |
| 82–89 | 7 | ⬜ **the third memory layer** — session memory / conversation continuity, alongside CLAUDE.md and auto memory |
| 90–97 | 11 | ⬜ `assets/` and `references/` in the canonical skill layout. ⬜ a **CLAUDE.md vs rules vs skills** comparison |
| 98–100 | 11 | ✅ none |
| 101–109 | 12 | ⬜ **hooks are isolated from the context window** — they run externally and cost zero context unless they return `additionalContext`. ⬜ **language choice and startup cost** — bash ~10–20ms, Node ~50–100ms, Python ~200–400ms, and why that matters for `PreToolUse`. ⬜ the desktop-notification hook as a worked example |
| 110–115 | 14 | ✅ none |
| 116–122 | 15 | ⬜ **the three named servers** — Chrome DevTools, Playwright, Context7 — with their add commands, and the four cross-tool scenarios |
| 123–124 | 14 | ✅ none |
| 125–136 | 17–18 | ⬜ not yet written — audit while writing |

## Writing a chapter

1. Re-read the source slides, then fetch every documentation page listed for the chapter. Never write a technical claim from the deck alone.
2. Draft with the front matter from `archetypes/default.md`. **Date it in the past.** CI passes `--buildFuture` but a bare local `hugo` does not, so a future-dated chapter builds in CI and vanishes locally — the two stop agreeing, which is the worst way for this to fail. `series` is the part name, `series_order` is the chapter's position within that part, `draft: true` until verified.
3. Diagrams as ` ```mermaid ` fences. No semicolons inside labels — a semicolon silently kills the whole diagram.
4. Widget as a single raw HTML block with no blank lines anywhere inside it. **No `//` comments in its JavaScript** — collapsing to one line turns one into a line-swallower and the minifier fails the whole build with `unexpected EOF`. Use `/* */`. Styles into `custom-styles.css` under a short prefix, with a `[data-theme="dark"]` variant and a `40em` fallback.
   A `<pre>` inside a widget inherits the global `pre { background: var(--code-bg) !important }` but not `pre code`'s light colour, so it renders dark-on-dark. Set an explicit `color` on it.
   Drive a widget that makes technical claims: click every preset in headless Chrome and check each verdict against the docs. Chapter 4's matcher shipped one wrong verdict (`timeout 30 npm test`) that only this caught.
5. Cover: add an `art_*()` motif and a `COVERS` entry. **Check the name is not a prefix of an existing one** — an `art_gate` guard passes `"def art_gate" not in s` only if `art_gates` does not already exist. Then then `python3 tools/gen_covers.py <slug>` and `python3 tools/gen_social.py`.
6. Verify, drop `draft: true`, add the chapter to `content/pages/guide.md`, commit and push.

Keep `series_order` in step with the `PART n · CH n` badge baked into the cover.

## Verifying a chapter

```bash
hugo -D --buildFuture --minify --cleanDestinationDir --quiet
python3 -m http.server 8901 --directory public &

grep -c '^```mermaid' content/posts/2026/cc-NN-<slug>.md          # source blocks
chrome --headless --dump-dom "http://localhost:8901/2026/09/<slug>/" \
  | grep -c 'id="mermaid-svg-'                                     # rendered
```

The two counts must match — a broken diagram renders nothing and reports no error. Count the ids mermaid assigns, not `<pre class="mermaid"...><svg`: the `<pre>` stores the source in `data-src` and that source contains `-->`, so a regex ending the tag at the first `>` matches nothing.

Also check: the widget driven at several inputs in headless Chrome, with every number in the prose matching what it computes; light, dark and narrow viewports; the prev/next chain and chapter badge; an `og:image` that resolves to a file on disk.

Three headless traps, each of which has already cost time once:

- **Viewport clamping.** Headless clamps to 500 CSS px, so a 360px window is a crop of a 500px layout, not an overflow.
- **CSS transitions never settle.** Under `--virtual-time-budget`, a screenshot taken after JS runs catches any `transition` part-way, and `getComputedStyle` returns the interpolated value. A control that looks half-styled is usually mid-transition, not miscascaded. Re-render with `transition: none !important` before concluding the CSS is wrong.
- **`scrollIntoView` doesn't move the capture.** To photograph something below the fold, extract the component into a standalone harness with the stylesheet inlined.
