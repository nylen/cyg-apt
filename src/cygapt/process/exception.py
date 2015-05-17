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

class ProcessFailedException(Exception):
    def __init__(self, process):
        Exception.__init__(self, """\
The command "{0}" failed.
Exit Code: {1} ({2})

Output:
================
{3}

Error Output:
================
{4}\
""".format(
            process.getCommandLine(),
            process.getExitCode(),
            process.getExitCodeText(),
            process.getOutput(),
            process.getErrorOutput(),
        ));

class LogicException(Exception):
    pass;
