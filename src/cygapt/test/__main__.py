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

from cygapt.test.test_utils import TestUtils;
from cygapt.test.test_url_opener import TestUrlOpener;
from cygapt.test.test_argparser import TestArgParser;
from cygapt.test.test_ob import TestOb;
from cygapt.test.test_path_mapper import TestPathMapper;
from cygapt.test.test_setup import TestSetup;
from cygapt.test.test_cygapt import TestCygApt as TestCygAptClass;
from cygapt.test.test_process import TestProcess;

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
            loader.loadTestsFromTestCase(TestProcess),
        );

if __name__ == "__main__":
    unittest.main();
