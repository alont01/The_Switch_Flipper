// Servo full range: moves the servo on D4 to 180 degrees, then 0, and repeats.
// Wiring: servo brown -> GND, red -> 5V, orange -> D4.
// Needs the ESP32Servo library.

#include <ESP32Servo.h>

const int SERVO_PIN = D4;
const int PAUSE_MS  = 1500;  // time at each end

Servo servo;

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Servo full range: 180 <-> 0");
  servo.setPeriodHertz(50);
  servo.attach(SERVO_PIN, 500, 2400);
}

void loop() {
  Serial.println("180");
  servo.write(180);
  delay(PAUSE_MS);

  Serial.println("0");
  servo.write(0);
  delay(PAUSE_MS);
}
