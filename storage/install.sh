#!/bin/bash

# Copyright (c) 2024 InfraMatrix. All rights reserved.

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

sudo apt install -y cephadm

cephadm add-repo --release reef
cephadm install

cephadm bootstrap --mon-ip 10.0.0.154

sudo apt-get install python3-rados
sudo apt-get install python3-rbd

