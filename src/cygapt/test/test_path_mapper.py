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

from cygapt.path_mapper import PathMapper;

class TestPathMapper(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self);
        self._var_root = "";
        self._var_cygwin_p = sys.platform.startswith("cygwin");
        self.obj = PathMapper(self._var_root, self._var_cygwin_p);

    def test__init__(self):
        self.assertTrue(isinstance(self.obj, PathMapper));
        self.assertEqual(self._var_root, self.obj.getRoot());

    def testAddMapping(self):
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
        self.obj._addMapping(mtab);
        self.assertEqual(self.obj.getMap(), mapping);
        self.assertEqual(self.obj.getMountRoot(), "C:/cygwin/");

    def testMapPath(self):
        if self._var_cygwin_p:
            self.assertEqual(self.obj.mapPath("/usr/bin/"), "/usr/bin/");
            return;

        mapping = {
             '/usr/bin/': 'C:/cygwin/bin/',
             '/usr/lib/': 'C:/cygwin/lib/',
             '/cygdrive/c/': 'C:/',
        };

        self.obj.setMap(mapping);

        for cyg in list(mapping.keys()):
            self.assertEqual(self.obj.mapPath(cyg), mapping[cyg]);

if __name__ == "__main__":
    unittest.main();
