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

class ApplicationException(Exception):
    def __init__(self, message="", code=1, previous=None):
        Exception.__init__(self, message);
        self._message = str(message);
        self._code = int(code);
        if previous is None:
            self._previous = None;
        else:
            assert isinstance(previous, BaseException);
            self._previous = previous;

    def getCode(self):
        return self._code;

    def getMessage(self):
        return self._message;

    def getPrevious(self):
        return self._previous;

class ProcessException(ApplicationException):
    pass;

class InvalidArgumentException(ApplicationException):
    pass;

class PathExistsException(ApplicationException):
    pass;

class InvalidFileException(ApplicationException):
    pass;

class UnexpectedValueException(ApplicationException):
    pass;
