#!/usr/bin/python
######################## BEGIN LICENSE BLOCK ########################
# This file is part of the cygapt package.
#
# Copyright (C) 2002-2009 Jan Nieuwenhuizen  <janneke@gnu.org>
#               2002-2009 Chris Cormie       <cjcormie@gmail.com>
#                    2012 James Nylen        <jnylen@gmail.com>
#               2012-2013 Alexandre Quercia  <alquerci@email.com>
#
# For the full copyright and license information, please view the
# LICENSE file that was distributed with this source code.
######################### END LICENSE BLOCK #########################

from __future__ import print_function;
from __future__ import absolute_import;

import unittest;
import sys;
import os;
import gzip;

from cygapt.cygapt import CygApt;
from cygapt.setup import CygAptSetup;
from cygapt.ob import CygAptOb;
from cygapt.test.utils import TestCase;
from cygapt.path_mapper import PathMapper;
from cygapt.structure import ConfigStructure;

class TestCygApt(TestCase):
    def setUp(self):
        TestCase.setUp(self);

        self._var_verbose = False;
        self._var_cygwin_p = sys.platform.startswith("cygwin");

        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        setup = CygAptSetup(self._var_cygwin_p, self._var_verbose);
        setup.setTmpDir(self._dir_tmp);
        setup.setAppName(self._var_exename);
        setup.setSetupDir(self._dir_confsetup);
        setup.getRC().ROOT = self._dir_mtroot;

        setup._gpgImport(setup.GPG_CYG_PUBLIC_RING_URI);
        setup.setup();

        f = open(self._file_setup_ini, 'w');
        f.write(self._var_setupIni.contents);
        f.close();

        f = open(self._file_installed_db, 'w');
        f.write(CygApt.INSTALLED_DB_MAGIC);
        f.close();

        self._var_packagename = self._var_setupIni.pkg.name;
        self._var_files = ["", self._var_packagename];
        self._var_download_p = False;
        self._var_downloads = None;
        self._var_distname = None;
        self._var_nodeps_p = False;
        self._var_regex_search = False;
        self._var_nobarred = False;
        self._var_nopostinstall = False;
        self._var_nopostremove = False;
        self._var_dists = 0;
        self._var_installed = 0;

        self.obj = CygApt(
            self._var_packagename,
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
            self._var_verbose
        );

        # set attributes
        rc = ConfigStructure();
        rc.cache = self._dir_execache;
        rc.distname = 'curr';
        rc.setup_ini = self._file_setup_ini;
        rc.ROOT = self._dir_mtroot;
        rc.always_update = False;
        rc.mirror = self._var_mirror;
        self.obj.setRC(rc);

        self.obj.setDownlaodDir(self._dir_downloads);
        self.obj.setInstalledDbFile(self._file_installed_db);
        self.obj.setSetupDir(self._dir_confsetup);

        pm = PathMapper("", False);
        pm.setRoot(self._dir_mtroot[:-1]);
        pm.setMountRoot(self._dir_mtroot);
        pm.setMap({self._dir_mtroot:self._dir_mtroot});

        expected = self._dir_mtroot;
        ret = pm.mapPath(self._dir_mtroot);
        self.assertEqual(ret, expected);
        expected = os.path.join(self._dir_mtroot, "diranme");
        ret = pm.mapPath(expected);
        self.assertEqual(ret, expected);

        self.obj.setPathMapper(pm);

        self.obj.setDists(self._var_setupIni.dists.__dict__);

        self.obj.CYG_POSTINSTALL_DIR = self._dir_postinstall;
        self.obj.CYG_PREREMOVE_DIR = self._dir_preremove;
        self.obj.CYG_POSTREMOVE_DIR = self._dir_postremove;

        self.obj.setDosBash("/usr/bin/bash");
        self.obj.setDosLn("/usr/bin/ln");

        self.obj.setPrefixRoot(self._dir_mtroot[:-1]);
        self.obj.setAbsRoot(self._dir_mtroot);
        self.obj.setInstalled({0:{}});

        self.obj.FORCE_BARRED = [self._var_setupIni.barredpkg.name];

    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygApt));

    def testWriteFileList(self):
        lst = ["file1", "file2/", "file3/dfd"];
        lstret = [b"file1\n", b"file2/\n", b"file3/dfd\n"];
        gzfile = os.path.join(self._dir_confsetup, "pkg.lst.gz");
        self.obj.setSetupDir(self._dir_confsetup);
        self.obj.setPkgName("pkg");
        self.obj._writeFileList(lst);
        gzf = gzip.open(gzfile);
        expected = gzf.readlines();
        gzf.close();
        self.assertEqual(expected, lstret);

    def testRunScript(self):
        script = "/pkg.sh";
        script_done = script + ".done";
        map_script = self.obj.getPathMapper().mapPath(script);
        map_script_done = self.obj.getPathMapper().mapPath(script_done);
        f = open(map_script, 'w');
        f.write("#!/bin/bash\nexit 0;");
        f.close();

        self.obj._runScript(script, False);
        self.assertTrue(os.path.exists(map_script_done));

    def testVersionToString(self):
        versiont = [1,12,3,1];
        out = "1.12.3-1";
        ret = self.obj._versionToString(versiont);
        self.assertEqual(ret, out);

    def testStringToVersion(self):
        string = "1.12.3-1";
        out = [1,12,3,1];
        ret = self.obj._stringToVersion(string);
        self.assertEqual(list(ret), out);

    def testSplitBall(self):
        value = "pkgball-1.12.3-1.tar.bz2";
        output = ["pkgball", (1,12,3,1)];
        ret = self.obj._splitBall(value);
        self.assertEqual(list(ret), output);
        
    def testJoinBall(self):
        value = ["pkgball", [1,12,3,1]];
        output = "pkgball-1.12.3-1";
        ret = self.obj._joinBall(value);
        self.assertEqual(ret, output);
        
    def testGetSetupIni(self):
        self.obj.setDists(0);
        self.obj._getSetupIni();
        self.assertEqual(
            self.obj.getDists(),
            self._var_setupIni.dists.__dict__
        );

    def testGetUrl(self):
        ret = self.obj._getUrl();
        install = self._var_setupIni.pkg.install.curr.toString();
        filename, size, md5 = install.split(" ", 3);

        self.assertEqual(ret, (filename, md5));

    #test also doDownload ball getmd5 and md5
    def testDownload(self):
        self.obj.download();
        filename = os.path.join(
            self._dir_downloads,
            self._var_setupIni.pkg.install.curr.url
        );
        self.assertTrue(os.path.exists(filename));

    def testGetRequires(self):
        expected = self._var_setupIni.pkg.requires.split(" ");
        ret = self.obj.getRequires();
        self.assertEqual(ret, expected);

    def testGetInstalled(self):
        pkg = ["pkgname", "pkgname-1.1-1.tar.bz2", "0"];
        f = open(self._file_installed_db, 'a');
        f.write(" ".join(pkg));
        f.close();
        expected = {int(pkg[2]):{pkg[0]:pkg[1]}};
        self.obj.setInstalled(0);

        ret = self.obj.getInstalled();

        self.assertEqual(ret, expected);

    def testWriteInstalled(self):
        pkg = ["pkgname", "pkgname-1.1-1.tar.bz2", "0"];
        expected = CygApt.INSTALLED_DB_MAGIC;
        expected += " ".join(pkg);

        self.obj.setInstalled({int(pkg[2]):{pkg[0]:pkg[1]}});

        self.obj._writeInstalled();
        f = open(self._file_installed_db);
        ret = f.read();
        f.close();

        self.assertEqual(ret.replace("\n", ""), expected.replace("\n", ""));

    def testGetField(self):
        expected = self._var_setupIni.pkg.category;
        ret = self.obj.getField('category');
        self.assertEqual(ret, expected);

    def testGetVersion(self):
        expected = self._var_setupIni.pkg.version.curr;
        expected = expected.replace(".", "").replace("-", "");
        expected = list(expected);
        i = 0;
        for val in expected:
            expected[i] = int(val);
            i = i + 1;
        del i;
        expected = tuple(expected);

        ret = self.obj.getVersion();
        self.assertEqual(ret, expected);

    def testSearch(self):
        self.obj.setPkgName("libp");

        expected = "{0} - {1}\n".format(
            self._var_setupIni.libpkg.name,
            self._var_setupIni.libpkg.shortDesc.replace('"','')
        );

        ob = CygAptOb(True);
        self.obj.search();
        ret = ob.getClean();

        self.assertEqual(ret, expected);

    def testGetMissing(self):
        expected = self._var_setupIni.pkg.requires.split(" ");
        expected.append(self.obj.getPkgName());
        ret = self.obj.getMissing();

        self.assertEqual(ret, expected);

    def testDoInstall(self):
        self.testDownload();
        self.obj._doInstall();
        self.assertInstall([self.obj.getPkgName()]);

    def testDoInstallExternal(self):
        self.testDownload();
        self.obj.setCygwinPlatform(False);
        self.obj._doInstall();
        self.assertInstall([self.obj.getPkgName()]);

    def testPostInstall(self):
        self.testDoInstall();
        self.obj._postInstall();
        self.assertPostInstall();

    def testGetFileList(self):
        self.testDoInstall();
        expected = self._var_setupIni.pkg.filelist;
        ret = self.obj.getFileList();
        self.assertEqual(ret.sort(), expected.sort());

    def testDoUninstall(self):
        self.testPostInstall();
        self.obj._doUninstall();
        self.assertRemove([self.obj.getPkgName()]);

    def testInstall(self):
        # INSTALL
        self.obj.install();

        expected = self._var_setupIni.pkg.requires.split(" ");
        expected.append(self.obj.getPkgName());
        self.assertInstall(expected);
        self.assertPostInstall();

    def testRemove(self):
        self.testInstall();
        # REMOVE
        self.obj.remove();
        self.assertRemove([self.obj.getPkgName()]);

    def testUpgrade(self):
        self.testInstall();
        pkgname = self._var_setupIni.pkg.name;
        version_file = os.path.join(
            self._dir_mtroot,
            "var",
            pkgname,
            "version"
        );
        f = open(version_file);
        retcurr = f.read();
        f.close();

        self.obj.getRC().distname = "test";
        self.obj.upgrade();

        f = open(version_file);
        rettest = f.read();
        f.close();
        self.assertNotEqual(retcurr, rettest);

    def testPurge(self):
        self.testPostInstall();
        self.obj.purge();
        self.assertRemove([self.obj.getPkgName()]);

        self.assertFalse(os.path.exists(self.obj.getBall()));

    def testSource(self):
        os.chdir(self._dir_user);
        self.obj.source();
        self.assertTrue(os.path.isdir(self.obj.getPkgName()));

    def testFind(self):
        self.testDoInstall();

        self.obj.setPkgName("version");

        pkgname = self._var_setupIni.pkg.name;
        expected = "{0}: {1}\n".format(
            pkgname,
            os.path.join("/var", pkgname, "version")
        );
        ob = CygAptOb(True);
        self.obj.find();
        ret = ob.getClean();
        self.assertEqual(ret, expected);

    def testIsBarredPackage(self):
        self.assertTrue(
            self.obj._isBarredPackage(self._var_setupIni.libbarredpkg.name)
        );
        self.assertTrue(
            self.obj._isBarredPackage(self._var_setupIni.barredpkg.name)
        );
        self.assertFalse(
            self.obj._isBarredPackage(self._var_setupIni.libpkg.name)
        );
        self.assertFalse(
            self.obj._isBarredPackage(self._var_setupIni.pkg.name)
        );
        self.obj._isBarredPackage("not_exists_pkg");

    def assertInstall(self, pkgname_list):
        pkg_ini_list = [];
        for pkg in pkgname_list:
            pkg_ini_list.append(self._var_setupIni.__dict__[pkg]);

        for pkg in pkg_ini_list:
            gz_file = os.path.join(
                self._dir_confsetup,
                "{0}.lst.gz".format(pkg.name)
            );
            f = gzip.open(gz_file);
            lines = f.readlines();
            f.close();
            self.assertEqual(pkg.filelist.sort(), lines.sort());
            for filename in pkg.filelist:
                filename = self._dir_mtroot + filename;
                if os.path.dirname(filename) != self._dir_postinstall:
                    self.assertTrue(
                        os.path.exists(filename),
                        "{0} not exists".format(filename)
                    );

    def assertPostInstall(self):
        for filename in os.listdir(self._dir_postinstall):
            if filename[-3:] == ".sh":
                self.fail("{0} running fail".format(filename));

    def assertRemove(self, pkgname_list):
        pkg_ini_list = [];
        for pkgname in pkgname_list:
            pkg_ini_list.append(self._var_setupIni.__dict__[pkgname]);

        for pkg in pkg_ini_list:
            for filename in pkg.filelist:
                if filename[-1] != "/":
                    filename = self._dir_mtroot + filename;
                    self.assertFalse(
                        os.path.exists(filename),
                        "{0} exists".format(filename)
                    );

            for filename in os.listdir(self._dir_preremove):
                if filename == pkg.name + ".sh":
                    self.fail("{0} preremove runing fail".format(filename));

            for filename in os.listdir(self._dir_postremove):
                if filename == pkg.name + ".sh":
                    self.fail("{0} postremove runing fail".format(filename));

if __name__ == "__main__":
    unittest.main();
