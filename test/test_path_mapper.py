#!/usr/bin/python
'''

'''

from __future__ import print_function
import unittest
import sys
from tempfile import TemporaryFile

from cygapt.path_mapper import PathMapper

class TestPathMapper(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self._var_root = ""
        self._var_cygwin_p = sys.platform == 'cygwin'
        self.obj = PathMapper(self._var_root, self._var_cygwin_p)
        
    def test___init__(self):
        self.assertTrue(isinstance(self.obj, PathMapper))
        self.assertEqual(self._var_root, self.obj.root)
        self.assertEqual(self._var_cygwin_p, self.obj.cygwin_p)

    def test_add_mapping(self):
        mount = r"""C:/cygwin/bin on /usr/bin type ntfs (binary,auto)
C:/cygwin/lib on /usr/lib type ntfs (binary,auto)
C:/cygwin on / type ntfs (binary,auto)
C: on /cygdrive/c type ntfs (binary,posix=0,user,noumount,auto)
"""
        f = TemporaryFile(mode="w+")
        f.file.writelines(mount)
        f.file.seek(0)
        mtab = f.file.readlines()
        f.close()
        
        mapping = {'/usr/bin/': 'C:/cygwin/bin/',
                        '/usr/lib/': 'C:/cygwin/lib/',
                        '/cygdrive/c/': 'C:/'}
        self.obj.add_mapping(mtab)
        self.assertEqual(self.obj.map, mapping)
        self.assertEqual(self.obj.mountroot, "C:/cygwin/")

    def test_map_path(self):
        if sys.platform == "cygwin":
            self.assertEqual(self.obj.map_path("/usr/bin/"), "/usr/bin/")
            return
        
        self.obj.map = {'/usr/bin/': 'C:/cygwin/bin/',
                        '/usr/lib/': 'C:/cygwin/lib/',
                        '/cygdrive/c/': 'C:/'}
        
        for cyg in list(self.obj.map.keys()):
            self.assertEqual(self.obj.map_path(cyg), self.obj.map[cyg])


if __name__ == '__main__':
    unittest.main()