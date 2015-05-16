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

import cygapt.utils as cautils;
from cygapt.process import Process;

class PathMapper:
    def __init__(self, root, cygwin_p):
        self.__root = root;
        self.__mountRoot = "/";
        self.__cygwinPlatform = cygwin_p;
        self.__map = {};

        p = Process(self.__root + "/bin/mount");
        p.run();
        mountout = p.getOutput().splitlines(True);
        self._addMapping(mountout);

    def getRoot(self):
        return self.__root;

    def setRoot(self, root_dir):
        self.__root = root_dir;

    def getMountRoot(self):
        return self.__mountRoot;

    def setMountRoot(self, mount_root):
        self.__mountRoot = mount_root;

    def getMap(self):
        return self.__map;

    def setMap(self, mapping):
        self.__map = mapping;

    def _addMapping(self, mtab):
        self.__map = {};
        mtab = [l.split() for l in mtab];
        for l in mtab:
            if l[2] != "/":
                self.__map[l[2] + "/"] = l[0] + "/";
            else:
                self.__mountRoot = l[0] + "/";

    def mapPath(self, path):
        if self.__cygwinPlatform:
            return path;

        # does map a path that has been already mapped
        if ':' in path :
            return path;

        # sort to map to /e/bar/foo in pefrence /e/bar
        l = cautils.prsort(list(self.__map.keys()));
        for cygpath in l:
            index = path.find(cygpath);
            if index == 0:
                return self.__map[cygpath]+path[len(cygpath):];
            if cygpath.rstrip('/') == path :
                return self.__map[cygpath].rstrip('/');
        return self.__root + path;
