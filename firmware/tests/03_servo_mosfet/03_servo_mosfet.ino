// Test 3: MOSFET servo power switch
// Powers the servo, moves it, then cuts its power.
// Wiring: as test 2, but servo brown -> MOSFET drain,
//         MOSFET source -> GND rail, MOSFET gate -> D5,
//         100 kOhm from gate to GND rail.
// Test 7 reuses this program: the boost converter's EN pin also goes to D5,
// so the converter and the MOSFET switch on and off together.
// Needs the ESP32Servo library.

#include <ESP32Servo.h>

const int SERVO_PIN = D4;
const int POWER_PIN = D5;

Servo servo;
bool up = false;

void moveTo(int angle) {
  Serial.println("Servo power ON");
  digitalWrite(POWER_PIN, HIGH);
  delay(50);                        // let the servo power up

  servo.attach(SERVO_PIN, 500, 2400);
  servo.write(angle);
  delay(600);                       // time to reach the position

  servo.detach();                   // stop sending the position signal
  digitalWrite(POWER_PIN, LOW);
  Serial.println("Servo power OFF (arm should turn freely by hand)");
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Test 3: servo through MOSFET");
  pinMode(POWER_PIN, OUTPUT);
  digitalWrite(POWER_PIN, LOW);
  servo.setPeriodHertz(50);
}

void loop() {
  up = !up;
  Serial.printf("Moving %s\n", up ? "up" : "down");
  moveTo(up ? 150 : 30);
  delay(4000);
}
