"""
  cyg-apt - a Cygwin package manager.

  (c) 2002--2009 Chris Cormie         Jan Nieuwenhuizen
                 <cjcormie@gmail.com> <janneke@gnu.org>
  (c) 2012       James Nylen
                 <jnylen@gmail.com>
  (c) 2012-2013  Alexandre Querci
                 <alquerci@email.com>

  License: GNU GPL
"""

import os

import utils as cautils

class PathMapper:
    def __init__(self, root, cygwin_p):
        self.root = root
        mountout = os.popen(self.root + "/bin/mount").readlines()
        self.mountroot = "/"
        self.add_mapping(mountout)
        self.cygwin_p = cygwin_p

    def add_mapping(self, mtab):
        self.map = {}
        mtab = [l.split() for l in mtab]
        for l in mtab:
            if l[2] != "/":
                self.map[l[2] + "/"] = l[0] + "/"
            else:
                self.mountroot = l[0] + "/"

    def map_path(self, path):
        if self.cygwin_p:
            return path
        # sort to map to /e/bar/foo in pefrence /e/bar
        l = cautils.prsort(list(self.map.keys()))
        for cygpath in l:
            if path.find(cygpath) == 0:
                path = path.replace(cygpath, self.map[cygpath])
                return path
        return self.root + path
