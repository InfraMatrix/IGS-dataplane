#!/usr/bin/env python3

# Copyright 2024 InfraMatrix

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import grpc
from concurrent import futures

from generated import hdp_pb2, hdp_pb2_grpc

from vm_manager import VMManager

class VMMServicer(hdp_pb2_grpc.vmmServicer):

    def __init__(self):
        self.vm_manager = VMManager()

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
