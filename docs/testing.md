# Bench tests

Eight tests: one per part, then double-clap detection (test 7 reuses the
program from test 3). Run them in order and only move on when a
test passes. Everything runs on USB power. Keep the battery disconnected.

## One-time setup

1. Install the Arduino IDE (arduino.cc).
2. Tools > Board > Boards Manager: install **esp32 by Espressif Systems**.
3. Tools > Board: select **XIAO_ESP32C3**.
4. Sketch > Include Library > Manage Libraries: install **ESP32Servo** (by Kevin Harrington).
5. Use a USB-C cable that carries data, not a charge-only cable.

The test programs are in [`firmware/tests`](../firmware/tests). To open one:
File > Open, then pick the `.ino` file inside its folder.

With arduino-cli instead of the IDE:

```bash
arduino-cli core install esp32:esp32
arduino-cli lib install ESP32Servo
arduino-cli compile --fqbn esp32:esp32:XIAO_ESP32C3 firmware/tests/02_servo_sweep
arduino-cli upload -p /dev/cu.usbmodem101 --fqbn esp32:esp32:XIAO_ESP32C3 firmware/tests/02_servo_sweep
```

(Replace the port with yours: `arduino-cli board list`.)
After uploading, open Tools > Serial Monitor (or Serial Plotter for test 4)
and set it to **115200 baud**.

If the Serial Monitor stays blank: Tools > **USB CDC On Boot** > **Enabled**,
then upload again.

If an upload fails: hold the **B** (boot) button on the XIAO, press and release
**R** (reset), release **B**, then upload again.

## Breadboard layout

Push the XIAO into the breadboard so it straddles the centre gap, USB port
facing off the end of the board.

XIAO pins, seen from the top with the USB port at the top
(check against the pinout card that came with your board):

```
            USB
      D0  [     ]  5V
      D1  [     ]  GND
      D2  [     ]  3V3
      D3  [     ]  D10
      D4  [     ]  D9
      D5  [     ]  D8
      D6  [     ]  D7
```

Power rails:
- **5V pin** to the red (+) rail on one side: powers the servo during testing only.
- **GND pin** to the blue (-) rail.
- **3V3 pin**: run a separate jumper wherever a part needs 3.3 V (mic, LED).
  Don't put 3V3 on the same rail as 5V.

## Test 1: board and Wi-Fi

- **Wiring:** only the antenna. Snap its small connector onto the board.
- **Program:** `01_wifi_scan`
- **Passes when:** your home network appears in the Serial Monitor list.

## Test 2: servo

- **Wiring:**
  - Servo red: + rail (5V)
  - Servo brown: - rail (GND)
  - Servo orange: D4
  - 470 µF capacitor across the + and - rails, **stripe (negative leg) on the - rail**
- **Program:** `02_servo_sweep`
- **Passes when:** the arm swings slowly back and forth.
- **If the board keeps restarting:** the servo is pulling too much from USB.
  Check the capacitor and its direction, and try a different USB port.

- **Extra tools:**
  - `servo_angle`: type an angle (0-180) in the Serial Monitor and the servo
    goes there and holds. Use it to find the carriage's up and down angles.
    `STEP_MS` at the top sets the speed (0 = full speed).
  - `servo_full_range`: swings 180 ↔ 0 forever.

## Test 3: MOSFET (servo power switch)

- **Wiring change:** servo brown no longer goes to GND.
  - FQP30N06L, label facing you, legs down: **Gate, Drain, Source** left to right.
  - Gate: D5
  - 100 kΩ resistor from Gate to the - rail
  - Drain: servo brown
  - Source: - rail
  - Servo red and orange stay as in test 2.
- **Program:** `03_servo_mosfet`
- **Passes when:** the servo moves only during the "power ON" messages and the
  arm turns freely by hand during "power OFF".

## Test 4: microphone

- **Wiring:**
  - Mic VCC: 3V3
  - Mic GND: - rail
  - Mic OUT: D1
- **Program:** `04_mic_plotter`
- **Use the Serial Plotter**, not the Monitor.
- **Passes when:** a clap makes a tall spike well above talking or background noise.
- Turn the tiny screw on the back of the mic to change its gain. Aim for claps
  around 2000-3500 on the plot (never 4095, which means clipping) and normal
  noise below about 200.

## Test 5: reed switch

- **Wiring:**
  - One leg: D10
  - Other leg: - rail
  - (no resistor needed; the program uses the board's internal pull-up)
- **Program:** `05_reed_switch`
- **Passes when:** "CLOSED" appears as a magnet comes within a few mm, and "OPEN" when it moves away.
- The glass breaks easily. Bend the legs gently, gripping them near the glass.

## Test 6: status LED

- **Wiring:**
  - 3V3 to a 1 kΩ resistor
  - Resistor to the LED's **long leg**
  - LED's short leg to D8
- **Program:** `06_led`
- **Passes when:** the LED blinks once a second.
- If it never lights, the LED is probably the wrong way round.

## Test 7: battery and 5 V boost converter

Do this last, after tests 1-6 pass. Unplug USB while rewiring.

- **Wiring change:** the servo's red wire moves from the 5V rail to the
  converter's output. The battery replaces USB as the servo's power source.
  - Battery + to converter **VIN**
  - Battery - to the - rail (shared ground with the XIAO)
  - Converter **GND** to the - rail
  - Converter **VOUT** to servo red
  - Converter **EN** to D5 (same pin as the MOSFET gate; both turn on together)
  - Keep the MOSFET exactly as in test 3. Many boost converters still pass
    battery voltage through to the output when disabled, so the MOSFET is what
    actually switches the servo fully off.
  - 470 µF capacitor across VOUT and the - rail, close to the servo, stripe on -
  - A second capacitor (220-470 µF) across battery + and the - rail, stripe on -
- **Connect the battery one wire at a time** and never let its bare ends touch.
- Plug USB back in so you can see the Serial Monitor. The XIAO runs from USB,
  the servo from the battery through the converter.
- **Program:** `03_servo_mosfet` again (no changes needed).
- **Passes when:** the servo moves as strongly as it did on USB, and the board
  doesn't restart during moves.
- With the MOSFET and converter both off, measure VOUT with a multimeter if you
  have one. If it shows close to battery voltage, the converter passes power
  through when disabled, which confirms the MOSFET is needed.

## Test 8: double-clap detection

Can run any time after tests 4 and 6 pass.

- **Wiring:** mic as in test 4, LED as in test 6. Nothing else needed.
- **Program:** `08_double_clap`
- **Passes when:** two claps about half a second apart print `DOUBLE CLAP` and
  flash the LED, while a single clap, three claps, talking and music don't.
- **What to try:**
  - Clap twice from where you'd normally stand, then from across the room.
  - A single clap, three quick claps, a door closing, a book dropped on a table.
  - Talking and music playing near it.
- **Tuning** (settings at the top of the program):
  - Missing claps from far away: lower `ABS_MIN` or `RATIO`, or turn up the
    mic's gain screw.
  - Triggering on other noises: raise `ABS_MIN` or `RATIO`.
  - "first sound lasted too long" on real claps in an echoey room: raise
    `MAX_CLAP_MS` a little.
  - Your claps are slower or faster than it expects: adjust `MIN_GAP_MS` and
    `MAX_GAP_MS`.

## Results so far

| Test | Status | Notes |
|---|---|---|
| 1 Wi-Fi | Pass | −47 dBm, 40 networks with the antenna on (−78 dBm without) |
| 2 Servo | Pass on its own | Sweeps 0–180°. In the printed housing with the carriage attached, the board brownout-resets during moves on USB power |
| 3 MOSFET | Not yet | |
| 4 Mic | Works, gain too high | Quiet ≈ 34, every clap clipped at 4095. Turn the gain screw down |
| 5 Reed switch | Not yet | |
| 6 LED | Not yet | |
| 7 Battery + boost | Not yet | Waiting on the boost converter |
| 8 Double clap | Not yet | Run after the mic gain is set |

### If the board restarts when the servo moves

The serial output shows `E BOD: Brownout detector was triggered`: the supply
dipped so low the XIAO reset itself. In order of likelihood:

1. **The mechanism is binding or the horn hits the box.** A strained servo
   draws its stall current (several hundred mA) whatever speed you ask for.
   Test with the horn removed: if it moves fine then, fix the print (more slot
   clearance, smoother linkage), or stop short of the obstruction.
2. **No capacitor.** Add the 470 µF across the servo's + and − supply.
3. **Weak USB supply.** Try another port, cable or a powered hub. The final
   build runs the servo from the battery through the boost converter instead.

## After all eight pass

Leave everything wired. The full firmware uses the same pins, so the breadboard
becomes the complete circuit for the next stage.
