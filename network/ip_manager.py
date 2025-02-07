#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import yaml
from pathlib import Path

class IPManager:

    def __init__(self, network_address=""):
        self.network_addr = network_address
        self.network_subnet = '.'.join(network_address.split('.')[:3])
        self.start = 5
        self.end = 252
        self.used_ips = {}
        self.free_ips = {
        f'{i}': ""
        for i in range(self.start, self.end + 1)
        }
        self.inventory_ips()

    def inventory_ips(self):
        vm_dir = Path("/IGS/compute/vms")
        for vm_dir in vm_dir.iterdir():
            cloudinit_path = vm_dir / "user-data"
            try:
                with open(cloudinit_path) as f:
                    config = yaml.safe_load(f)
                for file in config.get('write_files', []):
                    if file.get('path') == '/etc/netplan/99-netcfg.yaml':
                        netplan = yaml.safe_load(file['content'])
                        for interface in netplan.get('network', {}).get('ethernets', {}).values():
                            if interface.get('addresses'):
                                ip = interface['addresses'][0].split('/')[0].split('.')[-1]
                                self.used_ips[vm_dir.name] = ip
                                del self.free_ips[ip]
                                return
            except Exception as e:
                print(f"Error getting IP: {e}")

    def acquire_ip(self, vm_name=""):
        ip = next(iter(self.free_ips))
        del self.free_ips[ip]
        self.used_ips[vm_name] = ip
        return ip

    def release_ip(self, vm_name):
        ip = self.used_ips[vm_name]
        del self.used_ips[vm_name]
        self.free_ips[ip] = ""
        return

    def get_vm_ip(self, vm_name=""):
        return f"{self.network_subnet}.{self.used_ips[vm_name]}" or ""
