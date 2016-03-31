import os
import unittest
from yapxed import pxe_config
from oslo_config import cfg
from oslo_utils import fileutils


CONF = cfg.CONF

#class testConfig(unittest.TestCase):
#    def setUp(self):
#        super(testConfig, self).__init__(*args, **kwargs)
#

class testPXEConfig(unittest.TestCase):
    def setUp(self):
        #super(testPXEConfig, self).__init__()
        CONF([], project='yapxed')
        self.man = pxe_config.PXEConfig()

    def test_get_pxe_config_path(self):
        path = self.man.get_pxe_config_path("02:46:81:35:79:01")
        self.assertEqual(path, os.path.join(CONF.tftp_root, "pxelinux.cfg", "01-02-46-81-35-79-01"))

    def test_get_pxe_template_path(self):
        pass

    def test_create_pxe_config(self):
        fileutils.delete_if_exists(os.path.join(CONF.tftp_root, "pxelinux.cfg", "01-02-46-81-35-79-01"))
        self.man.create_pxe_config("02:46:81:35:79:01")
        self.assertTrue(os.path.isfile(os.path.join(CONF.tftp_root, "pxelinux.cfg", "01-02-46-81-35-79-01")))

def initialize():
    return testPXEConfig
