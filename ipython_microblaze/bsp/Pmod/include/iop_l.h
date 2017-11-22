#pragma once

#include <iop_switch.h>

void iop_i2c_write(switch_handle, unsigned int addr, unsigned char* data, unsigned char length);
void iop_i2c_read(switch_handle, unsigned int addr, unsigned char* data, unsigned char length);
int iop_gpio_read(switch_handle);
void iop_gpio_write(switch_handle, unsigned char value);
void iop_gpio_set_direction(switch_handle, unsigned char dir);
void iop_pwm_generate_cycles(switch_handle, int period, int pulse);
void iop_pwm_stop(switch_handle);
int iop_analog_read(switch_handle);
int iop_analog_range(switch_handle);
float iop_analog_vref(switch_handle);
void iop_delay(unsigned int us);
