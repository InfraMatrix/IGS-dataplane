#!/usr/bin/env python3

#Copyright (c) 2024 InfraMatrix. All rights reserved.

#The user ("Licensee") is hereby granted permission to use this software and
#associated documentation files (the "Software"),
#subject to the express condition that Licensee shall not, under any circumstances,
#redistribute, sublicense, copy, transfer, publish, disseminate, transmit,
#broadcast, sell, lease, rent, share, loan, or otherwise make available the
#Software, in whole or in part, in any form or by any means, to any third party
#without prior written consent from the copyright holder,
#and any such unauthorized distribution shall constitute a material breach of this
#license and result in immediate, automatic termination of all rights granted
#hereunder.

import grpc
from concurrent import futures
import subprocess
import socket
import threading
import os
import select

from generated import hdp_pb2, hdp_pb2_grpc

from vm_manager import VMManager

class VMMServicer(hdp_pb2_grpc.vmmServicer):

    def __init__(self):
        self.vm_manager = VMManager()
        self.server_socket = None

    def GetVMS(self, request, context):
        response = self.vm_manager.get_vms(request.status)
        return hdp_pb2.GetVMSResponse(vm_names=response)

    def CreateVM(self, request, context):
        response = self.vm_manager.create_vm()
        return hdp_pb2.CreateVMResponse(vm_name=response)

    def DeleteVM(self, request, context):
        vm_name = self.vm_manager.get_vms(1)[request.vm_number]
        response = self.vm_manager.delete_vm(vm_num=request.vm_number)
        return hdp_pb2.DeleteVMResponse(vm_name=vm_name)

    def StartVM(self, request, context):
        vm_name = self.vm_manager.get_vms(2)[request.vm_number]
        response = self.vm_manager.start_vm(vm_num=request.vm_number)
        return hdp_pb2.StartVMResponse(vm_name=vm_name)

    def ShutdownVM(self, request, context):
        vm_name = self.vm_manager.get_vms(3)[request.vm_number]
        response = self.vm_manager.shutdown_vm(vm_num=request.vm_number)
        return hdp_pb2.ShutdownVMResponse(vm_name=vm_name)

    def ResumeVM(self, request, context):
        vm_name = self.vm_manager.get_vms(4)[request.vm_number]
        response = self.vm_manager.resume_vm(vm_num=request.vm_number)
        return hdp_pb2.ResumeVMResponse(vm_name=vm_name)

    def StopVM(self, request, context):
        vm_name = self.vm_manager.get_vms(5)[request.vm_number]
        response = self.vm_manager.stop_vm(vm_num=request.vm_number)
        return hdp_pb2.StopVMResponse(vm_name=response)

    def GetVMStatus(self, request, context):
        vm_name = self.vm_manager.get_vms(3)[request.vm_number]
        response = self.vm_manager.get_vm_status(vm_num=request.vm_number)
        return hdp_pb2.GetVMStatusResponse(vm_status=response)

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

        return hdp_pb2.StartPTYConnectionResponse(vm_number=request.vm_number)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    hdp_pb2_grpc.add_vmmServicer_to_server(
        VMMServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
