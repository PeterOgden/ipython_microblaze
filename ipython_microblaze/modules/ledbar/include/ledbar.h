#pragma once

#include <iop.h>

typedef struct {
    gpio data;
    gpio clk;
} ledbar;

ledbar ledbar_init(unsigned char port);
void ledbar_set_level(ledbar, unsigned char i);
void ledbar_set_data(ledbar, unsigned char data[10]);

