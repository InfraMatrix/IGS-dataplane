#!/bin/sh

# Copyright 2024 InfraMatrix

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

rm -rf generated
mkdir -p generated

touch generated/__init__.py

python3 -m grpc_tools.protoc \
  -I protos \
  --python_out=generated \
  --grpc_python_out=generated \
  protos/hdp.proto

sed -i 's/^import \([a-zA-Z0-9_]*_pb2\) as /from . import \1 as /g' generated/hdp_pb2.py
sed -i 's/^import \([a-zA-Z0-9_]*_pb2\)$/from . import \1/g' generated/hdp_pb2.py
sed -i 's/^import \([a-zA-Z0-9_]*_pb2\) as /from . import \1 as /g' generated/hdp_pb2_grpc.py
sed -i 's/^import \([a-zA-Z0-9_]*_pb2\)$/from . import \1/g' generated/hdp_pb2_grpc.py

