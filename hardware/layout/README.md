# Layout model

A 3D model and 2D drawings of where every part sits inside the box. It's a
**layout** model, not print-ready CAD: parts are simple blocks and cylinders at
typical datasheet sizes, used to check that everything fits and to plan the
real housing.

| File | What it is |
|---|---|
| [`layout.py`](layout.py) | All dimensions and part positions. Edit this to change the design. |
| [`build_3d.py`](build_3d.py) | Builds the 3D model in FreeCAD, checks for overlapping parts, renders the images |
| [`draw_2d.py`](draw_2d.py) | Draws the dimensioned 2D views (plain Python, no FreeCAD needed) |
| `switch_flipper_layout.step` | 3D assembly with colours, opens in Fusion 360, Onshape, SolidWorks, FreeCAD |
| `switch_flipper_layout.FCStd` | The same model as a FreeCAD document |
| [`switch_flipper_inside.stl`](switch_flipper_inside.stl) | Everything except the shell. GitHub shows it as an interactive 3D view |
| `interference_report.txt` | Result of the overlap check |

Outputs in [`docs/`](../../docs):
- [`layout_2d.svg`](../../docs/layout_2d.svg): front, side and two section views with dimensions and labels
- [`images/`](../../docs/images): rendered 3D views (closed, open, front, side, exploded)

## Regenerating

```bash
# 2D drawings
python3 hardware/layout/draw_2d.py

# 3D model, exports and images (opens a FreeCAD window briefly, FreeCAD 1.x)
cd hardware/layout
/Applications/FreeCAD.app/Contents/MacOS/FreeCAD "$PWD/build_3d.py"

# Same, but only the CAD files and overlap check, with no window
/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
  -c "import os; __file__=os.path.abspath('build_3d.py'); exec(open('build_3d.py').read())"

# Check the switch-DOWN position as well
SF_STATE=down /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd \
  -c "import os; __file__=os.path.abspath('build_3d.py'); exec(open('build_3d.py').read())"
```

Both positions (switch up and down) currently pass with no overlapping solids.
Wires and the wall/switch body are not included in the check.

## Coordinates

- **x** across the switch, + to the right when facing the wall
- **y** out of the wall, 0 = faceplate surface
- **z** up, 0 = centre of the toggle

## Key numbers

| | mm |
|---|---|
| Box (W × H × D) | 44 × 100 × 34.5 |
| Front of box from faceplate | 38 (46 to the handle knob) |
| Box extends below a US single plate | 6 |
| Carriage travel | 11.3 (crank radius 6.5, ±60°) |
| Inner width | 40 |

## Assumptions to check against your parts

- **Battery: 803040** (8 × 30 × 40 mm). If yours is bigger, the box gets
  taller: change `BAT_T`, `BAT_W`, `BAT_L` and `BOX_Z0`.
- **Toggle:** 13 mm long, tilting ±25°. Measure how far yours sticks out and
  how far its tip moves, then set `TOGGLE_LEN` / `TOGGLE_ANGLE`, and
  `CRANK_R` so the travel matches.
- **Servo:** MG90S case 22.8 × 12.2 × 22.7 mm, tabs 32.5 mm across.
- **Boost converter:** drawn as an 11 × 18 mm board; check your module.
- **Reed switch:** 14 mm glass. Smaller ones make placement easier.

## Arrangement

- **Top bay:** the servo lies with its shaft facing out of the box, held by a
  bulkhead through its mounting tabs. Its horn works as a crank: a link rod
  turns the horn's rotation into the carriage's up/down movement.
- **Middle:** the carriage slides on guide ribs on the side walls. Its fork
  hugs the toggle at the back, its handle comes out of a slot in the front.
  The magnet sits in the carriage's front face; the reed switch is fixed on the
  inside of the front wall where the magnet stops when the switch is up.
- **Bottom bay, back to front:** the LiPo lies flat against the backplate; the
  perfboard stands in front of it carrying the XIAO (USB-C pointing down
  through the bottom wall), boost converter, MOSFET, capacitors and resistors.
  The mic is mounted on the front wall behind the sound holes, and the Wi-Fi
  antenna is stuck on the inside of the front wall, away from the servo and
  battery.
- **Wires** run down the side walls behind and beside the carriage, to the top
  edge of the perfboard.
