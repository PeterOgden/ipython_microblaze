#pragma once

#include <mbio.h>

typedef unsigned int ledbar;

ledbar ledbar_open_grove(unsigned char port);
ledbar ledbar_open(mb_gpio data, mb_gpio clk);
void ledbar_set_level(ledbar, unsigned char i);
void ledbar_set_data(ledbar, const unsigned char* data);

