#pragma once

typedef unsigned short analog;

int analog_num_devices();
analog analog_open(int index);
int analog_read_raw(analog device);
float analog_read(analog device);
int analog_range(analog device);
float analog_vref(analog device);
