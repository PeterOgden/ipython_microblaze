#pragma once

enum {
GPIO_OUT = 0,
GPIO_IN = 1
};

typedef unsigned short gpio;

int gpio_num_devices();
gpio gpio_open_pin(int index, int channel, int pin);
gpio gpio_open_range(int index, int channel, int low, int high);
gpio gpio_open_all(int index, int channel);
void gpio_set_direction(gpio dev, int direction);
void gpio_write(gpio dev, int val);
int gpio_read(gpio dev);

