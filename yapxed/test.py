#!/usr/bin/env python

import os
from yapxed import pxe_config


pxe_opts = [
    cfg.StrOpt('tftp_root',
               default='/data/tftpboot',
               help='TFTP root directory.'),
    cfg.StrOpt('os_distribution',
               default='centos7',
               help='OS distribution to be installed, such as RHEL7, CentOS7.'),
    cfg.StrOpt('pxe_server_ip',
               default='128.0.0.1',
               help='Server IP address.'),
    cfg.StrOpt('protocol',
               default='nfs',
               help='Protocol pxe client download vmlinuz and initrd.img from
                    server through, also use as to download installation
                    packages, it could be NFS share, TFTP, FTP or HTTP.'),
]

CONF = cfg.CONF
CONF.register_opts(pxe_opts)

def create_config():
    base_options = {
        'mac_addr': '11:22:33:44:55:66',
        'os_distribution': 'centos7',
        'pxe_server_ip': '128.0.0.1',
        'protocol': 'nfs',
        'tftp_root': '/data/tftp_boot/'
    }

    # pxe configuration test
    mac_addr = base_options.get("mac_addr","")
    if not mac_addr:
        raise
    pxe_options = {
        'path_to_vmlinuz': os.path.join(CONF.tftp_root, 'node', mac_addr, 'vmlinuz'),
        'path_to_initrd': os.path.join(CONF.tftp_root, 'node', mac_addr, 'initrd.img'),
        'path_to_kickstart_cfg': os.path.join(CONF.tftp_root, 'node', mac_addr, 'ks.cfg')
    }
    combined_pxe_options = pxe_options.copy()
    combined_pxe_options.update(base_options)
    pxe_cfg = pxe_config.PXEConfig(combined_pxe_options)
    pxe_cfg.create_pxe_config()

    # dhcp configuration test
    dhcp_options = {
        'boot_strap_file': 'pxelinux.0',
        'ctrl_plane_subnet': '128.0.0.0',
        'ctrl_plane_subnet_mask': '255.0.0.0',
        'dhcp_range_lower_limit': '128.0.0.2',
        'dhcp_range_upper_limit': '128.0.0.200'
    }
    combined_dhcp_options = dhcp_options.copy()
    combined_dhcp_options.update(base_options)
    dhcp_cfg = pxe_config.DHCPConfig(combined_dhcp_options)
    dhcp_cfg.create_dhcp_config()
    dhcp_cfg.restart_service()

    # kickstart configuration test
    ks_options = {
        # installation method can either be:
        # "nfs --server=x.x.x.x  --dir=/path/to/mnt"  or
        # "url --url http://path/to/mnt
        # more method(cdrom, harddrive, nfs, liveimg or url), refer:
        # https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux/7/html/Installation_Guide/sect-kickstart-syntax.html
        'installation_method': '',
        'initial_password': 'xxxxxx'
    }
    combined_ks_options = ks_options.copy()
    combined_ks_options.update(base_options)
    ks_cfg = pxe_config.KSConfig(combined_ks_options)
    method = ks_cfg.get_installation_method()
    ks_cfg.opts.update(installation_method = method)
    ks_cfg.create_ks_config()

if __name__ == "__main__":
    create_config()

