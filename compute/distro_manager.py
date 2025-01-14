#!/usr/bin/env python3

# Copyright (c) 2025 InfraMatrix. All rights reserved.

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
