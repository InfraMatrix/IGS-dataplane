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
import socket
import time
import shutil
import select
import re

from distro_manager import DistroManager
from vm import VM

class VMManager:

    def __init__(self): ...
    def connect(self): ...

    def create_vm(self): ...
    def delete_vm(self): ...
    def allocate_vm_disk(self, vm_id): ...
    def copy_image(self, vm_id): ...
    def write_vm_config(self, vm_id): ...

    def start_vm(self): ...
    def shutdown_vm(self): ...
    def resume_vm(self): ...
    def pause_vm(self): ...

    def get_vm_status(self): ...

    def connect_to_vm(self): ...

    def _send_command_to_vm(self, curr_vm, cmd): ...

    def __init__(self):

        self._uri = "qemu:///system"
        self._conn = None
        self._logger = None
        self._vm_location = "/compute/vms"
        self._vms     = []
        self._live_vms = []
        self._running_vms = []
        self._stopped_vms = []
        self._paused_vms = []
        self._distro_manager = DistroManager()

        for d in os.listdir(f"{self._vm_location}/"):

            self._vms.append(VM(d, f"{self._vm_location}/{d}/{d}.qcow2"))
            self._stopped_vms.append(VM(d, f"{self._vm_location}/{d}/{d}.qcow2"))


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

        self._distro_manager.download_ubuntu_iso()

        vm_uuid = str(uuid.uuid4())
        vm_path = f"{vm_uuid}"

        os.makedirs(f"{self._vm_location}/{vm_path}")
        self.copy_vm_image(vm_uuid)
        self.write_vm_config(vm_uuid)

        new_vm = VM(vm_uuid, vm_path+"/{vm_uuid}.qcow2")

        print(f"Created VM: {vm_uuid}\n")

        self._vms.append(new_vm)
        self._stopped_vms.append(new_vm)

    def delete_vm(self):
        num_vms = len(self._vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to delete:")

            for i in range(1, len(self._vms) + 1):
                print(f"{i}: {self._vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._vms[vm_num]

        if (curr_vm in self._paused_vms):

            self._send_command_to_vm(curr_vm, "cont")

            self._running_vms.append(curr_vm)
            self._stopped_vms.remove(curr_vm)
            self._paused_vms.remove(curr_vm)

        if (curr_vm in self._running_vms):

            self._send_command_to_vm(curr_vm, "system_powerdown")

            self._stopped_vms.append(curr_vm)
            self._running_vms.remove(curr_vm)

        shutil.rmtree(f"{self._vm_location}/{curr_vm.name}")

        self._live_vms.remove(curr_vm)
        self._stopped_vms.remove(curr_vm)
        self._vms.remove(curr_vm)

    def start_vm(self):

        num_vms = len(self._stopped_vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to start:")

            for i in range(1, len(self._stopped_vms) + 1):
                print(f"{i}: {self._stopped_vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._stopped_vms[vm_num]

        try:

            run_vm_cmd = [

                "qemu-system-x86_64",
                "-nographic",
                "-monitor", f"unix:/tmp/{curr_vm.name}.sock,server,nowait",
                "-serial", "pty",
                "-readconfig", f"{self._vm_location}/{curr_vm.name}/{curr_vm.name}.conf"
            ]

            process = subprocess.Popen(
                run_vm_cmd,
                # Uncomment for testing that vms run
                start_new_session = True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True
            )

            time.sleep(0.1)

            readable, _, _ = select.select([process.stdout, process.stderr], [], [], 2.0)

            match = None
            for pipe in readable:

                for line in pipe:

                    if (match):
                        break

                    match = re.search(r"char device redirected to (/dev/pts/\d+)", line)
                    if (match):
                        break

            serial_port = match.group(1)

            print(f"Starting VM: {curr_vm.name} with serial: {serial_port}\n")

            time.sleep(2.0)

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(f"/tmp/{curr_vm.name}.sock")

            curr_vm.hv_conn = sock
            curr_vm.serial_conn = serial_port

            self._live_vms.append(curr_vm)
            self._running_vms.append(curr_vm)
            self._stopped_vms.remove(curr_vm)

        except Exception as e:
            print(f"Failed to start vm: {e}")

    def shutdown_vm(self):

        num_vms = len(self._running_vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to start:")

            for i in range(1, len(self._running_vms) + 1):
                print(f"{i}: {self._running_vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._running_vms[vm_num]

        try:

            print(f"Shutting down VM: {curr_vm.name}\n")

            self._send_command_to_vm(curr_vm, "system_powerdown")

            self._stopped_vms.append(curr_vm)
            self._live_vms.remove(curr_vm)
            self._running_vms.remove(curr_vm)

        except Exception as e:
            print(f"Failed to start vm: {e}")

    def resume_vm(self):

        num_vms = len(self._paused_vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to start:")

            for i in range(1, len(self._paused_vms) + 1):
                print(f"{i}: {self._paused_vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._paused_vms[vm_num]

        try:

            print(f"Resuming VM: {curr_vm.name}\n")

            self._send_command_to_vm(curr_vm, "cont")

            self._running_vms.append(curr_vm)
            self._stopped_vms.remove(curr_vm)
            self._paused_vms.remove(curr_vm)

        except Exception as e:
            print(f"Failed to start vm: {e}")

    def pause_vm(self):

        num_vms = len(self._running_vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to start:")

            for i in range(1, len(self._running_vms) + 1):
                print(f"{i}: {self._running_vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._running_vms[vm_num]

        try:

            print(f"Pausing VM: {curr_vm.name}\n")

            self._send_command_to_vm(curr_vm, "stop")

            self._stopped_vms.append(curr_vm)
            self._paused_vms.append(curr_vm)
            self._running_vms.remove(curr_vm)

        except Exception as e:
            print(f"Failed to start vm: {e}")

    def get_vm_status(self):

        num_vms = len(self._live_vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to get the status of:")

            for i in range(1, len(self._live_vms) + 1):
                print(f"{i}: {self._live_vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._live_vms[vm_num]

        try:

            cmd_output = self._send_command_to_vm(curr_vm, "info status")

            status = re.search(r"VM status: (\w+)", cmd_output).group(1)

            print(f"{curr_vm.name}'s status: {status}\n")

        except Exception as e:
            print(f"Failed to start vm: {e}")

    def connect_to_vm(self):

        num_vms = len(self._running_vms)

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):

            print("Input the vm that you want to connect to over serial :")

            for i in range(1, len(self._running_vms) + 1):
                print(f"{i}: {self._running_vms[i-1].name}")

            vm_num = int(input("")) - 1

        curr_vm = self._running_vms[vm_num]

        print(f"Attempting to patch you into {curr_vm.name}\n")

        try:
            subprocess.run([
                'socat', '-',
                f"{curr_vm.serial_conn}"
            ], check=True)

            return True

        except Exception as e:
            print(f"Failed to connect to VM: {e}")

        except KeyboardInterrupt:
            print(f"\n\nExited from: {curr_vm.name}\n")

    def _send_command_to_vm(self, curr_vm, cmd):

        sock = curr_vm.hv_conn

        time.sleep(0.3)

        sock.send(f"{cmd}\r\n".encode())

        time.sleep(0.3)

        response = sock.recv(1024).decode()

        return response

    def allocate_vm_disk(self, vm_id):

        vm_path = f"{self._vm_location}/{vm_id}/{vm_id}.qcow2"

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

    def copy_vm_image(self, vm_id):

        try:

            copy_image_cmd = [

                "qemu-img", "create",
                "-f", "qcow2",
                "-b", "/compute/images/ubuntu22.04.qcow2",
                "-F", "qcow2",
                f"{self._vm_location}/{vm_id}/{vm_id}.qcow2",
                "10G"

            ]

            result = subprocess.run(
                copy_image_cmd,
                check = True,
                capture_output = True,
                text = True
            )

        except Exception as e:
            print(f"Failed to create vm disk: {e}")

    def write_vm_config(self, vm_id):

        try:
            with open("../conf/instances/micro.conf", "r") as cfile:

                content = cfile.read()

                content = content.replace("GNAME", vm_id)
                content = content.replace("FPATH", f"/compute/vms/{vm_id}/{vm_id}.qcow2")

                with open(f"/compute/vms/{vm_id}/{vm_id}.conf", "w") as fcfile:

                    fcfile.write(content)
        except Exception as e:
            print(f"Failed to open instance config file: {e}")
