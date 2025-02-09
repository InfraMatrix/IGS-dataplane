#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import os
import requests
import hashlib
import sys
from tqdm import tqdm
import subprocess
import shutil

class DistroManager:

    def __init__(self): ...
    def download_ubuntu_iso(self, version): ...
    def verify_ubuntu_image(self, version): ...
    def generate_ubuntu_image(self, version): ...

    def __init__(self):
        self.iso_location = "/IGS/compute/isos"
        self.image_location = "/IGS/compute/images"
        os.makedirs(self.iso_location, exist_ok=True)

    def download_ubuntu_iso(self, version="22.04.5"):
        base_url = f"https://releases.ubuntu.com"
        iso_fname = f"ubuntu-{version}-live-server-amd64.iso"
        iso_url = f"{base_url}/{version}/{iso_fname}"
        iso_path = f"{self.iso_location}/ubuntu/{iso_fname}"

        if os.path.exists(f"{self.iso_location}/ubuntu/ubuntu-{version}-live-server-amd64.iso"):
            return

        os.makedirs(self.iso_location + "/ubuntu/", exist_ok=True)

        print(f"Downloading Ubuntu {version} iso from {iso_url}")
        print(f"Please wait...\n")

        subprocess.run([
            'curl', '-L', '-o', iso_path,
            '--progress-bar',
            iso_url
        ], check=True)

        print("\nFinished downloading Ubuntu iso")

    def verify_ubuntu_image(self, version="22.04.5"):
        #self.download_ubuntu_iso(version=version)

        if os.path.exists(f"{self.image_location}/ubuntu_{version}_base.qcow2"):
            return 0

        #self.generate_ubuntu_image(version=version)

        print("An ubuntu base image has not been created yet. Please follow the creating_ubuntu_base_image steps to enable IGS.")
        return 1

    def generate_ubuntu_image(self, version="22.04.5"):
        image_path = f"/IGS/compute/images/ubuntu_{version}_base.qcow2"
        try:
            subprocess.run([
                'qemu-img', 'create',
                '-f', 'qcow2', image_path,
                f'10G'
            ], check=True)

            print(f"Created base image disk: {image_path}")

        except subprocess.CalledProcessError as e:
            print(f"Failed to create disk: {e}")
            return False

        os.makedirs("iso_mount", exist_ok=True)

        mount_iso_cmd = [
            "mount",
            "-o", "loop",
            f"{self.iso_location}/ubuntu/ubuntu-22.04.5-live-server-amd64.iso", f"iso_mount"
        ]
        subprocess.run(mount_iso_cmd)

        run_ubuntu_base_generation_cmd = [
            "qemu-system-x86_64",
            "-machine", "q35",
            "-enable-kvm",
            "-m", "6G",
            "-cpu", "host",
            "-serial", "mon:stdio",
            "-drive", f"file={image_path},format=qcow2",
            "-drive", f"file=/IGS/compute/isos/ubuntu/ubuntu-22.04.5-live-server-amd64.iso,media=cdrom",
            "-net", "nic", "-net", "user",
            "-kernel", "iso_mount/casper/vmlinuz",
            "-initrd", "iso_mount/casper/initrd",
            "-nographic",
            "-boot", "menu=on",
            "-append", "\"console=ttyS0 only-ubiquity\""
        ]
        process = subprocess.run(run_ubuntu_base_generation_cmd)

        mount_iso_cmd = [
            "umount", "iso_mount"
        ]
        subprocess.run(mount_iso_cmd)

        shutil.rmtree('iso_mount')

        setup_base_cmdline = [
            "./setup/setup_base_image.sh"
        ]
        subprocess.run(setup_base_cmdline)

        os.system('clear')

        print("Compressing the Ubuntu base image. Please wait, this will take a while..\n")

        compress_ubuntu_base_image_cmd = [
            "qemu-img",
            "convert",
            "-c",
            "-O", "qcow2",
            f"{image_path}", f"{self.image_location}/compressed_ubuntu"
        ]
        subprocess.run(compress_ubuntu_base_image_cmd)

        shutil.move(f"{self.image_location}/compressed_ubuntu", f"{image_path}")

        return 0
