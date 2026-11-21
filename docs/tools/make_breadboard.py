"""Draws docs/breadboard.svg: where every part and jumper goes on a standard
half-size+ breadboard (30 columns, rows a-j, two power rails each side).

Run:  python3 docs/tools/make_breadboard.py              -> breadboard.svg (with boost converter)
      python3 docs/tools/make_breadboard.py --no-boost   -> breadboard_no_boost.svg
"""
import os
import sys

BOOST = "--no-boost" not in sys.argv
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                   "breadboard.svg" if BOOST else "breadboard_no_boost.svg")

P = 20                       # hole pitch in px
X0 = 80                      # x of column 1
ROWS = {"a": 170, "b": 190, "c": 210, "d": 230, "e": 250,
        "f": 300, "g": 320, "h": 340, "i": 360, "j": 380}
TOP_P, TOP_N, BOT_P, BOT_N = 110, 130, 420, 440   # rail y positions

RED, BLACK = "#d62f2f", "#222"
el = []


def add(s):
    el.append(s)


def X(c):
    return X0 + (c - 1) * P


def h(ref):
    """'h8' -> (x, y) of that hole. Rails: 'T+5', 'T-5', 'B+5', 'B-5'."""
    if ref[0] in "TB" and ref[1] in "+-":
        y = {"T+": TOP_P, "T-": TOP_N, "B+": BOT_P, "B-": BOT_N}[ref[:2]]
        return X(int(ref[2:])), y
    return X(int(ref[1:])), ROWS[ref[0]]


def rect(x0, y0, x1, y1, fill, stroke="none", sw=1, rx=0, extra=""):
    add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rx}" fill="{fill}" '
        f'stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def circ(cx, cy, r, fill, stroke="none", sw=1):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def line(x0, y0, x1, y1, stroke, sw=1, extra=""):
    add(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linecap="round" {extra}/>')


def text(x, y, s, size=12, anchor="start", weight="normal", fill="#222", extra=""):
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" '
        f'fill="{fill}" {extra}>{s}</text>')


def plug(x, y, color):
    rect(x - 4, y - 4, x + 4, y + 4, color, "#000", 0.8, rx=1)


def wire(a, b, color, lift=0, pts=None, dash=False):
    """Jumper from a to b (hole refs or (x, y)). lift bows it so it reads as a hop."""
    pa = h(a) if isinstance(a, str) else a
    pb = h(b) if isinstance(b, str) else b
    ex = ' stroke-dasharray="6 4"' if dash else ""
    if pts:
        d = f"M{pa[0]},{pa[1]} " + " ".join(f"L{x},{y}" for x, y in pts) + f" L{pb[0]},{pb[1]}"
    elif lift:
        mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        n = (dx * dx + dy * dy) ** 0.5 or 1
        cx, cy = mx - dy / n * lift, my + dx / n * lift
        d = f"M{pa[0]},{pa[1]} Q{cx:.1f},{cy:.1f} {pb[0]},{pb[1]}"
    else:
        d = f"M{pa[0]},{pa[1]} L{pb[0]},{pb[1]}"
    add(f'<path d="{d}" fill="none" stroke="#000" stroke-opacity="0.35" stroke-width="5.2" '
        f'stroke-linecap="round" stroke-linejoin="round"{ex}/>')
    add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="3.6" stroke-linecap="round" '
        f'stroke-linejoin="round"{ex}/>')
    for p, r in ((pa, a), (pb, b)):
        if isinstance(r, str):
            plug(p[0], p[1], color)


def resistor(a, b, bands, name, below=False):
    pa, pb = h(a), h(b)
    line(*pa, *pb, "#8c8c8c", 1.6)
    mx, my = (pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2
    vertical = abs(pb[1] - pa[1]) > abs(pb[0] - pa[0])
    if vertical:
        rect(mx - 5, my - 13, mx + 5, my + 13, "#e8d3a6", "#a88d5a", 0.8, rx=4)
        for i, c in enumerate(bands):
            rect(mx - 5, my - 9 + i * 5, mx + 5, my - 6 + i * 5, c)
        text(mx + 9, my + 4, name, 11, weight="bold")
    else:
        rect(mx - 13, my - 5, mx + 13, my + 5, "#e8d3a6", "#a88d5a", 0.8, rx=4)
        for i, c in enumerate(bands):
            rect(mx - 9 + i * 5, my - 5, mx - 6 + i * 5, my + 5, c)
        text(mx, my + 19 if below else my - 9, name, 11, "middle", "bold")
    for p in (pa, pb):
        circ(*p, 2.5, "#8c8c8c")


def ecap(plus, minus, name):
    pp, pm = h(plus), h(minus)
    cx, cy = (pp[0] + pm[0]) / 2 + 14, (pp[1] + pm[1]) / 2
    line(*pp, cx - 6, cy - 4, "#8c8c8c", 1.6)
    line(*pm, cx - 6, cy + 4, "#8c8c8c", 1.6)
    circ(cx, cy, 11, "#244f9e", "#16336a")
    add(f'<path d="M{cx - 8},{cy + 6} A11,11 0 0 0 {cx + 8},{cy + 6}" fill="none" stroke="#dfe6f2" stroke-width="3"/>')
    text(cx, cy - 1, "+", 10, "middle", "bold", "#fff")
    text(cx + 15, cy + 4, name, 11, weight="bold")
    for p in (pp, pm):
        circ(*p, 2.5, "#8c8c8c")


# ================================================================ breadboard
rect(50, 88, 690, 462, "#f4f1ea", "#cfc8b8", 1.5, rx=10)
rect(50, 268, 690, 282, "#e6e1d5")                                   # centre gap
for y, col in ((TOP_P, RED), (TOP_N, "#2f62c9"), (BOT_P, RED), (BOT_N, "#2f62c9")):
    off = -10 if y in (TOP_P, BOT_P) else 10
    if y == TOP_P:
        off = -10
    elif y == TOP_N:
        off = 10
    elif y == BOT_P:
        off = -10
    else:
        off = 10
    line(70, y + off, 670, y + off, col, 1.2)
    for c in range(1, 31):
        rect(X(c) - 3, y - 3, X(c) + 3, y + 3, "#bdb6a6", rx=1)
for r, y in ROWS.items():
    text(62, y + 4, r, 10, "middle", fill="#8a8373")
    for c in range(1, 31):
        rect(X(c) - 3, y - 3, X(c) + 3, y + 3, "#bdb6a6", rx=1)
for c in range(1, 31):
    if c == 1 or c % 5 == 0:
        text(X(c), 160, str(c), 9, "middle", fill="#8a8373")
        text(X(c), 398, str(c), 9, "middle", fill="#8a8373")
text(676, TOP_P + 4, "+", 13, weight="bold", fill=RED)
text(676, TOP_N + 4, "−", 13, weight="bold", fill="#2f62c9")
text(676, BOT_P + 4, "+", 13, weight="bold", fill=RED)
text(676, BOT_N + 4, "−", 13, weight="bold", fill="#2f62c9")
text(370, 80, f"Rails:  top + = 3.3 V,  top − = GND    ·    bottom + = {'5 V' if BOOST else 'battery'} for the servo,  bottom − = GND", 11, "middle", "bold", "#7a1d1d")

# ================================================================ XIAO (USB-C to the left)
rect(104, 198, 256, 332, "#1f1f1f", "#000", 1, rx=6)
rect(86, 252, 106, 278, "#c7ccd1", "#888", 1, rx=4)                  # USB-C
rect(150, 236, 214, 294, "#9aa0a6", "#6f757b", 1, rx=2)              # RF can
text(182, 262, "XIAO", 13, "middle", "bold", "#fff")
text(182, 277, "ESP32-C3", 10, "middle", fill="#eee")
text(182, 289, "USB-C ←", 9, "middle", fill="#ddd")
for i, n in enumerate(("5V", "GND", "3V3", "D10", "D9", "D8", "D7")):
    x = X(3 + i)
    circ(x, ROWS["c"], 4, "#d4af37", "#8a6d10")
    text(x, 226, n, 8, "middle", fill="#fff")
for i, n in enumerate(("D0", "D1", "D2", "D3", "D4", "D5", "D6")):
    x = X(3 + i)
    circ(x, ROWS["g"], 4, "#d4af37", "#8a6d10")
    text(x, 310, n, 8, "middle", fill="#fff")
text(180, 344 + 0, "", 9)

# ================================================================ parts on the board
# MOSFET seen from above, in the centre gap; legs in f22 (G) f23 (D) f24 (S)
rect(X(22) - 13, 264, X(24) + 13, 270, "#c7ccd1", "#888", 0.8)      # tab (metal back)
rect(X(22) - 13, 270, X(24) + 13, 290, "#1f1f1f", "#000", 1, rx=1)
for c, n in ((22, "G"), (23, "D"), (24, "S")):
    line(X(c), 290, X(c), ROWS["f"], "#aaa", 2)
    text(X(c), 285, n, 10, "middle", "bold", "#fff")
text(X(23), 258, "MOSFET, metal tab toward the gap", 10, "middle", "bold")

# LED: cathode (short leg) b11, anode (long leg) b13
for c in (11, 13):
    line(X(c), ROWS["b"], X(12) + (c - 12) * 4, ROWS["b"] - 14, "#aaa", 1.6)
circ(X(12), ROWS["b"] - 18, 8, "#e74c3c", "#9b2d22")
circ(X(12) - 2, ROWS["b"] - 20, 2.4, "#f5b7b1")
text(X(12), ROWS["b"] - 30, "LED", 10, "middle", "bold")
for c in (11, 13):
    circ(X(c), ROWS["b"], 2.5, "#8c8c8c")

# reed switch: b6 to top − rail (col 7)
pa, pb = h("b6"), h("T-7")
line(*pa, *pb, "#8c8c8c", 1.4)
add(f'<rect x="{(pa[0] + pb[0]) / 2 - 4}" y="{(pa[1] + pb[1]) / 2 - 14}" width="8" height="28" rx="4" '
    f'fill="#d6eefc" stroke="#6aa7cc" transform="rotate(-18 {(pa[0] + pb[0]) / 2} {(pa[1] + pb[1]) / 2})"/>')
circ(*pa, 2.5, "#8c8c8c")
circ(*pb, 2.5, "#8c8c8c")
text(X(7) + 10, 163, "reed", 10, weight="bold")

resistor("T+13", "a13", ("#8B4513", "#222", "#d62f2f"), "1k")           # R4 LED
resistor("j12", "B-12", ("#d62f2f", "#d62f2f", "#f1c40f"), "220k")      # R2
resistor("h12", "h16", ("#d62f2f", "#d62f2f", "#f1c40f"), "220k", below=True)       # R1
resistor("j22", "B-22", ("#8B4513", "#222", "#f1c40f"), "100k")         # R3
ecap("i16", "B-17", "C1")
ecap("B+20", "B-20", "C2")

# ================================================================ jumpers on the board
wire("a4", "T-4", BLACK)                       # XIAO GND -> top GND rail
wire("a5", "T+5", RED)                         # XIAO 3V3 -> top 3V3 rail
wire("a8", "a11", "#f1c40f", lift=-10)         # D8 -> LED cathode
wire("i5", "i12", "#2e86de", lift=14)          # D2 -> divider midpoint
wire("h8", "h22", "#16a085", lift=-48)         # D5 -> MOSFET gate
wire("j24", "B-24", BLACK)                     # MOSFET source -> GND
wire((X(30), TOP_N), (X(30), BOT_N), BLACK, pts=[(700, TOP_N), (700, BOT_N)])  # join GND rails
plug(X(30), TOP_N, BLACK)
plug(X(30), BOT_N, BLACK)

# ================================================================ off-board parts
# microphone module (bottom left)
rect(60, 520, 190, 580, "#7a1f8f", "#4d1159", 1, rx=4)
circ(160, 556, 14, "#333", "#111")
circ(160, 556, 9, "#555")
text(70, 572, "MAX4466 mic", 11, weight="bold", fill="#fff")
for x, n in ((80, "OUT"), (105, "GND"), (130, "VCC")):
    circ(x, 528, 3.5, "#d4af37")
    text(x, 544, n, 8, "middle", fill="#fff")
wire((80, 528), "j4", "#8e44ad", lift=10)
wire((105, 528), "B-2", BLACK)
wire((130, 528), "T+1", RED, pts=[(130, 500), (34, 500), (34, TOP_P)])

# boost converter (bottom centre)
if not BOOST:
    wire("j16", "B+29", RED, lift=-16)         # battery + straight to the servo rail
    text(330, 520, "No boost: battery + goes straight", 11, weight="bold", fill="#7a1d1d")
    text(330, 535, "to the servo rail (j16 → bottom +).", 11, weight="bold", fill="#7a1d1d")
else:
    rect(330, 520, 500, 585, "#5b3a8a", "#3b2460", 1, rx=4)
    text(415, 566, "5 V boost converter", 11, "middle", "bold", "#fff")
    for x, n in ((350, "EN"), (390, "VIN"), (430, "GND"), (470, "VOUT")):
        circ(x, 528, 3.5, "#d4af37")
        text(x, 544, n, 8, "middle", fill="#fff")
    wire((350, 528), "i8", "#16a085", lift=-30, dash=True)
    wire((390, 528), "j16", "#e67e22", lift=8)
    wire((430, 528), "B-27", BLACK, lift=-10)
    wire((470, 528), "B+29", RED, lift=-14)
    text(330, 600, "EN: only if your module has one.", 10, fill="#555")

# battery (bottom right)
rect(560, 605, 700, 660, "#c7ccd1", "#8f969c", 1.2, rx=8)
text(630, 630, "LiPo 3.7 V", 12, "middle", "bold", fill="#333")
text(630, 646, "1000 mAh", 10, "middle", fill="#333")
wire((560, 618), "f16", RED, pts=[(540, 618), (540, 500), (X(16) + 8, 480), (X(16) + 8, 300)])
wire((560, 645), "B-19", BLACK, pts=[(520, 645), (520, 490), (X(19), 470)])
if BOOST:
    text(400, 625, "Battery + also goes to the", 10, "middle", fill="#555")
    text(400, 639, "BAT+ pad under the XIAO", 10, "middle", fill="#555")
    wire("g16", (254, 316), RED, dash=True, lift=-12)
else:
    text(400, 625, "XIAO runs from USB for now. The battery", 10, "middle", fill="#555")
    text(400, 639, "only powers the servo; grounds are shared.", 10, "middle", fill="#555")
text(232, 352, "", 9)

# servo (right)
rect(760, 300, 880, 360, "#3b6fd6", "#24489a", 1.5, rx=5)
circ(850, 330, 12, "#e8e8e8", "#999")
text(805, 335, "MG90S", 13, "middle", "bold", "#fff")
for i, (c, ref, lift) in enumerate((("#f39c12", "h7", 40), (RED, "B+30", -10), ("#6b3e1f", "i23", 10))):
    y = 314 + i * 16
    line(744, y, 760, y, c, 4)
    wire((744, y), ref, c, lift=lift)

# ================================================================ connection list + notes
NX = 895
text(NX, 110, "Connections", 15, weight="bold")
rows = [
    ("XIAO GND (a4)", "top − rail"),
    ("XIAO 3V3 (a5)", "top + rail"),
    ("D10 (b6)", "reed switch → top − rail"),
    ("D8 (a8)", "LED short leg (b11)"),
    ("LED long leg (b13)", "1 kΩ → top + rail"),
    ("D1 (j4)", "mic OUT"),
    ("D2 (i5)", "R1/R2 midpoint (col 12)"),
    ("R1 220k", "h12 → h16 (battery +)"),
    ("R2 220k", "j12 → bottom − rail"),
    ("D4 (h7)", "servo orange"),
    ("D5 (h8)", "MOSFET gate (h22)" + (" + boost EN" if BOOST else "")),
    ("R3 100k", "gate (j22) → GND"),
    ("MOSFET drain (i23)", "servo brown"),
    ("MOSFET source (j24)", "bottom − rail"),
    ("Servo red", "bottom + rail (5 V)" if BOOST else "bottom + rail (battery)"),
    ("Battery +", "col 16 → boost VIN, C1+, R1" if BOOST else "col 16 → C1+, R1, + rail"),
    ("Battery −", "bottom − rail"),
    ("C1 470µF", "col 16 (+) → − rail"),
    ("C2 470µF", "across bottom rails (col 20)"),
    ("Both − rails", "joined (right edge)"),
]
for i, (a, b) in enumerate(rows):
    y = 134 + i * 19
    if i % 2 == 0:
        rect(NX - 6, y - 13, 1194, y + 5, "#f3f4f6")
    text(NX, y, a, 11, weight="bold")
    text(NX + 122, y, b, 11)

text(40, 690, "Before you power it:", 13, weight="bold")
notes = [
    "• Capacitor stripe = minus. LED long leg = plus. MOSFET: printed side facing you, legs are Gate, Drain, Source left to right.",
    "• If your breadboard's rails have a break in the middle, bridge each one. Never join the 5 V servo rail to the XIAO's 5V pin.",
    "• No battery or boost yet? Skip them, C1 and R1, and run a wire from the XIAO 5V pin (a3) to the bottom + rail: the servo runs from USB.",
]
if not BOOST:
    notes = [
        "• Capacitor stripe = minus. MOSFET: printed side facing you, legs are Gate, Drain, Source left to right.",
        "• The servo runs straight from the battery (3.7-4.2 V): a bit weaker than on 5 V but fine for testing. Don't connect the XIAO's 5V pin to anything.",
        "• No reed switch or LED yet? Leave them out. Plug the XIAO's USB-C into the computer to power and program it.",
    ]
for i, n in enumerate(notes):
    text(40, 712 + i * 18, n, 12)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 780" width="1200" height="780"
     font-family="Helvetica, Arial, sans-serif">
<rect width="1200" height="780" fill="#fff"/>
<text x="40" y="40" font-size="22" font-weight="bold" fill="#222">The Switch Flipper: breadboard wiring{"" if BOOST else " (battery, no boost converter)"}</text>
<text x="40" y="62" font-size="13" fill="#666">Every part of the circuit on one breadboard. Holes are named column number + row letter (h8 = row h, column 8).</text>
{chr(10).join(el)}
</svg>
'''
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", os.path.normpath(OUT))
