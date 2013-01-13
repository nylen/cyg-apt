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
import bz2
import inspect
import os
import re
import shutil
import subprocess
import sys
import urllib
import platform

from cygapt import CygApt
from error import CygAptError
from path_mapper import PathMapper
import utils as cautils

class CygAptSetup:
    def __init__(self, cygwin_p, verbose):
        self.cygwin_p = cygwin_p
        self.verbose = verbose
        self.rc_options = ['ROOT', 'mirror', 'cache', 'setup_ini', 'distname',\
            'barred', 'always_update']
        self.rc_comments = {\
            "ROOT" : "# The root of your Cygwin installation as a windows path\n",\
            "mirror" : "# URL of your Cygwin mirror: example "\
            "http://mirror.internode.on.net/pub/cygwin/\n",\
            "cache" : "# Your package cache as a POSIX path: example "\
            "/e/home/cygwin_package_cache\n",\
            "setup_ini" : "# setup.ini lists available packages and is "\
            "downloaded from the top level\n"\
            "# of the downloaded mirror. Standard location is "\
            "/etc/setup/setup.ini,\n"\
            "# seutp-2.ini for Cygwin 1.7 Beta\n",\
            "distname" : "# The distribution, current previous or test "\
            "[curr, prev, test].\n"\
            "# Usually you want the \"curr\" version of a package.\n",\
            "barred" : "# Packages which cyg-apt can't change under Cygwin "\
            "since it depends on them.\n"\
            "# Run cyg-apt under DOS with -f (force) option to change "\
            "these packages.\n"\
            "# Treat Cygwin core packages with CAUTION.\n",\
            "always_update" : "# Always update setup.ini before any command"\
            " that uses it. cyg-apt will be\n# faster and use less bandwidth if"\
            " False but you will have to run the update\n# command manually.\n"
            }
        self.sn = os.path.basename(sys.argv[0])
        self.rc_regex = re.compile("^\s*(\w+)\s*=\s*(.*)\s*$")
        if 'TMP' in os.environ:
            self.tmpdir = os.environ['TMP']
        else:
            self.tmpdir = "/usr/share/cyg-apt"
        self.gpg_good_sig_msg = "1169 DF9F 2273 4F74 3AA5  9232 A9A2 62FF 6760 41BA"
        #self.gpg_good_sig_msg = "Good signature"
        self.pm = PathMapper("", self.cygwin_p)
        self.ROOT = self.pm.mountroot
        self.ABSOLUTE_ROOT = self.ROOT
        self.config = '/etc/setup'
        self.cygwin_pubring_uri = "http://cygwin.com/key/pubring.asc"
        self.installed_db_magic = 'INSTALLED.DB 2\n'

    def set_verbose(self, verbose):
        self.verbose = verbose

    def get_setup_rc(self, location):
        if not (os.path.exists(location + "/" + "setup.rc")):
            return (None, None)
        f = open(location + "/" + "setup.rc");
        setup_rc = f.readlines()
        f.close();
        last_cache = None
        last_mirror = None
        for i in range(0, (len(setup_rc) -1)):
            if "last-cache" in setup_rc[i]:
                last_cache = setup_rc[i+1].strip()
            if "last-mirror" in setup_rc[i]:
                last_mirror = setup_rc[i+1].strip()
        last_cache = cautils.cygpath(last_cache)
        return (last_cache, last_mirror)

    def setup(self, force=False):
        """create cyg-apt configuration file, it overwrite with -f option"""
        if not self.cygwin_p:
            print("{0}: setup outside Cygwin not supported. Exiting.".format(self.sn))
            sys.exit(1)
        if "HOME" in os.environ:
            self.cyg_apt_rc = os.environ['HOME'] + '/.' + self.sn
        else:
            sys.stderr.write("{0}: can't locate home directory. Setup "\
                "failed, exiting.\n".format(self.sn))
            sys.exit(1)
        if os.path.exists(self.cyg_apt_rc) and not force:
            sys.stderr.write("{0}: {1} exists, not overwriting. "\
                "\n".format(self.sn, self.cyg_apt_rc))
            sys.exit(0)


        installed_db = self.config + '/installed.db'
        missing_cache_marker = ""
        missing_mirror_marker = ""
        self.distname = "curr"
        # Refuse to remove/install any package including these substrings
        # since cyg-apt is dependent on them
        self.barred = ""
        self.always_update = False

        if not self.cygwin_p:
            print("{0}: settup only supported under Cygwin."\
                  "Exiting.".format(self.sn))
            return

        (last_cache, last_mirror) = self.get_setup_rc(self.config)
        if ((not last_cache) or (not last_mirror)):
            (last_cache, last_mirror) = self.get_pre17_last(self.config)
            if ((not last_cache) or (not last_mirror)):
                print("{0}: {1}/setup.rc not found. Please edit {2} to "\
                "provide mirror and cache.".format(self.sn, self.config, self.cyg_apt_rc))
                last_cache = missing_cache_marker
                last_mirror  = missing_mirror_marker
        self.mirror = last_mirror
        self.cache = last_cache

        cygwin_version = platform.release()[:3]
        self.setup_ini = self.config + "/setup.ini"
        self.cygwin_version = float(cygwin_version)

        contents = "";
        for i in self.rc_options:
            if i in list(self.rc_comments.keys()):
                contents += self.rc_comments[i];
            contents += '{0}="{1}"\n\n'.format(i, eval("self." + i))
        f = open(self.cyg_apt_rc, "w");
        f.write(contents);
        f.close();
        print("{0}: creating {1}".format(self.sn, self.cyg_apt_rc))

        if not os.path.isdir(self.ABSOLUTE_ROOT):
            sys.stderr.write('error: {0} no root dir\n'.format(self.ABSOLUTE_ROOT))
            sys.exit(2)
        if not os.path.isdir(self.config):
            sys.stderr.write('creating {0}\n'.format(self.config))
            os.makedirs(self.config)
        if not os.path.isfile(installed_db):
            self.write_installed(installed_db)
        if not os.path.isfile(self.setup_ini):
            sys.stderr.write('getting {0}\n'.format(self.setup_ini))
            self.update(self.cyg_apt_rc, True)

    def usage(self, cyg_apt_rc=None):
        print("{0} [OPTION]... COMMAND [PACKAGE]...".format(self.sn))
        if (cyg_apt_rc):
            print(("Configuration: {0}".format(cyg_apt_rc)))
        print("\n  Commands:")
        members = [m
                for m in inspect.getmembers(CygAptSetup) + inspect.getmembers(CygApt)
                if isinstance(m[1], type(self.usage)) and m[1].__doc__]
        pad = max(len(m[0]) for m in members)
        for m in members:
            print("    " + m[0].ljust(pad) + " : " + m[1].__doc__)
        sys.stdout.write(r"""
  Options:
    -d, --download       download only
    -h, --help           show brief usage
    -m, --mirror=URL     use mirror
    -t, --dist=NAME      set dist name (curr, test, prev)
    -x, --no-deps        ignore dependencies
    -s, --regexp         search as regex pattern
    -f, --nobarred       add/remove packages cyg-apt depends on
    -X, --no-verify      do not verify setup.ini signatures
    -y, --nopostinstall  do not run postinstall scripts
    -z, --nopostremove   do not run preremove/postremove scripts
    -q, --quiet          Loggable output - no progress indicator.
""")

    def update(self, cyg_apt_rc, verify, main_mirror=None):
        """fetch current package database from mirror"""
        rc = {}
        sig_name = None
        f = open(cyg_apt_rc);
        lines = f.readlines();
        f.close();
        for i in lines:
            result = self.rc_regex.search(i)
            if result:
                k = result.group(1)
                v = result.group(2)
                if k in self.rc_options:
                    rc[k] = eval(v)

        if(not self.cygwin_p):
            self.pm = PathMapper(rc["ROOT"][:-1], False)

        setup_ini = self.pm.map_path(rc["setup_ini"])
        if (main_mirror):
            mirror = main_mirror
        else:
            mirror = rc["mirror"]
        downloads = self.pm.map_path(rc["cache"]) + '/' + urllib.quote(mirror, '').lower()
        if not mirror[-1] == "/":
            sep = "/"
        else:
            sep = ""

        setup_ini_names = [os.path.basename(setup_ini).replace(".ini", ".bz2"),\
            os.path.basename(setup_ini)]

        for (setup_ini_name, index) in zip(setup_ini_names, list(range(len(setup_ini_names)))):
            setup_ini_url = '{0}{1}{2}'.format(mirror, sep, setup_ini_name)
            err = None
            try:
                cautils.uri_get(self.tmpdir, setup_ini_url, verbose=self.verbose)
            except CygAptError as xxx_todo_changeme:
                # Failed to find a possible .ini
                (err) = xxx_todo_changeme
                # Failed to find a possible .ini
                if index == len(setup_ini_names) - 1:
                    sys.stderr.write(self.sn + ": " + err.msg +\
                    ", exiting.\n")
                    sys.exit(1)
                else:
                    continue
                    # Not an error to fail to find the first one
            # Take the first one we find
            break

        if setup_ini_name[-4:] == ".bz2":
            f = open(self.tmpdir + "/" + setup_ini_name, "rb");
            compressed = f.read();
            f.close();

            decomp = bz2.decompress(compressed)
            os.remove(self.tmpdir + "/" + setup_ini_name)
            setup_ini_name =  os.path.basename(setup_ini)

            f = open(self.tmpdir + "/" + setup_ini_name, "wb");
            f.write(decomp);
            f.close();

        if not self.cygwin_p:
            sys.stderr.write("WARNING can't verify setup.ini outside Cygwin.\n")
            verify = False

        if verify:
            sig_name = setup_ini_name + ".sig"
            sig_url = "{0}{1}{2}".format(mirror, sep, sig_name)
            err = cautils.uri_get(self.tmpdir, sig_url, verbose=self.verbose)
            if err:
                print("{0}: failed to download signature {1} Use -X to ignore "\
                    "signatures. Exiting".format(
                    self.sn, sig_url))
                sys.exit(1)
            if self.cygwin_p:
                gpg_path = "gpg "
            else:
                if self.cygwin_version < 1.7:
                    gpg_path = "/usr/bin/gpg "
                else:
                    gpg_path = "/usr/local/bin/gpg "
            cmd = gpg_path + "--verify --no-secmem-warning "
            cmd += self.tmpdir + "/" + sig_name + " "
            cmd += self.tmpdir + "/" + setup_ini_name
            p = subprocess.Popen(cmd, shell=True,
                    stderr=subprocess.PIPE);
            p.wait();
            verify = p.stderr.read();
            if isinstance(verify, bytes):
                marker = self.gpg_good_sig_msg.encode();
            else:
                marker = self.gpg_good_sig_msg;
            if not marker in verify:
                sys.stderr.write("{0}: {1} not signed by Cygwin's public key. "\
                    "Use -X to ignore signatures. Exiting.\n".format(
                    self.sn, setup_ini_url))
                sys.exit(1)

        if not os.path.exists(downloads):
            os.makedirs(downloads)

        shutil.copy(self.tmpdir + "/" + setup_ini_name, downloads + "/" +\
                    setup_ini_name)
        if os.path.exists(setup_ini):
            shutil.copy(setup_ini, setup_ini + ".bak")
        shutil.copy(downloads + "/" + setup_ini_name, setup_ini)
        if os.path.exists(self.tmpdir + "/" + setup_ini_name):
            os.remove(self.tmpdir + "/" + setup_ini_name)
        if sig_name:
            if os.path.exists(self.tmpdir + "/" + sig_name):
                os.remove(self.tmpdir + "/" + sig_name)

    def get_pre17_last(self, location):
        if not os.path.exists(location + "/last-mirror" or\
            not os.path.exists(location + "/last-cache")):
            return (None, None)
        else:
            f = open(location + "/last-cache");
            last_cache = f.read().strip()
            f.close();
            last_cache = cautils.cygpath(last_cache)
            f = open(location + "/last-mirror");
            last_mirror = f.read().strip()
            f.close();
            return (last_cache, last_mirror)

    def write_installed(self, installed_db):
        if not self.cygwin_p:
            print("{0}: fail to create {1} only supported under Cygwin. "\
                  "Exiting.".format(self.sn, installed_db))
            return

        sys.stderr.write('creating {0} ... '.format(installed_db))

        db_contents = self.installed_db_magic
        cygcheck_path = self.pm.map_path("/bin/cygcheck")

        if os.path.exists(cygcheck_path):
            cmd = cygcheck_path + " -cd "
            proc = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)

            if proc.wait():
                raise CygAptError(proc.stderr.readlines())

            lines = proc.stdout.readlines()
            # remove first two lines
            pkgs = lines[2:]

            for pkg in pkgs:
                pkg = pkg.split()
                db_contents += "{0} {0}-{1}.tar.bz2 0\n".format(pkg[0], pkg[1])


        f = open(installed_db, "w");
        f.write(db_contents)
        f.close();

        sys.stderr.write("OK\n")

    def gpg_import(self, uri):
        if not self.cygwin_p:
            return

        cautils.uri_get(self.tmpdir, uri, verbose=self.verbose)
        tmpfile = os.path.join(self.tmpdir, os.path.basename(uri))
        cmd = "gpg "
        cmd += "--no-secmem-warning "
        cmd += "--import {0}".format(tmpfile)
        p = subprocess.Popen(cmd, shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

        if p.wait():
            raise CygAptError(p.stderr.readlines())
