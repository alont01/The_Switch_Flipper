// Test 5: reed switch
// Reports when a magnet closes or opens the reed switch.
// Wiring: one leg -> D10, other leg -> GND rail. No resistor needed.

const int REED_PIN = D10;

bool lastClosed = false;

void setup() {
  Serial.begin(115200);
  delay(2000);
  Serial.println("Test 5: reed switch. Move a magnet near it.");
  pinMode(REED_PIN, INPUT_PULLUP);  // reads HIGH when open, LOW when closed
  lastClosed = (digitalRead(REED_PIN) == LOW);
  Serial.println(lastClosed ? "Starting state: CLOSED (magnet near)"
                            : "Starting state: OPEN (no magnet)");
}

void loop() {
  bool closed = (digitalRead(REED_PIN) == LOW);
  if (closed != lastClosed) {
    delay(20);  // ignore the brief chatter as the contacts settle
    closed = (digitalRead(REED_PIN) == LOW);
    if (closed != lastClosed) {
      Serial.println(closed ? "CLOSED (magnet near)" : "OPEN (no magnet)");
      lastClosed = closed;
    }
  }
}
