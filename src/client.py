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

from generated import hdp_pb2, hdp_pb2_grpc

def print_commands():

    print("Press 1 to create a VM")
    print("Press 2 to delete a VM")
    print("Press 3 to start a VM")
    print("Press 4 to shutdown a VM")
    print("Press 5 to resume a VM")
    print("Press 6 to stop a VM")
    print("Press 7 to get a VM's status")
    print("Press 8 to connect to a VM")
    print("Press 9 to end the session\n")

def pick_vm(stub=None, status=None, action=""):

    request = hdp_pb2.GetVMSRequest(status=status)
    response = stub.GetVMS(request)

    vms = response.vm_names
    num_vms = len(vms)

    vm_num = -1
    while (vm_num < 0 or vm_num > num_vms):

        print(f"Input the vm that you want to {action}:")

        for i in range(1, num_vms + 1):
            print(f"{i}: {vms[i-1]}")

        vm_num = int(input("")) - 1

    return vm_num

def process_command(cmd="", stub=None):

    if (cmd == "1"):

        request = hdp_pb2.CreateVMRequest()
        response = stub.CreateVM(request)

        print(f"VM Created: {response.vm_name}")

    elif (cmd == "2"):

        vm_num = pick_vm(stub=stub, status=1, action="delete")

        print(vm_num)

        request = hdp_pb2.DeleteVMRequest(vm_number=vm_num)
        response = stub.DeleteVM(request)

        print(f"VM Deleted: {response.vm_name}")

    elif (cmd == "3"):

        vm_num = pick_vm(stub=stub, status=2, action="start")

        request = hdp_pb2.StartVMRequest(vm_number=vm_num)
        response = stub.StartVM(request)

        print(f"VM Started: {response.vm_name}")

    elif (cmd == "4"):

        vm_num = pick_vm(stub=stub, status=3, action="shut down")

        request = hdp_pb2.ShutdownVMRequest(vm_number=vm_num)
        response = stub.ShutdownVM(request)

        print(f"VM Shut Down: {response.vm_name}")

    elif (cmd == "5"):

        vm_num = pick_vm(stub=stub, status=4, action="resume")

        request = hdp_pb2.ResumeVMRequest(vm_number=vm_num)
        response = stub.ResumeVM(request)

        print(f"VM Resumed: {response.vm_name}")

    elif (cmd == "6"):

        vm_num = pick_vm(stub=stub, status=5, action="stop")

        request = hdp_pb2.StopVMRequest(vm_number=vm_num)
        response = stub.StopVM(request)

        print(f"VM Stopped: {response.vm_name}")

    elif (cmd == "7"):

        vm_num = pick_vm(stub=stub, status=3, action="monitor its status")

        request = hdp_pb2.GetVMStatusRequest(vm_number=vm_num)
        response = stub.GetVMStatus(request)

        print(f"VM Status: {response.vm_status}")

    else:
        print("Exiting")
        exit()

    """elif (cmd == "3"):
        vm_manager.start_vm()

    elif (cmd == "4"):
        vm_manager.shutdown_vm()

    elif (cmd == "5"):
        vm_manager.resume_vm()

    elif (cmd == "6"):
        vm_manager.stop_vm()

    elif (cmd == "7"):
        vm_manager.get_vm_status()

    elif (cmd == "8"):
        vm_manager.connect_to_vm()"""


    print("\n")

def vm_manager_shell(stub=None):

    print("\nWelcome to the VM Manager!\n")

    while(True):

        print_commands()
        command = input("")
        process_command(command, stub)

def main():

    channel = grpc.insecure_channel('localhost:50051')
    
    stub = hdp_pb2_grpc.vmmStub(channel)

    vm_manager_shell(stub)

if __name__ == '__main__':
    main()