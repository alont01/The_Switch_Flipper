# Design

How The Switch Flipper works and why it's built this way. For wiring see
[schematic.svg](schematic.svg); for bench tests see [testing.md](testing.md).

## Goal

A 3D-printed box that fits over an existing wall light switch and flips it
mechanically. No house wiring is touched, so it's safe, renter-friendly, and
the switch still works normally for anyone in the house.

It can be controlled three ways:

1. **Double clap**, heard by a built-in microphone.
2. **Phone**, through a small web page the box serves on your home Wi-Fi.
3. **By hand**, with a handle on the front that slides the mechanism directly.

The main target is the **US single toggle switch**.

## Mechanism

```
  Front view (cover removed)            Side view (cross-section)

  ┌─────────────────┐                   wall │
  │  [ servo ]──┐   │                        │ ┌─────────────────┐
  │   crank     │   │                  plate │ │  servo ─ crank  │
  │      link rod   │                  ──────┤ │        │        │
  │  ┌──────────┴┐  │                 toggle ├─┼──◄ fork┼────────┼─● handle
  │  │ carriage  │◄─┼─ handle         ──────┤ │                 │
  │  │  ╓────╖   │  │                        │ │ mic  XIAO  LiPo │
  │  └──╨─toggle─┘  │                        │ └─────────────────┘
  │  mic · XIAO     │
  │  battery        │
  └─────────────────┘
```

- **One sliding carriage** runs up and down on guide rails inside the box.
- **A two-pronged finger (fork)** on the carriage straddles the toggle. Its
  depth is adjustable with a lock screw, so one design fits toggles that stick
  out by different amounts.
- **The servo sits above the carriage** and drives it through a short crank and
  link rod. In a 44 mm wide box there's no room for the servo beside the
  carriage.
- **The handle is part of the carriage** and sticks out through a slot in the
  front. Moving it by hand moves the fork, so the light works even with a flat
  battery.
- **The servo only pushes the carriage while powered.** Between moves its power
  is cut, so it turns freely and doesn't fight the handle.
- **The fork has about 1 mm of play** around the toggle. Wall toggles snap to
  one end or the other, so a move that stops halfway can never leave the light
  in between.

### Knowing the switch position

A **reed switch** is fixed to the inside of the box at the top of the
carriage's travel, and a **5×2 mm neodymium magnet** rides in a pocket in the
carriage.

- Carriage up: the magnet is next to the reed switch, it closes, D10 reads LOW.
- Carriage down: the magnet is ~20 mm away, it opens, D10 reads HIGH.

The servo can't report its position (its signal wire only goes in), so this
sensor is the only way the box notices a flip made by hand. Before each move
the firmware reads the reed switch and drives to the **opposite** position,
then checks the reed switch changed. If it didn't, the web page reports
"stuck". Some switches are installed upside down, so "up = on" is a firmware
setting.

Halfway reads as "down". A second reed switch at the bottom of the travel could
tell "down" from "stuck halfway" if that turns out to matter.

## Size

The box is **44 mm wide**. Neighbouring switches on a shared faceplate are 46 mm
apart centre to centre, so a 44 mm box fits on single plates **and** on
multi-switch plates without covering the next switch. Each automated switch
gets its own box.

That width shapes the inside: the servo is about 23 mm wide and the XIAO about
18 mm, so parts are stacked vertically, and the battery is a flat pouch cell
(a round 18650 would push the box too far off the wall).

Layout, top to bottom: servo (with its capacitor and MOSFET on short wires) →
carriage and reed switch → mic behind sound holes → XIAO with USB-C facing down
→ flat LiPo against the backplate. The XIAO's stick-on antenna goes on the
inside of the front shell, away from the battery and servo.

## Mounting

A **full-size backplate** covers the whole faceplate (about 70 × 114 mm on a US
single plate) and sticks on with **3M Command strips**. The box **hooks on at
the top and clicks in at the bottom**, so it comes off for charging without
disturbing the adhesive.

- Clean the faceplate with rubbing alcohol, stick the strips to the backplate,
  press it on for 30 s, wait an hour before clipping the box on.
- Run the strips vertically on each side of the switch opening, with the pull
  tabs sticking out below the backplate so they can be removed cleanly.
- Use the plain foam refill strips, not the Velcro-style picture hangers, which
  let the box shift on every flip.
- It sticks to the faceplate, not the wall, so removal can't damage paint.
- **Fallback:** the backplate keeps holes for the two faceplate screws, so
  longer 6-32 screws can be added without reprinting. Foam (VHB-type) tape is
  the stronger stick-on alternative.

Every flip pushes the box slightly; toggles push mostly up and down, which
strips resist well. This is untested on the real design, so try one switch for
a week or two.

## Electronics

| Ref | Part | Job |
|---|---|---|
| U1 | Seeed XIAO ESP32-C3 | Wi-Fi, web page, clap detection; built-in LiPo charger on USB-C |
| BT1 | 3.7 V LiPo, 1000 mAh, with protection circuit | Power |
| U2 | 5 V boost converter (Adafruit MiniBoost TPS61023 or Pololu 5 V step-up; avoid MT3608) | Full servo torque from a 3.7 V cell |
| M2 | MG90S metal-gear micro servo | Moves the carriage |
| Q1 | FQP30N06L logic-level N-MOSFET (or AO3400 SMD) | Cuts servo power when idle |
| M1 | MAX4466 mic module (adjustable gain) | Hears claps |
| S1 | Reed switch + 5×2 mm magnet | Carriage position |
| D1 | LED + 1 kΩ (R4) | Status light |
| C1, C2 | 220–470 µF and 470 µF electrolytic | Supply the servo's start-up surge |
| R1, R2 | 2 × 220 kΩ | Battery voltage divider |
| R3 | 100 kΩ | Keeps the MOSFET off while the XIAO boots |

Built on perfboard, with jumper-wire breadboard tests first.

### Pin map

| Pin | Connects to | Notes |
|---|---|---|
| D1 | Mic OUT | ADC1 |
| D2 | Battery divider midpoint | ADC1, reads half the battery voltage |
| D4 | Servo signal (orange) | 50 Hz PWM, 500–2400 µs |
| D5 | MOSFET gate **and** boost EN | HIGH = servo powered |
| D8 | LED cathode | Active low |
| D10 | Reed switch (other leg to GND) | `INPUT_PULLUP`, LOW = carriage up |
| 3V3 | Mic VCC, LED resistor | |
| BAT+/BAT− pads | LiPo | Underside of the XIAO |

D0 and D9 are left free: they're ESP32-C3 strapping pins and affect boot.

### Power

- The servo is fed from the battery through the **boost converter**, so it gets
  a full 5 V instead of 3.7–4.2 V.
- **Q1 switches the servo's ground** (low side). It stays in even with the
  boost converter, because many boost modules pass battery voltage straight
  through when EN is low, which would leave the servo drawing current.
- **The capacitors sit on the supply side** (across battery and across the
  boost output near the servo), not after the MOSFET. They cover the servo's
  start-up surge so it doesn't reset the XIAO. They can't finish a move if the
  battery is actually flat.
- The firmware reads the battery **before** each move and refuses to move below
  about **3.6 V** (tunable), so the servo never runs on a nearly flat cell.
- If the XIAO restarts from a brownout, it starts in low-battery mode and
  never moves the servo at boot; it only reads the reed switch.
- The LiPo's own protection cuts off around 2.5–3.0 V as a last resort.

Battery life is still an estimate. Staying on Wi-Fi to serve the page is the
biggest drain. A later revision could add a comparator on the mic output so a
loud sound wakes the XIAO from light sleep.

## Firmware

### Double-clap detection

Implemented and ready to tune in
[`firmware/tests/08_double_clap`](../firmware/tests/08_double_clap/08_double_clap.ino).

- Loudness is measured as the peak-to-peak ADC reading over 5 ms chunks.
- A **running noise floor** follows background sound over a few seconds, so a
  TV or music raises the threshold automatically.
- A clap must be louder than `max(ABS_MIN, noise × RATIO)` **and** start
  sharply (much quieter 5–10 ms earlier).
- A clap must die away within `MAX_CLAP_MS`, measured against its own peak, so
  echoey rooms and loud claps still count.
- The second clap must start 120–700 ms after the first, then there must be
  300 ms of quiet; a third sound cancels it.
- After a detection, and around every servo move, the mic is ignored for a
  moment (`muteFor()`), so the motor noise isn't heard as a clap.

Mic gain is set once with the trimpot on the MAX4466 so claps peak around
2000–3500 (out of 4095) from where you'd normally stand without clipping; the
software thresholds are what you tune day to day.

### Phone control (planned)

- **First setup:** with no saved Wi-Fi, the box opens its own network
  (`LightSwitch-Setup`). Joining it from a phone pops up a captive-portal page
  to pick the home network, enter its password and name the box.
- **Everyday:** the box serves a page at `<name>.local` showing the light state,
  a flip button, battery level and clap sensitivity. It can be added to the
  phone's home screen.
- 2.4 GHz Wi-Fi only; works on the home network only; no cloud or account.
- If the saved network is unreachable for a few minutes, setup mode reopens.
  Sliding the handle up and down five times quickly also forces setup mode.
- Clapping and the handle keep working when Wi-Fi is down.

### Language

The bench tests are Arduino C++. The full firmware may move to Rust with
`esp-idf-svc` (std on ESP-IDF), which provides Wi-Fi, HTTP server, mDNS, NVS
and OTA out of the box. The ESP32-C3 is RISC-V and well supported by esp-rs.

## Limits

- On/off toggles only (rockers are a possible later variant). Not dimmers with
  sliders or knobs, or touch switches.
- UK/EU/AU switches need a different backplate.
- On a two-way circuit (e.g. stairs), the box can flip its switch but can't
  know whether the light is actually on.
- Every box in a room hears the same claps; multiple boxes need different clap
  patterns.

## Bench findings so far

- Wi-Fi works well with the stick-on antenna attached (−47 dBm vs −78 dBm
  without).
- The MAX4466 at its default gain clipped every clap at 4095 and made claps
  appear to last ~200 ms; gain needs turning down.
- The MG90S sweeps 0–180° fine on USB power by itself. **Inside the printed
  housing, with the carriage attached, the XIAO brownout-resets during moves**
  on USB power, at full speed and slowed down. Next steps: check the
  mechanism for binding, add C1/C2, and test on the battery + boost supply.
- 0–180° (500–2400 µs) is the servo's whole range, so it can't be extended
  past 0° in software. Re-seating the horn on the spline shifts where the
  usable range falls in the box. The firmware should use end angles a few
  degrees short of any hard stop.
