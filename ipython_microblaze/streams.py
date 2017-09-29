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

import numpy as np

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"


class SimpleMBChannel:
    def __init__(self, buffer, offset=0, length=0):
        self.control_array = np.frombuffer(buffer, count=2,
                                           offset=offset, dtype=np.uint32)
        if not length:
            length = len(buffer) - offset
        self.data_array = np.frombuffer(buffer, count=(length - 8),
                                        offset=offset + 8, dtype=np.uint8)
        self.length = length - 8

    def write(self, b):
        written = int(self.control_array[0])
        read = self._safe_control_read(1)
        available = (read - written - 1 + 2 * self.length) % self.length
        to_write = min(len(b), available)
        write_array = np.fromstring(b, np.uint8)
        end_block = min(to_write, self.length - written)
        self.data_array[written:written + end_block] = write_array[0:end_block]
        # Automatically wrap the write if necessary
        if end_block < to_write:
            self.data_array[0:to_write-end_block] = \
                write_array[end_block:to_write]
        # Atomically increase the write pointer to make data handling easier
        self.control_array[0] = (written + to_write) % self.length
        return to_write

    def bytes_available(self):
        written = int(self._safe_control_read(0))
        read = self._safe_control_read(1)
        available = (written - read + self.length) % self.length
        return available

    def buffer_space(self):
        written = int(self.control_array[0])
        read = self._safe_control_read(1)
        available = (read - written - 1 + 2 * self.length) % self.length
        return available

    def read(self):
        written = int(self._safe_control_read(0))
        read = self.control_array[1]
        available = (written - read + self.length) % self.length
        if available == 0:
            return None
        read_array = np.empty([available], dtype=np.uint8)
        end_block = min(available, self.length - read)
        read_array[0:end_block] = self.data_array[read:read + end_block]
        if end_block < available:
            read_array[end_block:available] = \
                self.data_array[0:available - end_block]
        self.control_array[1] = (read + available) % self.length
        return read_array.tobytes()

    def _safe_control_read(self, index):
        last_value = self.control_array[index]
        value = self.control_array[index]
        while value != last_value:
            last_value = value
            value = self.control_array[index]
        return value


class SimpleMBStream:
    def __init__(self, iop):
        self.read_channel = SimpleMBChannel(iop.mmio.mem, offset=0xF800,
                                            length=0x800)
        self.write_channel = SimpleMBChannel(iop.mmio.mem, offset=0xF000,
                                             length=0x800)

    def read(self):
        return self.read_channel.read()

    def write(self, b):
        return self.write_channel.write(b)

    def bytes_available(self):
        return self.read_channel.bytes_available()

    def buffer_space(self):
        return self.write_channel.buffer_space()


class InterruptMBStream(SimpleMBStream):
    def __init__(self, iop):
        super().__init__(iop)
        self.interrupt = iop.interrupt

    async def read_async(self):
        data = self.read()
        while not data:
            await self.interrupt.wait()
            data = self.read()
            self.interrupt.clear()
        return data
