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

from pyroute2 import IPRoute

class VM:

    def __init__(self): ...

    def __init__(self, vm_name, disk_location, tap_intf=None, hv_conn=None,
                 serial_conn=None, ip_address=None, mac_address=None):
        self.name = vm_name
        self.disk_location = disk_location
        self.tap_intf = tap_intf
        self.hv_conn = hv_conn
        self.serial_conn = serial_conn
        self.ip_address = ip_address
        self.mac_address = mac_address
