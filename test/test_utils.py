#!/usr/bin/python
"""
Created on 23 dec. 2012

"""

import unittest
import sys
import os

import cygapt.utils as utils
import cygapt.error as error
from testcase import TestCase

class TestUtils(TestCase):
    def _get_tmpdir(self):
        return self._dir_tmp
    
    def _get_tmpfilename(self):
        filename = "%s%stest~" % (self._get_tmpdir(), os.path.sep)
        return filename

    def test_cygpath(self):
        if sys.platform != "cygwin":
            self.skipTest("requires cygwin")

        good_paths = ["/", ".", "./", "./.", "/bin"]
        
        for path in good_paths:
            ret = utils.cygpath(path)
            self.assertEquals(ret, path)

    def test_parse_rc(self):
        f = open(self._get_tmpfilename(), "wb")
        f.write("always_update = True")
        f.close()
        
        ret = utils.parse_rc(self._get_tmpfilename())
        self.assertTrue(ret)
        
        
        f = open(self._get_tmpfilename(), "wb")
        f.write("always_update = bad_value")
        f.close()
        
        self.assertRaises(NameError,
                          utils.parse_rc,
                          self._get_tmpfilename())


    def test_prsort(self):
        in_lst = ["B",
                  "A",
                  "a",
                  "1",
                  "b",
                  "/",
                  "",
                  "2",
                  ]
        
        out_lst = ["b",
                   "a",
                   "B",
                   "A",
                   "2",
                   "1",
                   "/",
                   "",
                   ]
        
        utils.prsort(in_lst)
        self.assertEqual(in_lst, out_lst)

    def test_rename(self):
        dest = self._get_tmpfilename()
        src = "%s2" % (self._get_tmpfilename())
        stream = open(src, 'wb+')
        stream.writelines('1')
        stream.seek(0)
        src_content = stream.readlines()
        stream.close()
        
        stream = open(dest, "wb")
        stream.writelines('2')
        stream.close()
        
        utils.rename(src, dest)
        
        stream = open(dest, "r")
        res_dest_content = stream.readlines()
        stream.close()
        
        self.assertFalse(os.path.exists(src))
        self.assertEqual(src_content, res_dest_content)
        
        if os.path.exists(src):
            os.unlink(src)

    def test_rmtree(self):
        # create tree
        root = os.path.join(self._get_tmpdir(), "root~")
        subdir = os.path.join(root, "subdir~")
        rootfile = os.path.join(root, "file~")
        subdirfile = os.path.join(subdir, "file~")
        def build_tree():
            if not os.path.exists(subdir):
                os.makedirs(subdir)
            f = open(rootfile, "w")
            e = open(subdirfile, "w")
            f.close()
            e.close()
            
        def rm_tree():
            if os.path.exists(rootfile):
                os.unlink(rootfile)
            if os.path.exists(rootfile):
                os.unlink(subdirfile)
            if os.path.exists(rootfile):
                os.rmdir(subdir)
            if os.path.exists(rootfile):
                os.rmdir(root)
        
        build_tree()
        
        utils.rmtree(root)
        ok = False
        if  os.path.exists(subdirfile) or \
            os.path.exists(subdir) or \
            os.path.exists(rootfile) or \
            os.path.exists(root):
            ok = False
        else:
            ok = True
        
        self.assertTrue(ok)
        rm_tree()
        
        build_tree()
        utils.rmtree(rootfile)
        ok = False
        if  os.path.exists(subdirfile) and \
            os.path.exists(subdir) and \
            not os.path.exists(rootfile) and \
            os.path.exists(root):
            ok = True
        else:
            ok = False
        self.assertTrue(ok)
        rm_tree()
        
    def test_uri_get(self):
        directory = self._get_tmpdir()
        uri = "http://cygwin.uib.no/setup.bz2.sig"
        verbose = False
        utils.uri_get(directory, uri, verbose)
        self.assertTrue(os.path.exists(os.path.join(directory, "setup.bz2.sig")),
                        "http request")
        
        self.assertRaises(error.CygAptError,
                          utils.uri_get,
                          "", "", verbose)
        
        uri = "ftp://cygwin.uib.no/pub/cygwin/setup.ini.sig"
        utils.uri_get(directory, uri, verbose)
        self.assertTrue(os.path.exists(os.path.join(directory, "setup.ini.sig")),
                        "ftp request")

        uri = "rsync://cygwin.uib.no/cygwin/setup-legacy.bz2.sig"
        self.assertRaises(error.CygAptError,
                          utils.uri_get,
                          directory,
                          uri,
                          verbose)

if __name__ == "__main__":
    unittest.main()
