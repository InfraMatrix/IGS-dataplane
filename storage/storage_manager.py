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

import sys
import os
import json

from .disk_manager import DiskManager

class StorageManager:

    def __init__(self): ...

    def get_disks(self): ...
    def get_free_disks(self): ...

    def add_disk(self, disk_num, part_size): ...

    def get_vm_disks(self, vm_name): ...
    def attach_disk_to_vm(self, vm_name): ...
    def detach_disk_from_vm(self, vm_name): ...

    def __init__(self):

        self.disk_manager = DiskManager()

    def get_disks(self):

        return self.disk_manager.get_disks()

    def get_free_disks(self):

        return self.disk_manager.get_free_disks()

    def add_disk(self, disk_num, part_size):

        return self.disk_manager.add_disk(disk_num, part_size)

    def get_vm_disks(self, vm_name):

        return self.disk_manager.get_vm_disks(vm_name)

    def attach_disk_to_vm(self, vm_name):

        return self.disk_manager.attach_disk_to_vm(vm_name)

    def detach_disk_from_vm(self, vm_name, vm_disk_name):

        return self.disk_manager.detach_disk_from_vm(vm_name, vm_disk_name)
