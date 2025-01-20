
# Launch Guide

This document explains how to launch IGS.

## Basic Usage

1. In a terminal, start the server:
```bash
./run_server.sh
```

and you should see the server running.

2. In another terminal, start the client:
```bash
./run_client.sh
```

and you should arrive at the CLI for IGS.

If you haven't launched a VM yet, you will need to build your own Ubuntu base image.

To build the base image do the following:

1: Press 1 to enter the compute subsystem

2: Press 1 to create a VM.
After doing this, it will fetch the Ubuntu ISO.
Once the ISO has been downloaded, the server will launch a VM that you use to create the base image.

3: Go to the terminal that you launched on the server and go through the process of installing Ubuntu.
Please note that the username and password you supply will be used for VMs that are created on the fly.

4: Once you have installed ubuntu on the base image, do ctrl-a followed by x to tell QEMU to shut the VM off.

Notice that you have access to the compute and storage subsystems.
The compute subsystem manages VMs and the storage subsystem manages storage disks for the VMs.

If you receive any issues, please post on the [issues page][issues].

[issues]: https://github.com/InfraMatrix/IGS-dataplane/issues
