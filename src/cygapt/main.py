#!/usr/bin/python
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
import os;

import cygapt.utils as cautils;
from cygapt.setup import CygAptSetup;
from cygapt.ob import CygAptOb;
from cygapt.argparser import CygAptArgParser;
from cygapt.cygapt import CygApt;
from cygapt.exception import ApplicationException;

class CygAptMain():
    def __init__(self):
        self.__appName = None;
        try:
            exit_code = self.main();
        except ApplicationException as e:
            print("{0}: {1}".format(self.getAppName(), e),
                  file=sys.stderr
            );
            exit_code = e.getCode();

        sys.exit(exit_code);

    def getAppName(self):
        if self.__appName is None:
            self.__appName = os.path.basename(sys.argv[0]);
            if (self.__appName[-3:] == ".py"):
                self.__appName = self.__appName[:-3];
        return self.__appName;

    def main(self):
        main_downloads = None;
        main_dists = 0;
        main_installed = 0;
        main_packagename = None;
        main_cyg_apt_rc = None;
        home_cyg_apt_rc = None;
        main_verbose = False;

        main_cygwin_p = (sys.platform == "cygwin");
        cas = CygAptSetup(main_cygwin_p, main_verbose);
        update_not_needed = ["ball", "find", "help", "purge", "remove", "version",\
            "filelist", "update", "setup", "md5"];

        ob = CygAptOb(True);
        cas.usage();
        usage = ob.getFlush();

        cap = CygAptArgParser(usage=usage, scriptname=self.getAppName());
        args = cap.parse();

        main_command = args.command;

        main_files = args.package[:];
        main_files.insert(0, main_command);
        if len(args.package) > 0:
            main_packagename = args.package[0];
        else:
            main_packagename = None;

        main_verbose = args.verbose;
        main_download_p = args.download_p;
        main_mirror = args.mirror;
        main_distname = args.distname;
        main_noupdate = args.noupdate;
        main_nodeps_p = args.nodeps_p;
        main_regex_search = args.regex_search;
        main_nobarred = args.force;
        main_verify = args.verify;
        main_nopostinstall = args.nopostinstall;
        main_nopostremove = args.nopostremove;


        cas.setVerbose(main_verbose);

        # Take most of our configuration from .cyg-apt
        # preferring .cyg-apt in current directory over $(HOME)/.cyg-apt
        cwd_cyg_apt_rc = os.getcwd() + '/.' + self.getAppName();
        if os.path.exists(cwd_cyg_apt_rc):
            main_cyg_apt_rc = cwd_cyg_apt_rc;
        elif "HOME" in os.environ:
            home_cyg_apt_rc = os.environ['HOME'] + '/.' + self.getAppName();
            if os.path.exists(home_cyg_apt_rc):
                main_cyg_apt_rc = home_cyg_apt_rc;


        if main_cyg_apt_rc:
            # Take our configuration from .cyg-apt
            # Command line options can override, but only for this run.
            main_cyg_apt_rc = main_cyg_apt_rc.replace("\\","/");
        elif (main_command != "setup"):
            print("{0}: no .{0}: run \"{0} setup\"".format(self.getAppName()),
                  file=sys.stderr);
            return 1;

        if (main_command == "setup"):
            cas.setup(args.force);
            return 0;
        elif (main_command == "help"):
            cas.usage(main_cyg_apt_rc);
            return 0;
        elif (main_command == "update"):
            cas.update(main_cyg_apt_rc, main_verify, main_mirror = main_mirror);
            return 0;
        always_update = cautils.parse_rc(main_cyg_apt_rc);
        always_update = always_update and\
            main_command not in update_not_needed and\
            not main_noupdate;
        if always_update:
            cas.update(main_cyg_apt_rc, main_verify, main_mirror = main_mirror);

        if main_command and main_command in dir(CygApt):
            cyg_apt = CygApt(main_packagename,\
                main_files,\
                main_cyg_apt_rc,\
                main_cygwin_p,\
                main_download_p,\
                main_mirror,\
                main_downloads,\
                main_distname,\
                main_nodeps_p,\
                main_regex_search,\
                main_nobarred,\
                main_nopostinstall,\
                main_nopostremove,\
                main_dists,\
                main_installed,\
                self.getAppName(),\
                main_verbose);

            getattr(cyg_apt, main_command)();
        else:
            cas.usage(main_cyg_apt_rc);

        return 0;

if __name__ == '__main__':
    CygAptMain();
