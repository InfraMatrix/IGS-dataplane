#!/usr/bin/env python3
 
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

class VM:

    def __init__(self): ...

    def __init__(self, vm_name, disk_location, hv_conn=None, serial_conn=None):

        self.name = vm_name
        self.disk_location = disk_location
        self.hv_conn = None
        self.serial_conn = None
