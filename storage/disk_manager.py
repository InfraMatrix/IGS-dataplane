#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import json
import subprocess
import parted
import yaml
import fcntl
import time

class DiskManager:

    def __init__(self): ...

    def set_state(self): ...

    # Server functions
    def get_disks(self): ...
    def get_free_disks(self): ...
    def get_scaler_disks(self): ...
    def add_disk(self, disk_num, part_size): ...
    def remove_disk(self, disk_num): ...
    def partition_disk(self, disk_name="", size_gb=0): ...
    def get_vm_disks(self, vm_name=""): ...
    def attach_disk_to_vm(self, vm_name=""): ...
    def detach_disk_from_vm(self, vm_name="", disk_name=""): ...

    # Setup and maintenance functions
    def dump_config(self): ...

    def _get_host_root_disk(self): ...
    def _get_host_nonroot_disks(self): ...
    def _get_scaler_disks(self): ...
    def _get_available_scaler_partitions(self): ...
    def _get_vm_disks(self): ...
    def _write_vm_disk_configuration(self): ...

    def __init__(self):
        self.disk_config = {}
        self.set_state()

    def set_state(self):
        self.disk_config = {
            "host_root_disk": self._get_host_root_disk(),
            "host_disks": self._get_host_nonroot_disks(),
            "vm_disks": self._get_vm_disks() or {},
        }

        self.disk_config["free_disks"] = self._get_free_disks()
        self.disk_config["scaler_disks"] = self._get_scaler_disks()
        self.disk_config["scaler_partitions"] = self._get_available_scaler_partitions()

    def dump_config(self):
        print(yaml.dump(self.disk_config))

    def get_disks(self):
        disk_list = []
        for disk in self.disk_config["host_disks"]:
            disk_list.append(disk["name"])
        return disk_list
    
    def get_free_disks(self):
        disk_list = []
        for disk in self.disk_config["free_disks"]:
            disk_list.append(disk["name"])
        return disk_list
    
    def get_scaler_disks(self):
        disk_list = []
        for disk in self.disk_config["scaler_disks"]:
            disk_list.append(disk["name"])
        return disk_list

    def _get_host_root_disk(self):
        try:
            cmd = ["findmnt", "--noheadings", "--output", "SOURCE", "/"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            rp = result.stdout.strip()

            cmd = ["lsblk", "--noheadings", "--output", "PKNAME", rp]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return f"/dev/{result.stdout.strip()}"
        
        except Exception as e:
            print(f"Failed to get root host disk: {e}")

        return ""

    def _get_host_nonroot_disks(self):
        disks = None
        try:
            cmd = ["lsblk", "--json", "--paths", "--bytes",
                   "--output", "NAME,SIZE,TYPE,PARTLABEL"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            disks = json.loads(result.stdout)["blockdevices"]

        except Exception as e:
            print(f"Failed to get nonroot host disks: {e}")
        
        return disks
    
    def _get_free_disks(self):
        free_disks = []
        for disk in self.disk_config["host_disks"]:
            if (disk["type"] != "disk" or disk.get("mountpoint") or 
                disk.get("fstype") or disk.get("children")):
                continue

            free_disks.append(disk)

        return free_disks

    def _get_scaler_disks(self):
        scaler_disks = []
        for disk in self.disk_config["host_disks"]:

            has_igs_part = False
            if ("children" in disk):
                for partition in disk["children"]:
                    partlabel = partition.get("partlabel")
                    if (partlabel and partlabel.startswith("igs")):
                        has_igs_part = True
                        break

                if (has_igs_part):
                    scaler_disks.append(disk)
                    
                has_igs_part = False

        return scaler_disks

    def _get_available_scaler_partitions(self):
        parts = []
        for disk in self.disk_config["scaler_disks"]:
            for part in disk["children"]:
                parts.append(part)

        for vm in self.disk_config["vm_disks"]:
            for part in self.disk_config["vm_disks"][vm]:
                for disk in self.disk_config["scaler_disks"]:
                    if part in disk["children"]:
                        parts.remove(part)

        return parts

    def _get_vm_disks(self):
        try:
            with open('/IGS/storage/vm_disks.yaml', 'r') as f:
                return yaml.safe_load(f)

        except Exception as e:
            pass

    def _write_vm_disk_configuration(self):
        with open('/IGS/storage/vm_disks.yaml', 'w') as f:
            yaml.safe_dump(self.disk_config["vm_disks"], f, default_flow_style=False)

    def add_disk(self, disk_num=-1, part_size=-1):
        disk = self.disk_config["free_disks"][disk_num]
        self.partition_disk(disk, part_size)
        self.set_state()

        return 0

    def remove_disk(self, disk_num=-1):
        disk = self.disk_config["scaler_disks"][disk_num]
        disk_parts = []
        for part in disk["children"]:
            disk_parts.append(part)

        for vm_name in self.disk_config["vm_disks"].keys():
            for part in self.disk_config["vm_disks"][vm_name]:
                if part in disk_parts:
                    self.detach_disk_from_vm(vm_name=vm_name, vm_disk_name=part["name"])

        self.disk_config["scaler_disks"].remove(disk)
        self.disk_config["free_disks"].append(disk)

        try:
            subprocess.run(['sudo', 'wipefs', '--all', disk["name"]], check=True)
        except Exception as e:
            print(f"Unable to wipe disk: {e}")

        self.set_state()

        return 0

    def partition_disk(self, disk=None, part_size=-1):
        fs = disk["size"]
        disk["free_space_gb"] = int(fs / (1024 ** 3))
        num_partitions = disk["free_space_gb"] / part_size - 1

        # Change this for production
        num_partitions = 5

        try:
            parted_device = parted.getDevice(disk["name"])
            parted_disk = parted.freshDisk(parted_device, 'gpt')
            part_len = parted.sizeToSectors(part_size, "GiB", parted_device.sectorSize)

            for i in range(0, num_partitions):
                pregion = parted.Geometry(device=parted_device, start = i*part_len, length=part_len )
                fs = parted.FileSystem(type="ext4", geometry=pregion)
                partition = parted.Partition(disk=parted_disk, type=parted.PARTITION_NORMAL, fs=fs, geometry=pregion)
                parted_disk.addPartition(partition, constraint=parted_device.optimalAlignedConstraint)

            parted_disk.commit()

            for i in range(0, num_partitions):
                name_partition_cmd = ["parted", disk["name"], "name", f"{i+1}", f"igs_{disk['name'].split('/')[-1]}_{i+1}"]
                subprocess.run(name_partition_cmd)

            subprocess.run(['udevadm', 'settle'])

        except Exception as e:
            print(f"Failed to partition disk: {e}")
            return -1
        
        return 0

    def _get_partitions(self):
        partitions = []
        for disk in self.scaler_disks:
            for part in disk["children"]:
               partitions.append(part)

        return partitions
    
    def _get_available_partitions(self):
        available_partitions = []
        for part in self.partitions:
            available_partitions.append(part)

        for vm in self.disk_config["vm_disks"]:
            for part in self.disk_config["vm_disks"][vm]:
                for i in available_partitions:
                    if (i["name"] == part):
                        available_partitions.remove(i)
                        break

        return available_partitions

    def get_vm_disks(self, vm_name=""):
        if (vm_name not in self.disk_config["vm_disks"].keys()):
            return []

        vm_disk_names = []
        for part in self.disk_config["vm_disks"][vm_name]:
            vm_disk_names.append(part["name"])

        return vm_disk_names

    def attach_disk_to_vm(self, vm_name=""):
        if (len(self.disk_config["scaler_partitions"]) == 0):
            return -1

        part = self.disk_config["scaler_partitions"][0]
        if (vm_name not in self.disk_config["vm_disks"].keys()):
            self.disk_config["vm_disks"][vm_name] = []

        self.disk_config["vm_disks"][vm_name].append(part)
        self.disk_config["scaler_partitions"].remove(part)
        self._write_vm_disk_configuration()

        with open(f"/IGS/compute/vms/{vm_name}/{vm_name}.conf", "a") as conf_file:
            conf_file.write(f"\n[drive]\nfile = \"{part['name']}\"\nformat = \"raw\"\n")
            conf_file.close()

        return 0

    def detach_disk_from_vm(self, vm_name="", vm_disk_name=""):
        if (vm_name not in self.disk_config["vm_disks"].keys()):
            return -1

        vm_part = None
        for part in self.disk_config["vm_disks"][vm_name]:
            if (vm_disk_name == part["name"]):
                vm_part = part
            if (vm_part):
                break

        self.disk_config["vm_disks"][vm_name].remove(vm_part)
        self.disk_config["scaler_partitions"].append(vm_part)

        vm_conf_fname = f"/IGS/compute/vms/{vm_name}/{vm_name}.conf"
        remove_string = f"\n[drive]\nfile = \"{vm_disk_name}\"\nformat = \"raw\"\n"

        file_content = ""

        with open(vm_conf_fname, "r") as conf_file:
            file_content = conf_file.read()
            file_content = file_content.replace(remove_string, "")
            conf_file.close()

        with open(vm_conf_fname, "w") as conf_file:
            conf_file.write(file_content)
            conf_file.close()

        self._write_vm_disk_configuration()

        return 0
