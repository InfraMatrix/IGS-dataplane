# Creating base ubuntu image

Steps that need to be run in a base ubuntu VM to create it. Eventually we will build a system that auto-generates this on the fly.

1: Create the base ubuntu image disk:

```bash
sudo qemu-img create -f qcow2 /IGS/compute/images/ubuntu_22.04.5_base.qcow2 10G
```

2: Go through the process of setting up the VM. Plug the ISO that was downloaded by IGS plugged into or download the ubuntu server
ISO from the site.

Make sure to click to install SSH on the VM.
Also, pick a user and password that can be easily remembered.

```bash
sudo qemu-system-x86_64 \
-machine q35,accel=kvm \
-cpu host \
-m 6G \
-cdrom /IGS/compute/isos/ubuntu/ubuntu-22.04.5-live-server-amd64.iso \
-drive file=/IGS/compute/images/ubuntu_22.04.5_base.qcow2,if=virtio,format=qcow2 \
-net nic -net user
```

3: After installing ubuntu server onto the image, boot the image so we can install universal packages and proceed to step 3:

```bash
sudo qemu-system-x86_64 \
-machine q35,accel=kvm \
-cpu host \
-m 6G \
-drive file=/IGS/compute/images/ubuntu_22.04.5_base.qcow2,if=virtio,format=qcow2 \
-device virtio-serial-pci \
-chardev socket,path=/tmp/qga.sock,server,nowait,id=qga0 \
-device virtserialport,chardev=qga0,name=org.qemu.guest_agent.0 \
-net nic -net user
```

4: We are in the base ubuntu image. Run the following commands to set everything up
for the VM instances that you plan to spin up.

First, add the following to /etc/default/grub

GRUB_CMDLINE_LINUX_DEFAULT="console=ttyS0"

and run the following command:
```bash
sudo update-grub
```

This will allow you to interact with instances over the serial port.

Next, run the following commands:

```bash
sudo apt-get install qemu-guest-agent cloud-init
sudo rm -rf /etc/systemd/system/qemu-guest-agent.service.d
sudo apt-get install openssh-server
sudo ufw enable
sudo ufw allow ssh
sudo systemctl daemon-reload
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
sudo systemctl restart ssh
```

This will enable remote interfacing and observability of the VMs.

Uncomment the following lines in /etc/ssh/sshd_config:

PasswordAuthentication yes
PubkeyAuthentication yes

This will allow you to ssh into instances.

Finally run the following command:
```bash
sudo rm /etc/cloud/cloud/.cfg.d/*
sudo echo "datasource_list: [ NoCloud, None ]" | sudo tee /etc/cloud/cloud.cfg.d/90_vm_init.cfg
sudo cloud-init clean
```

Next, shut down the VM.

5: Compress the ubuntu server base image:

Run the following commands:

```bash
sudo qemu-img convert -c -O qcow2 /IGS/compute/images/ubuntu_22.04.5_base.qcow2 /IGS/compute/images/compressed_ubuntu
sudo mv /IGS/compute/images/compressed_ubuntu /IGS/compute/images/ubuntu_22.04.5_base.qcow2
```

This will compress the image and make it more efficient.

You should now be able to use IGS' virtualization functionality.
