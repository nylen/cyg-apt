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

import gzip;
import hashlib;
import io;
import os;
import re;
import shutil;
import sys;
import urllib;
import tempfile;

import cygapt.utils as cautils;
from cygapt.exception import ApplicationException;
from cygapt.exception import InvalidFileException;
from cygapt.exception import InvalidArgumentException;
from cygapt.exception import UnexpectedValueException;
from cygapt.path_mapper import PathMapper;
from cygapt.structure import ConfigStructure;
from cygapt.process import Process;

class CygApt:
    INSTALLED_DB_MAGIC = "INSTALLED.DB 2\n";
    DIST_NAMES = ('curr', 'test', 'prev');
    FORCE_BARRED = ["python", "python-argparse", "gnupg", "xz"];
    SH_OPTIONS = " --norc --noprofile ";
    DASH_OPTIONS = " ";
    CMD_OPTIONS = " /V:ON /E:ON /C ";
    CYG_POSTINSTALL_DIR = "/etc/postinstall";
    CYG_PREREMOVE_DIR = "/etc/preremove";
    CYG_POSTREMOVE_DIR = "/etc/postremove";

    def __init__(self,
        main_packagename,
        main_files,
        main_cyg_apt_rc,
        main_cygwin_p,
        main_download_p,
        main_mirror,
        main_downloads,
        main_distname,
        main_nodeps_p,
        main_regex_search,
        main_nobarred,
        main_nopostinstall,
        main_nopostremove,
        main_dists,
        main_installed,
        main_scriptname,
        main_verbose,
        arch,
        setupDir="/etc/setup",
    ):

        # Define private properties
        self.__ballTarget = 'install';
        self.__regexSearch = main_regex_search;
        self.__noBarred = main_nobarred;
        self.__noPostInstall = main_nopostinstall;
        self.__noPostRemove = main_nopostremove;
        self.__appName = main_scriptname;
        self.__files = main_files;
        self.__downloadOnly = main_download_p;
        self.__downloadDir = main_downloads;
        self.__noDeps = main_nodeps_p;
        self.__rcFile = main_cyg_apt_rc;
        self.__verbose = main_verbose;
        self.__setupDir = setupDir;
        self.__rc = ConfigStructure();
        self.__setupIniPath = None;
        self.__arch = arch;

        # Init
        self.setPkgName(main_packagename);
        self.setCygwinPlatform(main_cygwin_p);
        self.setDists(main_dists);
        self.setInstalled(main_installed);

        # Read in our configuration
        self.getRessource(self.__rcFile);

        # Now we have a path mapper, check setup.exe is not running
        self._checkForSetupExe();

        # DOS specific
        if not self.__cygwinPlatform:
            self.__lnExists = os.path.exists(
                "{0}/bin/ln.exe".format(self.__prefixRoot)
            );
        else:
            self.__lnExists = True;

        # Overrides to the .rc
        if (main_mirror):
            self.__rc.mirror = main_mirror;
            self.__downloadDir = os.path.join(
                self.__rc.cache,
                urllib.quote(self.__rc.mirror+('' if self.__rc.mirror.endswith('/') else '/'), '').lower()
            );

        if (main_distname):
            self.__rc.distname = main_distname;

        if not (os.path.isfile(self.__installedDbFile) \
                or os.path.isfile(self.__setupIniPath)):
            msg = "{0} no such file, run {1} setup?".format(
                self.__installedDbFile,
                self.__appName
            );
            raise PackageCacheException(msg);
        else:
            self._getSetupIni();
            self.getInstalled();

    def getPkgName(self):
        return self.__pkgName;

    def setPkgName(self, pkg_name):
        self.__pkgName = str(pkg_name);

    def getCygwinPlatform(self):
        return self.__cygwinPlatform;

    def setCygwinPlatform(self, cygwin_p):
        self.__cygwinPlatform = bool(cygwin_p);

    def getDownloadDir(self):
        return self.__downloadDir;

    def setDownlaodDir(self, download_dir):
        self.__downloadDir = str(download_dir);

    def getDists(self):
        return self.__dists;

    def setDists(self, dists):
        self.__dists = dists;

    def getSetupDir(self):
        return self.__setupDir;

    def setSetupDir(self, setup_dir):
        self.__setupDir = str(setup_dir);

    def getInstalledDbFile(self):
        return self.__installedDbFile;

    def setInstalledDbFile(self, installed_db_file):
        self.__installedDbFile = str(installed_db_file);

    def getDosBash(self):
        return self.__dosBash;

    def setDosBash(self, dos_bash):
        self.__dosBash = str(dos_bash);

    def getDosLn(self):
        return self.__dosLn;

    def setDosLn(self, dos_ln):
        self.__dosLn = str(dos_ln);

    def getDosXz(self):
        return self.__dosXz;

    def setDosXz(self, dos_xz):
        self.__dosXz = str(dos_xz);

    def getDosDash(self):
        return self.__dosDash;

    def setDosDash(self, dosDash):
        self.__dosDash = str(dosDash);

    def getPrefixRoot(self):
        return self.__prefixRoot;

    def setPrefixRoot(self, prefix_root):
        self.__prefixRoot = prefix_root;

    def getAbsRoot(self):
        return self.__absRoot;

    def setAbsRoot(self, absolute_root):
        self.__absRoot = absolute_root;

    def getPathMapper(self):
        return self.__pm;

    def setPathMapper(self, path_mapper):
        assert isinstance(path_mapper, PathMapper);
        self.__pm = path_mapper;

    def getRC(self):
        return self.__rc;

    def setRC(self, rc_structure):
        assert isinstance(rc_structure, ConfigStructure);
        self.__rc = rc_structure;

    def _checkForSetupExe(self):
        # It's far from bulletproof, but it's surprisingly hard to detect
        # setup.exe running since it doesn't lock any files.
        p = Process(self.__pm.mapPath("/bin/ps -W"));
        p.run();
        psout = p.getOutput().splitlines(True);
        setup_re = re.compile(r"(?<![a-z0-9_ -])setup(|-1\.7|-x86|-x86_64)\.exe", re.IGNORECASE);
        for l in psout:
            m = setup_re.search(l);
            if m:
                raise AppConflictException(
                    "Please close {0} while "
                    "running {1}".format(m.group(0), self.__appName)
                );

    def _versionToString(self, t):
        def try_itoa(x):
            if isinstance(x, int):
                return "{0:d}".format(x);
            return x
        return "{0}-{1}".format(
            ".".join(list(map(try_itoa, t[:-1]))),
            t[-1]
        );

    def _stringToVersion(self, s):
        s = re.sub(r"([^0-9][^0-9]*)", " \\1 ", s);
        s = re.sub(r"[ _.-][ _.-]*", " ", s);
        def try_atoi(x):
            if re.match(r"^[0-9]*$", x):
                return int(x);
            return x
        return tuple(map(try_atoi, (s.split(' '))));

    def _splitBall(self, p):
        m = re.match(r"^(.*)-([0-9].*-[0-9]+)(.tar.(bz2|xz))?$", p);
        if not m:
            print("splitBall: {0}".format(p));
            return (p[:2], (0, 0));
        t = (m.group(1), self._stringToVersion(m.group(2)));
        return t;

    def _joinBall(self, t):
        return "{0}-{1}".format(t[0], self._versionToString(t[1]));

    def _debug(self, s):
        s;

    def help(self,):
        """this help message"""
        pass;

    def _getSetupIni(self):
        if self.__dists:
            return;
        self.__dists = {'test': {}, 'curr': {}, 'prev' : {}};
        f = open(self.__setupIniPath);
        contents = f.read();
        f.close();
        chunks = contents.split("\n\n@ ");
        for i in chunks[1:]:
            lines = i.split("\n");
            name = lines[0].strip();
            self._debug("package: {0}".format(name));
            packages = self.__dists['curr'];
            records = {'sdesc': name};
            j = 1;
            while j < len(lines) and lines[j].strip():
                self._debug("raw: {0}".format(lines[j]));
                if lines[j][0] == '#':
                    j = j + 1;
                    continue;
                elif lines[j][0] == '[':
                    self._debug('dist: {0}'.format(lines[j][1:5]));
                    packages[name] = records.copy();
                    packages = self.__dists[lines[j][1:5]];
                    j = j + 1;
                    continue;

                duo = lines[j].split(": ", 1);
                key = duo[0].strip();
                value = duo[1].strip();

                if value.find('"') != -1 \
                   and value.find('"', value.find('"') + 1) == -1:
                    while True:
                        j = j + 1;
                        value += "\n" + lines[j];
                        if lines[j].find('"') != -1:
                            break;
                records[key] = value;
                j = j + 1;
            packages[name] = records;

    def _getUrl(self):
        if self.__pkgName not in self.__dists[self.__rc.distname] \
           or self.__ballTarget not in self.__dists[self.__rc.distname][self.__pkgName]:
            self._printErr(self._noPackage());
            install = 0;
            for d in self.DIST_NAMES:
                if self.__pkgName in self.__dists[d] \
                   and self.__ballTarget in self.__dists[d][self.__pkgName]:
                    install = self.__dists[d][self.__pkgName][self.__ballTarget];
                    print("warning: using [{0}]\n".format(d), file=sys.stderr);
                    break;
            if not install:
                raise PackageException("{0} is not in {1}".format(
                    self.__pkgName,
                    self.__setupIniPath
                ));
        else:
            install = self.__dists[self.__rc.distname][self.__pkgName][self.__ballTarget];
        filename, size, md5 = install.split();
        return filename, md5;

    def url(self):
        """print tarball url"""
        if not self.__pkgName:
            raise CommandLineException("url command requires a package name");
        print("{0}/{1}".format(self.__rc.mirror, self._getUrl()[0]));

    def getBall(self):
        url, md5 = self._getUrl();
        return os.path.join(self.__downloadDir, url);

    def ball(self):
        """print tarball name"""
        print(self.getBall());

    def _doDownload(self):
        url, md5 = self._getUrl();
        directory = os.path.join(self.__downloadDir, os.path.split(url)[0]);
        if not os.path.exists(self.getBall()) or not self._checkMd5():
            if not os.path.exists(directory):
                os.makedirs(directory);
            status = cautils.uri_get(
                directory,
                "{0}/{1}".format(self.__rc.mirror, url)
            );
            if status:
                raise PackageCacheException(
                    "didn't find {0} "
                    "on mirror {1}: possible mismatch between setup.ini and "
                    "mirror requiring {2} update?".format(
                    self.__pkgName,
                    self.__rc.mirror,
                    self.__appName
                ));

    def download(self):
        """download package (only, do not install)"""
        self._doDownload();
        self.ball();
        self.checksum();

    def _noPackage(self):
        return "{0} is not on mirror {1} in [{2}].".format(
            self.__pkgName,
            self.__rc.mirror,
            self.__rc.distname
        );

    # return an array contents all dependencies of self.__pkgName
    def getRequires(self):
        # Looking for dependencies on curr not prev or test
        dist = self.__dists['curr'];
        if self.__pkgName not in self.__dists[self.__rc.distname]:
            raise PackageException(self._noPackage());
        if self.__noDeps:
            return [];
        reqs = {self.__pkgName:0};
        if self.__ballTarget == 'source' \
            and 'external-source' in dist[self.__pkgName]:
            reqs[dist[self.__pkgName]['external-source']] = 0;
        n = 0;
        while len(reqs) > n:
            n = len(reqs);
            for i in list(reqs.keys()):
                if i not in dist:
                    sys.stderr.write("error: {0} not in [{1}]\n".format(
                        i, self.__rc.distname
                    ));
                    if i != self.__pkgName:
                        del reqs[i];
                    continue;
                reqs[i] = '0';
                p = dist[i];
                if 'requires' not in p:
                    continue;
                update_list = [(x, 0) for x in p['requires'].split()];
                reqs.update(update_list);
        # Delete the ask package it is not require by it self (joke)
        reqs.pop(self.__pkgName);
        rlist = sorted(reqs.keys());
        return rlist;

    def requires(self):
        """print requires: for package"""
        reqs = self.getRequires();
        if len(reqs) == 0:
            print("No dependencies for package {0}".format(self.__pkgName));
        else:
            print("\n".join(reqs));

    def getInstalled(self):
        if self.__installed:
            return self.__installed;
        self.__installed = {0:{}};
        f = open(self.__installedDbFile);
        lines = f.readlines();
        f.close();
        for i in lines[1:]:
            name, ball, status = i.split();
            self.__installed[int(status)][name] = ball;
        return self.__installed;

    def setInstalled(self, installed):
        self.__installed = installed;

    def _writeInstalled(self):
        file_db = open(self.__installedDbFile, 'w');
        file_db.write(self.INSTALLED_DB_MAGIC);
        lines = [];
        for x in list(self.__installed[0].keys()):
            lines.append("{0} {1} 0\n".format(x, self.__installed[0][x]));
        file_db.writelines(lines);
        if file_db.close():
            raise IOError(self.__installedDbFile);

    def getField(self, field, default=''):
        for d in (self.__rc.distname,) + self.DIST_NAMES:
            if self.__pkgName in self.__dists[d] \
               and field in self.__dists[d][self.__pkgName]:
                return self.__dists[d][self.__pkgName][field];
        return default;

    def _psort(self, lst):
        lst.sort();
        return lst;

    def _preverse(self, lst):
        lst.reverse();
        return lst;

    def list(self):
        """list installed packages"""
        print("--- Installed packages ---");
        for self.__pkgName in self._psort(list(self.__installed[0].keys())):
            ins = self.getInstalledVersion();
            new = 0;
            if self.__pkgName in self.__dists[self.__rc.distname] \
               and self.__ballTarget in self.__dists[self.__rc.distname][self.__pkgName]:
                new = self.getVersion();
            s = "{0:<19} {1:<15}".format(
                self.__pkgName,
                self._versionToString(ins)
            );
            if new and new != ins:
                s += "({0})".format(self._versionToString(new));
            print(s);

    def filelist(self):
        """list files installed by given packages"""
        if not self.__pkgName:
            msg = "no package name given.";
            raise CommandLineException(msg);
        else:
            print("\n".join(self.getFileList()));

    def _postInstall(self):
        self._runAll(self.CYG_POSTINSTALL_DIR);

    def _postRemove(self):
        if len(self.__files[1:]) == 0:
            msg = "must specify package to run postremove.";
            raise CommandLineException(msg);
        else:
            for self.__pkgName in self.__files[1:]:
                preremove_sh = os.path.join(
                    self.CYG_PREREMOVE_DIR,
                    "{0}.sh".format(self.__pkgName)
                );
                postremove_sh = os.path.join(
                    self.CYG_POSTREMOVE_DIR,
                    "{0}.sh".format(self.__pkgName)
                );
                self._runScript(preremove_sh);
                self._runScript(postremove_sh);

    def getVersion(self):
        if self.__pkgName not in self.__dists[self.__rc.distname] \
           or self.__ballTarget not in self.__dists[self.__rc.distname][self.__pkgName]:
            self._printErr(self._noPackage());
            return (0, 0);
        package = self.__dists[self.__rc.distname][self.__pkgName];
        if 'ver' not in package:
            filename = package[self.__ballTarget].split()[0];
            ball = os.path.split(filename)[1];
            package['ver'] = self._splitBall(ball)[1];
        return package['ver'];

    def getInstalledVersion(self):
        return self._splitBall(self.__installed[0][self.__pkgName])[1];

    def version(self):
        """print installed version"""
        if self.__pkgName:
            if self.__pkgName not in self.__installed[0]:
                msg = "{0} is not installed".format(self.__pkgName);
                raise PackageException(msg);
            print(self._versionToString(self.getInstalledVersion()));
        else:
            for self.__pkgName in self._psort(list(self.__installed[0].keys())):
                if self.__pkgName not in self.__installed[0]:
                    self.__rc.distname = 'installed';
                    raise PackageException(self._noPackage());
                print("{0:<20}{1:<12}".format(
                    self.__pkgName,
                    self._versionToString(self.getInstalledVersion())
                ));

    def getNew(self):
        lst = [];
        for self.__pkgName in list(self.__installed[0].keys()):
            new = self.getVersion();
            ins = self.getInstalledVersion();
            if new > ins:
                self._debug(" {0} > {1}".format(new, ins));
                lst.append(self.__pkgName);
        return lst;

    def new(self):
        """list new (upgradable) packages in distribution"""
        for self.__pkgName in self._psort(self.getNew()):
            print("{0:<20}{1:<12}".format(
                self.__pkgName,
                self._versionToString(self.getVersion())
            ));

    def getMd5(self):
        url, md5 = self._getUrl();
        f = open(os.path.join(self.__downloadDir, url), 'rb');
        data = f.read();
        f.close();
        m = hashlib.md5();
        if 64 == len(md5) :
            m = hashlib.sha256();
        if 128 == len(md5) :
            m = hashlib.sha512();
        m.update(data);
        digest = m.hexdigest();
        return digest;

    def _checkMd5(self):
        return self._getUrl()[1] == self.getMd5();

    def checksum(self):
        """check digest of cached package against database"""
        if not os.path.exists(self.getBall()):
            msg = "{0} not downloaded.".format(self.__pkgName);
            raise PackageCacheException(msg);
        url, md5 = self._getUrl();
        ball = os.path.basename(url);
        print("{0}  {1}".format(md5, ball));
        actual_md5 = self.getMd5();
        print("{0}  {1}".format(actual_md5, ball));
        if actual_md5 != md5:
            raise HashException(
                "digest of cached package doesn't match digest "
                "in setup.ini from mirror"
            );

    def search(self):
        """search all package descriptions for string"""
        if not self.__pkgName:
            raise CommandLineException(
                "search command requires a string to search for"
            );
        if not self.__regexSearch:
            regexp = re.escape(self.__pkgName);
        else:
            regexp = self.__pkgName;
        packages = [];
        keys = [];
        if self.__rc.distname in self.__dists:
            keys = list(self.__dists[self.__rc.distname].keys());
        else:
            for i in list(self.__dists.keys()):
                for j in list(self.__dists[i].keys()):
                    if not j in keys:
                        keys.append(j);
        for i in keys:
            self.__pkgName = i;
            if not regexp or re.search(regexp, i) \
               or re.search(regexp, self.getField('sdesc'), re.IGNORECASE) \
               or re.search(regexp, self.getField('ldesc'), re.IGNORECASE):
                if self.__rc.distname in self.__dists:
                    if self.__ballTarget in self.__dists[self.__rc.distname][i]:
                        packages.append(i);
                else:
                    packages.append(i);
        for self.__pkgName in self._psort(packages):
            s = self.__pkgName;
            d = self.getField('sdesc');
            if d:
                s += " - {0}".format(d[1:-1]);
            print(s);

    def show(self):
        """print package description"""
        s = self.__pkgName;
        d = self.getField('sdesc');
        if d:
            s += ' - {0}'.format(d[1:-1]);
        ldesc = self.getField('ldesc');
        if ldesc != "":
            print(s + "\n");
            print(ldesc);
        else:
            print("{0}: not found in setup.ini: {1}".format(
                self.__appName,
                s
            ));

    # return an array with all packages that must to be install
    def getMissing(self):
        reqs = self.getRequires();
        missingreqs = [];  # List of missing package on requires list
        for i in reqs:
            if i not in self.__installed[0]:
                missingreqs.append(i);
        if self.__pkgName not in self.__installed[0]:
            missingreqs.append(self.__pkgName);
        if missingreqs and self.__pkgName not in missingreqs:
            sys.stderr.write("warning: missing packages: {0}\n".format(
                " ".join(missingreqs)
            ));
        elif self.__pkgName in self.__installed[0]:  # Check version
            ins = self.getInstalledVersion();
            new = self.getVersion();
            if ins >= new:
                sys.stderr.write("{0} is already the newest version\n".format(
                    self.__pkgName
                ));
                # missingreqs.remove(self.__pkgName)
            elif self.__pkgName not in missingreqs:
                missingreqs.append(self.__pkgName);
        return missingreqs;

    def missing(self):
        """print missing dependencies for package"""
        missing = self.getMissing();
        if len(missing) > 0:
            print("\n".join(missing));
        else:
            print("All dependent packages for {0} installed".format(
                self.__pkgName
            ));

    def _runScript(self, file_name, optional=True):
        mapped_file = self.__pm.mapPath(file_name);
        mapped_file_done = mapped_file + ".done";
        if os.path.isfile(mapped_file):
            sys.stderr.write("running: {0}\n".format(file_name));
            if self.__cygwinPlatform:
                cmd = " ".join([
                    "bash",
                    self.SH_OPTIONS,
                    mapped_file
                ]);
            else:
                cmd = " ".join([
                    self.__dosBash,
                    self.SH_OPTIONS,
                    mapped_file
                ]);

            cwd = None;
            extension = os.path.splitext(mapped_file)[1];

            if ".dash" == extension :
                cmd = ["dash", self.DASH_OPTIONS, mapped_file];
                if not self.__cygwinPlatform:
                    cmd[0] = self.__dosDash;
                cmd = " ".join(cmd);

            if extension in [".bat", ".cmd"] :
                cmd = " ".join(["cmd", self.CMD_OPTIONS, os.path.basename(mapped_file)]);
                cwd = os.path.dirname(mapped_file);

            retval = Process(cmd, cwd).run(True);

            if os.path.exists(mapped_file_done):
                os.remove(mapped_file_done);
            if retval == 0 and os.path.basename(file_name)[:3] not in ['0p_', 'zp_']:
                shutil.move(mapped_file, mapped_file_done);
        else:
            if not optional:
                sys.stderr.write("{0}: WARNING couldn't find {1}.\n".format(
                    self.__appName,
                    mapped_file
                ));

    def _runAll(self, dirname):
        dirname = self.__pm.mapPath(dirname);

        if os.path.isdir(dirname):
            lst = list();
            for filename in os.listdir(dirname) :
                if os.path.splitext(filename)[1] in ['.sh', '.dash', '.bat', '.cmd'] :
                    lst.append(filename);

            perpetualScripts = list();
            regularScripts = list();
            for filename in lst:
                if filename[:3] in ['0p_', 'zp_'] :
                    perpetualScripts.append(filename);
                else:
                    regularScripts.append(filename);

            perpetualScripts.sort();
            lst = perpetualScripts + regularScripts;

            for i in lst:
                self._runScript("{0}/{1}".format(dirname, i));

    def _doInstallExternal(self, ball):
        # Currently we use a temporary directory and extractall() then copy:
        # this is very slow. The Python documentation warns more sophisticated
        # approaches have pitfalls without specifying what they are.
        tf = cautils.open_tarfile(ball, self.__dosXz);
        members = tf.getmembers();
        tempdir = tempfile.mkdtemp();
        try:
            tf.extractall(tempdir);
            for m in members:
                if m.isdir():
                    path = self.__pm.mapPath("/" + m.name);
                    if not os.path.exists(path):
                        os.makedirs(path, m.mode);
            for m in members:
                if m.isdir():
                    path = self.__pm.mapPath("/" + m.name);
                    if not os.path.exists(path):
                        os.makedirs(path, m.mode);
                else:
                    path = self.__pm.mapPath("/" + m.name);
                    dirname = os.path.dirname(path);
                    if not os.path.exists(dirname):
                        os.makedirs(dirname);
                    if os.path.exists(path):
                        os.chmod(path, 0o777);
                        os.remove(path);
                    # Windows extract() is robust but can't form Cygwin links
                    # (It produces copies instead: bulky and bugbait.)
                    # Convert to links if possible -- depends on coreutils being installed
                    if m.issym() and self.__lnExists:
                        link_target = m.linkname;
                        Process(" ".join([
                            self.__dosLn,
                            "-s",
                            link_target,
                            path
                        ])).run(True);
                    elif m.islnk() and self.__lnExists:
                        # Hard link -- expect these to be very rare
                        link_target = m.linkname;
                        mapped_target = self.__pm.mapPath("/" + m.linkname);
                        # Must ensure target exists before forming hard link
                        if not os.path.exists(mapped_target):
                            shutil.move(
                                os.path.join(tempdir, link_target),
                                mapped_target
                            );
                        Process(" ".join([
                            self.__dosLn,
                            mapped_target,
                            path
                        ])).run(True);
                    else:
                        shutil.move(os.path.join(tempdir, m.name), path);
        finally:
            tf.close();
            cautils.rmtree(tempdir);

    def _doInstall(self):
        ball = self.getBall();
        if cautils.is_tarfile(ball):
            if not self.__cygwinPlatform:
                self._doInstallExternal(ball);
            tf = cautils.open_tarfile(ball, self.__dosXz);
            if self.__cygwinPlatform:
                tf.extractall(self.__absRoot);
            # Force slash to the end of each directories
            members = tf.getmembers();
            tf.close();
            lst = [];
            for m in members:
                if m.isdir() and not m.name.endswith("/"):
                    lst.append(m.name + "/");
                else:
                    lst.append(m.name);
        else:
            print("{0}: bad tarball {1}. Install failed.".format(
                self.__appName,
                ball
            ), file=sys.stderr);
            return;
        self._writeFileList(lst);

        status = 1;
        if not self.__pkgName in self._integrityControl():
            status = 0;
        self.__installed[status][self.__pkgName] = os.path.basename(ball);

        self._writeInstalled();

    def getFileList(self):
        filelist_file = os.path.join(
            self.__setupDir,
            "{0}.lst.gz".format(self.__pkgName)
        );
        if not os.path.exists(filelist_file):
            if self.__pkgName not in self.__installed[0]:
                raise PackageException(
                    "{0} is not installed".format(self.__pkgName)
                );
            else:
                raise PackageException(
                    "{0} is installed, but {1} is missing".format(
                    self.__pkgName,
                    filelist_file
                ));
        gzf = gzip.GzipFile(filelist_file);
        lst = gzf.readlines();
        gzf.close();
        lst = [x.decode().strip() for x in lst];
        return lst;

    def _touch(self, fname, times=None):
        f = open(fname, 'a');
        os.utime(fname, times);
        f.close();

    def _writeFileList(self, lst):
        gz_filename = os.path.join(
            self.__setupDir,
            "{0}.lst.gz".format(self.__pkgName)
        );

        lst_cr = [x + "\n" for x in lst];

        # create iostring and write in gzip
        lst_io = io.BytesIO();
        lst_io_gz = gzip.GzipFile(fileobj=lst_io, mode='w');
        lst_io_gz.writelines([x.encode() for x in lst_cr]);
        lst_io_gz.close();

        # save it in the file
        lst_gz = open(gz_filename, 'wb');
        lst_gz.write(lst_io.getvalue());
        lst_gz.close();
        lst_io.close();

        stat_struct = os.stat(self.__setupIniPath);
        atime = stat_struct[7];
        mtime = stat_struct[8];
        self._touch(gz_filename, (atime, mtime));

    def _removeFileList(self):
        lst_name = os.path.join(
            self.__setupDir,
            "{0}.lst.gz".format(self.__pkgName)
        );
        if os.path.exists(lst_name):
            os.remove(lst_name);
        else:
            sys.stderr.write("{0}: warning {1} no such file\n".format(
                 sys.argv[0], lst_name
            ));

    def _uninstallWantFileRemoved(self, filename, noremoves, nowarns):
        # Returns true if the path from the tarball should result in a file 
        # removal operation, false if not.
        if not os.path.exists(filename) and not os.path.islink(filename):
            if filename not in nowarns:
                sys.stderr.write("warning: {0} no such file\n".format(
                    filename
                ));
            return False;
        elif not os.path.isdir(filename) and filename not in noremoves:
            return True;

    def _doUninstall(self):
        postremove_sh = "{0}/{1}.sh".format(
            self.CYG_POSTREMOVE_DIR,
            self.__pkgName
        );
        postinstall_sh = "{0}/{1}.sh".format(
            self.CYG_POSTINSTALL_DIR,
            self.__pkgName
        );
        preremove_sh = "{0}/{1}.sh".format(
            self.CYG_PREREMOVE_DIR,
            self.__pkgName
        );

        postinstall_done = "{0}.done".format(postinstall_sh);
        suppression_msg = (
            "{0}: postremove suppressed: "
            "\"{0} postremove {1}\" to complete.".format(
            self.__appName,
            self.__pkgName
        ));

        lst = self.getFileList();
        expect_preremove = preremove_sh[1:] in lst;
        expect_postremove = postremove_sh[1:] in lst;

        if not self.__noPostRemove:
            if expect_preremove:
                self._runScript(preremove_sh, optional=False);
        else:
            print("{0}".format(suppression_msg),
                  file=sys.stderr);

        # We don't expect these to be present: they are executed
        # and moved to $(packagename).sh.done
        nowarns = [];
        nowarns.append(self.__pm.mapPath(postinstall_sh));
        nowarns.append(self.__pm.mapPath(preremove_sh));

        noremoves = [];
        if self.__noPostRemove:
            noremoves.append(self.__pm.mapPath(preremove_sh));
        noremoves.append(self.__pm.mapPath(postremove_sh));

        # remove files
        for i in lst:
            filename = self.__pm.mapPath("/" + i);
            if os.path.islink(filename):
                os.remove(filename);
                continue;
            if os.path.isdir(filename):
                continue;
            if (self._uninstallWantFileRemoved(filename, noremoves, nowarns)):
                if os.path.exists(filename):
                    if self.__cygwinPlatform:
                        os.chmod(filename, 0o777);
                    if os.remove(filename):
                        raise IOError(filename);
                else:
                    if os.path.islink(filename):
                        os.remove(filename);
                    else:
                        print(
                            "{0}: warning: expected to remove {1} but it was"
                            " not there.".format(
                            self.__appName,
                            filename
                        ));
        if not self.__noPostRemove:
            if expect_postremove:
                self._runScript(postremove_sh, optional=False);
            postremove_sh_mapped = self.__pm.mapPath(postremove_sh)
            if os.path.isfile(postremove_sh_mapped):
                if os.remove(postremove_sh_mapped):
                    raise IOError(postremove_sh_mapped);

        # We don't remove empty directories: the problem is are we sure no other
        # package is depending on them.

        # setup.exe removes the filelist when a package is uninstalled: we try to be
        # as much like setup.exe as possible
        self._removeFileList();

        # Clean up the postintall script: it's been moved to .done
        if os.path.isfile(self.__pm.mapPath(postinstall_done)):
            os.remove(self.__pm.mapPath(postinstall_done));

        # update installed[]
        del(self.__installed[0][self.__pkgName]);
        self._writeInstalled();

    def remove(self):
        """uninstall packages"""
        barred = [];
        for self.__pkgName in self.__files[1:]:
            if self.__pkgName not in self.__installed[0]:
                sys.stderr.write("warning: {0} not installed\n".format(
                    self.__pkgName
                ));
                continue;
            if self._isBarredPackage(self.__pkgName):
                barred.append(self.__pkgName);
                continue;
            sys.stderr.write("uninstalling {0} {1}\n".format(
                self.__pkgName,
                self._versionToString(self.getInstalledVersion())
            ));
            self._doUninstall();
        self._barredWarnIfNeed(barred, "removing");

    def purge(self):
        """uninstall packages and delete from cache"""
        barred = [];

        for self.__pkgName in self.__files[1:]:
            if self.__pkgName in self.__installed[0]:
                if self._isBarredPackage(self.__pkgName):
                    barred.append(self.__pkgName);
                    continue;
                sys.stderr.write("uninstalling {0} {1}\n".format(
                    self.__pkgName,
                    self._versionToString(self.getInstalledVersion())
                ));
                self._doUninstall();
            scripts = [
                self.CYG_POSTINSTALL_DIR + "/{0}.sh.done",
                self.CYG_PREREMOVE_DIR + "/{0}.sh.done",
                self.CYG_POSTREMOVE_DIR + "/{0}.sh.done"
            ];
            scripts = [s.format(self.__pkgName) for s in scripts];
            scripts = [self.__pm.mapPath(s) for s in scripts];
            for s in scripts:
                if os.path.exists(s):
                    os.remove(s);
            ball = self.getBall();
            if os.path.exists(ball):
                print("{0}: removing {1}".format(self.__appName, ball));
                os.remove(ball);

        self._barredWarnIfNeed(barred, "purging");

    def _barredWarnIfNeed(self, barred, command):
        num_barred = len(barred);
        if num_barred > 0:
            if num_barred == 1:
                this_these = "this package";
            else:
                this_these = "these packages";
            barredstr = ", ".join(barred);
            helpfull = "";
            close_all_cygwin_programs = "";
            if command == "installing":
                helpfull += (
"You can force the installation with the option -f. But it is recommended\n"
"to upgrade the Cygwin distribution, with the official Setup program\n"
"(e.g., setup.exe)."
                );
                if "_autorebase" in barred:
                    close_all_cygwin_programs += (
"\n"
"Before that, you must close all Cygwin programs to perform rebasing\n"
"(e.g., rebaseall)."
                    );
            print(
                "BarredWarning: NOT {1}:"
                "    {2}\n{0} is dependent on {3} under Cygwin."
                "{4}{5}".format(
                    self.__appName,
                    command,
                    barredstr,
                    this_these,
                    helpfull,
                    close_all_cygwin_programs
            ), file=sys.stderr);
            if not self.__cygwinPlatform:
                print(
                    "Use -f to override but proceed with caution.",
                    file=sys.stderr
                );
    def install(self):
        """download and install packages with dependencies"""
        suppression_msg = (
            "{0}: postinstall suppressed: "
            "\"{0} postinstall\" to complete.".format(
            self.__appName
        ));
        missing = {};
        barred = [];
        for self.__pkgName in self.__files[1:]:
            missing.update(dict([(x, 0) for x in self.getMissing()]));

        if len(missing) > 1:
            sys.stderr.write("to install: \n");
            sys.stderr.write("    {0}".format(" ".join(list(missing.keys()))));
            sys.stderr.write("\n");

        for self.__pkgName in list(missing.keys()):
            if not self._getUrl():
                del missing[self.__pkgName];

        for self.__pkgName in list(missing.keys()):
            if self._isBarredPackage(self.__pkgName):
                barred.append(self.__pkgName);
                del missing[self.__pkgName];

        for self.__pkgName in list(missing.keys()):
            self.download();
        if self.__downloadOnly:
            return;
        for self.__pkgName in list(missing.keys()):
            if self.__pkgName in self.__installed[0]:
                sys.stderr.write("preparing to replace {0} {1}\n".format(
                    self.__pkgName,
                    self._versionToString(self.getInstalledVersion())
                ));
                self._doUninstall();
            sys.stderr.write("installing {0} {1}\n".format(
                self.__pkgName,
                self._versionToString(self.getVersion())
            ));
            self._doInstall();

        if self.__noPostInstall:
            print(suppression_msg, file=sys.stderr);
        else:
            self._postInstall();

        self._barredWarnIfNeed(barred, "installing");

    def postinstall(self):
        """Executes all undone postinstall scripts."""
        self._postInstall();

    def postremove(self):
        """Executes all undone preremove and postremove scripts."""
        self._postRemove();

    def _integrityControl(self, checklist=[]):
        options = "-c ";
        if self.__verbose:
            options += "-v ";

        if len(checklist) == 0:
            checklist.append(self.__pkgName);

        pkg_lst = " ".join(checklist);
        command = '';
        if not self.__cygwinPlatform:
            command += self.__dosBash + ' ' + self.SH_OPTIONS;
            command += " -c ";
            command += "'";
        command += "/bin/cygcheck ";
        command += options;
        command += pkg_lst;
        if not self.__cygwinPlatform:
            command += "'";

        p = Process(command);
        p.run();
        outputlines = p.getOutput().splitlines(True);

        unformat = "";
        start = False;
        incomplete = [];
        for res in outputlines:
            try:
                res_split = res.split();
                package, version, status = res_split;
            except ValueError:
                if len(res_split) > 0:
                    unformat += res;
                continue;

            if package == 'Package' \
               and version == 'Version' \
               and status == 'Status':
                start = True;
                unformat = '';
            elif not start:
                continue;

            if start and status == 'Incomplete':
                print(res[:-2]);
                print(unformat);
                unformat = "";
                incomplete.append(package);

        return incomplete;

    def upgrade(self):
        """all installed packages"""
        self.__files[1:] = self.getNew();
        self.install();

    def _printErr(self, err):
        print("{0}: {1}".format(self.__appName, err), file=sys.stderr);

    def _doUnpack(self):
        ball = self.getBall();
        basename = os.path.basename(ball);
        self.__pkgName = re.sub(r"(-src)*\.tar\.(bz2|gz)", '', basename);
        if os.path.exists(self.__pkgName):
            self._printErr("{0} already exists. Not overwriting.".format(
                self.__pkgName
            ));
            return 1;
        os.mkdir(self.__pkgName);
        if cautils.is_tarfile(ball):
            tf = cautils.open_tarfile(ball, self.__dosXz);
            tf.extractall(self.__pkgName);
            tf.close();
        else:
            raise InvalidFileException(
                "Bad source tarball {0}, \n"
                "SOURCE UNPACK FAILED".format(ball)
            );
        if not os.path.exists(self.__pkgName):
            raise IOError(self.__pkgName);
        print(self.__pkgName);

    def source(self):
        """download source package"""
        self.__ballTarget = 'source';
        for self.__pkgName in self.__files[1:]:
            self.download();
            self._doUnpack();

    def find(self):
        """find package containing file"""
        if self.__regexSearch:
            file_to_find = self.__pkgName;
        else:
            file_to_find = re.escape(self.__pkgName);
        hits = [];
        for self.__pkgName in self._psort(list(self.__installed[0].keys())):
            filenames_file = os.path.join(
                self.__setupDir,
                "{0}.lst.gz".format(self.__pkgName)
            );
            if not os.path.exists(filenames_file):
                continue;
            files = self.getFileList();
            for i in files:
                if re.search(file_to_find, "/{0}".format(i)):
                    hits.append("{0}: /{1}".format(self.__pkgName, i));
        print("\n".join(hits));

    def setRoot(self, root):
        if len(root) < 1 or root[-1] != "/":
            raise InvalidArgumentException("ROOT must end in a slash.");
        self.__prefixRoot = root[:-1];
        self.__absRoot = root;

    def getRessource(self, filename):
        self.__rc = cautils.parse_rc(filename);

        if not self.__rc.cache:
            msg = "{0} doesn't define cache.".format(self.__rcFile);
            raise UnexpectedValueException(msg);
        if not self.__rc.mirror:
            msg = "{0} doesn't define mirror.".format(self.__rcFile);
            raise UnexpectedValueException(msg);

        # We want ROOT + "/etc/setup" and cd(ROOT) to work:
        # necessitates two different forms, prefix and absolute
        if(self.__cygwinPlatform):
            self.setRoot("/");
        else:
            self.setRoot(self.__rc.ROOT);
        self.__rc.ROOT = None;
        self.__pm = PathMapper(self.__prefixRoot, self.__cygwinPlatform);
        self.__setupDir = self.__pm.mapPath(self.__setupDir);
        self.__rc.cache = self.__pm.mapPath(self.__rc.cache);
        self.__downloadDir = os.path.join(
            self.__rc.cache,
            urllib.quote(self.__rc.mirror+('' if self.__rc.mirror.endswith('/') else '/'), '').lower()
        );
        self.__installedDbFile = os.path.join(self.__setupDir, "installed.db");

        self.__setupIniPath = os.path.join(
            self.__downloadDir,
            self.__arch,
            "setup.ini",
        );
        self.__dosBash = "{0}bin/bash".format(self.__pm.getMountRoot());
        self.__dosLn = "{0}bin/ln".format(self.__pm.getMountRoot());
        self.__dosXz = self.__pm.mapPath("/usr/bin/xz");
        self.__dosDash = "{0}bin/dash".format(self.__pm.getMountRoot());
        return 0;

    def _isBarredPackage(self, package):
        barred = [];
        # add user barred package
        barred.extend(self.__rc.barred.split());
        # add force barred package
        barred.extend(self.FORCE_BARRED);

        # store current package name
        curr_pkgname = self.__pkgName;

        # get barred package requires
        depbarred = [];
        for self.__pkgName in barred:
            try:
                depbarred.extend(self.getRequires());
            except PackageException:
                pass;

        barred.extend(depbarred);

        # set current package name
        self.__pkgName = curr_pkgname;

        return (not self.__noBarred) and package in barred;

class AppConflictException(ApplicationException):
    pass;

class CommandLineException(ApplicationException):
    pass;

class PackageException(ApplicationException):
    pass;

class HashException(ApplicationException):
    pass;

class PackageCacheException(ApplicationException):
    pass;
