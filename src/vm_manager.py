#!/usr/bin/env python3
 
# Copyright 2024 InfraMatrix

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import libvirt

class VMManager:

    def __init__(self):

        self._uri    = "qemu:///system"
        self._conn   = None
        self._logger = None
        self.vms     = None

    def connect(self):

        try:

            self._conn = libvirt.open(self._uri)
            if self._conn is None:

                raise Exception('Failed to connect to KVM')

            return True

        except libvirt.libvirtError as e:

            print(f'Connection error: {e}', file=sys.stderr)

            return False
        
    
    def create_vm(self):

        print("Creating a VM")