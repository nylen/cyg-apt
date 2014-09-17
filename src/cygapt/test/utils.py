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

import os;
import tempfile;
import urllib;
import tarfile;
import bz2;
import hashlib;
import subprocess;
import atexit;
import time;

from cygapt.test.case import TestCase as BaseTestCase;

class TestCase(BaseTestCase):
    __mirrorDir = None;

    def setUp(self):
        BaseTestCase.setUp(self);

        self._var_tmpdir = tempfile.mkdtemp();
        self._var_old_cwd = os.getcwd();
        os.chdir(self._var_tmpdir);
        self._var_exename = "cyg-apt";
        self._var_old_env = os.environ;
        self._var_arch = "x86";

        # unix tree
        self._dir_mtroot = "{0}/".format(self._var_tmpdir);
        self._dir_tmp = os.path.join(self._dir_mtroot, "tmp");
        self._dir_prefix = os.path.join(self._dir_mtroot, "usr");
        self._dir_bin = os.path.join(self._dir_prefix, "bin");
        self._dir_sysconf = os.path.join(self._dir_mtroot, "etc");
        self._dir_localstate = os.path.join(self._dir_mtroot, "var");
        self._dir_home = os.path.join(self._dir_mtroot, "home");
        self._dir_libexec = os.path.join(self._dir_prefix, "lib");
        self._dir_data = os.path.join(self._dir_prefix, "share");
        self._dir_man = os.path.join(self._dir_data, "man");
        self._dir_info = os.path.join(self._dir_data, "info");
        self._dir_postinstall = os.path.join(self._dir_sysconf, "postinstall");
        self._dir_preremove = os.path.join(self._dir_sysconf, "preremove");
        self._dir_postremove = os.path.join(self._dir_sysconf, "postremove");

        # bulld unix tree
        os.mkdir(self._dir_tmp);
        os.mkdir(self._dir_prefix);
        os.mkdir(self._dir_bin);
        os.mkdir(self._dir_sysconf);
        os.mkdir(self._dir_localstate);
        os.mkdir(self._dir_home);
        os.mkdir(self._dir_libexec);
        os.mkdir(self._dir_data);
        os.mkdir(self._dir_man);
        os.mkdir(self._dir_info);

        self._dir_mirror = self.__getMirrorDir();
        self._var_mirror = "file://{0}".format(self._dir_mirror);
        self._var_mirror_http = "http://cygwin.uib.no/";

        # exe tree
        self._dir_confsetup = os.path.join(self._dir_sysconf, "setup");
        self._dir_user = os.path.join(self._dir_home, "user");
        self._dir_execache = os.path.join(
            self._dir_localstate,
            "cache",
            self._var_exename
        );
        self._dir_exedata = os.path.join(self._dir_data, self._var_exename);
        self._dir_downloads = os.path.join(
            self._dir_execache,
            urllib.quote(self._var_mirror, '').lower()
        );

        # build exe tree
        os.mkdir(self._dir_confsetup);
        os.mkdir(self._dir_user);
        os.mkdir(self._dir_exedata);

        # exe files
        self._file_cygwin_sig = os.path.join(
            self._dir_exedata,
            "cygwin.sig"
        );
        self._file_installed_db = os.path.join(
            self._dir_confsetup,
            "installed.db"
        );

        # BC layer for `setup_ini` configuration field
        self._file_setup_ini = os.path.join(
            self._dir_confsetup,
            "setup.ini"
        );

        self._file_setup_rc = os.path.join(
            self._dir_confsetup,
            "setup.rc"
        );
        self._file_user_config = os.path.join(
            self._dir_user,
            ".{0}".format(self._var_exename)
        );

        self._writeSetupRc();

        os.environ['TMP'] = self._dir_tmp;
        os.environ['HOME'] = self._dir_user;

        os.chdir(self._dir_user);

        # build the mirror
        self._var_setupIni = SetupIniProvider(self, self._var_arch);

    def tearDown(self):
        BaseTestCase.tearDown(self);

        os.environ = self._var_old_env;
        os.chdir(self._var_old_cwd);
        self.__rmtree(self._var_tmpdir);

    def _writeSetupRc(self, path=None):
        if None is path :
            path = self._file_setup_rc;

        f = open(path, 'w');
        f.write(
        "last-cache{LF}"
        "{2}{0}{LF}"
        "mirrors-lst{LF}"
        "{2}http://mirrors.163.com/cygwin/;mirrors.163.com;Asia;China{LF}"
        "{2}http://cygwin.uib.no/;cygwin.uib.no;Europe;Norway{LF}"
        "new-cygwin-version{LF}"
        "{2}1{LF}"
        "avahi{LF}"
        "{2}1{LF}"
        "mDNSResponder{LF}"
        "{2}1{LF}"
        "chooser_window_settings{LF}"
        "{2}44,2,3,4294935296,4294935296,4294967295,4294967295,371,316,909,709{LF}"
        "last-mirror{LF}"
        "{2}{1}{LF}"
        "net-method{LF}"
        "{2}Direct{LF}"
        "last-action{LF}"
        "{2}Download,Install{LF}"
        "".format(
            self._dir_execache,
            self._var_mirror,
            "\t",
            LF="\n"
        ));
        f.close();

    def _writeUserConfig(self, path=None, keepBC=False):
        if None is path :
            path = self._file_user_config;

        f = open(path, 'w');
        f.write("\n".join([
            "ROOT={self[_dir_mtroot]!r}",
            "mirror={self[_var_mirror]!r}",
            "cache={self[_dir_execache]!r}",

            # BC layer for `setup_ini` configuration field
            "setup_ini={self[_file_setup_ini]!r}" if keepBC else "",

            "distname='curr'",
            "barred=''",
            "always_update='False'",
            "",
        ]).format(self=vars(self)));
        f.close();

    def _writeSetupIni(self, keepBC=False):
        """Updates the `setup.ini` file for the current configuration.

        It makes the same result that the `update` command.
        """
        setupIniDir = os.path.join(self._dir_downloads, self._var_arch);
        setupIni = os.path.join(setupIniDir, "setup.ini");

        if not os.path.isdir(setupIniDir) :
            os.makedirs(setupIniDir);

        with open(setupIni, 'w') as f :
            f.write(self._var_setupIni.contents);

        if not keepBC :
            return;

        # BC layer for `setup_ini` configuration field
        with open(self._file_setup_ini, 'w') as f :
            f.write(self._var_setupIni.contents);

    @classmethod
    def __getMirrorDir(cls):
        """Gets the mirror directory.

        @return: str The mirror directory.
        """
        if None is not TestCase.__mirrorDir :
            return TestCase.__mirrorDir;

        tmpDir = tempfile.mkdtemp();
        TestCase.__mirrorDir = os.path.join(tmpDir, "mirror");

        atexit.register(cls.__rmtree, tmpDir);

        return TestCase.__mirrorDir;

    @classmethod
    def __rmtree(cls, path):
        """Removes a directory.

        @param path: str A path to a directory.
        """
        if not os.path.isdir(path) :
            return;

        files = os.listdir(path);
        for filename in files:
            subpath = os.path.join(path, filename);
            if not os.path.islink(subpath) :
                os.chmod(subpath, 0o700);
            if os.path.isdir(subpath):
                cls.__rmtree(subpath);
            else:
                os.remove(subpath);
        os.rmdir(path);

class SetupIniProvider():
    """Create a fictif setup.ini"""
    def __init__(self, app, architecture="x86"):
        assert isinstance(app, TestCase);

        self.dists = DistNameStruct();

        self._architecture = architecture;
        self._localMirror = os.path.join(app._dir_mirror, self._architecture);

        isBuilt = os.path.isdir(self._localMirror);

        packages = [
            PackageIni(app, self._architecture, name="libpkg"),
            PackageIni(app, self._architecture, name="pkg", requires="libpkg"),
            PackageIni(app, self._architecture, name="libbarredpkg"),
            PackageIni(app, self._architecture, name="barredpkg", requires="libbarredpkg"),
            PackageIni(app, self._architecture, name="pkgxz", compression="xz"),
        ];

        for package in packages :
            name = package.name;
            self.__dict__[name] = package;
            for distname in self.dists.__dict__:
                if None is self.dists.__dict__[distname] :
                    self.dists.__dict__[distname] = dict();
                self.dists.__dict__[distname][name] = package.dists.__dict__[distname].__dict__;

        if isBuilt :
            with open(os.path.join(self._localMirror, "setup.ini"), 'r' ) as f :
                self.contents = f.read();

            return;

        if not os.path.isdir(self._localMirror) :
            os.makedirs(self._localMirror);

        self.contents = "\n".join([
            "# This file is automatically generated.  If you edit it, your",
            "# edits will be discarded next time the file is generated.",
            "# See http://cygwin.com/setup.html for details.",
            "#",
            "release: cygapt.test",
            "arch: {0}",
            "setup-timestamp: {1}",
            "setup-version: 2.850",
            "",
        ]).format(
            self._architecture,
            int(time.time()),
        );

        for package in packages :
            self.contents += "\n".join([
                "",
                package.ini_contents,
                "",
            ]);

        self._buildMirror();

    def getArchitecture(self):
        return self._architecture;

    def _buildMirror(self):
        setup_ini = os.path.join(self._localMirror, "setup.ini");
        setup_bz2 = os.path.join(self._localMirror, "setup.bz2");

        f = open(setup_ini, 'w');
        f.write(self.contents);
        f.close();

        open(setup_ini+".sig", 'w').close();

        compressed = bz2.compress(self.contents.encode());
        f = open(setup_bz2, 'wb');
        f.write(compressed);
        f.close();

        open(setup_bz2+".sig", 'w').close();

        # Add a README file for the mirror
        readmePath = os.path.join(self._localMirror, "README.md");
        f = open(readmePath, 'w');
        f.write("\n".join([
            "The mirror has been auto-generated by the `cygapt.test.utils.TestCase` class.",
            "",
            "For update it just delete the parent directory of the current file.",
            "",
        ]));
        f.close();

class PackageIni():
    def __init__(self, app, arch, name="testpkg", category="test", requires="", compression="bz2"):
        assert isinstance(app, TestCase);

        self._localMirror = app._dir_mirror;
        self._tmpdir = app._dir_tmp;
        self._compression = compression;
        self._generated = False;

        self.name = name;
        self.category = category;
        self.requires = requires;

        self.shortDesc = "\"Short description for {0}\"".format(self.name);
        self.longDesc = "\"Long description\nfor {0}\"".format(self.name);

        self.pkgPath = os.path.join(arch, "test", self.name);

        self.filelist = [];

        self.install = DistNameStruct();
        self.install.curr = FileStruct();
        self.install.prev = FileStruct();
        self.install.test = FileStruct();

        self.source = DistNameStruct();
        self.source.curr = FileStruct();
        self.source.prev = FileStruct();
        self.source.test = FileStruct();

        self.version = DistNameStruct();
        self.ini_contents = "";
        self.dists = DistsStruct();

        self.build();

    def build(self):
        mirror_pkg_dir = os.path.join(self._localMirror, self.pkgPath);
        self._generated = os.path.exists(mirror_pkg_dir);
        if not self._generated :
            os.makedirs(mirror_pkg_dir);

        self._buildDist();
        self._buildPkg();
        self._buildDists();
        self._buildIniContents();

    def _buildDist(self):
        self.version.prev = "1.0.1-1";
        self.version.curr = "2.0.1-1";
        self.version.test = "3.0.1-1";

        for distname in self.install.__dict__:
            tarball = "{0}-{1}.tar.{2}".format(
                self.name,
                self.version.__dict__[distname],
                self._compression,
            );
            self.install.__dict__[distname].url = os.path.join(
                self.pkgPath,
                tarball
            );

        for distname in self.source.__dict__:
            srctarball = "{0}-{1}.src.tar.{2}".format(
                self.name,
                self.version.__dict__[distname],
                self._compression,
            );
            self.source.__dict__[distname].url = os.path.join(
                self.pkgPath,
                srctarball
            );

    def _buildIniContents(self):
        self.ini_contents = (
        "@ {self[name]}{LF}"
        "sdesc: {self[shortDesc]}{LF}"
        "ldesc: {self[longDesc]}{LF}"
        "category: {self[category]}{LF}"
        "requires: {self[requires]}{LF}"
        "version: {self[version][curr]}{LF}"
        "install: {self[install][curr]}{LF}"
        "source: {self[source][curr]}{LF}"
        "[prev]{LF}"
        "version: {self[version][prev]}{LF}"
        "install: {self[install][prev]}{LF}"
        "source: {self[source][prev]}{LF}"
        "[test]{LF}"
        "version: {self[version][test]}{LF}"
        "install: {self[install][test]}{LF}"
        "source: {self[source][test]}"
        "".format(self=vars(self), LF="\n")
        );

    def _buildDists(self):
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].category = self.category;
            self.dists.__dict__[distname].ldesc = self.longDesc;
            self.dists.__dict__[distname].sdesc = self.shortDesc;
            self.dists.__dict__[distname].requires = self.requires;

        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].version = self.version.__dict__[distname];
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].install = self.install.__dict__[distname].toString();
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].source = self.source.__dict__[distname].toString();

    def _buildPkg(self):
        for distname in self.dists.__dict__:
            self._buildDistFiles(distname);

    def _buildDistFiles(self, distname='curr'):
        # create build directory
        if not self._generated :
            self._generateDistFiles(distname);

        tar_name = os.path.join(self._localMirror, self.install.__dict__[distname].url);
        tar_src_name = os.path.join(self._localMirror, self.source.__dict__[distname].url);

        md5sum = self._md5Sum(tar_name);
        md5sum_src = self._md5Sum(tar_src_name);

        self.install.__dict__[distname].size = self._fileSize(tar_name);
        self.source.__dict__[distname].size = self._fileSize(tar_src_name);
        self.install.__dict__[distname].md5 = md5sum;
        self.source.__dict__[distname].md5 = md5sum_src;

        self.filelist = self._getFileList(distname);

    def _generateDistFiles(self, distname='curr'):
        dirname = os.path.join(self._tmpdir, self.name + self.version.__dict__[distname]);
        os.makedirs(dirname);
        usr_d = os.path.join(dirname, "usr");
        etc_d = os.path.join(dirname, "etc");
        var_d = os.path.join(dirname, "var");
        bin_d = os.path.join(dirname, "usr", "bin");
        postinstall_d = os.path.join(dirname, "etc", "postinstall");
        postremove_d = os.path.join(dirname, "etc", "postremove");
        preremove_d = os.path.join(dirname, "etc", "preremove");
        marker_d = os.path.join(dirname, "var", self.name);
        os.makedirs(bin_d);
        os.makedirs(postinstall_d);
        os.makedirs(postremove_d);
        os.makedirs(preremove_d);
        os.makedirs(marker_d);
        bin_f = os.path.join(bin_d, self.name);
        link_bin_f = os.path.join(bin_d, self.name + "-link");
        hardlink_bin_f = os.path.join(bin_d, self.name + "-hardlink");
        postinstall_f = os.path.join(postinstall_d, self.name + ".sh");
        postremove_f = os.path.join(postremove_d, self.name + ".sh");
        preremove_f = os.path.join(preremove_d, self.name + ".sh");
        marker_f = os.path.join(marker_d, "version");

        # create exec "#!/usr/bin/sh\necho running;" <pkg> > root/usr/bin
        #    link
        #    hard link
        f = open(bin_f, 'w');
        f.write('#!/bin/sh\necho "running";');
        f.close();
        ret = 0;
        ret += os.system('ln -s "' + self.name + '" "' + link_bin_f + '"');
        ret += os.system('ln "' + bin_f + '" "' + hardlink_bin_f + '"');
        if ret > 0:
            raise OSError("fail to create links");

        # create postinstall > root/etc/postinstall
        f = open(postinstall_f, 'w');
        f.write(
        "#!/bin/sh{LF}"
        "exit 0;{LF}"
        "".format(LF="\n")
        );
        f.close();
        # create preremove > root/etc/postremove
        f = open(preremove_f, 'w');
        f.write(
        "#!/bin/sh{LF}"
        "exit 0;{LF}"
        "".format(LF="\n")
        );
        f.close();
        # create postremmove > root/etc/preremmove
        f = open(postremove_f, 'w');
        f.write(
        "#!/bin/sh{LF}"
        "exit 0;{LF}"
        "".format(LF="\n")
        );
        f.close();
        # create version marker > root/var/<pkg>/<version>
        f = open(marker_f, 'w');
        f.write(self.version.__dict__[distname]);
        f.close();
        # build install tar
        tar_name = os.path.join(
            self._localMirror,
            self.install.__dict__[distname].url
        );
        tarInstallPath = ".".join(tar_name.split(".")[:-1]);
        tar = tarfile.open(tarInstallPath, mode='w');
        for name in [usr_d, etc_d, var_d]:
            tar.add(name, os.path.basename(name));
        members = tar.getmembers();
        tar.close();
        self._compressFollowingTargetExtension(tarInstallPath, tar_name);
        del tarInstallPath;

        # Force slash to the end of each directories
        lst = [];
        for m in members:
            if m.isdir() and not m.name.endswith("/"):
                lst.append(m.name + "/");
            else:
                lst.append(m.name);
        f = open("{0}.lst".format(tar_name), 'w');
        f.write("\n".join(lst));
        f.close();

        # build source tar
        tar_src_name = os.path.join(
            self._localMirror,
            self.source.__dict__[distname].url
        );
        tarSrcPath = ".".join(tar_src_name.split(".")[:-1]);
        tar = tarfile.open(tarSrcPath, mode='w');
        tar.add(dirname, "{0}-{1}".format(
            self.name,self.version.__dict__[distname]
        ));
        tar.close();
        self._compressFollowingTargetExtension(tarSrcPath, tar_src_name);
        del tarSrcPath;

        md5sum = self._md5Sum(tar_name);
        md5sum_src = self._md5Sum(tar_src_name);

        md5_sum_f = os.path.join(os.path.dirname(tar_name), "md5.sum");

        f = open(md5_sum_f, 'a');
        f.write(
        "{0}  {1}{LF}"
        "{2}  {3}{LF}"
        "".format(
            md5sum,
            os.path.basename(self.install.__dict__[distname].url),
            md5sum_src,
            os.path.basename(self.source.__dict__[distname].url),
            LF="\n"
        ));
        f.close();

    def _compressFollowingTargetExtension(self, srcPath, targetPath):
        compression = targetPath.split(".")[-1];
        if "bz2" == compression :
            f = open(srcPath, 'rb');
            contents = f.read();
            compressed = bz2.compress(contents);
            f.close();
            f = open(targetPath, 'wb');
            f.write(compressed);
            f.close();
            os.remove(srcPath);
        elif "xz" == compression :
            subprocess.check_call(['xz', '-f', srcPath]);

    def _md5Sum(self, path):
        """Generate the md5sum from a file.

        @param path: str The path to a file for unsed to generate md5sum.

        @return: str The resulted md5sum.
        """
        f = open(path, 'rb');
        content = f.read();
        f.close();

        return hashlib.md5(content).hexdigest();

    def _fileSize(self, path):
        """Determine the file size for the specified path.

        @param path: str The path to check the file size.

        @return: integer The file size.
        """
        return long(os.path.getsize(path));

    def _getFileList(self, distname):
        """Gets file list from a distribution.

        @param distname: str The distribution name.

        @return: list A list of paths that contains the given distribution.
        """
        tar_name = os.path.join(self._localMirror, self.install.__dict__[distname].url);

        f = open("{0}.lst".format(tar_name), 'r');
        contents = f.read();
        f.close();

        lst = contents.split("\n");

        return lst;

class DistNameStruct():
    def __init__(self):
        self.curr = None;
        self.prev = None;
        self.test = None;

    def __getitem__(self, key):
        return self.__dict__[key];

class DistStruct():
    def __init__(self):
        self.category = None;
        self.sdesc = None;
        self.ldesc = None;
        self.requires = None;
        self.version = None;
        self.install = None;
        self.source = None;

class DistsStruct(DistNameStruct):
    def __init__(self):
        self.curr = DistStruct();
        self.prev = DistStruct();
        self.test = DistStruct();

class FileStruct():
    def __init__(self):
        self.url = "";
        self.size = "1024";
        self.md5 = "md5";

    def __str__(self):
        return self.toString();

    def __repr__(self):
        return self.toString();

    def toString(self):
        ball = "{0} {1} {2}".format(
            self.url,
            self.size,
            self.md5
        );
        return ball;
