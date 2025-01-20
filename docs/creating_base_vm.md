# Creating base ubuntu image

Steps that need to be run in a base ubuntu VM to create it:

1: Go through the process of setting up the VM. Have the plugged into the vm's cdrom.

Avoid installing using the LVM storage options.

```bash
qemu-system-x86_64 \
-machine pc-q35-6.2,accel=kvm \
-cpu host \
-m 6G \
-cdrom /IGS/compute/isos/ubuntu/ubuntu-22.04.5-live-server-amd64.iso \
-drive file=/IGS/compute/images/ubuntu_22.04.5_base.qcow2,if=virtio,format=qcow2 \
-nographic \
-serial mon:stdio \
-netdev user,id=net0,hostfwd=tcp::2222-:22 \
-device virtio-net-pci,netdev=net0 \
-boot menu=on \
-nographic \
-net nic -net user \
  -kernel iso_mount/casper/vmlinuz \
  -initrd iso_mount/casper/initrd \
  -append "console=ttyS0 only-ubiquity"
```

2: After installing ubuntu server onto the image, boot the image so we can install universal packages and proceed to step 3:

```bash
qemu-system-x86_64 \
-machine pc-q35-6.2,accel=kvm \
-cpu host \
-m 6G \
-drive file=/IGS/compute/images/ubuntu_22.04.5_base.qcow2,if=virtio,format=qcow2 \
-nographic \
-serial mon:stdio \
-netdev user,id=net0,hostfwd=tcp::2222-:22 \
-device virtio-net-pci,netdev=net0 \
-boot menu=on \
-nographic \
-net nic -net user \
-device virtio-serial-pci \
-chardev socket,id=ch0,path=/tmp/base_qga.sock,server=on,wait=off \
-device virtserialport,chardev=ch0,name=org.qemu.guest_agent.0
```



3: We are in the base ubuntu image. Run the following commands to set everything up
for the VM instances that you plan to spin up.

First, add the following to /etc/ssh/sshd_config:

PasswordAuthentication no
PubkeyAuthentication yes

This will allow us to ssh into the derivative VMs.

Next, run the following commands:

```bash
sudo apt-get install qemu-guest-additions
sudo rm -rf /etc/systemd/system/qemu-guest-agent.service.d
sudo ufw enable
sudo ufw allow ssh
sudo systemctl daemon-reload
sudo systemctl enable qemu-guest-agent
sudo systemctl start qemu-guest-agent
sudo systemctl restart ssh
```

This will set up the qemu agent which will enable observability and set up ufw and ssh.

