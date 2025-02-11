#!/usr/bin/env python3

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

import pytest

import os

from compute.vm_manager import VMManager
from network.network_manager import NetworkManager

@pytest.fixture(scope="function")
def setup_vm_manager():
    global vm_manager
    global network_manager
    network_manager = NetworkManager()
    vm_manager = VMManager(network_manager=network_manager)
    return vm_manager

def create_vm_helper():
    global vm_manager
    vm_uuid = vm_manager.create_vm()
    IGS_vm_path = "/IGS/compute/vms"
    assert vm_uuid is not None
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/{vm_uuid}.conf")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/{vm_uuid}.qcow2")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/user-data")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/meta-data")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/cloud-init.iso")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/id_rsa")
    assert os.path.exists(f"{IGS_vm_path}/{vm_uuid}/id_rsa.pub")
    return vm_uuid

def delete_vm_helper(vm_name):
    global vm_manager
    vms = vm_manager.get_vms(status=1)
    vm_manager.delete_vm(vm_name=vm_name)
    vms = vm_manager.get_vms(status=1)
    assert len(vms) == 0

def test_compute(setup_vm_manager):
    global vm_manager
    vm_uuid = create_vm_helper()
    delete_vm_helper(vm_uuid)
