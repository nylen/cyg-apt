#!/usr/bin/python
"""
    Unit test for cygapt.argparser
"""

import unittest
import sys

from cygapt.argparser import CygAptArgParser


class TestArgParser(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.obj = CygAptArgParser("usage", "scriptname")

    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygAptArgParser))
        self.assertEqual(self.obj.usage, "usage")
        self.assertEqual(self.obj.scriptname, "scriptname")

    def test_parse(self):
        argv = sys.argv[:]
        sys.argv = sys.argv[:1]
        sys.argv.append("install")
        sys.argv.append("pkg")
        
        ret = self.obj.parse()
        
        self.assertTrue(ret.verbose)
        self.assertEqual(ret.command, "install")
        self.assertEqual(ret.package, ['pkg'])
        
        sys.argv = argv


if __name__ == "__main__":
    unittest.main()