#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import grpc
from concurrent import futures

from compute import compute

from network import network

from storage import storage

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

    vmm_servicer = compute.VMMServicer()
    nm_servicer = network.NMServicer()
    sm_servicer = storage.SMServicer()

    vmm_servicer.setup_vm_manager(network_manager=nm_servicer.network_manager)
    nm_servicer.set_managers(vm_manager=vmm_servicer.vm_manager)

    compute.compute_pb2_grpc.add_vmmServicer_to_server(
        vmm_servicer, server
    )

    network.network_pb2_grpc.add_nmServicer_to_server(
        nm_servicer, server
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
