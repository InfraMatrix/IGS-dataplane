#!/bin/bash

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

install_python_dependencies()
{
    sudo apt-get install -y \
    python3-full \
    python3-pip \
    python3-dev \
    python3-parted \
    libparted-dev \
    libvirt-dev \
    libvirt-daemon-system > /dev/null

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
    pyyaml

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
