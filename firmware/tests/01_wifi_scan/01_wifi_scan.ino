// Test 1: board and Wi-Fi
// Lists nearby Wi-Fi networks every 10 seconds.
// Wiring: antenna only.

#include <WiFi.h>

void setup() {
  Serial.begin(115200);
  delay(2000);  // give the Serial Monitor time to connect
  Serial.println("Test 1: Wi-Fi scan");
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
}

void loop() {
  Serial.println("Scanning...");
  int count = WiFi.scanNetworks();

  if (count == 0) {
    Serial.println("No networks found. Is the antenna attached?");
  } else {
    Serial.printf("Found %d networks:\n", count);
    for (int i = 0; i < count; i++) {
      // Signal: -30 is excellent, -70 is fine, below -85 is weak
      Serial.printf("  %-32s  signal %d dBm\n", WiFi.SSID(i).c_str(), WiFi.RSSI(i));
    }
  }
  WiFi.scanDelete();
  Serial.println();
  delay(10000);
}
