// Test 6: status LED
// Blinks the LED once a second.
// Wiring: 3V3 -> 1 kOhm -> LED long leg, LED short leg -> D8.
// The LED lights when D8 is LOW, because current flows from 3V3 into the pin.

const int LED_PIN = D8;

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Test 6: LED blink");
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);  // off
}

void loop() {
  digitalWrite(LED_PIN, LOW);   // on
  Serial.println("LED on");
  delay(500);
  digitalWrite(LED_PIN, HIGH);  // off
  Serial.println("LED off");
  delay(500);
}
