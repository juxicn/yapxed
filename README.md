## yapxed
yet another pxe deployment

## Assume we have follow hierachy directory tree:

./tftpboot/
|-- gpxelinux.0
|-- node
|   |-- xx:xx:xx:xx:xx:xx
|   |   |-- initrd.img -> /mnt/centos7/isolinux/initrd.img
|   |   |-- ks.cfg
|   |   `-- vmlinuz -> /mnt/centos7/isolinux/vmlinuz
|   `-- zz:zz:zz:zz:zz:zz
|       |-- initrd.img -> /mnt/rhel7/isolinux/initrd.img
|       |-- ks.cfg
|       `-- vmlinuz -> /mnt/rhel7/isolinux/vmlinuz
|-- pxelinux.0
|-- pxelinux.cfg
|   |-- 01-xx-xx-xx-xx-xx-xx
|   `-- 01-zz-zz-zz-zz-zz-zz
`-- template
    |-- 01-xx-xx-xx-xx-xx-xx.template
    |-- dhcp.conf.template
    |-- dhcpd.conf.template
    |-- exports.template
    `-- ks.cfg.template

Note that xx-xx-...(xx:xx:...) and zz-zz-...(zz:zz:...) is MAC address of separated client node.

The mount directory would have tree:
mnt/
|-- centos7
|   |-- EFI
|   |-- EULA
|   |-- GPL
|   |-- images
|   |-- isolinux
|   |-- LiveOS
|   |-- Packages
|   |-- repodata
|   |-- RPM-GPG-KEY-CentOS-7
|   |-- RPM-GPG-KEY-CentOS-Testing-7
|   `-- TRANS.TBL
|-- cgslv5
|   |-- isolinux
|   |-- repodata
|   |-- RPM-GPG-KEY-CGSL-V5
|-- rhel7
|   |-- isolinux
|   |-- LiveOS
|   |-- media.repo
|   |-- Packages
|   |-- release-notes
|   |-- repodata
|   |-- RPM-GPG-KEY-redhat-beta
|   |-- RPM-GPG-KEY-redhat-release
`-- ubuntu14
    |-- boot
    |-- dists
    |-- doc
    |-- EFI
    |-- install
    |-- isolinux
    |-- md5sum.txt
    |-- pics
    |-- pool
    |-- preseed

## user application can follow steps list as:
 - Make sure TFTP root directory, PXE server IP address(also netmask, subnet).
 - Make sure the IP range to be allocated.
 - Discover, get client MAC address.
 - Get image(Linux OS distribution, xxx.iso), and:
    1. Mount xxx.iso
    2. Copy /mnt/xxx/isolinux/vmlinuz to ./tftpboot/node/xx:xx:xx:xx:xx:xx/vmlinuz
    3. Copy /mnt/xxx/isolinux/initrd.img to ./tftpboot/node/xx:xx:xx:xx:xx:xx/initrd.img
    4. Prepare boot strap file(pxelinux.0)
 - Create(Update) configuration file(pxe,dhcp,nfs,kickstart,tftp...).
 - Restart related service(systemctl restart xxx.service).
 - Reboot client node.


## To be fulfilled
 - multi-node deploy OS simutaneously.
 - .

That's all, have a good luck!

