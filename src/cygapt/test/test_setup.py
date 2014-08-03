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
"""
    Unit test for cygapt.setup
"""

from __future__ import absolute_import;

import unittest;
import sys;
import os;
import subprocess;

from cygapt.setup import CygAptSetup;
from cygapt.test.utils import TestCase;
from cygapt.setup import PlatformException;
from cygapt.setup import EnvironementException;
from cygapt.exception import PathExistsException;
from cygapt.exception import UnexpectedValueException;


class TestSetup(TestCase):
    def setUp(self):
        TestCase.setUp(self);
        self._var_verbose = False;
        self._var_cygwin_p = sys.platform.startswith("cygwin");
        self.obj = CygAptSetup(self._var_cygwin_p, self._var_verbose);
        self.obj.setTmpDir(self._dir_tmp);
        self.obj.setAppName(self._var_exename);
        self.obj.setSetupDir(self._dir_confsetup);
        self.obj.getRC().ROOT = self._dir_mtroot;

    def test__init__(self):
        self.assertTrue(isinstance(self.obj, CygAptSetup));
        self.assertEqual(self.obj.getCygwinPlatform(), self._var_cygwin_p);
        self.assertEqual(self.obj.getVerbose(), self._var_verbose);

    def testGetSetupRc(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        badlocation = os.path.join(self._var_tmpdir, "not_exist_file");
        last_cache, last_mirror = self.obj.getSetupRc(badlocation);
        self.assertEqual(last_cache, None);
        self.assertEqual(last_mirror, None);

        last_cache, last_mirror = self.obj.getSetupRc(self._dir_confsetup);
        self.assertEqual(last_cache, self._dir_execache);
        self.assertEqual(last_mirror, self._var_mirror_http);

    def testGetPre17Last(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        location = self._var_tmpdir;
        last_mirror = "http://cygwin.uib.no/";
        last_cache = os.path.join(self._var_tmpdir, "last_cache");
        os.mkdir(last_cache);
        lm_file = os.path.join(self._var_tmpdir, "last-mirror");
        lc_file = os.path.join(self._var_tmpdir, "last-cache");
        lm_stream = open(lm_file, 'w');
        lm_stream.write(last_mirror);
        lm_stream.close();
        lc_stream = open(lc_file, 'w');
        lc_stream.write(last_cache);
        lc_stream.close();

        rlast_cache, rlast_mirror = self.obj._getPre17Last(location);
        self.assertEqual(last_cache, rlast_cache);
        self.assertEqual(last_mirror, rlast_mirror);

    def testUpdate(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);
        self.obj.setup();

        self.obj.update(self._file_user_config, True);

    def testUpdateWithoutMirror(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);
        self._var_mirror_http = "";
        self._writeSetupRc();

        try:
            self.obj.setup();
            self.obj.update(self._file_user_config, True);
        except Exception as e:
            self.assertTrue(isinstance(e, UnexpectedValueException));
            self.assertEqual(e.getMessage(), (
                "A mirror must be specified on the configuration file \"{0}\" "
                "or with the command line option \"--mirror\"."
                "".format(self._file_user_config)
            ));
        else:
            self.fail(
                ".update() raises an UnexpectedValueException if the mirror "
                "was not defined."
            );

    def testSetup(self):
        if not self._var_cygwin_p:
            self.assertRaises(PlatformException, self.obj.setup);
            return;

        # env HOME not exists
        os.environ.pop('HOME');
        self.assertRaises(EnvironementException, self.obj.setup);
        os.environ['HOME'] = self._dir_user;

        # config file already isset
        f = open(self._file_user_config, 'w');
        f.close();
        self.assertRaises(PathExistsException, self.obj.setup);
        self.assertTrue(os.path.exists(self._file_user_config));

        os.remove(self._file_user_config);

        # next
        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);
        self.obj.setup();

    def testWriteInstalled(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        real_installed_db = self._file_installed_db.replace(self._var_tmpdir, "");
        self.obj._writeInstalled(self._file_installed_db);
        self.assertTrue(os.path.exists(self._file_installed_db));
        f = open(self._file_installed_db);
        ret = f.readlines().sort();
        f.close();
        f = open(real_installed_db);
        expected = f.readlines().sort();
        f.close();
        self.assertEqual(ret, expected);

    def testGpgImport(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);

        cmd = " ".join([
            "gpg",
            "--no-secmem-warning",
            "--list-public-keys",
            "--fingerprint",
        ]);
        p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE);
        if p.wait():
            raise RuntimeError(p.stderr.read());
        lines = p.stdout.readlines();
        findout = False;
        for line in lines:
            if isinstance(line, bytes):
                marker = self.obj.GPG_GOOD_FINGER.encode();
            else:
                marker = self.obj.GPG_GOOD_FINGER;
            if marker in line:
                findout = True;
                break;

        self.assertTrue(findout);

    def testUsage(self):
        self.obj.usage();

if __name__ == "__main__":
    unittest.main()
