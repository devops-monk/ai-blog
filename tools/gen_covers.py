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
    ("hello-transformers", "PART 1 · CH 1", "How a Transformer<br>Actually Predicts", 54,
     "One token at a time, and everything else follows from that.",
     "the model outputs a <i>distribution</i>, not a word", art_tokens),
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
