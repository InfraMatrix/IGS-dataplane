#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import sys
import os
import json

from .disk_manager import DiskManager

class StorageManager:

    def __init__(self): ...

    def get_disks(self): ...
    def get_free_disks(self): ...

    def add_disk(self, disk_num, part_size): ...
    def remove_disk(self, disk_name): ...

    def get_vm_disks(self, vm_name): ...
    def attach_disk_to_vm(self, vm_name): ...
    def detach_disk_from_vm(self, vm_name): ...

    def __init__(self):
        self.disk_manager = DiskManager()

    def get_disks(self):
        return self.disk_manager.get_disks()

    def get_free_disks(self):
        return self.disk_manager.get_free_disks()

    def get_scaler_disks(self):
        return self.disk_manager.get_scaler_disks()

    def add_disk(self, disk_num, part_size):
        return self.disk_manager.add_disk(disk_num, part_size)

    def remove_disk(self, disk_num):
        return self.disk_manager.remove_disk(disk_num)

    def get_vm_disks(self, vm_name):
        return self.disk_manager.get_vm_disks(vm_name)

    def attach_disk_to_vm(self, vm_name):
        return self.disk_manager.attach_disk_to_vm(vm_name)

    def detach_disk_from_vm(self, vm_name, vm_disk_name):
        return self.disk_manager.detach_disk_from_vm(vm_name, vm_disk_name)
