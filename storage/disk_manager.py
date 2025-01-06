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

class DiskManager:

    def __init__(self): ...

    def get_disks(self): ...
    def _get_host_root_disk(self): ...
    def _get_host_nonroot_disks(self): ...
    def _get_free_disks(self): ...
    def _get_ceph_disks(self): ...
    def _set_ceph_disk_free_space(self): ... 

    def create_partition(self, disk_name="", size_gb=0): ...

    def __init__(self):

        self.host_root_disk = self._get_host_root_disk()

        self.disks = self._get_host_nonroot_disks()

        self.free_disks = self._get_free_disks()

        self.ceph_disks = self._get_ceph_disks()

        self._set_ceph_disk_free_space()

    def get_disks(self):

        disk_list = []

        for disk in self.free_disks:

            disk_list.append(f"{disk}")

        for disk in self.ceph_disks:

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

    
    def _get_ceph_disks(self):

        ceph_disks = []

        for disk in self.disks:

            has_ceph_part = False

            if ("children" in disk):

                for partition in disk["children"]:

                    partlabel = partition.get("partlabel")

                    if (partlabel and partlabel.startswith("ceph")):

                        has_ceph_part = True

                        break

                if (has_ceph_part):

                    ceph_disks.append(disk)
                    
                has_ceph_part = False

        return ceph_disks

    def _set_ceph_disk_free_space(self):

        for disk in self.free_disks:

            disk["free_space_gb"] = int(disk["size"] / (1024 ** 3))

        for disk in self.ceph_disks:

            fs = disk["size"]

            for partition in disk["children"]:

                fs -= partition["size"]

            disk["free_space_gb"] = int(fs / (1024 ** 3))
            disk["num_partitions"] = len(disk["children"])

    def create_partition(self, disk_name="", size_gb=0):

        if (size_gb == 0 or disk_name == ""):

            return None

        ceph_disk = None
        for disk in self.free_disks:

            if (disk_name == disk["name"]):

                self.free_disks.remove(disk)

                self.ceph_disks.append(disk)

                ceph_disk = disk

        if (ceph_disk == None):

            for disk in self.ceph_disks:

                if (disk_name == disk["name"]):

                    ceph_disk = disk

        if (ceph_disk == None or size_gb > ceph_disk["free_space_gb"]):

            return None

        return None
