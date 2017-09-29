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

from pynq.lib import PynqMicroblaze
from pynq import PL

from os import path
import tempfile
import shutil

from .streams import InterruptMBStream
from .library import Peripheral

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"

_script_dir = path.dirname(path.realpath(__file__))
BSP_ROOT_DIR = path.join(_script_dir, "bsp")


class _DependencyResolution:
    def __init__(self, libraries):
        self.added = set()
        self.total_libs = []
        for l in libraries:
            self.add_library(l)

    def add_library(self, lib):
        if lib.name not in self.added:
            for d in lib.dependencies:
                self.add_library(d)
            self.total_libs.append(lib)
            self.added.add(lib.name)


def _resolve_dependencies(libraries):
    resolver = _DependencyResolution(libraries)
    return resolver.total_libs


class MicroblazeProgram(PynqMicroblaze):
    @staticmethod
    def _real_library(library, mbtype):
        if type(library) is Peripheral:
            if mbtype in library.implementations:
                return library.implementations[mbtype]
            else:
                raise RuntimeError("Could not find a implementation of " +
                                   library.name + " for mbtype " + mbtype)
        else:
            return library

    def __init__(self, mb_info, program_text, libraries=[]):
        from subprocess import run, PIPE
        bsp_dir = path.join(BSP_ROOT_DIR, mb_info['mbtype'])
        if not path.exists(bsp_dir):
            raise RuntimeError("Could not find BSP for Microblaze type" +
                               mb_info['mbtype'])
        real_libs = [MicroblazeProgram._real_library(l, mb_info['mbtype'])
                     for l in libraries]
        all_libs = _resolve_dependencies(real_libs)

        with tempfile.TemporaryDirectory() as tempdir:
            files = [path.join(tempdir, 'main.c')]
            args = ['mb-gcc', '-o', path.join(tempdir, 'a.out'), '-Os',
                    '-I', path.join(bsp_dir, 'include'),
                    '-L', path.join(bsp_dir, 'lib'),
                    '-lxil', f'-Wl,{bsp_dir}/lscript.ld', '-mlittle-endian',
                    '-mcpu=v9.6', '-mxl-soft-mul', '-Wl,--no-relax']

            with open(path.join(tempdir, 'main.c'), 'w') as f:
                for lib in all_libs:
                    deps = _resolve_dependencies(lib.dependencies)
                    f.write(f'#line 1 "{lib.name}.declaration"\n')
                    f.write(lib.declaration)
                    libsrc = path.join(tempdir, f"{lib.name}.c")
                    with open(libsrc, 'w') as libfile:
                        for d in deps:
                            libfile.write(f'#line 1 "{d.name}.declaration"\n')
                            libfile.write(d.declaration)
                        libfile.write(f'#line 1 "{lib.name}.definition"\n')
                        libfile.write(lib.definition)
                    args.append(path.join(tempdir, f"{lib.name}.c"))
                    for headerdir in {path.dirname(h) for h in lib.headers}:
                        args.append('-I')
                        args.append(headerdir)
                    for source in lib.sources:
                        files.append(source)
                f.write('#line 1 "program_text"\n')
                f.write(program_text)
            shutil.copy(path.join(tempdir, 'main.c'), '/tmp/last.c')

            result = run(args + files, stdout=PIPE, stderr=PIPE)
            if result.returncode:
                raise RuntimeError(result.stderr.decode())
            shutil.copy(path.join(tempdir, 'a.out'), '/tmp/last.elf')
            result = run(['mb-objcopy', '-O', 'binary',
                          path.join(tempdir, 'a.out'),
                          path.join(tempdir, 'a.bin')],
                         stderr=PIPE)
            if result.returncode:
                print("Objcopy Failed!")
                print(result.stderr.decode())

            super().__init__(mb_info, path.join(tempdir, 'a.bin'))
            self.stream = InterruptMBStream(self)

    def reset(self):
        PL.client_request()
        PL._ip_dict[self.ip_name]['state'] = None
        PL.server_update()
        super().reset()
        self.mmio.write(0, (64 * 1024) * b'\x00')
