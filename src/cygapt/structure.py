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

class ConfigStructure():
    def __init__(self):
        self.ROOT = "";
        self.mirror = "";
        self.cache = "";

        # BC layer for `setup_ini` configuration field
        self.setup_ini = "";

        self.distname = "";
        self.barred = "";
        self.always_update = False;
