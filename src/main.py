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

from vm_manager import VMManager

global vm_manager

def print_commands():

    print("Press 1 to create a VM")
    print("Press 2 to delete a VM")
    print("Press 3 to start a VM")
    print("Press 4 to shutdown a VM")
    print("Press 5 to resume a VM")
    print("Press 6 to pause a VM")
    print("Press 7 to get a VM's status")
    print("Press 8 to connect to a VM")
    print("Press 9 to end the session\n")

def process_command(cmd=""):

    if (cmd == "1"):
        vm_manager.create_vm()

    elif (cmd == "2"):
        vm_manager.delete_vm()

    elif (cmd == "3"):
        vm_manager.start_vm()

    elif (cmd == "4"):
        vm_manager.shutdown_vm()

    elif (cmd == "5"):
        vm_manager.resume_vm()

    elif (cmd == "6"):
        vm_manager.pause_vm()

    elif (cmd == "7"):
        vm_manager.get_vm_status()

    elif (cmd == "8"):
        vm_manager.connect_to_vm()

    else:
        print("Exiting")
        exit()

    print("\n")

def vm_manager_shell():

    print("Welcome to the VM Manager!\n")

    while(True):

        print_commands()
        command = input("")
        process_command(command)

if __name__ == "__main__":

    vm_manager = VMManager()

    vm_manager.connect()

    vm_manager_shell()