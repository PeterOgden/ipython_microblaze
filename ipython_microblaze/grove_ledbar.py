#   Copyright (c) 2016, Xilinx, Inc.
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   1.  Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#   2.  Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
#   3.  Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#   OR BUSINESS INTERRUPTION). HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#   WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#   OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#   ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from .library import Peripheral, Library
from .grove_gpio import PmodGPIO
from .grove_gpio import ArduinoGPIO

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

PmodLEDBar = Library("PmodLEDBar")

PmodLEDBar.declaration = R"""

typedef struct {
    short data;
    short clk;
} ledbar;

ledbar ledbar_init(unsigned char port);
void ledbar_set_level(ledbar, unsigned char i);
void ledbar_set_data(ledbar, unsigned char data[10]);

"""
PmodLEDBar.definition = R"""
#include "pmod.h"

typedef struct {
    short data;
    short clk;
} ledbar;

void send_data(ledbar info, u8 data){
    int i;
    u8 data_state, clk_state, detect, data_internal;

    data_internal = data;

    int clkval = 0;
    // Pad the upper 8 bits
    for (i = 0; i < 8; ++i) {
        clkval ^= 1;
        gpio_write(info.data, 0);
        gpio_write(info.clk, clkval);
    }

    // Working in 8-bit mode
    for (i = 0; i < 8; i++){
        /*
         * Read each bit of the data to be sent LSB first
         * Write it to the data_pin
         */
        data_state = (data_internal & 0x80) ? 0x00000001 : 0x00000000;
        gpio_write(info.data, data_state);
        clkval ^= 1;
        gpio_write(info.clk, clkval);

        // Shift Incoming data to fetch next bit
        data_internal = data_internal << 1;
    }
}

void latch_data(ledbar info){
    int i;
    gpio_write(info.data, 0);
    delay_ms(10);
    // Generate four pulses on the data pin as per data sheet
    for (i = 0; i < 4; i++){
        gpio_write(info.data, 1);
        gpio_write(info.data, 0);
    }
}

void ledbar_set_level(ledbar info, u8 val) {
    val = 10 - val;
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, i >= val? 0xFF: 0x00);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

void ledbar_set_data(ledbar info, u8 val[10]) {
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, val[i]);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

ledbar ledbar_init(unsigned char port) {
    ledbar info;
    info.data = gpio_connect(port, 0);
    info.clk = gpio_connect(port, 1);
    gpio_set_direction(info.data, GPIO_OUT);
    gpio_set_direction(info.clk, GPIO_OUT);
    return info;
}
"""

PmodLEDBar.dependencies.append(PmodGPIO)

ArduinoLEDBar = Library("ArduinoLEDBar")

ArduinoLEDBar.declaration = PmodLEDBar.declaration

ArduinoLEDBar.definition = R"""
#include "arduino.h"

typedef struct {
    short data;
    short clk;
} ledbar;

void send_data(ledbar info, u8 data){
    int i;
    u8 data_state, clk_state, detect, data_internal;

    data_internal = data;

    int clkval = 0;
    // Pad the upper 8 bits
    for (i = 0; i < 8; ++i) {
        clkval ^= 1;
        gpio_write(info.data, 0);
        gpio_write(info.clk, clkval);
    }

    // Working in 8-bit mode
    for (i = 0; i < 8; i++){
        /*
         * Read each bit of the data to be sent LSB first
         * Write it to the data_pin
         */
        data_state = (data_internal & 0x80) ? 0x00000001 : 0x00000000;
        gpio_write(info.data, data_state);
        clkval ^= 1;
        gpio_write(info.clk, clkval);

        // Shift Incoming data to fetch next bit
        data_internal = data_internal << 1;
    }
}

void latch_data(ledbar info){
    int i;
    gpio_write(info.data, 0);
    delay_ms(10);
    // Generate four pulses on the data pin as per data sheet
    for (i = 0; i < 4; i++){
        gpio_write(info.data, 1);
        gpio_write(info.data, 0);
    }
}

void ledbar_set_level(ledbar info, u8 val) {
    val = 10 - val;
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, i >= val? 0xFF: 0x00);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

void ledbar_set_data(ledbar info, u8 val[10]) {
    send_data(info, 0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(info, val[i]);
    }
    send_data(info, 0x00);
    send_data(info, 0x00);
    latch_data(info);
}

ledbar ledbar_init(unsigned char port) {
    ledbar info;
    info.data = gpio_connect(port, 0);
    info.clk = gpio_connect(port, 1);
    gpio_set_direction(info.data, GPIO_OUT);
    gpio_set_direction(info.clk, GPIO_OUT);
    return info;
}
"""

ArduinoLEDBar.dependencies.append(ArduinoGPIO)

LEDBar = Peripheral("LEDBar")
LEDBar.declaration = PmodLEDBar.declaration
LEDBar.implementations["Pmod"] = PmodLEDBar
LEDBar.implementations["Arduino"] = ArduinoLEDBar
