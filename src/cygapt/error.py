"""
  cyg-apt - a Cygwin package manager.

  (c) 2002--2009 Chris Cormie         Jan Nieuwenhuizen
                 <cjcormie@gmail.com> <janneke@gnu.org>
  (c) 2012       James Nylen
                 <jnylen@gmail.com>

  License: GNU GPL
"""

class CygAptError(Exception):
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg
