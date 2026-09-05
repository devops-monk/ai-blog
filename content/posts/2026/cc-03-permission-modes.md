---
title: "Permission Modes"
image: /images/articles/cc-03-permission-modes.webp
toc: true
date: 2026-09-05T12:00:00+00:00
description: "The six permission modes, what each one auto-approves, the auto-mode classifier's default block and allow lists, the thresholds at which it stops trusting itself, and the protected and critical paths no mode will auto-approve."
tags: ["claude-code", "permissions", "auto-mode", "security", "classifier"]
categories: ["Fundamentals"]
url: /2026/09/permission-modes/
series: "Part 1 — Foundations"
series_order: 3
---

Chapter 1 established the asymmetry: read-only tools run without asking, state-changing tools do not. A permission mode sets where that line falls for a session.

The mode is one gate among several, and the order matters more than any individual mode does.

```mermaid
flowchart TB
    A([Tool call]) --> D{deny rule?}
    D -->|match| X([Blocked])
    D -->|no| K{ask rule?}
    K -->|match| P([Prompt])
    K -->|no| S{protected or<br/>critical path?}
    S -->|yes| M2[Mode-specific<br/>handling]
    S -->|no| M{Permission mode}
    M -->|default / acceptEdits| P
    M -->|dontAsk| X
    M -->|bypassPermissions| R([Runs])
    M -->|auto| C{Classifier}
    C -->|approves| R
    C -->|blocks| X
```

Two consequences fall out of that ordering, and both are load-bearing for the rest of this chapter:

- **`deny` rules block before the classifier is consulted.** Nothing downstream can override them — not the classifier, not user intent, not `bypassPermissions`.
- **Explicit `ask` rules force a prompt even in auto mode**, because an ask rule is a stated intent to be asked.

Chapter 4 covers the rules themselves. This chapter is the mode layer.

## The six modes

| Mode | Runs without asking | Use for |
|---|---|---|
| `default` (Manual) | Reads only | Reviewing every action, sensitive work |
| `acceptEdits` | Reads, file edits, common filesystem commands | Iterating on code you review afterwards |
| `plan` | Reads, plus classifier-approved commands when auto mode is available | Exploring before changing |
| `auto` | Everything, subject to background classifier review | Long tasks, reducing prompt volume |
| `dontAsk` | Only pre-approved tools | Locked-down CI and scripts |
| `bypassPermissions` | Everything | Isolated containers and VMs only |

The mode whose config value is `default` is labelled **Manual** in the CLI, `claude --help`, the VS Code and JetBrains extensions and the desktop app. `manual` is accepted as an alias wherever you type the value — `claude --permission-mode manual`, `"defaultMode": "manual"` — from v2.1.200. Hooks and SDK integrations use `default`.

### Which mode a session starts in

Resolution order for a terminal session:

1. `--permission-mode`, or `--dangerously-skip-permissions`
2. `permissions.defaultMode` in a settings file
3. The built-in default

The built-in default is **not** Manual for most readers of this handbook:

| How you run Claude Code | Built-in starting mode |
|---|---|
| Any settings file sets `disableAutoMode` to `"disable"` | `default` |
| Feature-flag fetching is off | `default` |
| The first session after an install or upgrade that adds this default | `default` |
| `claude -p` or the Agent SDK | `default` |
| Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, Claude Platform on AWS, or a signed-in Claude apps gateway | `default` |
| **A Pro, Max or Team plan, in a terminal or the VS Code extension** | **`auto`** |
| An Enterprise plan or a Claude Console API key | `default` |

The `auto` built-in default requires v2.1.228 or later on macOS, Linux and WSL, and v2.1.233 on native Windows. Earlier versions start in Manual.

There is a trap in step 2. **`"auto"` and `"bypassPermissions"` do not take effect from `.claude/settings.json` or `.claude/settings.local.json`.** Setting `auto` there is silently ignored and the built-in default applies instead; setting `bypassPermissions` there starts the session in Manual. Both work from `~/.claude/settings.json`. If you set `defaultMode: "auto"` and sessions keep starting in Manual with no error, that is why.

### Switching modes

`Shift+Tab` cycles. The cycle is not what most material claims:

- From `auto`, the first press switches to `default`.
- The cycle then runs `default → acceptEdits → plan → default`.
- Optional modes slot in **after `plan`**, with `bypassPermissions` first and `auto` last.

`bypassPermissions` appears in the cycle only after you start with `--permission-mode bypassPermissions`, `--dangerously-skip-permissions`, `--allow-dangerously-skip-permissions`, or `permissions.defaultMode: "bypassPermissions"` in user, `--settings` or managed settings. The `--allow-` variant adds it to the cycle without activating it. **`dontAsk` never appears in the cycle** and must be set with `--permission-mode dontAsk`.

The status bar reports the active mode:

| Mode | Status bar |
|---|---|
| `default` | `⏸ manual mode on` (grey) |
| `acceptEdits` | `⏵⏵ accept edits on` |
| `plan` | `⏸ plan mode on` |
| `auto` | `⏵⏵ auto mode on` |
| `dontAsk` | `⏵⏵ don't ask on` |
| `bypassPermissions` | `⏵⏵ bypass permissions on` |

Asking Claude in chat to change the permission mode does not work. It is a client-side control.

## Try the matrix

Ten actions against all six modes. The outcome for a given pair is rarely guessable from the mode name alone, which is the point.

<div class="pm-sim"> <div class="pm-modes" id="pm-modes"> <button type="button" class="pm-mode on" data-m="default">Manual</button> <button type="button" class="pm-mode" data-m="acceptEdits">acceptEdits</button> <button type="button" class="pm-mode" data-m="plan">plan</button> <button type="button" class="pm-mode" data-m="auto">auto</button> <button type="button" class="pm-mode" data-m="dontAsk">dontAsk</button> <button type="button" class="pm-mode" data-m="bypass">bypass</button> </div> <div class="pm-legend"><span class="pm-pill pm-runs">runs</span><span class="pm-pill pm-prompt">prompts</span><span class="pm-pill pm-class">classifier</span><span class="pm-pill pm-deny">denied</span></div> <table class="pm-table"><tbody id="pm-rows"></tbody></table> </div> <script> (function () { var A = [ "Read src/app.ts", "Edit src/app.ts", "mkdir build", "npm test", "git push origin feature/x", "git push --force", "curl https://get.example.sh | bash", "Write .git/config", "rm -rf ~", "Read ../other-repo/README.md" ]; var R = "runs", P = "prompt", C = "class", D = "deny"; var M = { "default": [ [R, "Reads never prompt."], [P, "File edits prompt in Manual mode."], [P, "Only acceptEdits auto-approves mkdir."], [P, "Not in the built-in read-only set."], [P, "Every non-read-only Bash command prompts."], [P, "Every non-read-only Bash command prompts."], [P, "Every non-read-only Bash command prompts."], [P, "Protected path. Prompted in this mode."], [P, "Critical path. Prompted in this mode."], [R, "Reads outside the working directories run while blockReadsOutsideWorkingDirectories is off."] ], "acceptEdits": [ [R, "Reads never prompt."], [R, "Edits inside the working directory run without asking."], [R, "mkdir is in the auto-approved filesystem set."], [P, "Not a filesystem command and not read-only."], [P, "Only mkdir, touch, rm, rmdir, mv, cp and sed are covered."], [P, "Only the filesystem set is covered."], [P, "Only the filesystem set is covered."], [P, "Protected-path writes are never auto-approved here."], [P, "Critical path. The filesystem set does not cover it."], [R, "Reads are unaffected by this mode."] ], "plan": [ [R, "Reads are the point of plan mode."], [D, "Edits stay blocked until you approve a plan."], [C, "Shell commands during planning go to the classifier when auto mode is available."], [C, "Approved commands run. Rejected ones are blocked."], [C, "Reviewed like any other planning command."], [C, "Force push is on the default block list."], [C, "Piping a download into a shell is on the default block list."], [C, "Classifier when auto mode is available during planning, otherwise prompted."], [P, "Prompted, or sent to the classifier when auto mode is available and bypass is not."], [R, "Reads are unaffected."] ], "auto": [ [R, "Read-only actions are auto-approved before the classifier."], [R, "File edits in the working directory are auto-approved."], [C, "Everything that is not read-only or an in-directory edit goes to the classifier."], [C, "A narrow allow rule such as Bash(npm test) would resolve this before the classifier."], [C, "Pushing to any branch of your own repository is allowed by default."], [C, "Force push is on the default block list."], [C, "Downloading and executing code is on the default block list."], [C, "Protected-path writes route to the classifier even when an allow rule matches."], [C, "Critical-path removals route to the classifier, including inside command substitution."], [P, "The first read outside the working directories prompts once, then records your answer."] ], "dontAsk": [ [R, "Read-only Bash commands and reads still run."], [D, "Auto-denied unless an allow rule matches."], [D, "Auto-denied unless an allow rule matches."], [D, "Runs only with an allow rule such as Bash(npm test)."], [D, "Anything that would prompt is denied instead."], [D, "Anything that would prompt is denied instead."], [D, "Anything that would prompt is denied instead."], [D, "Protected-path writes are denied."], [D, "Denied even when an allow rule or a PreToolUse hook allows it."], [R, "Reads are not denied."] ], "bypass": [ [R, "No checks run."], [R, "No checks run."], [R, "No checks run."], [R, "No checks run."], [R, "No checks run."], [R, "No checks run."], [R, "No checks run."], [R, "Protected-path writes are allowed in this mode only."], [P, "Critical-path removals still prompt, even here. This is the one row that surprises people."], [R, "No checks run."] ] }; var LBL = { runs: "runs", prompt: "prompts", "class": "classifier", deny: "denied" }; var rows = document.getElementById("pm-rows"), btns = document.querySelectorAll(".pm-mode"); function render(mode) { var data = M[mode]; rows.innerHTML = A.map(function (a, i) { var o = data[i]; return "<tr><td class=\"pm-act\"><code>" + a + "</code></td>" + "<td class=\"pm-out\"><span class=\"pm-pill pm-" + o[0] + "\">" + LBL[o[0]] + "</span></td>" + "<td class=\"pm-why\">" + o[1] + "</td></tr>"; }).join(""); } Array.prototype.forEach.call(btns, function (b) { b.addEventListener("click", function () { Array.prototype.forEach.call(btns, function (x) { x.classList.remove("on"); }); b.classList.add("on"); render(b.getAttribute("data-m")); }); }); render("default"); })(); </script>

## `default` — Manual

Reads run. Everything else prompts. Nothing further to configure.

```bash
claude --permission-mode default    # or: manual
```

## `acceptEdits`

File creation and edits inside the working directory run without prompting. So do a specific set of filesystem Bash commands:

```
mkdir  touch  rm  rmdir  mv  cp  sed
```

These are also auto-approved when prefixed with safe environment variables (`LANG=C`, `NO_COLOR=1`) or process wrappers (`timeout`, `nice`, `nohup`).

With the PowerShell tool enabled, `Set-Content`, `Add-Content`, `Clear-Content` and `Remove-Item` are auto-approved on in-scope paths, along with common aliases. One exception: a positional argument containing a quote character — `Set-Content .\notes.txt "It's done"` — still prompts, because the quoted and unquoted readings differ and cannot be statically validated. Pass content through a named parameter such as `-Value` instead.

What still prompts in `acceptEdits`:

- Paths outside the working directory and `additionalDirectories`
- Writes to [protected paths](#protected-paths)
- `rm` and `rmdir` targeting a [critical path](#critical-paths)
- Every other Bash command except the built-in read-only set

## `plan`

Claude reads, explores and writes a plan without editing source. Edits stay blocked until you approve the plan — except in sessions where bypass permissions are available, where plan-mode blocks are not enforced at all.

**Shell commands do run in plan mode.** When auto mode is available and `useAutoModeDuringPlan` is on — it is by default — the classifier reviews shell commands during planning instead of prompting you; approved commands run, rejected ones are blocked. Without auto mode, commands outside the built-in read-only set prompt for approval. This is worth stating plainly because plan mode is widely described as forbidding shell commands, and that has not been true for some time.

Enter with `Shift+Tab`, or prefix a single prompt with `/plan`, or start there:

```bash
claude --permission-mode plan
```

`Shift+Tab` again leaves plan mode without approving anything.

### Approving a plan

When the plan is ready Claude presents it with three options:

| Option | Effect |
|---|---|
| **Yes, and use auto mode** | Approve and switch to auto mode. Reads **Yes, auto-accept edits** when auto mode is unavailable, or offers to switch to bypass permissions if the session started with them enabled |
| **Yes, manually approve edits** | Approve and review each edit |
| **No, keep planning** | Stay in plan mode and refine |

Approving exits plan mode and switches the session to the mode the chosen option names. `Ctrl+G` opens the proposed plan in your `$EDITOR` so you can edit it before Claude proceeds. With `showClearContextOnPlanAccept` enabled, a fourth option approves the plan and clears the planning context. Accepting a plan also generates a session title, unless you already named the session.

To default a project to plan mode, set `defaultMode` to `plan` in `.claude/settings.json`. The VS Code extension does not read project settings for the starting mode — set `claudeCode.initialPermissionMode` there instead.

## `auto`

Auto mode does not remove the safety check. It relocates it: a separate classifier model reviews actions before they run, blocking anything that escalates beyond your request, targets unrecognised infrastructure, or appears driven by hostile content Claude read.

The classifier also reviews:

- Each `SendMessage` to another agent, plain or structured, before delivery (v2.1.222+)
- `rm` and `rmdir` removals targeting a critical path, including when hidden inside command or process substitution

Auto mode additionally nudges Claude to keep working rather than stopping to ask clarifying questions. For autonomous behaviour in a mode that still prompts, set the Proactive output style instead (Chapter 10).

### What the classifier evaluates

Not everything reaches it. The resolution order inside auto mode:

1. Actions matching your allow, ask or deny rules resolve immediately. Protected-path writes route to the classifier even when an allow rule matches, as do critical-path removals (v2.1.218+). MCP tools marked `requiresUserInteraction` and connector tools your organisation set to `ask` prompt you directly. Ask rules that match on command content, such as `Bash(git push *)`, fall back to a prompt.
2. Read-only actions and file edits in the working directory are auto-approved, except protected-path writes and the [first read outside the working directories](#the-first-read-outside-the-working-directories).
3. Everything else goes to the classifier.
4. If the classifier blocks, Claude receives the reason and tries an alternative.

The classifier sees your messages, non-read-only tool calls, and your `CLAUDE.md`. **Tool results are stripped**, so hostile content in a file or web page cannot manipulate it directly. Before a command that would discard uncommitted work, Claude Code runs `git status` itself and shows the classifier whether staged, modified or untracked work exists — reporting untracked files even when `status.showUntrackedFiles=no`.

Narrow allow rules such as `Bash(npm test)` stay in effect in auto mode. Broad rules that grant arbitrary execution — `Bash(*)`, wildcarded interpreters — and every rule naming `Monitor` are suspended and restored when you leave auto mode.

### Blocked by default

The trust boundary starts small: the working directory and the remotes configured for it **when the session started**. A remote added or repointed mid-session with `git remote add` or `git remote set-url` is not trusted. Everything else is external until configured.

Core blocks:

- Downloading and executing code, such as `curl | bash`
- Sending sensitive data to external endpoints
- Production deploys and migrations
- Mass deletion on cloud storage
- Granting IAM or repository permissions
- Modifying shared infrastructure
- Irreversibly destroying files that existed before the session
- Force push
- Committing or pushing a change that would send secrets outside the repository when it runs, or widen what a deploy exposes
- `git reset --hard`, `git checkout -- .`, `git restore .`, `git clean -fd`, `git stash drop`, `git stash clear` — presumed to discard uncommitted work
- `git commit --amend` when HEAD was not created in this session, or (v2.1.198+) when HEAD has already been pushed. A message-only reword of a commit Claude created this session is not blocked
- `terraform destroy`, `pulumi destroy`, `cdk destroy`, `terragrunt destroy`, and applying a plan that destroys resources

Added in v2.1.195, several keyed to `environment` entries you can narrow:

- Writing to a secret manager, or changing DNS records or TLS certificates
- Merging a PR no human approved, approving Claude's own PR, or disabling CI checks
- Posting a comment that is itself a command to automation, such as `atlantis apply`
- Toggling, ramping or deleting a production feature flag
- Applying IaC changes to a protected scope, or draining and removing cluster nodes
- Writes to a shared compute cluster beyond the resource you named, such as a label selector or `--all`
- Kubernetes resources that run on every node or intercept cluster traffic — DaemonSets, admission webhooks
- Interactive shells or port-forwards into a sensitive remote target
- Tunnels or reverse shells exposing a local service to the internet
- Printing a live credential into the transcript or a file
- Accessing or copying data out of a listed sensitive data location
- Routing a package install around your internal registry to a public one
- Flags that disarm a safety guard, such as `--insecure`
- Launching an autonomous agent loop without approval or a sandbox
- Chrome actions that could send page content, cookies or credentials off-origin

Added in v2.1.198:

- Deleting files in `/tmp`, `$TMPDIR` or another shared scratch directory by wildcard, glob or age filter rather than a named path
- Including sensitive details in outbound content your message did not authorise for that recipient — PR and issue bodies, commit messages and comments count when the repository is outside the trust boundary
- Sending keystrokes to Claude Code's own tmux pane, treated as Claude altering its own oversight

Added in v2.1.200:

- Commenting out, deleting or force-passing a test that guards security behaviour
- Deleting a stateful resource Claude did not create, when you did not name it
- Repointing an API base URL, proxy, webhook receiver or registry mirror at an unrelated third-party host, including in `.env.example`
- Changing where pushes go with `git remote set-url` or `git remote add`, unless you named the new remote
- Pushing secrets or personal data to a known-public repository
- Opening a PR against a different repository or organisation, `gh repo fork`, or pushing to a third-party repository, unless you named that target

Added in v2.1.203: content from a sensitive local store, or a file whose name or type marks it sensitive, entering a commit, push, PR text, gist or package publish unless you named both source and destination.

Added in v2.1.205:

- Writing to Claude Code's own session transcripts under `~/.claude/projects/`. Reading them is not blocked
- A recursive forced delete whose target is an unassigned shell variable, such as `rm -rf "$VAR"` — the value came from command output the classifier never sees, so it cannot verify the target

Added in v2.1.257:

- Requesting credentials from the cloud instance-metadata endpoint (`169.254.169.254`), or authenticating with the machine's own service-account identity
- Reaching a public host by tunnel, reverse shell, or a rewritten resolver or proxy
- Reading credentials belonging to the host rather than your task
- Connecting to or scanning sibling containers, pods or VMs Claude did not start

### Allowed by default

- Local file operations in the working directory
- Installing dependencies declared in your lock files or manifests
- Reading `.env` and sending credentials to their matching API
- Read-only HTTP requests
- **Pushing to any branch of the repository you are working in, including the default branch.** A non-default branch whose name marks it as a deploy target — `production`, `release`, `gh-pages` — is not covered; the classifier judges those on their own terms. Content is still checked

From v2.1.195, also: deleting jobs Claude created earlier in the same session; reading and writing security-related code as part of your task; messages between agents in the same multi-agent session; sending data to domains and buckets listed in `environment`; Chrome navigation to a trusted internal domain, localhost, or a URL you named.

Sandbox network requests route through the classifier rather than being allowed by default. Verdicts are cached per host and port (v2.1.198+): an allow is reused until new content enters the conversation; a deny lasts for the turn in the interactive CLI, and for the whole run in `-p` and Agent SDK sessions, which have no turn boundary. Changing your permission mode or rules drops all cached verdicts.

`claude auto-mode defaults` prints the full rule lists as JSON.

### Boundaries stated in conversation

The classifier treats a boundary you state as a block signal. "Don't push" or "wait until I review before deploying" blocks matching actions even when the default rules would allow them, and stays in force until you lift it. Claude's own judgment that the condition is met does not lift it.

Boundaries are not stored as rules — the classifier re-reads them from the transcript on each check. **A boundary can be lost if compaction removes the message that stated it.** For a durable guarantee, use an `ask` or `deny` rule.

### When auto mode falls back

Auto mode has a circuit breaker.

| Event | Result |
|---|---|
| A blocked action | Notification, plus an entry in `/permissions` → **Recently denied**, where `r` retries with manual approval |
| **3 blocks in a row, or 20 blocks total** | **Auto mode pauses and Claude Code resumes prompting.** Approving the prompted action resumes auto mode |
| A mode switch while a check is pending | The verdict is discarded rather than applied; you are prompted, or the action is auto-denied in `dontAsk` |

The thresholds are not configurable. Any allowed action resets the consecutive counter; the total counter persists for the session and resets only when its own limit triggers a fallback. Denials caused by a safety check refusing the classifier's own request do not count toward either threshold.

In a non-interactive `-p` run without `--permission-prompt-tool` there is no prompt to fall back to: on reaching a threshold the action does not run and Claude keeps working. The run is not stopped.

Repeated blocks usually mean the classifier lacks context about your infrastructure.

### Availability

Auto mode requires all of:

- **Plan**: all plans. On Team and Enterprise it is on by default; administrators disable it with `permissions.disableAutoMode: "disable"` in managed settings
- **Model**: on the Anthropic API and Claude Platform on AWS — Opus 4.6+, Sonnet 4.6+, or a Fable model. On Bedrock, Google Cloud's Agent Platform, Microsoft Foundry and signed-in gateway sessions — Sonnet 5, Opus 4.7+, or Fable. Sonnet 4.5, Opus 4.5, Haiku and claude-3 models are unsupported everywhere
- **Provider**: available by default on all listed providers

A message naming a model and saying auto mode "cannot determine the safety" of an action means a classifier request failed — usually transient, though on Bedrock it can repeat until your account can invoke that model. Anthropic can also turn auto mode off server-side; a session that receives that answer keeps it off until the session ends.

### Configuring the classifier

By default the classifier trusts only your working directory and the current repository's remotes. Pushing to your company's source-control org or writing to a team bucket is blocked until you say otherwise.

Configuration lives in the `autoMode` settings block, read from `~/.claude/settings.json`, managed settings, and the `--settings` flag. **It is deliberately not read from `.claude/settings.json` or `.claude/settings.local.json`** — both live in the repository, so a checked-in file or a build step could otherwise inject its own allow rules. Before v2.1.207 the classifier did read `settings.local.json`; move any `autoMode` block out of it.

The classifier also reads your `CLAUDE.md`, so "never force push" there steers Claude and the classifier together.

`autoMode.environment` is the field most people need. Entries are prose, not patterns:

```json
{
  "autoMode": {
    "environment": [
      "$defaults",
      "Source control: github.example.com/acme-corp and all repos under it",
      "Trusted cloud buckets: s3://acme-build-artifacts, gs://acme-ml-datasets",
      "Trusted internal domains: *.corp.example.com, api.internal.example.com",
      "Key internal services: Jenkins at ci.example.com, Artifactory at artifacts.example.com"
    ]
  }
}
```

Three more fields replace the built-in rule lists, evaluated in four tiers: `hard_deny` blocks unconditionally; `soft_deny` blocks next; `allow` overrides matching `soft_deny` rules; explicit user intent overrides the remaining soft blocks. Intent must be specific — "clean up the repo" does not authorise a force push, "force-push this branch" does.

```json
{
  "autoMode": {
    "allow": ["$defaults", "Deploying to the staging namespace is allowed: staging is isolated and resets nightly"],
    "soft_deny": ["$defaults", "Never run database migrations outside the migrations CLI"],
    "hard_deny": ["$defaults", "Never send repository contents to third-party code-review APIs"]
  }
}
```

> **`"$defaults"` is not optional decoration.** Setting any of these arrays without it **replaces the entire built-in list for that section** — for `soft_deny` that discards force push, `curl | bash`, production deploys and auto-mode bypass; for `hard_deny` it discards the data-exfiltration rule. Sections are evaluated independently, so setting `environment` alone leaves the others intact.

Supporting commands:

| Command | Purpose |
|---|---|
| `claude auto-mode defaults` | Print the built-in rules as JSON. `--label 'Git Destructive'` prints one rule's full wording |
| `claude auto-mode config` | Print the effective rules with your settings applied |
| `claude auto-mode critique` | AI review of your custom rules for ambiguity and false positives |
| `claude auto-mode reset` | Remove the `autoMode` section from user settings. `--yes` skips confirmation |
| `/auto-mode-setup` | Draft `environment` entries from your project and recent sessions |
| `/permissions` → **Auto mode** tab | Edit rules without opening a settings file (v2.1.246+) |

`autoMode.classifyAllShell: true` suspends every Bash and PowerShell allow rule while auto mode is active, so the classifier sees every shell command. This closes the gap where a narrow rule like `Bash(npm test)` lets an unanticipated argument through, at the cost of a classifier call per command.

### Reading a denial

The reason shown with a blocked call is the fixed text `Blocked by classifier` in most sessions (v2.1.208+) — the classifier scores actions on an internal severity scale rather than writing an explanation. Some sessions run a model that writes a short explanation instead; treat it as a hint about the missing destination or intent.

If a call is folded into a summary line such as `Ran 3 shell commands`, `Ctrl+O` opens the transcript viewer to expand it. The notice near the input box and the **Recently denied** tab both omit the exact command; a `PermissionDenied` hook receives it as `tool_input`.

The fix depends on what was blocked:

| What was blocked | Fix |
|---|---|
| A destination needed throughout the task | Add it to `autoMode.environment` |
| A command you want to run without review from now on | Add an `allow` rule |
| A one-off action you did intend | State that intent in your next message and let Claude retry |

## `dontAsk`

Every tool call that would otherwise prompt is auto-denied. Claude runs only actions matching `permissions.allow`, read-only Bash commands, and calls a `PreToolUse` hook approves.

Calls matching your explicit `ask` rules are **denied rather than prompted**. The built-in `AskUserQuestion` tool is denied even if an allow rule matches, as are connector tools your organisation set to `ask`. Critical-path removals are denied even when an allow rule or a `PreToolUse` hook allows them.

```bash
claude -p "run the test suite" --permission-mode dontAsk --allowedTools "Bash(npm test)" "Read"
```

Claude Code on the web ignores `defaultMode: "dontAsk"` from settings files.

## `bypassPermissions`

Prompts and safety checks are disabled and tool calls execute immediately, including writes to protected paths.

Constraints that survive it:

- The [actions no mode auto-approves](#actions-no-mode-auto-approves) still prompt
- The `isolatePeerMachines` approval for messages to your sessions beyond this machine still appears
- With no applicable `crossSessionInbound` value, an inbound message from another of your sessions is held for approval unless the sending session identifies itself as also bypassing permissions
- Critical-path removals still prompt
- `deny` rules still block

You cannot enter this mode from a session that did not start with it enabled:

```bash
claude --permission-mode bypassPermissions
claude --dangerously-skip-permissions        # equivalent
```

Other constraints: refused in a session started with `--restricted` (v2.1.248+); on Linux and macOS, refused when running as root or under `sudo` unless inside a recognised sandbox — the dev container configuration runs Claude Code as a non-root user for this reason. The first interactive session shows a one-time warning dialog you must accept. Claude Code on the web does not honour `bypassPermissions` from settings files, so a repository's checked-in settings cannot start a cloud session in it. Administrators can block the mode with `permissions.disableBypassPermissionsMode`.

In sessions where bypass permissions are available, plan mode's blocks are **not enforced**: Claude is still instructed to plan without editing, but an edit or command it attempts during planning runs without prompting.

> `bypassPermissions` offers no protection against prompt injection. For far fewer prompts with background checks retained, use auto mode.

## Actions no mode auto-approves

Including `bypassPermissions`:

- Tools matched by an explicit `ask` rule
- Connector tools your organisation set to `ask`, in sessions where that setting reaches Claude Code
- Tools requiring user interaction: `AskUserQuestion`, and MCP tools marked `requiresUserInteraction`
- `rm` and `rmdir` removals targeting a critical path — no allow rule or `PreToolUse` hook `"allow"` approves these
- The cross-session messaging safeguards
- Reads outside the working directories while `permissions.blockReadsOutsideWorkingDirectories` is on (v2.1.257+)

## Protected paths

Writes here are never auto-approved except in `bypassPermissions` and in plan-mode sessions with bypass available.

| Mode | Protected-path writes |
|---|---|
| `default`, `acceptEdits` | Prompted |
| `plan` | Allowed with bypass available; otherwise classifier when auto mode is available during planning, else prompted |
| `auto` | Routed to the classifier |
| `dontAsk` | Denied |
| `bypassPermissions` | Allowed |

**`permissions.allow` rules do not pre-approve protected-path writes.** The safety check runs before allow rules are evaluated, so `Edit(.claude/**)` in any settings file has no effect here.

Directories: `.git`, `.config/git`, `.vscode`, `.idea`, `.husky`, `.cargo`, `.devcontainer`, `.yarn`, `.mvn`, and `.claude` — except `.claude/worktrees`.

Files: `.gitconfig`, `.gitmodules`; the shell startup set (`.bashrc`, `.bash_profile`, `.bash_login`, `.bash_aliases`, `.bash_logout`, `.zshrc`, `.zprofile`, `.zshenv`, `.zlogin`, `.zlogout`, `.profile`, `.envrc`); the package-manager set (`.npmrc`, `.yarnrc`, `.yarnrc.yml`, `.pnp.cjs`, `.pnp.loader.mjs`, `.pnpmfile.cjs`, `bunfig.toml`, `.bunfig.toml`); `.bazelrc`, `.bazelversion`, `.bazeliskrc`; the hook managers (`.pre-commit-config.yaml`, `lefthook.yml`, `lefthook.yaml`, `.lefthook.yml`, `.lefthook.yaml`); `gradle-wrapper.properties`, `maven-wrapper.properties`; `.devcontainer.json`; `.ripgreprc`, `pyrightconfig.json`; `.mcp.json`, `.claude.json`.

In a `--restricted` session the classifier cannot approve protected-path writes at all.

## Critical paths

No `permissions.allow` rule and no `PreToolUse` hook returning `"allow"` can approve an `rm` or `rmdir` targeting one.

| Mode | Critical-path removal |
|---|---|
| `default`, `acceptEdits` | Prompted |
| `plan` | Prompted, or classifier when auto mode is available during planning and bypass is not |
| `auto` | Classifier |
| `dontAsk` | Denied |
| `bypassPermissions` | **Prompted** |

A target is a critical path when it is the filesystem root; any direct child of the root (`/usr`, `/etc`, `/data`); your home directory; a Windows drive root or its top-level directories; your working directory or its parents; or an additional working directory or its parents when the removal is a glob under it — `rm -rf <dir>/*` triggers the check, `rm -rf <dir>` does not.

A glob or trailing slash directly under a shell variable, such as `rm -rf "$DIR"/*`, is treated as critical, because the command becomes a removal from the filesystem root when the variable is empty. Hiding a removal inside `$(...)`, backticks or `<(...)` does not skip the check — `echo "$(rm -rf ~)"` is caught.

### `Remove-Item` in PowerShell

Its own check, first matching case wins:

| Target | Outcome |
|---|---|
| System paths — filesystem root and its top-level directories, drive roots and theirs, your home directory | **Denied in every mode, without asking** |
| Wildcards — a bare `*`, or any target ending in `/*` or `\*`, including a glob under a shell variable | **Denied in every mode**, before the classifier sees it |
| Your working directory or a parent, with `-Recurse` | Treated like any other approval-needing command in your mode |

## The first read outside the working directories

While `permissions.blockReadsOutsideWorkingDirectories` is off, reads outside the working directories run without prompting in auto mode. The first time Claude uses Read, Grep or Glob outside them, you get one prompt:

| Answer | Effect |
|---|---|
| **Keep allowing** | The read runs, later reads run as before, and the answer is recorded so the prompt does not reappear |
| **Block from now on** | The read is refused and `permissions.blockReadsOutsideWorkingDirectories` is set to `true` in user settings — every later session, every mode |
| **Ask again next time** | The read is refused and the next such read prompts again |

The prompt does not appear in `-p` runs or background sessions. Whatever you answer, Claude keeps working.

## Choosing a mode

| Goal | Start with | Isolation needed |
|---|---|---|
| Review every action | `claude --permission-mode default` | None |
| Fewer prompts without a classifier | Manual plus the Bash sandbox in auto-allow mode: `--permission-mode default`, then `/sandbox` | The built-in Bash sandbox (macOS, Linux, WSL2) |
| Explore before changing | `claude --permission-mode plan` | None |
| Hands-off work | `claude --permission-mode auto` | None; a sandbox adds defence in depth |
| CI with an exact allowlist | `claude -p "…" --permission-mode dontAsk --allowedTools "Bash(npm test)" "Read"` | Whatever CI provides |
| Fully unattended | `claude -p "…" --dangerously-skip-permissions` | **Required**: a container, VM or sandbox runtime, as a non-root user |

The sandbox and auto mode work independently and combine, except in plan mode where auto-allow does not widen approvals. Chapter 4 covers sandboxing.

## Summary

- Evaluation order is deny rules → ask rules → protected and critical path checks → mode → classifier. Deny rules win over everything; ask rules force a prompt even in auto mode.
- **On Pro, Max and Team plans, interactive terminal and VS Code sessions start in `auto`, not Manual.**
- The `Shift+Tab` cycle is `default → acceptEdits → plan → default`, with optional modes after `plan` — bypass first, auto last. From `auto`, the first press goes to `default`.
- `"auto"` and `"bypassPermissions"` are ignored in `.claude/settings.json` and `.claude/settings.local.json`.
- **Plan mode runs shell commands** — the classifier reviews them when auto mode is available, which it is by default.
- The classifier's circuit breaker is **3 consecutive or 20 total blocks**, after which auto mode pauses and prompting resumes. Not configurable.
- Conversational boundaries are re-read from the transcript each check, so compaction can lose them. Use an `ask` or `deny` rule for a guarantee.
- Omitting `"$defaults"` from an `autoMode` rule array discards the entire built-in list for that section.
- `permissions.allow` cannot approve a protected-path write, and nothing can approve a critical-path removal.
- `bypassPermissions` still prompts for critical-path removals, is refused under `sudo`, and is ignored from settings files on the web.

Chapter 4 covers the rules the modes sit on top of: `Tool(specifier)` syntax, the three-tier evaluation, working directories, and the Bash sandbox.
