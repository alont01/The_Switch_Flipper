// Servo angle tester: type an angle (0-180) in the Serial Monitor and press
// Enter; the servo on D4 moves there and stays. Starts at 90.
// Wiring: servo brown -> GND, red -> 5V, orange -> D4.
// Needs the ESP32Servo library.
#include <ESP32Servo.h>

const int SERVO_PIN = D4;
Servo servo;
int current = 90;

// Delay per degree when moving. 0 = full speed (jumps straight there).
// Raise it (e.g. 25) to move slowly.
const int STEP_MS = 0;

void moveSlowly(int target) {
  if (STEP_MS == 0) { servo.write(target); current = target; return; }
  int step = target > current ? 1 : -1;
  while (current != target) {
    current += step;
    servo.write(current);
    delay(STEP_MS);
  }
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);
  servo.write(90);
  Serial.println("Servo angle tester. At 90. Type an angle 0-180.");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) return;
    int angle = constrain(line.toInt(), 0, 180);
    moveSlowly(angle);
    Serial.printf("Moved to %d\n", angle);
  }
}
