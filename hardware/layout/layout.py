"""Physical layout of The Switch Flipper: every part as simple solids.

One source of truth for both the 3D model (build_3d.py, run in FreeCAD) and
the 2D drawings (draw_2d.py, plain Python).

Coordinates (mm), shown in the 3D model and the drawings:
  x  across the switch, + to the right when facing the wall
  y  out of the wall, 0 = faceplate surface, + toward you
  z  up, 0 = centre of the toggle

Component sizes are typical datasheet values. Measure your own parts
(especially the battery and your toggle) and change the numbers below.
"""
from math import cos, sin, radians

# ------------------------------------------------------------------ parameters
PLATE_W, PLATE_H, PLATE_T = 70.0, 114.0, 5.0       # US single toggle faceplate
STRIP_T = 1.5                                       # Command strip thickness
BP_T = 2.0                                          # backplate thickness
BP_Y0 = STRIP_T
BP_Y1 = BP_Y0 + BP_T                                # 3.5

BOX_W = 44.0                                        # fits 46 mm multi-gang pitch
WALL = 2.0
BOX_Y0, BOX_Y1 = BP_Y1, 38.0                        # box depth 34.5
BOX_Z0, BOX_Z1 = -63.0, 37.0                        # box height 100
IX = BOX_W / 2 - WALL                               # inner half width, 20
FRONT_IN = BOX_Y1 - WALL                            # inner face of front wall, 36
TOP_IN, BOT_IN = BOX_Z1 - WALL, BOX_Z0 + WALL       # 35, -61

TOGGLE_LEN, TOGGLE_ANGLE = 13.0, 25.0               # lever length, tilt (deg)

# Servo: MG90S, lying with its shaft pointing out of the box front.
SERVO_L, SERVO_W, SERVO_H = 22.8, 12.2, 22.7        # case
SERVO_TAB_SPAN, SERVO_TAB_FROM_BOTTOM, SERVO_TAB_T = 32.5, 15.9, 2.5
SERVO_SHAFT_FROM_END = 5.9
SHAFT_X, SHAFT_Z = -2.0, 26.5
SERVO_Y0 = 4.0                                      # back of the servo case
CRANK_R = 6.5                                       # horn hole radius used
CRANK_SWING = 60.0                                  # +-deg -> +-5.6 mm travel
LINK_L = 17.6

# Carriage (slides up and down). State drawn: switch UP.
import os as _os
STATE_UP = _os.environ.get("SF_STATE", "up") != "down"
CAR_HALF_H = 11.0
CAR_X = 17.5                                        # half width
CAR_Y0, CAR_Y1 = 5.0, 32.5
FORK_GAP = 4.0                                      # half gap between prongs

# Battery: 803040 1000 mAh LiPo (8 x 30 x 40). Measure yours.
BAT_T, BAT_W, BAT_L = 8.0, 30.0, 40.0

# ------------------------------------------------------------------ helpers
parts = []


def B(x0, x1, y0, y1, z0, z1):
    return {"t": "box", "p": (min(x0, x1), min(y0, y1), min(z0, z1)),
            "s": (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0))}


def C(p, d, r):
    """Cylinder from point p along vector d (its length is the height)."""
    return {"t": "cyl", "p": tuple(p), "d": tuple(d), "r": r}


def part(name, group, color, prims, alpha=1.0, cuts=(), label=None):
    parts.append({"name": name, "group": group, "color": color, "alpha": alpha,
                  "prims": list(prims), "cuts": list(cuts), "label": label})


def wire(name, color, pts, r=0.55):
    prims = [C(a, (b[0] - a[0], b[1] - a[1], b[2] - a[2]), r) for a, b in zip(pts, pts[1:])]
    part(name, "wires", color, prims)


# colours (r, g, b) 0-1
WHITE = (0.96, 0.96, 0.94)
IVORY = (0.93, 0.90, 0.82)
GREY = (0.70, 0.71, 0.73)
ORANGE = (0.95, 0.52, 0.12)
BLUE = (0.18, 0.35, 0.75)
BLACK = (0.13, 0.13, 0.14)
SILVER = (0.78, 0.79, 0.80)
PCB_GREEN = (0.12, 0.45, 0.25)
PERF = (0.78, 0.62, 0.35)
PURPLE = (0.45, 0.25, 0.60)
TEAL = (0.10, 0.55, 0.60)
GOLD = (0.83, 0.65, 0.17)
RED = (0.85, 0.12, 0.12)
BROWN = (0.45, 0.25, 0.10)
YELLOW = (0.95, 0.80, 0.10)
GLASS = (0.65, 0.85, 0.90)
WALL_C = (0.88, 0.84, 0.76)

# ------------------------------------------------------------------ wall + switch
part("Wall", "wall", WALL_C, [B(-60, 60, -9, -PLATE_T, -80, 75)], alpha=0.35)
part("Faceplate (US toggle)", "wall", IVORY,
     [B(-PLATE_W / 2, PLATE_W / 2, -PLATE_T, 0, -PLATE_H / 2, PLATE_H / 2)],
     cuts=[B(-5, 5, -PLATE_T - 1, 1, -12, 12)], label="Faceplate")
part("Switch body", "wall", BLACK, [B(-5, 5, -PLATE_T, 0.5, -12, 12)])
a = radians(TOGGLE_ANGLE if STATE_UP else -TOGGLE_ANGLE)
lever_tip = (0, TOGGLE_LEN * cos(a), TOGGLE_LEN * sin(a))
part("Toggle lever", "wall", IVORY, [C((0, 0, 0), lever_tip, 2.6)], label="Toggle")

# ------------------------------------------------------------------ mount
part("Command strips", "mount", (0.95, 0.95, 0.95),
     [B(14, 30, 0, STRIP_T, -35, 35), B(-30, -14, 0, STRIP_T, -35, 35)], alpha=0.6,
     label="Command strips")
part("Backplate", "mount", GREY,
     [B(-PLATE_W / 2, PLATE_W / 2, BP_Y0, BP_Y1, -PLATE_H / 2, PLATE_H / 2),
      B(-18, 18, BP_Y1, BP_Y1 + 3, BOX_Z1, BOX_Z1 + 3)],          # top ridge the box hangs on
     cuts=[B(-12, 12, BP_Y0 - 1, BP_Y1 + 1, -20, 20)], label="Backplate")

# ------------------------------------------------------------------ shell
shell_c = WHITE
part("Shell left wall", "shell", shell_c, [B(-BOX_W / 2, -IX, BOX_Y0, BOX_Y1, BOX_Z0, BOX_Z1)], alpha=0.25)
part("Shell right wall", "shell", shell_c, [B(IX, BOX_W / 2, BOX_Y0, BOX_Y1, BOX_Z0, BOX_Z1)], alpha=0.25)
part("Shell top", "shell", shell_c, [B(-IX, IX, BOX_Y0, BOX_Y1, TOP_IN, BOX_Z1),
                                      B(-18, 18, BP_Y1 + 3, BP_Y1 + 4.5, BOX_Z1, BOX_Z1 + 4.5),
                                      B(-18, 18, BP_Y1, BP_Y1 + 4.5, BOX_Z1 + 3, BOX_Z1 + 4.5)],  # hook over ridge
     alpha=0.25)
part("Shell bottom", "shell", shell_c,
     [B(-IX, IX, BOX_Y0, BOX_Y1, BOX_Z0, BOT_IN),
      B(-8, 8, 0.5, BOX_Y0, -PLATE_H / 2 - 2, -PLATE_H / 2)],    # click latch under plate edge
     alpha=0.25, cuts=[B(-12.6, -1.6, 15.5, 22.5, BOX_Z0 - 1, BOT_IN + 1)])  # USB-C opening
z_c = (CRANK_R * sin(radians(CRANK_SWING))) * (1 if STATE_UP else -1)  # carriage centre
slot_half = CRANK_R * sin(radians(CRANK_SWING)) + 3.5
MIC_Z = -25.1
front_cuts = [B(-3.5, 3.5, FRONT_IN - 1, BOX_Y1 + 1, -slot_half, slot_half),        # handle slot
              C((-15, FRONT_IN - 1, 30), (0, WALL + 2, 0), 1.6)]                     # LED hole
for dx, dz in ((0, 0), (-2.6, 0), (2.6, 0), (0, -2.6), (0, 2.6)):                    # sound holes
    front_cuts.append(C((dx, FRONT_IN - 1, MIC_Z + dz), (0, WALL + 2, 0), 0.8))
part("Shell front", "shell", shell_c, [B(-IX, IX, FRONT_IN, BOX_Y1, BOT_IN, TOP_IN)], alpha=0.25,
     cuts=front_cuts)
# guide ribs for the carriage, and the servo bulkhead
part("Carriage guide ribs", "shell", WHITE,
     [B(s * (CAR_X + 0.1), s * IX, y0, y0 + 2, -19, 19) for s in (-1, 1) for y0 in (7, 26)])
sv_x = SHAFT_X - SERVO_SHAFT_FROM_END + SERVO_L / 2          # servo case centre x
sv_z0, sv_z1 = SHAFT_Z - SERVO_W / 2, SHAFT_Z + SERVO_W / 2
tab_y = SERVO_Y0 + SERVO_TAB_FROM_BOTTOM
part("Servo bulkhead", "shell", WHITE,
     [B(-IX, IX, tab_y - 2.5, tab_y, 19, TOP_IN)],
     cuts=[B(sv_x - SERVO_L / 2 - 0.3, sv_x + SERVO_L / 2 + 0.3, tab_y - 4, tab_y + 1, sv_z0 - 0.3, sv_z1 + 0.3)],
     label="Servo bulkhead")

# ------------------------------------------------------------------ servo + linkage
part("MG90S servo", "servo", BLUE,
     [B(sv_x - SERVO_L / 2, sv_x + SERVO_L / 2, SERVO_Y0, SERVO_Y0 + SERVO_H, sv_z0, sv_z1),
      B(sv_x - SERVO_TAB_SPAN / 2, sv_x + SERVO_TAB_SPAN / 2, tab_y, tab_y + SERVO_TAB_T, sv_z0, sv_z1),
      C((SHAFT_X, SERVO_Y0 + SERVO_H, SHAFT_Z), (0, 4.0, 0), 5.9),
      C((SHAFT_X + 5, SERVO_Y0 + SERVO_H, SHAFT_Z), (0, 2.5, 0), 3.0)],
     label="MG90S servo")
shaft_top = SERVO_Y0 + SERVO_H + 4.0
part("Servo shaft", "servo", SILVER, [C((SHAFT_X, shaft_top, SHAFT_Z), (0, 0.25, 0), 2.4)])
th = radians(CRANK_SWING if STATE_UP else -CRANK_SWING)
pin = (SHAFT_X + CRANK_R * cos(th), SHAFT_Z + CRANK_R * sin(th))
horn_y = shaft_top + 0.3
part("Servo horn (crank)", "mechanism", WHITE,
     [C((SHAFT_X, horn_y, SHAFT_Z), (0, 2.0, 0), 3.5),
      C((SHAFT_X, horn_y + 1.0, SHAFT_Z), (pin[0] - SHAFT_X, 0, pin[1] - SHAFT_Z), 1.0),
      C((pin[0], horn_y, pin[1]), (0, 2.0, 0), 2.3)], label="Horn / crank")
car_pin = (3.0, z_c + 9.0)
link_y = horn_y + 2.3
part("Link rod", "mechanism", ORANGE,
     [C((pin[0], link_y + 0.7, pin[1]), (car_pin[0] - pin[0], 0, car_pin[1] - pin[1]), 1.0),
      C((pin[0], link_y, pin[1]), (0, 1.4, 0), 2.0),
      C((car_pin[0], link_y, car_pin[1]), (0, 1.4, 0), 2.0),
      C((car_pin[0], CAR_Y1 + 0.05, car_pin[1]), (0, link_y - CAR_Y1 - 0.05, 0), 1.0)], label="Link rod")

# ------------------------------------------------------------------ carriage
zc0, zc1 = z_c - CAR_HALF_H, z_c + CAR_HALF_H
part("Carriage", "mechanism", ORANGE,
     [B(-CAR_X, -CAR_X + 2.5, CAR_Y0, CAR_Y1, zc0, zc1),
      B(CAR_X - 2.5, CAR_X, CAR_Y0, CAR_Y1, zc0, zc1),
      B(-CAR_X, CAR_X, CAR_Y1 - 3.5, CAR_Y1, zc0, zc1),
      B(-CAR_X, CAR_X, 14, 17, z_c - 4 - 2.5, z_c + 4 + 2.5),
      B(-4, 4, 10, 14, z_c + FORK_GAP, z_c + FORK_GAP + 2.5),          # upper prong
      B(-4, 4, 10, 14, z_c - FORK_GAP - 2.5, z_c - FORK_GAP)],         # lower prong
     cuts=[C((12, CAR_Y1 - 2.0, z_c - 8), (0, 2.5, 0), 2.6)], label="Carriage + fork")
part("Handle", "mechanism", ORANGE,
     [B(-3, 3, CAR_Y1, BOX_Y1 + 2, z_c - 3, z_c + 3),
      B(-7, 7, BOX_Y1 + 2, BOX_Y1 + 8, z_c - 8, z_c + 8)], label="Handle")
part("Magnet 5x2 mm", "mechanism", SILVER, [C((12, CAR_Y1 - 2.0, z_c - 8), (0, 2.0, 0), 2.5)],
     label="Magnet")
reed_z = CRANK_R * sin(radians(CRANK_SWING)) - 8          # magnet height when UP
part("Reed switch", "electronics", GLASS,
     [C((6, FRONT_IN - 1.3, reed_z), (12, 0, 0), 1.1),
      C((3.5, FRONT_IN - 1.3, reed_z), (2.5, 0, 0), 0.3),
      C((18, FRONT_IN - 1.3, reed_z), (1.6, 0, 0), 0.3)], label="Reed switch")

# ------------------------------------------------------------------ lower bay
BAT_Z1 = -20.0
part("LiPo battery", "electronics", SILVER,
     [B(-BAT_W / 2, BAT_W / 2, 4, 4 + BAT_T, BAT_Z1 - BAT_L, BAT_Z1)], label="LiPo 1000 mAh")
PB_Y0 = 4 + BAT_T + 1
PB_Y1 = PB_Y0 + 1.6
part("Perfboard", "electronics", PERF,
     [B(-18, 18, PB_Y0, PB_Y1, BOT_IN + 1, -21)], label="Perfboard")
# XIAO on headers, USB-C down through the bottom wall
xy0 = PB_Y1 + 2.5
part("XIAO headers", "electronics", BLACK,
     [B(-16, -13.5, PB_Y1, xy0, -60, -39), B(-0.7, 1.8, PB_Y1, xy0, -60, -39)])
part("XIAO ESP32-C3", "electronics", (0.12, 0.12, 0.15),
     [B(-16, 1.8, xy0, xy0 + 1.2, -60, -39)], label="XIAO ESP32-C3")
part("XIAO shield", "electronics", SILVER, [B(-14, 0, xy0 + 1.2, xy0 + 3.6, -52, -40)])
part("USB-C port", "electronics", SILVER, [B(-11.6, -2.6, xy0 + 1.2, xy0 + 4.4, -61.3, -54)],
     label="USB-C (charging)")
part("Boost converter 5 V", "electronics", PURPLE,
     [B(4, 15, PB_Y1, PB_Y1 + 1.2, -60, -42), B(6, 12, PB_Y1 + 1.2, PB_Y1 + 3.5, -57, -51)],
     label="Boost 5 V")
part("MOSFET FQP30N06L", "electronics", BLACK,
     [B(5, 15, PB_Y1, PB_Y1 + 4.5, -40, -31)], label="MOSFET")
part("MOSFET tab", "electronics", SILVER, [B(5, 15, PB_Y1, PB_Y1 + 1.3, -31, -25)])
for name, x in (("C2 470uF", -12), ("C1 470uF", -3)):
    part(name, "electronics", (0.15, 0.20, 0.45), [C((x, PB_Y1, -33), (0, 12, 0), 4.0)],
         label="470 µF caps" if x == -3 else None)
for name, x0, z in (("R1 220k", -17, -26), ("R2 220k", -9, -26), ("R3 100k", 5, -22.5),
                    ("R4 1k", -17, -22.5)):
    part(name, "electronics", (0.80, 0.70, 0.55), [C((x0, PB_Y1 + 1.2, z), (6, 0, 0), 1.2)],
         label="Resistors" if name.startswith("R1") else None)
# mic on the front wall, behind the sound holes
part("MAX4466 mic board", "electronics", BLUE,
     [B(-10, 10, FRONT_IN - 5.7, FRONT_IN - 4.1, MIC_Z - 6.9, MIC_Z + 6.9)], label="MAX4466 mic")
part("Mic capsule", "electronics", SILVER, [C((0, FRONT_IN - 4.1, MIC_Z), (0, 4.1, 0), 4.85)])
part("Antenna (stick-on)", "electronics", GOLD,
     [B(-18, -6, FRONT_IN - 0.4, FRONT_IN, -58, -36)], label="Wi-Fi antenna")
part("Status LED", "electronics", RED,
     [C((-15, FRONT_IN - 5, 30), (0, 5.5, 0), 1.5)], label="Status LED")

# ------------------------------------------------------------------ wires
cw_y = 4.4
for i, col in enumerate((BROWN, RED, ORANGE)):
    dz = i * 1.2
    wire(f"Servo cable {i}", col, [(sv_x + SERVO_L / 2, 6, sv_z0 + 1 + dz), (18.9 - dz * 0.0, cw_y + dz * 0.5, sv_z0 + 1 + dz),
                                    (18.9, cw_y + dz * 0.5, -19), (14 - 2 * i, PB_Y1 + 0.5, -21.5)])
wire("Reed lead 0", BLACK, [(19.6, FRONT_IN - 1.3, reed_z), (19.0, FRONT_IN - 1.3, reed_z),
                             (19.0, FRONT_IN - 1.3, -19), (16, PB_Y1 + 0.5, -21.5)])
wire("Reed lead 1", BLACK, [(3.5, FRONT_IN - 1.3, reed_z), (3.5, FRONT_IN - 1.3, reed_z - 2.2),
                             (18.0, FRONT_IN - 2.3, reed_z - 2.2), (18.0, FRONT_IN - 2.3, -19),
                             (15, PB_Y1 + 0.5, -21.5)])
for i, col in enumerate((RED, BLACK, YELLOW)):   # from the mic's top edge, under the carriage
    x = -4 + 4 * i
    wire(f"Mic wire {i}", col, [(x, FRONT_IN - 5.7, MIC_Z + 6.0), (x, FRONT_IN - 8, -19.6),
                                (x, PB_Y1 + 0.5, -19.6), (x, PB_Y1 + 0.5, -21.5)])
for i, col in enumerate((RED, BLACK)):
    x = -18.9 + i * 1.2
    wire(f"LED wire {i}", col, [(-15 + 0.8 * (i - 0.5), FRONT_IN - 5, 30), (x, FRONT_IN - 5, 30),
                                (x, FRONT_IN - 5, -19), (-15 + i, PB_Y1 + 0.5, -21.5)])
for i, col in enumerate((RED, BLACK)):
    x = -12 + 2 * i
    wire(f"Battery lead {i}", col, [(x, 8, BAT_Z1), (x, 8, BAT_Z1 + 0.8), (x, PB_Y0 - 0.2, BAT_Z1 + 0.8),
                                    (x, PB_Y1 + 0.5, -21.5)])

# ------------------------------------------------------------------ views
GROUP_ORDER = ["wall", "mount", "shell", "servo", "mechanism", "electronics", "wires"]
EXPLODE_Y = {"wall": 0, "mount": 18, "servo": 45, "mechanism": 45, "electronics": 45,
             "wires": 45, "shell": 105}
CARRIAGE_TRAVEL = 2 * CRANK_R * sin(radians(CRANK_SWING))

DIMENSIONS = {
    "box_w": BOX_W, "box_h": BOX_Z1 - BOX_Z0, "box_d": BOX_Y1 - BOX_Y0,
    "standoff": BOX_Y1, "handle_out": BOX_Y1 + 8,
    "travel": CARRIAGE_TRAVEL,
}
