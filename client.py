#!/usr/bin/env python3

# Copyright (c) 2024 InfraMatrix. All rights reserved.

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

import grpc
import sys

from compute import compute

from storage import storage

def print_subsytems():

    print("Press 1 to invoke compute subsystem")
    print("Press 2 to invoke network subsystem")
    print("Press 3 to invoke storage subsystem")
    print("Press 4 to exit the dataplane\n")

def print_compute_commands():

    print("Press 1 to create a VM")
    print("Press 2 to delete a VM")
    print("Press 3 to start a VM")
    print("Press 4 to shutdown a VM")
    print("Press 5 to resume a VM")
    print("Press 6 to stop a VM")
    print("Press 7 to get a VM's status")
    print("Press 8 to connect to a VM")

def print_storage_commands():

    print("Press 1 to get available disks\n")

def dataplane_shell(compute_stub=None, storage_stub=None):

    print("\nWelcome to the dataplane shell\n")

    while(True):

        print_subsytems()
        subsystem = input("")

        if (subsystem == "1"):

            print_compute_commands()
            command = input("")
            compute.process_compute_command(command, compute_stub)

        elif (subsystem == "3"):

            print_storage_commands()
            command = input("")
            storage.process_storage_command(command, storage_stub)

        elif (subsystem == "4"):

            exit()

def main():

    channel = grpc.insecure_channel('localhost:50051')
    
    stub = compute.compute_pb2_grpc.vmmStub(channel)

    dataplane_shell(stub)

if __name__ == '__main__':

    main()
