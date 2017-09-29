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

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

PmodGroveADC = Library("PmodGroveADC")

PmodGroveADC.declaration = R"""
void adc_init(unsigned char port);
float adc_read_sample();
"""

PmodGroveADC.definition = R"""
#include "pmod.h"

#define IIC_ADDRESS 0x50

#define V_REF 3.10

// ADC Registers
#define REG_ADDR_RESULT        0x00
#define REG_ADDR_ALERT         0x01
#define REG_ADDR_CONFIG        0x02
#define REG_ADDR_LIMITL        0x03
#define REG_ADDR_LIMITH        0x04
#define REG_ADDR_HYST          0x05
#define REG_ADDR_CONVL         0x06
#define REG_ADDR_CONVH         0x07

u32 read_adc(u8 reg){
   u8 data_buffer[2];
   u32 sample;

   data_buffer[0] = reg; // Set the address pointer register
   iic_write(XPAR_IIC_0_BASEADDR, IIC_ADDRESS, data_buffer, 1);

   iic_read(XPAR_IIC_0_BASEADDR, IIC_ADDRESS,data_buffer,2);
   sample = ((data_buffer[0]&0x0f) << 8) | data_buffer[1];
   return sample;
}


// Write a number of bytes to a Register
// Maximum of 2 data bytes can be written in one transaction
void write_adc(u8 reg, u32 data, u8 bytes){
   u8 data_buffer[3];
   data_buffer[0] = reg;
   if(bytes ==2){
      data_buffer[1] = data & 0x0f; // Bits 11:8
      data_buffer[2] = data & 0xff; // Bits 7:0
   }else{
      data_buffer[1] = data & 0xff; // Bits 7:0
   }

   iic_write(XPAR_IIC_0_BASEADDR, IIC_ADDRESS, data_buffer, bytes+1);
}

void adc_init(unsigned char port) {
    pmod_switch_init();
    pmod_switch_grove_i2c(port);
    write_adc(REG_ADDR_CONFIG, 0x20, 1);
}

float adc_read_sample() {
    return (float)((read_adc(REG_ADDR_RESULT))*V_REF*2/4096);
}
"""

PmodGroveADC.dependencies.append(PmodSwitch)

GroveADC = Peripheral("GroveADC")
GroveADC.declaration = PmodGroveADC.declaration
GroveADC.implementations["Pmod"] = PmodGroveADC
