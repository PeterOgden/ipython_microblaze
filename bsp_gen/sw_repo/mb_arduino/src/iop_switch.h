#pragma once
#include <mbio.h>

#define ASSIGN_FAILED -1

enum {
G1, G2, G3, G4, G5, G6, G7
};

enum {
A1, A2, A3, A4
};

enum {
I2C = 0xFF
};

void iop_switch_init();
mb_i2c iop_switch_i2c_raw(unsigned char scl, unsigned char sda);
mb_i2c iop_switch_i2c_grove(unsigned char port);
mb_gpio iop_switch_gpio_raw(unsigned char pin);
mb_gpio iop_switch_gpio_grove(unsigned char port, unsigned char wire);
mb_timer iop_switch_pwm_raw(unsigned char pin);
mb_timer iop_switch_pwm_grove(unsigned char port, unsigned char wire);
mb_adc iop_switch_analog_raw(unsigned char pin);
mb_adc iop_switch_analog_grove(unsigned char port, unsigned char wire);
