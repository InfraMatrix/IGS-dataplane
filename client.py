#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import grpc
import sys

from compute import compute

from network import network

from storage import storage

def print_subsytems():
    print("\nPress 1 to invoke compute subsystem")
    print("Press 2 to invoke network subsystem")
    print("Press 3 to invoke storage subsystem")
    print("Press 4 to exit the dataplane")

def print_compute_commands():
    print("\nPress 1 to create a VM")
    print("Press 2 to delete a VM")
    print("Press 3 to start a VM")
    print("Press 4 to shutdown a VM")
    print("Press 5 to resume a VM")
    print("Press 6 to stop a VM")
    print("Press 7 to get a VM's status")
    print("Press 8 to connect to a VM over serial")
    print("Press 9 to connect to a VM over SSH")

def print_network_commands():
    print("\nThere are currently no network commands")

def print_storage_commands():
    print("\nPress 1 to get system disks")
    print("Press 2 to add a disk to IGS")
    print("Press 3 to remove a disk from IGS")
    print("Press 4 to attach a disk partition to a vm")
    print("Press 5 to detach a disk partition from a vm")

def dataplane_shell(compute_stub=None, network_stub=None, storage_stub=None):
    print("\nWelcome to the dataplane shell\n")

    while(True):
        print_subsytems()
        subsystem = input("\n")
        if (subsystem == "1"):
            print_compute_commands()
            command = input("\n")
            compute.process_compute_command(command, compute_stub, network_stub)

        elif (subsystem == "2"):
            print_network_commands()

        elif (subsystem == "3"):
            print_storage_commands()
            command = input("\n")
            storage.process_storage_command(command, storage_stub, compute_stub)

        elif (subsystem == "3"):
            exit()

def main():
    channel = grpc.insecure_channel('localhost:50051')
    compute_stub = compute.compute_pb2_grpc.vmmStub(channel)
    network_stub = network.network_pb2_grpc.nmStub(channel)
    storage_stub = storage.storage_pb2_grpc.smStub(channel)
    dataplane_shell(compute_stub, network_stub, storage_stub)

if __name__ == '__main__':
    main()
