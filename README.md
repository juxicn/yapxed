# yapxed
yet another pxe deployment

Assume we have follow hierachy directory tree:


tftpboot/
|-- gpxelinux.0
|-- node
|   |-- xx:xx:xx:xx:xx:xx
|   |   |-- initrd.img -> /data/iso/mnt/centos7/isolinux/initrd.img
|   |   |-- ks.cfg
|   |   `-- vmlinuz -> /data/iso/mnt/centos7/isolinux/vmlinuz
|   `-- zz:zz:zz:zz:zz:zz
|       |-- initrd.img -> /data/iso/mnt/rhel7/isolinux/initrd.img
|       |-- ks.cfg
|       `-- vmlinuz -> /data/iso/mnt/rhel7/isolinux/vmlinuz
|-- pxelinux.0
|-- pxelinux.cfg
|   |-- 01-01-23-45-67-89-01
|   |-- 01-xx-xx-xx-xx-xx-xx
|   `-- 01-zz-zz-zz-zz-zz-zz
`-- template
    `-- 01-xx-xx-xx-xx-xx-xx.template


Note that xx-xx-...(xx:xx:...) and zz-zz-...(zz:zz:...) is MAC address of separated client node.


