#!/usr/bin/env python3
"""Generates docs/schematic.svg. Run from the repo root:  python3 docs/tools/make_schematic.py

Hand-drawn style schematic using net labels: a wire ending in a tag such as
[BAT+] connects to every other tag with the same name.
"""
from pathlib import Path

W, H = 1240, 900
out = []

INK = "#1f2328"
MUTED = "#57606a"
NET_COLORS = {"power": "#cf222e", "signal": "#0969da"}


def add(s):
    out.append(s)


def text(x, y, s, size=13, anchor="start", weight="normal", color=INK, italic=False):
    style = ' font-style="italic"' if italic else ""
    add(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" fill="{color}"{style}>{s}</text>')


def wire(*pts):
    p = " ".join(f"{x},{y}" for x, y in pts)
    add(f'<polyline points="{p}" fill="none" stroke="{INK}" stroke-width="2"/>')


def dot(x, y):
    add(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{INK}"/>')


def panel(x, y, w, h, title):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#f6f8fa" '
        f'stroke="#d0d7de" stroke-width="1.5"/>')
    text(x + 12, y + 22, title, size=14, weight="bold")


def flag(x, y, name, kind="signal", side="left"):
    """Net label whose connecting end is at (x, y).
    side: where the tag sits relative to the wire end (left/right/up/down)."""
    color = NET_COLORS[kind]
    tw = 9 + 7.6 * len(name)
    th = 22
    if side == "left":
        bx, by = x - tw, y - th / 2
    elif side == "right":
        bx, by = x, y - th / 2
    elif side == "up":
        bx, by = x - tw / 2, y - th
    else:  # down
        bx, by = x - tw / 2, y
    add(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{tw:.1f}" height="{th}" rx="4" '
        f'fill="white" stroke="{color}" stroke-width="2"/>')
    text(bx + tw / 2, by + 15.5, name, size=12, anchor="middle", weight="bold", color=color)


def gnd(x, y):
    """Ground symbol hanging below (x, y)."""
    wire((x, y), (x, y + 10))
    for i, half in enumerate((12, 8, 4)):
        yy = y + 10 + i * 5
        add(f'<line x1="{x - half}" y1="{yy}" x2="{x + half}" y2="{yy}" stroke="{INK}" stroke-width="2"/>')


def resistor_v(x, y1, y2, label):
    mid = (y1 + y2) / 2
    wire((x, y1), (x, mid - 18))
    wire((x, mid + 18), (x, y2))
    add(f'<rect x="{x - 7}" y="{mid - 18}" width="14" height="36" fill="white" stroke="{INK}" stroke-width="2"/>')
    text(x + 14, mid + 5, label, size=12)


def cap_v(x, y1, y2, label, polarized=True):
    mid = (y1 + y2) / 2
    wire((x, y1), (x, mid - 4))
    wire((x, mid + 4), (x, y2))
    add(f'<line x1="{x - 13}" y1="{mid - 4}" x2="{x + 13}" y2="{mid - 4}" stroke="{INK}" stroke-width="2.5"/>')
    if polarized:  # curved negative plate
        add(f'<path d="M{x - 13},{mid + 8} Q{x},{mid + 1} {x + 13},{mid + 8}" fill="none" stroke="{INK}" stroke-width="2.5"/>')
        text(x - 22, mid - 8, "+", size=13, weight="bold")
    else:
        add(f'<line x1="{x - 13}" y1="{mid + 4}" x2="{x + 13}" y2="{mid + 4}" stroke="{INK}" stroke-width="2.5"/>')
    lines = label.split("\n")
    for i, l in enumerate(lines):
        text(x + 18, mid + 4 + 15 * (i - (len(lines) - 1) / 2), l, size=12)


def box(x, y, w, h, title, sub=None):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="white" stroke="{INK}" stroke-width="2"/>')
    text(x + w / 2, y + h / 2 - (4 if sub else -5), title, size=13, anchor="middle", weight="bold")
    if sub:
        text(x + w / 2, y + h / 2 + 14, sub, size=11, anchor="middle", color=MUTED)


def pin_label(x, y, s, anchor):
    text(x, y + 4, s, size=11, anchor=anchor, color=MUTED)


add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif">')
add(f'<rect width="{W}" height="{H}" fill="white"/>')
text(20, 28, "The Switch Flipper: wiring schematic", size=20, weight="bold")
text(20, 48, "Tags with the same name are connected. All grounds are common.", size=12, color=MUTED)

# ---------------------------------------------------------------- XIAO
panel(330, 60, 560, 360, "Seeed XIAO ESP32-C3 (U1)")
bx, by, bw, bh = 520, 95, 180, 290
add(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="white" stroke="{INK}" stroke-width="2.5"/>')
text(bx + bw / 2, by + 18, "USB-C", size=11, anchor="middle", color=MUTED)
text(bx + bw / 2, by + bh / 2 - 6, "XIAO", size=16, anchor="middle", weight="bold")
text(bx + bw / 2, by + bh / 2 + 14, "ESP32-C3", size=13, anchor="middle")
text(bx + bw / 2, by + bh / 2 + 32, "(top view)", size=11, anchor="middle", color=MUTED)

left = [("D0", None), ("D1", ("MIC_OUT", "signal")), ("D2", ("VBAT_SENSE", "signal")),
        ("D3", None), ("D4", ("SERVO_SIG", "signal")), ("D5", ("SERVO_EN", "signal")), ("D6", None)]
right = [("5V", None), ("GND", "gnd"), ("3V3", ("3V3", "power")), ("D10", ("REED", "signal")),
         ("D9", None), ("D8", ("LED_K", "signal")), ("D7", None)]
for i, (pin, net) in enumerate(left):
    y = by + 40 + i * 37
    pin_label(bx + 6, y, pin, "start")
    if net:
        wire((bx, y), (bx - 50, y))
        flag(bx - 50, y, net[0], net[1], "left")
    else:
        wire((bx, y), (bx - 14, y))
        text(bx - 18, y + 4, "nc", size=11, anchor="end", color=MUTED, italic=True)
for i, (pin, net) in enumerate(right):
    y = by + 40 + i * 37
    pin_label(bx + bw - 6, y, pin, "end")
    if net == "gnd":
        wire((bx + bw, y), (bx + bw + 30, y))
        gnd(bx + bw + 30, y)
    elif net:
        wire((bx + bw, y), (bx + bw + 50, y))
        flag(bx + bw + 50, y, net[0], net[1], "right")
    else:
        wire((bx + bw, y), (bx + bw + 14, y))
        text(bx + bw + 18, y + 4, "nc" if pin != "5V" else "nc (bench tests: servo +)", size=11,
             color=MUTED, italic=True)
# battery pads on the underside
for px, name in ((bx + 60, "BAT+"), (bx + 120, "BAT−")):
    add(f'<rect x="{px - 9}" y="{by + bh - 14}" width="18" height="10" fill="#d4a72c"/>')
pin_label(bx + 60, by + bh - 22, "BAT+", "middle")
pin_label(bx + 120, by + bh - 22, "BAT−", "middle")
wire((bx + 60, by + bh), (bx + 60, by + bh + 14))
flag(bx + 60, by + bh + 14, "BAT+", "power", "down")
wire((bx + 120, by + bh), (bx + 120, by + bh + 8))
gnd(bx + 120, by + bh + 8)
text(bx + bw + 14, by + bh + 2, "pads on the underside;", size=11, color=MUTED)
text(bx + bw + 14, by + bh + 16, "XIAO charges the LiPo over USB-C", size=11, color=MUTED)

# ---------------------------------------------------------------- Battery sense
panel(20, 60, 290, 200, "Battery sense")
x = 80
wire((x, 120), (x, 125))
flag(x, 120, "BAT+", "power", "up")
resistor_v(x, 125, 170, "R1 220 kΩ")
dot(x, 170)
wire((x, 170), (x + 95, 170))
flag(x + 95, 170, "VBAT_SENSE", "signal", "right")
resistor_v(x, 170, 215, "R2 220 kΩ")
gnd(x, 215)
text(175, 210, "D2 reads half the", size=11, color=MUTED)
text(175, 224, "battery voltage", size=11, color=MUTED)

# ---------------------------------------------------------------- Microphone
panel(20, 275, 290, 145, "Microphone")
box(40, 305, 110, 85, "MAX4466", "M1")
for yy, name, net in ((325, "VCC", ("3V3", "power")), (365, "OUT", ("MIC_OUT", "signal"))):
    pin_label(144, yy, name, "end")
    wire((150, yy), (185, yy))
    flag(185, yy, net[0], net[1], "right")
pin_label(95, 383, "GND", "middle")
wire((95, 390), (95, 395))
gnd(95, 395)
text(165, 405, "gain screw on back", size=11, color=MUTED)

# ---------------------------------------------------------------- Servo power
panel(20, 440, 930, 440, "Servo power (only on while moving)")
# battery
bx0 = 75
wire((bx0, 520), (bx0, 545))
for i, (half, yy) in enumerate(((20, 545), (10, 553), (20, 561), (10, 569))):
    add(f'<line x1="{bx0 - half}" y1="{yy}" x2="{bx0 + half}" y2="{yy}" stroke="{INK}" stroke-width="2.5"/>')
text(bx0 - 32, 545, "+", size=14, weight="bold")
wire((bx0, 569), (bx0, 600))
gnd(bx0, 600)
text(bx0 - 45, 650, "BT1  LiPo 3.7 V", size=12)
text(bx0 - 45, 665, "1000 mAh, protected", size=11, color=MUTED)
# BAT+ rail
wire((bx0, 520), (bx0, 510), (310, 510))
dot(150, 510)
wire((150, 510), (150, 498))
flag(150, 498, "BAT+", "power", "up")
dot(215, 510)
cap_v(215, 510, 600, "C1\n220–470 µF")
gnd(215, 600)
# boost converter
box(310, 490, 150, 100, "Boost 5 V", "U2 · TPS61023 / Pololu")
pin_label(316, 510, "VIN", "start")
pin_label(454, 510, "VOUT", "end")
pin_label(345, 578, "EN", "middle")
pin_label(425, 578, "GND", "middle")
wire((345, 590), (345, 620))
flag(345, 620, "SERVO_EN", "signal", "down")
wire((425, 590), (425, 605))
gnd(425, 605)
# VOUT rail
wire((460, 510), (650, 510))
dot(545, 510)
cap_v(545, 510, 600, "C2 470 µF\nclose to servo")
gnd(545, 600)
# servo
box(650, 490, 140, 100, "MG90S servo", "M2")
pin_label(656, 510, "red +", "start")
pin_label(784, 510, "orange", "end")
pin_label(720, 582, "brown −", "middle")
wire((790, 510), (815, 510))
flag(815, 510, "SERVO_SIG", "signal", "right")
# MOSFET (low-side switch)
mx, my = 720, 690
wire((720, 590), (720, my - 30))
add(f'<rect x="{mx - 50}" y="{my - 30}" width="100" height="70" rx="6" fill="white" stroke="{INK}" stroke-width="2"/>')
text(mx + 2, my + 2, "Q1", size=13, anchor="middle", weight="bold")
text(mx + 2, my + 18, "FQP30N06L", size=11, anchor="middle", color=MUTED)
pin_label(mx, my - 20, "D", "middle")
pin_label(mx - 42, my + 5, "G", "start")
pin_label(mx, my + 32, "S", "middle")
wire((mx, my + 40), (mx, my + 60))
gnd(mx, my + 60)
wire((mx - 50, my + 5), (600, my + 5))
dot(600, my + 5)
resistor_v(600, my + 5, my + 85, "R3 100 kΩ")
gnd(600, my + 85)
wire((600, my + 5), (560, my + 5))
flag(560, my + 5, "SERVO_EN", "signal", "left")
text(800, 690, "N-channel, logic level,", size=11, color=MUTED)
text(800, 704, "low-side switch: cuts the", size=11, color=MUTED)
text(800, 718, "servo fully off when idle", size=11, color=MUTED)
text(40, 850, "D5 drives the boost EN and the MOSFET gate together. Keep the MOSFET: many boosts pass", size=11, color=MUTED)
text(40, 865, "battery voltage through when disabled. R3 keeps the servo off while the XIAO boots.", size=11, color=MUTED)

# ---------------------------------------------------------------- Reed switch
panel(970, 440, 250, 190, "Carriage position")
rx = 1040
wire((rx, 497), (rx, 515))
flag(rx, 497, "REED", "signal", "up")
add(f'<rect x="{rx - 14}" y="515" width="28" height="60" rx="14" fill="white" stroke="{INK}" stroke-width="2"/>')
wire((rx, 515), (rx, 538))
add(f'<line x1="{rx}" y1="555" x2="{rx + 8}" y2="538" stroke="{INK}" stroke-width="2"/>')
wire((rx, 555), (rx, 590))
gnd(rx, 590)
text(rx + 24, 530, "S1 reed switch", size=12)
text(rx + 24, 548, "closed = magnet", size=11, color=MUTED)
text(rx + 24, 562, "near = carriage up", size=11, color=MUTED)
text(rx + 24, 576, "internal pull-up", size=11, color=MUTED)

# ---------------------------------------------------------------- LED
panel(970, 650, 250, 230, "Status LED")
lx = 1040
wire((lx, 707), (lx, 712))
flag(lx, 707, "3V3", "power", "up")
resistor_v(lx, 712, 765, "R4 1 kΩ")
wire((lx, 765), (lx, 775))
add(f'<polygon points="{lx - 12},775 {lx + 12},775 {lx},795" fill="white" stroke="{INK}" stroke-width="2"/>')
add(f'<line x1="{lx - 12}" y1="795" x2="{lx + 12}" y2="795" stroke="{INK}" stroke-width="2"/>')
for dx in (0, 8):
    add(f'<line x1="{lx + 16 + dx}" y1="{780 + dx / 2}" x2="{lx + 26 + dx}" y2="{772 + dx / 2}" stroke="{INK}" stroke-width="1.5"/>')
wire((lx, 795), (lx, 820))
flag(lx, 820, "LED_K", "signal", "down")
text(lx + 44, 790, "D1 LED", size=12)
text(lx + 44, 806, "on when D8", size=11, color=MUTED)
text(lx + 44, 820, "is LOW", size=11, color=MUTED)

# ---------------------------------------------------------------- Notes
panel(910, 60, 310, 360, "Notes")
notes = [
    "Avoid D0, D8*, D9 for inputs: they are",
    "ESP32-C3 strapping pins. (*D8 only",
    "drives the LED, which is safe.)",
    "",
    "Analog needs ADC1 pins (D0–D2 on the",
    "C3): mic on D1, battery sense on D2.",
    "",
    "Servo current comes from the battery",
    "through the boost, never from 3V3.",
    "",
    "C1/C2 go on the supply side of the",
    "servo, not after the MOSFET.",
    "",
    "Bench tests (docs/testing.md) power the",
    "servo from the XIAO 5V pin over USB.",
    "",
    "Check pins against your board's",
    "pinout card before soldering.",
]
for i, n in enumerate(notes):
    text(926, 108 + i * 17, n, size=12, color=INK if n else MUTED)

add("</svg>")
Path(__file__).resolve().parents[1].joinpath("schematic.svg").write_text("\n".join(out), encoding="utf-8")
print("wrote docs/schematic.svg")
