#!/bin/bash

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
