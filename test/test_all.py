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
import unittest;

from test_utils import TestUtils;
from test_url_opener import TestUrlOpener;
from test_argparser import TestArgParser;
from test_ob import TestOb;
from test_path_mapper import TestPathMapper;
from test_setup import TestSetup;
from test_cygapt import TestCygApt as TestCygAptClass;

class TestCygApt(unittest.TestSuite):
    def __init__(self):
        loader = unittest.TestLoader();
        self.addTests(
            loader.loadTestsFromTestCase(TestUtils),
            loader.loadTestsFromTestCase(TestUrlOpener),
            loader.loadTestsFromTestCase(TestArgParser),
            loader.loadTestsFromTestCase(TestOb),
            loader.loadTestsFromTestCase(TestPathMapper),
            loader.loadTestsFromTestCase(TestSetup),
            loader.loadTestsFromTestCase(TestCygAptClass),
        );

if __name__ == "__main__":
    unittest.main();
