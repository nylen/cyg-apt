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
"""
    Unit test for cygapt.argparser
"""

from __future__ import print_function;
import unittest;
import sys;

from cygapt.argparser import CygAptArgParser;


class TestArgParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self);
        self.obj = CygAptArgParser("usage", "scriptname");

    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygAptArgParser));
        self.assertEqual(self.obj.usage, "usage");
        self.assertEqual(self.obj.scriptName, "scriptname");

    def testParse(self):
        argv = sys.argv[:];
        sys.argv = sys.argv[:1];
        sys.argv.append("install");
        sys.argv.append("pkg");
        
        ret = self.obj.parse();
        
        self.assertTrue(ret.verbose);
        self.assertEqual(ret.command, "install");
        self.assertEqual(ret.package, ['pkg']);
        
        sys.argv = argv;


if __name__ == "__main__":
    unittest.main();
