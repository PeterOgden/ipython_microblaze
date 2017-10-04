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

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

from .library import Peripheral, Library
from .arduino_switch import ArduinoSwitch
from .pmod_switch import PmodSwitch

ArduinoPWM = Library('ArduinoPWM')

ArduinoPWM.declaration = R"""
typedef int pwm;

pwm pwm_connect(unsigned char port, unsigned char wire);
void pwm_generate_cycles(pwm timer, int period, int pulse);
void pwm_generate_us(pwm timer, int period, int pulse);
void pwm_stop(pwm timer);
"""

ArduinoPWM.definition = R"""
#include <arduino.h>
#include "xparameters.h"
#include "xtmrctr_l.h"


// D3, D5, D6, D9, D10, D11
char pwm_offsets[14] = {
    -1, -1, -1, 0, -1, 1, 2,
    -1, -1, 3, 4, 5, -1, -1
};

unsigned int base_addresses[6] = {
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_0_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_1_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_2_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_3_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_4_BASEADDR,
    XPAR_IOP3_MB3_TIMERS_SUBSYSTEM_MB3_TIMER_5_BASEADDR
};

typedef int pwm;

pwm pwm_connect(unsigned char port, unsigned char wire) {
    arduino_switch_init(0,0,0,0);
    int offset = arduino_switch_pwm_grove(port, wire);
    int timer = pwm_offsets[offset];
    return timer;
}

void pwm_generate_cycles(pwm timer, int period, int pulse) {
    if (timer >= 0) {
        unsigned int base_addr = base_addresses[timer];
        if (XTmrCtr_ReadReg(base_addr, 0, XTC_TCSR_OFFSET) != 0x296) {
            XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0x296);
            XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0x296);
        }
        XTmrCtr_WriteReg(base_addr, 0, XTC_TLR_OFFSET, period);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TLR_OFFSET, pulse);
    }
}

void pwm_generate_us(pwm timer, int period, int pulse) {
    pwm_generate_cycles(timer, period * 100, pulse * 100);
}

void pwm_stop(pwm timer) {
    if (timer >= 0) {
        unsigned int base_addr = base_addresses[timer];
        XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0);
    }
}

"""

ArduinoPWM.dependencies.append(ArduinoSwitch)

PmodPWM = Library('PmodPWM')

PmodPWM.declaration = R"""
typedef int pwm;

pwm pwm_connect(unsigned char port, unsigned char wire);
void pwm_generate_cycles(pwm timer, int period, int pulse);
void pwm_generate_us(pwm timer, int period, int pulse);
void pwm_stop(pwm timer);
"""

PmodPWM.definition = R"""
#include <pmod.h>
#include "xparameters.h"
#include "xtmrctr_l.h"


typedef int pwm;

pwm pwm_connect(unsigned char port, unsigned char wire) {
    pmod_switch_init();
    pmod_switch_pwm_grove(port, wire);
    return 0;
}

void pwm_generate_cycles(pwm timer, int period, int pulse) {
    unsigned int base_addr = XPAR_IOP1_MB1_TIMER_BASEADDR;
    if (XTmrCtr_ReadReg(base_addr, 0, XTC_TCSR_OFFSET) != 0x296) {
        XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0x296);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0x296);
    }
    XTmrCtr_WriteReg(base_addr, 0, XTC_TLR_OFFSET, period);
    XTmrCtr_WriteReg(base_addr, 1, XTC_TLR_OFFSET, pulse);
}

void pwm_generate_us(pwm timer, int period, int pulse) {
    pwm_generate_cycles(timer, period * 100, pulse * 100);
}

void pwm_stop(pwm timer) {
    if (timer >= 0) {
        unsigned int base_addr = XPAR_IOP1_MB1_TIMER_BASEADDR;
        XTmrCtr_WriteReg(base_addr, 0, XTC_TCSR_OFFSET, 0);
        XTmrCtr_WriteReg(base_addr, 1, XTC_TCSR_OFFSET, 0);
    }
}

"""

PmodPWM.dependencies.append(PmodSwitch)

PWM = Peripheral("PWM")
PWM.declaration = ArduinoPWM.declaration
PWM.implementations['Pmod'] = PmodPWM
PWM.implementations['Arduino'] = ArduinoPWM


