#!/bin/bash

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

rm -rf generated
mkdir -p generated

touch generated/__init__.py

python3 -m grpc_tools.protoc \
  -I protos \
  --python_out=generated \
  --grpc_python_out=generated \
  protos/storage.proto

sed -i 's/^import \([a-zA-Z0-9_]*_pb2\) as /from . import \1 as /g' generated/storage_pb2.py
sed -i 's/^import \([a-zA-Z0-9_]*_pb2\)$/from . import \1/g' generated/storage_pb2.py
sed -i 's/^import \([a-zA-Z0-9_]*_pb2\) as /from . import \1 as /g' generated/storage_pb2_grpc.py
sed -i 's/^import \([a-zA-Z0-9_]*_pb2\)$/from . import \1/g' generated/storage_pb2_grpc.py
