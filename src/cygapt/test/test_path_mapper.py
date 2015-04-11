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
import sys;
from tempfile import TemporaryFile;

from cygapt.test.case import TestCase;
from cygapt.path_mapper import PathMapper;

class TestPathMapper(TestCase):
    def setUp(self):
        TestCase.setUp(self);
        self._var_root = "C:/cygwin";
        self._var_cygwin_p = sys.platform.startswith("cygwin");

    def test__init__(self):
        pm = self._createPathMapper(self._var_root, self._var_cygwin_p);

        self.assertTrue(isinstance(pm, PathMapper));
        self.assertEqual(self._var_root, pm.getRoot());

    def testAddMapping(self):
        pm = self._createPathMapper(self._var_root, self._var_cygwin_p);

        mount = (
        "C:/cygwin/bin on /usr/bin type ntfs (binary,auto){LF}"
        "C:/cygwin/lib on /usr/lib type ntfs (binary,auto){LF}"
        "C:/cygwin on / type ntfs (binary,auto){LF}"
        "C: on /cygdrive/c type ntfs (binary,posix=0,user,noumount,auto){LF}"
        "".format(LF="\n")
        );
        f = TemporaryFile(mode='w+');
        f.writelines(mount);
        f.seek(0);
        mtab = f.readlines();
        f.close();

        mapping = {
            '/usr/bin/': "C:/cygwin/bin/",
            '/usr/lib/': "C:/cygwin/lib/",
            '/cygdrive/c/': "C:/",
        };
        pm._addMapping(mtab);
        self.assertEqual(pm.getMap(), mapping);
        self.assertEqual(pm.getMountRoot(), "C:/cygwin/");

    def testMapPath(self):
        pm = self._createPathMapper(self._var_root, True);

        self.assertEqual(pm.mapPath("/usr/bin/"), "/usr/bin/");

    def testMapPathOutsideCygwin(self):
        pm = self._createPathMapper(self._var_root, False);

        mapping = {
             '/usr/bin/': 'C:/cygwin/bin/',
             '/usr/lib/': 'C:/cygwin/lib/',
             '/cygdrive/c/': 'C:/',
        };

        pm.setMap(mapping);

        for cygpath, winpath in list(mapping.items()):
            self.assertEqual(pm.mapPath(cygpath), winpath);

            # Does not map path that has been already mapped
            self.assertEqual(pm.mapPath(pm.mapPath(cygpath)), winpath);

            # also work without ending slash
            self.assertEqual(pm.mapPath(cygpath.rstrip('/')), winpath.rstrip('/'));

            # Replaced only at the beginning of the path
            self.assertEqual(pm.mapPath(cygpath+'foo'+cygpath), winpath+'foo'+cygpath);

    def _createPathMapper(self, root='', cygwin_p=False):
        return PathMapper(root, cygwin_p);

if __name__ == "__main__":
    unittest.main();
