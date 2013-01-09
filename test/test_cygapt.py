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
from cygapt.ob import CygAptOb
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

        self._var_packagename = self._var_setupIni.pkg.name
        self._var_files = ["", self._var_packagename];
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
        self.obj.config = self._dir_confsetup;

        # set attributes
        self.obj.sn = self._var_exename
        self.obj.pm.cygwin_p = False
        self.obj.pm.mountroot = self._dir_mtroot
        self.obj.pm.root = self._dir_mtroot[:-1]
        self.obj.pm.map = {self._dir_mtroot:self._dir_mtroot}

        expected = self._dir_mtroot;
        ret = self.obj.pm.map_path(self._dir_mtroot);
        self.assertEqual(ret, expected);
        expected = os.path.join(self._dir_mtroot, "diranme");
        ret = self.obj.pm.map_path(expected);
        self.assertEqual(ret, expected);

        self.obj.dists = self._var_setupIni.dists.__dict__
        self.obj.distname = "curr"
        self.obj.INSTALL = "install"
        self.obj.always_update = False;

        self.obj.postinstall_dir = self._dir_postinstall;
        self.obj.preremove_dir = self._dir_preremove;
        self.obj.postremove_dir = self._dir_postremove;

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

    #test also do_download ball getmd5 and md5
    def test_download(self):
        self.obj.download();
        filename = os.path.join(self._dir_downloads,
                                self._var_setupIni.pkg.install.curr.url);

        self.assertTrue(os.path.exists(filename));

    def test_get_requires(self):
        expected = self._var_setupIni.pkg.requires.split(" ");
        ret = self.obj.get_requires();

        self.assertEqual(ret, expected);

    def test_get_installed(self):
        pkg = ['pkgname', 'pkgname-1.1-1.tar.bz2', "0"];
        open(self._file_installed_db, "ab").write(string.join(pkg, " "));

        expected = {int(pkg[2]):{pkg[0]:pkg[1]}};

        self.obj.installed = 0;
        ret = self.obj.get_installed();

        self.assertEqual(ret, expected);

    def test_write_installed(self):
        pkg = ['pkgname', 'pkgname-1.1-1.tar.bz2', "0"];
        expected = self.obj.installed_db_magic;
        expected += string.join(pkg, " ");

        self.obj.installed = {int(pkg[2]):{pkg[0]:pkg[1]}};

        self.obj.write_installed();
        ret = open(self._file_installed_db).read();

        self.assertEqual(ret.replace("\n", ""), expected.replace("\n", ""));

    def test_get_field(self):
        expected = self._var_setupIni.pkg.category;
        ret = self.obj.get_field("category");
        self.assertEqual(ret, expected);

    def test_get_version(self):
        expected = self._var_setupIni.pkg.version.curr;
        expected = expected.replace(".", "").replace("-", "");
        expected = list(expected);
        i = 0;
        for val in expected:
            expected[i] = int(val);
            i = i + 1;
        del i;
        expected = tuple(expected);

        ret = self.obj.get_version();
        self.assertEqual(ret, expected);

    def test_search(self):
        self.obj.packagename = "libp";

        expected = self._var_setupIni.libpkg.name + \
                   " - " + \
                   self._var_setupIni.libpkg.shortDesc.replace('"','') + \
                   "\n";

        ob = CygAptOb(True);
        self.obj.search();
        ret = ob.get_clean();

        self.assertEqual(ret, expected);

    def test_get_missing(self):
        expected = self._var_setupIni.pkg.requires.split(" ");
        expected.append(self.obj.packagename);
        ret = self.obj.get_missing();

        self.assertEqual(ret, expected);

    def test_do_install(self):
        self.test_download();
        self.obj.do_install();
        self.assertInstall([self.obj.packagename]);

    def test_do_install_external(self):
        self.test_download();
        self.obj.cygwin_p = False;
        self.obj.do_install();
        self.assertInstall([self.obj.packagename]);


    def test_postinstall(self):
        self.test_do_install();
        self.obj.postinstall();
        self.assertPostInstall();

    def test_get_filelist(self):
        self.test_do_install();
        expected = self._var_setupIni.pkg.filelist;
        ret = self.obj.get_filelist();
        self.assertEqual(ret, expected);

    def test_do_uninstall(self):
        self.test_postinstall();
        self.obj.do_uninstall();
        self.assertRemove([self.obj.packagename])

    def test_install(self):
        # INSTALL
        self.obj.install();

        expected = self._var_setupIni.pkg.requires.split(" ");
        expected.append(self.obj.packagename);
        self.assertInstall(expected);
        self.assertPostInstall();

    def test_remove(self):
        self.test_install();
        # REMOVE
        self.obj.remove();
        self.assertRemove([self.obj.packagename]);

    def test_upgrade(self):
        self.test_install();
        pkgname = self._var_setupIni.pkg.name;
        version_file = os.path.join(self._dir_mtroot,
                                    "var",
                                    pkgname,
                                    "version");
        retcurr = open(version_file).read();

        self.obj.distname = "test";
        self.obj.upgrade();

        expected = self._var_setupIni.pkg.version.test;
        rettest = open(version_file).read();
        self.assertNotEqual(retcurr, rettest);

    def test_purge(self):
        self.test_postinstall();
        self.obj.purge();
        self.assertRemove([self.obj.packagename]);

        self.assertFalse(os.path.exists(self.obj.get_ball()));

    def test_source(self):
        os.chdir(self._dir_user);
        self.assertRaises(SystemExit, self.obj.source);
        self.assertTrue(os.path.isdir(self.obj.packagename));

    def test_find(self):
        self.test_do_install();

        self.obj.packagename = "version";

        pkgname = self._var_setupIni.pkg.name;
        expected = pkgname + ": " + os.path.join("/var",
                                    pkgname,
                                    "version") + "\n";

        ob = CygAptOb(True);
        self.obj.find();
        ret = ob.get_clean();
        self.assertEqual(ret, expected);


    def assertInstall(self, pkgname_list):
        pkg_ini_list = [];
        for pkg in pkgname_list:
            pkg_ini_list.append(self._var_setupIni.__dict__[pkg]);

        for pkg in pkg_ini_list:
            for filename in pkg.filelist:
                filename = self._dir_mtroot + filename;
                if os.path.dirname(filename) != self._dir_postinstall:
                    self.assertTrue(os.path.exists(filename),
                                    filename + " not exists");

    def assertPostInstall(self):
        for filename in os.listdir(self._dir_postinstall):
            if filename[-3:] == ".sh":
                self.assertTrue(False, filename + " runing fail");

    def assertRemove(self, pkgname_list):
        pkg_ini_list = [];
        for pkgname in pkgname_list:
            pkg_ini_list.append(self._var_setupIni.__dict__[pkgname]);

        for pkg in pkg_ini_list:
            for filename in pkg.filelist:
                if filename[-1] != "/":
                    filename = self._dir_mtroot + filename;
                    self.assertFalse(os.path.exists(filename),
                                     filename + " exists");

            for filename in os.listdir(self._dir_preremove):
                if filename == pkg.name + ".sh":
                    self.assertTrue(False, filename + " preremove runing fail");

            for filename in os.listdir(self._dir_postremove):
                if filename == pkg.name + ".sh":
                    self.assertTrue(False, filename + " postremove runing fail");

if __name__ == "__main__":
    unittest.main()
