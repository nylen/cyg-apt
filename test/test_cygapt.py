#!/usr/bin/python
'''
Created on 26 dec. 2012

'''
import unittest
import sys
import os
import gzip

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
        self.obj.sn = self._var_exename
        self.obj.pm.cygwin_p = False
        self.obj.pm.mountroot = self._dir_mtroot
        self.obj.pm.root = self._dir_mtroot[:-1]
        self.obj.pm.map = {}

    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygApt))

    def test_write_filelist(self):
        lst = ["file1", "file2/", "file3/dfd"]
        lstret = ["file1\n", "file2/\n", "file3/dfd\n"]
        gzfile = os.path.join(self._dir_confsetup, "pkg.lst.gz")
        self.obj.config = self._dir_confsetup
        self.obj.packagename = "pkg"
        self.obj.setup_ini = self._file_setup_ini
        self.obj.write_filelist(lst)
        self.assertEqual(gzip.GzipFile(gzfile, "r").readlines(), lstret)

    def test_run_script(self):
        script = "/pkg.sh"
        script_done = script + ".done"
        map_script = self.obj.pm.map_path(script)
        map_script_done = self.obj.pm.map_path(script_done)
        open(map_script, "wb").write("#!/bin/bash\nexit 0;")

        self.obj.run_script(script, False)
        self.assertTrue(os.path.exists(map_script_done))
        
    def test_version_to_string(self):
        versiont = [1,12,3,1]
        out = "1.12.3-1"
        ret = self.obj.version_to_string(versiont)
        self.assertEqual(ret, out)
        
    def test_string_to_version(self):
        string = "1.12.3-1"
        out = [1,12,3,1]
        ret = self.obj.string_to_version(string)
        self.assertEqual(list(ret), out)
        
    def test_split_ball(self):
        input = "pkgball-1.12.3-1.tar.bz2"
        output = ["pkgball", (1,12,3,1)]
        ret = self.obj.split_ball(input)
        self.assertEqual(list(ret), output)
        
    def test_join_ball(self):
        input = ["pkgball", [1,12,3,1]]
        output = "pkgball-1.12.3-1"
        ret = self.obj.join_ball(input)
        self.assertEqual(ret, output)

if __name__ == "__main__":
    unittest.main()