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
    Unit test for cygapt.setup
"""

from __future__ import print_function
import unittest
import sys
import os
import subprocess

from cygapt.setup import CygAptSetup
import cygapt.utilstest

class TestSetup(cygapt.utilstest.TestCase):
    def setUp(self):
        cygapt.utilstest.TestCase.setUp(self)
        self._var_verbose = False
        self._var_cygwin_p = sys.platform == "cygwin"
        self.obj = CygAptSetup(self._var_cygwin_p, self._var_verbose)
        self.obj.tmpdir = self._dir_tmp
        self.obj.sn = self._var_exename
        self.obj.config = self._dir_confsetup
        self.obj.ROOT = self._dir_mtroot
        self.obj.ABSOLUTE_ROOT = self._dir_mtroot
        
    def test___init__(self):
        self.assertTrue(isinstance(self.obj, CygAptSetup))
        self.assertEqual(self.obj.cygwin_p, self._var_cygwin_p)
        self.assertEqual(self.obj.verbose, self._var_verbose)
        
    def test_get_setup_rc(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin")
            
        badlocation = os.path.join(self._var_tmpdir, "not_exist_file")
        last_cache, last_mirror = self.obj.get_setup_rc(badlocation)
        self.assertEqual(last_cache, None)
        self.assertEqual(last_mirror, None)
        
        last_cache, last_mirror = self.obj.get_setup_rc(self._dir_confsetup)
        self.assertEqual(last_cache, self._dir_execache)
        self.assertEqual(last_mirror, self._var_mirror_http)

    def test_get_pre17_last(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin")
        
        location = self._var_tmpdir
        last_mirror = "http://cygwin.xl-mirror.nl/"
        last_cache = os.path.join(self._var_tmpdir, "last_cache")
        os.mkdir(last_cache)
        lm_file = os.path.join(self._var_tmpdir, "last-mirror")
        lc_file = os.path.join(self._var_tmpdir, "last-cache")
        lm_stream = open(lm_file, "w")
        lm_stream.write(last_mirror)
        lm_stream.close()
        lc_stream = open(lc_file, "w")
        lc_stream.write(last_cache)
        lc_stream.close()
        
        
        rlast_cache, rlast_mirror = self.obj.get_pre17_last(location)
        self.assertEqual(last_cache, rlast_cache)
        self.assertEqual(last_mirror, rlast_mirror)
    
    def test_update(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin")

        self.obj.gpg_import(self.obj.cygwin_pubring_uri)
        self.obj.setup()
        
        self.obj.update(self._file_user_config, True)
    
    def test_setup(self):
        if not self._var_cygwin_p:
            self.obj.sn = self._var_exename
            self.assertRaises(SystemExit, self.obj.setup)
            return
        
        # env HOME not exists
        os.environ.pop('HOME')
        self.assertRaises(SystemExit, self.obj.setup)
        os.environ['HOME'] = self._dir_user
        
        # config file already isset
        f = open(self._file_user_config, "w")
        f.close()
        self.assertRaises(SystemExit, self.obj.setup)
        self.assertEqual(self.obj.cyg_apt_rc, self._file_user_config)
        
        os.remove(self._file_user_config)

        # next
        self.obj.gpg_import(self.obj.cygwin_pubring_uri)
        self.obj.setup()
        
    def test_write_installed(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin")
        
        real_installed_db = self._file_installed_db.replace(self._var_tmpdir, "")
        self.obj.write_installed(self._file_installed_db)
        self.assertTrue(os.path.exists(self._file_installed_db))
        f = open(self._file_installed_db);
        ret = f.readlines().sort();
        f.close();
        f = open(real_installed_db);
        expected = f.readlines().sort();
        f.close();
        self.assertEqual(ret, expected)
    
    def test_gpg_import(self):
        if not self._var_cygwin_p:
            self.skipTest("requires cygwin")
        
        self.obj.gpg_import(self.obj.cygwin_pubring_uri)
        
        cmd = "gpg "
        cmd += "--no-secmem-warning "
        cmd += "--list-public-keys --fingerprint "
        p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE);
        if p.wait():
            raise RuntimeError(p.stderr.read());
        lines = p.stdout.readlines();
        findout = False
        for line in lines:
            if isinstance(line, bytes):
                marker = self.obj.gpg_good_sig_msg.encode();
            else:
                marker = self.obj.gpg_good_sig_msg;
            if marker in line:
                findout = True
                break
            
        self.assertTrue(findout)
        
    def test_usage(self):
        self.obj.usage();

if __name__ == "__main__":
    unittest.main()