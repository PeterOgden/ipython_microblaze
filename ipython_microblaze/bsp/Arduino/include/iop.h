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

i2c    i2c_open_iop_pins(unsigned char scl, unsigned char sda);
i2c    i2c_open_iop_grove(unsigned char port);
gpio   gpio_open_iop_pin(unsigned char pin);
gpio   gpio_open_iop_grove(unsigned char port, unsigned char wire);
timer  timer_open_iop_pin(unsigned char pin);
timer  timer_open_iop_grove(unsigned char port, unsigned char wire);
analog analog_open_iop_pin(unsigned char pin);
analog analog_open_iop_grove(unsigned char port, unsigned char wire);
