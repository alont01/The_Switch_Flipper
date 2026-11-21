// Test 8: double-clap detection
// Listens for exactly two sharp, short sounds 0.12-0.7 s apart, followed by
// silence. Lights the LED and prints DOUBLE CLAP when it hears one.
//
// Wiring: mic as in test 4 (OUT -> D1), LED as in test 6 (D8).
// Open the Serial Monitor at 115200 baud to see what it hears.

const int MIC_PIN = D1;
const int LED_PIN = D8;  // LED is on when this pin is LOW

// ---------- Settings to tune ----------
// Loudness is the same scale as test 4's plot (0-4095).
int   ABS_MIN = 600;    // a clap must be at least this loud
float RATIO   = 5.0;    // ...and this many times louder than the background

const uint32_t MAX_CLAP_MS    = 200;   // a clap (plus its echo) dies away within this
const float    CLAP_END       = 0.2f;  // clap is over below this fraction of its peak
const uint32_t MIN_GAP_MS     = 120;   // claps closer than this count as one
const uint32_t MAX_GAP_MS     = 700;   // second clap must start within this
const uint32_t QUIET_AFTER_MS = 300;   // silence needed after the second clap
const uint32_t LOCKOUT_MS     = 1500;  // ignore everything after a detection
// ---------------------------------------

const uint32_t WINDOW_US = 5000;  // measure loudness over 5 ms chunks

float noise = 50;        // running estimate of background loudness
int prev1 = 0, prev2 = 0;  // loudness of the last two chunks

enum State { IDLE, CLAP1, WAIT2, CLAP2, CONFIRM, REJECT };
State state = IDLE;

uint32_t firstOnset = 0;   // when the first clap started
uint32_t clapStart = 0;    // when the current clap started
uint32_t stateTime = 0;    // general-purpose timer for CONFIRM and REJECT
uint32_t muteUntil = 0;    // ignore the mic until this time
int clapPeak = 0;          // loudest chunk of the current clap

// The full firmware calls this before moving the servo, so the motor's
// noise isn't mistaken for claps.
void muteFor(uint32_t ms) {
  muteUntil = millis() + ms;
  state = IDLE;
}

// Loudness of one 5 ms chunk: the gap between the highest and lowest reading.
int measureChunk() {
  int lo = 4095, hi = 0;
  uint32_t start = micros();
  while (micros() - start < WINDOW_US) {
    int v = analogRead(MIC_PIN);
    if (v < lo) lo = v;
    if (v > hi) hi = v;
  }
  return hi - lo;
}

void reject(const char *why) {
  Serial.printf("  rejected: %s\n", why);
  state = REJECT;
  stateTime = millis();
}

void doubleClap() {
  Serial.println(">>> DOUBLE CLAP <<<");
  digitalWrite(LED_PIN, LOW);   // LED on
  delay(300);
  digitalWrite(LED_PIN, HIGH);  // LED off
  muteFor(LOCKOUT_MS);
}

void setup() {
  Serial.begin(115200);
  delay(2000);
  analogReadResolution(12);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  Serial.println("Test 8: double clap. Clap twice, about half a second apart.");
}

void loop() {
  int loud = measureChunk();
  uint32_t now = millis();

  // How loud a clap must be right now, and how quiet counts as "it's over".
  float trigger = fmaxf((float)ABS_MIN, noise * RATIO);
  float release = trigger * 0.4f;

  // A clap starts suddenly: loud now, and much quieter 5-10 ms ago.
  bool onset = loud > trigger && min(prev1, prev2) < loud / 2;
  bool quiet = loud < release;

  // A clap is over once it has fallen well below its own peak. Measuring
  // against the peak keeps loud claps and echoey rooms from counting as
  // "too long".
  if (state == CLAP1 || state == CLAP2) clapPeak = max(clapPeak, loud);
  bool clapOver = loud < fmaxf(release, clapPeak * CLAP_END);

  // Slowly follow the background level (about 2.5 s to adjust). Claps are
  // too short to move it much; a TV or music raises it within a few seconds.
  noise += (loud - noise) * 0.002f;
  if (noise < 5) noise = 5;

  prev2 = prev1;
  prev1 = loud;

  if ((int32_t)(now - muteUntil) < 0) return;

  if (onset) {
    Serial.printf("sound: loudness %d (needs %d)\n", loud, (int)trigger);
  }

  switch (state) {
    case IDLE:
      if (onset) {
        state = CLAP1;
        firstOnset = clapStart = now;
        clapPeak = loud;
      }
      break;

    case CLAP1:  // first clap: wait for it to die away
      if (clapOver) state = WAIT2;
      else if (now - clapStart > MAX_CLAP_MS) reject("first sound lasted too long");
      break;

    case WAIT2:  // between claps
      if (onset && now - firstOnset >= MIN_GAP_MS) {
        state = CLAP2;
        clapStart = now;
        clapPeak = loud;
      } else if (now - firstOnset > MAX_GAP_MS) {
        Serial.println("  single clap, ignored");
        state = IDLE;
      }
      break;

    case CLAP2:  // second clap: wait for it to die away
      if (clapOver) {
        state = CONFIRM;
        stateTime = now;
      } else if (now - clapStart > MAX_CLAP_MS) {
        reject("second sound lasted too long");
      }
      break;

    case CONFIRM:  // must stay quiet, or it was three claps or ongoing noise
      if (onset) reject("third sound");
      else if (now - stateTime >= QUIET_AFTER_MS) doubleClap();
      break;

    case REJECT:  // wait for a stretch of quiet before listening again
      if (!quiet) stateTime = now;
      else if (now - stateTime >= QUIET_AFTER_MS) state = IDLE;
      break;
  }
}
