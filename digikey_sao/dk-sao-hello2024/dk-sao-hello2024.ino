/*
Using ATMEL-SAM-ICE debug probe

Mattairtech arduino platform
board: generic D11C14A
bootloader size: 4kb bootloader?
clock source: internal oscilator
build options: config.h disabled
float point: ???
serial_config: one_uart_one_wire_no_spi (or no_uart_one_wire_one_spi?)
timer:
usb: usb disabled
*/

#include <Wire.h>

// see pinout table on https://github.com/mattairtech/ArduinoCore-samd/blob/master/variants/Generic_D11C14A/README.md
const unsigned int MYPIN_LED1 =  5; // PA05 can PWM
const unsigned int MYPIN_LED2 = 24; // PA24 no PWM
const unsigned int MYPIN_LED3 = 25; // PA25 no PWM
const unsigned int MYPIN_LED4 =  9; // PA09 can PWM
const unsigned int MYPIN_SPKR = 8; // PA08 can PWM
const unsigned int MYPIN_SDA = 14; // PA14
const unsigned int MYPIN_SCL = 15; // PA15
const unsigned int MYPIN_CAPSENSE = A2; // PA04

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

void setup() {
  // put your setup code here, to run once:
  pinMode(MYPIN_LED1, OUTPUT);
  pinMode(MYPIN_LED2, OUTPUT);
  pinMode(MYPIN_LED3, OUTPUT);
  pinMode(MYPIN_LED4, OUTPUT);
  pinMode(MYPIN_SPKR, OUTPUT);

  Wire.begin(0x4B); // chosen by random.org 1..100
  Wire.onReceive(wire_onRecieve);
  Wire.onRequest(wire_onRequest);
}

void loop() {
  bool prev_play_tone = false;
  uint32_t prev_tone_freq = 0;
  uint16_t fakepwm_counter = 1; // counts 1..256
  while (true) {
    uint32_t tone_freq = 
      ((uint32_t)i2c_incoming_bytes[8]) |
      ((uint32_t)i2c_incoming_bytes[9] << 8) |
      ((uint32_t)i2c_incoming_bytes[10] << 16) |
      ((uint32_t)i2c_incoming_bytes[11] << 24);
    bool play_tone = (i2c_incoming_bytes[5] != 0);

    if (play_tone && (
      (tone_freq != prev_tone_freq) || (play_tone != prev_play_tone))) {
        tone(MYPIN_SPKR, tone_freq);
    }
    if (!play_tone && (play_tone != prev_play_tone)) {
      noTone(MYPIN_SPKR);
    }

    // pwm works
    analogWrite(MYPIN_LED1, i2c_incoming_bytes[1]);

    // analogWrite(MYPIN_LED2, i2c_incoming_bytes[2]);
    // analogWrite(MYPIN_LED3, i2c_incoming_bytes[3]);
    // fake pwm on MYPIN_LED2 and MYPIN_LED3
    digitalWrite(MYPIN_LED2, i2c_incoming_bytes[2] >= fakepwm_counter);
    digitalWrite(MYPIN_LED3, i2c_incoming_bytes[3] >= fakepwm_counter);

    // pwm works
    analogWrite(MYPIN_LED4, i2c_incoming_bytes[4]);

    fakepwm_counter = (fakepwm_counter & 0xFF) + 1;
  }
}
