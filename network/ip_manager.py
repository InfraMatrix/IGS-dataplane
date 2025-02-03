#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

class IPManager:

    def __init__(self, network_address=""):
        self.network_addr = network_address
        self.start = 5
        self.end = 252
        self.used_ips = {}
        self.free_ips = {
        f'{i}': ""
        for i in range(self.start, self.end + 1)
    }

    def acquire_ip(self, vm_name=""):
        ip = next(iter(self.free_ips))
        del self.free_ips[ip]
        self.used_ips[ip] = vm_name
        return ip

    def release_ip(self, ip):
        del self.used_ips[ip]
        self.free_ips[ip] = ""
        return