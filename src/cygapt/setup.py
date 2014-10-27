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

from __future__ import print_function;
from __future__ import absolute_import;

import bz2;
import inspect;
import os;
import shutil;
import subprocess;
import sys;
import urllib;
import platform;

from cygapt.cygapt import CygApt;
from cygapt.exception import ApplicationException;
from cygapt.exception import ProcessException;
from cygapt.exception import PathExistsException;
from cygapt.exception import UnexpectedValueException;
from cygapt.utils import RequestException;
from cygapt.path_mapper import PathMapper;
import cygapt.utils as cautils;
import cygapt.version as version;
import cygapt.copying as copying;
from cygapt.structure import ConfigStructure;

class CygAptSetup:
    RC_OPTIONS = [
        'ROOT',
        'mirror',
        'cache',

        # BC layer for `setup_ini` configuration field
        'setup_ini',

        'distname',
        'barred',
        'always_update'
    ];
    RC_COMMENTS = {
        'ROOT' : "# The root of your Cygwin installation as a windows path\n",
        'mirror' : (
            "# URL of your Cygwin mirror: example "
            "http://mirror.internode.on.net/pub/cygwin/\n"
        ),
        'cache' : (
            "# Your package cache as a POSIX path: example "
            "/e/home/cygwin_package_cache\n"
        ),

        # BC layer for `setup_ini` configuration field
        "setup_ini" : (
            "# setup.ini lists available packages and is "
            "downloaded from the top level\n"
            "# of the downloaded mirror. Standard location is "
            "/etc/setup/setup.ini,\n"
            "# seutp-2.ini for Cygwin 1.7 Beta\n"
            "# Deprecated since version 1.1 and will be removed in 2.0.\n"
            "# "
        ),

        "distname" : (
            "# The distribution, current previous or test "
            "[curr, prev, test].\n"
            "# Usually you want the \"curr\" version of a package.\n"
        ),
        "barred" : (
            "# Packages which cyg-apt can't change under Cygwin "
            "since it depends on them.\n"
            "# Run cyg-apt under DOS with -f (force) option to change "
            "these packages.\n"
            "# Treat Cygwin core packages with CAUTION.\n"
        ),
        "always_update" : (
            "# Always update setup.ini before any command "
            "that uses it. cyg-apt will be\n# faster and use less bandwidth if "
            "False but you will have to run the update\n# command manually.\n"
        ),
    };
    GPG_GOOD_FINGER = "1169 DF9F 2273 4F74 3AA5  9232 A9A2 62FF 6760 41BA";
    GPG_CYG_PUBLIC_RING_URI = "http://cygwin.com/key/pubring.asc";
    VERSION = version.__version__;

    def __init__(self, cygwin_p, verbose, arch="x86"):
        self.__cygwinPlatform = cygwin_p;
        self.__verbose = verbose;
        self.__appName = os.path.basename(sys.argv[0]);
        self.setTmpDir();
        self.setPathMapper();
        self.__setupDir = "/etc/setup";
        self.__rc = ConfigStructure();
        self.__arch = arch;
        
        self.__rc.ROOT = self.__pm.getMountRoot();

    def getCygwinPlatform(self):
        return self.__cygwinPlatform;

    def setCygwinPlatform(self, cygwin_p):
        self.__cygwinPlatform = bool(cygwin_p);

    def setVerbose(self, verbose):
        self.__verbose = verbose;

    def getVerbose(self):
        return self.__verbose;

    def getAppName(self):
        return self.__appName;

    def setAppName(self, app_name):
        self.__appName = str(app_name);

    def getTmpDir(self):
        return self.__tmpDir;

    def setTmpDir(self, tmp_dir=None):
        if tmp_dir:
            self.__tmpDir = tmp_dir;
        elif 'TMP' in os.environ:
            self.__tmpDir = os.environ['TMP'];
        else:
            self.__tmpDir = "/usr/share/cyg-apt";

    def getPathMapper(self):
        return self.__pm;

    def setPathMapper(self, path_mapper=None):
        if path_mapper:
            assert isinstance(path_mapper, PathMapper);
            self.__pm = path_mapper;
        else:
            self.__pm = PathMapper("", self.__cygwinPlatform);

    def getRC(self):
        return self.__rc;

    def setRC(self, rc_structure):
        assert isinstance(rc_structure, ConfigStructure);
        self.__rc = rc_structure;

    def getSetupDir(self):
        return self.__setupDir;

    def setSetupDir(self, setup_dir):
        self.__setupDir = str(setup_dir);

    def setArchitecture(self, architecture):
        self.__arch = architecture;

    def _cygwinVersion(self):
        return float(platform.release()[:3]);

    def getSetupRc(self, location):
        filename = os.path.join(location, "setup.rc");
        if not (os.path.exists(filename)):
            return (None, None);
        f = open(filename);
        setup_rc = f.readlines();
        f.close();
        last_cache = None;
        last_mirror = None;
        for i in range(0, (len(setup_rc) -1)):
            if 'last-cache' in setup_rc[i]:
                last_cache = setup_rc[i+1].strip();
            if 'last-mirror' in setup_rc[i]:
                last_mirror = setup_rc[i+1].strip();
        last_cache = self.__pm.mapPath(last_cache);
        return (last_cache, last_mirror);

    def setup(self, force=False):
        """create cyg-apt configuration file, it overwrite with -f option"""
        if not self.__cygwinPlatform:
            msg = "setup outside Cygwin not supported.";
            raise PlatformException(msg);
        if "HOME" in os.environ:
            rc_file = os.path.join(
                os.environ['HOME'],
                ".{0}".format(self.__appName)
            );
        else:
            msg = "Can't locate home directory. Setup failed.";
            raise EnvironementException(msg);
        if os.path.exists(rc_file) and not force:
            msg = "{0} exists, not overwriting.".format(rc_file);
            raise PathExistsException(msg, code=0);

        installed_db = os.path.join(self.__setupDir, "installed.db");
        missing_cache_marker = "";
        missing_mirror_marker = "";
        self.__rc.distname = 'curr';
        # Refuse to remove/install any package including these substrings
        # since cyg-apt is dependent on them
        self.__rc.barred = "";
        self.__rc.always_update = False;

        if not self.__cygwinPlatform:
            msg = "Setup only supported under Cygwin.";
            raise PlatformException(msg);

        (last_cache, last_mirror) = self.getSetupRc(self.__setupDir);
        if ((not last_cache) or (not last_mirror)):
            (last_cache, last_mirror) = self._getPre17Last(self.__setupDir);
            if ((not last_cache) or (not last_mirror)):
                print("{0}: {1}/setup.rc not found. Please edit {2} to "\
                "provide mirror and cache. See cygwin.com/mirrors.html "\
                "for the list of mirrors.".format(
                    self.__appName,
                    self.__setupDir,
                    rc_file
                ));
                last_cache = missing_cache_marker;
                last_mirror  = missing_mirror_marker;
        self.__rc.mirror = last_mirror;
        self.__rc.cache = last_cache;

        # BC layer for `setup_ini` configuration field
        self.__rc.setup_ini = "{0}/setup.ini".format(self.__setupDir);

        contents = "";
        for i in self.__rc.__dict__:
            if i in list(self.RC_COMMENTS.keys()):
                contents += self.RC_COMMENTS[i];
            contents += "{0}=\"{1}\"\n\n".format(i, self.__rc.__dict__[i]);
        f = open(rc_file, 'w');
        f.write(contents);
        f.close();
        print("{0}: creating {1}".format(self.__appName, rc_file));

        if not os.path.isdir(self.__rc.ROOT):
            msg = "{0} no root directory".format(self.__rc.ROOT);
            raise UnexpectedValueException(msg);
        if not os.path.isdir(self.__setupDir):
            sys.stderr.write('creating {0}\n'.format(self.__setupDir));
            os.makedirs(self.__setupDir);
        if not os.path.isfile(installed_db):
            self._writeInstalled(installed_db);

        setupIniPath = os.path.join(
            self.__pm.mapPath(self.__rc.cache),
            urllib.quote(self.__rc.mirror+('' if self.__rc.mirror.endswith('/') else '/'), '').lower(),
            self.__arch,
            'setup.ini',
        );
        if not os.path.isfile(setupIniPath):
            sys.stderr.write('getting {0}\n'.format(setupIniPath));
            self.update(rc_file, True);

    def usage(self, cyg_apt_rc=None):
        print("{0}, version {1}".format(self.__appName, self.VERSION));
        print(copying.help_message, end="\n\n");
        if (cyg_apt_rc):
            print("Configuration: {0}".format(cyg_apt_rc));
        print("Usage: {0} [OPTION]... COMMAND [PACKAGE]...".format(
            self.__appName
        ));
        print("\n  Commands:");
        members = [];
        for m in inspect.getmembers(CygAptSetup) + inspect.getmembers(CygApt):
            if isinstance(m[1], type(self.usage)) and m[1].__doc__:
                members.append(m);

        pad = max(len(m[0]) for m in members);
        for m in members:
            print("    {0} : {1}".format(m[0].ljust(pad), m[1].__doc__));
        sys.stdout.write(
        "{LF}"
        "  Options:{LF}"
        "    -d, --download       download only{LF}"
        "    -h, --help           show brief usage{LF}"
        "    -m, --mirror=URL     use mirror{LF}"
        "    -t, --dist=NAME      set dist name (curr, test, prev){LF}"
        "    -x, --no-deps        ignore dependencies{LF}"
        "    -s, --regexp         search as regex pattern{LF}"
        "    -f, --nobarred       add/remove packages cyg-apt depends on{LF}"
        "    -X, --no-verify      do not verify setup.ini signatures{LF}"
        "    -y, --nopostinstall  do not run postinstall scripts{LF}"
        "    -z, --nopostremove   do not run preremove/postremove scripts{LF}"
        "    -q, --quiet          loggable output - no progress indicator{LF}"
        "".format(LF="\n")
        );

    def update(self, cyg_apt_rc, verify, main_mirror=None):
        """fetch current package database from mirror"""
        sig_name = None;
        self.__rc = cautils.parse_rc(cyg_apt_rc);

        if(not self.__cygwinPlatform):
            self.__pm = PathMapper(self.__rc.ROOT[:-1], False);

        if (main_mirror):
            mirror = main_mirror;
        else:
            mirror = self.__rc.mirror;

        if not mirror :
            raise UnexpectedValueException(
                "A mirror must be specified on the configuration file \"{0}\" "
                "or with the command line option \"--mirror\". "
                "See cygwin.com/mirrors.html for the list of mirrors."
                "".format(cyg_apt_rc)
            );

        if not mirror[-1] == "/":
            sep = "/";
        else:
            sep = "";

        setup_ini_names = [
            "setup.bz2",
            "setup.ini",
        ];

        bag = zip(setup_ini_names, list(range(len(setup_ini_names))));
        platform_dir = self.__arch+"/";

        for (setup_ini_name, index) in bag:
            setup_ini_url = '{0}{1}{2}{3}'.format(mirror, sep, platform_dir, setup_ini_name);
            try:
                cautils.uri_get(
                    self.__tmpDir,
                    setup_ini_url,
                    verbose=self.__verbose
                );
            except ApplicationException as e:
                # Failed to find a possible .ini
                if index == len(setup_ini_names) - 1:
                    raise e;
                else:
                    continue;
                    # Not an error to fail to find the first one
            # Take the first one we find
            break;

        if setup_ini_name[-4:] == ".bz2":
            bz_file = os.path.join(self.__tmpDir, setup_ini_name);
            f = open(bz_file, "rb");
            compressed = f.read();
            f.close();

            decomp = bz2.decompress(compressed);
            os.remove(bz_file);
            setup_ini_name = "setup.ini";

            f = open(os.path.join(self.__tmpDir, setup_ini_name), "wb");
            f.write(decomp);
            f.close();

        if not self.__cygwinPlatform:
            sys.stderr.write("WARNING can't verify setup.ini outside Cygwin.\n");
            verify = False;

        if verify:
            sig_name = "{0}.sig".format(setup_ini_name);
            sig_url = "{0}{1}{2}{3}".format(mirror, sep, platform_dir, sig_name);
            try:
                cautils.uri_get(self.__tmpDir, sig_url, verbose=self.__verbose);
            except RequestException as e:
                msg = (
                    "Failed to download signature {0} Use -X to ignore "
                    "signatures.".format(sig_url)
                );
                raise RequestException(msg, previous=e);

            if self.__cygwinPlatform:
                gpg_path = "gpg ";
            else:
                if self._cygwinVersion() < 1.7:
                    gpg_path = "/usr/bin/gpg ";
                else:
                    gpg_path = "/usr/local/bin/gpg ";
            cmd = gpg_path + "--verify --no-secmem-warning ";
            cmd += "{0}/{1} ".format(self.__tmpDir, sig_name);
            cmd += "{0}/{1} ".format(self.__tmpDir, setup_ini_name);
            p = subprocess.Popen(
                cmd,
                shell=True,
                stderr=subprocess.PIPE
            );
            p.wait();
            verify = p.stderr.read();
            if isinstance(verify, bytes):
                marker = self.GPG_GOOD_FINGER.encode();
            else:
                marker = self.GPG_GOOD_FINGER;
            if not marker in verify:
                msg = (
                    "{0} not signed by Cygwin's public key. "
                    "Use -X to ignore signatures.".format(setup_ini_url)
                );
                raise SignatureException(msg);

        downloads = os.path.join(
            self.__pm.mapPath(self.__rc.cache),
            urllib.quote(mirror+('' if mirror.endswith('/') else '/'), '').lower(),
            platform_dir,
        );

        if not os.path.exists(downloads):
            os.makedirs(downloads);

        shutil.copy(
            os.path.join(self.__tmpDir, setup_ini_name),
            os.path.join(downloads, setup_ini_name)
        );

        # BC layer for `setup_ini` configuration field
        if self.__rc.setup_ini :
            setup_ini = self.__pm.mapPath(self.__rc.setup_ini);
            if os.path.exists(setup_ini):
                shutil.copy(setup_ini, "{0}.bak".format(setup_ini));
            shutil.copy(
                os.path.join(downloads, setup_ini_name),
                setup_ini
            );

        if os.path.exists(os.path.join(self.__tmpDir, setup_ini_name)):
            os.remove(os.path.join(self.__tmpDir, setup_ini_name));
        if sig_name:
            if os.path.exists(os.path.join(self.__tmpDir, sig_name)):
                os.remove(os.path.join(self.__tmpDir, sig_name));

    def _getPre17Last(self, location):
        if not os.path.exists(os.path.join(location, "last-mirror")) \
            or not os.path.exists(os.path.join(location, "last-cache")):
            return (None, None);
        else:
            f = open(os.path.join(location, "last-cache"));
            last_cache = f.read().strip();
            f.close();
            last_cache = self.__pm.mapPath(last_cache);
            f = open(os.path.join(location, "last-mirror"));
            last_mirror = f.read().strip();
            f.close();
            return (last_cache, last_mirror);

    def _writeInstalled(self, installed_db):
        if not self.__cygwinPlatform:
            raise PlatformException(
                "fail to create {0} only supported under Cygwin."
                "".format(installed_db)
            );

        sys.stderr.write("creating {0} ... ".format(installed_db));

        db_contents = CygApt.INSTALLED_DB_MAGIC;
        cygcheck_path = self.__pm.mapPath("/bin/cygcheck");

        if os.path.exists(cygcheck_path):
            cmd = cygcheck_path + " -cd ";
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            );
            if proc.wait():
                raise ProcessException(proc.stderr.readlines());

            lines = proc.stdout.readlines();
            # remove first two lines
            pkgs = lines[2:];

            for pkg in pkgs:
                pkg = pkg.split();
                db_contents += "{0} {0}-{1}.tar.bz2 0\n".format(pkg[0], pkg[1]);

        f = open(installed_db, 'w');
        f.write(db_contents);
        f.close();

        sys.stderr.write("OK\n");

    def _gpgImport(self, uri):
        if not self.__cygwinPlatform:
            return;

        cautils.uri_get(self.__tmpDir, uri, verbose=self.__verbose);
        tmpfile = os.path.join(self.__tmpDir, os.path.basename(uri));
        cmd = "gpg ";
        cmd += "--no-secmem-warning ";
        cmd += "--import {0}".format(tmpfile);
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        );
        if p.wait():
            raise ProcessException(p.stderr.readlines());

class PlatformException(ApplicationException):
    pass;

class EnvironementException(ApplicationException):
    pass;

class SignatureException(ApplicationException):
    pass;
