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
from subprocess import run, PIPE

from .streams import InterruptMBStream
from . import BSPs
from . import Modules

__author__ = "Peter Ogden"
__copyright__ = "Copyright 2017, Xilinx"
__email__ = "ogden@xilinx.com"


def dependencies(source, bsp):
    args = ['cpp', '-MM']
    for include_path in bsp.include_path:
        args.append('-I')
        args.append(include_path)
    paths = {}
    for name, module in Modules.items():
        for include_path in module.include_path:
            args.append('-I')
            args.append(include_path)
            paths[include_path] = name

    result = run(args, stdout=PIPE, stderr=PIPE, input=source.encode())
    if result.returncode:
        raise RuntimeError("Preproseeor failed: \n" + result.stderr)
    dependent_paths = result.stdout.decode()
    dependent_modules = {v for k, v in paths.items()
                         if dependent_paths.find(k) != -1 }
    return [Modules[k] for k in dependent_modules]
     

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

    def __init__(self, mb_info, program_text, bsp=None):
        if bsp is None:
            if mb_info['mbtype'] not in BSPs:
                raise RuntimeError("Could not find BSP for Microblaze type" +
                                   mb_info['mbtype'])
            bsp = BSPs[mb_info['mbtype']]

        modules = dependencies(program_text, bsp)

        with tempfile.TemporaryDirectory() as tempdir:
            files = [path.join(tempdir, 'main.c')]
            args = ['mb-gcc', '-o', path.join(tempdir, 'a.out') ]
            args.extend(bsp.cflags)
            args.extend(bsp.sources)
            for include_path in bsp.include_path:
                args.append('-I')
                args.append(include_path)
            for lib_path in bsp.library_path:
                args.append('-L')
                args.append(lib_path)
            for lib in bsp.libraries:
                args.append(f'-l{lib}')
            args.append(f'-Wl,{bsp.linker_script}')
            args.extend(bsp.ldflags)

            for module in modules:
                files.extend(module.sources)
                for include_path in module.include_path:
                     args.append('-I')
                     args.append(include_path)
                for lib_path in module.library_path:
                     args.append('-L')
                     args.append(lib_path)
                for lib in module.libraries:
                     args.append(f'-l{lib}')

            with open(path.join(tempdir, 'main.c'), 'w') as f:
                f.write('#line 1 "cell_magic"\n')
                f.write(program_text)
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
            self.read = self.stream.read
            self.write = self.stream.write
            self.read_async = self.stream.read_async

    def reset(self):
        PL.client_request()
        PL._ip_dict[self.ip_name]['state'] = None
        PL.server_update()
        super().reset()
        self.mmio.write(0, (64 * 1024) * b'\x00')
