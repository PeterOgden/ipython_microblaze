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

PmodSwitch = Library("PmodSwitch")

PmodSwitch.declaration = R"""
#define G1 0
#define G2 1
#define G3 2
#define G4 3

void pmod_switch_init();
void pmod_switch_grove_i2c(unsigned char port);
void pmod_switch_grove_gpio(unsigned char port, unsigned char channel0,
                            unsigned char channel1);

"""

PmodSwitch.definition = R"""
#include "pmod.h"

static unsigned char grove_port_map[4][2] = {
    {0, 4}, {1, 5}, {7, 3}, {6, 2}
};

static char assignments[16];
static char uses[16];
static char initialised;

void pmod_switch_init() {
    if (initialised) return;
    pmod_init(0, 0);
    for (int i = 0; i < 16; ++i) {
        assignments[i] = i;
        uses[i] = i;
    }
    initialised = 1;
}

static void commit_assignments() {
    config_pmod_switch(
        assignments[0],
        assignments[1],
        assignments[2],
        assignments[3],
        assignments[4],
        assignments[5],
        assignments[6],
        assignments[7]
    );
}

static void assign_connection(unsigned char input, unsigned char output) {
    if (assignments[input] == output) return;
    char prev_output = assignments[input];
    char prev_input = uses[output];
    assignments[prev_input] = prev_output;
    uses[prev_output] = prev_input;
    assignments[input] = output;
    uses[output] = input;
}

void pmod_switch_grove_gpio(unsigned char port, unsigned channel0,
                            unsigned char channel1) {
    assign_connection(grove_port_map[port][0], channel0);
    assign_connection(grove_port_map[port][1], channel1);
    commit_assignments();
}

void pmod_switch_grove_i2c(unsigned char port) {
    assign_connection(grove_port_map[port][0], SCL);
    assign_connection(grove_port_map[port][1], SDA);
    commit_assignments();
}

"""
