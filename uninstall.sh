#!/bin/bash

# Copyright © 2025 InfraMatrix. All Rights Reserved.

# SPDX-License-Identifier: BSD-3-Clause

remove_IGS_directories()
{
    rm -rf IGS_venv
    sudo rm -rf /IGS

    cd compute
    sudo rm -rf generated
    cd ../storage
    sudo rm -rf generated
}

main()
{
    remove_IGS_directories

    printf "\nFinished uninstalling IGS\n\n"
}

main
