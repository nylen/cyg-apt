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
import argparse;

class CygAptArgParser():
    def __init__(self, usage=None, scriptname=None):
        self.setUsage(usage);
        self.setAppName(scriptname);

    def getUsage(self):
        return self._usage;

    def setUsage(self, usage):
        self._usage = str(usage);

    def getAppName(self):
        return self._appName;

    def setAppName(self, app_name):
        self._appName = str(app_name);

    def parse(self):
        commands = ['setup',
                    'update',
                    'ball',
                    'download',
                    'filelist',
                    'find',
                    'help',
                    'install',
                    'list',
                    'md5',
                    'missing',
                    'new',
                    'purge',
                    'remove',
                    'requires',
                    'search',
                    'show',
                    'source',
                    'upgrade',
                    'url',
                    'version',
                    ];

        parser = argparse.ArgumentParser(prog=self._appName,
                                         add_help=False,
                                         usage=self._usage);

        parser.add_argument('command',
                            nargs='?',
                            default='help',
                            choices=commands
                            );

        parser.add_argument('package',
                            nargs="*");

        parser.add_argument('-q', '--quiet',
                            action='store_false',
                            default=True,
                            help='Loggable output - no progress indicator',
                            dest="verbose");

        parser.add_argument('-d', '--download',
                            action='store_true',
                            dest='download_p',
                            help='download only');

        parser.add_argument('-m', '--mirror',
                            nargs=1,
                            help='use mirror');

        parser.add_argument('-t', '--dist',
                            nargs=1,
                            dest='distname',
                            default='curr',
                            choices=['curr', 'test', 'prev'],
                            help='set dist name');

        parser.add_argument('-a',
                            action='store_true',
                            dest='noupdate',
                            help='do not update');

        parser.add_argument('-x', '--no-deps',
                            action='store_true',
                            dest='nodeps_p',
                            help='ignore dependencies');

        parser.add_argument('-s', '--regexp',
                            action='store_true',
                            dest='regex_search',
                            help='search as regex pattern');

        parser.add_argument('-f', '--nobarred', '--force',
                            action='store_true',
                            dest='force',
                            help='add/remove packages cyg-apt depends on');

        parser.add_argument('-X', '--no-verify',
                            action='store_false',
                            dest='verify',
                            help='do not verify setup.ini signatures');

        parser.add_argument('-y', '--nopostinstall',
                            action='store_true',
                            help='do not run postinstall scripts');

        parser.add_argument('-z', '--nopostremove',
                            action='store_true',
                            help='do not run preremove/postremove scripts');

        parser.add_argument('-h', '--help',
                            action='store_true',
                            help='show brief usage');

        args = parser.parse_args();

        return args;
