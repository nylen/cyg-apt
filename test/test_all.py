#!/usr/bin/python
"""
Created on 23 dec. 2012

"""

from __future__ import print_function
import unittest
import sys

from test_utils import TestUtils
from test_url_opener import TestUrlOpener
from test_argparser import TestArgParser
from test_ob import TestOb
from test_path_mapper import TestPathMapper
from test_setup import TestSetup
from test_cygapt import TestCygApt as TestCygAptClass


class TestCygApt(unittest.TestSuite):
    def __init__(self):
        loader = unittest.TestLoader()
        self.addTests(loader.loadTestsFromTestCase(TestUtils),
                      loader.loadTestsFromTestCase(TestUrlOpener),
                      loader.loadTestsFromTestCase(TestArgParser),
                      loader.loadTestsFromTestCase(TestOb),
                      loader.loadTestsFromTestCase(TestPathMapper),
                      loader.loadTestsFromTestCase(TestSetup),
                      loader.loadTestsFromTestCase(TestCygAptClass),)

def main():
    argv = sys.argv[:]
    argv.insert(1, '-v')
    unittest.main(argv=argv)

if __name__ == "__main__":
    main()
