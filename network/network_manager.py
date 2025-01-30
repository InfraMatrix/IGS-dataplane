#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

from pyroute2 import IPRoute
import subprocess
import sys
import random

def run_network_cmd(cmd):
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Command: {cmd} failed: {e}")
        return False

class NetworkManager:

    def __init__(self):
        self._host_network_interface = IPRoute()
        self._used_macs = []
        self.vm_ssh_ports = list(range(7600,7700))
        self.port_map = {}

        add_bridge_cmd = ["ovs-vsctl", "add-br", "ovs-vm-bridge"]
        run_network_cmd(add_bridge_cmd)

        setup_bridge_cmd = ["ip", "link", "set", "ovs-vm-bridge", "up"]
        run_network_cmd(setup_bridge_cmd)

    def setup_vm_networking_interface(self, vm_name=""):
        tap_name = vm_name + "_tap"

        if (not self._host_network_interface.link_lookup(ifname=tap_name)):
            self._host_network_interface.link('add', ifname=tap_name, kind="tuntap", mode="tap")
            tap_index = self._host_network_interface.link_lookup(ifname=tap_name)[0]
            self._host_network_interface.link('set', index=tap_index, state='up')

        result = subprocess.run(['ovs-vsctl', 'add-port', "vm_switch", tap_name])

        return tap_name
    
    def generate_mac(self):
        mac = ""
        while (mac not in self._used_macs):
            mac = '02:%02x:%02x:%02x:%02x:%02x' % tuple(random.randint(0, 255) for _ in range(5))
            self._used_macs.append(mac)
            return mac

    def acquire_vm_port(self, vm_name):
        vm_port = self.vm_ssh_ports[0]
        self.port_map[vm_name] = vm_port
        self.vm_ssh_ports.pop(0)
        return vm_port

    def release_vm_port(self, vm_name):
        self.vm_ssh_ports.append(self.port_map(vm_name))
        self.port_map.remove(vm_name)

    def allocate_vm_tap_interface(self, vm_name):
        tap_name = f"tap_{vm_name}"[:15]

        print("Creating VM TAP")

        create_tap_cmd = ["ip", "tuntap", "add", "dev", tap_name, "mode", "tap"]
        run_network_cmd(create_tap_cmd)

        add_tap_ovs_cmd = ["ovs-vsctl", "add-port", "ovs-vm-bridge", tap_name]
        run_network_cmd(add_tap_ovs_cmd)

        set_tap_up_cmd = ["ip", "link", "set", tap_name, "up"]
        run_network_cmd(set_tap_up_cmd)

        return tap_name

    def deallocate_vm_tap_interface(self, vm_name):
        tap_name = f"tap_{vm_name}"[:15]

        add_tap_ovs_cmd = ["ovs-vsctl", "del-port", "ovs-vm-bridge", tap_name]
        run_network_cmd(add_tap_ovs_cmd)

        create_tap_cmd = ["ip", "tuntap", "del", "dev", tap_name, "mode", "tap"]
        run_network_cmd(create_tap_cmd)
