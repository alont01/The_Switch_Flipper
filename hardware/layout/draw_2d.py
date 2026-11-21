#!/usr/bin/env python3
"""Draws dimensioned 2D layout views from layout.py into docs/layout_2d.svg.

Run from anywhere with plain Python 3:  python3 hardware/layout/draw_2d.py
"""
import math
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout as L  # noqa: E402

OUT = HERE.parents[1] / "docs" / "layout_2d.svg"
S = 4.2            # px per mm
INK, MUTED, DIM = "#1f2328", "#57606a", "#0969da"
out = []


def add(s):
    out.append(s)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=12, anchor="start", weight="normal", color=INK):
    add(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" '
        f'font-weight="{weight}" fill="{color}">{esc(s)}</text>')


# ------------------------------------------------------------------ geometry
def prim_points(p):
    if p["t"] == "box":
        (x, y, z), (dx, dy, dz) = p["p"], p["s"]
        return [(x + i * dx, y + j * dy, z + k * dz) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    (x, y, z), d, r = p["p"], p["d"], p["r"]
    n = math.sqrt(sum(c * c for c in d))
    a = [c / n for c in d]
    ref = (1, 0, 0) if abs(a[0]) < 0.9 else (0, 1, 0)
    u = (a[1] * ref[2] - a[2] * ref[1], a[2] * ref[0] - a[0] * ref[2], a[0] * ref[1] - a[1] * ref[0])
    un = math.sqrt(sum(c * c for c in u))
    u = [c / un for c in u]
    v = (a[1] * u[2] - a[2] * u[1], a[2] * u[0] - a[0] * u[2], a[0] * u[1] - a[1] * u[0])
    pts = []
    for end in (0, 1):
        cx, cy, cz = x + d[0] * end, y + d[1] * end, z + d[2] * end
        for i in range(20):
            t = 2 * math.pi * i / 20
            c, s = math.cos(t) * r, math.sin(t) * r
            pts.append((cx + c * u[0] + s * v[0], cy + c * u[1] + s * v[1], cz + c * u[2] + s * v[2]))
    return pts


def hull(pts):
    pts = sorted(set((round(a, 3), round(b, 3)) for a, b in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


VIEWS = {
    # name: (project 3D->2D in mm with screen y down, depth key: larger = nearer the viewer)
    "front": (lambda q: (q[0], -q[2]), lambda q: q[1]),
    "side": (lambda q: (q[1], -q[2]), lambda q: q[0]),
    "top": (lambda q: (q[0], q[1]), lambda q: q[2]),
}


def hexcol(c):
    return "#%02x%02x%02x" % tuple(int(255 * v) for v in c)


def darker(c, f=0.55):
    return hexcol(tuple(v * f for v in c))


def draw_view(view, ox, oy, include, section_z=None, fill_alpha=None):
    """Draws the parts with origin (0,0,0) at screen (ox, oy). Returns label anchors."""
    proj, depth = VIEWS[view]
    items = []
    anchors = {}
    for prt in L.parts:
        if not include(prt):
            continue
        for p in prt["prims"]:
            pts = prim_points(p)
            if section_z is not None:
                zs = [q[2] for q in pts]
                if not (min(zs) <= section_z <= max(zs)):
                    continue
            d = sum(depth(q) for q in pts) / len(pts)
            if section_z is None and view != "top":
                d = max(depth(q) for q in pts) * 0.5 + d * 0.5
            poly = hull([proj(q) for q in pts])
            items.append((d, prt, poly))
            if prt["label"]:
                anchors.setdefault(prt["label"], []).extend(poly)
    items.sort(key=lambda t: t[0])
    for d, prt, poly in items:
        a = prt["alpha"] if fill_alpha is None else fill_alpha(prt)
        pts = " ".join(f"{ox + u * S:.1f},{oy + v * S:.1f}" for u, v in poly)
        add(f'<polygon points="{pts}" fill="{hexcol(prt["color"])}" fill-opacity="{a:.2f}" '
            f'stroke="{darker(prt["color"])}" stroke-width="0.8" stroke-linejoin="round"/>')
    res = {}
    for lab, pts in anchors.items():
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        res[lab] = (ox + (min(xs) + max(xs)) / 2 * S, oy + (min(ys) + max(ys)) / 2 * S)
    return res


def callouts(anchors, wanted, x_left, x_right, mid_x, y_min, y_max):
    """Labels in two columns with leader lines, spread so they don't overlap."""
    left = sorted([(anchors[w][1], w) for w in wanted if w in anchors and anchors[w][0] < mid_x])
    right = sorted([(anchors[w][1], w) for w in wanted if w in anchors and anchors[w][0] >= mid_x])
    for col, xcol, anchor in ((left, x_left, "end"), (right, x_right, "start")):
        ys = [y for y, _ in col]
        for i in range(1, len(ys)):
            ys[i] = max(ys[i], ys[i - 1] + 18)
        over = (ys[-1] - y_max) if ys else 0
        if over > 0:
            ys = [y - over for y in ys]
            for i in range(len(ys) - 2, -1, -1):
                ys[i] = min(ys[i], ys[i + 1] - 18)
        for (ay, w), ly in zip(col, ys):
            axp, ayp = anchors[w]
            tx = xcol + (-6 if anchor == "end" else 6)
            add(f'<polyline points="{xcol:.1f},{ly:.1f} {axp:.1f},{ayp:.1f}" fill="none" '
                f'stroke="{MUTED}" stroke-width="0.9"/>')
            add(f'<circle cx="{axp:.1f}" cy="{ayp:.1f}" r="2.2" fill="{MUTED}"/>')
            text(tx, ly + 4, w, size=12, anchor=anchor)


def dim_h(x0, x1, y, label, ext_from=None):
    add(f'<line x1="{x0:.1f}" y1="{y:.1f}" x2="{x1:.1f}" y2="{y:.1f}" stroke="{DIM}" stroke-width="1" '
        f'marker-start="url(#a)" marker-end="url(#a)"/>')
    if ext_from is not None:
        for x in (x0, x1):
            add(f'<line x1="{x:.1f}" y1="{ext_from:.1f}" x2="{x:.1f}" y2="{y + (4 if y > ext_from else -4):.1f}" '
                f'stroke="{DIM}" stroke-width="0.6" stroke-dasharray="3 2"/>')
    text((x0 + x1) / 2, y - 5, label, size=12, anchor="middle", color=DIM, weight="bold")


def dim_v(x, y0, y1, label, ext_from=None, side="left"):
    add(f'<line x1="{x:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y1:.1f}" stroke="{DIM}" stroke-width="1" '
        f'marker-start="url(#a)" marker-end="url(#a)"/>')
    if ext_from is not None:
        for y in (y0, y1):
            add(f'<line x1="{ext_from:.1f}" y1="{y:.1f}" x2="{x + (4 if x > ext_from else -4):.1f}" y2="{y:.1f}" '
                f'stroke="{DIM}" stroke-width="0.6" stroke-dasharray="3 2"/>')
    ty = (y0 + y1) / 2
    tx = x - 6 if side == "left" else x + 6
    add(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="12" font-weight="bold" fill="{DIM}" '
        f'text-anchor="middle" transform="rotate(-90 {tx:.1f} {ty:.1f})">{esc(label)}</text>')


def panel(x, y, w, h, title, sub):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#ffffff" stroke="#d0d7de"/>')
    text(x + 14, y + 24, title, size=15, weight="bold")
    text(x + 14, y + 42, sub, size=11, color=MUTED)


# ------------------------------------------------------------------ page
W, H = 1600, 1320
add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
    f'font-family="-apple-system, Segoe UI, Helvetica, Arial, sans-serif">')
add('<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" '
    'orient="auto-start-reverse"><path d="M0,2 L10,5 L0,8 z" fill="#0969da"/></marker></defs>')
add(f'<rect width="{W}" height="{H}" fill="#f6f8fa"/>')
text(24, 36, "The Switch Flipper: 2D layout", size=22, weight="bold")
text(24, 58, f"Front and side views at {S:g} px/mm, sections at 7 px/mm. Switch shown UP. Generated from hardware/layout/layout.py; "
     "component sizes are typical values, measure your own parts.", size=12, color=MUTED)

BOX = L.DIMENSIONS
LABELS_MAIN = ["MG90S servo", "Horn / crank", "Link rod", "Carriage + fork", "Handle", "Magnet", "Reed switch",
               "MAX4466 mic", "Perfboard", "XIAO ESP32-C3", "USB-C (charging)", "Boost 5 V", "MOSFET",
               "470 µF caps", "Resistors", "LiPo 1000 mAh", "Wi-Fi antenna", "Status LED", "Servo bulkhead",
               "Backplate", "Toggle"]

# ---------------- front view (cover removed)
px, py, pw, ph = 20, 80, 760, 670
panel(px, py, pw, ph, "Front view, cover removed", "Looking at the wall. Front wall and handle knob not drawn.")
ox, oy = px + pw / 2, py + 90 + 57 * S
inc_front = lambda p: p["name"] not in ("Wall", "Shell front", "Handle", "Command strips")
anchors = draw_view("front", ox, oy, inc_front,
                    fill_alpha=lambda p: 0.5 if p["group"] == "shell" else (0.35 if p["name"].startswith("Face") else p["alpha"]))
# plate + box outlines
add(f'<rect x="{ox - L.PLATE_W / 2 * S:.1f}" y="{oy - L.PLATE_H / 2 * S:.1f}" width="{L.PLATE_W * S:.1f}" '
    f'height="{L.PLATE_H * S:.1f}" fill="none" stroke="{MUTED}" stroke-dasharray="6 4"/>')
text(ox + L.PLATE_W / 2 * S - 4, oy - L.PLATE_H / 2 * S - 6, "faceplate / backplate 70 × 114", size=11,
     anchor="end", color=MUTED)
bx0, bx1 = ox - BOX["box_w"] / 2 * S, ox + BOX["box_w"] / 2 * S
bz0, bz1 = oy - L.BOX_Z1 * S, oy - L.BOX_Z0 * S
add(f'<line x1="{ox - 30 * S:.1f}" y1="{oy:.1f}" x2="{ox + 30 * S:.1f}" y2="{oy:.1f}" stroke="{MUTED}" '
    f'stroke-dasharray="10 3 2 3" stroke-width="0.8"/>')
text(ox + 30 * S + 4, oy + 4, "toggle centre", size=10, color=MUTED)
dim_h(bx0, bx1, bz1 + 30, f"{BOX['box_w']:g}", ext_from=bz1)
dim_v(bx0 - 34, bz0, bz1, f"{BOX['box_h']:g}", ext_from=bx0)
dim_v(bx1 + 26, oy - L.z_c * S - L.CAR_HALF_H * S, oy - L.z_c * S + L.CAR_HALF_H * S,
      "carriage 22", ext_from=bx1 - 3 * S, side="right")
callouts(anchors, LABELS_MAIN, px + 150, px + pw - 150, ox, py + 60, py + ph - 20)

# ---------------- side view (right wall removed)
sx, sy, sw, sh = 800, 80, 780, 670
panel(sx, sy, sw, sh, "Side view, right wall removed", "Wall on the left, you on the right.")
ox2, oy2 = sx + 300, oy
inc_side = lambda p: p["name"] not in ("Wall", "Shell right wall")
anchors2 = draw_view("side", ox2, oy2, inc_side,
                     fill_alpha=lambda p: 0.45 if p["group"] == "shell" else p["alpha"])
add(f'<rect x="{ox2 - 9 * S:.1f}" y="{oy2 - 62 * S:.1f}" width="{4 * S:.1f}" height="{130 * S:.1f}" '
    f'fill="#e9e2d0" stroke="#b8ae96"/>')
text(ox2 - 7 * S, oy2 + 72 * S, "wall", size=11, anchor="middle", color=MUTED)
yb0, yb1 = ox2 + L.BOX_Y0 * S, ox2 + L.BOX_Y1 * S
dim_h(yb0, yb1, bz1 + 30, f"box {BOX['box_d']:g}", ext_from=bz1)
dim_h(ox2, yb1, bz1 + 58, f"{BOX['standoff']:g} from faceplate", ext_from=bz1)
dim_h(ox2, ox2 + BOX["handle_out"] * S, bz0 - 40, f"{BOX['handle_out']:g} to handle", ext_from=bz0)
dim_v(yb1 + 60, oy2 - (L.z_c + 3) * S, oy2 - (L.z_c + 3 - BOX["travel"]) * S,
      f"travel {BOX['travel']:.1f}", ext_from=yb1 + 34, side="right")
callouts(anchors2, LABELS_MAIN + ["Command strips", "Faceplate"], sx + 120, sx + sw - 150, ox2 + 20 * S,
         sy + 60, sy + ph - 20)

# ---------------- sections looking down
for i, (zc, title, sub) in enumerate((
        (L.SHAFT_Z, f"Section A–A at servo shaft (z = {L.SHAFT_Z:g})", "Looking down. Wall at the top, you at the bottom."),
        (-45.0, "Section B–B through the electronics bay (z = −45)", "Looking down. Battery, perfboard, XIAO and boost; the mic sits higher."))):
    S = 7.0
    qx, qy, qw, qh = 20 + i * 790, 770, 770, 530
    panel(qx, qy, qw, qh, title, sub)
    ox3, oy3 = qx + qw / 2 - 40, qy + 130
    anch = draw_view("top", ox3, oy3, lambda p: p["name"] != "Wall", section_z=zc,
                     fill_alpha=lambda p: 0.5 if p["group"] == "shell" else p["alpha"])
    dim_h(ox3 - BOX["box_w"] / 2 * S, ox3 + BOX["box_w"] / 2 * S, oy3 + L.BOX_Y1 * S + 40,
          f"{BOX['box_w']:g}", ext_from=oy3 + L.BOX_Y1 * S)
    dim_v(ox3 + BOX["box_w"] / 2 * S + 40, oy3 + L.BOX_Y0 * S, oy3 + L.BOX_Y1 * S, f"{BOX['box_d']:g}",
          ext_from=ox3 + BOX["box_w"] / 2 * S, side="right")
    callouts(anch, LABELS_MAIN + ["Faceplate", "Command strips"], qx + 170, qx + qw - 150, ox3,
             qy + 70, qy + qh - 30)
    text(ox3, oy3 - 2 * S - 12 - L.PLATE_T * S, "wall side", size=11, anchor="middle", color=MUTED)
    text(ox3, oy3 + L.BOX_Y1 * S + 72, "front (sound holes, handle, LED)", size=11, anchor="middle", color=MUTED)

add("</svg>")
OUT.write_text("\n".join(out), encoding="utf-8")
print("wrote", OUT.relative_to(HERE.parents[1]))
