#sudo systemctl stop ceph-mon@dev-server

#sudo rm -f /tmp/monmap /tmp/ceph.mon.keyring
#sudo rm -rf /var/lib/ceph/mon/ceph-dev-server/*

#sudo ceph-authtool --create-keyring /tmp/ceph.mon.keyring --gen-key -n mon. --cap mon 'allow *'

#sudo ceph-authtool --create-keyring /etc/ceph/ceph.client.admin.keyring --gen-key -n client.admin --cap mon 'allow *' --cap osd 'allow *' --cap mds 'allow *' --cap mgr 'allow *'

#sudo ceph-authtool /tmp/ceph.mon.keyring --import-keyring /etc/ceph/ceph.client.admin.keyring

#sudo chown ceph:ceph /tmp/ceph.mon.keyring
#sudo chown ceph:ceph /etc/ceph/ceph.client.admin.keyring
#sudo chmod 600 /tmp/ceph.mon.keyring
#sudo chmod 600 /etc/ceph/ceph.client.admin.keyring

#sudo monmaptool --create --add dev-server 10.0.0.154:6789 --fsid 428142f4-c8c8-11ef-8524-d9143dedd4e6 /tmp/monmap

#sudo -u ceph ceph-mon --mkfs -i dev-server --monmap /tmp/monmap --keyring /tmp/ceph.mon.keyring

#sudo systemctl start ceph-mon@dev-server

#sudo ceph -s --keyring /etc/ceph/ceph.client.admin.keyring



#rbd pool init rbd_pool

#rbd create --size 10G --pool rbd_pool --image myimage

#rbd showmapped

#rbd map vm_pool/vm-drive1

#rbd lock list vm_pool/vm-drive1

#rbd lock remove vm_pool/vm-drive1 "auto ID_NUMBER" client.NUMBER