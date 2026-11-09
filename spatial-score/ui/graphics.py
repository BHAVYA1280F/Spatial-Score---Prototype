"""HTML / SVG graphics for the frontend. No Streamlit imports, so it can be tested on its own."""
import html

ZONES = [
    ("Intro", "#ffb454", [18, 26, 20, 30, 22, 16], "Enclosed and soft. Low light, few ribs, quiet geometry."),
    ("Rhythm", "#4f8cff", [62] * 8, "Repeated ribs and columns. The spacing follows the beat."),
    ("Harmony", "#9b6bff", [40, 78, 55, 92, 48, 70], "Layered, overlapping glass volumes at different heights."),
    ("Climax", "#ff2d55", [22, 48, 100, 64, 96, 42, 26], "Tall, leaning walls and spires under pulsing light."),
    ("Outro", "#3fd6a0", [92, 76, 62, 48, 34, 22, 12], "Calmer. Lower, more open, slowly dimming."),
]
ZONE_COLORS = {z[0].lower(): z[1] for z in ZONES}


def bars(hs, color, cls="bp", gap=4, w=140, h=76, svg_cls=""):
    n = len(hs)
    bw = (w - gap * (n - 1)) / n
    r = "".join(
        f'<rect x="{i * (bw + gap):.1f}" y="{h - v * h / 100:.1f}" width="{bw:.1f}" height="{v * h / 100:.1f}" rx="2" '
        f'class="{cls}" style="fill:{color};animation-delay:{i * 0.12:.2f}s"/>' for i, v in enumerate(hs))
    return f'<svg viewBox="0 0 {w} {h}" class="ico {svg_cls}">{r}</svg>'


def icon(name, c):
    if name == "pitch":
        return bars([15, 30, 45, 60, 75, 92], c)
    if name == "duration":
        return '<svg viewBox="0 0 140 76" class="ico">' + "".join(
            f'<rect x="0" y="{8 + i * 22}" width="{w}" height="12" rx="3" class="hb" style="fill:{c};animation-delay:{i * .3}s"/>'
            for i, w in enumerate([140, 90, 120])) + "</svg>"
    if name == "rhythm":
        return bars([70] * 10, c, gap=6)
    if name == "tempo":
        return bars([50, 70, 50, 70, 50, 70, 50], c, cls="", svg_cls="sq")
    if name == "melody":
        return (f'<svg viewBox="0 0 140 76" class="ico"><path class="dr" d="M2 60 C 25 5, 50 5, 70 40 S 115 75, 138 14" '
                f'fill="none" stroke="{c}" stroke-width="4" stroke-linecap="round"/></svg>')
    if name == "harmony":
        return '<svg viewBox="0 0 140 76" class="ico">' + "".join(
            f'<rect x="{10 + i * 30}" y="{14 + i * 8}" width="60" height="{50 - i * 6}" rx="4" class="fl" '
            f'style="fill:{c};opacity:.45;animation-delay:{i * .5}s"/>' for i in range(3)) + "</svg>"
    if name == "texture":
        return '<svg viewBox="0 0 140 76" class="ico">' + "".join(
            f'<circle cx="{10 + x * 12}" cy="{10 + y * 14}" r="3.2" class="tw" style="fill:{c};animation-delay:{((x * 7 + y * 3) % 10) * .17:.2f}s"/>'
            for x in range(11) for y in range(5)) + "</svg>"
    if name == "timbre":
        return (f'<svg viewBox="0 0 140 76" class="ico"><rect x="6" y="12" width="36" height="52" rx="4" fill="#8a8a8a"/>'
                f'<rect x="52" y="12" width="36" height="52" rx="4" fill="#b07d45"/>'
                f'<rect x="98" y="12" width="36" height="52" rx="4" fill="#9fd8ee" opacity=".6" class="fl"/></svg>')
    if name == "form":
        xs = 0
        out = ""
        for (nm, col, _, _), wd in zip(ZONES, [20, 28, 28, 24, 20]):
            out += f'<rect x="{xs}" y="14" width="{wd - 3}" height="48" rx="3" style="fill:{col}" class="fl"/>'
            xs += wd + 2
        return f'<svg viewBox="0 0 140 76" class="ico">{out}</svg>'
    return (f'<svg viewBox="0 0 140 76" class="ico"><rect x="50" y="8" width="8" height="60" class="wl" style="fill:{c}"/>'
            f'<rect x="82" y="8" width="8" height="60" class="wr" style="fill:{c}"/></svg>')


METHOD = [
    ("Pitch", "Height", "pitch", "#ff2d55", "Higher notes lift the walls. Low notes keep the room close to the ground."),
    ("Duration", "Spatial length", "duration", "#ff7a45", "A long note becomes a long room. Short notes make short rooms."),
    ("Rhythm", "Repetition and spacing", "rhythm", "#4f8cff", "Busy music packs in more ribs, spaced tighter."),
    ("Tempo", "Compression and expansion", "tempo", "#35c4e0", "Fast songs squeeze every room. Slow songs let space breathe."),
    ("Melody", "Spatial path", "melody", "#9b6bff", "The rise and fall of the tune bends the route you walk."),
    ("Harmony", "Overlap and layers", "harmony", "#c86bff", "Sustained passages become overlapping glass layers."),
    ("Texture", "Spatial density", "texture", "#3fd6a0", "How much is happening decides how dense the structure feels."),
    ("Timbre", "Materiality", "timbre", "#ffb454", "Dull sounds turn concrete, warm ones wood, bright ones glass."),
    ("Form", "Spatial organisation", "form", "#ff5c7c", "Intro, rhythm, harmony, climax and outro become connected zones."),
    ("Dynamics", "Openness and enclosure", "dynamics", "#7aa2ff", "Loud passages open the walls. Quiet ones close them in."),
]

COVERS = [("Neon Hours", ("#ff2d55", "#2b0a3d", "#ffd36b")), ("Static Bloom", ("#0f2a5a", "#7aa2ff", "#ff7ab6")),
          ("Glass Weather", ("#1c1c28", "#4f8cff", "#d9f1ff")), ("Night Registry", ("#2a0a12", "#c4122f", "#f3eefc")),
          ("Low Orbit", ("#0b3b3a", "#3fd6a0", "#fff1a8")), ("Paper Skyline", ("#f1e6d2", "#c9884a", "#2b2b3a")),
          ("Velvet Signal", ("#3a0f5c", "#ff5c7c", "#ffe1a8")), ("Afterimage", ("#101018", "#9b6bff", "#ff2d55"))]


def cover_svg(i, pal):
    a, b, c = pal
    s = i % 6
    if s == 0:
        body = f'<circle cx="150" cy="125" r="72" fill="{c}"/>' + "".join(
            f'<rect y="{170 + k * 15}" width="300" height="{3 + k}" fill="{a}"/>' for k in range(7))
    elif s == 1:
        body = "".join(f'<rect x="{k * 25}" y="{40 + (k * 37) % 120}" width="14" height="{260 - (k * 37) % 120}" fill="{c if k % 3 else a}" opacity=".9"/>' for k in range(12))
    elif s == 2:
        body = "".join(f'<circle cx="150" cy="150" r="{20 + k * 20}" fill="none" stroke="{c}" stroke-width="{1 + k % 3}" opacity="{1 - k * .07:.2f}"/>' for k in range(7))
    elif s == 3:
        body = "".join(f'<rect x="{10 + k * 28}" y="{300 - (60 + (k * 53) % 170)}" width="22" height="{60 + (k * 53) % 170}" fill="{c}" opacity=".9"/>' for k in range(10))
    elif s == 4:
        body = "".join(f'<path d="M0 {70 + k * 22} Q 75 {30 + k * 22} 150 {70 + k * 22} T 300 {70 + k * 22}" fill="none" stroke="{c}" stroke-width="3"/>' for k in range(9))
    else:
        body = f'<polygon points="150,40 260,250 40,250" fill="{c}" opacity=".9"/><polygon points="150,110 220,250 80,250" fill="{a}"/>'
    return (f'<svg viewBox="0 0 300 300" preserveAspectRatio="xMidYMid slice"><defs><linearGradient id="g{i}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{a}"/><stop offset="1" stop-color="{b}"/></linearGradient></defs>'
            f'<rect width="300" height="300" fill="url(#g{i})"/>{body}</svg>')


def cover_card(art_html, title, pal, sp):
    dots = "".join(f'<i style="background:{p}"></i>' for p in pal)
    return (f'<div class="float" style="--sp:{sp}"><div class="cover tilt reveal"><div class="vinyl"><i></i></div>'
            f'<div class="art">{art_html}</div><div class="meta"><b>{html.escape(title)}</b><em>{dots}</em></div></div></div>')


def head(kicker, title, text):
    return (f'<div class="eyebrow reveal">{kicker}</div><h1 class="reveal disp" style="font-size:clamp(2.4rem,6vw,4.6rem);margin:0">{title}</h1>'
            f'<p class="lead reveal">{text}</p>')


def band(words, rev=False):
    return f'<div class="band{" rev" if rev else ""}"><span>{words}</span></div>'


def card(c, num, title, text, svg=""):
    n = f'<div class="num">{num}</div>' if num else ""
    return f'<div class="card tilt reveal" style="--c:{c}">{n}{svg}<h3>{title}</h3><p>{text}</p></div>'


def score_strip(segs):
    mx = max((s["height"] for s in segs), default=1) or 1
    cells = "".join(
        f'<i style="--c:{ZONE_COLORS.get(s["zone"], "#ff2d55")};--i:{k};height:{max(8, 100 * s["height"] / mx):.0f}%" '
        f'title="{s["zone"]} | {s["start_time"]}s | height {s["height"]}"></i>' for k, s in enumerate(segs))
    return f'<div class="score">{cells}</div>'


def stats(items):
    return '<div class="grid3">' + "".join(f'<div class="card stat tilt reveal"><b>{v}</b><span>{k}</span></div>' for k, v in items) + "</div>"


def hero_html():
    letters = lambda w, d: "".join(f'<span style="animation-delay:{d + i * .06:.2f}s">{ch}</span>' for i, ch in enumerate(w))
    return """<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@800&family=Inter:wght@300;400&display=swap" rel="stylesheet">
<style>html,body{margin:0;height:100%;overflow:hidden;background:transparent;font-family:Inter,sans-serif;color:#f3eefc}
canvas{position:absolute;inset:0}
#t{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;pointer-events:none}
h1{margin:0;font-family:Syne,sans-serif;font-weight:800;font-size:clamp(3rem,10vw,8rem);line-height:.9;letter-spacing:-.03em;text-shadow:0 0 40px rgba(0,0,0,.8)}
h1 span{display:inline-block;pointer-events:auto;opacity:0;transform:translateY(40px);animation:up .9s cubic-bezier(.2,.8,.2,1) forwards;transition:transform .3s,color .3s}
h1 span:hover{transform:translateY(-16px) scale(1.12);color:#ff2d55}
.o{-webkit-text-stroke:2px #fff;color:transparent}
p{margin:1.4rem 0 0;letter-spacing:.35em;text-transform:uppercase;font-size:.8rem;color:#c9c0e6;opacity:0;animation:up 1s .9s forwards}
#h{position:absolute;bottom:16px;left:50%;width:1px;height:44px;background:linear-gradient(#ff2d55,transparent);animation:dr 1.8s infinite}
@keyframes up{to{opacity:1;transform:none}}@keyframes dr{0%{transform:scaleY(0);transform-origin:top}50%{transform:scaleY(1);transform-origin:top}51%{transform-origin:bottom}100%{transform:scaleY(0);transform-origin:bottom}}
</style></head><body><canvas id="c"></canvas>
<div id="t"><h1>""" + letters("SPATIAL", 0.1) + '</h1><h1 class="o">' + letters("SCORE", 0.5) + """</h1><p>Music becomes architecture</p></div><div id="h"></div>
<script>
var c=document.getElementById('c'),x=c.getContext('2d'),T=document.getElementById('t'),W,H,mx=-1,my=-1,sy=0,m=0,t0=performance.now(),N=110;
function rs(){var d=window.devicePixelRatio||1;W=innerWidth;H=innerHeight;c.width=W*d;c.height=H*d;c.style.width=W+'px';c.style.height=H+'px';x.setTransform(d,0,0,d,0,0)}
addEventListener('resize',rs);rs();
addEventListener('mousemove',function(e){mx=e.clientX;my=e.clientY});addEventListener('mouseout',function(){mx=-1});
try{window.parent.document.addEventListener('scroll',function(e){var el=e.target;if(el&&el.scrollTop!==undefined)sy=el.scrollTop},true)}catch(e){}
function frame(now){var t=(now-t0)/1000;m+=(Math.min(1,sy/420)-m)*.08;x.clearRect(0,0,W,H);
 var cx=W/2,cy=H*.5,R=Math.min(W,H)*.22;
 for(var i=0;i<N;i++){var u=i/N,ang=u*Math.PI*2-Math.PI/2;
  var a=.5+.28*Math.sin(t*1.6+i*.35)+.18*Math.sin(t*2.7+i*.11)+.1*Math.sin(t*.7+i*.9);
  var rx=cx+Math.cos(ang)*R,ry=cy+Math.sin(ang)*R,fx=(i+.5)/N*W,fy=H*.92;
  var px=rx+(fx-rx)*m,py=ry+(fy-ry)*m;
  if(mx>=0){var d=Math.hypot(mx-px,my-py);a+=Math.max(0,1-d/170)*.9}
  a=Math.min(1.4,Math.max(.08,a));
  var len=(R*.95*(1-m)+H*.5*m)*a,dx=Math.cos(ang)*(1-m),dy=Math.sin(ang)*(1-m)-m,L=Math.hypot(dx,dy)||1;
  x.strokeStyle='hsl('+(350-u*140)+',90%,62%)';x.shadowColor=x.strokeStyle;x.shadowBlur=14;
  x.lineWidth=(1-m)*3+m*(W/N*.6);x.lineCap=m>.5?'butt':'round';
  x.beginPath();x.moveTo(px,py);x.lineTo(px+dx/L*len,py+dy/L*len);x.stroke()}
 if(mx>=0){x.shadowBlur=0;x.strokeStyle='rgba(255,255,255,.5)';x.lineWidth=1;x.beginPath();x.arc(mx,my,18+6*Math.sin(t*5),0,6.283);x.stroke()}
 T.style.opacity=1-m*.9;T.style.transform='translateY('+(-m*50)+'px)';
 requestAnimationFrame(frame)}
requestAnimationFrame(frame);
</script></body></html>"""


def summary_html(arch):
    S = arch["segments"]
    n = len(S)
    if not n:
        return ""
    avg = lambda k, rows: sum(r[k] for r in rows) / max(1, len(rows))
    hs = [s["height"] for s in S]
    cards = [("Rooms", n), ("Path length", f'{sum(s["length"] for s in S):.0f} m'),
             ("Height range", f"{min(hs):.1f} to {max(hs):.1f} m"), ("Average height", f"{sum(hs) / n:.1f} m"),
             ("Average openness", f'{avg("openness", S) * 100:.0f}%'), ("Total ribs", sum(s["ribs"] for s in S))]
    top = '<div class="grid3">' + "".join(
        f'<div class="card stat tilt reveal"><b>{v}</b><span>{k}</span></div>' for k, v in cards) + "</div>"
    mats = {"concrete": "#8a8a8a", "wood": "#b07d45", "glass": "#9fd8ee"}
    mb = '<div class="mbar">' + "".join(
        f'<i style="flex:{max(0.001, sum(1 for s in S if s["material"] == k))};background:{c}" title="{k}: {sum(1 for s in S if s["material"] == k)} rooms"></i>'
        for k, c in mats.items()) + "</div>"
    legend = " ".join(f'<span style="color:{c}">{k} {sum(1 for s in S if s["material"] == k)}</span>' for k, c in mats.items())
    rows = ""
    for name, col, _, _ in ZONES:
        z = [s for s in S if s["zone"] == name.lower()]
        if z:
            rows += (f'<tr><td style="color:{col}"><b>{name}</b></td><td>{len(z)}</td><td>{avg("height", z):.1f}</td><td>{avg("length", z):.1f}</td>'
                     f'<td>{avg("openness", z) * 100:.0f}%</td><td>{avg("density", z) * 100:.0f}%</td><td>{sum(s["ribs"] for s in z)}</td><td>{avg("light", z):.2f}</td></tr>')
    table = ""
    if rows:
        table = ('<table class="ztable"><tr><th>Zone</th><th>Rooms</th><th>Avg height</th><th>Avg length</th><th>Openness</th>'
                 f'<th>Density</th><th>Ribs</th><th>Light</th></tr>{rows}</table>')
    return (top + '<div class="card reveal" style="margin-top:1rem"><p style="margin:0 0 .5rem">Materials chosen from brightness</p>' + mb +
            f'<p style="margin:.5rem 0 0;font-size:.85rem">{legend}</p>{table and "<div style=margin-top:1rem></div>" + table}</div>')
