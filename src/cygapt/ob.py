# -*- coding: utf-8 -*-
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

import sys;
from cStringIO import StringIO;

class CygAptOb:
    """Output Buffering Control (like php)

    The Output Control functions allow you to control
    when output is sent from the script.
    """

    def __init__(self, start=False):
        self._state = False;
        self._buffer = None;
        self._value = '';
        self._stdout = None;
        if start:
            self.start();

    def start(self):
        """Turn on output buffering
        """
        self._stdout = sys.stdout;
        sys.stdout = StringIO();
        self._buffer = sys.stdout;
        self._state = True;
        self._value = '';

    def _end(self):
        """Turn off output buffering
        """
        if self._state:
            self._buffer.close();
            self._buffer = None;
            sys.stdout = self._stdout;
            self._state = False;

    def flush(self):
        """Flush (send) the output buffer
        """
        self.clean();
        if self._value:
            self._stdout.write(self._value);
            self._stdout.flush();
        self._value = '';

    def getFlush(self):
        """Flush the output buffer,
        return it as a string and turn off output buffering
        """
        self.clean();
        content = self.getContents();
        self._end();
        return content;

    def endFlush(self):
        """Flush (send) the output buffer and turn off output buffering
        """
        self.flush();
        self._end();

    def clean(self):
        """Clean (erase) the output buffer
        """
        if self._state:
            self._value = self._buffer.getvalue();
            self._buffer.truncate(0);

    def getClean(self):
        """Get current buffer contents and delete current output buffer
        """
        if not self._state:
            return False;

        content = self.getContents();
        self.endClean();
        return content;

    def endClean(self):
        """Clean (erase) the output buffer and turn off output buffering
        """
        self._value = '';
        self._end();

    def implicitFlush(self, flag=True):
        """Turn implicit flush on/off
        """
        if flag and self._state:
            self._end();
        elif not flag and not self._state:
            self.start();

    def getContents(self):
        """Return the contents of the output buffer
        """
        if not self._state:
            return False;

        buf = self._buffer.getvalue();
        if buf:
            self._value = buf;
        return self._value;

    def getLength(self):
        """Return the length of the output buffer
        """
        if not self._state:
            return False;

        return len(self.getContents());
