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
    print("Press 2 to start a VM")
    print("Press 3 to stop a VM")
    print("Press 4 to restart a VM")
    print("Press 5 to delete a VM")
    print("Press 6 to end the session\n")

def process_command(cmd=""):

    if (cmd == "1"):
        vm_manager.create_vm()
        
    elif (cmd == "2"):
        print("Starting a VM")

    elif (cmd == "3"):
        print("Stopping a VM")

    elif (cmd == "4"):
        print("Restarting a VM")

    elif (cmd == "5"):
        print("Deleting a VM")

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