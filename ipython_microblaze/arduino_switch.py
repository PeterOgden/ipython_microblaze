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

from .library import Library

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

ArduinoSwitch = Library("ArduinoSwitch")

ArduinoSwitch.declaration = R"""
#define G1 0
#define G2 1
#define G3 2
#define G4 3
#define G5 4
#define G6 5
#define G7 6

#define A1 0
#define A2 1
#define A3 2
#define A4 3

void arduino_switch_init();
int arduino_switch_gpio_grove(unsigned char port, unsigned char wire);
int arduino_switch_gpio_raw(unsigned char pin);
int arduino_switch_analog_grove(unsigned char port, unsigned char wire);
int arduino_switch_analog_raw(unsigned char pin);
int arduino_switch_pwm_grove(unsigned char port, unsigned char wire);
int arduino_switch_pwm_raw(unsigned char pin);
"""

ArduinoSwitch.definition = R"""
#include <arduino.h>
#include <arduino_io_switch.h>

char analog_pins[6];
char uart_pin;
char digital_pins[14];

static char pin_offsets[7] = {
    2, 3, 4, 6, 8, 10, 12
};

static char analog_offsets[4] = {
    0, 2, 3, 4
};

static void commit_assignments() {
    config_arduino_switch(
        analog_pins[0],
        analog_pins[1],
        analog_pins[2],
        analog_pins[3],
        analog_pins[4],
        analog_pins[5],
        uart_pin,
        digital_pins[2],
        digital_pins[3],
        digital_pins[4],
        digital_pins[5],
        digital_pins[6],
        digital_pins[7],
        digital_pins[8],
        digital_pins[9],
        digital_pins[10],
        digital_pins[11],
        digital_pins[12],
        digital_pins[13]
    );

}

void arduino_switch_init() {
    arduino_init(0, 0, 0, 0);
    commit_assignments();
}

int arduino_switch_gpio_raw(unsigned char pin) {
    digital_pins[pin] = D_GPIO;
    commit_assignments();
    return pin;
}
int arduino_switch_gpio_grove(unsigned char port, unsigned char wire) {
    return arduino_switch_gpio_raw(pin_offsets[port] + wire);
}

int arduino_switch_analog_raw(unsigned char pin) {
    analog_pins[pin] = A_GPIO;
    commit_assignments();
    return pin;
}
int arduino_switch_analog_grove(unsigned char port, unsigned char wire) {
    return arduino_switch_analog_raw(analog_offsets[port] + wire);
}

int arduino_switch_pwm_raw(unsigned char pin) {
    digital_pins[pin] = D_PWM;
    commit_assignments();
    return pin;
}

int arduino_switch_pwm_grove(unsigned char port, unsigned char wire) {
    return arduino_switch_pwm_raw(pin_offsets[port] + wire);
}
"""
