#pragma once

#define ASSIGN_FAILED -1

typedef unsigned short switch_handle;

void iop_switch_init();
switch_handle iop_switch_i2c_raw(unsigned char scl, unsigned char sda);
switch_handle iop_switch_i2c_grove(unsigned char port);
switch_handle iop_switch_gpio_raw(unsigned char pin);
switch_handle iop_switch_gpio_grove(unsigned char port, unsigned char wire);
switch_handle iop_switch_pwm_raw(unsigned char pin);
switch_handle iop_switch_pwm_grove(unsigned char port, unsigned char wire);
switch_handle iop_switch_analog_raw(unsigned char pin);
switch_handle iop_switch_analog_grove(unsigned char port, unsigned char wire);
