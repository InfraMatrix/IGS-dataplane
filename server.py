#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

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
