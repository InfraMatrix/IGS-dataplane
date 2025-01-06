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
from concurrent import futures

from compute import compute

from storage import storage

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    compute.compute_pb2_grpc.add_vmmServicer_to_server(
        compute.VMMServicer(), server
    )

    storage.storage_pb2_grpc.add_smServicer_to_server(
        storage.SMServicer(), server
    )

    server.add_insecure_port('[::]:50051')
    server.start()

    print("Started the dataplane server on port 50051")

    server.wait_for_termination()

if __name__ == "__main__":

    serve()
