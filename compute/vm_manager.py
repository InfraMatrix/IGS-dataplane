#!/usr/bin/env python3

# Copyright (c) 2025 InfraMatrix. All rights reserved.

# The user ("Licensee") is hereby granted permission to use this software and
# associated documentation files (the "Software"),
# subject to the express condition that Licensee shall not, under any circumstances,
# redistribute, sublicense, copy, transfer, publish, disseminate, transmit,
# broadcast, sell, lease, rent, share, loan, or otherwise make available the
# Software, in whole or in part, in any form or by any means, to any third party
# without prior written consent from the copyright holder,
# and any such unauthorized distribution shall constitute a material breach of this
# license and result in immediate, automatic termination of all rights granted
# hereunder.

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
import grpc
import json
from concurrent import futures

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from .distro_manager import DistroManager
from .vm import VM
from .generated import compute_pb2
from .generated import compute_pb2_grpc

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from network.vm_network_manager import VMNetworkManager

class VMManager():

    def __init__(self): ...
    def connect(self): ...

    def get_vms(self): ...

    def create_vm(self): ...
    def delete_vm(self): ...
    def allocate_vm_disk(self, vm_id): ...
    def copy_image(self, vm_id): ...
    def write_vm_config(self, vm_id): ...

    def start_vm(self): ...
    def shutdown_vm(self): ...
    def resume_vm(self): ...
    def stop_vm(self): ...

    def get_vm_status(self): ...
    def get_vm_link(self): ...


    def _send_command_to_vm(self, curr_vm, cmd): ...

    def __init__(self):
        self._uri = "qemu:///system"
        self._conn = None
        self._logger = None
        self._vm_location = "/IGS/compute/vms"
        self._vms     = []
        self._live_vms = []
        self._down_vms = []
        self._running_vms = []
        self._stopped_vms = []
        self._distro_manager = DistroManager()
        self._network_manager = VMNetworkManager()

        count = 0

        for d in os.listdir(f"{self._vm_location}/"):
            vm_tap_intf = None
            vm_ip_port = self._network_manager.acquire_vm_port(d)
            vm = VM(d, disk_location=f"{self._vm_location}/{d}/{d}.qcow2", tap_intf=vm_tap_intf,
                    mac_address=self._network_manager.generate_mac(), ip_port=vm_ip_port)
            self._vms.append(vm)
            self._down_vms.append(vm)

            count += 1

        self.connect()

    def connect(self):
        try:
            self._conn = libvirt.open(self._uri)
            if self._conn is None:
                raise Exception('Failed to connect to KVM')

            return True

        except libvirt.libvirtError as e:
            print(f'Connection error: {e}', file=sys.stderr)
            return False

    def get_vms(self, status=None):
        vm_names = []
        vms = None
        if (status == 1):
            vms = self._vms

        elif (status == 2):
            vms = self._down_vms

        elif (status == 3):
            vms = self._live_vms

        elif (status == 4):
            vms = self._stopped_vms

        elif (status == 5):
            vms = self._running_vms

        for i in vms:
            vm_names.append(i.name)

        return vm_names
    
    def get_vm_pty_file(self, vm_num=-1):
        return self._running_vms[vm_num].serial_conn
    
    def create_vm(self):

        self._distro_manager.verify_ubuntu_image()

        print("Creating the vm\n")

        vm_uuid = str(uuid.uuid4())
        vm_path = f"{vm_uuid}"

        os.makedirs(f"{self._vm_location}/{vm_path}")
        self.copy_vm_image(vm_uuid)
        self.write_vm_config(vm_uuid)

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        private_key_str = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        public_key = private_key.public_key()
        public_key_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )
        public_key_str = public_key_bytes.decode('utf-8')
        public_key_str = public_key_str + f" {os.getlogin()}@{socket.gethostname()}"

        with open(f"{self._vm_location}/{vm_uuid}/id_rsa", "w") as pkf:
            pkf.write(private_key_str)
            os.chmod(f"{self._vm_location}/{vm_uuid}/id_rsa", 0o600)
            pkf.close()

        with open(f"{self._vm_location}/{vm_uuid}/id_rsa.pub", "w") as pkf:
            pkf.write(public_key_str)
            pkf.close()

        with open(f"compute/provisioning/vm_config/user-data", 'r') as udf:
            data = udf.read()
            data = data + "\n" + " " * 6 + f"- {public_key_str}\n"

        with open(f"{self._vm_location}/{vm_uuid}/user-data", 'w') as wdf:
            wdf.write(data)
        os.chmod(f"{self._vm_location}/{vm_uuid}/user-data", 0o600)

        data = f"instance-id: {vm_uuid}\n"
        data = data + f"local-hostname: ubuntu\n"

        with open(f"{self._vm_location}/{vm_uuid}/meta-data", 'w') as wdf:
            wdf.write(data)
        os.chmod(f"{self._vm_location}/{vm_uuid}/meta-data", 0o644)

        private_key_str = ""
        public_key_str = ""

        subprocess.run(["genisoimage",
            "-output", f"{self._vm_location}/{vm_uuid}/cloud-init.iso",
            "-volid", "cidata",
            "-joliet", "-rock",
            "-input-charset", "utf-8",
            f"{self._vm_location}/{vm_uuid}/user-data", f"{self._vm_location}/{vm_uuid}/meta-data"]
        )

        vm_tap_intf = None
        vm_ip_port = self._network_manager.acquire_vm_port(vm_uuid)
        new_vm = VM(vm_uuid, disk_location=vm_path+"/{vm_uuid}.qcow2", tap_intf=vm_tap_intf,
                    mac_address=self._network_manager.generate_mac(), ip_port=vm_ip_port)

        self._vms.append(new_vm)
        self._down_vms.append(new_vm)

        return vm_uuid

    def delete_vm(self, vm_num=-1):
        curr_vm = self._vms[vm_num]
        if (curr_vm in self._stopped_vms):
            self._send_command_to_vm(curr_vm, "cont")

            self._running_vms.append(curr_vm)
            self._stopped_vms.remove(curr_vm)

        if (curr_vm in self._running_vms):
            self._send_command_to_vm(curr_vm, "system_powerdown")

            self._stopped_vms.append(curr_vm)
            self._running_vms.remove(curr_vm)

        shutil.rmtree(f"{self._vm_location}/{curr_vm.name}")

        if (curr_vm in self._live_vms):
            self._live_vms.remove(curr_vm)

        if (curr_vm in self._stopped_vms):
            self._stopped_vms.remove(curr_vm)

        if (curr_vm in self._down_vms):
            self._down_vms.remove(curr_vm)

        self._vms.remove(curr_vm)

        return curr_vm.name

    def start_vm(self, vm_num=-1):
        num_vms = len(self._down_vms)
        curr_vm = self._down_vms[vm_num]

        try:
            run_vm_cmd = [
                "qemu-system-x86_64",
                "-nographic",
                "-monitor", f"unix:/tmp/{curr_vm.name}.sock,server,nowait",
                "-serial", "pty",
                "-readconfig", f"{self._vm_location}/{curr_vm.name}/{curr_vm.name}.conf",
                "-netdev", f"user,id=net0,hostfwd=tcp:127.0.0.1:{curr_vm.ip_port}-:22",
                "-device", "virtio-net-pci,netdev=net0",
                "-drive", f"file={self._vm_location}/{curr_vm.name}/cloud-init.iso,format=raw,if=virtio,media=cdrom",
                "-device", "virtio-serial-pci",
                "-chardev", f"socket,id=ch0,path=/tmp/{curr_vm.name}_qga.sock,server=on,wait=off",
                "-device", "virtserialport,chardev=ch0,name=org.qemu.guest_agent.0",
            ]

            process = subprocess.Popen(
                run_vm_cmd,
                start_new_session = True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                bufsize=0
            )

            readable, _, _ = select.select([process.stdout, process.stderr], [], [], 2.0)

            match = None
            for pipe in readable:
                for line in pipe:
                    print(f"QEMU output: {line}")

                    match = re.search(r"char device redirected to (/dev/pts/\d+)", line)
                    if (match):
                        break

            serial_port = match.group(1)

            time.sleep(2.0)

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(f"/tmp/{curr_vm.name}.sock")

            curr_vm.hv_conn = sock
            curr_vm.serial_conn = serial_port

            self._live_vms.append(curr_vm)
            self._running_vms.append(curr_vm)
            self._down_vms.remove(curr_vm)

            return curr_vm.name

        except Exception as e:
            print(f"Failed to start vm: {e}")

    def shutdown_vm(self, vm_num=-1):
        num_vms = len(self._live_vms)
        curr_vm = self._live_vms[vm_num]

        try:
            self._send_command_to_vm(curr_vm, "system_powerdown")

            self._down_vms.append(curr_vm)
            self._live_vms.remove(curr_vm)

            self._network_manager.release_vm_port(curr_vm.name)

            if (curr_vm in self._running_vms):
                self._running_vms.remove(curr_vm)

            if (curr_vm in self._stopped_vms):
                self._stopped_vms.remove(curr_vm)

        except Exception as e:

            print(f"Failed to start vm: {e}")

        return curr_vm.name

    def resume_vm(self, vm_num=-1):
        num_vms = len(self._stopped_vms)
        curr_vm = self._stopped_vms[vm_num]

        try:
            self._send_command_to_vm(curr_vm, "cont")

        except Exception as e:
            print(f"Failed to start vm: {e}")
            self._running_vms.append(curr_vm)
            self._stopped_vms.remove(curr_vm)

        return curr_vm.name

    def stop_vm(self, vm_num=-1):
        num_vms = len(self._running_vms)
        curr_vm = self._running_vms[vm_num]

        try:
            self._send_command_to_vm(curr_vm, "stop")

        except Exception as e:
            print(f"Failed to start vm: {e}")

        self._stopped_vms.append(curr_vm)
        self._running_vms.remove(curr_vm)

        return curr_vm.name

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
                "-b", "/IGS/compute/images/ubuntu_22.04.5_base.qcow2",
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
            with open("conf/instances/micro.conf", "r") as cfile:
                content = cfile.read()
                content = content.replace("GNAME", vm_id)
                content = content.replace("FPATH", f"/IGS/compute/vms/{vm_id}/{vm_id}.qcow2")

                with open(f"/IGS/compute/vms/{vm_id}/{vm_id}.conf", "w") as fcfile:
                    fcfile.write(content)

        except Exception as e:
            print(f"Failed to open instance config file: {e}")

    def get_vm_status(self, vm_num=-1):
        curr_vm = self._live_vms[vm_num]

        try:
            cmd_output = self._send_command_to_vm(curr_vm, "info status")
            status = re.search(r"VM status: (\w+)", cmd_output).group(1)

        except Exception as e:
            print(f"Failed to start vm: {e}")

        return status

    def get_vm_link(self, vm_num=-1):
        curr_vm = self._live_vms[vm_num]

        socket_path = f"/tmp/{curr_vm.name}_qga.sock"
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.connect(socket_path)
            command = json.dumps({"execute": "guest-network-get-interfaces"})
            sock.send(command.encode())

            response = "" + sock.recv(4096).decode()
            interfaces = json.loads(response)
            for iface in interfaces["return"]:
                if iface["name"] != "lo":
                    for addr in iface["ip-addresses"]:
                        if addr["ip-address-type"] == "ipv4" and addr["ip-address"].startswith("10"):
                            return (addr["ip-address"], f"{self._network_manager.port_map[curr_vm.name]}")

            sock.close()

        except Exception as e:
            print(f"Failed to get VM IP: {e}")

        return ""