#!/usr/bin/env python

import os
import subprocess
from jinja2 import Environment, FileSystemLoader
from oslo_config import cfg
from oslo_utils import fileutils


pxe_opts = [
    cfg.StrOpt('tftp_root',
               default='/data/tftpboot',
               help=''),
    cfg.StrOpt('os_distribution',
               default='centos7',
               help=''),
    cfg.StrOpt('pxe_server_ip',
               default='128.0.0.1',
               help=''),
    cfg.StrOpt('protocol',
               default='nfs',
               help=''),
]

PXE_CFG_DIR_NAME = 'pxelinux.cfg'

CONF = cfg.CONF
CONF.register_opts(pxe_opts)

class Config(object):
    def __init__(self):
        pass

    def get_template_path(self):
        return os.path.join(CONF.tftp_root, 'template')

    def build_config(self, ctxt, template): 
        """Build the PXE boot configuration file.

        This method builds the PXE boot configuration file by rendering the
        template with the given parameters.

        :param pxe_options: A dict of values to set on the configuration file.
        :param template: The PXE configuration template.
        :param root_tag: Root tag used in the PXE config file.
        :param disk_ident_tag: Disk identifier tag used in the PXE config file.
        :returns: A formatted string with the file content.

        """
        # PATH = os.path.dirname(os.path.abspath(__file__))
        # env = Environment(loader=FileSystemLoader(os.path.join(PATH, 'templates')))
        tmpl_path, tmpl_file = os.path.split(template)
        env = Environment(loader=FileSystemLoader(tmpl_path))
        template = env.get_template(tmpl_file)
        return template.render(ctxt)


class PXEConfig(Config):
    def __init__(self):
        super(PXEConfig, self).__init__()

    def create_pxe_config(self, mac=':::::'):
        self.mac_addr = mac
        self.pxe_options = {
            'os_distribution': 'centos7',
            'path_to_vmlinuz': os.path.join(CONF.tftp_root, 'node', self.mac_addr, 'vmlinuz'),
            'path_to_initrd': os.path.join(CONF.tftp_root, 'node', self.mac_addr, 'initrd.img'),
            'path_to_kickstart_cfg': os.path.join(CONF.tftp_root, 'node', self.mac_addr, 'ks.cfg'),
            'protocol': 'nfs'
        }
        tname = self.get_pxe_template_path()
        cname = self.get_pxe_config_path(self.mac_addr)
        fileutils.delete_if_exists(cname)

        context = {
            'pxe_opts': self.pxe_options,
            'pxe_server_ip': CONF.pxe_server_ip
        }

        with open(cname, 'w') as f:
            config = self.build_config(context, tname)
            f.write(config)


    def render_template(self, template_filename, context):
        return env.get_template(template_filename).render(context)

    def get_root_dir():
        """Returns the directory where the config files and images will live."""
        return CONF.tftp_root

    def get_pxe_config_path(self, mac, delimiter=None):
        """Convert a MAC address into a PXE config file name.

        :param mac: A MAC address string in the format xx:xx:xx:xx:xx:xx.
        :param delimiter: The MAC address delimiter. Defaults to dash ('-').
        :returns: the path to the config file.

        """
        if delimiter is None:
            delimiter = '-'

        mac_file_name = mac.replace(':', delimiter).lower()
        mac_file_name = '01-' + mac_file_name

        return os.path.join(CONF.tftp_root, PXE_CFG_DIR_NAME, mac_file_name)
     
    def get_pxe_template_path(self):
        teml_dir = self.get_template_path()
        return os.path.join(teml_dir, '01-xx-xx-xx-xx-xx-xx.template')


class DHCPConfig(Config):
    def __init__(self):
        super(DHCPConfig, self).__init__()
        self.dhcp_options = {
            'boot_strap_file': 'pxelinux.0',
            'ctrl_plane_subnet': '128.0.0.0',
            'ctrl_plane_subnet_mask': '255.0.0.0',
            'dhcp_range_lower_limit': '128.0.0.1',
            'dhcp_range_upper_limit': '128.0.0.200'
        }

    def create_dhcp_config(self):
        tname = self.get_dhcp_template_path()
        cname = self.get_dhcp_config_path()
        fileutils.delete_if_exists(cname)
        
        context = {
            'dhcp_opts': self.dhcp_options,
            'pxe_server_ip': CONF.pxe_server_ip
        }

        with open(cname, 'w') as f:
            config = self.build_config(context, tname)
            f.write(config)

    def get_dhcp_config_path(self):
        out = subprocess.check_output(["rpm", "-ql", "dhcp"])
        path = ''
        for line in out.splitlines():
            #return line if "dhcp.conf" in line
            if "dhcp.conf" in line:
                return line
        return path

    def get_dhcp_template_path(self):
        teml_dir = self.get_template_path()
        return os.path.join(teml_dir, 'dhcp.conf.template')


class KSConfig(Config):
    def __init__(self):
        super(KSConfig, self).__init__()
    
    def create_ks_config(self):
        pass

    def get_ks_template_path(self):
        teml_dir = self.get_template_path()
        return os.path.join(teml_dir, 'ks.cfg.template')


if __name__ == "__main__":
    cfg = PXEConfig("11:22:33:44:55:66")
    cfg.create_pxe_config()
