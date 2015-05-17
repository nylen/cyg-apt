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
import urllib;
import re;

from cygapt.setup import CygAptSetup;
from cygapt.test.case import dataProvider;
from cygapt.test.utils import TestCase;
from cygapt.test.utils import SetupIniProvider;
from cygapt.setup import PlatformException;
from cygapt.setup import EnvironementException;
from cygapt.exception import PathExistsException;
from cygapt.exception import UnexpectedValueException;
from cygapt.setup import SignatureException;
from cygapt.ob import CygAptOb;
from cygapt.process import Process;


class TestSetup(TestCase):
    def setUp(self):
        TestCase.setUp(self);
        self._var_verbose = False;
        self._var_cygwin_p = (
            sys.platform.startswith("cygwin")
            or sys.platform.startswith("linux")
        );
        self.obj = CygAptSetup(
            self._var_cygwin_p,
            self._var_verbose,
            self._var_arch,
        );
        self.obj.setTmpDir(self._dir_tmp);
        self.obj.setAppName(self._var_exename);
        self.obj.setSetupDir(self._dir_confsetup);
        self.obj.getRC().ROOT = self._dir_mtroot;

    def test__init__(self):
        self.assertTrue(isinstance(self.obj, CygAptSetup));
        self.assertEqual(self.obj.getCygwinPlatform(), self._var_cygwin_p);
        self.assertEqual(self.obj.getVerbose(), self._var_verbose);

    def testGetSetupRc(self):
        badlocation = os.path.join(self._var_tmpdir, "not_exist_file");
        last_cache, last_mirror = self.obj.getSetupRc(badlocation);
        self.assertEqual(last_cache, None);
        self.assertEqual(last_mirror, None);

        last_cache, last_mirror = self.obj.getSetupRc(self._dir_confsetup);
        self.assertEqual(last_cache, self._dir_execache);
        self.assertEqual(last_mirror, self._var_mirror);

    def testGetPre17Last(self):
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

    def testUpdateWithGoodMirrorSignature(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin or linux");

        self._writeUserConfig(self._file_user_config);

        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);
        self.obj.update(self._file_user_config, True, self._var_mirror_http);

    def testUpdateWithBadMirrorSignature(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin or linux");

        self._writeUserConfig(self._file_user_config);
        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);

        message = '^{0}$'.format(re.escape(
            "{0}{1}{2}/setup.bz2 not signed by Cygwin's public key."
            " Use -X to ignore signatures."
            "".format(
            self._var_mirror,
            '' if self._var_mirror.endswith('/') else '/',
            self._var_setupIni.getArchitecture(),
        )));

        with self.assertRaisesRegexp(SignatureException, message):
            self.obj.update(self._file_user_config, True);

    @dataProvider('getUpdateWithoutVerifySignatureWithAnyEndSlashCountData')
    def testUpdateWithoutVerifySignatureWithAnyEndSlashCount(self, mirrorEndSlashCount):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin or linux");

        self._var_mirror = self._var_mirror.rstrip('/')+'/'*mirrorEndSlashCount;
        self._writeUserConfig(self._file_user_config);

        self.obj.update(self._file_user_config, False);

        self._assertUpdate();

    def getUpdateWithoutVerifySignatureWithAnyEndSlashCountData(self):
        return [
            [0],
            [1],
        ];

    @dataProvider('getUpdateWithoutVerifySignatureAndWithValidArchitectureData')
    def testUpdateWithoutVerifySignatureAndWithValidArchitecture(self, arch):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin or linux");

        self._var_arch = arch;
        self._var_setupIni = SetupIniProvider(self, self._var_arch);
        self.obj.setArchitecture(self._var_arch);

        self._writeUserConfig(self._file_user_config);

        self.obj.update(self._file_user_config, False);

        self._assertUpdate();

    def getUpdateWithoutVerifySignatureAndWithValidArchitectureData(self):
        return [
            ["x86"],
            ["x86_64"],
        ];

    def testUpdateWithoutMirror(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin or linux");

        self._var_mirror = "";
        self._writeUserConfig(self._file_user_config);

        message = '^{0}$'.format(re.escape(
            'A mirror must be specified on the configuration file "{0}"'
            ' or with the command line option "--mirror".'
            ' See cygwin.com/mirrors.html for the list of mirrors.'
            ''.format(self._file_user_config),
        ));

        with self.assertRaisesRegexp(UnexpectedValueException, message):
            self.obj.update(self._file_user_config, False);

    def testUpdateWithSetupIniFieldWarnDeprecationWarning(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self._writeUserConfig(self._file_user_config, keepBC=True);

        self._assertDeprecatedWarning(
            "The configuration field `setup_ini` is deprecated since version"
            " 1.1 and will be removed in 2.0.",
            self.obj.update,
            self._file_user_config,
            False,
        );

        self._assertUpdate(keepBC=True);

    def testUpdateWithoutSetupIniFieldNotWarnDeprecationWarning(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self._writeUserConfig(self._file_user_config);

        self._assertNotDeprecatedWarning(
            "The configuration field `setup_ini` is deprecated since version"
            " 1.1 and will be removed in 2.0.",
            self.obj.update,
            self._file_user_config,
            False,
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
        # mirror end with one slash
        self._var_mirror = self._var_mirror_http.rstrip('/')+'/';
        self._writeSetupRc(self._file_setup_rc);
        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);
        self.obj.setup();

        # create a default user configuration file
        self.assertTrue(os.path.isfile(self._file_user_config));
        with open(self._file_user_config, 'r') as f :
            self.assertEqual("\n".join([
                "# The distribution, current previous or test [curr, prev, test].",
                '# Usually you want the "curr" version of a package.',
                'distname="curr"',
                "",
                "# Your package cache as a POSIX path: example /e/home/cygwin_package_cache",
                'cache="{self[_dir_execache]}"',
                "",
                "# Packages which cyg-apt can't change under Cygwin since it depends on them.",
                "# Run cyg-apt under DOS with -f (force) option to change these packages.",
                "# Treat Cygwin core packages with CAUTION.",
                'barred=""',
                "",
                "# URL of your Cygwin mirror: example http://mirror.internode.on.net/pub/cygwin/",
                'mirror="{self[_var_mirror]}"',
                "",
                "# Always update setup.ini before any command that uses it. cyg-apt will be",
                "# faster and use less bandwidth if False but you will have to run the update",
                "# command manually.",
                'always_update="False"',
                "",
                "# setup.ini lists available packages and is downloaded from the top level",
                "# of the downloaded mirror. Standard location is /etc/setup/setup.ini,",
                "# seutp-2.ini for Cygwin 1.7 Beta",
                "# Deprecated since version 1.1 and will be removed in 2.0.",
                '# setup_ini="{self[_file_setup_ini]}"',
                "",
                "# The root of your Cygwin installation as a windows path",
                'ROOT="{self[_dir_mtroot]}"',
                "",
                "",
            ]).format(self=vars(self)), f.read());

        # create setup.ini on `/etc/setup/`
        self.assertFalse(os.path.isfile(self._file_setup_ini));

        # create setup.ini on `<cachedir>/<mirror>/<arch>/`
        setupIniPath = os.path.join(
            self._getDownloadDir(),
            self._var_arch,
            "setup.ini",
        );
        self.assertTrue(os.path.isfile(setupIniPath));

        # mirror end without slash
        self._var_mirror = self._var_mirror_http.rstrip('/');
        self._writeSetupRc(self._file_setup_rc);
        # fail if setupIniPath will be rewrite
        os.chmod(setupIniPath, 0o000);
        self.obj.setup(True);

    def testSetupNotWarnDeprecationWarning(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin");

        self._var_mirror = self._var_mirror_http;
        self._writeSetupRc(self._file_setup_rc);
        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);

        self._assertNotDeprecatedWarning(
            "The configuration field `setup_ini` is deprecated since version"
            " 1.1 and will be removed in 2.0.",
            self.obj.setup,
        );

    def testWriteInstalled(self):
        if not sys.platform.startswith("cygwin"):
            self.skipTest("requires cygwin");

        real_installed_db = self._file_installed_db.replace(self._var_tmpdir, "");
        self.obj._writeInstalled(self._file_installed_db);
        self.assertTrue(os.path.exists(self._file_installed_db));
        f = open(self._file_installed_db);
        ret = f.readlines();
        ret.sort();
        f.close();
        f = open(real_installed_db);
        expected = f.readlines();
        expected.sort();
        f.close();
        self.assertEqual(ret, expected);

    def testGpgImport(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin or linux");

        self.obj._gpgImport(self.obj.GPG_CYG_PUBLIC_RING_URI);

        cmd = " ".join([
            "gpg",
            "--no-secmem-warning",
            "--list-public-keys",
            "--fingerprint",
        ]);
        p = Process(cmd);
        p.mustRun();
        lines = p.getOutput().splitlines(True);
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

    def testUsageNotContainMd5Command(self):
        try:
            self.testUsageContainCommand("md5");
        except self.failureException :
            pass;
        else:
            self.fail("Failed asserting that usage does not contain md5 command.");

    @dataProvider('getUsageContainCommandData')
    def testUsageContainCommand(self, command):
        ob = CygAptOb(True);
        try:
            self.obj.usage();
        finally:
            ret = ob.getClean();

        self.assertTrue("    {0}".format(command) in ret);

    def getUsageContainCommandData(self):
        return [
            ['postinstall'],
            ['postremove'],
            ['checksum'],
        ];

    def _assertUpdate(self, keepBC=False):
        """Asserts that the local setup.ini has been updated.

        @raise AssertionError: When the assertion is not verify.
        """
        onCache = os.path.join(
            self._getDownloadDir(),
            self._var_setupIni.getArchitecture(),
            "setup.ini"
        );

        self.assertTrue(os.path.isfile(onCache), onCache+" not exists.");

        expected = self._var_setupIni.contents;

        with open(onCache, 'r') as f :
            actual = f.read();
        self.assertEqual(expected, actual);

        if not keepBC :
            return;

        # BC layer for `setup_ini` configuration field
        onEtc = self._file_setup_ini;
        self.assertTrue(os.path.isfile(onEtc), onEtc+" not exists.");
        with open(onEtc, 'r') as f :
            actual = f.read();
        self.assertEqual(expected, actual);

if __name__ == "__main__":
    unittest.main()
