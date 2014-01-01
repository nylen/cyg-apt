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

import os;

import cygapt.utils as cautils;

class PathMapper:
    def __init__(self, root, cygwin_p):
        self.__root = root;
        self.__mountRoot = "/";
        self.__cygwinPlatform = cygwin_p;
        self.__map = {};

        p = os.popen(self.__root + "/bin/mount");
        mountout = p.readlines();
        p.close();
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
        # sort to map to /e/bar/foo in pefrence /e/bar
        l = cautils.prsort(list(self.__map.keys()));
        for cygpath in l:
            if path.find(cygpath) == 0:
                path = path.replace(cygpath, self.__map[cygpath]);
                return path;
        return self.__root + path;
