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

from compute.generated import compute_pb2, compute_pb2_grpc

from compute.compute import pick_vm

def process_storage_command(cmd="", storage_stub=None, compute_stub=None):
    if (cmd == "1"):
        request = storage_pb2.GetDisksRequest()
        response = storage_stub.GetDisks(request)

        print(f"\nAvailable and IGS Disks:\n")

        for disk in response.disk_names:
            print(f"{disk}")

    elif (cmd == "2"):
        fdrequest = storage_pb2.GetFreeDisksRequest()
        fdresponse = storage_stub.GetFreeDisks(fdrequest)

        if (len(fdresponse.disk_names) == 0):
            print(f"\nNo disks to add to IGS")
            return

        disk_num = -1
        while (disk_num < 0 or disk_num >= len(fdresponse.disk_names)):
            print("Please select a disk to add to IGS:")

            count = 1
            for i in fdresponse.disk_names:
                print(f"{count}: {i}")

                count += 1

            disk_num = int(input("\n")) - 1

        part_size = -1
        disk_increment=5
        while(part_size < 0 or part_size > 50 or part_size % 5 != 0):
            print("\nPlease give a size of the partitions for the disk in GB(increments of 5), greater than 0 and less than or equal to 50:")

            part_size = int(input("\n"))

        adrequest = storage_pb2.AddDiskRequest(disk_num=disk_num, part_size=part_size)
        adresponse = storage_stub.AddDisk(adrequest)
        if (adresponse.op_status == 0):
            print("\nAdded the disk to storage")

        else:
            print("\nFailed to add disk to storage")

    elif (cmd == "3"):

        gsdrequest = storage_pb2.GetScalerDisksRequest()
        gsdresponse = storage_stub.GetScalerDisks(gsdrequest)

        print('1')

        disk_names = gsdresponse.disk_names
        if (len(disk_names) == 0):
            print(f"\nNo disks to remove from IGS")
            return

        disk_num = -1
        while (disk_num < 0 or disk_num >= len(disk_names)):
            print("Please select a disk to remove from IGS:")

            count = 1
            for i in gsdresponse.disk_names:
                print(f"{count}: {i}")

                count += 1

            disk_num = int(input("\n")) - 1

        rdrequest = storage_pb2.RemoveDiskRequest(disk_num=disk_num)
        rdresponse = storage_stub.RemoveDisk(rdrequest)
        if (rdresponse.op_status == 0):
            print("\nRemoved the disk from IGS")

        else:
            print("\nFailed to remove the disk from IGS")

    elif (cmd == "4"):
        action="attach a disk to"

        request = compute_pb2.GetVMSRequest(status=1)
        response = compute_stub.GetVMS(request)

        vms = response.vm_names
        num_vms = len(vms)
        if (num_vms == 0):
            print(f"\nNo VMs to {action}")
            return -1

        vm_num = -1
        while (vm_num < 0 or vm_num > num_vms):
            print(f"Input the VM that you want to {action}:")

            for i in range(1, num_vms + 1):
                print(f"{i}: {vms[i-1]}")

            vm_num = int(input("\n")) - 1

        print("")

        adtvmrequest = storage_pb2.AttachDiskToVMRequest(vm_name=vms[vm_num])
        adtvmresponse = storage_stub.AttachDiskToVM(adtvmrequest)
        if (adtvmresponse.op_status == 0):
            print("Added disk to the VM. Restart the VM to see the changes.")

        else:
            print("\nFailed to add disk to storage")

    elif (cmd == "5"):
        action="remove a disk from"

        request = compute_pb2.GetVMSRequest(status=1)
        response = compute_stub.GetVMS(request)

        vms = response.vm_names
        num_vms = len(vms)

        if (num_vms == 0):
            print(f"\nNo VMs to {action}")

            return -1

        vm_num = -1
        while (vm_num < 0 or vm_num >= num_vms):
            print(f"Input the VM that you want to {action}:")

            for i in range(1, num_vms + 1):
                print(f"{i}: {vms[i-1]}")

            vm_num = int(input("\n")) - 1

        print("")

        gvmdrequest = storage_pb2.GetVMDisksRequest(vm_name=vms[vm_num])
        gvmdresponse = storage_stub.GetVMDisks(gvmdrequest)

        vm_disks = gvmdresponse.vm_disk_names
        num_vm_disks = len(vm_disks)

        if (num_vm_disks == 0):
            print(f"\nNo disks to detach from the VM")
            return -1

        vm_disk_num = -1
        while (vm_disk_num < 0 or vm_disk_num >= num_vm_disks):
            print(f"Input the disk that you want to remove from the VM:")

            for i in range(1, num_vm_disks + 1):
                print(f"{i}: {vm_disks[i-1]}")

            vm_disk_num = int(input("\n")) - 1

        selected_vm = vms[vm_num]
        selected_disk = vm_disks[vm_disk_num]

        ddfvmrequest = storage_pb2.DetachDiskFromVMRequest(vm_name=selected_vm, vm_disk_name=selected_disk)
        ddfvmresponse = storage_stub.DetachDiskFromVM(ddfvmrequest)

        if (ddfvmresponse.op_status == 0):
            print("\nDetached disk from VM. Restart the VM to see the changes.")

        else:
            print("\nFailed to detach disk from VM")

    else:
        print("Exiting")

class SMServicer(storage_pb2_grpc.smServicer):

    def __init__(self):
        self.s_manager = StorageManager()
        self.server_socket = None

    def GetDisks(self, request, context):
        disk_names = self.s_manager.get_free_disks()
        return storage_pb2.GetDisksResponse(disk_names=disk_names)

    def GetFreeDisks(self, request, context):
        disk_names = self.s_manager.get_free_disks()
        return storage_pb2.GetFreeDisksResponse(disk_names=disk_names)

    def GetScalerDisks(self, request, context):
        disk_names = self.s_manager.get_scaler_disks()
        return storage_pb2.GetScalerDisksResponse(disk_names=disk_names)

    def GetVMDisks(self, request, context):
        vm_disk_names = self.s_manager.get_vm_disks(request.vm_name)
        return storage_pb2.GetVMDisksResponse(vm_disk_names=vm_disk_names)

    def AddDisk(self, request, context):
        op_status = self.s_manager.add_disk(request.disk_num, request.part_size)
        return storage_pb2.AddDiskResponse(op_status=op_status)

    def RemoveDisk(self, request, context):
        op_status = self.s_manager.remove_disk(request.disk_num)
        return storage_pb2.AddDiskResponse(op_status=op_status)

    def AttachDiskToVM(self, request, context):
        op_status = self.s_manager.attach_disk_to_vm(request.vm_name)
        return storage_pb2.AttachDiskToVMResponse(op_status=op_status)

    def DetachDiskFromVM(self, request, context):
        op_status = self.s_manager.detach_disk_from_vm(request.vm_name, request.vm_disk_name)
        return storage_pb2.DetachDiskFromVMResponse(op_status=op_status)
