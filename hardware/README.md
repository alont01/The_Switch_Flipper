# Hardware

Printable parts and CAD go here.

The first prototype housing has been printed: the MG90S sits in the left bay,
and the right side holds an adjustable slotted plate. Add its source files and
STLs to this folder, for example:

```
hardware/
  layout/     layout model (done)
  cad/        source files (Fusion, OpenSCAD, STEP)
  stl/        print-ready parts: box, backplate, carriage, finger
  photos/
```

**[layout/](layout)** has the 3D layout model: where every part sits, with
STEP/FreeCAD/STL exports, rendered views and 2D drawings. Use it as the
reference when modelling the real printed parts.

Design requirements are in [docs/design.md](../docs/design.md):

- Box no wider than **44 mm** (fits shared multi-switch plates, 46 mm pitch).
- Full-size backplate for Command strips, with fallback holes for the faceplate
  screws; box hooks on at the top and clicks in at the bottom.
- Sliding carriage with an adjustable two-pronged finger and a front handle.
- Pocket in the carriage for a 5×2 mm magnet; reed switch fixed at the top of
  the carriage's travel, away from the servo motor.
- Sound holes in front of the mic, a status-LED hole, and a USB-C opening at
  the bottom.
- Leave 0.3–0.5 mm clearance per side on sliding parts so the servo never has
  to fight friction.

Print in PLA for prototypes; PETG for anything that sits in a warm spot.
