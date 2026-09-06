#!/usr/bin/env python3
"""Cover generator for the AI blog.

One shared identity (dark ground, chapter badge, Inter title, accent rule)
with a distinct hand-drawn SVG motif per article, so the set reads as a
series without every cover looking identical.
"""
import subprocess, os, sys

SP = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SP)
OUT = os.path.join(ROOT, "static/images/articles")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

BLUE, PINK, PURPLE = "#a78bfa", "#f472b6", "#7c3aed"
GREEN, AMBER, RED = "#4ade80", "#fbbf24", "#f87171"
DIM, FAINT = "#64748b", "#334155"

SHELL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
 *{margin:0;padding:0;box-sizing:border-box}
 body{width:1600px;height:640px;overflow:hidden;font-family:'Inter',sans-serif;
  background:radial-gradient(900px 600px at 12% 105%, rgba(244,114,182,.16), transparent 62%),
             radial-gradient(900px 620px at 88% -10%, rgba(167,139,250,.16), transparent 60%),
             linear-gradient(140deg,#120b20 0%,#171033 48%,#1d1440 100%)}
 .grid{position:absolute;inset:0;
  background-image:linear-gradient(rgba(148,163,184,.055) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(148,163,184,.055) 1px,transparent 1px);
  background-size:80px 80px}
 .edge{position:absolute;left:0;top:0;bottom:0;width:5px;
  background:linear-gradient(180deg,#a78bfa,#7c3aed 55%,#f472b6)}
 .wrap{position:relative;display:flex;height:100%;align-items:center;padding:0 76px 0 104px;gap:56px}
 .left{width:600px;flex:0 0 600px}
 .kicker{display:flex;align-items:center;gap:16px;margin-bottom:28px}
 .badge{border:1.5px solid rgba(167,139,250,.55);color:#a78bfa;border-radius:7px;
  padding:8px 15px;font-size:15px;font-weight:700;letter-spacing:.15em}
 .sub{color:#7c8ba1;font-size:15px;font-weight:600;letter-spacing:.24em}
 h1{color:#fff;font-size:__FS__px;font-weight:800;line-height:1.07;letter-spacing:-.022em}
 .rule{width:82px;height:5px;border-radius:3px;margin:28px 0 24px;
  background:linear-gradient(90deg,#a78bfa,#f472b6)}
 .tag{color:#b6c2d4;font-size:21px;font-weight:500;line-height:1.5}
 .right{flex:1;display:flex;align-items:center;justify-content:center}
 .cap{position:absolute;right:76px;bottom:56px;font-family:'JetBrains Mono',monospace;
  font-size:17px;color:#8fa0b8;letter-spacing:.01em}
 .cap i{color:#a78bfa;font-style:normal}
 text{font-family:'JetBrains Mono',monospace}
</style></head><body>
<div class="grid"></div><div class="edge"></div>
<div class="wrap">
  <div class="left">
    <div class="kicker"><span class="badge">__BADGE__</span><span class="sub">AI ENGINEERING</span></div>
    <h1>__TITLE__</h1>
    <div class="rule"></div>
    <div class="tag">__TAG__</div>
  </div>
  <div class="right">__ART__</div>
</div>
<div class="cap">__CAP__</div>
</body></html>"""


def art_loop():
    """The agentic loop: three phases on a cycle, with tools hanging off them."""
    import math
    cx, cy, r = 300, 200, 118
    labels = [("gather", -90), ("act", 30), ("verify", 150)]
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{FAINT}" '
           f'stroke-width="1.4" stroke-dasharray="4 6"/>']
    pts = []
    for name, deg in labels:
        a = math.radians(deg)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        pts.append((x, y, name))
    for i, (x, y, name) in enumerate(pts):
        col = [BLUE, PURPLE, GREEN][i]
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="46" fill="{col}" opacity=".14"/>')
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="46" fill="none" stroke="{col}" '
                   f'stroke-opacity=".75" stroke-width="1.8"/>')
        out.append(f'<text x="{x:.0f}" y="{y+5:.0f}" fill="#dbd3f5" font-size="16" '
                   f'text-anchor="middle">{name}</text>')
    # Arrowheads midway along each arc. The heading is measured from two
    # points on the circle rather than derived by hand, so it always points
    # the way the cycle actually runs: gather -> act -> verify -> gather.
    def on_circle(deg):
        a = math.radians(deg)
        return cx + r * math.cos(a), cy + r * math.sin(a)

    for i in range(3):
        mid = labels[i][1] + 60
        x, y = on_circle(mid)
        ax, ay = on_circle(mid + 4)          # a nudge further around the loop
        t = math.degrees(math.atan2(ay - y, ax - x))
        out.append(f'<path d="M -7 -6 L 7 0 L -7 6 Z" fill="{PINK}" opacity=".9" '
                   f'transform="translate({x:.0f} {y:.0f}) rotate({t:.0f})"/>')
    out.append(f'<text x="60" y="392" fill="{DIM}" font-size="15">'
               f'each step exists because the last one returned something</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_channels():
    """Three prompt lines, each with its channel sigil picked out."""
    rows = [
        ("$", "claude --model opus", GREEN, "before the session"),
        (">", "/context", BLUE, "during the session"),
        (">", "explain @auth.ts", PINK, "inside the prompt"),
    ]
    out = ['<rect x="30" y="40" width="580" height="290" rx="10" fill="#0d0a1a" '
           f'opacity=".55" stroke="{FAINT}" stroke-opacity=".7"/>']
    for i, (sigil, text, col, note) in enumerate(rows):
        y = 100 + i * 82
        out.append(f'<text x="58" y="{y}" fill="{col}" font-size="24">{sigil}</text>')
        x = 86
        for ch in text:
            # The sigil that names the channel is the only coloured glyph.
            hot = (ch in "-/@" and (ch != "-" or text.startswith("claude")))
            fill = col if hot else "#9d92bd"
            out.append(f'<text x="{x}" y="{y}" fill="{fill}" font-size="20">{ch}</text>')
            x += 12
        out.append(f'<text x="58" y="{y+26}" fill="{DIM}" font-size="13">{note}</text>')
    # No caption here — the shell already prints one at the bottom right.
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_gates():
    """An action falling through the gate stack: rules, mode, classifier."""
    out = []
    gates = [
        ("deny rules", RED, 90),
        ("ask rules", AMBER, 160),
        ("protected / critical", PINK, 230),
        ("permission mode", PURPLE, 300),
    ]
    for label, col, y in gates:
        out.append(f'<rect x="90" y="{y-20}" width="330" height="40" rx="8" '
                   f'fill="{col}" opacity=".13" stroke="{col}" stroke-opacity=".65"/>')
        out.append(f'<text x="110" y="{y+6}" fill="#dbd3f5" font-size="17">{label}</text>')
        # Each gate has a side exit for the calls it stops.
        out.append(f'<path d="M420 {y} L470 {y}" stroke="{col}" stroke-opacity=".7" stroke-width="1.6"/>')
        out.append(f'<path d="M-6 -5 L6 0 L-6 5 Z" fill="{col}" opacity=".8" '
                   f'transform="translate(474 {y})"/>')
    # The spine the surviving call travels down.
    out.append(f'<path d="M60 60 L60 360" stroke="{FAINT}" stroke-width="1.6" stroke-dasharray="5 5"/>')
    for _, _, y in gates:
        out.append(f'<path d="M60 {y} L90 {y}" stroke="{FAINT}" stroke-width="1.6"/>')
    out.append(f'<circle cx="60" cy="60" r="7" fill="{BLUE}"/>')
    out.append(f'<text x="78" y="65" fill="{DIM}" font-size="15">tool call</text>')
    out.append(f'<circle cx="60" cy="360" r="7" fill="{GREEN}"/>')
    out.append(f'<text x="78" y="365" fill="{DIM}" font-size="15">runs</text>')
    out.append(f'<text x="470" y="396" fill="{DIM}" font-size="14" text-anchor="end">stopped here</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_tokens():
    """A token stream with the next-token distribution hanging off the end."""
    s, x = [], 40
    for i, t in enumerate(["The", "cat", "sat", "on", "the"]):
        w = 34 + 11 * len(t)
        s.append(f'<rect x="{x}" y="150" width="{w}" height="46" rx="7" '
                 f'fill="{BLUE}" opacity=".16" stroke="{BLUE}" stroke-opacity=".5"/>')
        s.append(f'<text x="{x + w/2:.0f}" y="180" fill="#dbd3f5" font-size="19" '
                 f'text-anchor="middle">{t}</text>')
        x += w + 12
    s.append(f'<rect x="{x}" y="150" width="52" height="46" rx="7" fill="none" '
             f'stroke="{PINK}" stroke-dasharray="5 4" stroke-width="1.6"/>')
    s.append(f'<text x="{x + 26}" y="181" fill="{PINK}" font-size="22" text-anchor="middle">?</text>')
    for i, (word, p) in enumerate([("mat", .61), ("floor", .18), ("roof", .09), ("bed", .05)]):
        y = 236 + i * 40
        s.append(f'<text x="40" y="{y + 15}" fill="#9d92bd" font-size="16">{word}</text>')
        s.append(f'<rect x="126" y="{y}" width="{p * 430:.0f}" height="20" rx="4" '
                 f'fill="{PINK if i == 0 else BLUE}" opacity="{.92 if i == 0 else .3}"/>')
        s.append(f'<text x="{126 + p * 430 + 12:.0f}" y="{y + 15}" fill="{DIM}" font-size="14">{p:.2f}</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(s)}</svg>'


def art_embedding():
    """Vectors in space, with the neighbours of one query highlighted."""
    import random
    random.seed(7)
    s, near = [], []
    qx, qy = 330, 205
    for _ in range(120):
        x, y = random.gauss(320, 130), random.gauss(210, 92)
        x, y = max(30, min(610, x)), max(28, min(372, y))
        d = ((x - qx) ** 2 + (y - qy) ** 2) ** .5
        if d < 78:
            near.append((x, y))
        else:
            s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="3.4" fill="{FAINT}" opacity=".75"/>')
    s.append(f'<circle cx="{qx}" cy="{qy}" r="86" fill="{PURPLE}" opacity=".10"/>')
    s.append(f'<circle cx="{qx}" cy="{qy}" r="86" fill="none" stroke="{BLUE}" '
             f'stroke-opacity=".45" stroke-dasharray="5 5"/>')
    for x, y in near:
        s.append(f'<line x1="{qx}" y1="{qy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{BLUE}" stroke-opacity=".35"/>')
        s.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5" fill="{BLUE}"/>')
    s.append(f'<circle cx="{qx}" cy="{qy}" r="8.5" fill="{PINK}"/>')
    s.append(f'<text x="30" y="404" fill="{DIM}" font-size="15">nearest neighbours, not keyword matches</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(s)}</svg>'


def art_attention():
    """A causal attention matrix: the mask is the whole point, so draw it."""
    s, n, c = [], 11, 30
    ox, oy = 150, 44
    for r in range(n):
        for col in range(n):
            if col > r:
                s.append(f'<rect x="{ox + col*c}" y="{oy + r*c}" width="{c-3}" height="{c-3}" '
                         f'rx="2" fill="{FAINT}" opacity=".16"/>')
            else:
                w = (col + 1) / (r + 1)
                s.append(f'<rect x="{ox + col*c}" y="{oy + r*c}" width="{c-3}" height="{c-3}" '
                         f'rx="2" fill="{PURPLE if w < .8 else PINK}" opacity="{.16 + .74*w:.2f}"/>')
    s.append(f'<text x="{ox}" y="{oy + n*c + 26}" fill="{DIM}" font-size="15">'
             f'each token sees only what came before</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(s)}</svg>'


def art_boundary():
    """A sandboxed command reaching out: one write lands, two hit the wall."""
    out = []
    # The OS boundary the command runs inside.
    out.append(f'<rect x="40" y="120" width="250" height="200" rx="12" fill="{PURPLE}" '
               f'opacity=".10" stroke="{BLUE}" stroke-opacity=".55" stroke-dasharray="7 5"/>')
    out.append(f'<text x="56" y="146" fill="{BLUE}" font-size="13" opacity=".85">sandbox</text>')
    out.append(f'<rect x="86" y="196" width="150" height="48" rx="8" fill="{PURPLE}" '
               f'opacity=".30" stroke="{BLUE}" stroke-opacity=".8"/>')
    out.append(f'<text x="161" y="226" fill="#e9e3fb" font-size="17" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">bash</text>')
    # Three reaches: the allowed one crosses, the other two stop at the wall.
    reaches = [
        ("./src", GREEN, 160, True),
        ("~/.ssh", RED, 220, False),
        ("api.evil.sh", AMBER, 280, False),
    ]
    for label, col, y, ok in reaches:
        end = 470 if ok else 290
        out.append(f'<path d="M236 {y if y != 220 else 220} L{end} {y}" stroke="{col}" '
                   f'stroke-opacity=".75" stroke-width="1.8"/>')
        if ok:
            out.append(f'<path d="M-6 -5 L6 0 L-6 5 Z" fill="{col}" opacity=".85" '
                       f'transform="translate({end + 4} {y})"/>')
            out.append(f'<text x="{end + 20}" y="{y + 5}" fill="{DIM}" font-size="15">{label}</text>')
        else:
            # Blocked: a short bar on the wall, and the target greyed out beyond it.
            out.append(f'<path d="M290 {y - 11} L290 {y + 11}" stroke="{col}" stroke-width="3.5"/>')
            out.append(f'<text x="{end + 26}" y="{y + 5}" fill="{FAINT}" font-size="15">{label}</text>')
    out.append(f'<text x="40" y="360" fill="{DIM}" font-size="14">rules decide whether</text>')
    out.append(f'<text x="40" y="382" fill="{DIM}" font-size="14">the wall decides what</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_stack():
    """Five settings scopes stacked, with the value from the top one winning."""
    out = []
    rows = [
        ("managed", PINK, 90, True),
        ("--settings", AMBER, 150, False),
        ("settings.local.json", BLUE, 210, False),
        ("settings.json", BLUE, 270, False),
        ("~/.claude/settings.json", PURPLE, 330, False),
    ]
    for label, col, y, wins in rows:
        # Only the winning row is drawn solid; the rest are shadowed by it.
        op = ".26" if wins else ".10"
        out.append(f'<rect x="70" y="{y-21}" width="330" height="42" rx="8" fill="{col}" '
                   f'opacity="{op}" stroke="{col}" stroke-opacity="{".85" if wins else ".45"}"/>')
        out.append(f'<text x="90" y="{y+6}" fill="{"#f3eefe" if wins else "#8b93a7"}" '
                   f'font-size="15" font-family="ui-monospace,monospace">{label}</text>')
    out.append(f'<path d="M430 90 L430 330" stroke="{FAINT}" stroke-width="1.6" stroke-dasharray="4 5"/>')
    out.append(f'<path d="M400 90 L466 90" stroke="{PINK}" stroke-width="1.8"/>')
    out.append(f'<path d="M-6 -5 L6 0 L-6 5 Z" fill="{PINK}" opacity=".9" transform="translate(470 90)"/>')
    out.append(f'<text x="486" y="95" fill="{DIM}" font-size="15">wins</text>')
    for _, _, y, _ in rows[1:]:
        out.append(f'<path d="M400 {y} L430 {y}" stroke="{FAINT}" stroke-width="1.4"/>')
        out.append(f'<text x="446" y="{y+5}" fill="{FAINT}" font-size="14">shadowed</text>')
    out.append(f'<text x="70" y="376" fill="{DIM}" font-size="14">highest level that sets the key</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_layers():
    """Instruction files stacking into one context, most specific last."""
    out = []
    files = [
        ("/etc/claude-code/CLAUDE.md", PINK, 74),
        ("~/.claude/CLAUDE.md", AMBER, 128),
        ("repo/CLAUDE.md", BLUE, 182),
        ("services/api/CLAUDE.md", BLUE, 236),
        ("CLAUDE.local.md", PURPLE, 290),
    ]
    for i, (label, col, y) in enumerate(files):
        # Each file is offset a little further right: deeper scope, later read.
        x = 60 + i * 18
        out.append(f'<rect x="{x}" y="{y-19}" width="300" height="38" rx="7" fill="{col}" '
                   f'opacity=".13" stroke="{col}" stroke-opacity=".6"/>')
        out.append(f'<text x="{x+16}" y="{y+5}" fill="#c9c2e4" font-size="13.5" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
    out.append(f'<path d="M470 74 L470 330" stroke="{FAINT}" stroke-width="1.6" stroke-dasharray="4 5"/>')
    for _, col, y in files:
        out.append(f'<path d="M400 {y} L468 {y}" stroke="{col}" stroke-opacity=".5" stroke-width="1.4"/>')
    out.append(f'<circle cx="470" cy="330" r="7" fill="{GREEN}"/>')
    out.append(f'<text x="60" y="352" fill="{DIM}" font-size="14">concatenated, not overridden</text>')
    out.append(f'<text x="60" y="374" fill="{DIM}" font-size="14">closest to you is read last</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_scoped():
    """Rules waiting off to one side; opening a file pulls two of them in."""
    out = []
    # The context column: what is loaded right now.
    out.append(f'<rect x="52" y="70" width="210" height="270" rx="10" fill="{PURPLE}" '
               f'opacity=".10" stroke="{BLUE}" stroke-opacity=".5"/>')
    out.append(f'<text x="68" y="96" fill="{BLUE}" font-size="13" opacity=".9">in context</text>')
    loaded = [("CLAUDE.md", 130), ("code-style.md", 176), ("api.md", 222)]
    for label, y in loaded:
        col = GREEN if label == "api.md" else PURPLE
        out.append(f'<rect x="70" y="{y-15}" width="174" height="32" rx="6" fill="{col}" '
                   f'opacity=".26" stroke="{col}" stroke-opacity=".8"/>')
        out.append(f'<text x="84" y="{y+6}" fill="#e6e0f8" font-size="13" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
    # The rules that stay out until a matching file is read.
    waiting = [("components.md", 130), ("testing.md", 176), ("docs.md", 222)]
    for label, y in waiting:
        out.append(f'<rect x="400" y="{y-15}" width="180" height="32" rx="6" fill="{FAINT}" '
                   f'opacity=".22" stroke="{FAINT}" stroke-opacity=".7" stroke-dasharray="4 4"/>')
        out.append(f'<text x="414" y="{y+6}" fill="#6b7280" font-size="13" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
    out.append(f'<path d="M398 222 L266 222" stroke="{GREEN}" stroke-opacity=".8" stroke-width="1.8"/>')
    out.append(f'<path d="M6 -5 L-6 0 L6 5 Z" fill="{GREEN}" opacity=".9" transform="translate(262 222)"/>')
    out.append(f'<text x="290" y="252" fill="{DIM}" font-size="13" text-anchor="middle">src/api/users.ts</text>')
    out.append(f'<text x="52" y="378" fill={chr(34)}{DIM}{chr(34)} font-size="14">a rule with no paths: field is CLAUDE.md with extra steps</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_fill():
    """A context window filling, with the auto-compact trigger marked."""
    out = []
    segs = [("startup", PURPLE, 96), ("files", BLUE, 150), ("turns", GREEN, 120), ("skills", AMBER, 54)]
    x = 60
    for label, col, w in segs:
        out.append(f'<rect x="{x}" y="150" width="{w}" height="46" fill="{col}" opacity=".30" '
                   f'stroke="{col}" stroke-opacity=".7"/>')
        out.append(f'<text x="{x + w / 2}" y="{218}" fill="{DIM}" font-size="12" '
                   f'text-anchor="middle">{label}</text>')
        x += w
    # The rest of the window, and the point where the automatic pass fires.
    out.append(f'<rect x="{x}" y="150" width="{560 - x}" height="46" fill="none" '
               f'stroke="{FAINT}" stroke-opacity=".7" stroke-dasharray="4 4"/>')
    out.append(f'<rect x="60" y="150" width="500" height="46" fill="none" stroke="{FAINT}" stroke-opacity=".8"/>')
    out.append(f'<path d="M460 132 L460 214" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
    out.append(f'<text x="460" y="124" fill="{RED}" font-size="13" text-anchor="middle">auto-compact</text>')
    out.append(f'<text x="60" y="120" fill="{DIM}" font-size="13">200K</text>')
    out.append(f'<text x="60" y="272" fill="{DIM}" font-size="14">compaction re-reads five files</text>')
    out.append(f'<text x="60" y="294" fill="{DIM}" font-size="14">and summarises the rest</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_rewind():
    """A timeline rewound: tool edits come back, bash and subagent edits don't."""
    out = []
    out.append(f'<path d="M70 200 L560 200" stroke="{FAINT}" stroke-width="2"/>')
    marks = [
        ("prompt", 110, PURPLE, True), ("edit", 176, BLUE, True),
        ("bash", 258, AMBER, False), ("sub", 340, PINK, False), ("edit", 424, BLUE, True),
    ]
    for kind, x, col, tracked in marks:
        out.append(f'<circle cx="{x}" cy="200" r="8" fill="{col}" opacity="{".85" if tracked else ".4"}"/>')
        if not tracked:
            # Untracked edits stay on disk, so they sit below the line.
            out.append(f'<path d="M{x} 208 L{x} 248" stroke="{col}" stroke-opacity=".55" stroke-dasharray="3 3"/>')
            out.append(f'<text x="{x}" y="266" fill="{col}" font-size="12" text-anchor="middle" opacity=".8">stays</text>')
        else:
            out.append(f'<path d="M{x} 192 L{x} 156" stroke="{col}" stroke-opacity=".55" stroke-dasharray="3 3"/>')
            out.append(f'<text x="{x}" y="146" fill="{col}" font-size="12" text-anchor="middle" opacity=".8">reverts</text>')
    # The rewind target, and the arc back to it.
    out.append(f'<path d="M176 200 L176 200" stroke="{GREEN}"/>')
    out.append(f'<path d="M424 96 Q300 62 180 96" fill="none" stroke="{GREEN}" stroke-opacity=".8" stroke-width="1.8"/>')
    out.append(f'<path d="M6 -5 L-6 0 L6 5 Z" fill="{GREEN}" opacity=".9" transform="translate(178 96)"/>')
    out.append(f'<text x="300" y="52" fill="{GREEN}" font-size="14" text-anchor="middle" opacity=".85">/rewind</text>')
    out.append(f'<text x="70" y="330" fill="{DIM}" font-size="14">bash and subagent edits survive the rewind</text>')
    out.append(f'<text x="70" y="352" fill="{DIM}" font-size="14">git is still the backstop</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_prompt():
    """The system prompt, with the built-in engineering block swapped out."""
    out = []
    blocks = [
        ("core instructions", PURPLE, 96, True),
        ("tool definitions", PURPLE, 152, True),
        ("software engineering", FAINT, 208, False),
        ("your output style", GREEN, 264, True),
    ]
    for label, col, y, on in blocks:
        dash = '' if on else ' stroke-dasharray="5 4"'
        out.append(f'<rect x="70" y="{y-21}" width="330" height="42" rx="8" fill="{col}" '
                   f'opacity="{".22" if on else ".07"}" stroke="{col}" stroke-opacity="{".8" if on else ".5"}"{dash}/>')
        out.append(f'<text x="90" y="{y+6}" fill="{"#e6e0f8" if on else "#5b6475"}" font-size="15" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
    # The engineering block is the one keep-coding-instructions decides on.
    out.append(f'<path d="M400 208 L470 208" stroke="{RED}" stroke-opacity=".7" stroke-width="1.6"/>')
    out.append(f'<text x="480" y="204" fill="{RED}" font-size="13" opacity=".9">dropped unless</text>')
    out.append(f'<text x="480" y="222" fill="{RED}" font-size="13" opacity=".9">you keep it</text>')
    out.append(f'<text x="70" y="60" fill="{DIM}" font-size="14">system prompt</text>')
    out.append(f'<text x="70" y="330" fill={chr(34)}{DIM}{chr(34)} font-size="14">every other mechanism adds context around this</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_disclosure():
    """Three tiers: names always loaded, content on invocation, files on demand."""
    out = []
    tiers = [
        ("names + descriptions", PURPLE, 100, "always", 1.0),
        ("SKILL.md content", GREEN, 190, "on invocation", 0.55),
        ("reference.md, scripts/", BLUE, 280, "on demand", 0.25),
    ]
    for label, col, y, when, fill in tiers:
        out.append(f'<rect x="70" y="{y-24}" width="300" height="48" rx="8" fill="{col}" '
                   f'opacity="{0.06 + 0.2 * fill:.2f}" stroke="{col}" stroke-opacity="{0.35 + 0.5 * fill:.2f}"'
                   f'{"" if fill > 0.5 else " stroke-dasharray=\"5 4\""}/>')
        out.append(f'<text x="90" y="{y+6}" fill="#ded7f2" font-size="15" '
                   f'font-family="ui-monospace,monospace" opacity="{0.45 + 0.55 * fill:.2f}">{label}</text>')
        out.append(f'<text x="392" y="{y+5}" fill="{col}" font-size="13" opacity=".8">{when}</text>')
    # The context window only ever holds the top tier by default.
    out.append(f'<path d="M56 76 L56 124" stroke={chr(34)}{PURPLE}{chr(34)} stroke-width="3"/>')
    out.append(f'<text x="70" y="60" fill="{DIM}" font-size="13">in context</text>')
    out.append(f'<text x="70" y="350" fill="{DIM}" font-size="14">a hundred skills cost about 1% of the window</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_lifecycle():
    """A turn's spine with hook events hanging off it; the blockers have a bar."""
    out = []
    out.append(f'<path d="M100 70 L100 350" stroke="{FAINT}" stroke-width="2"/>')
    evs = [
        ("SessionStart", 90, False),
        ("UserPromptSubmit", 138, True),
        ("PreToolUse", 186, True),
        ("PostToolUse", 234, False),
        ("Stop", 282, True),
        ("SessionEnd", 330, False),
    ]
    for label, y, blocks in evs:
        col = RED if blocks else PURPLE
        out.append(f'<circle cx="100" cy="{y}" r="6" fill="{col}" opacity="{".9" if blocks else ".5"}"/>')
        out.append(f'<path d="M106 {y} L150 {y}" stroke="{col}" stroke-opacity=".5" stroke-width="1.4"/>')
        out.append(f'<text x="160" y="{y+5}" fill="{"#e8dcdc" if blocks else "#8b93a7"}" font-size="14" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
        if blocks:
            # A blocking event can stop the turn dead.
            out.append(f'<path d="M400 {y-11} L400 {y+11}" stroke="{RED}" stroke-width="3.5"/>')
            out.append(f'<text x="416" y="{y+5}" fill="{RED}" font-size="13" opacity=".85">blocks</text>')
    out.append(f'<text x="70" y="386" fill="{DIM}" font-size="14">a deny here holds even under bypassPermissions</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_bundle():
    """Loose components on the left, gathered into one installable unit."""
    out = []
    parts = [("skills/", GREEN, 92), ("agents/", BLUE, 140), ("hooks/", AMBER, 188),
             (".mcp.json", PINK, 236), ("bin/", PURPLE, 284)]
    for label, col, y in parts:
        out.append(f'<rect x="46" y="{y-16}" width="130" height="33" rx="6" fill="{col}" opacity=".16" '
                   f'stroke="{col}" stroke-opacity=".55" stroke-dasharray="4 4"/>')
        out.append(f'<text x="60" y="{y+5}" fill="#8b93a7" font-size="12.5" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
        out.append(f'<path d="M180 {y} Q250 {y} 268 188" fill="none" stroke="{col}" '
                   f'stroke-opacity=".4" stroke-width="1.3"/>')
    # The bundle everything resolves into.
    out.append(f'<rect x="272" y="120" width="200" height="136" rx="12" fill="{PURPLE}" opacity=".2" '
               f'stroke="{BLUE}" stroke-opacity=".8"/>')
    out.append(f'<text x="372" y="176" fill="#e9e3fb" font-size="17" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">release-tools</text>')
    out.append(f'<text x="372" y="202" fill="{DIM}" font-size="14" text-anchor="middle">v1.2.0</text>')
    out.append(f'<path d="M472 188 L534 188" stroke="{GREEN}" stroke-opacity=".8" stroke-width="1.8"/>')
    out.append(f'<path d="M-6 -5 L6 0 L-6 5 Z" fill="{GREEN}" opacity=".9" transform="translate(538 188)"/>')
    out.append(f'<text x="504" y="170" fill="{GREEN}" font-size="13" text-anchor="middle" opacity=".85">install</text>')
    out.append(f'<text x="46" y="342" fill="{DIM}" font-size="14">no new capability — one installable unit</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_defer():
    """Many servers, only their names in context until a tool is called."""
    out = []
    # The servers, sitting unconnected.
    for i, label in enumerate(["github", "postgres", "sentry", "notion", "figma"]):
        y = 84 + i * 54
        out.append(f'<rect x="392" y="{y-17}" width="176" height="35" rx="7" fill="{FAINT}" opacity=".18" '
                   f'stroke="{FAINT}" stroke-opacity=".6" stroke-dasharray="4 4"/>')
        out.append(f'<text x="408" y="{y+5}" fill="#6b7280" font-size="13" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
        out.append(f'<path d="M388 {y} L300 {y}" stroke="{FAINT}" stroke-opacity=".35" stroke-width="1.2" '
                   f'stroke-dasharray="3 4"/>')
    # What is actually in context: the names.
    out.append(f'<rect x="60" y="120" width="180" height="150" rx="10" fill="{PURPLE}" opacity=".16" '
               f'stroke="{BLUE}" stroke-opacity=".7"/>')
    out.append(f'<text x="150" y="180" fill="#e9e3fb" font-size="15" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">tool names</text>')
    out.append(f'<text x="150" y="206" fill="{GREEN}" font-size="15" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">~1K</text>')
    out.append(f'<text x="150" y="236" fill="{DIM}" font-size="13" text-anchor="middle">schemas deferred</text>')
    out.append(f'<text x="60" y="100" fill="{DIM}" font-size="13">in context</text>')
    out.append(f'<text x="60" y="336" fill="{DIM}" font-size="14">servers stay unconnected until a tool is called</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_browser():
    """A browser window Claude drives, wired back to the editor."""
    out = []
    # The browser, sharing your logged-in session.
    out.append(f'<rect x="240" y="86" width="330" height="212" rx="10" fill="{PURPLE}" opacity=".13" '
               f'stroke="{BLUE}" stroke-opacity=".7"/>')
    out.append(f'<path d="M240 118 L570 118" stroke="{BLUE}" stroke-opacity=".5"/>')
    for i, cx in enumerate([258, 274, 290]):
        out.append(f'<circle cx="{cx}" cy="102" r="4" fill="{FAINT}" opacity=".8"/>')
    out.append(f'<rect x="306" y="94" width="150" height="16" rx="8" fill="{FAINT}" opacity=".35"/>')
    out.append(f'<text x="264" y="164" fill="#c9c2e4" font-size="14" '
               f'font-family="ui-monospace,monospace">localhost:3000</text>')
    out.append(f'<rect x="264" y="182" width="200" height="26" rx="5" fill="{RED}" opacity=".18" '
               f'stroke="{RED}" stroke-opacity=".55"/>')
    out.append(f'<text x="276" y="200" fill="{RED}" font-size="12" opacity=".9">console: TypeError</text>')
    out.append(f'<text x="264" y="240" fill="{GREEN}" font-size="13" opacity=".8">signed in already</text>')
    # Back to the code.
    out.append(f'<path d="M236 192 L150 192" stroke="{GREEN}" stroke-opacity=".7" stroke-width="1.8"/>')
    out.append(f'<path d="M6 -5 L-6 0 L6 5 Z" fill="{GREEN}" opacity=".9" transform="translate(146 192)"/>')
    out.append(f'<rect x="52" y="168" width="90" height="48" rx="7" fill="{GREEN}" opacity=".2" '
               f'stroke="{GREEN}" stroke-opacity=".6"/>')
    out.append(f'<text x="97" y="197" fill="#dff3e4" font-size="13" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">fix</text>')
    out.append(f'<text x="52" y="340" fill="{DIM}" font-size="14">it shares the browser session you already have</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_pipeline():
    """Three levels: your session, a workflow, a pipeline step."""
    out = []
    rows = [
        ("your session", "claude", PURPLE, 100),
        ("a workflow", "@claude", BLUE, 190),
        ("any pipeline", "claude -p", GREEN, 280),
    ]
    for label, cmd, col, y in rows:
        out.append(f'<text x="60" y="{y-26}" fill="{DIM}" font-size="13">{label}</text>')
        out.append(f'<rect x="60" y="{y-14}" width="150" height="38" rx="7" fill="{col}" opacity=".22" '
                   f'stroke="{col}" stroke-opacity=".75"/>')
        out.append(f'<text x="78" y="{y+11}" fill="#e6e0f8" font-size="14" '
                   f'font-family="ui-monospace,monospace">{cmd}</text>')
        out.append(f'<path d="M214 {y+5} L360 {y+5}" stroke="{col}" stroke-opacity=".5" stroke-width="1.5"/>')
        out.append(f'<path d="M-6 -5 L6 0 L-6 5 Z" fill="{col}" opacity=".8" transform="translate(364 {y+5})"/>')
    # All three land on the same place.
    out.append(f'<rect x="382" y="120" width="176" height="150" rx="10" fill="{PINK}" opacity=".13" '
               f'stroke="{PINK}" stroke-opacity=".6"/>')
    out.append(f'<text x="470" y="188" fill="#f3d9e6" font-size="15" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">a pull request</text>')
    out.append(f'<text x="470" y="214" fill="{DIM}" font-size="13" text-anchor="middle">reviewed by a person</text>')
    out.append(f'<text x="60" y="352" fill="{DIM}" font-size="14">level 1 needs no setup at all</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_delegate():
    """Noisy work sent out to its own window; only a summary comes back."""
    out = []
    # Your window, holding only the summary.
    out.append(f'<rect x="48" y="110" width="196" height="180" rx="10" fill="{PURPLE}" opacity=".14" '
               f'stroke="{BLUE}" stroke-opacity=".75"/>')
    out.append(f'<text x="146" y="98" fill="{DIM}" font-size="13" text-anchor="middle">your window</text>')
    out.append(f'<rect x="70" y="180" width="152" height="34" rx="6" fill="{GREEN}" opacity=".3" '
               f'stroke="{GREEN}" stroke-opacity=".8"/>')
    out.append(f'<text x="146" y="202" fill="#dff3e4" font-size="14" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">summary</text>')
    # The subagent's own window, holding the noise.
    out.append(f'<rect x="386" y="76" width="206" height="248" rx="10" fill="{FAINT}" opacity=".16" '
               f'stroke="{FAINT}" stroke-opacity=".7" stroke-dasharray="5 4"/>')
    out.append(f'<text x="489" y="64" fill="{DIM}" font-size="13" text-anchor="middle">its own window</text>')
    for i, label in enumerate(["test output", "11 files read", "API docs", "grep results"]):
        y = 118 + i * 52
        out.append(f'<rect x="406" y="{y-15}" width="166" height="32" rx="5" fill="{AMBER}" opacity=".16" '
                   f'stroke="{AMBER}" stroke-opacity=".45"/>')
        out.append(f'<text x="420" y="{y+5}" fill="#8b8270" font-size="12.5" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
    out.append(f'<path d="M248 168 L382 130" stroke="{DIM}" stroke-opacity=".5" stroke-width="1.4" '
               f'stroke-dasharray="4 4"/>')
    out.append(f'<text x="315" y="140" fill="{DIM}" font-size="12" text-anchor="middle">task</text>')
    out.append(f'<path d="M382 250 L252 206" stroke="{GREEN}" stroke-opacity=".8" stroke-width="1.8"/>')
    out.append(f'<path d="M6 -5 L-6 0 L6 5 Z" fill="{GREEN}" opacity=".9" transform="translate(248 204)"/>')
    out.append(f'<text x="48" y="352" fill="{DIM}" font-size="14">verbose work in, a summary back</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_team():
    """A lead over teammates who also talk to each other."""
    out = []
    out.append(f'<rect x="248" y="66" width="140" height="42" rx="8" fill="{PURPLE}" opacity=".28" '
               f'stroke="{BLUE}" stroke-opacity=".85"/>')
    out.append(f'<text x="318" y="93" fill="#eae4fb" font-size="15" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">lead</text>')
    mates = [(96, "security"), (248, "perf"), (400, "tests")]
    for x, label in mates:
        out.append(f'<path d="M318 112 L{x + 62} 196" stroke="{FAINT}" stroke-opacity=".55" stroke-width="1.4"/>')
        out.append(f'<rect x="{x}" y="200" width="124" height="40" rx="7" fill="{GREEN}" opacity=".2" '
                   f'stroke="{GREEN}" stroke-opacity=".65"/>')
        out.append(f'<text x="{x + 62}" y="225" fill="#d9efdf" font-size="13.5" text-anchor="middle" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
    # The lateral messaging is what distinguishes a team from subagents.
    for x1, x2 in [(224, 248), (372, 400)]:
        out.append(f'<path d="M{x1} 220 L{x2} 220" stroke="{PINK}" stroke-opacity=".85" stroke-width="1.8"/>')
        out.append(f'<path d="M-5 -4 L5 0 L-5 4 Z" fill="{PINK}" opacity=".9" transform="translate({x2} 220)"/>')
        out.append(f'<path d="M5 -4 L-5 0 L5 4 Z" fill="{PINK}" opacity=".9" transform="translate({x1} 220)"/>')
    out.append(f'<text x="318" y="272" fill="{PINK}" font-size="13" text-anchor="middle" opacity=".9">they message each other</text>')
    out.append(f'<text x="96" y="330" fill="{DIM}" font-size="14">no worktrees — partition the files yourself</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_clock():
    """A loop with a seven-day fuse, and the cloud that outlives it."""
    out = []
    # The in-session loop.
    out.append(f'<circle cx="180" cy="196" r="66" fill="none" stroke="{BLUE}" stroke-opacity=".65" '
               f'stroke-width="2" stroke-dasharray="9 6"/>')
    out.append(f'<path d="M-7 -6 L7 0 L-7 6 Z" fill="{BLUE}" opacity=".9" transform="translate(180 130) rotate(28)"/>')
    out.append(f'<text x="180" y="192" fill="#dfe6f6" font-size="16" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">/loop</text>')
    out.append(f'<text x="180" y="214" fill="{DIM}" font-size="12.5" text-anchor="middle">while the session is open</text>')
    out.append(f'<text x="180" y="298" fill="{RED}" font-size="13" text-anchor="middle" opacity=".9">expires after 7 days</text>')
    # The cloud routine that does not need you there.
    out.append(f'<rect x="360" y="150" width="200" height="92" rx="12" fill="{PURPLE}" opacity=".2" '
               f'stroke="{GREEN}" stroke-opacity=".7"/>')
    out.append(f'<text x="460" y="190" fill="#e6e0f8" font-size="15" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">routine</text>')
    out.append(f'<text x="460" y="212" fill="{GREEN}" font-size="12.5" text-anchor="middle">machine off, still runs</text>')
    out.append(f'<path d="M252 196 L354 196" stroke="{FAINT}" stroke-width="1.4" stroke-dasharray="4 5"/>')
    out.append(f'<text x="70" y="352" fill="{DIM}" font-size="14">machine on, session open, how often — pick two</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_surfaces():
    """One engine, several front doors — split by where the code runs."""
    out = []
    out.append(f'<circle cx="320" cy="196" r="52" fill="{PURPLE}" opacity=".26" stroke="{BLUE}" stroke-opacity=".85"/>')
    out.append(f'<text x="320" y="192" fill="#eae4fb" font-size="14" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">one</text>')
    out.append(f'<text x="320" y="210" fill="#eae4fb" font-size="14" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">engine</text>')
    left = [("CLI", 96), ("Desktop", 152), ("VS Code", 208), ("JetBrains", 264)]
    right = [("web", 124), ("Slack", 186), ("routines", 248)]
    for label, y in left:
        out.append(f'<rect x="52" y="{y-15}" width="128" height="32" rx="6" fill="{GREEN}" opacity=".2" '
                   f'stroke="{GREEN}" stroke-opacity=".6"/>')
        out.append(f'<text x="116" y="{y+5}" fill="#d9efdf" font-size="13" text-anchor="middle" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
        out.append(f'<path d="M184 {y} L266 196" stroke="{GREEN}" stroke-opacity=".3" stroke-width="1.2"/>')
    for label, y in right:
        out.append(f'<rect x="460" y="{y-15}" width="128" height="32" rx="6" fill="{PINK}" opacity=".2" '
                   f'stroke="{PINK}" stroke-opacity=".6"/>')
        out.append(f'<text x="524" y="{y+5}" fill="#f3d9e6" font-size="13" text-anchor="middle" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
        out.append(f'<path d="M456 {y} L374 196" stroke="{PINK}" stroke-opacity=".3" stroke-width="1.2"/>')
    out.append(f'<text x="116" y="316" fill="{GREEN}" font-size="13" text-anchor="middle" opacity=".85">your machine</text>')
    out.append(f'<text x="524" y="316" fill="{PINK}" font-size="13" text-anchor="middle" opacity=".85">the cloud</text>')
    out.append(f'<text x="320" y="366" fill="{DIM}" font-size="14" text-anchor="middle">the question is where the code runs</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_meter():
    """Every turn re-sends the whole conversation. The staircase is the bill."""
    out = []
    heights = [26, 44, 60, 79, 96, 116, 134, 156, 176, 200]
    for i, h in enumerate(heights):
        x = 60 + i * 52
        colour = GREEN if i < 4 else (BLUE if i < 7 else PINK)
        out.append(f'<rect x="{x}" y="{312-h}" width="34" height="{h}" rx="4" fill="{colour}" '
                   f'opacity=".{22 + i*4}" stroke="{colour}" stroke-opacity=".65"/>')
    out.append(f'<path d="M60 312 L580 312" stroke="{DIM}" stroke-opacity=".5" stroke-width="1.2"/>')
    out.append(f'<text x="77" y="332" fill="{DIM}" font-size="12" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">turn 1</text>')
    out.append(f'<text x="545" y="332" fill="{DIM}" font-size="12" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">turn 10</text>')
    out.append(f'<rect x="330" y="56" width="250" height="46" rx="8" fill="{PINK}" opacity=".18" '
               f'stroke="{PINK}" stroke-opacity=".6"/>')
    out.append(f'<text x="455" y="85" fill="#f3d9e6" font-size="15" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">one question, all of it</text>')
    out.append(f'<path d="M455 104 L455 128" stroke="{PINK}" stroke-opacity=".5" stroke-width="1.4"/>')
    out.append(f'<text x="60" y="372" fill="{DIM}" font-size="14">the context is paid again every turn</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


def art_triage():
    """Four failure groups, four pages. The first job is picking the branch."""
    out = []
    out.append(f'<rect x="238" y="52" width="164" height="42" rx="8" fill="{PURPLE}" opacity=".26" '
               f'stroke="{BLUE}" stroke-opacity=".85"/>')
    out.append(f'<text x="320" y="79" fill="#eae4fb" font-size="14" text-anchor="middle" '
               f'font-family="ui-monospace,monospace">how far did it get?</text>')
    rows = [("never started", "install", 150, GREEN, "#d9efdf"),
            ("config ignored", "debug-your-config", 208, BLUE, "#dbe4fb"),
            ("slow or stuck", "troubleshooting", 266, PINK, "#f3d9e6"),
            ("a message", "errors", 324, PURPLE, "#eae4fb")]
    for label, page, y, colour, ink in rows:
        out.append(f'<path d="M320 94 L320 {y} L196 {y}" stroke="{colour}" stroke-opacity=".4" '
                   f'stroke-width="1.2" fill="none"/>')
        out.append(f'<rect x="52" y="{y-15}" width="146" height="31" rx="6" fill="{colour}" opacity=".2" '
                   f'stroke="{colour}" stroke-opacity=".6"/>')
        out.append(f'<text x="125" y="{y+5}" fill="{ink}" font-size="12.5" text-anchor="middle" '
                   f'font-family="ui-monospace,monospace">{label}</text>')
        out.append(f'<path d="M320 {y} L390 {y}" stroke="{colour}" stroke-opacity=".4" stroke-width="1.2"/>')
        out.append(f'<text x="398" y="{y+5}" fill="{DIM}" font-size="12.5" '
                   f'font-family="ui-monospace,monospace">{page}</text>')
    out.append(f'<text x="52" y="378" fill="{DIM}" font-size="14">route it before you debug it</text>')
    return f'<svg width="640" height="420" viewBox="0 0 640 420">{"".join(out)}</svg>'


COVERS = [
    # (slug, badge, title with <br>, title font size, tagline, mono caption, motif)
    ("cc-01-what-claude-code-is", "PART 1 · CH 1", "What Claude Code<br>Actually Is", 54,
     "An LLM cannot read your files. So how does Claude Code read your files?",
     "the model never touches your <i>disk</i>", art_loop),
    ("cc-02-three-ways-to-talk", "PART 1 · CH 2", "Three Ways to Talk<br>to Claude Code", 50,
     "CLI flags, slash commands, and sigils. Three channels, three rules.",
     "two of the three never reach the <i>model</i>", art_channels),
    ("cc-03-permission-modes", "PART 1 · CH 3", "Permission<br>Modes", 62,
     "Six modes, a classifier, and the paths no mode will approve.",
     "3 in a row and auto mode <i>stops trusting itself</i>", art_gates),
    ("cc-04-permissions-sandboxing", "PART 1 · CH 4", "Permissions &amp;<br>Sandboxing", 54,
     "Rules decide whether a call happens. The sandbox decides what it can touch.",
     "a deny rule cannot carry <i>exceptions</i>", art_boundary),
    ("cc-05-settings", "PART 2 · CH 5", "Settings:<br>the Control Panel", 54,
     "Four files, one precedence stack, and the keys that break its rules.",
     "your team's file <i>outranks</i> your own", art_stack),
    ("cc-06-claude-md", "PART 2 · CH 6", "CLAUDE.md", 68,
     "The file that stops you re-explaining your project every session.",
     "it is <i>context</i>, not configuration", art_layers),
    ("cc-07-rules-auto-memory", "PART 2 · CH 7", "Rules &amp;<br>Auto Memory", 54,
     "Instructions that cost nothing until they are relevant, and the notes Claude keeps.",
     "only the first 200 lines <i>load</i>", art_scoped),
    ("cc-08-context-window", "PART 2 · CH 8", "The Context<br>Window", 60,
     "The budget every other chapter spends, and what compaction keeps.",
     "each model has its own <i>cache</i>", art_fill),
    ("cc-09-sessions-checkpoints", "PART 2 · CH 9", "Sessions, Checkpoints<br>&amp; Rewind", 46,
     "Resume, branch, rewind — and the four changes rewind cannot undo.",
     "checkpoints are not <i>version control</i>", art_rewind),
    ("cc-10-output-styles", "PART 3 · CH 10", "Output<br>Styles", 62,
     "The one extension point that edits the system prompt itself.",
     "keep-coding-instructions defaults to <i>false</i>", art_prompt),
    ("cc-11-skills", "PART 3 · CH 11", "Skills", 72,
     "Instructions that stay out of context until they are needed.",
     "the description is the <i>trigger</i>", art_disclosure),
    ("cc-12-hooks", "PART 3 · CH 12", "Hooks", 72,
     "The layer that turns an instruction into a guarantee.",
     "hooks tighten, never <i>loosen</i>", art_lifecycle),
    ("cc-13-plugins", "PART 3 · CH 13", "Plugins &amp;<br>Marketplaces", 54,
     "One installable unit for skills, hooks, agents and MCP servers.",
     "only plugin.json goes in <i>.claude-plugin/</i>", art_bundle),
    ("cc-14-mcp-fundamentals", "PART 4 · CH 14", "MCP<br>Fundamentals", 62,
     "Typed tools for systems Claude Code has no tool for.",
     "ten servers cost <i>names</i>, not schemas", art_defer),
    ("cc-15-mcp-in-practice", "PART 4 · CH 15", "MCP in<br>Practice", 62,
     "When a server earns its place, and when Bash already did the job.",
     "Chrome inherits your <i>login state</i>", art_browser),
    ("cc-16-github-gitlab-ci", "PART 4 · CH 16", "GitHub, GitLab<br>&amp; CI", 52,
     "Three levels, from Claude running git to Claude as a CI step.",
     "the <i>prompt</i> input is the mode switch", art_pipeline),
    ("cc-17-subagents", "PART 5 · CH 17", "Sub-Agents", 64,
     "Delegation as context management, not as extra horsepower.",
     "a blank slate with its own <i>window</i>", art_delegate),
    ("cc-18-agent-teams", "PART 5 · CH 18", "Agent Teams &amp;<br>Parallel Work", 50,
     "Four ways to run sessions at once, and the questions that pick between them.",
     "teams do not <i>isolate</i> teammates", art_team),
    ("cc-19-automation-scheduling", "PART 5 · CH 19", "Automation &amp;<br>Scheduling", 52,
     "Four schedulers, and the constraints that pick between them.",
     "a forgotten loop <i>expires</i>", art_clock),
    ("cc-20-everywhere", "PART 5 · CH 20", "Claude Code<br>Everywhere", 56,
     "Same engine, different front doors — and one question that sorts them.",
     "Remote Control runs on <i>your</i> machine", art_surfaces),
    ("hello-transformers", "PART 1 · CH 1", "How a Transformer<br>Actually Predicts", 54,
     "One token at a time, and everything else follows from that.",
     "the model outputs a <i>distribution</i>, not a word", art_tokens),
    ("cc-21-cost-monitoring-security", "PART 6 · CH 21", "Cost, Monitoring<br>&amp; Security", 50,
     "What it costs, why an idle session keeps spending, and the model underneath the prompts.",
     "no system is <i>completely immune</i>", art_meter),
    ("cc-22-when-it-goes-wrong", "PART 6 · CH 22", "When It<br>Goes Wrong", 60,
     "Four groups of failure, and the commands that show what actually loaded.",
     "look at what loaded, don't <i>reason about it</i>", art_triage),
]

def build(only=None):
    for name, badge, title, fs, tag, cap, art in COVERS:
        if only and name not in only:
            continue
        html = (SHELL.replace("__BADGE__", badge).replace("__TITLE__", title)
                     .replace("__FS__", str(fs)).replace("__TAG__", tag)
                     .replace("__CAP__", cap).replace("__ART__", art()))
        hp = os.path.join(SP, f"cv_{name}.html")
        pp = os.path.join(SP, f"cv_{name}.png")
        open(hp, "w").write(html)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                        "--window-size=1600,640", "--virtual-time-budget=8000",
                        f"--screenshot={pp}", "file://" + hp],
                       capture_output=True)
        subprocess.run(["cwebp", "-q", "90", pp, "-o", os.path.join(OUT, name + ".webp")],
                       capture_output=True)
        print("built", name)

if __name__ == "__main__":
    build(sys.argv[1:] or None)
