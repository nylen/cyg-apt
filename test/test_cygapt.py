#!/usr/bin/python
'''
Created on 26 dec. 2012

'''
import unittest
import sys

from cygapt.cygapt import CygApt
from cygapt.setup import CygAptSetup


from testcase import TestCase

class TestCygApt(TestCase):
    def setUp(self):
        
        TestCase.setUp(self)
        
        self._var_verbose = False
        self._var_cygwin_p = sys.platform == "cygwin"
        
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin")
        
        setup = CygAptSetup(self._var_cygwin_p, self._var_verbose)
        setup.tmpdir = self._dir_tmp
        setup.sn = self._var_exename
        setup.config = self._dir_confsetup
        setup.ROOT = self._dir_mtroot
        setup.ABSOLUTE_ROOT = self._dir_mtroot
        
        setup.gpg_import(setup.cygwin_pubring_uri)
        setup.setup()
        
        self._var_packagename = ""
        self._var_files = []
        self._var_download_p = False
        self._var_downloads = None
        self._var_distname = None
        self._var_nodeps_p = False
        self._var_regex_search = False
        self._var_nobarred = False
        self._var_nopostinstall = False
        self._var_nopostremove = False
        self._var_dists = 0
        self._var_installed = 0
        
        self.obj = CygApt(self._var_packagename,
                          self._var_files,
                          self._file_user_config,
                          self._var_cygwin_p,
                          self._var_download_p,
                          self._var_mirror,
                          self._var_downloads,
                          self._var_distname,
                          self._var_nodeps_p,
                          self._var_regex_search,
                          self._var_nobarred,
                          self._var_nopostinstall,
                          self._var_nopostremove,
                          self._var_dists,
                          self._var_installed,
                          self._var_exename,
                          self._var_verbose)
        
        # FIXME: set attributes
    
    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygApt))
    
if __name__ == "__main__":
    unittest.main()