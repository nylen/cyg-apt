"""
"""

from __future__ import print_function
import unittest
import os
import tempfile
import urllib
import tarfile
import bz2
import hashlib

class TestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self._var_tmpdir = tempfile.mkdtemp()
        self._var_old_cwd = os.getcwd()
        os.chdir(self._var_tmpdir)
        self._var_exename = "cyg-apt"
        self._var_old_env = os.environ

        # unix tree
        self._dir_mtroot = self._var_tmpdir + "/"
        self._dir_tmp = os.path.join(self._dir_mtroot, "tmp")
        self._dir_prefix = os.path.join(self._dir_mtroot, "usr")
        self._dir_bin = os.path.join(self._dir_prefix, "bin")
        self._dir_sysconf = os.path.join(self._dir_mtroot, "etc")
        self._dir_localstate = os.path.join(self._dir_mtroot, "var")
        self._dir_home = os.path.join(self._dir_mtroot, "home")
        self._dir_libexec = os.path.join(self._dir_prefix, "lib")
        self._dir_data = os.path.join(self._dir_prefix, "share")
        self._dir_man = os.path.join(self._dir_data, "man")
        self._dir_info = os.path.join(self._dir_data, "info")
        self._dir_postinstall = os.path.join(self._dir_sysconf, "postinstall");
        self._dir_preremove = os.path.join(self._dir_sysconf, "preremove");
        self._dir_postremove = os.path.join(self._dir_sysconf, "postremove");

        # bulld unix tree
        os.mkdir(self._dir_tmp)
        os.mkdir(self._dir_prefix)
        os.mkdir(self._dir_bin)
        os.mkdir(self._dir_sysconf)
        os.mkdir(self._dir_localstate)
        os.mkdir(self._dir_home)
        os.mkdir(self._dir_libexec)
        os.mkdir(self._dir_data)
        os.mkdir(self._dir_man)
        os.mkdir(self._dir_info)

        self._dir_mirror = os.path.join(self._dir_mtroot, "_tcm");
        self._var_mirror = "file://" + self._dir_mirror;
        self._var_mirror_http = "http://cygwin.xl-mirror.nl/";

        # exe tree
        self._dir_confsetup = os.path.join(self._dir_sysconf, "setup")
        self._dir_user = os.path.join(self._dir_home, "user")
        self._dir_execache = os.path.join(self._dir_localstate, "cache",
                                          self._var_exename)
        self._dir_exedata = os.path.join(self._dir_data, self._var_exename)
        self._dir_downloads = os.path.join(self._dir_execache,
                                           urllib.quote(self._var_mirror, '').lower())
        # build exe tree
        os.mkdir(self._dir_confsetup)
        os.mkdir(self._dir_user)
        os.mkdir(self._dir_exedata)
        os.makedirs(self._dir_mirror);

        # exe files
        self._file_cygwin_sig = os.path.join(self._dir_exedata,
                                               "cygwin.sig")
        self._file_installed_db = os.path.join(self._dir_confsetup,
                                               "installed.db")
        self._file_setup_ini = os.path.join(self._dir_confsetup,
                                               "setup.ini")
        self._file_setup_rc = os.path.join(self._dir_confsetup,
                                               "setup.rc")
        self._file_user_config = os.path.join(self._dir_user,
                                               "." + self._var_exename)

        f = open(self._file_setup_rc, "w");
        f.write(r"""
last-cache
{2}{0}
mirrors-lst
{2}http://mirrors.163.com/cygwin/;mirrors.163.com;Asia;China
{2}http://cygwin.mirrors.hoobly.com/;cygwin.mirrors.hoobly.com;United States;Pennsylvania
{2}http://cygwin.xl-mirror.nl/;cygwin.xl-mirror.nl;Europe;Netherlands
new-cygwin-version
{2}1
avahi
{2}1
mDNSResponder
{2}1
chooser_window_settings
{2}44,2,3,4294935296,4294935296,4294967295,4294967295,371,316,909,709
last-mirror
{2}{1}
net-method
{2}Direct
last-action
{2}Download,Install
""".format(self._dir_execache, self._var_mirror_http, "\t"))
        f.close();

        os.environ['TMP'] = self._dir_tmp
        os.environ['HOME'] = self._dir_user

        os.chdir(self._dir_user);

        self._var_setupIni = SetupIniProvider(self);

    def tearDown(self):
        unittest.TestCase.tearDown(self)

        os.environ = self._var_old_env
        os.chdir(self._var_old_cwd)
        def rmtree(path):
            files = os.listdir(path)
            for filename in files:
                subpath = os.path.join(path, filename)
                if os.path.isdir(subpath):
                    rmtree(subpath)
                else:
                    os.remove(subpath)
            os.rmdir(path)
        rmtree(self._var_tmpdir)

class SetupIniProvider():
    """Create a fictif setup.ini"""
    def __init__(self, app):
        if not isinstance(app, TestCase):
            raise Exception();
        self._localMirror = app._dir_mirror;

        self.libpkg = PackageIni(app, name="libpkg");
        self.pkg = PackageIni(app, name="pkg", requires="libpkg");
        self.libbarredpkg = PackageIni(app, name="libbarred");
        self.barredpkg = PackageIni(app, name="barred", requires="libbarred");

        self.contents = r"""
# This file is automatically generated.  If you edit it, your
# edits will be discarded next time the file is generated.
# See http://cygwin.com/setup.html for details.
#
setup-timestamp: 1356999079
setup-version: 2.774

{pkg}

{libpkg}

{libbarred}

{barred}
""".format(pkg=self.pkg.ini_contents,
           libpkg=self.libpkg.ini_contents,
           libbarred=self.libbarredpkg.ini_contents,
           barred=self.barredpkg.ini_contents,)

        self._buildMirror();

        self.dists = DistNameStruct()
        
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname] = {self.pkg.name: self.pkg.dists.__dict__[distname].__dict__,
                                             self.libpkg.name: self.libpkg.dists.__dict__[distname].__dict__,
                                             self.libbarredpkg.name: self.libbarredpkg.dists.__dict__[distname].__dict__,
                                             self.barredpkg.name: self.barredpkg.dists.__dict__[distname].__dict__,}

    def _buildMirror(self):
        setup_ini = os.path.join(self._localMirror, "setup.ini");
        setup_bz2 = os.path.join(self._localMirror, "setup.bz2");

        f = open(setup_ini, "w");
        f.write(self.contents);
        f.close();

        compressed = bz2.compress(self.contents.encode());
        f = open(setup_bz2, "wb");
        f.write(compressed);
        f.close();

class PackageIni():
    def __init__(self, app, name="testpkg", category="test", requires=""):
        if not isinstance(app, TestCase):
            raise Exception();

        self._localMirror = app._dir_mirror;
        self._mtRoot = app._dir_mtroot;
        self._tmpdir = app._dir_tmp;

        self.name = name;
        self.category = category;
        self.requires = requires;

        self.shortDesc = "\"Short description for " + self.name + "\""
        self.longDesc = "\"Long description\nfor " + self.name + "\""

        self.pkgPath = os.path.join("test", self.name);

        self.filelist = [];

        self.install = DistNameStruct()
        self.install.curr = FileStruct()
        self.install.prev = FileStruct()
        self.install.test = FileStruct()

        self.source = DistNameStruct()
        self.source.curr = FileStruct()
        self.source.prev = FileStruct()
        self.source.test = FileStruct()

        self.version = DistNameStruct()
        self.ini_contents = ""
        self.dists = DistsStruct()

        self.build();

    def build(self):
        self._build_dist()
        self._buildPkg();
        self._build_dists();
        self._build_ini_contents();

    def _build_dist(self):
        self.version.prev = "1.0.1-1"
        self.version.curr = "2.0.1-1"
        self.version.test = "3.0.1-1"

        for distname in self.install.__dict__:
            self.install.__dict__[distname].url = os.path.join(
                            self.pkgPath,
                            self.name + \
                                "-"+ \
                                self.version.__dict__[distname] + \
                                ".tar.bz2");

        for distname in self.source.__dict__:
            self.source.__dict__[distname].url = os.path.join(
                            self.pkgPath,
                            self.name + \
                                "-"+ \
                                self.version.__dict__[distname] + \
                                ".src.tar.bz2");

    def _build_ini_contents(self):
        self.ini_contents = r"""@ {self[name]}
sdesc: {self[shortDesc]}
ldesc: {self[longDesc]}
category: {self[category]}
requires: {self[requires]}
version: {self[version][curr]}
install: {self[install][curr]}
source: {self[source][curr]}
[prev]
version: {self[version][prev]}
install: {self[install][prev]}
source: {self[source][prev]}
[test]
version: {self[version][test]}
install: {self[install][test]}
source: {self[source][test]}""".format(self=vars(self));

    def _build_dists(self):
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].category = self.category
            self.dists.__dict__[distname].ldesc = self.longDesc
            self.dists.__dict__[distname].sdesc = self.shortDesc
            self.dists.__dict__[distname].requires = self.requires

        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].version = self.version.__dict__[distname]
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].install = self.install.__dict__[distname].toString()
        for distname in self.dists.__dict__:
            self.dists.__dict__[distname].source = self.source.__dict__[distname].toString()

    def _buildPkg(self):
        for distname in self.dists.__dict__:
            self._buildDistFiles(distname);

    def _buildDistFiles(self, distname="curr"):
        # create build directory
        mirror_pkg_dir = os.path.join(self._localMirror, self.pkgPath);
        if not os.path.exists(mirror_pkg_dir):
            os.makedirs(mirror_pkg_dir);

        dirname = os.path.join(self._tmpdir, self.name + self.version.__dict__[distname]);
        os.makedirs(dirname);
        usr_d = os.path.join(dirname, "usr");
        etc_d = os.path.join(dirname, "etc");
        var_d = os.path.join(dirname, "var");
        bin_d = os.path.join(dirname, "usr", "bin");
        postinstall_d = os.path.join(dirname, "etc", "postinstall");
        postremove_d = os.path.join(dirname, "etc", "postremove");
        preremove_d = os.path.join(dirname, "etc", "preremove");
        sys_marker_d = os.path.join(self._mtRoot, "var", self.name);
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
        f = open(bin_f, "w");
        f.write('#!/usr/bin/sh\necho "running";');
        f.close();
        ret = 0;
        ret += os.system('ln -s "' + bin_f + '" "' + link_bin_f + '"')
        ret += os.system('ln "' + bin_f + '" "' + hardlink_bin_f + '"')
        if ret > 0:
            raise Exception("fail to create links");

        # create postinstall > root/etc/postinstall
        f = open(postinstall_f, "w");
        f.write(r"""#!/usr/bin/sh
echo "postinstall ... ok" >> {marker_d}/log;
""".format(marker_d=sys_marker_d));
        f.close();
        # create preremove > root/etc/postremove
        f = open(preremove_f, "w");
        f.write(r"""#!/usr/bin/sh
echo "preremove ... ok" >> {marker_d}/log;
""".format(marker_d=sys_marker_d));
        f.close();
        # create postremmove > root/etc/preremmove
        f = open(postremove_f, "w");
        f.write(r"""#!/usr/bin/sh
echo "postremove ... ok" >> {marker_d}/log;
""".format(marker_d=sys_marker_d));
        f.close();
        # create version marker > root/var/<pkg>/<version>
        f = open(marker_f, "w");
        f.write(self.version.__dict__[distname]);
        f.close();
        # build tar.bz2
        tar_name = os.path.join(self._localMirror, self.install.__dict__[distname].url);
        tar = tarfile.open(tar_name, mode="w:bz2");
        for name in [usr_d, etc_d, var_d]:
            tar.add(name, os.path.basename(name));
        members = tar.getmembers();
        tar.close();

        # Force slash to the end of each directories
        lst = []
        for m in members:
            if m.isdir() and not m.name.endswith("/"):
                lst.append(m.name + "/")
            else:
                lst.append(m.name)
        self.filelist = lst;

        # build source tar
        tar_src_name = os.path.join(self._localMirror, self.source.__dict__[distname].url);
        tar = tarfile.open(tar_src_name, mode="w:bz2");
        tar.add(dirname, self.name+"-"+self.version.__dict__[distname]);
        tar.close();

        f = open(tar_name, "rb");
        content = f.read();
        f.close();
        md5sum = hashlib.md5(content).hexdigest();

        f = open(tar_src_name, "rb");
        content = f.read();
        f.close();
        md5sum_src = hashlib.md5(content).hexdigest();

        md5_sum_f = os.path.join(os.path.dirname(tar_name), "md5.sum");

        f = open(md5_sum_f, "a");
        f.write(\
            md5sum + \
            "  " + \
            os.path.basename(self.install.__dict__[distname].url) + \
            "\n" + \
            md5sum_src + \
            "  " + \
            os.path.basename(self.source.__dict__[distname].url) + \
            "\n"
        );
        f.close();

        self.install.__dict__[distname].size = long(os.path.getsize(tar_name));
        self.source.__dict__[distname].size = long(os.path.getsize(tar_src_name));
        self.install.__dict__[distname].md5 = md5sum;
        self.source.__dict__[distname].md5 = md5sum_src;

class DistNameStruct():
    def __init__(self):
        self.curr = None
        self.prev = None
        self.test = None

    def __getitem__(self, key):
        return self.__dict__[key];

class DistStruct():
    def __init__(self):
        self.category = None
        self.sdesc = None
        self.ldesc = None
        self.requires = None
        self.version = None
        self.install = None
        self.source = None

class DistsStruct(DistNameStruct):
    def __init__(self):
        self.curr = DistStruct()
        self.prev = DistStruct()
        self.test = DistStruct()

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
        ball =  self.url + " " + \
                str(self.size) + " " + \
                self.md5;
        return ball;
