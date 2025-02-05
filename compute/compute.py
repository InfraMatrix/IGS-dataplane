#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import time
import socket
import select
import sys
import threading
import os
import subprocess

from .generated import compute_pb2, compute_pb2_grpc
from network.generated import network_pb2, network_pb2_grpc

from compute.vm_manager import VMManager

def pick_vm(stub=None, status=None, action=""):
    request = compute_pb2.GetVMSRequest(status=status)
    response = stub.GetVMS(request)

    vms = response.vm_names
    num_vms = len(vms)
    if (num_vms == 0):
        print(f"No VMs to {action}")
        return -1

    vm_num = -1
    while (vm_num < 0 or vm_num > num_vms):
        print(f"Input the VM that you want to {action}:")

        for i in range(1, num_vms + 1):
            print(f"{i}: {vms[i-1]}")

        vm_num = int(input("\n")) - 1

        print("")

    return (vm_num, vms[vm_num])

def process_compute_command(cmd="", compute_stub=None, network_stub=None):
    print("")
    if (cmd == "1"):
        request = compute_pb2.CreateVMRequest()
        response = compute_stub.CreateVM(request)
        if(response.vm_name == ""):
            print(f"Failed to create VM. You must first create the base ubuntu image in order to generate a VM based off of it.")
            print(f"Please follow the creating_base_ubuntu_image guide in the documentation.")
        else:
            print(f"VM Created: {response.vm_name}")

    elif (cmd == "2"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=1, action="delete")
        if (vm_num == -1):
            return

        request = compute_pb2.DeleteVMRequest(vm_number=vm_num)
        response = compute_stub.DeleteVM(request)

        print(f"VM Deleted: {response.vm_name}")

    elif (cmd == "3"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=2, action="start")
        if (vm_num == -1):
            return

        request = compute_pb2.StartVMRequest(vm_number=vm_num)
        response = compute_stub.StartVM(request)

        print(f"VM Started: {response.vm_name}")

    elif (cmd == "4"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=3, action="shut down")
        if (vm_num == -1):
            return

        request = compute_pb2.ShutdownVMRequest(vm_number=vm_num)
        response = compute_stub.ShutdownVM(request)

        print(f"VM Shut Down: {response.vm_name}")

    elif (cmd == "5"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=4, action="resume")
        if (vm_num == -1):
            return

        request = compute_pb2.ResumeVMRequest(vm_number=vm_num)
        response = compute_stub.ResumeVM(request)

        print(f"VM Resumed: {response.vm_name}")

    elif (cmd == "6"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=5, action="stop")
        if (vm_num == -1):
            return

        request = compute_pb2.StopVMRequest(vm_number=vm_num)
        response = compute_stub.StopVM(request)

        print(f"VM Stopped: {response.vm_name}")

    elif (cmd == "7"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=5, action="monitor its status")
        if (vm_num == -1):
            return

        request = compute_pb2.GetVMStatusRequest(vm_number=vm_num)
        response = compute_stub.GetVMStatus(request)

        print(f"VM Status: {response.vm_status}")

    elif (cmd == "8"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=5, action="connect to over serial")
        if (vm_num == -1):
            return

        request = compute_pb2.StartPTYConnectionRequest(vm_number=vm_num)
        response = compute_stub.StartPTYConnection(request)

        print("Connecting to server\n")

        time.sleep(1)

        client = socket.socket()
        client.connect(("0.0.0.0", 9001))

        client.send(b"\n")

        print("Connected to server, patching you into the VM\n")

        continue_processing = True
        while continue_processing:
            try:
                fds, _, _ = select.select([sys.stdin, client], [], [], 0.1)
                for fd in fds:
                    if fd is sys.stdin:
                        data = sys.stdin.buffer.read1(1024)
                        if data:
                            client.send(data)

                    else:
                        data = client.recv(1024)
                        if data:
                            sys.stdout.buffer.write(data)

                        sys.stdout.buffer.flush()

            except KeyboardInterrupt:
                client.send(b"exit\n\n")
                continue_processing = False

        client.close()

    elif (cmd == "9"):
        vm_num, vm_name = pick_vm(stub=compute_stub, status=5, action="connect to over SSH")
        if (vm_num == -1):
            return

        request = network_pb2.GetVMIPRequest(vm_name=vm_name)
        response = network_stub.GetVMIP(request)
        vm_ip = response.vm_ip_addr

        ssh_command = [
            "sudo", "ssh",
            "-i", f"/IGS/compute/vms/{vm_name}/id_rsa",
            "-o", "StrictHostKeyChecking=no",
            f"ubuntu@{vm_ip}"
        ]
        print("Run the following command in another shell or this one after exiting the dataplane client:\n")
        print(' '.join(ssh_command))

    else:
        print("Exiting")

class VMMServicer(compute_pb2_grpc.vmmServicer):

    def __init__(self):
        self.server_socket = None

    def setup_vm_manager(self, network_manager):
        self.vm_manager = VMManager(network_manager=network_manager)

    def GetVMS(self, request, context):
        response = self.vm_manager.get_vms(request.status)
        return compute_pb2.GetVMSResponse(vm_names=response)

    def CreateVM(self, request, context):
        response = self.vm_manager.create_vm()
        return compute_pb2.CreateVMResponse(vm_name=response)

    def DeleteVM(self, request, context):
        vm_name = self.vm_manager.get_vms(1)[request.vm_number]
        response = self.vm_manager.delete_vm(vm_num=request.vm_number)
        return compute_pb2.DeleteVMResponse(vm_name=vm_name)

    def StartVM(self, request, context):
        vm_name = self.vm_manager.get_vms(2)[request.vm_number]
        response = self.vm_manager.start_vm(vm_num=request.vm_number)
        return compute_pb2.StartVMResponse(vm_name=vm_name)

    def ShutdownVM(self, request, context):
        vm_name = self.vm_manager.get_vms(3)[request.vm_number]
        response = self.vm_manager.shutdown_vm(vm_num=request.vm_number)
        return compute_pb2.ShutdownVMResponse(vm_name=vm_name)

    def ResumeVM(self, request, context):
        vm_name = self.vm_manager.get_vms(4)[request.vm_number]
        response = self.vm_manager.resume_vm(vm_num=request.vm_number)
        return compute_pb2.ResumeVMResponse(vm_name=vm_name)

    def StopVM(self, request, context):
        vm_name = self.vm_manager.get_vms(5)[request.vm_number]
        response = self.vm_manager.stop_vm(vm_num=request.vm_number)
        return compute_pb2.StopVMResponse(vm_name=response)

    def GetVMStatus(self, request, context):
        vm_name = self.vm_manager.get_vms(3)[request.vm_number]
        response = self.vm_manager.get_vm_status(vm_num=request.vm_number)
        return compute_pb2.GetVMStatusResponse(vm_status=response)

    def run_pty_connection(self, client, pty_path):
        pty = os.open(pty_path, os.O_RDWR | os.O_NONBLOCK)
        while True:
            try:
                fds, _, _ = select.select([client, pty], [], [], 0.1)
                for fd in fds:
                    if fd is client:
                        data = client.recv(1024)
                        if data:
                            os.write(pty, data)
                    else:
                        data = os.read(pty, 1024)
                        if data:
                            client.send(data)
            except:
                break

    def StartPTYConnection(self, request, context):
        vm_conn = self.vm_manager._running_vms[request.vm_number]

        def pty_server():
            if (self.server_socket== None):
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server.bind(("0.0.0.0", 9001))
                server.listen(1)
                self.server_socket = server

            try:
                print("Waiting for connection from client\n")
                client, addr = self.server_socket.accept()
                print("Accepted connection\n")
                self.run_pty_connection(client, vm_conn.serial_conn)

            except socket.error:
                pass

        thread = threading.Thread(target=pty_server)
        thread.daemon = True
        thread.start()

        return compute_pb2.StartPTYConnectionResponse(vm_number=request.vm_number)

