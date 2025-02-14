#!/bin/bash

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

install_dependencies()
{
    if ! dpkg -l | grep -q "grafana"; then
        echo "Setting up grafana repo\n"
        sudo mkdir -p /etc/apt/keyrings/
        wget -q -O - https://apt.grafana.com/gpg.key | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
        echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main" | \
        sudo tee -a /etc/apt/sources.list.d/grafana.list
    fi

    sudo apt-get update && sudo apt-get install -y \
    python3-full \
    python3-pip \
    python3-dev \
    python3-parted \
    libparted-dev \
    libvirt-dev \
    libvirt-daemon-system > /dev/null \
    genisoimage \
    openvswitch-switch \
    openvswitch-common \
    apt-transport-https \
    software-properties-common \
    wget \
    prometheus \
    grafana

    python3 -m venv IGS_venv
    source IGS_venv/bin/activate

    sudo systemctl start libvirtd
    sudo systemctl enable libvirtd
    sudo systemctl enable openvswitch-switch.service
    sudo systemctl stop prometheus
    sudo systemctl disable prometheus

    pip3 install \
    pytest \
    grpcio-tools \
    grpcio \
    libvirt-python \
    requests \
    tqdm \
    pyroute2 \
    pyparted \
    pyyaml \
    cryptography \
    psutil \
    prometheus_client

    deactivate
}

generate_grpc_scripts()
{
    source IGS_venv/bin/activate

    cd compute
    sudo rm -rf generated
    ./generate_grpc_scripts.sh
    cd ../network
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
    printf "\nInstalling system dependencies. Please be patient. This may take a while...\n"
    install_dependencies

    printf "\nFinished installing python dependencies\n"
    generate_grpc_scripts

    printf "\nFinished generating messaging scripts\n"
    create_IGS_directories

    printf "\nFinished installing IGS\n\n"
}

main
