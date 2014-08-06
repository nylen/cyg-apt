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

    def testRmtree(self):
        # create tree
        root = os.path.join(self._getTmpDir(), "root~");
        subdir = os.path.join(root, "subdir~");
        rootfile = os.path.join(root, "file~");
        subdirfile = os.path.join(subdir, "file~");
        def build_tree():
            if not os.path.exists(subdir):
                os.makedirs(subdir);
            f = open(rootfile, 'w');
            e = open(subdirfile, 'w');
            f.close();
            e.close();

        def rm_tree():
            if os.path.exists(rootfile):
                os.unlink(rootfile);
            if os.path.exists(rootfile):
                os.unlink(subdirfile);
            if os.path.exists(rootfile):
                os.rmdir(subdir);
            if os.path.exists(rootfile):
                os.rmdir(root);

        build_tree();

        utils.rmtree(root);
        ok = False;
        if os.path.exists(subdirfile) or \
           os.path.exists(subdir) or \
           os.path.exists(rootfile) or \
           os.path.exists(root):
            ok = False;
        else:
            ok = True;

        self.assertTrue(ok);
        rm_tree();

        build_tree();
        utils.rmtree(rootfile);
        ok = False;
        if  os.path.exists(subdirfile) and \
            os.path.exists(subdir) and \
            not os.path.exists(rootfile) and \
            os.path.exists(root):
            ok = True;
        else:
            ok = False;
        self.assertTrue(ok);
        rm_tree();

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

    def _successOpenTarfile(self, pkgname):
        ball = os.path.join(
            self._dir_mirror,
            self._var_setupIni.__dict__[pkgname].install.curr.url,
        );

        filesOnBallDir = os.listdir(os.path.dirname(ball));

        tf = utils.open_tarfile(ball);
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
