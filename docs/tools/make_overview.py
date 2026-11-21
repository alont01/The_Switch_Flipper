"""Draws docs/overview.svg: a simple, not-to-scale picture of what's inside
the box. The exact, dimensioned drawings are in docs/layout_2d.svg.

Run:  python3 docs/tools/make_overview.py
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "overview.svg")

# colours: each kind of part gets its own so they're easy to tell apart
MECH = "#f28c28"      # slider + sticks (printed, moving)
MECH_D = "#b85f0f"
SERVO = "#3b6fd6"
SERVO_D = "#24489a"
BOARD = "#2f8f4e"     # perfboard
BOARD_D = "#1d5e32"
CHIP = "#2b2b2b"
SILVER = "#c7ccd1"
SHELL = "#9aa3ab"
WALL = "#d9d4cc"
SWITCH = "#8a8f94"
TXT = "#222"
LEAD = "#777"

el = []


def add(s):
    el.append(s)


def rect(x0, y0, x1, y1, fill, stroke="none", sw=1, rx=0, extra=""):
    add(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def circ(cx, cy, r, fill, stroke="none", sw=1):
    add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def line(x0, y0, x1, y1, stroke, sw=1, extra=""):
    add(f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y1}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linecap="round" {extra}/>')


def path(d, stroke, sw=1, fill="none", extra=""):
    add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
        f'stroke-linecap="round" stroke-linejoin="round" {extra}/>')


def text(x, y, s, size=13, anchor="start", weight="normal", fill=TXT, style=""):
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" fill="{fill}" {style}>{s}</text>')


def label(tx, ty, px, py, s, anchor="start"):
    """Text at (tx, ty) with a leader line to the point (px, py)."""
    lx = tx - 4 if anchor == "start" else tx + 4
    line(lx, ty - 4, px, py, LEAD, 0.8)
    circ(px, py, 1.8, LEAD)
    text(tx, ty, s, anchor=anchor)


def arrow(x0, y0, x1, y1, color, both=False, sw=2):
    m = ' marker-end="url(#ah)"' + (' marker-start="url(#ah)"' if both else "")
    line(x0, y0, x1, y1, color, sw, m)


def perf_holes(x0, y0, x1, y1, step=9):
    y = y0 + step / 2
    while y < y1:
        x = x0 + step / 2
        while x < x1:
            circ(round(x, 1), round(y, 1), 1.1, BOARD_D)
            x += step
        y += step


def resistor(x0, y, w=34):
    line(x0 - 6, y, x0 + w + 6, y, SILVER, 1.5)
    rect(x0, y - 4, x0 + w, y + 4, "#e8d3a6", "#a88d5a", 0.8, rx=3)
    for i, c in enumerate(("#c0392b", "#c0392b", "#f1c40f")):
        rect(x0 + 7 + i * 7, y - 4, x0 + 10 + i * 7, y + 4, c)


def cap(cx, cy, r=11):
    circ(cx, cy, r, "#244f9e", "#16336a", 1)
    path(f"M{cx - r + 3},{cy - 4} A{r},{r} 0 0 1 {cx + r - 3},{cy - 4}", "#dfe6f2", 3)


# ================================================================ FRONT VIEW
FX = 0
text(220, 88, "Front view (cover off)", 15, "middle", "bold")

# faceplate opening behind, dashed
rect(196, 214, 244, 300, "none", SWITCH, 1, rx=3, extra='stroke-dasharray="4 3"')

# box shell
rect(120, 100, 320, 550, "#f7f8f9", SHELL, 9, rx=14)

# --- wires (drawn first so parts sit on top)
for i, c in enumerate(("#6b3e1f", "#d62f2f", "#f39c12")):          # servo lead
    x = 133 + i * 4
    path(f"M{x},368 L{x},150 L150,{144 + i * 4}", c, 2)
path("M300,197 L311,197 L311,368", "#555", 1.6)                     # reed leads
path("M304,200 L308,200 L308,368", "#555", 1.6)

# --- servo
rect(128, 120, 257, 129, SERVO_D, rx=2)                              # mounting tabs
rect(140, 104, 245, 158, SERVO, SERVO_D, 1.5, rx=4)
circ(168, 124, 9, "#e8e8e8", "#999")                                 # shaft
path("M168,124 L203,151", "#f2f2f2", 7)                              # horn
path("M168,124 L203,151", "#999", 1, extra='stroke-dasharray="0"')
circ(168, 124, 3, "#999")
line(203, 151, 220, 196, "#5b5b5b", 3)                               # link rod
circ(203, 151, 2.5, "#5b5b5b")
circ(220, 196, 2.5, "#5b5b5b")

# --- slider: two rails, a top bar, and the two sticks
rect(165, 190, 275, 202, MECH, MECH_D, 1.2, rx=3)                    # top bar
rect(165, 190, 177, 330, MECH, MECH_D, 1.2, rx=3)                    # left rail
rect(263, 190, 275, 330, MECH, MECH_D, 1.2, rx=3)                    # right rail
rect(264, 193, 274, 200, "#444", rx=1)                               # magnet
# toggle lever, seen from the front (tip up)
rect(214, 229, 226, 262, SWITCH, "#5d6166", 1, rx=5)
circ(220, 231, 6, "#a7acb1", "#5d6166")
rect(170, 211, 270, 220, MECH, MECH_D, 1.2, rx=4)                    # upper stick
rect(170, 240, 270, 249, MECH, MECH_D, 1.2, rx=4)                    # lower stick
arrow(150, 270, 150, 210, MECH_D, both=True)

# reed switch (glass tube)
rect(282, 193, 304, 201, "#d6eefc", "#6aa7cc", 1, rx=4)
line(285, 197, 301, 197, "#6aa7cc", 1)

# --- perfboard + parts
rect(128, 360, 312, 530, BOARD, BOARD_D, 1.5, rx=3)
perf_holes(128, 360, 312, 530)
cap(152, 385)
cap(178, 385)
rect(198, 370, 236, 410, "#6c3fa0", "#46266e", 1, rx=2)               # boost
text(217, 388, "5V", 10, "middle", fill="#fff")
text(217, 400, "boost", 9, "middle", fill="#fff")
rect(251, 368, 274, 377, SILVER, "#888", 0.8)                        # MOSFET tab
circ(262.5, 372.5, 2.4, BOARD)
rect(251, 377, 274, 400, CHIP, "#000", 1, rx=1)
for x in (256, 262.5, 269):
    line(x, 400, x, 408, SILVER, 1.6)
circ(295, 372, 6, "#e74c3c", "#9b2d22")                              # LED
circ(293, 370, 2, "#f5b7b1")
resistor(254, 428)
resistor(254, 446)
resistor(254, 464)
rect(146, 422, 234, 512, CHIP, "#000", 1, rx=4)                      # XIAO
rect(156, 432, 224, 476, "#9aa0a6", "#6f757b", 1, rx=2)               # RF can
text(190, 491, "XIAO", 12, "middle", "bold", "#fff")
text(190, 504, "ESP32-C3", 10, "middle", fill="#ddd")
rect(180, 512, 200, 520, SILVER, "#888", 1, rx=2)                    # USB-C
rect(247, 482, 300, 520, "#7a1f8f", "#4d1159", 1, rx=2)               # mic module
circ(273, 500, 11, "#333", "#111")
circ(273, 500, 7, "#555")
rect(178, 546, 202, 554, "#fff", SHELL, 1, rx=2)                     # USB hole in shell

# --- front labels
label(112, 128, 140, 124, "Servo", "end")
label(112, 160, 190, 141, "Horn + link", "end")
label(112, 242, 150, 240, "Slider moves ↕", "end")
label(112, 390, 150, 385, "Capacitors", "end")
label(112, 470, 146, 470, "XIAO", "end")
label(112, 538, 190, 520, "USB-C (charge)", "end")
label(335, 197, 304, 197, "Reed switch")
label(335, 222, 270, 215, "Two sticks")
label(335, 262, 226, 255, "Toggle")
label(335, 342, 312, 350, "Perfboard")
label(335, 372, 301, 372, "LED")
label(335, 392, 274, 389, "MOSFET")
label(335, 412, 236, 405, "5 V boost")
label(335, 448, 288, 446, "Resistors")
label(335, 500, 300, 500, "Microphone")

# ================================================================ SIDE VIEW
text(680, 88, "Side view", 15, "middle", "bold")
TY = 231   # toggle tip height

# wall, faceplate, backplate
rect(510, 74, 540, 600, WALL)
for y in range(80, 600, 14):
    line(510, y + 10, 520, y, "#bdb6ab", 1)
rect(540, 80, 560, 578, "#ecebe7", "#b9b6ae", 1, rx=2)
rect(560, 77, 570, 581, "#e2d9f3", "#9c8bc2", 1, rx=2)
# box shell
path("M570,100 L712,100 Q726,100 726,114 L726,536 Q726,550 712,550 L570,550",
     SHELL, 9, fill="#f7f8f9")
# toggle
path(f"M560,256 L611,{TY + 2}", SWITCH, 8)
circ(612, TY + 2, 5, "#a7acb1", "#5d6166")
rect(556, 248, 566, 264, "#6d7277", rx=2)

rect(722, 290, 730, 320, "#f7f8f9")                                   # handle slot
for y in (480, 492, 504, 516):                                        # sound holes
    rect(721, y, 731, y + 4, "#fff")

# battery against backplate
rect(576, 362, 612, 532, SILVER, "#8f969c", 1.2, rx=6)
text(594, 450, "LiPo", 11, "middle", fill="#333", style='transform="rotate(-90 594 450)"')

# servo (shaft points to the front)
rect(600, 120, 655, 129, SERVO_D, rx=2)
rect(605, 104, 652, 158, SERVO, SERVO_D, 1.5, rx=4)
rect(652, 120, 664, 128, "#e8e8e8", "#999")
rect(664, 112, 671, 150, "#f2f2f2", "#999", 1, rx=3)                  # horn
line(668, 146, 668, 194, "#5b5b5b", 3)                                # link rod

# slider: rail + top block + sticks reaching back toward the wall
rect(640, 190, 676, 202, MECH, MECH_D, 1.2, rx=3)
rect(640, 190, 655, 330, MECH, MECH_D, 1.2, rx=3)
rect(606, 212, 655, 220, MECH, MECH_D, 1.2, rx=3)                    # upper stick
rect(606, 241, 655, 249, MECH, MECH_D, 1.2, rx=3)                    # lower stick
rect(655, 300, 732, 310, MECH, MECH_D, 1.2, rx=2)                    # handle stem
rect(732, 288, 748, 322, MECH, MECH_D, 1.4, rx=5)                    # handle knob
rect(622, 182, 638, 188, "#d6eefc", "#6aa7cc", 1, rx=3)              # reed

# perfboard edge-on, parts toward the front
rect(660, 360, 667, 530, BOARD, BOARD_D, 1)
rect(667, 368, 697, 380, "#244f9e", "#16336a", 1, rx=4)              # caps
rect(667, 384, 697, 396, "#244f9e", "#16336a", 1, rx=4)
rect(667, 402, 677, 425, CHIP)                                       # MOSFET
rect(677, 402, 680, 425, SILVER)
rect(667, 432, 671, 470, "#6c3fa0")                                  # boost
rect(667, 440, 679, 470, CHIP, rx=1)                                 # XIAO
rect(667, 480, 676, 520, "#7a1f8f")                                  # mic board
rect(676, 488, 690, 512, "#333", rx=3)                               # mic capsule

# side labels
label(576, 194, 606, 228, "Toggle")
label(760, 132, 652, 132, "Servo")
label(760, 160, 671, 140, "Horn + link")
label(760, 186, 638, 185, "Reed switch")
label(760, 232, 655, 245, "Two sticks")
label(760, 306, 748, 306, "Handle (flip by hand)")
label(760, 376, 697, 376, "Capacitors")
label(760, 414, 680, 414, "MOSFET")
label(760, 452, 679, 455, "XIAO on perfboard")
label(760, 500, 690, 500, "Mic → sound holes")
# bottom labels
for px, py, tx, ty, s in ((525, 600, 505, 636, "Wall"), (550, 578, 560, 636, "Faceplate"),
                          (565, 581, 640, 660, "Backplate (Command strips)"), (600, 532, 700, 636, "LiPo battery")):
    line(px, py, tx, ty - 14, LEAD, 0.8)
    circ(px, py, 1.8, LEAD)
    text(tx, ty, s, anchor="middle")

# ================================================================ BOTH SWITCH TYPES
text(1050, 88, "Fits both switch types", 15, "middle", "bold")

# toggle example
text(940, 120, "Toggle", 13, weight="bold")
rect(930, 130, 944, 240, "#ecebe7", "#b9b6ae", 1, rx=2)
path("M944,200 L986,181", SWITCH, 7)
circ(987, 181, 4.5, "#a7acb1", "#5d6166")
rect(978, 165, 1020, 171, MECH, MECH_D, 1, rx=3)
rect(978, 192, 1020, 198, MECH, MECH_D, 1, rx=3)
rect(1020, 150, 1028, 220, MECH, MECH_D, 1, rx=3)
arrow(1040, 160, 1040, 205, MECH_D)
text(1052, 168, "Slider moves", 12)
text(1052, 183, "down: top stick", 12)
text(1052, 198, "pushes the lever", 12)
text(1052, 213, "down. Up: the", 12)
text(1052, 228, "bottom one up.", 12)

# rocker example
text(940, 280, "Rocker (Decora)", 13, weight="bold")
rect(930, 292, 944, 432, "#ecebe7", "#b9b6ae", 1, rx=2)
path("M944,304 L958,304 L948,420 L944,420 Z", "#5d6166", 1, fill="#bfc3c7")
rect(950, 294, 1020, 300, MECH, MECH_D, 1, rx=3)
rect(950, 424, 1020, 430, MECH, MECH_D, 1, rx=3)
rect(1020, 286, 1028, 438, MECH, MECH_D, 1, rx=3)
arrow(1040, 310, 1040, 355, MECH_D)
text(1052, 318, "Sticks sit above", 12)
text(1052, 333, "and below the", 12)
text(1052, 348, "paddle. Sliding", 12)
text(1052, 363, "down, the top stick", 12)
text(1052, 378, "presses the raised", 12)
text(1052, 393, "end in.", 12)

# legend
text(940, 478, "Key", 13, weight="bold")
keys = [(MECH, "Moving parts (printed)"), (SERVO, "Servo"), (BOARD, "Perfboard + parts on it"),
        (SILVER, "Battery"), (SWITCH, "Wall switch"), ("#f7f8f9", "Box shell")]
for i, (c, s) in enumerate(keys):
    y = 492 + i * 22
    rect(940, y, 958, y + 14, c, "#777", 0.8, rx=2)
    text(966, y + 12, s, 12)

# ================================================================ assemble
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 680" width="1200" height="680"
     font-family="Helvetica, Arial, sans-serif">
<defs>
  <marker id="ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
    <path d="M0,0 L10,5 L0,10 z" fill="{MECH_D}"/>
  </marker>
</defs>
<rect width="1200" height="680" fill="#fff"/>
<text x="30" y="38" font-size="22" font-weight="bold" fill="{TXT}">The Switch Flipper: what's inside</text>
<text x="30" y="60" font-size="13" fill="#666">Simplified, not to scale. The servo slides two sticks up and down past the switch. Exact dimensions: layout_2d.svg</text>
{chr(10).join(el)}
</svg>
'''
with open(OUT, "w") as f:
    f.write(svg)
print("wrote", os.path.normpath(OUT))
