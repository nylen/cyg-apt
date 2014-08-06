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
import stat;

import cygapt.utils as utils;
from cygapt.exception import ApplicationException;
from cygapt.test.utils import TestCase;

class TestUtils(TestCase):
    def _getTmpDir(self):
        return self._dir_tmp;

    def _getTmpFileName(self):
        filename = "{0}{1}test~".format(self._getTmpDir(), os.path.sep);
        return filename;

    def testCygpath(self):
        if not sys.platform.startswith("cygwin"):
            self.skipTest("requires cygwin");

        good_paths = ["/", ".", "./", "./.", "/bin"];

        for path in good_paths:
            ret = utils.cygpath(path);
            self.assertEquals(ret, path);

    def testParseRc(self):
        f = open(self._getTmpFileName(), 'w');
        f.write("always_update = \"True\"");
        f.close();

        ret = utils.parse_rc(self._getTmpFileName());
        self.assertTrue(ret);

        f = open(self._getTmpFileName(), 'w');
        f.write("always_update = \"False\"");
        f.close();

        ret = utils.parse_rc(self._getTmpFileName());
        self.assertFalse(ret);

        f = open(self._getTmpFileName(), 'w');
        f.write("always_update = bad_value");
        f.close();

        self.assertRaises(
            NameError,
            utils.parse_rc,
            self._getTmpFileName()
        );

    def testPrsort(self):
        in_lst = ["B", "A", "a", "1", "b", "/", "", "2"];

        out_lst = ["b", "a", "B", "A", "2", "1", "/", ""];

        utils.prsort(in_lst);
        self.assertEqual(in_lst, out_lst);

    def testRename(self):
        dest = self._getTmpFileName();
        src = "{0}2".format(self._getTmpFileName());
        stream = open(src, 'w+');
        stream.writelines("1");
        stream.seek(0);
        src_content = stream.readlines();
        stream.close();

        stream = open(dest, 'w');
        stream.writelines("2");
        stream.close();

        utils.rename(src, dest);

        stream = open(dest, 'r');
        res_dest_content = stream.readlines();
        stream.close();

        self.assertFalse(os.path.exists(src));
        self.assertEqual(src_content, res_dest_content);

        if os.path.exists(src):
            os.unlink(src);

    def testRmtreeCleansFilesAndDirectories(self):
        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        open(basePath+"file", 'w').close();

        utils.rmtree(basePath+"dir");
        utils.rmtree(basePath+"file");

        self.assertFalse(os.path.isdir(basePath+"dir"));
        self.assertFalse(os.path.isfile(basePath+"file"));

    def testRmtreeCleansFilesAndDirectoriesIteratively(self):
        basePath = os.path.join(self._getTmpDir(), "directory")+os.path.sep;

        os.mkdir(basePath);
        os.mkdir(basePath+"dir");
        open(basePath+"file", 'w').close();

        utils.rmtree(basePath);

        self.assertFalse(os.path.isdir(basePath));

    def testRmtreeCleansWithoutPermission(self):
        basePath = os.path.join(self._getTmpDir(), "directory")+os.path.sep;

        os.mkdir(basePath);
        os.mkdir(basePath+"dir");
        open(basePath+"file", 'w').close();

        # Removes permissions
        os.chmod(basePath+"dir", 0o000);
        os.chmod(basePath+"file", 0o000);

        utils.rmtree(basePath+"dir");
        utils.rmtree(basePath+"file");

        self.assertFalse(os.path.isdir(basePath+"dir"));
        self.assertFalse(os.path.isfile(basePath+"file"));

    def testRmtreeCleansWithoutPermissionIteratively(self):
        basePath = os.path.join(self._getTmpDir(), "directory")+os.path.sep;

        os.mkdir(basePath);
        os.mkdir(basePath+"dir");
        open(basePath+"file", 'w').close();

        # Removes permissions
        os.chmod(basePath+"dir", 0o000);
        os.chmod(basePath+"file", 0o000);

        utils.rmtree(basePath);

        self.assertFalse(os.path.isdir(basePath));

    def testRmtreeIgnoresNonExistingFiles(self):
        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");

        utils.rmtree(basePath+"dir");
        utils.rmtree(basePath+"file");

        self.assertFalse(os.path.isdir(basePath+"dir"));

    def testRmtreeCleansValidLinksToFile(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        open(basePath+"file", 'w').close();
        os.symlink(basePath+"file", basePath+"link");

        utils.rmtree(basePath+"link");

        self.assertTrue(os.path.isfile(basePath+"file"));
        self.assertFalse(os.path.islink(basePath+"link"));

    def testRmtreeCleansValidLinksToFileIteratively(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        open(basePath+"file", 'w').close();
        os.symlink(basePath+"file", basePath+"dir"+os.path.sep+"link");

        utils.rmtree(basePath+"dir");

        self.assertTrue(os.path.isfile(basePath+"file"));
        self.assertFalse(os.path.isdir(basePath+"dir"));

    def testRmtreeKeepsTargetLinkPermissionsToFile(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        open(basePath+"file", 'w').close();
        os.symlink(basePath+"file", basePath+"link");

        # Removes permissions
        os.chmod(basePath+"file", 0o000);
        fileMode = os.stat(basePath+"file")[stat.ST_MODE];

        utils.rmtree(basePath+"link");

        self.assertTrue(os.path.isfile(basePath+"file"));
        self.assertEqual(fileMode, os.stat(basePath+"file")[stat.ST_MODE]);

    def testRmtreeKeepsTargetLinkPermissionsToFileIteratively(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        open(basePath+"file", 'w').close();
        os.symlink(basePath+"file", basePath+"dir"+os.path.sep+"link");

        # Removes permissions
        os.chmod(basePath+"file", 0o000);
        fileMode = os.stat(basePath+"file")[stat.ST_MODE];

        utils.rmtree(basePath+"dir");

        self.assertTrue(os.path.isfile(basePath+"file"));
        self.assertEqual(fileMode, os.stat(basePath+"file")[stat.ST_MODE]);

    def testRmtreeCleansValidLinksToDirectory(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        os.symlink(basePath+"dir", basePath+"link");

        utils.rmtree(basePath+"link");

        self.assertTrue(os.path.isdir(basePath+"dir"));
        self.assertFalse(os.path.islink(basePath+"link"));

    def testRmtreeCleansValidLinksToDirectoryIteratively(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        os.mkdir(basePath+"dir2");
        os.symlink(basePath+"dir2", basePath+"dir"+os.path.sep+"link");

        utils.rmtree(basePath+"dir");

        self.assertTrue(os.path.isdir(basePath+"dir2"));
        self.assertFalse(os.path.isdir(basePath+"dir"));

    def testRmtreeKeepsTargetLinkPermissionsToDirectory(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        os.symlink(basePath+"dir", basePath+"link");

        # Removes permissions
        os.chmod(basePath+"dir", 0o000);
        fileMode = os.stat(basePath+"dir")[stat.ST_MODE];

        utils.rmtree(basePath+"link");

        self.assertTrue(os.path.isdir(basePath+"dir"));
        self.assertEqual(fileMode, os.stat(basePath+"dir")[stat.ST_MODE]);

    def testRmtreeKeepsTargetLinkPermissionsToDirectoryIteratively(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        os.mkdir(basePath+"dir");
        os.mkdir(basePath+"dir2");
        os.symlink(basePath+"dir2", basePath+"dir"+os.path.sep+"link");

        # Removes permissions
        os.chmod(basePath+"dir2", 0o000);
        fileMode = os.stat(basePath+"dir2")[stat.ST_MODE];

        utils.rmtree(basePath+"dir");

        self.assertTrue(os.path.isdir(basePath+"dir2"));
        self.assertEqual(fileMode, os.stat(basePath+"dir2")[stat.ST_MODE]);

    def testRmtreeCleansInvalidLinks(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = self._getTmpDir()+os.path.sep;

        # create symlink to unexisting file
        os.symlink(basePath+"file", basePath+"link");

        utils.rmtree(basePath+"link");

        self.assertFalse(os.path.islink(basePath+"link"));

    def testRmtreeCleansInvalidLinksIteratively(self):
        if not hasattr(os, "symlink") :
            self.skipTest("symlink is not supported");

        basePath = os.path.join(self._getTmpDir(), "directory")+os.path.sep;

        os.mkdir(basePath);
        os.mkdir(basePath+"dir");

        # create symlink to unexisting file
        os.symlink(basePath+"file", basePath+"link");

        utils.rmtree(basePath);

        self.assertFalse(os.path.isdir(basePath));

    def testUriGet(self):
        directory = self._getTmpDir();
        uri = "http://cygwin.uib.no/x86/setup.bz2.sig";
        verbose = False;
        utils.uri_get(directory, uri, verbose);
        self.assertTrue(
            os.path.exists(os.path.join(directory, "setup.bz2.sig")),
            "http request"
        );

        self.assertRaises(
            ApplicationException,
            utils.uri_get,
            "",
            "",
            verbose
        );

        uri = "ftp://cygwin.uib.no/pub/cygwin/x86/setup.ini.sig";
        try:
            utils.uri_get(directory, uri, verbose);
        except utils.RequestException:
            self.skipTest("Your network doesn't allow FTP requests.");
        self.assertTrue(
            os.path.exists(os.path.join(directory, "setup.ini.sig")),
            "ftp request"
        );

        uri = "rsync://cygwin.uib.no/cygwin/x86/setup-legacy.bz2.sig";
        self.assertRaises(
            ApplicationException,
            utils.uri_get,
            directory,
            uri,
            verbose
        );

    def testOpenTarfileFromLZMABall(self):
        self._successOpenTarfile("pkgxz");

    def testOpenTarfileFromBzip2Ball(self):
        self._successOpenTarfile("pkg");

    def testOpenTarfileFromLZMABallWithoutPATH(self):
        if not sys.platform.startswith("cygwin") and not sys.platform.startswith("linux") :
            self.skipTest("requires cygwin or linux");

        old_path = os.environ['PATH'];

        try:
            os.environ['PATH'] = "";
            self._successOpenTarfile("pkgxz", "/usr/bin/xz");
        finally:
            os.environ['PATH'] = old_path;

    def _successOpenTarfile(self, pkgname, xzPath="xz"):
        ball = os.path.join(
            self._dir_mirror,
            self._var_setupIni.__dict__[pkgname].install.curr.url,
        );

        filesOnBallDir = os.listdir(os.path.dirname(ball));

        tf = utils.open_tarfile(ball, xzPath);
        members = tf.getmembers();
        tf.close();

        self.assertEqual(filesOnBallDir, os.listdir(os.path.dirname(ball)));

        filelist = [];
        for member in members :
            path = member.name;
            if member.isdir() :
                path = path.rstrip("/")+"/";
            filelist.append(path);

        self.assertEqual(sorted(filelist), sorted(self._var_setupIni.__dict__[pkgname].filelist));

if __name__ == "__main__":
    unittest.main();
