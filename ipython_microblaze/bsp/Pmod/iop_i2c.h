#pragma once

typedef int i2c;

i2c i2c_connect_grove(unsigned char port);
i2c i2c_connect_raw(unsigned char sda, unsigned chane sck);
void i2c_read(i2c instance, unsigned char address, unsigned char* data, int length);
void i2c_write(i2c instance, unsigned char address, unsigned char* data, int length);
