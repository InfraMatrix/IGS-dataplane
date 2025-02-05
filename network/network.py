#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

from .generated import network_pb2, network_pb2_grpc

from network.network_manager import NetworkManager

class NMServicer(network_pb2_grpc.nmServicer):

    def __init__(self):
        self.network_manager = NetworkManager()
        self.server_socket = None

    def set_managers(self, vm_manager=None):
        self.network_manager.vm_manager = vm_manager

    def GetVMIP(self, request, context):
        vm_name = request.vm_name
        vm_ip = self.network_manager.get_vm_ip(vm_name=vm_name)
        return network_pb2.GetVMIPResponse(vm_ip_addr=vm_ip)
