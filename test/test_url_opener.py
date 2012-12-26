#!/usr/bin/python

import unittest
import sys
from tempfile import TemporaryFile

from cygapt.url_opener import CygAptURLopener

class TestUrlOpener(unittest.TestCase):
    '''
    Unit test for cygapt.url_opener
    '''

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.obj = CygAptURLopener(True)

    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygAptURLopener))

    def test_http_error_default(self):
        f = TemporaryFile()
        errcode = 404
        self.obj.http_error_default("url", f.file, errcode, "errmsg", "headers")
        self.assertTrue(self.obj.errcode == errcode)
        f.close()
        
    def test_dlProgress(self):
        self.obj.verbose = 1
        f = TemporaryFile()
        old_stdout = sys.stdout
        sys.stdout = f.file
        self.obj.dlProgress(1, 512, 1024)
        sys.stdout = old_stdout
        f.file.seek(0)
        out = f.file.readline()
        f.close()
        expect_out = "[====================>                   ]\r"
        
        self.assertEqual(out, expect_out)
        
        
if __name__ == "__main__":
    unittest.main()