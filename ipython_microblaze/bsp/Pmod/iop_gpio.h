#pragma once

#define GPIO_IN 1
#define GPIO_OUT 0

typedef int gpio;

gpio gpio_connect_grove(unsigned char port, unsigned char wire);
gpio gpio_connect(unsigned char wire);
void gpio_write(gpio channel, unsigned char value);
unsigned char gpio_read(gpio channel);
void gpio_set_direction(gpio channel, unsigned char direction);

