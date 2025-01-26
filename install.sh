#!/bin/bash

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

install_python_dependencies()
{
    sudo apt-get install -y \
    python3-full \
    python3-pip \
    python3-dev \
    python3-parted \
    libparted-dev \
    libvirt-dev \
    libvirt-daemon-system > /dev/null \
    genisoimage

    python3 -m venv IGS_venv
    source IGS_venv/bin/activate

    sudo systemctl start libvirtd
    sudo systemctl enable libvirtd

    pip3 install \
    grpcio-tools \
    grpcio \
    libvirt-python \
    requests \
    tqdm \
    pyroute2 \
    pyparted \
    pyyaml \
    cryptography

    deactivate
}

generate_grpc_scripts()
{
    source IGS_venv/bin/activate

    cd compute
    sudo rm -rf generated
    ./generate_grpc_scripts.sh
    cd ../storage
    sudo rm -rf generated
    ./generate_grpc_scripts.sh
    cd ..

    deactivate
}

create_IGS_directories()
{
    sudo mkdir -p /IGS
    sudo mkdir -p /IGS/compute
    sudo mkdir -p /IGS/compute/vms
    sudo mkdir -p /IGS/compute/isos
    sudo mkdir -p /IGS/compute/images
    sudo mkdir -p /IGS/storage
}

main()
{
    printf "\nInstalling python dependencies. Please be patient. This may take a while...\n"

    install_python_dependencies

    printf "\nFinished installing python dependencies\n"

    generate_grpc_scripts

    printf "\nFinished generating messaging scripts\n"

    create_IGS_directories

    printf "\nFinished installing IGS\n\n"
}

main
