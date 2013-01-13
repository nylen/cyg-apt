"""
  cyg-apt - a Cygwin package manager.

  (c) 2002--2009 Chris Cormie         Jan Nieuwenhuizen
                 <cjcormie@gmail.com> <janneke@gnu.org>
  (c) 2012       James Nylen
                 <jnylen@gmail.com>
  (c) 2012-2013  Alexandre Quercia
                 <alquerci@email.com>

  License: GNU GPL
"""

from __future__ import print_function
import sys
import urllib

class CygAptURLopener(urllib.FancyURLopener):
    def __init__(self, verbose, *args):
        urllib.FancyURLopener.__init__(self, *args)
        self.verbose = verbose
        self.errcode = 200
        self.barmax = 40

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        self.errcode = errcode
        return urllib.FancyURLopener.http_error_default\
            (self, url, fp, errcode, errmsg, headers)

    def dlProgress(self, count, blockSize, totalSize):
        if self.errcode != 200:
            return
        if not self.verbose:
            return
        barmax = self.barmax
        ratio = min((count * blockSize), totalSize) / float(totalSize)
        bar = int(barmax * ratio)
        if ratio == 1.0:
            sys.stdout.write(" "*70 + "\r")
            sys.stdout.flush()
        else:
            print("[", end="");
            for i in range(barmax):
                if i < bar:
                    sys.stdout.write("=")
                elif i == bar:
                    sys.stdout.write(">")
                else:
                    sys.stdout.write(" ")
            sys.stdout.write("]\r")
            sys.stdout.flush()

