#!/usr/bin/python
'''
Created on 26 dec. 2012

'''
import unittest
import sys
import os
import gzip
import string

from cygapt.cygapt import CygApt
from cygapt.setup import CygAptSetup
import cygapt.utilstest

class TestCygApt(cygapt.utilstest.TestCase):
    def setUp(self):
        cygapt.utilstest.TestCase.setUp(self)

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

        f = open(self._file_setup_ini, "wb");
        f.truncate(0);
        f.write(self._var_setupIni.contents);
        f.close();

        f = open(self._file_installed_db, "wb");
        f.truncate(0);
        f.write(setup.installed_db_magic);
        f.close();

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

        self.obj.cache = self._dir_execache;
        self.obj.downloads = self._dir_downloads;
        self.obj.setup_ini = self._file_setup_ini;
        self.obj.ROOT = self._dir_mtroot;
        self.obj.mirror = self._var_mirror;
        self.obj.installed_db = self._file_installed_db;

        # set attributes
        self.obj.sn = self._var_exename
        self.obj.pm.cygwin_p = False
        self.obj.pm.mountroot = self._dir_mtroot
        self.obj.pm.root = self._dir_mtroot[:-1]
        self.obj.pm.map = {}

        self.obj.packagename = self._var_setupIni.pkg.name
        self.obj.dists = self._var_setupIni.dists.__dict__
        self.obj.distname = "curr"
        self.obj.INSTALL = "install"
        self.obj.always_update = False;

        self.obj.postinstall_dir = os.path.join(self._dir_sysconf, "postinstall");
        self.obj.preremove_dir = os.path.join(self._dir_sysconf, "preremove");
        self.obj.postremove_dir = os.path.join(self._dir_sysconf, "postremove");

        self.obj.dos_bin_dir = self._dir_bin;
        self.obj.dos_bash = "/usr/bin/bash";
        self.obj.dos_ln = "/usr/bin/ln";

        self.obj.PREFIX_ROOT = self._dir_mtroot[:-1];
        self.obj.ABSOLUTE_ROOT = self._dir_mtroot;
        self.obj.installed = {0:{}};

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
        
    def test_get_setup_ini(self):
        self.obj.dists = 0
        self.obj.get_setup_ini()
        self.assertEqual(self.obj.dists, self._var_setupIni.dists.__dict__)

    def test_get_url(self):
        ret = self.obj.get_url()
        filename, size, md5 = self._var_setupIni.pkg.install.curr.toString().split(
                                           " ",
                                           3)
        
        self.assertEqual(ret, (filename, md5))

if __name__ == "__main__":
    unittest.main()
