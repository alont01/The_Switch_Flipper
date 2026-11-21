// Test 2: servo
// Swings the servo slowly between two angles.
// Wiring: servo red -> 5V rail, brown -> GND rail, orange -> D4.
//         470 uF capacitor across the rails (stripe on GND).
// Needs the ESP32Servo library.

#include <ESP32Servo.h>

const int SERVO_PIN = D4;
const int LOW_ANGLE = 30;
const int HIGH_ANGLE = 150;

Servo servo;

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Test 2: servo sweep");
  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);  // pulse range in microseconds
}

void sweep(int from, int to) {
  int step = (to > from) ? 1 : -1;
  for (int a = from; a != to; a += step) {
    servo.write(a);
    delay(10);
  }
  servo.write(to);
}

void loop() {
  Serial.println("Moving up");
  sweep(LOW_ANGLE, HIGH_ANGLE);
  delay(1000);
  Serial.println("Moving down");
  sweep(HIGH_ANGLE, LOW_ANGLE);
  delay(1000);
}
