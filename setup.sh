
# install needed packages

## set yum repository

## install
yum install -y crudini
yum install -y dhcpd tftp-server syslinux nfs-utils

# setup according to yapxed.conf

## get conf from yapxed.conf
CRUD=$(which crudini)
local iso_file=$(CRUD yapxed.conf os iso_file)
local mount_path=$(CRUD yapxed.conf os mount_path)
local tftp_root_path=$(CRUD yapxed.conf tftp tftp_root_path)
local client_mac_addr=$(CRUD yapxed.conf client client_mac_addr)

## mount xxx.iso
mount -o loop ${iso_file} ${mount_path}
echo "${iso_file}   ${mount_path}   iso9660,ro,auto 0   0" >> /etc/fstab

## dhcpd configuration
local subnet=echo ${dhcp_server} | awk 'BEGIN{FS=OFS="."} {print $1,$2,$3,0}'
local subnet_mask=echo ${dhcp_server} | awk 'BEGIN{FS=OFS="."} {print $1,$2,$3,255}'
echo <<EOF >/etc/dhcp/dhcpd.conf
authoritative;
ddns-update-style interim;
allow booting;
allow bootp;
next-server ${dhcp_server};
filename "pxelinux.0";

default-lease-time 1800;
max-lease-time 7200;
ping-check true;
option domain-name-servers ${dhcp_server};
subnet ${subnet} netmask 255.255.255.0
{
    range ${dhcp_range_lower_limit}  ${dhcp_range_upper_limit};
    option routers ${dhcp_server};
    option broadcast-address ${subnet_mask};
}
EOF

## tftp configuration
### set tftp root path and enable tftp server
sed -i '/server_args/c 	server_args     = -s '"${tftp_root_path}"'' /etc/xinetd.d/tftp
sed -i '/disable/c 	disable                 = no' /etc/xinetd.d/tftp
mkdir -p ${tftp_root_path}/pxelinux.cfg
cp ${mount_path}/vmlinuz ${tftp_root_path}
cp ${mount_path}/initrd.img ${tftp_root_path}
boot_strap=$(rpm -ql syslinux | grep "pxelinux.0")
cp ${boot_strap} ${tftp_root_path}/
echo <<EOF >${tftp_root_path}/pxelinux.cfg/${client_mac_addr}
default rhel
prompt   10
timeout  20
label rhel
  kernel vmlinuz
  ipappend 2
  append ksdevice=bootif ks=nfs:${dhcp_server}:${tftp_root_path}/kickstart.cfg initrd=initrd.img  text splash=silent showopts
EOF

### default setting ??
echo <<EOF >${tftp_root_path}/pxelinux.cfg/default
default rhel
prompt   10
timeout  20
label rhel
  kernel vmlinuz
  ipappend 2
  append ksdevice=bootif ks=nfs:${dhcp_server}:${tftp_root_path}/kickstart.cfg initrd=initrd.img  text splash=silent showopts
EOF

### kickstart configuration
echo <<EEOOFF >${tftp_root_path}/kickstart.cfg
install
nfs --server=${dhcp_server} --dir=${mount_path}
lang en_US.UTF-8
keyboard us
text
rootpw  xxxxxx
firewall --disabled
authconfig --enableshadow --enablemd5
selinux --disabled
timezone --utc Asia/Shanghai
bootloader --location=mbr --driveorder=sda

%include /tmp/part-include
reboot

%packages  --ignoremissing
@Core
@development
nss-softokn-freebl.i686
%end

%pre
ROOTDRIVE=""
for dev in sda sdb sdc sdd hda hdb; do
    if [ -b /dev/$dev ]; then
        ROOTDRIVE=$dev
        break
    fi
done
cat << EOF > /tmp/part-include
zerombr
clearpart --all  --drives=$ROOTDRIVE  --initlabel
bootloader  --location=mbr  --driveorder=$ROOTDRIVE
part /boot --fstype ext4 --size=400
part swap --fstype swap --size=8000
part / --fstype ext4  --grow  --size=1
EOF
%end

%post  --nochroot
%end

%post
sleep 3
%end
EEOOFF

## nfs/http/ftp configuration
echo <<EOF >/etc/exports
${mount_path}             *(ro,sync)
${tftp_root_path}         *(ro)
EOF

## start and enable service
systemctl start dhcpd xinetd nfs
systemctl enable dhcpd xinetd nfs


