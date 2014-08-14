#!/usr/bin/env python
# -*- coding: utf-8 -*-
######################## BEGIN LICENSE BLOCK ########################
# This file is part of the cygapt package.
#
# Copyright (C) 2002-2009 Jan Nieuwenhuizen  <janneke@gnu.org>
#               2002-2009 Chris Cormie       <cjcormie@gmail.com>
#                    2012 James Nylen        <jnylen@gmail.com>
#               2012-2014 Alexandre Quercia  <alquerci@email.com>
#
# For the full copyright and license information, please view the
# LICENSE file that was distributed with this source code.
######################### END LICENSE BLOCK #########################

from __future__ import absolute_import;

import unittest;
import sys;
import os;
import gzip;

from cygapt.cygapt import CygApt;
from cygapt.ob import CygAptOb;
from cygapt.test.utils import TestCase;
from cygapt.test.utils import SetupIniProvider;
from cygapt.path_mapper import PathMapper;
from cygapt.structure import ConfigStructure;

class TestCygApt(TestCase):
    def setUp(self):
        TestCase.setUp(self);

        self._var_verbose = False;
        self._var_cygwin_p = sys.platform.startswith("cygwin");

        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self._writeUserConfig();

        self._writeSetupIni();

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

        self.obj = self._createCygApt();

    def _createCygApt(self):
        """Creates a CygApt instance.

        @return: CygApt
        """
        cygapt = CygApt(
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
            self._var_verbose,
            self._var_arch,
            self._dir_confsetup,
        );

        # set attributes
        rc = ConfigStructure();
        rc.cache = self._dir_execache;
        rc.distname = 'curr';

        # BC layer for `setup_ini` configuration field
        rc.setup_ini = self._file_setup_ini;

        rc.ROOT = self._dir_mtroot;
        rc.always_update = False;
        rc.mirror = self._var_mirror;
        cygapt.setRC(rc);

        cygapt.setDownlaodDir(self._dir_downloads);
        cygapt.setInstalledDbFile(self._file_installed_db);
        self.assertEqual(self._dir_confsetup, cygapt.getSetupDir());

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

        cygapt.setPathMapper(pm);

        cygapt.setDists(self._var_setupIni.dists.__dict__);

        cygapt.CYG_POSTINSTALL_DIR = self._dir_postinstall;
        cygapt.CYG_PREREMOVE_DIR = self._dir_preremove;
        cygapt.CYG_POSTREMOVE_DIR = self._dir_postremove;

        cygapt.setDosBash("/usr/bin/bash");
        cygapt.setDosLn("/usr/bin/ln");

        cygapt.setPrefixRoot(self._dir_mtroot[:-1]);
        cygapt.setAbsRoot(self._dir_mtroot);
        cygapt.setInstalled({0:{}});

        cygapt.FORCE_BARRED.extend([
            self._var_setupIni.barredpkg.name,
        ]);

        return cygapt;

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

    def testUseDifferentMirrorThanTheLastUpdate(self):
        # backup
        backupMirror = self._var_setupIni;
        backupArch = self._var_arch;

        # make an update to another mirror
        self._var_arch = 'x86_64';
        self._var_setupIni = SetupIniProvider(self, self._var_arch);
        self._writeSetupIni();

        # restore
        self._var_arch = backupArch;
        self._var_setupIni = backupMirror;

        self.testGetSetupIni();

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
            self._var_setupIni.__dict__[self.obj.getPkgName()].install.curr.url
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

    def testDoInstallExternalWithLZMACompression(self):
        self.obj.setPkgName("pkgxz");

        self.testDownload();
        self.obj.setCygwinPlatform(False);
        self.obj._doInstall();
        self.assertInstall([self.obj.getPkgName()]);

    def testPostInstall(self):
        self.testDoInstall();
        self.obj._postInstall();
        self.assertPostInstall();

    def testPostInstallWhenScriptSuccess(self):
        foo = os.path.join(self._dir_postinstall, "foo.sh");
        bar = os.path.join(self._dir_postinstall, "bar.sh");
        self._writeScript(foo, 0);
        self._writeScript(bar, 0);

        self.obj.postinstall();

        self.assertPostInstall();
        self.assertTrue(os.path.isfile(foo+".done"));
        self.assertTrue(os.path.isfile(bar+".done"));

    def testPostInstallWhenScriptFails(self):
        foo = os.path.join(self._dir_postinstall, "foo.sh");
        self._writeScript(foo, 1);
        bar = os.path.join(self._dir_postinstall, "bar.sh");
        self._writeScript(bar, 2);

        self.obj.postinstall();

        self.assertTrue(os.path.isfile(foo));
        self.assertFalse(os.path.isfile(foo+".done"));
        self.assertTrue(os.path.isfile(bar));
        self.assertFalse(os.path.isfile(bar+".done"));

    def testPostRemoveWhenScriptSuccess(self):
        self._var_packagename = "foo";
        self._var_files = ["", "foo", "bar"];
        self.obj = self._createCygApt();

        prefoo = os.path.join(self._dir_preremove, "foo.sh");
        foo = os.path.join(self._dir_postremove, "foo.sh");
        bar = os.path.join(self._dir_postremove, "bar.sh");
        baz = os.path.join(self._dir_postremove, "baz.sh");
        self._writeScript(prefoo, 0);
        self._writeScript(foo, 0);
        self._writeScript(bar, 0);
        self._writeScript(baz, 0);

        self.obj.postremove();

        self.assertFalse(os.path.isfile(prefoo));
        self.assertTrue(os.path.isfile(prefoo+".done"));
        self.assertFalse(os.path.isfile(foo));
        self.assertTrue(os.path.isfile(foo+".done"));
        self.assertFalse(os.path.isfile(bar));
        self.assertTrue(os.path.isfile(bar+".done"));
        self.assertTrue(os.path.isfile(baz));
        self.assertFalse(os.path.isfile(baz+".done"));

    def testPostRemoveWhenScriptFails(self):
        self._var_packagename = "foo";
        self._var_files = ["", "foo", "bar"];
        self.obj = self._createCygApt();

        prefoo = os.path.join(self._dir_preremove, "foo.sh");
        foo = os.path.join(self._dir_postremove, "foo.sh");
        bar = os.path.join(self._dir_postremove, "bar.sh");
        self._writeScript(prefoo, 1);
        self._writeScript(foo, 1);
        self._writeScript(bar, 2);

        self.obj.postremove();

        self.assertTrue(os.path.isfile(prefoo));
        self.assertFalse(os.path.isfile(prefoo+".done"));
        self.assertTrue(os.path.isfile(foo));
        self.assertFalse(os.path.isfile(foo+".done"));
        self.assertTrue(os.path.isfile(bar));
        self.assertFalse(os.path.isfile(bar+".done"));

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

    def testInstallWithLZMACompression(self):
        self._var_packagename = self._var_setupIni.pkgxz.name;
        self._var_files = ["", self._var_packagename];
        self.obj = self._createCygApt();

        # INSTALL
        self.obj.install();

        self.assertInstall([self._var_packagename]);
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

        barredPackages = [
            "python",
            "python-argparse",
            "gnupg",
            "xz",
        ];
        for package in barredPackages:
            result = self.obj._isBarredPackage(package);
            message = "The package `{0}` is barred.".format(package);
            self.assertTrue(result, message);

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

            # Confirm the package is represented in installed.db
            message = "The package '{0}' is in '{1}'.".format(
                pkg.name,
                self._file_installed_db,
            );
            with open(self._file_installed_db, 'r') as f :
                contents = f.read();
            line = "{0} {1} 0".format(
                pkg.name,
                os.path.basename(pkg.install.curr.url),
            );
            self.assertTrue(line in contents.splitlines(), message);

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

            # Next confirm that the filelist file is gone
            # Not the original cyg-apt behaviour but setup.exe removes
            # this file, so that's taken as correct behaviour.
            filelist = os.path.join(self._dir_confsetup, pkg.name+".lst.gz");
            message = "The '{0}' file is gone.".format(filelist);
            self.assertFalse(os.path.isfile(filelist), message);

            # Confirm the package is not represented in installed.db
            message = "The package '{0}' is not in '{1}'.".format(
                pkg.name,
                self._file_installed_db,
            );
            with open(self._file_installed_db, 'r') as f :
                contents = f.read();
            for line in contents.splitlines() :
                self.assertNotEqual(line.split()[0], pkg.name, message);

    def _writeScript(self, path, exitCode=0):
        """Writes sh script to path.

        @param path:     str     A file to write the sript.
        @param exitCode: integer The exit code of the script.
        """
        directory = os.path.dirname(path);
        if not os.path.isdir(directory) :
            os.makedirs(directory);

        with open(path, 'w') as f :
            f.write("\n".join([
                "#!/bin/sh",
                "exit {0:d};",
                "",
            ]).format(exitCode));

if __name__ == "__main__":
    unittest.main();
