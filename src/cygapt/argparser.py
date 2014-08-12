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

import argparse;
import warnings;

class CygAptArgParser():
    def __init__(self, usage=None, scriptname=None):
        self.__parser = None;
        self.__isCompiled = False;

        self.setUsage(usage);
        self.setAppName(scriptname);

        self.__parser = argparse.ArgumentParser(
            prog=self._appName,
            add_help=False,
            usage=self._usage,
        );

        self.__commands = [
            'setup',
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
            'postinstall',
        ];


    def getUsage(self):
        return self._usage;

    def setUsage(self, usage):
        self._usage = str(usage);

    def getAppName(self):
        return self._appName;

    def setAppName(self, app_name):
        self._appName = str(app_name);

    def compile(self):
        if self.__isCompiled:
            return;

        self.__parser.add_argument(
            'command',
            nargs='?',
            default="help",
            choices=self.__commands
        );

        self.__parser.add_argument(
            'package',
            nargs='*'
        );

        self.__parser.add_argument(
            '-q', '--quiet',
            action='store_false',
            default=True,
            help="Loggable output - no progress indicator",
            dest='verbose'
        );

        self.__parser.add_argument(
            '-d', '--download',
            action='store_true',
            dest='download_p',
            help="download only"
        );

        self.__parser.add_argument(
            '-m', '--mirror',
            nargs=1,
            help="use mirror"
        );

        self.__parser.add_argument(
            '-t', '--dist',
            nargs=1,
            dest='distname',
            default='curr',
            choices=['curr', 'test', 'prev'],
            help="set dist name"
        );

        self.__parser.add_argument(
            '-a',
            action='store_true',
            dest='noupdate',
            help="do not update"
        );

        self.__parser.add_argument(
            '-x', '--no-deps',
            action='store_true',
            dest='nodeps_p',
            help="ignore dependencies"
        );

        self.__parser.add_argument(
            '-s', '--regexp',
            action='store_true',
            dest='regex_search',
            help="search as regex pattern"
        );

        self.__parser.add_argument(
            '-f', '--nobarred', '--force',
            action='store_true',
            dest='force',
            help="add/remove packages cyg-apt depends on"
        );

        self.__parser.add_argument(
            '-X', '--no-verify',
            action='store_false',
            dest='verify',
            help="do not verify setup.ini signatures"
        );

        self.__parser.add_argument(
            '-y', '--nopostinstall',
            action='store_true',
            help="do not run postinstall scripts"
        );

        self.__parser.add_argument(
            '-z', '--nopostremove',
            action='store_true',
            help="do not run preremove/postremove scripts"
        );

        self.__parser.add_argument(
            '-h', '--help',
            action='store_true',
            help="show brief usage"
        );

        self.__isCompiled = True;


    def parse(self):
        """Parse the system args

        """
        if not self.__isCompiled:
            self.compile();

        args = self.__parser.parse_args();

        args = self.__castTypes(args);

        if args.nopostinstall :
            warnings.warn(
                "The option -y, --nopostinstall is deprecated since version "
                "1.1 and will be removed in 2.0.",
                DeprecationWarning
            );

        return args;

    def __castTypes(self, args):
        if args.mirror and isinstance(args.mirror, list):
            args.mirror = args.mirror[0];

        if args.distname and isinstance(args.distname, list):
            args.distname = args.distname[0];

        return args;
