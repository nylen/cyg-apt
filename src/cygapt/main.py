#!/usr/bin/python
"""
  cyg-apt - a Cygwin package manager.

  (c) 2002--2009 Chris Cormie         Jan Nieuwenhuizen
                 <cjcormie@gmail.com> <janneke@gnu.org>
  (c) 2012       James Nylen
                 <jnylen@gmail.com>

  License: GNU GPL
"""

import sys
import os

import utils as cautils
from setup import CygAptSetup
from ob import CygAptOb
from argparser import CygAptArgParser
from cygapt import CygApt
from error import CygAptError

class CygAptMain():
    def __init__(self):
        main_downloads = None
        main_dists = 0
        main_installed = 0
        main_packagename = None
        main_cyg_apt_rc = None
        home_cyg_apt_rc = None
        main_verbose = False

        main_cygwin_p = (sys.platform == "cygwin")
        cas = CygAptSetup(main_cygwin_p, main_verbose)
        update_not_needed = ["ball", "find", "help", "purge", "remove", "version",\
            "filelist", "update", "setup", "md5"]

        main_scriptname = os.path.basename(sys.argv[0])
        if (main_scriptname[-3:] == ".py"):
            main_scriptname = main_scriptname[:-3]

        ob = CygAptOb(True)
        cas.usage()
        usage = ob.get_flush()

        cap = CygAptArgParser(usage=usage, scriptname=main_scriptname)
        args = cap.parse()

        main_command = args.command

        main_files = args.package[:]
        main_files.insert(0, main_command)
        if len(args.package) > 0:
            main_packagename = args.package[0]
        else:
            main_packagename = None

        main_verbose = args.verbose
        main_download_p = args.download_p
        main_mirror = args.mirror
        main_distname = args.distname
        main_noupdate = args.noupdate
        main_nodeps_p = args.nodeps_p
        main_regex_search = args.regex_search
        main_nobarred = args.nobarred
        main_verify = args.verify
        main_nopostinstall = args.nopostinstall
        main_nopostremove = args.nopostremove


        cas.set_verbose(main_verbose)

        # Take most of our configuration from .cyg-apt
        # preferring .cyg-apt in current directory over $(HOME)/.cyg-apt
        cwd_cyg_apt_rc = os.getcwd() + '/.' + main_scriptname
        if os.path.exists(cwd_cyg_apt_rc):
            main_cyg_apt_rc = cwd_cyg_apt_rc
        elif "HOME" in os.environ:
            home_cyg_apt_rc = os.environ['HOME'] + '/.' + main_scriptname
            if os.path.exists(home_cyg_apt_rc):
                main_cyg_apt_rc = home_cyg_apt_rc


        if main_cyg_apt_rc:
            # Take our configuration from .cyg-apt
            # Command line options can override, but only for this run.
            main_cyg_apt_rc = main_cyg_apt_rc.replace("\\","/")
        elif (main_command != "setup"):
            print("%(sn)s: no .%(sn)s: run \"%(sn)s setup\" Exiting." \
                  % {'sn':main_scriptname})
            sys.exit(1)

        if (main_command == "setup"):
            cas.setup()
            sys.exit(0)
        elif (main_command == "help"):
            cas.usage(main_cyg_apt_rc)
            sys.exit(0)
        elif (main_command == "update"):
            cas.update(main_cyg_apt_rc, main_verify, main_mirror = main_mirror)
            sys.exit(0)
        always_update = cautils.parse_rc(main_cyg_apt_rc)
        always_update = always_update and\
            main_command not in update_not_needed and\
            not main_noupdate
        if always_update:
            cas.update(main_cyg_apt_rc, main_verify, main_mirror = main_mirror)

        if main_command and main_command in dir(CygApt):
            try:
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
                    main_scriptname,\
                    main_verbose)
            except CygAptError as exp:
                print(exp)
                sys.exit(1)

            # Launch!
            try:
                getattr(cyg_apt, main_command)()
            except CygAptError as xxx_todo_changeme2:
                (err) = xxx_todo_changeme2
                sys.stderr.write(main_scriptname + ": " + err.msg +\
                    ", exiting.\n")
        else:
            cas.usage(main_cyg_apt_rc)


if __name__ == '__main__':
    CygAptMain()
