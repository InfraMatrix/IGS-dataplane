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
import os
import libvirt
import uuid
import subprocess

from distro_manager import DistroManager

class VMManager:

    def __init__(self): ...
    def connect(self): ...

    def create_vm(self): ...
    def allocate_vm_disk(self, uuid): ...

    def __init__(self):

        self._uri    = "qemu:///system"
        self._conn   = None
        self._logger = None
        self.vms     = None
        self.distro_manager = DistroManager()

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

        print("Creating a VM\n")

        print("Downloading Ubuntu distro\n")

        self.distro_manager.download_ubuntu_iso()

        vm_uuid = str(uuid.uuid4())

        vm_path = f"/compute/vms/{vm_uuid}"

        os.makedirs(vm_path)

        self.allocate_vm_disk(vm_uuid)


    def allocate_vm_disk(self, vm_id):

        vm_path = f"/compute/vms/{vm_id}/{vm_id}.qcow2"

        try:
            subprocess.run([
                'qemu-img', 'create',
                '-f', 'qcow2', vm_path,
                f'10G'
            ], check=True)

            print(f"Created disk image: {vm_path}")
            return True
    
        except subprocess.CalledProcessError as e:
            print(f"Failed to create disk: {e}")
            return False