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
import subprocess
import random

class VMNetworkManager:

    def __init__(self):

        self._host_network_interface = IPRoute()
        self._used_macs = []
        self.vm_ssh_ports = list(range(7600,7700))
        self.port_map = {}

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
