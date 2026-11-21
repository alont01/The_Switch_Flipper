# Firmware

## `tests/`: bench test programs (Arduino C++)

One small program per part, run in order. The full guide, with wiring for
each, is [docs/testing.md](../docs/testing.md).

| Folder | What it does |
|---|---|
| `01_wifi_scan` | Lists nearby Wi-Fi networks and signal strength |
| `02_servo_sweep` | Sweeps the servo on D4 between 30° and 150° |
| `03_servo_mosfet` | Powers the servo through the MOSFET (D5) only while moving; also test 7 with the boost converter |
| `04_mic_plotter` | Streams mic loudness for the Serial Plotter |
| `05_reed_switch` | Prints OPEN/CLOSED as a magnet passes the reed switch on D10 |
| `06_led` | Blinks the status LED on D8 |
| `08_double_clap` | Full double-clap detector with tunable settings |
| `servo_angle` | Type an angle in the Serial Monitor and the servo goes there |
| `servo_full_range` | Swings the servo 180 ↔ 0 forever |

**Board:** esp32 by Espressif (Boards Manager), board `XIAO_ESP32C3`,
FQBN `esp32:esp32:XIAO_ESP32C3`. Tested with core 4.0.0.
**Library:** ESP32Servo (tested with 3.2.1).

## Main firmware (not written yet)

Will combine the tests into one program: double-clap detection, reed-switch
state, servo moves with power gating and a low-battery cutoff, captive-portal
Wi-Fi setup, the `<name>.local` web page, and OTA updates. See
[docs/design.md](../docs/design.md#firmware). It may be written in Rust
(`esp-idf-svc`) instead of Arduino.
