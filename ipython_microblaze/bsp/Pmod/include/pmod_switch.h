#pragma once

#define G1 0
#define G2 1
#define G3 2
#define G4 3

void pmod_switch_init();
void pmod_switch_i2c_grove(unsigned char port);
void pmod_switch_i2c_raw(unsigned char scl, unsigned char sda);
int pmod_switch_gpio_grove(unsigned char port, unsigned char wire);
int pmod_switch_gpio_raw(unsigned char pin);
void pmod_switch_pwm_grove(unsigned char port, unsigned char wire);
void pmod_switch_pwm_raw(unsigned char pin);

