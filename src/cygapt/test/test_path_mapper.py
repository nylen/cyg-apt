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
from cygapt.test.case import dataProvider;
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

    @dataProvider('getMapPathOutsideCygwinData')
    def testMapPathOutsideCygwin(self, path, expected, message=None):
        pm = self._createPathMapper(self._var_root, False);

        pm.setMap({
            '/usr/bin/': 'C:/cygwin/bin/',
            '/usr/lib/': 'C:/cygwin/lib/',
            '/cygdrive/c/': 'C:/',
        });

        self.assertEqual(pm.mapPath(path), expected, message);

    def getMapPathOutsideCygwinData(self):
        return [
            ['/usr/bin/', 'C:/cygwin/bin/'],
            ['C:/cygwin/lib/', 'C:/cygwin/lib/', 'Does not map path that has been already mapped'],
            ['/cygdrive/c', 'C:', 'Work without ending slash'],
            ['/cygdrive/c/foo/cygdrive/c/', 'C:/foo/cygdrive/c/', 'Replaced only at the beginning of the path'],
            ['/', 'C:/cygwin/'],
        ];

    def _createPathMapper(self, root='', cygwin_p=False):
        return PathMapper(root, cygwin_p);

if __name__ == "__main__":
    unittest.main();
