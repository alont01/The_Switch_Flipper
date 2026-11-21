"""Builds the 3D layout model from layout.py in FreeCAD.

Run from this folder (FreeCAD 1.x):
  GUI, makes everything incl. rendered images:
      /Applications/FreeCAD.app/Contents/MacOS/FreeCAD build_3d.py
  Headless, CAD files + interference check only:
      freecadcmd -c "exec(open('build_3d.py').read())"

Outputs:
  switch_flipper_layout.FCStd   FreeCAD document (one coloured object per part)
  switch_flipper_layout.step    STEP assembly, opens in Fusion/Onshape/SolidWorks
  switch_flipper_inside.stl     everything except the shell (GitHub shows STL in 3D)
  ../../docs/images/layout_*.png  rendered views (GUI run only)

FreeCAD's front view looks along +Y, so the model's y (out of the wall) is
stored as FreeCAD -Y: the box front faces FreeCAD's "Front" view.
"""
import os
import sys
import importlib

import FreeCAD as App
import Part

HERE = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
sys.path.insert(0, HERE)
import layout as L  # noqa: E402
importlib.reload(L)

GUI = App.GuiUp
if GUI:
    import FreeCADGui as Gui

V = App.Vector


def solid(p):
    if p["t"] == "box":
        (x, y, z), (dx, dy, dz) = p["p"], p["s"]
        return Part.makeBox(dx, dy, dz, V(x, -(y + dy), z))
    x, y, z = p["p"]
    dx, dy, dz = p["d"]
    d = V(dx, -dy, dz)
    return Part.makeCylinder(p["r"], d.Length, V(x, -y, z), d)


def shape_of(part):
    shapes = [solid(p) for p in part["prims"]]
    s = shapes[0] if len(shapes) == 1 else shapes[0].fuse(shapes[1:])
    for c in part["cuts"]:
        s = s.cut(solid(c))
    try:
        s = s.removeSplitter()
    except Exception:
        pass
    return s


doc = App.newDocument("SwitchFlipperLayout")
objs = []
for prt in L.parts:
    o = doc.addObject("Part::Feature", "".join(ch if ch.isalnum() else "_" for ch in prt["name"]))
    o.Label = prt["name"]
    o.Shape = shape_of(prt)
    o.addProperty("App::PropertyString", "Group_", "Layout").Group_ = prt["group"]
    objs.append((o, prt))
doc.recompute()

# ---------------------------------------------------------------- interference check
SKIP = {"wall", "wires"}          # wall/switch body and wires touch things on purpose
problems = []
pairs = [(a, b) for i, a in enumerate(objs) for b in objs[i + 1:]]
for (oa, pa), (ob, pb) in pairs:
    if pa["group"] in SKIP or pb["group"] in SKIP:
        continue
    if not oa.Shape.BoundBox.intersect(ob.Shape.BoundBox):
        continue
    v = oa.Shape.common(ob.Shape).Volume
    if v > 0.05:
        problems.append((pa["name"], pb["name"], round(v, 2)))
# moving parts must also clear the lever
lever = next(o for o, p in objs if p["name"] == "Toggle lever")
for o, p in objs:
    if p["group"] in ("mechanism", "servo", "electronics", "shell"):
        if o.Shape.BoundBox.intersect(lever.Shape.BoundBox):
            v = o.Shape.common(lever.Shape).Volume
            if v > 0.05:
                problems.append((p["name"], "Toggle lever", round(v, 2)))
report = os.path.join(HERE, "interference_report.txt")
with open(report, "w") as f:
    f.write("Overlapping solids (mm^3) with the switch %s. Wires and the wall/switch body are not checked.\n"
            % ("UP" if L.STATE_UP else "DOWN"))
    for a, b, v in problems:
        f.write(f"{a}  <->  {b}: {v}\n")
    if not problems:
        f.write("none\n")
print("interference:", problems or "none")

# ---------------------------------------------------------------- exports
doc.saveAs(os.path.join(HERE, "switch_flipper_layout.FCStd"))
import Mesh  # noqa: E402
inside = [o for o, p in objs if p["group"] not in ("shell", "wall")]
Mesh.export(inside, os.path.join(HERE, "switch_flipper_inside.stl"))

if not GUI:
    Part.export([o for o, _ in objs], os.path.join(HERE, "switch_flipper_layout.step"))
else:
    for o, p in objs:
        vo = o.ViewObject
        vo.ShapeColor = p["color"]
        vo.Transparency = int(round((1 - p["alpha"]) * 100))
        vo.LineColor = (0.25, 0.25, 0.25)
        vo.LineWidth = 1.0
    try:
        import Import
        Import.export([o for o, _ in objs], os.path.join(HERE, "switch_flipper_layout.step"))
    except Exception as e:  # fall back to uncoloured STEP
        print("coloured STEP failed:", e)
        Part.export([o for o, _ in objs], os.path.join(HERE, "switch_flipper_layout.step"))

    img_dir = os.path.normpath(os.path.join(HERE, "..", "..", "docs", "images"))
    os.makedirs(img_dir, exist_ok=True)
    vp = App.ParamGet("User parameter:BaseApp/Preferences/View")
    vp.SetBool("UseNavigationAnimations", False)
    gdoc = Gui.getDocument(doc.Name)
    view = gdoc.activeView()
    Gui.runCommand("Std_OrthographicCamera")

    def show(fn):
        for o, p in objs:
            o.ViewObject.Visibility = bool(fn(o, p))

    def place(explode):
        for o, p in objs:
            dy = L.EXPLODE_Y.get(p["group"], 0) if explode else 0
            o.Placement.Base = V(0, -dy, 0)
        doc.recompute()

    import time

    def settle():
        for _ in range(5):
            Gui.updateGui()
            time.sleep(0.15)

    def shot(name, orient, w=2400, h=2400):
        getattr(view, orient)()
        settle()
        view.fitAll()
        settle()
        path = os.path.join(img_dir, name)
        view.saveImage(path, w, h, "White")
        try:  # trim the empty margin fitAll leaves
            from PIL import Image, ImageChops
            im = Image.open(path).convert("RGB")
            box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
            if box:
                m = 30
                box = (max(box[0] - m, 0), max(box[1] - m, 0), min(box[2] + m, im.width), min(box[3] + m, im.height))
                im.crop(box).save(path)
        except Exception as e:
            print("trim failed:", e)

    is_shell_wall = lambda p: p["group"] == "shell" and p["name"].startswith("Shell")
    place(False)
    show(lambda o, p: p["name"] != "Wall")
    shot("layout_iso.png", "viewIsometric")
    show(lambda o, p: p["name"] != "Wall" and not is_shell_wall(p))
    shot("layout_iso_open.png", "viewIsometric")
    show(lambda o, p: p["group"] != "wall" or p["name"] == "Toggle lever")
    for o, p in objs:
        if is_shell_wall(p) and p["name"] != "Shell front":
            o.ViewObject.Transparency = 60
    show(lambda o, p: p["name"] not in ("Wall", "Shell front", "Shell top") and p["group"] != "mount"
         and p["name"] != "Faceplate (US toggle)")
    shot("layout_front_open.png", "viewFront")
    show(lambda o, p: p["name"] not in ("Wall", "Shell right wall"))
    shot("layout_side_open.png", "viewRight")
    for o, p in objs:
        o.ViewObject.Transparency = int(round((1 - p["alpha"]) * 100))
    place(True)
    show(lambda o, p: p["name"] != "Wall")
    shot("layout_exploded.png", "viewIsometric")
    place(False)
    show(lambda o, p: True)
    doc.save()
    print("images written to", img_dir)
    if os.environ.get("SF_QUIT", "1") == "1":
        os._exit(0)
