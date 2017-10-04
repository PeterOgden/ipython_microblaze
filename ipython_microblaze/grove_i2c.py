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

PmodI2C = Library("PmodI2C")

PmodI2C.declaration = R"""
void i2c_connect(unsigned char port);
void i2c_read(unsigned char address, unsigned char* data, int length);
void i2c_write(unsigned char address, unsigned char* data, int length);
"""

PmodI2C.definition = R"""
#include <pmod.h>

void i2c_connect(unsigned char port) {
    pmod_switch_init();
    pmod_switch_i2c_grove(port);
}

void i2c_write(unsigned char address, unsigned char* data, int length) {
    iic_write(XPAR_IIC_0_BASEADDR, address, data, length);
}

void i2c_read(unsigned char address, unsigned char* data, int length) {
    iic_read(XPAR_IIC_0_BASEADDR, address, data, length);
}
"""

PmodI2C.dependencies.append(PmodSwitch)


ArduinoI2C = Library("ArduinoI2C")

ArduinoI2C.declaration = PmodI2C.declaration

ArduinoI2C.definition = R"""
#include <arduino.h>

void i2c_connect(unsigned char port) {
    arduino_switch_init();
}

void i2c_write(unsigned char address, unsigned char* data, int length) {
    iic_write(XPAR_IIC_0_BASEADDR, address, data, length);
}

void i2c_read(unsigned char address, unsigned char* data, int length) {
    iic_read(XPAR_IIC_0_BASEADDR, address, data, length);
}
"""

ArduinoI2C.dependencies.append(ArduinoSwitch)

I2C = Peripheral("I2C")
I2C.declaration = PmodI2C.declaration
I2C.implementations["Pmod"] = PmodI2C
I2C.implementations["Arduino"] = ArduinoI2C


