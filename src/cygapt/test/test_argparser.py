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
    Unit test for cygapt.argparser
"""

from __future__ import absolute_import;

import unittest;
import sys;

from cygapt.test.case import TestCase;
from cygapt.argparser import CygAptArgParser;

class TestArgParser(TestCase):
    def setUp(self):
        TestCase.setUp(self);
        self.obj = CygAptArgParser("scriptname");

        self.__originArgv = sys.argv[:];
        sys.argv = sys.argv[:1];

    def tearDown(self):
        sys.argv = self.__originArgv;

        TestCase.tearDown(self);

    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygAptArgParser));
        self.assertEqual(self.obj.getAppName(), "scriptname");

    def testParse(self):
        sys.argv.append("install");
        sys.argv.append("pkg");

        ret = self.obj.parse();

        self.assertTrue(ret.verbose);
        self.assertEqual(ret.command, "install");
        self.assertEqual(ret.package, ['pkg']);

    def testParsePostInstall(self):
        self._assertParseCommand("postinstall");

    def testParsePostRemove(self):
        self._assertParseCommand("postremove", ["pkg"]);

    def testParseChecksum(self):
        self._assertParseCommand("checksum", ["pkg"]);

    def testArgumentType(self):
        sys.argv.append("--mirror=http://a.mirror.str");
        sys.argv.append("update");
        sys.argv.append("--dist=test");

        ret = self.obj.parse();

        self.assertEqual("test", ret.distname);
        self.assertEqual("http://a.mirror.str", ret.mirror);


    def testArgumentTypeDefault(self):
        ret = self.obj.parse();

        self.assertEqual("curr", ret.distname);
        self.assertEqual(True, ret.verbose);

    def testNoPostInstallOptionIsDeprecated(self):
        sys.argv.append("-y");

        ret = self._assertDeprecatedWarning(
            "The option -y, --nopostinstall is deprecated since version "
            "1.1 and will be removed in 2.0.",
            self.obj.parse
        );

        self.assertTrue(ret.nopostinstall);

    def testNoPostRemoveOptionIsDeprecated(self):
        sys.argv.append("-z");

        ret = self._assertDeprecatedWarning(
            "The option -z, --nopostremove is deprecated since version "
            "1.1 and will be removed in 2.0.",
            self.obj.parse
        );

        self.assertTrue(ret.nopostremove);

    def testMd5CommandIsDeprecated(self):
        sys.argv.append("md5");

        ret = self._assertDeprecatedWarning(
            "The command md5 is deprecated since version 1.2 and will be "
            "removed in 2.0, use checksum instead.",
            self.obj.parse
        );

        self.assertEqual(ret.command, "checksum");

    def _assertParseCommand(self, command, args=None):
        """
        @param command: str
        @param args:    list
        """
        if None is args :
            args = list();

        sys.argv.append(command);
        for arg in args :
            sys.argv.append(arg);

        ret = self.obj.parse();

        self.assertEqual(ret.command, command);
        self.assertEqual(ret.package, args);

if __name__ == "__main__":
    unittest.main();
