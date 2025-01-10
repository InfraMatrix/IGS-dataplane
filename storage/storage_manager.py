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

import rados
import rbd
import sys
import os
import json

from .disk_manager import DiskManager

class StorageManager:

    def create_pool(self, name): ...
    def get_osds(self): ...

    def __init__(self, conf="/etc/ceph/ceph.conf"):

        self.disk_manager = DiskManager()

        self.cluster = rados.Rados(conffile='/etc/ceph/ceph.conf')

        self.cluster_conn = self.cluster.connect()

        self.rbd_conn = rbd.RBD()

        self.pools = self.cluster.list_pools()
        if "vm_pool" not in self.pools:

            self.create_pool(name="vm_pool")

    def create_pool(self, name=""):

        try:

            self.cluster.create_pool("vm_pool")
            self.ioctx = self.cluster.open_ioctx("vm_pool")
            self.rbd_conn.pool_init(self.ioctx)
            self.pools.append("vm_pool", True)

            return True

        except Exception as e:

            print(f"Error creating pool: {e}")

            return False

    def get_osds(self):

        try:

            cmd = json.dumps({
                "prefix": "osd ls",
                "format": "json"
            })

            ret, outbuf, outs = self.cluster.mon_command(cmd, b'')

            osds = json.loads(outbuf)

            return osds

        except Exception as e:

            print(e)

            return []

    def create_disk(self, name="", size=""):

        try:

            ts = size * 1024 * 1024 * 1024

            self.rbd_conn.create(self.ioctx, name, ts)

            return True
        
        except Exception as e:

            pass

    def delete_disk(self, name=""):

        try:

            self.rbd_conn.remove(self.ioctx, name)

        except Exception as e:

            pass