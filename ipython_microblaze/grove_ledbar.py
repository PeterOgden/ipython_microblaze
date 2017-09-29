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
from .pmod_switch import PmodSwitch
from .arduino_switch import ArduinoSwitch

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

PmodLEDBar = Library("PmodLEDBar")

PmodLEDBar.declaration = R"""
void ledbar_init(unsigned char port);
void ledbar_set_level(unsigned char i);
void ledbar_set_data(unsigned char data[10]);
"""
PmodLEDBar.definition = R"""
#include "pmod.h"
#include "xgpio_l.h"
#include "xgpio.h"
#include "unistd.h"

XGpio gpo;

void send_data(u8 data){
    int i;
    u8 data_state, clk_state, detect, data_internal;

    data_internal = data;
    // Working in 8-bit mode
    for (i = 0; i < 8; i++){
        /*
         * Read each bit of the data to be sent LSB first
         * Write it to the data_pin
         */
        data_state = (data_internal & 0x80) ? 0x00000001 : 0x00000000;
        XGpio_DiscreteWrite(&gpo, 1, data_state);

        // Read Clock pin and regenerate clock
        detect = XGpio_DiscreteRead(&gpo, 1);
        clk_state = (detect & 0x02) ? 0x00000000 : 0x00000001;
        clk_state = clk_state << 1;
        XGpio_DiscreteWrite(&gpo, 1, (clk_state & 2));

        // Shift Incoming data to fetch next bit
        data_internal = data_internal << 1;
    }
}

void latch_data(){
    int i;
    XGpio_DiscreteWrite(&gpo, 1, 0);
    delay_ms(10);
    // Generate four pulses on the data pin as per data sheet
    for (i = 0; i < 4; i++){
        XGpio_DiscreteWrite(&gpo, 1, 1);
        XGpio_DiscreteWrite(&gpo, 1, 0);
    }
}

void ledbar_set_level(u8 val) {
    val = 10 - val;
    send_data(0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(i >= val? 0xFF: 0x00);
    }
    send_data(0x00);
    send_data(0x00);
    latch_data();
}

void ledbar_set_data(u8 val[10]) {
    send_data(0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(val[i]);
    }
    send_data(0x00);
    send_data(0x00);
    latch_data();
}

void ledbar_init(unsigned char port) {
    pmod_switch_init();
    pmod_switch_grove_gpio(port, 0, 1);
    XGpio_Initialize(&gpo, XPAR_GPIO_0_DEVICE_ID);
    XGpio_SetDataDirection(&gpo, 1, 0);
}
"""

PmodLEDBar.dependencies.append(PmodSwitch)

ArduinoLEDBar = Library("ArduinoLEDBar")

ArduinoLEDBar.declaration = PmodLEDBar.declaration

ArduinoLEDBar.definition = R"""
#include "xgpio_l.h"
#include "xgpio.h"
#include "unistd.h"
#include "arduino.h"

XGpio gpo;

static int shift = 0;

void send_data(u8 data){
    int i;
    u8 data_state, clk_state, detect, data_internal;

    data_internal = data;
    // Working in 8-bit mode
    for (i = 0; i < 8; i++){
        /*
         * Read each bit of the data to be sent LSB first
         * Write it to the data_pin
         */
        data_state = (data_internal & 0x80) ? 0x00000001 : 0x00000000;
        XGpio_DiscreteWrite(&gpo, 1, data_state << shift);

        // Read Clock pin and regenerate clock
        detect = XGpio_DiscreteRead(&gpo, 1);
        clk_state = detect ^ (2 << shift);
        XGpio_DiscreteWrite(&gpo, 1, clk_state);

        // Shift Incoming data to fetch next bit
        data_internal = data_internal << 1;
    }
}

void latch_data(){
    int i;
    XGpio_DiscreteWrite(&gpo, 1, 0);
    delay_ms(10);
    // Generate four pulses on the data pin as per data sheet
    for (i = 0; i < 4; i++){
        XGpio_DiscreteWrite(&gpo, 1, 1 << shift);
        XGpio_DiscreteWrite(&gpo, 1, 0);
    }
}

void ledbar_set_level(u8 val) {
    val = 10 - val;
    send_data(0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(i >= val? 0xFF: 0x00);
    }
    send_data(0x00);
    send_data(0x00);
    latch_data();
}

void ledbar_set_data(u8 val[10]) {
    send_data(0x00);
    for (int i = 0; i < 10; ++i) {
        send_data(val[i]);
    }
    send_data(0x00);
    send_data(0x00);
    latch_data();
}

void ledbar_init(unsigned char port) {
    arduino_switch_init();
    shift = arduino_switch_grove_gpio(port);
    XGpio_Initialize(&gpo, XPAR_GPIO_0_DEVICE_ID);
    XGpio_SetDataDirection(&gpo, 1, 0);
}
"""

ArduinoLEDBar.dependencies.append(ArduinoSwitch)

LEDBar = Peripheral("LEDBar")
LEDBar.declaration = PmodLEDBar.declaration
LEDBar.implementations["Pmod"] = PmodLEDBar
LEDBar.implementations["Arduino"] = ArduinoLEDBar
