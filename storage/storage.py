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

from .generated import storage_pb2, storage_pb2_grpc

from .storage_manager import StorageManager

def process_storage_command(cmd="", stub=None):

    if (cmd == "1"):

        request = storage_pb2.GetDisksRequest()
        response = stub.GetDisks(request)

        print(f"Available and Ceph Disks:\n")

        for disk in response.disk_names:

            print(f"{disk}")

    elif (cmd == "2"):

        fdrequest = storage_pb2.GetFreeDisksRequest()
        fdresponse = stub.GetFreeDisks(fdrequest)

        if (len(fdresponse.disk_names) == 0):

            print(f"No disks to add storage")

            return

        disk_num = -1
        while (disk_num < 0 or disk_num >= len(fdresponse.disk_names)):

            print("Please select a disk to add to storage:")

            count = 1
            for i in fdresponse.disk_names:

                print(f"{count}: {i}")

                count += 1

            disk_num = int(input("\n")) - 1

        part_size = -1
        disk_increment=5
        while(part_size < 0 or part_size > 50 or part_size % 5 != 0):

            print("Please give a size of the partitions for the disk in GB(increments of 5), greater than 0 and less than or equal to 50:")

            part_size = int(input("\n"))

        adrequest = storage_pb2.AddDiskRequest(disk_num=disk_num, part_size=part_size)
        adresponse = stub.AddDisk(adrequest)

        if (adresponse.op_status == 0):

            print("\nAdded the disk to storage")

        else:

            print("\nFailed to add disk to storage")

    else:

        print("Exiting")

class SMServicer(storage_pb2_grpc.smServicer):

    def __init__(self):

        self.s_manager = StorageManager()
        self.server_socket = None

    def GetDisks(self, request, context):

        disk_names = self.s_manager.disk_manager.get_disks()

        return storage_pb2.GetDisksResponse(disk_names=disk_names)

    def GetFreeDisks(self, request, context):

        disk_names = []
        for i in self.s_manager.disk_manager.free_disks:

            disk_names.append(i["name"])

        return storage_pb2.GetFreeDisksResponse(disk_names=disk_names)

    def AddDisk(self, request, context):

        op_status = self.s_manager.disk_manager.add_disk(request.disk_num, request.part_size)

        return storage_pb2.AddDiskResponse(op_status=op_status)
