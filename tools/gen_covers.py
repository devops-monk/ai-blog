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


COVERS = [
    # (slug, badge, title with <br>, title font size, tagline, mono caption, motif)
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
