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

from __future__ import print_function;
from __future__ import absolute_import;

import sys;
import urllib;

class CygAptURLopener(urllib.FancyURLopener):
    BAR_MAX = 40;

    def __init__(self, verbose, *args):
        urllib.FancyURLopener.__init__(self, *args);
        self.__verbose = verbose;
        self.__errorCode = 200;

    def getErrorCode(self):
        return self.__errorCode;

    def setErrorCode(self, code):
        self.__errorCode = int(code);

    def http_error_default(self, url, fp, errcode, errmsg, headers):
        self.__errorCode = errcode;
        return urllib.FancyURLopener.http_error_default(
            self,
            url,
            fp,
            errcode,
            errmsg,
            headers
        );

    def dlProgress(self, count, blockSize, totalSize):
        if self.__errorCode != 200:
            return;
        if not self.__verbose:
            return;
        barmax = self.BAR_MAX;
        ratio = min((count * blockSize), totalSize) / float(totalSize);
        bar = int(barmax * ratio);
        if ratio == 1.0:
            sys.stdout.write(" "*70 + "\r");
            sys.stdout.flush();
        else:
            print("[", end="");
            for i in range(barmax):
                if i < bar:
                    sys.stdout.write("=");
                elif i == bar:
                    sys.stdout.write(">");
                else:
                    sys.stdout.write(" ");
            sys.stdout.write("]\r");
            sys.stdout.flush();
