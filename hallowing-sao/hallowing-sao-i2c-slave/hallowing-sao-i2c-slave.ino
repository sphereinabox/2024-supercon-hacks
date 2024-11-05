#define PIN_NEOPIXELS 8
#define PIN_S1 A2
#define PIN_S2 A3
#define PIN_S3 A4
#define PIN_S4 A5

#include <Adafruit_NeoPixel.h>
#include <Wire.h>

volatile uint8_t i2c_incoming_bytes[32] = { 0 };
volatile uint8_t i2c_outgoing_bytes[32] = { 0 };

void wire_onRecieve(int byteCount) {
  int i = 0;
  while (Wire.available() && i < 32) {
    int rxbyte = Wire.read();
    i2c_incoming_bytes[i++] = (uint8_t)rxbyte;
  }
}

void wire_onRequest(void) {
  for (int i = 0; i < 32; i++) {
    Wire.write(i2c_outgoing_bytes[i]);
  }
}

Adafruit_NeoPixel strip(4, PIN_NEOPIXELS, NEO_GRB + NEO_KHZ800);

void setup() {
  pinMode(PIN_S1, INPUT_PULLUP);
  pinMode(PIN_S2, INPUT_PULLUP);
  pinMode(PIN_S3, INPUT_PULLUP);
  pinMode(PIN_S4, INPUT_PULLUP);

  Wire.begin(0x4A);
  Wire.onReceive(wire_onRecieve);
  Wire.onRequest(wire_onRequest);

  strip.begin();
  strip.show();
  strip.setBrightness(128);  // 50 is reasonably dim for indoors

  // set some incoming colors
  i2c_incoming_bytes[1] = 255;
  i2c_incoming_bytes[2] = 0;
  i2c_incoming_bytes[3] = 0;

  i2c_incoming_bytes[4] = 0;
  i2c_incoming_bytes[5] = 255;
  i2c_incoming_bytes[6] = 0;

  i2c_incoming_bytes[7] = 0;
  i2c_incoming_bytes[8] = 0;
  i2c_incoming_bytes[9] = 255;

  i2c_incoming_bytes[10] = 127;
  i2c_incoming_bytes[11] = 127;
  i2c_incoming_bytes[12] = 127;
}

void loop() {
  // set LEDs from i2c input:
  strip.setPixelColor(0,
                      i2c_incoming_bytes[1],
                      i2c_incoming_bytes[2],
                      i2c_incoming_bytes[3]);

  strip.setPixelColor(1,
                      i2c_incoming_bytes[4],
                      i2c_incoming_bytes[5],
                      i2c_incoming_bytes[6]);

  strip.setPixelColor(2,
                      i2c_incoming_bytes[7],
                      i2c_incoming_bytes[8],
                      i2c_incoming_bytes[9]);

  strip.setPixelColor(3,
                      i2c_incoming_bytes[10],
                      i2c_incoming_bytes[11],
                      i2c_incoming_bytes[12]);

  strip.show();

  // switches are active low
  uint8_t switch_bits = 0x0;
  int s1 = digitalRead(PIN_S1);
  if (!s1) switch_bits |= 0x1;
  int s2 = digitalRead(PIN_S2);
  if (!s2) switch_bits |= 0x2;
  int s3 = digitalRead(PIN_S3);
  if (!s3) switch_bits |= 0x4;
  int s4 = digitalRead(PIN_S4);
  if (!s4) switch_bits |= 0x8;

  i2c_outgoing_bytes[0] = switch_bits;

  delay(10);
}
