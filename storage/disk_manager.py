#!/usr/bin/env python3

# Copyright (c) 2024 InfraMatrix. All rights reserved.

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

import json
import subprocess
import parted
import yaml
import fcntl

class DiskManager:

    def __init__(self): ...

    def read_config(self): ...
    def write_config(self, config_path, config): ...

    def get_disks(self): ...
    def _get_host_root_disk(self): ...
    def _get_host_nonroot_disks(self): ...
    def _get_free_disks(self): ...
    def _get_scaler_disks(self): ...
    def _set_scaler_disk_free_space(self): ... 

    def add_disk(self, disk_name=""): ...
    def partition_disk(self, disk_name="", size_gb=0): ...

    def _get_partitions(self): ...
    def _get_available_partitions(self): ...

    def attach_disk_to_vm(self, vm_name=""): ...

    def __init__(self):

        self.host_root_disk = self._get_host_root_disk()

        self.disks = self._get_host_nonroot_disks()

        self.free_disks = self._get_free_disks()

        self.scaler_disks = self._get_scaler_disks()

        self._set_scaler_disk_free_space()

        self.partitions = self._get_partitions()

        self.disk_config = self.read_config(config_path=f"/IGS/storage/storage.conf")

        if ("storage_disks" not in self.disk_config):

            self.disk_config["storage_disks"] = {}

            self.disk_config["vm_disks"] = {}

            self.write_config(config_path=f"/IGS/storage/storage.conf", config=self.disk_config)

        self.available_partitions = self._get_available_partitions()

    def read_config(self, config_path=""):

        config = None

        try:

            with open(config_path, "r") as f:

                fcntl.flock(f.fileno(), fcntl.LOCK_SH)

                config = yaml.safe_load(f) or {}

                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except Exception as e:

            print(f"Failed to load storage configuration: {e}")

        return config

    def write_config(self, config_path, config):

        try:

            with open(config_path, "w") as f:

                fcntl.flock(f.fileno(), fcntl.LOCK_SH)

                yaml.safe_dump(config, f, default_flow_style=False)

                fcntl.flock(f.fileno(), fcntl.LOCK_UN)

        except Exception as e:

            print(f"Failed to write storage configuration: {e}")

    def get_disks(self):

        disk_list = []

        for disk in self.free_disks:

            disk_list.append(f"{disk}")

        for disk in self.scaler_disks:

            disk_list.append(f"{disk}")

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

        for disk in self.disks:

            if (disk["type"] != "disk" or disk.get("mountpoint") or 
                disk.get("fstype") or disk.get("children")):
                continue

            free_disks.append(disk)

        return free_disks

    
    def _get_scaler_disks(self):

        scaler_disks = []

        for disk in self.disks:

            has_ceph_part = False

            if ("children" in disk):

                for partition in disk["children"]:

                    partlabel = partition.get("partlabel")

                    if (partlabel and partlabel.startswith("ceph")):

                        has_ceph_part = True

                        break

                if (has_ceph_part):

                    scaler_disks.append(disk)
                    
                has_ceph_part = False

        return scaler_disks

    def _set_scaler_disk_free_space(self):

        for disk in self.free_disks:

            disk["free_space_gb"] = int(disk["size"] / (1024 ** 3))

        for disk in self.scaler_disks:

            fs = disk["size"]

            for partition in disk["children"]:

                fs -= partition["size"]

            disk["free_space_gb"] = int(fs / (1024 ** 3))
            disk["num_partitions"] = len(disk["children"])

    def add_disk(self, disk_num=-1, part_size=-1):

        disk = self.free_disks[disk_num]

        self.scaler_disks.append(disk)

        self.free_disks.remove(disk)

        self.partition_disk(disk, part_size)

        return 0
    
    def partition_disk(self, disk=None, part_size=-1):

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

                name_partition_cmd = ["parted", disk["name"], "name", f"{i+1}", f"ceph_{disk['name'].split('/')[-1]}_{i+1}"]
                subprocess.run(name_partition_cmd)

        except Exception as e:

            print(f"Failed to partition disk: {e}")

    def create_partition(self, disk_name="", size_gb=0):

        if (size_gb == 0 or disk_name == ""):

            return None

        scaler_disk = None
        for disk in self.free_disks:

            if (disk_name == disk["name"]):

                self.free_disks.remove(disk)

                self.scaler_disks.append(disk)

                scaler_disk = disk

        if (scaler_disk == None):

            for disk in self.scaler_disks:

                if (disk_name == disk["name"]):

                    scaler_disk = disk

        if (scaler_disk == None or size_gb > scaler_disk["free_space_gb"]):

            return None

        return None

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

    def attach_disk_to_vm(self, vm_name=""):

        if (len(self.available_partitions) == 0):

            return -1

        part = self.available_partitions[0]

        self.available_partitions.remove(part)

        if (vm_name not in self.disk_config["vm_disks"].keys()):

            self.disk_config["vm_disks"][vm_name] = []

        self.disk_config["vm_disks"][vm_name].append(part["name"])

        self.write_config(config_path=f"/IGS/storage/storage.conf", config=self.disk_config)

        with open(f"/IGS/compute/vms/{vm_name}/{vm_name}.conf", "a") as conf_file:

            conf_file.write(f"\n[drive]\nfile = \"{part['name']}\"\nformat = \"raw\"\n")

            conf_file.close()

        return 0
