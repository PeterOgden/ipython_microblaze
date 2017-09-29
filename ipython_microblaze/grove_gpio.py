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

PmodGPIO = Library("PmodGPIO")

PmodGPIO.declaration = R"""

#define GPIO_IN 1
#define GPIO_OUT 0

void gpio_connect(unsigned char port);
void gpio_write(unsigned char channel, unsigned char value);
unsigned char gpio_read(unsigned char channel);
void gpio_set_direction(unsigned char channel, unsigned char direction);

"""

PmodGPIO.definition = R"""
#include "xgpio_l.h"
#include "xgpio.h"

unsigned int values = 0;
unsigned int tristate = 0;
XGpio gpo;

void gpio_connect(unsigned char port) {
    XGpio_Initialize(&gpo, XPAR_GPIO_0_DEVICE_ID);
    pmod_switch_init();
    pmod_switch_grove_gpio(port, 0, 1);
}

void gpio_write(unsigned char channel, unsigned char value) {
    unsigned m = 1 << channel;
    if (value) {
        values |= m;
    } else {
        values &= ~m;
    }
    XGpio_DiscreteWrite(&gpo, 1, values);
}

unsigned char gpio_read(unsigned char channel) {
    unsigned int v = XGpio_DiscreteRead(&gpo, 1);
    return (v >> channel) & 1;   
}

void gpio_set_direction(unsigned char channel, unsigned char direction) {
    unsigned int m = 1 << channel;
    if (direction) {
        tristate |= m;
    } else {
        tristate &= ~m;
    }
    XGpio_SetDataDirection(&gpo, 1, tristate);
}


"""

PmodGPIO.dependencies.append(PmodSwitch)

ArduinoGPIO = Library("ArduinoGPIO")

ArduinoGPIO.declaration = PmodGPIO.declaration

ArduinoGPIO.definition = R"""
#include "xgpio_l.h"
#include "xgpio.h"

unsigned int values = 0;
unsigned int tristate = 0;
unsigned char shift = 0;
XGpio gpo;

void gpio_connect(unsigned char port) {
    XGpio_Initialize(&gpo, XPAR_GPIO_0_DEVICE_ID);
    arduino_switch_init();
    shift = arduino_switch_grove_gpio(port);
}

void gpio_write(unsigned char channel, unsigned char value) {
    unsigned m = 1 << (channel + shift);
    if (value) {
        values |= m;
    } else {
        values &= ~m;
    }
    XGpio_DiscreteWrite(&gpo, 1, values);
}

unsigned char gpio_read(unsigned char channel) {
    unsigned int v = XGpio_DiscreteRead(&gpo, 1);
    return (v >> (channel + shift)) & 1;   
}

void gpio_set_direction(unsigned char channel, unsigned char direction) {
    unsigned int m = 1 << (channel + shift);
    if (direction) {
        tristate |= m;
    } else {
        tristate &= ~m;
    }
    XGpio_SetDataDirection(&gpo, 1, tristate);
}



"""

ArduinoGPIO.dependencies.append(ArduinoSwitch)

GPIO = Peripheral("GPIO")
GPIO.declaration = PmodGPIO.declaration
GPIO.implementations["Pmod"] = PmodGPIO
GPIO.implementations["Arduino"] = ArduinoGPIO
