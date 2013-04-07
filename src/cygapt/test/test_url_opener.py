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

from __future__ import absolute_import;

import unittest;
import sys;
from tempfile import TemporaryFile;
from cStringIO import StringIO;

from cygapt.url_opener import CygAptURLopener;

class TestUrlOpener(unittest.TestCase):
    """Unit test for cygapt.url_opener
    """

    def setUp(self):
        unittest.TestCase.setUp(self);
        self.obj = CygAptURLopener(True);

    def test__init__(self):
        self.assertTrue(isinstance(self.obj, CygAptURLopener));

    def testHttp_error_default(self):
        f = TemporaryFile();
        errcode = 404;
        self.obj.http_error_default("url", f, errcode, "errmsg", "headers");
        f.close();
        self.assertEqual(self.obj.getErrorCode(), errcode);

    def testDlProgress(self):
        old_stdout = sys.stdout;
        buf = StringIO();
        sys.stdout = buf;
        self.obj.dlProgress(1, 512, 1024);
        sys.stdout = old_stdout;
        buf.seek(0);
        out = buf.readline();
        buf.close();
        expect_out = "[====================>                   ]\r";

        self.assertEqual(out, expect_out);

if __name__ == "__main__":
    unittest.main();
