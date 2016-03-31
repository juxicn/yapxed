import os
import unittest
from yapxed import pxe_config
from oslo_config import cfg


CONF = cfg.CONF

#class testConfig(unittest.TestCase):
#    def setUp(self):
#        super(testConfig, self).__init__(*args, **kwargs)
#

class testPXEConfig(unittest.TestCase):
    def setUp(self):
        #super(testPXEConfig, self).__init__()
        self.man = pxe_config.PXEConfig()

    def test_get_pxe_config_path(self):
        path = self.man.get_pxe_config_path("02:46:81:35:79:01")
        self.assertEqual(path, os.path.join(CONF.tftp_root_dir, "pxelinux.cfg", "01-02-46-81-35-79-01"))
