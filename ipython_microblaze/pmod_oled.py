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

import glob
from os import path
from .library import Library

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

PmodOLED = Library('PmodOLED')

PmodOLED.declaration = R"""
void oled_init();
void oled_clear();
void oled_print_string(char* string, int x, int y);
"""

PmodOLED.definition = R"""
#include "xparameters.h"
#include "xgpio.h"
#include "xspi_l.h"
#include "OledChar.h"
#include "OledGrph.h"
#include "pmod.h"

void OledInit(void);
void OledClearBuffer(void);
void OledUpdate(void);
void OledDvrInit(void);

void oled_init() {
    OledInit();
    OledDvrInit();
    OledClearBuffer();
    OledUpdate();
}

void oled_clear() {
    OledClearBuffer();
    OledUpdate();
}

void oled_print_string(char* string, int x, int y) {
    OledSetCursor(x, y);
    OledPutString(string);
    OledUpdate();
}

"""

_script_dir = path.dirname(path.realpath(__file__))
_source_dir = path.join(_script_dir, "sources", "pmod_oled")
PmodOLED.headers = glob.glob(_source_dir + '/*.h')
PmodOLED.sources = glob.glob(_source_dir + '/*.c')
