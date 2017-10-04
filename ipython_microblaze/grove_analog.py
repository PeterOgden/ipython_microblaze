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

from .arduino_switch import ArduinoSwitch
from .library import Peripheral, Library


ArduinoAnalog = Library("ArduinoAnalog")

ArduinoAnalog.declaration = R"""
typedef int analog;

analog analog_connect(unsigned char port, unsigned char wire);
int analog_read_raw(analog port);
float analog_read(analog port);

"""

ArduinoAnalog.definition = R"""
#include <arduino.h>
#include <xparameters.h>
#include <xsysmon.h>
typedef int analog;

#define VREF 3.3f
static const float VConv = VREF / 65536;

#define SYSMON_DEVICE_ID XPAR_SYSMON_0_DEVICE_ID

static char adc_offsets[6] = {
    1, 9, 6, 15, 5, 13
};
static char initialised = 0;

static XSysMon SysMonInst;
XSysMon_Config *SysMonConfigPtr;
XSysMon *SysMonInstPtr = &SysMonInst;

analog analog_connect(unsigned char port, unsigned char wire) {
    if (!initialised) {
         // SysMon Initialize
        SysMonConfigPtr = XSysMon_LookupConfig(SYSMON_DEVICE_ID);
        if(SysMonConfigPtr == NULL)
            xil_printf("SysMon LookupConfig failed.\n\r");
        unsigned int xStatus = XSysMon_CfgInitialize(SysMonInstPtr, SysMonConfigPtr,
                                        SysMonConfigPtr->BaseAddress);
        if(XST_SUCCESS != xStatus)
            xil_printf("SysMon CfgInitialize failed\r\n");
        // Clear the old status
        XSysMon_GetStatus(SysMonInstPtr);
        arduino_switch_init();
        initialised = 1;
    }
    return arduino_switch_analog_grove(port, wire);
}

int analog_read_raw(analog port) {
    int offset = adc_offsets[port];
    return XSysMon_GetAdcData(SysMonInstPtr, XSM_CH_AUX_MIN + offset);
}

float analog_read(analog port) {
    int raw = analog_read_raw(port);
    return raw * VConv;
}

"""

ArduinoAnalog.dependencies.append(ArduinoSwitch)

Analog = Peripheral("Analog")

Analog.declaration = ArduinoAnalog.declaration

Analog.implementations["Arduino"] = ArduinoAnalog


