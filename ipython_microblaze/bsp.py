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

from os import path, listdir
import re

class Module:
    def __init__(self, root, compatible=None):
        self.include_path = [
            path.join(root, 'include')
        ]
        self.library_path = []
        self.libraries = []
        library_path = path.join(root, 'lib')
        if path.isdir(library_path):
            self.library_path.append(library_path)
            for f in listdir(self.library_path[0]):
                 match = re.match('lib(.*)\.(?:a|so)', f)
                 if match:
                     self.libraries.append(match.group(1))

        self.sources = []
        if path.isdir(path.join(root, 'src')):
            for f in listdir(path.join(root, 'src')):
                match = re.match('.*\.(c|cpp)$', f)
                if match:
                    self.sources.append(path.join(root, 'src', f))
        if compatible is None:
            compatible_file = path.join(root, 'compatible.txt')
            if path.exists(compatible_file):
                with open(compatible_file, 'r') as f:
                    compatible = f.read().split('\n')
        self.compatible = compatible
        self.header = ""
        for f in listdir(path.join(root, 'include')):
             if re.match(".*\.h$", f):
                 with open(path.join(root, 'include', f), 'r') as data:
                     self.header += data.read()

class BSPInstance:
    def __init__(self, root):
        self.include_path = [
            path.join(root, 'include')
        ]
        self.library_path = [
            path.join(root, 'lib')
        ]
        self.libraries = ['xil']
        self.linker_script = path.join(root, 'lscript.ld')
        self.cflags = [
            '-Os', '-lxil', '-mlittle-endian',
            '-mcpu=v9.6', '-mxl-soft-mul'
        ]
        self.ldflags = {
            '-Wl,--no-relax'
        } 
        self.sources = []
        if path.isdir(path.join(root, 'src')):
            for f in listdir(path.join(root, 'src')):
                match = re.match('.*\.(c|cpp)$', f)
                if match:
                    self.sources.append(path.join(root, 'src', f))


SCRIPT_DIR = path.dirname(path.realpath(__file__))
BSP_DIR = path.join(SCRIPT_DIR, 'bsp')
MODULE_DIR = path.join(SCRIPT_DIR, 'modules')

BSPs = {}
Modules = {}

for filename in listdir(BSP_DIR):
    f = path.join(BSP_DIR, filename)
    if path.isdir(f) and path.exists(path.join(f, 'lscript.ld')):
        BSPs[filename] = BSPInstance(f)

for filename in listdir(MODULE_DIR):
    f = path.join(MODULE_DIR, filename)
    if path.isdir(f):
        Modules[filename] = Module(f)
