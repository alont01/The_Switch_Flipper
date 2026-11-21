// Test 4: microphone
// Shows loudness as a line in the Serial Plotter. Claps appear as tall spikes.
// Wiring: mic VCC -> 3V3, GND -> GND rail, OUT -> D1.
// Open Tools > Serial Plotter at 115200 baud.

const int MIC_PIN = D1;
const int WINDOW_MS = 20;  // measure loudness over 20 ms chunks

void setup() {
  Serial.begin(115200);
  delay(2000);
  analogReadResolution(12);  // readings from 0 to 4095
}

void loop() {
  int lowest = 4095;
  int highest = 0;
  unsigned long start = millis();

  // The mic signal swings around a middle value. The gap between the
  // highest and lowest reading in each chunk is how loud it was.
  while (millis() - start < WINDOW_MS) {
    int v = analogRead(MIC_PIN);
    if (v < lowest) lowest = v;
    if (v > highest) highest = v;
  }

  int loudness = highest - lowest;

  // Two labelled lines for the plotter: the reading, and a reference
  // line at the level a clap should clearly exceed.
  Serial.printf("loudness:%d,clap_level:1500\n", loudness);
}
