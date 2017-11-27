#pragma once

typedef unsigned short i2c;

int i2c_num_devices();
i2c i2c_open(int index);
int i2c_read(i2c device, unsigned char address, char* data, int length);
int i2c_write(i2c device, unsigned char address, const char* data, int length);

