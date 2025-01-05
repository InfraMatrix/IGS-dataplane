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

def process_storage_command(cmd="", stub=None):

    if (cmd == "1"):

        #request = storage_pb2.GetDisksRequest()
        #response = stub.GetDisks(request)

        #print(f"Disks: {response.disk_names}")

        print(f"Disks:")

    else:

        print("Exiting")

    print("\n")
