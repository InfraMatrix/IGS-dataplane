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

import os
import requests
import hashlib
from tqdm import tqdm

class DistroManager:

    def __init__(self):

        self.iso_location = "/IGS/compute/isos"
        os.makedirs(self.iso_location, exist_ok=True)

    def download_ubuntu_iso(self, version="22.04.5"):

        base_url = f"https://releases.ubuntu.com"
        iso_fname = f"ubuntu-{version}-live-server-amd64.iso"
        iso_url = f"{base_url}/{version}/{iso_fname}"

        iso_path = f"{self.iso_location}/ubuntu/{iso_fname}"

        if os.path.exists(f"{self.iso_location}/ubuntu/ubuntu-{version}-live-server-amd64.iso"):
            print("Ubuntu iso already exists")
            return

        os.makedirs(self.iso_location + "/ubuntu/", exist_ok=True)

        print(f"Downloading Ubuntu {version} iso")
        print(f"Please wait...\n")

        response = requests.get(iso_url, stream=True)

        tsize = int(response.headers.get('content-length', 0))
        bsize = 1024 ** 2

        with open(iso_path, 'wb') as f:
            with tqdm(total=tsize, unit='B', unit_scale=True) as pbar:
                for data in response.iter_content(bsize):
                    f.write(data)
                    pbar.update(len(data))

        print("Finished downloading Ubuntu iso")