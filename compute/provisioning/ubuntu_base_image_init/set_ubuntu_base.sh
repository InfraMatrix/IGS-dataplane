
sudo modprobe nbd nbds_max=16 max_part=16

for i in {0..15}; do
    if [ ! -e "/dev/nbd${i}" ]; then
    continue
    fi

    if [ "$(cat /sys/block/nbd${i}/size)" -eq 0 ] 2>/dev/null; then
        nbd_dev="/dev/nbd${i}"
        break
    fi
done

sudo qemu-nbd -c ${nbd_dev} /IGS/compute/images/ubuntu_22.04.5_base.qcow2

sleep 2

vg_name=$(sudo pvdisplay -C --noheadings -o vg_name ${nbd_dev}p3 | tr -d ' ')
lv_name=$(sudo pvdisplay -C --noheadings -o lv_name ${nbd_dev}p3 | tr -d ' ')

sudo vgchange -ay $(sudo vgs --noheadings -o vg_name ${nbd_dev}p3 | tr -d ' ')

mapper_path="/dev/mapper/${vg_name//-/--}-${lv_name//-/--}"

sudo mkdir -p /mnt/IGS
sudo mount $mapper_path /mnt/IGS

sudo mount -o bind /dev /mnt/IGS/dev
sudo mount -o bind /proc /mnt/IGS/proc
sudo mount -o bind /sys /mnt/IGS/sys

sudo mkdir -p /mnt/IGS/boot/grub

current_params=$(grep GRUB_CMDLINE_LINUX_DEFAULT /mnt/IGS/etc/default/grub | cut -d'"' -f2)
sudo sed -i "s/GRUB_CMDLINE_LINUX_DEFAULT=\".*\"/GRUB_CMDLINE_LINUX_DEFAULT=\"console=ttyS0\"/" /mnt/IGS/etc/default/grub

sudo chroot /mnt/IGS update-grub

sudo umount /mnt/IGS* 2>/dev/null || true


sudo vgchange -an $vg_name
sudo qemu-nbd -d ${nbd_dev}
sudo modprobe -r nbd
