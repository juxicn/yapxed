#!/usr/bin/env python

import os
import subprocess
from jinja2 import Environment, FileSystemLoader
from oslo_config import cfg
from oslo_utils import fileutils


PXE_CFG_DIR_NAME = 'pxelinux.cfg'


class Config(object):
    def __init__(self):
        pass

    #def get_template_dir(self):
    #    return os.path.join(CONF.tftp_root, 'template')

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

    def validate(self, config):
        """
        Validate and return validated config data. We would face these options
        in PXE deployment:

        'mac_addr': '11:22:33:44:55:66',
        'os_distribution': 'centos7',
        'pxe_server_ip': '128.0.0.1',
        'protocol': 'nfs',
        'tftp_root': '/data/tftp_boot/'

        'path_to_vmlinuz': '/path/to/vmlinuz',
        'path_to_initrd': '/path/to/initrd.img',
        'path_to_kickstart_cfg': '/path/to/ks.cfg'

        'boot_strap_file': 'pxelinux.0',
        'ctrl_plane_subnet': '128.0.0.0',
        'ctrl_plane_subnet_mask': '255.0.0.0',
        'dhcp_range_lower_limit': '128.0.0.2',
        'dhcp_range_upper_limit': '128.0.0.200'

        'installation_method': '',
        'initial_password': 'xxxxxx'
        """
        return config


class PXEConfig(Config):
    def __init__(self, pxe_config):
        """
        Here pxe_config would be a dictionary containing follow items:
        pxe_options = {
            'mac_addr': '11:22:33:44:55:66',
            'pxe_server_ip': '128.0.0.1',
            'os_distribution': 'centos7',
            'protocol': 'nfs',
            'path_to_vmlinuz': '/path/to/vmlinuz',
            'path_to_initrd': '/path/to/initrd.img',
            'path_to_kickstart_cfg': '/path/to/ks.cfg'
        }
        """
        super(PXEConfig, self).__init__()
        self.opts = self.validate(pxe_config)

    def create_pxe_config(self):
        tname = self.get_pxe_template_path()
        cname = self.get_pxe_config_path(self.mac_addr)
        fileutils.delete_if_exists(cname)

        context = {
            'pxe_opts': self.opts,
        }

        with open(cname, 'w') as f:
            config = self.build_config(context, tname)
            f.write(config)


    def render_template(self, template_filename, context):
        return env.get_template(template_filename).render(context)

    def get_root_dir(self):
        """Returns the directory where the config files and images will live."""
        #return CONF.tftp_root
        return self.opts["tftp_root"]

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
        teml_dir = os.path.join(self.opts["tftp_root"], 'template')
        #teml_dir = self.get_template_dir()
        return os.path.join(teml_dir, '01-xx-xx-xx-xx-xx-xx.template')


class DHCPConfig(Config):
    def __init__(self, dhcp_config):
        """
        dhcp_options = {
            'pxe_server_ip': '128.0.0.1',
            'boot_strap_file': 'pxelinux.0',
            'ctrl_plane_subnet': '128.0.0.0',
            'ctrl_plane_subnet_mask': '255.0.0.0',
            'dhcp_range_lower_limit': '128.0.0.2',
            'dhcp_range_upper_limit': '128.0.0.200'
        }
        """
        super(DHCPConfig, self).__init__()
        self.opts = self.validate(dhcp_config)

    def create_dhcp_config(self):
        tname = self.get_dhcp_template_path()
        cname = self.get_dhcp_config_path()
        # if in use?
        fileutils.delete_if_exists(cname)
        
        context = {
            'dhcp_opts': self.opts,
        }

        with open(cname, 'w') as f:
            config = self.build_config(context, tname)
            f.write(config)

    def get_dhcp_config_path(self):
        out = subprocess.check_output(["rpm", "-ql", "dhcp"])
        path = ''
        for line in out.splitlines():
            #return line if "dhcp.conf" in line
            if "dhcpd.conf" in line:
                return line
        return path

    def get_dhcp_template_path(self):
        teml_dir = os.path.join(self.opts["tftp_root"], 'template')
        return os.path.join(teml_dir, 'dhcpd.conf.template')

    def restart_service(self):
        out = subprocess.check_output(["systemctl", "restart", "dhcpd.service"])
        if out:
            print "dhcpd.service restart failed"

class KSConfig(Config):
    def __init__(self, ks_config):
        super(KSConfig, self).__init__()
        self.opts = self.validate(ks_config)
    
    def create_ks_config(self):
        tname = self.get_ks_template_path()
        cname = self.get_dhcp_config_path()
        fileutils.delete_if_exists(cname)
        context = {
            'ks_opts': self.opts,
        }

        with open(cname, 'w') as f:
            config = self.build_config(context, tname)
            f.write(config)

    def get_ks_config_path(self):
        return os.path.join(CONF.tftp_root, 'node', self.mac_addr, 'ks.cfg')

    def get_ks_template_path(self):
        teml_dir = os.path.join(self.opts["tftp_root"], 'template')
        return os.path.join(teml_dir, 'ks.cfg.template')

    def get_installation_method(self):
        proto = self.opts.get("protocol", "http")
        if proto == "nfs":
            method = 'nfs' + ' ' + '--server=' + self.opts.get("pxe_server_ip", "") + ' ' + '--dir=' + self.opts.get("path_to_mount", "")
            return method

        if proto != "http":
            return "unsupported"
        method = 'url' + ' ' + '--url=' + 'http://' + self.opts.get("pxe_server_ip", "") + self.opts.get("path_to_mount", "")
        return method
        

class NFSConfig(Config):
    def __init__(self, nfs_config):
        super(NFSConfig, self).__init__()
        self.opts = self.validate(nfs_config)

    def create_nfs_config(self):
        tname = self.get_nfs_template_path()
        cname = self.get_nfs_config_path()
        if os.path.isfile(cname):
            # append mount path to end of config file
            mount_path = self.opts.get("path_to_mount", "")
            subprocess.call(["echo", "'%s    *(ro,sync)'" % mount_path, ">>", "%s" % cname ])
        else:
            context = {
                'nfs_opts': self.opts,
            }

            with open(cname, 'w') as f:
                config = self.build_config(context, tname)
                f.write(config)

    def get_nfs_config_path(self):
        return os.path.join("/etc", "exports")

    def get_nfs_template_path(self):
        teml_dir = os.path.join(self.opts["tftp_root"], 'template')
        return os.path.join(teml_dir, 'exports.template')

    def restart_service(self):
        out = subprocess.check_output(["systemctl", "restart", "nfs.service"])
        if out:
            print "nfs.service restart failed"


class TFTPConfig(Config):
    def __init__(self):
        super(TFTPConfig, self).__init__()

    def update_tftp_config(self):
        config = "/etc/xinetd.d/tftp"
        tftp_root = self.opts.get("tftp_root", "")
        if not tftp_root:
            return "unchanged"
        subprocess.call(["sed", "'/server_args/c     server_args     = -s %s'"
                        % tftp_root])

    def restart_service(self):
        out = subprocess.check_output(["systemctl", "restart", "tftp-server.service"])
        if out:
            print "tftp-server.service restart failed"



