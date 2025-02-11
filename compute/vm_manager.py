#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

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
from network.network_manager import NetworkManager

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

    def update_vm_cloud_init(self, vm_name, old_string="", new_string=""): ...

    def _send_command_to_vm(self, curr_vm, cmd): ...

    def __init__(self, network_manager):
        self._uri = "qemu:///system"
        self._conn = None
        self._logger = None
        self._vm_location = "/IGS/compute/vms"
        self._vms = {}
        self._distro_manager = DistroManager()
        self.network_manager = network_manager

        count = 0
        for vm_name in os.listdir(f"{self._vm_location}/"):
            vm_tap_intf = self.network_manager.allocate_vm_tap_interface(vm_name)
            vm_ip = self.network_manager.get_vm_ip(vm_name)
            vm_mac_addr = self.network_manager.get_vm_mac(vm_name)
            vm = VM(vm_name, disk_location=f"{self._vm_location}/{vm_name}/{vm_name}.qcow2", tap_intf=vm_tap_intf,
                    ip_address=vm_ip,
                    mac_address=vm_mac_addr)
            self._vms[vm_name] = {"instance": vm, "status": "down"}

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

    def get_vms(self, status=""):
        vm_names = []

        for vm, vm_dict in self._vms.items():
            if (status == "all" or status == vm_dict["status"]):
                vm_names.append(vm)

        return vm_names
    
    def get_vm_pty_file(self, vm_name=""):
        return self._vms[vm_name]["instance"].serial_conn
    
    def create_vm(self):
        ret = self._distro_manager.verify_ubuntu_image()
        if (ret != 0):
            return ""

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

        with open(f"{self._vm_location}/{vm_uuid}/user-data", 'w') as wdf:
            wdf.write(data)
            wdf.close()
        os.chmod(f"{self._vm_location}/{vm_uuid}/user-data", 0o600)

        data = f"instance-id: {vm_uuid}\n"
        data = data + f"local-hostname: ubuntu\n"

        with open(f"{self._vm_location}/{vm_uuid}/meta-data", 'w') as wdf:
            wdf.write(data)
        os.chmod(f"{self._vm_location}/{vm_uuid}/meta-data", 0o644)

        vm_tap_intf = self.network_manager.allocate_vm_tap_interface(vm_uuid)
        vm_mac = f"{self.network_manager.generate_mac()}"
        vm_ip = f"192.168.100.{self.network_manager.ip_manager.acquire_ip(vm_uuid)}"

        self.update_vm_cloud_init(vm_uuid, old_string="SSH_KEY",
            new_string=f"- {public_key_str}")

        self.update_vm_cloud_init(vm_uuid, old_string="MAC_ADDRESS",
            new_string=f"{vm_mac}")

        self.update_vm_cloud_init(vm_uuid, old_string="IP_ADDRESS",
            new_string=f"{vm_ip}")

        subprocess.run(["genisoimage",
            "-output", f"{self._vm_location}/{vm_uuid}/cloud-init.iso",
            "-volid", "cidata",
            "-joliet", "-rock",
            "-input-charset", "utf-8",
            f"{self._vm_location}/{vm_uuid}/user-data",
            f"{self._vm_location}/{vm_uuid}/meta-data"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)

        new_vm = VM(vm_uuid, disk_location=vm_path+"/{vm_uuid}.qcow2", tap_intf=vm_tap_intf,
            ip_address=vm_ip, mac_address=vm_mac)

        self._vms[vm_uuid] = {"instance": new_vm, "status": "down"}

        return vm_uuid

    def delete_vm(self, vm_name=""):
        curr_vm = self._vms.get(vm_name)
        if (curr_vm == None):
            return

        if (curr_vm["status"] != "down"):
            pass

        self.network_manager.deallocate_vm_tap_interface(vm_name)

        shutil.rmtree(f"{self._vm_location}/{vm_name}")

        del self._vms[vm_name]

        return vm_name

    def start_vm(self, vm_name=""):
        vm_dict = self._vms.get(vm_name)
        if (vm_dict == None):
            return ""
        curr_vm = vm_dict["instance"]
        try:
            run_vm_cmd = [
                "qemu-system-x86_64",
                "-nographic",
                "-serial", "pty",
                "-monitor", f"unix:/tmp/{vm_name}.sock,server,nowait",
                "-device", "virtio-serial-pci",
                "-chardev", f"socket,id=ch0,path=/tmp/{vm_name}_qga.sock,server=on,wait=off",
                "-device", "virtserialport,chardev=ch0,name=org.qemu.guest_agent.0",
                "-readconfig", f"{self._vm_location}/{vm_name}/{vm_name}.conf",
                "-drive", f"file={self._vm_location}/{vm_name}/cloud-init.iso,format=raw,if=virtio,media=cdrom",
                "-netdev", f"tap,id={curr_vm.tap_intf},ifname={curr_vm.tap_intf},script=no,downscript=no",
                "-device", f"virtio-net-pci,netdev={curr_vm.tap_intf},mac={curr_vm.mac_address}",
            ]

            process = subprocess.Popen(
                run_vm_cmd,
                start_new_session = True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                universal_newlines=True,
                bufsize=1
            )

            readable, _, _ = select.select([process.stdout, process.stderr], [], [], 5.0)

            match = None
            for pipe in readable:
                for line in pipe:
                    match = re.search(r"char device redirected to (/dev/pts/\d+)", line)
                    if (match):
                        break

            serial_port = match.group(1)

            time.sleep(2.0)

            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(f"/tmp/{vm_name}.sock")

            curr_vm.hv_conn = sock
            curr_vm.serial_conn = serial_port

            self._vms[vm_name]["status"] = "running"
        except Exception as e:
            print(f"Failed to start vm: {e}")

        return vm_name

    def shutdown_vm(self, vm_name=""):
        vm_dict = self._vms.get(vm_name)
        if (vm_dict == None or vm_dict["status"] != "running"):
            return ""
        curr_vm = vm_dict["instance"]
        try:
            self._send_command_to_vm(curr_vm, "system_powerdown")
            #self.network_manager.release_vm_port(vm_name)
            print(vm_dict)
            vm_dict["status"] = "down"
        except Exception as e:
            print(f"Failed to shutdown vm: {e}")

        return vm_name

    def resume_vm(self, vm_name=""):
        vm_dict = self._vms.get(vm_name)
        if (vm_dict == None or vm_dict["status"] != "stopped"):
            return ""
        curr_vm = vm_dict["instance"]
        try:
            self._send_command_to_vm(curr_vm, "cont")
            vm_dict["status"] = "running"
        except Exception as e:
            print(f"Failed to start vm: {e}")

        return vm_name

    def stop_vm(self, vm_name=""):
        vm_dict = self._vms.get(vm_name)
        if (vm_dict == None or vm_dict["status"] != "running"):
            return ""
        curr_vm = vm_dict["instance"]
        try:
            self._send_command_to_vm(curr_vm, "stop")
        except Exception as e:
            print(f"Failed to start vm: {e}")

        return vm_name

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
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL)
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

    def get_vm_status(self, vm_name=-1):
        vm_dict = self._vms.get(vm_name)
        if (vm_dict == None or vm_dict["status"] != "stopped"):
            return ""
        curr_vm = vm_dict["instance"]
        try:
            cmd_output = self._send_command_to_vm(curr_vm, "info status")
            status = re.search(r"VM status: (\w+)", cmd_output).group(1)
        except Exception as e:
            print(f"Failed to start vm: {e}")
        return status

    def get_vm_link(self, vm_name=-1):
        vm_dict = self._vms.get(vm_name)
        if (vm_dict == None):
            return ""
        curr_vm = vm_dict["instance"]

        socket_path = f"/tmp/{vm_name}_qga.sock"
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
                            return (addr["ip-address"], f"{self.network_manager.port_map[vm_name]}")
            sock.close()
        except Exception as e:
            print(f"Failed to get VM IP: {e}")
        return ""

    def update_vm_cloud_init(self, vm_name, old_string="", new_string=""):
        conf_path = f"{self._vm_location}/{vm_name}/user-data"
        with open(conf_path, 'r') as file:
            conf_data = file.read()
        conf_data = conf_data.replace(old_string, new_string)

        with open(conf_path, 'w') as file:
            file.write(conf_data)
