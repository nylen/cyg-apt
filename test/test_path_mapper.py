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
'''

'''

from __future__ import print_function;
import unittest;
import sys;
from tempfile import TemporaryFile;

from cygapt.path_mapper import PathMapper;

class TestPathMapper(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self);
        self._var_root = "";
        self._var_cygwin_p = sys.platform == 'cygwin';
        self.obj = PathMapper(self._var_root, self._var_cygwin_p);
        
    def test__init__(self):
        self.assertTrue(isinstance(self.obj, PathMapper));
        self.assertEqual(self._var_root, self.obj.root);
        self.assertEqual(self._var_cygwin_p, self.obj.cygwinPlatform);

    def testAddMapping(self):
        mount = r"""C:/cygwin/bin on /usr/bin type ntfs (binary,auto)
C:/cygwin/lib on /usr/lib type ntfs (binary,auto)
C:/cygwin on / type ntfs (binary,auto)
C: on /cygdrive/c type ntfs (binary,posix=0,user,noumount,auto)
"""
        f = TemporaryFile(mode="w+");
        f.writelines(mount);
        f.seek(0);
        mtab = f.readlines();
        f.close();
        
        mapping = {'/usr/bin/': 'C:/cygwin/bin/',
                        '/usr/lib/': 'C:/cygwin/lib/',
                        '/cygdrive/c/': 'C:/'};
        self.obj.addMapping(mtab);
        self.assertEqual(self.obj.map, mapping);
        self.assertEqual(self.obj.mountRoot, "C:/cygwin/");

    def testMapPath(self):
        if sys.platform == "cygwin":
            self.assertEqual(self.obj.mapPath("/usr/bin/"), "/usr/bin/");
            return;
        
        self.obj.map = {'/usr/bin/': 'C:/cygwin/bin/',
                        '/usr/lib/': 'C:/cygwin/lib/',
                        '/cygdrive/c/': 'C:/'};
        
        for cyg in list(self.obj.map.keys()):
            self.assertEqual(self.obj.mapPath(cyg), self.obj.map[cyg]);


if __name__ == '__main__':
    unittest.main();
