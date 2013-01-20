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
import gzip;
import hashlib;
import io;
import os;
import re;
import shutil;
import sys;
import tarfile;
import urllib;

import utils as cautils;
from error import CygAptError;
from path_mapper import PathMapper;

class CygApt:
    def __init__(self, \
        main_packagename, \
        main_files, \
        main_cyg_apt_rc, \
        main_cygwin_p, \
        main_download_p, \
        main_mirror, \
        main_downloads, \
        main_distname, \
        main_nodeps_p, \
        main_regex_search, \
        main_nobarred, \
        main_nopostinstall, \
        main_nopostremove, \
        main_dists, \
        main_installed, \
        main_scriptname, \
        main_verbose):

        # Define constants
        self.installedDbMagic = 'INSTALLED.DB 2\n';
        self.ballTarget = 'install';
        self.rcOptions = ['ROOT', 'mirror', 'cache', 'setup_ini', 'distname', 'barred'];
        self.distNames = ('curr', 'test', 'prev');
        self.rcRegex = re.compile("^\s*(\w+)\s*=\s*(.*)\s*$");
        self._forceBarred = ['python', 'python-argparse', 'gnupg'];
        self._shOption = " --norc --noprofile ";

        # Default behaviours
        self.regexSearch = False;
        self.noBarred = False;
        self.noPostInstall = False;
        self.noPostRemove = False;

        # Init
        self.appName = main_scriptname;
        self.pkgName = main_packagename;
        self.files = main_files;
        self.cygwinPlatform = main_cygwin_p;
        self.downloadOnly = main_download_p;
        self.downloadDir = main_downloads;
        self.noDeps = main_nodeps_p;
        self.regexSearch = main_regex_search;
        self.noBarred = main_nobarred;
        self.noPostInstall = main_nopostinstall;
        self.noPostRemove = main_nopostremove;
        self.dists = main_dists;
        self.installed = main_installed;
        self.configFileName = main_cyg_apt_rc;
        self.verbose = main_verbose;

        # Read in our configuration
        self.getRessource(self.configFileName);

        # Now we have a path mapper, check setup.exe is not running
        self.checkForSetupExe();

        # DOS specific
        if not self.cygwinPlatform:
            self.lnExists = os.path.exists(self.prefixRoot + "/bin/ln.exe");
        else:
            self.lnExists = True;

        # Overrides to the .rc
        if (main_mirror):
            self.mirror = main_mirror;
            self.downloadDir = self.cache + '/' + urllib.quote(self.mirror, '').lower();

        if (main_distname):
            self.distname = main_distname;

        if not (os.path.isfile(self.installedDb) or os.path.isfile(self.setup_ini)):
            sys.stderr.write('\n');
            sys.stderr.write('error: \"{0}\" no such file\n'.format(self.installedDb));
            sys.stderr.write('error: run {0} setup?\n'.format(self.appName));
            sys.exit(2);
        else:
            self.getSetupIni();
            self.getInstalled();

    def checkForSetupExe(self):
        # It's far from bulletpoof, but it's surprisingly hard to detect
        # setup.exe running since it doesn't lock any files.
        p = os.popen(self.pm.mapPath("/usr/bin/ps -W"));
        psout = p.readlines();
        p.close();
        for l in psout:
            if "setup.exe" in l or "setup-1.7.exe" in l:
                raise AppConflictError("{0}: Please close setup.exe while "\
                    "running cyg-apt. Exiting.".format(self.appName));

    def versionToString(self, t):
        def try_itoa(x):
            if isinstance(x, int):
                return "{0:d}".format(x);
            return x
        return '{0}-{1}'.format('.'.join(list(map(try_itoa, t[:-1]))),
                  t[-1]);

    def stringToVersion(self, s):
        s = re.sub('([^0-9][^0-9]*)', ' \\1 ', s);
        s = re.sub('[ _.-][ _.-]*', ' ', s);
        def try_atoi(x):
            if re.match('^[0-9]*$', x):
                return int(x);
            return x
        return tuple(map(try_atoi, (s.split(' '))));

    def splitBall(self, p):
        m = re.match('^(.*)-([0-9].*-[0-9]+)(.tar.bz2)?$', p);
        if not m:
            print('splitBall: ' + p);
            return (p[:2], (0, 0));
        t = (m.group(1), self.stringToVersion(m.group(2)));
        return t;

    def joinBall(self, t):
        return t[0] + '-' + self.versionToString(t[1]);

    def debug(self, s):
        s;

    def help(self,):
        """this help message"""
        if len(self.files) < 2:
            self.usage();
            sys.exit();
        print(self.__dict__[self.pkgName].__doc__);

    def getSetupIni(self):
        if self.dists:
            return;
        self.dists = {'test': {}, 'curr': {}, 'prev' : {}};
        f = open(self.setup_ini);
        contents = f.read();
        f.close();
        chunks = contents.split('\n\n@ ');
        for i in chunks[1:]:
            lines = i.split('\n');
            name = lines[0].strip();
            self.debug('package: ' + name);
            packages = self.dists['curr'];
            records = {'sdesc': name};
            j = 1;
            while j < len(lines) and lines[j].strip():
                self.debug('raw: ' + lines[j]);
                if lines[j][0] == '#':
                    j = j + 1;
                    continue;
                elif lines[j][0] == '[':
                    self.debug('dist: ' + lines[j][1:5]);
                    packages[name] = records.copy();
                    packages = self.dists[lines[j][1:5]];
                    j = j + 1;
                    continue;

                try:
                    duo = lines[j].split(': ', 1);
                    key = duo[0].strip();
                    value = duo[1].strip();
                except:
                    print(lines[j]);
                    raise;
                if value.find('"') != -1 and value.find('"', value.find('"') + 1) == -1:
                    while True:
                        j = j + 1;
                        value += '\n' + lines[j];
                        if lines[j].find('"') != -1:
                            break;
                records[key] = value;
                j = j + 1;
            packages[name] = records;

    def getUrl(self):
        if self.pkgName not in self.dists[self.distname] \
           or self.ballTarget not in self.dists[self.distname][self.pkgName]:
            self.noPackage();
            install = 0;
            for d in self.distNames:
                if self.pkgName in self.dists[d] \
                   and self.ballTarget in self.dists[d][self.pkgName]:
                    install = self.dists[d][self.pkgName][self.ballTarget];
                    sys.stderr.write("warning: using [{0}]\n".format(d));
                    break;
            if not install:
                raise SetupIniError(str(self.pkgName) + " is not in " + self.setup_ini);
        else:
            install = self.dists[self.distname][self.pkgName][self.ballTarget];
        filename, size, md5 = install.split();
        return filename, md5;

    def url(self):
        """print tarball url"""
        if not self.pkgName:
            raise CygAptError("url command requires a package name");
        print(self.mirror + "/" + self.getUrl()[0]);

    def getBall(self):
        url, md5 = self.getUrl();
        return '{0}/{1}'.format(self.downloadDir, url);

    def ball(self):
        """print tarball name"""
        print(self.getBall());

    def doDownload(self):
        url, md5 = self.getUrl();
        directory = '{0}/{1}'.format(self.downloadDir, os.path.split(url)[0]);
        if not os.path.exists(self.getBall()) or not self.checkMd5():
            if not os.path.exists(directory):
                os.makedirs(directory);
            status = cautils.uri_get(directory, '{0}/{1}'.format(self.mirror, url));
            if status:
                sys.stderr.write("\n{0}: didn't find {1} "\
                    "on mirror {2}: possible mismatch between setup.ini and "\
                    "mirror requiring {3} update?".format(
                    self.appName, self.pkgName, self.mirror, \
                    self.appName));
                sys.exit(1);

    def download(self):
        """download package (only, do not install)"""
        self.doDownload();
        self.ball();
        self.md5();

    def noPackage(self):
        sys.stderr.write \
        ("{0}: {1} is not on mirror {2} in [{3}]\n".format(self.appName, self.pkgName, \
            self.mirror, self.distname));

    # return an array contents all dependencies of self.pkgName
    def getRequires(self):
        # Looking for dependencies on curr not prev or test
        dist = self.dists["curr"];
        if self.pkgName not in self.dists[self.distname]:
            self.noPackage();
            sys.exit(1);
        if self.noDeps:
            return [];
        reqs = {self.pkgName:0};
        if self.ballTarget == 'source' \
            and 'external-source' in dist[self.pkgName]:
            reqs[dist[self.pkgName]['external-source']] = 0;
        n = 0;
        while len(reqs) > n:
            n = len(reqs);
            for i in list(reqs.keys()):
                if i not in dist:
                    sys.stderr.write("error: {0} not in [{1}]\n".format(
                        i, self.distname));
                    if i != self.pkgName:
                        del reqs[i];
                    continue;
                reqs[i] = '0';
                p = dist[i];
                if 'requires' not in p:
                    continue;
                update_list = [(x, 0) for x in p['requires'].split()];
                reqs.update(update_list);
        # Delete the ask package it is not require by it self (joke)
        reqs.pop(self.pkgName);
        rlist = sorted(reqs.keys());
        return rlist;

    def requires(self):
        """print requires: for package"""
        reqs = self.getRequires();
        if len(reqs) == 0:
            print('No dependencies for package {0}'.format(self.pkgName));
        else:
            print('\n'.join(reqs));

    def getInstalled(self):
        if self.installed:
            return self.installed;
        self.installed = {0:{}};
        f = open(self.installedDb);
        lines = f.readlines();
        f.close();
        for i in lines[1:]:
            name, ball, status = i.split();
            self.installed[int(status)][name] = ball;
        return self.installed;

    def writeInstalled(self):
        file_db = open(self.installedDb, 'w');
        file_db.write(self.installedDbMagic);
        file_db.writelines(['{0} {1} 0\n'.format(x, self.installed[0][x]) for x in list(self.installed[0].keys())]);
        if file_db.close():
            raise IOError;

    def getField(self, field, default=''):
        for d in (self.distname,) + self.distNames:
            if self.pkgName in self.dists[d] \
               and field in self.dists[d][self.pkgName]:
                return self.dists[d][self.pkgName][field];
        return default;

    def psort(self, lst):
        lst.sort();
        return lst;

    def preverse(self, lst):
        lst.reverse();
        return lst;

    def list(self):
        """list installed packages"""
        print("--- Installed packages ---");
        for self.pkgName in self.psort(list(self.installed[0].keys())):
            ins = self.getInstalledVersion();
            new = 0;
            if self.pkgName in self.dists[self.distname] \
               and self.ballTarget in self.dists[self.distname][self.pkgName]:
                new = self.getVersion();
            s = '{0:<19} {1:<15}'.format(self.pkgName, self.versionToString(ins));
            if new and new != ins:
                s += '({0})'.formatself.versionToString(new);
            print(s);

    def filelist(self):
        """list files installed by given packages"""
        if not self.pkgName:
            print("{0}: no package name given. Exiting.\n".format(self.appName),
                  file=sys.stderr);
        else:
            print('\n'.join(self.getFileList()));

    def postInstall(self):
        self.runAll(self.postInstallDir);

    def postRemove(self):
        if len(self.files[1:]) == 0:
            print("{0}: must specify package to run postremove. "\
                  "Exiting.".format(self.appName),
                  file=sys.stderr);
        else:
            for self.pkgName in self.files[1:]:
                preremove_sh = self.preremove_dir + "/" + self.pkgName + ".sh";
                postremove_sh = self.postRemoveDir + "/" + self.pkgName + ".sh";
                self.runScript(preremove_sh);
                self.runScript(postremove_sh);

    def getVersion(self):
        if self.pkgName not in self.dists[self.distname] \
           or self.ballTarget not in self.dists[self.distname][self.pkgName]:
            self.noPackage();
            return (0, 0);
        package = self.dists[self.distname][self.pkgName];
        if 'ver' not in package:
            filename = package[self.ballTarget].split()[0];
            ball = os.path.split(filename)[1];
            package['ver'] = self.splitBall(ball)[1];
        return package['ver'];

    def getInstalledVersion(self):
        return self.splitBall(self.installed[0][self.pkgName])[1];

    def version(self):
        """print installed version"""
        if self.pkgName:
            if self.pkgName not in self.installed[0]:
                raise CygAptError(self.pkgName + " is not installed");
            print(self.versionToString(self.getInstalledVersion()));
        else:
            for self.pkgName in self.psort(list(self.installed[0].keys())):
                if self.pkgName not in self.installed[0]:
                    self.distname = 'installed';
                    self.noPackage();
                    sys.exit(1);
                print('{0:<20}{1:<12}'.format(self.pkgName,
                         self.versionToString(self.getInstalledVersion())));

    def getNew(self):
        lst = [];
        for self.pkgName in list(self.installed[0].keys()):
            new = self.getVersion();
            ins = self.getInstalledVersion();
            if new > ins:
                self.debug(" {0} > {1}".format(new, ins));
                lst.append(self.pkgName);
        return lst;

    def new(self):
        """list new (upgradable) packages in distribution"""
        for self.pkgName in self.psort(self.getNew()):
            print('{0:<20}{1:<12}'.format(self.pkgName,
                          self.versionToString(self.getVersion())));

    def getMd5(self):
        url, md5 = self.getUrl();
        f = open("{0}/{1}".format(self.downloadDir, url), "rb");
        data = f.read();
        f.close();
        m = hashlib.md5();
        m.update(data);
        digest = m.hexdigest();
        return digest;

    def checkMd5(self):
        return self.getUrl()[1] == self.getMd5();

    def md5(self):
        """check md5 sum of cached package against database"""
        if not os.path.exists(self.getBall()):
            sys.stderr.write("{0}: {1} not installed. Exiting.\n".format(
                os.path.basename(sys.argv[0]), self.pkgName));
            return 1;
        url, md5 = self.getUrl();
        ball = os.path.basename(url);
        print('{0}  {1}'.format(md5, ball));
        actual_md5 = self.getMd5();
        print('{0}  {1}'.format(actual_md5, ball));
        if actual_md5 != md5:
            raise CygAptError("md5sum of cached package doesn't match md5 in setup.ini from mirror");

    def search(self):
        """search all package descriptions for string"""
        if not self.pkgName:
            raise CygAptError("search command requires a string to search for");
        if not self.regexSearch:
            regexp = re.escape(self.pkgName);
        else:
            regexp = self.pkgName;
        packages = [];
        keys = [];
        if self.distname in self.dists:
            keys = list(self.dists[self.distname].keys());
        else:
            for i in list(self.dists.keys()):
                for j in list(self.dists[i].keys()):
                    if not j in keys:
                        keys.append(j);
        for i in keys:
            self.pkgName = i;
            if not regexp or re.search(regexp, i) \
               or re.search(regexp, self.getField('sdesc')) \
               or re.search(regexp, self.getField('ldesc')):
                if self.distname in self.dists:
                    if self.ballTarget in self.dists[self.distname][i]:
                        packages.append(i);
                else:
                    packages.append(i);
        for self.pkgName in self.psort(packages):
            s = self.pkgName;
            d = self.getField('sdesc');
            if d:
                s += ' - {0}'.format(d[1:-1]);
            print(s);

    def show(self):
        """print package description"""
        s = self.pkgName;
        d = self.getField('sdesc');
        if d:
            s += ' - {0}'.format(d[1:-1]);
        ldesc = self.getField('ldesc');
        if ldesc != "":
            print(s + "\n");
            print(ldesc);
        else:
            print("{0}: not found in setup.ini: {1}".format(self.appName, s));

    # return an array with all packages that must to be install
    def getMissing(self):
        reqs = self.getRequires();
        missingreqs = [];  # List of missing package on requires list
        for i in reqs:
            if i not in self.installed[0]:
                missingreqs.append(i);
        if self.pkgName not in self.installed[0]:
            missingreqs.append(self.pkgName);
        if missingreqs and self.pkgName not in missingreqs:
            sys.stderr.write('warning: missing packages: {0}\n'.format(" ".join(missingreqs)));
        elif self.pkgName in self.installed[0]:  # Check version
            ins = self.getInstalledVersion();
            new = self.getVersion();
            if ins >= new:
                sys.stderr.write('{0} is already the newest version\n'.format(self.pkgName));
                # missingreqs.remove(self.pkgName)
            elif self.pkgName not in missingreqs:
                missingreqs.append(self.pkgName);
        return missingreqs;

    def missing(self):
        """print missing dependencies for package"""
        missing = self.getMissing();
        if len(missing) > 0:
            print('\n'.join(missing));
        else:
            print("All dependent packages for {0} installed".format(self.pkgName));

    def runScript(self, file_name, optional=True):
        mapped_file = self.pm.mapPath(file_name);
        mapped_file_done = mapped_file + ".done";
        if os.path.isfile(mapped_file):
            sys.stderr.write('running: {0}\n'.format(file_name));
            if self.cygwinPlatform:
                cmd = "sh " + self._shOption + mapped_file;
            else:
                cmd = self.dosBash + self._shOption + mapped_file;
            retval = os.system(cmd);

            if os.path.exists(mapped_file_done):
                os.remove(mapped_file_done);
            if retval == 0:
                shutil.move(mapped_file, mapped_file_done);
        else:
            if not optional:
                sys.stderr.write("{0}: WARNING couldn't find {1}.\n".format(
                    self.appName, mapped_file));

    def runAll(self, dirname):
        if os.path.isdir(dirname):
            lst = [x for x in os.listdir(dirname) if x[-3:] == '.sh'];
            for i in lst:
                self.runScript('{0}/{1}'.format(dirname, i));

    def doInstallExternal(self, ball):
        # Currently we use a temporary directory and extractall() then copy:
        # this is very slow. The Python documentation warns more sophisticated
        # approaches have pitfalls without specifying what they are.
        tf = tarfile.open(ball);
        members = tf.getmembers();
        tempdir = os.path.basename(tf.name) + "-tmp";
        tempdir = tempdir.replace(".tar.bz2", "");
        if os.path.exists(tempdir):
            print("{0}: tmpdir {1} exists, won't overwrite.\nInstall "\
            "of {2} failed. exiting.".format(self.appName,
                                             tempdir,
                                             self.pkgName),
                  file=sys.stderr);
            sys.exit(1);
        try:
            tf.extractall(tempdir);
            for m in members:
                if m.isdir():
                    path = self.pm.mapPath("/" + m.name);
                    if not os.path.exists(path):
                        os.makedirs(path, m.mode);
            for m in members:
                if m.isdir():
                    path = self.pm.mapPath("/" + m.name);
                    if not os.path.exists(path):
                        os.makedirs(path, m.mode);
                else:
                    path = self.pm.mapPath("/" + m.name);
                    dirname = os.path.dirname(path);
                    if not os.path.exists(dirname):
                        os.makedirs(dirname);
                    if os.path.exists(path):
                        os.chmod(path, 0o777);
                        os.remove(path);
                    # Windows extract() is robust but can't form Cygwin links
                    # (It produces copies instead: bulky and bugbait.)
                    # Convert to links if possible -- depends on coreutils being installed
                    if m.issym() and self.lnExists:
                        link_target = m.linkname;
                        os.system(self.dosLn + " -s " + link_target + " " + path);
                    elif m.islnk() and self.lnExists:
                        # Hard link -- expect these to be very rare
                        link_target = m.linkname;
                        mapped_target = self.pm.mapPath("/" + m.linkname);
                        # Must ensure target exists before forming hard link
                        if not os.path.exists(mapped_target):
                            shutil.move(tempdir + "/" + link_target, mapped_target);
                        os.system(self.dosLn + " " + mapped_target + " " + path);
                    else:
                        shutil.move(tempdir + "/" + m.name, path);
        finally:
            tf.close();
            cautils.rmtree(tempdir);

    def doInstall(self):
        ball = self.getBall();
        if tarfile.is_tarfile(ball):
            if not self.cygwinPlatform:
                self.doInstallExternal(ball);
            tf = tarfile.open(ball);
            if self.cygwinPlatform:
                tf.extractall(self.absRoot);
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
            print("{0}: bad tarball {1}. Install failed.".format(self.appName,
                                                                 ball),
                  file=sys.stderr);
            return
        self.writeFileList(lst);

        status = 1;
        if not self.pkgName in self._integrityControl():
            status = 0;
        self.installed[status][self.pkgName] = os.path.basename(ball);

        self.writeInstalled();

    def getFileList(self):
        filelist_file = "{0}/{1}.lst.gz".format(self.config, self.pkgName);
        if not os.path.exists(filelist_file):
            if self.pkgName not in self.installed[0]:
                raise CygAptError(self.pkgName + " is not installed");
            else:
                raise CygAptError(self.pkgName + " is installed, but " + \
                    filelist_file + " is missing");
        gzf = gzip.GzipFile(filelist_file);
        lst = gzf.readlines();
        gzf.close();
        lst = [x.decode().strip() for x in lst];
        return lst;

    def touch(self, fname, times=None):
        f = open(fname, 'a');
        os.utime(fname, times);
        f.close();

    def writeFileList(self, lst):
        gz_filename = '{0}/{1}.lst.gz'.format(self.config, self.pkgName);
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

        stat_struct = os.stat(self.setup_ini);
        atime = stat_struct[7];
        mtime = stat_struct[8];
        self.touch(gz_filename, (atime, mtime));

    def removeFileList(self):
        lst_name = '{0}/{1}.lst.gz'.format(self.config, self.pkgName);
        if os.path.exists(lst_name):
            os.remove(lst_name);
        else:
            sys.stderr.write('{0}: warning {1} no such file\n'.format(
                 sys.argv[0], lst_name));

    def uninstallWantFileRemoved(self, filename, noremoves, nowarns):
        # Returns true if the path from the tarball should result in a file # removal operation, false if not.
        if not os.path.exists(filename) and not os.path.islink(filename):
            if filename not in nowarns:
                sys.stderr.write('warning: {0} no such file\n'.format(filename));
            return False;
        elif not os.path.isdir(filename) and filename not in noremoves:
            return True;

    def doUninstall(self):
        postremove_sh = self.postRemoveDir + "/" + self.pkgName + ".sh";
        postinstall_sh = self.postInstallDir + "/" + self.pkgName + ".sh";
        preremove_sh = self.preremove_dir + "/" + self.pkgName + ".sh";

        postinstall_done = self.postInstallDir + "/" + self.pkgName + ".sh.done";
        suppression_msg = \
            "{0}: postremove suppressed: \"{1} postremove {2}\" to complete.".format(
            self.appName, self.appName, self.pkgName);

        lst = self.getFileList();
        expect_preremove = preremove_sh[1:] in lst;
        expect_postremove = postremove_sh[1:] in lst;

        if not self.noPostRemove:
            if expect_preremove:
                self.runScript(preremove_sh, optional=False);
        else:
            print("{0}".format(suppression_msg),
                  file=sys.stderr);

        # We don't expect these to be present: they are executed
        # and moved to $(packagename).sh.done
        nowarns = [];
        nowarns.append(self.pm.mapPath(postinstall_sh));
        nowarns.append(self.pm.mapPath(preremove_sh));

        noremoves = [];
        if self.noPostRemove:
            noremoves.append(self.pm.mapPath(preremove_sh));
        noremoves.append(self.pm.mapPath(postremove_sh));

        # remove files
        for i in lst:
            filename = self.pm.mapPath("/" + i);
            if os.path.isdir(filename):
                continue;
            if (self.uninstallWantFileRemoved(filename, noremoves, nowarns)):
                if os.path.exists(filename):
                    if self.cygwinPlatform:
                        os.chmod(filename, 0o777);
                    if os.remove(filename):
                        raise IOError;
                else:
                    if os.path.islink(filename):
                        os.remove(filename);
                    else:
                        print("{0}: warning: expected to remove {1} but it was"\
                            " not there.".format(self.appName, filename));
        if not self.noPostRemove:
            if expect_postremove:
                self.runScript(postremove_sh, optional=False);
            if os.path.isfile(self.pm.mapPath(postremove_sh)):
                if os.remove(self.pm.mapPath(postremove_sh)):
                    raise IOError;

        # We don't remove empty directories: the problem is are we sure no other
        # package is depending on them.

        # setup.exe removes the filelist when a package is uninstalled: we try to be
        # as much like setup.exe as possible
        self.removeFileList();

        # Clean up the postintall script: it's been moved to .done
        if os.path.isfile(self.pm.mapPath(postinstall_done)):
            os.remove(self.pm.mapPath(postinstall_done));

        # update installed[]
        del(self.installed[0][self.pkgName]);
        self.writeInstalled();

    def remove(self):
        """uninstall packages"""
        barred = [];
        for self.pkgName in self.files[1:]:
            if self.pkgName not in self.installed[0]:
                sys.stderr.write('warning: {0} not installed\n'.format(self.pkgName));
                continue;
            if self.isBarredPackage(self.pkgName):
                barred.append(self.pkgName);
                continue;
            sys.stderr.write('uninstalling {0} {1}\n'.format(
                         self.pkgName,
                         self.versionToString(self.getInstalledVersion())));
            self.doUninstall();
        self.barredWarnIfNeed(barred, "removing");

    def purge(self):
        """uninstall packages and delete from cache"""
        barred = [];

        for self.pkgName in self.files[1:]:
            try:
                if self.pkgName in self.installed[0]:
                    if self.isBarredPackage(self.pkgName):
                        barred.append(self.pkgName);
                        continue;
                    sys.stderr.write('uninstalling {0} {1}\n'.format(
                        self.pkgName,
                        self.versionToString(self.getInstalledVersion())));
                    self.doUninstall();
                scripts = [self.postInstallDir + "/{0}.sh.done", \
                    self.preremove_dir + "/{0}.sh.done", \
                    self.postRemoveDir + "/{0}.sh.done"];
                scripts = [s.format(self.pkgName) for s in scripts];
                scripts = [self.pm.mapPath(s) for s in scripts];
                for s in scripts:
                    if os.path.exists(s):
                        os.remove(s);
                ball = self.getBall();
                if os.path.exists(ball):
                    print("{0}: removing {1}".format(self.appName, ball));
                    os.remove(ball);
            except SetupIniError as xxx_todo_changeme1:
                (err) = xxx_todo_changeme1;
                sys.stderr.write(self.appName + ": " + err.msg + \
                    " exiting.\n");
                sys.exit(1);
        self.barredWarnIfNeed(barred, "purging");

    def barredWarnIfNeed(self, barred, command):
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
                helpfull += r"""
You can force the installation with the option -f. But it is recommended
to upgrade the Cygwin distribution, with the official Setup program
(e.g., setup.exe).""";
                if "_autorebase" in barred:
                    close_all_cygwin_programs += r"""
Before that, you must close all Cygwin programs to perform rebasing
(e.g., rebaseall).""";
            print("BarredWarning: NOT {1}:\n    {2}\n{0} is dependent on {3} under Cygwin."\
                  "{4}{5}".format(self.appName,
                                  command,
                                  barredstr,
                                  this_these,
                                  helpfull,
                                  close_all_cygwin_programs),
                  file=sys.stderr);
            if not self.cygwinPlatform:
                print("Use -f to override but proceed with caution.",
                      file=sys.stderr);
    def install(self):
        """download and install packages with dependencies"""
        suppression_msg = \
            "{0}: postinstall suppressed: \"{1} postinstall\" to complete.".format(
            self.appName, self.appName);
        missing = {};
        barred = [];
        for self.pkgName in self.files[1:]:
            missing.update(dict([(x, 0) for x in self.getMissing()]));

        if len(missing) > 1:
            sys.stderr.write('to install: \n');
            sys.stderr.write('    {0}'.format(" ".join(list(missing.keys()))));
            sys.stderr.write('\n');

        for self.pkgName in list(missing.keys()):
            if not self.getUrl():
                del missing[self.pkgName];

        for self.pkgName in list(missing.keys()):
            if self.isBarredPackage(self.pkgName):
                barred.append(self.pkgName);
                del missing[self.pkgName];

        for self.pkgName in list(missing.keys()):
            self.download();
        if self.downloadOnly:
            sys.exit(0);
        for self.pkgName in list(missing.keys()):
            if self.pkgName in self.installed[0]:
                sys.stderr.write('preparing to replace {0} {1}\n'.format(
                    self.pkgName, self.versionToString(self.getInstalledVersion())));
                self.doUninstall();
            sys.stderr.write('installing {0} {1}\n'.format(
                  self.pkgName, self.versionToString(self.getVersion())));
            self.doInstall();

        if self.noPostInstall:
            print(suppression_msg, file=sys.stderr);
        else:
            self.postInstall();

        self.barredWarnIfNeed(barred, "installing");

    def _integrityControl(self, checklist=[]):
        options = "-c ";
        if self.verbose:
            options += '-v ';

        if len(checklist) == 0:
            checklist.append(self.pkgName);

        pkg_lst = " ".join(checklist);
        command = '';
        if not self.cygwinPlatform:
            command += self.dosBash + ' ' + self._shOption;
            command += ' -c ';
            command += "'";
        command += '/bin/cygcheck ';
        command += options;
        command += pkg_lst;
        if not self.cygwinPlatform:
            command += "'";

        p = os.popen(command);
        outputlines = p.readlines();
        p.close();

        unformat = '';
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

            if package == 'Package' and version == 'Version' and status == 'Status':
                start = True;
                unformat = '';
            elif not start:
                continue;

            if start and status == 'Incomplete':
                print(res[:-2]);
                print(unformat);
                unformat = '';
                incomplete.append(package);

        return incomplete;

    def upgrade(self):
        """all installed packages"""
        self.files[1:] = self.getNew();
        self.install();

    def printErr(self, err):
        print("{0}: {1}".format(self.appName, err));

    def doUnpack(self):
        ball = self.getBall();
        basename = os.path.basename(ball);
        self.pkgName = re.sub('(-src)*\.tar\.(bz2|gz)', '', basename);
        if os.path.exists(self.pkgName):
            self.printErr(self.pkgName + " already exists. Not overwriting.\n");
            return 1;
        os.mkdir(self.pkgName);
        if tarfile.is_tarfile(ball):
            tf = tarfile.open(ball);
            tf.extractall(self.pkgName);
            tf.close();
        else:
            print("{0}: bad source tarball {1}, exiting.\n"\
                  "{0}: SOURCE UNPACK FAILED".format(self.appName,
                                                     ball),
                  file=sys.stderr);
            sys.exit(1);
        if not os.path.exists(self.pkgName):
            raise IOError;
        print(self.pkgName);

    def source(self):
        """download source package"""
        self.ballTarget = 'source';
        for self.pkgName in self.files[1:]:
            self.download();
            self.doUnpack();
        sys.exit(0);

    def find(self):
        """find package containing file"""
        if self.regexSearch:
            file_to_find = self.pkgName;
        else:
            file_to_find = re.escape(self.pkgName);
        hits = [];
        for self.pkgName in self.psort(list(self.installed[0].keys())):
            filenames_file = "{0}/{1}.lst.gz".format(self.config, self.pkgName);
            if not os.path.exists(filenames_file):
                continue;
            files = self.getFileList();
            for i in files:
                if re.search(file_to_find, '/{0}'.format(i)):
                    hits.append('{0}: /{1}'.format(self.pkgName, i));
        print('\n'.join(hits));

    def setRoot(self, root):
        if len(root) < 1 or root[-1] != "/":
            print("{0}: ROOT must end in a slash. Exiting.".format(self.appName));
            sys.exit(1);
        self.prefixRoot = root[:-1];
        self.absRoot = root;

    def getRessource(self, filename):
        f = open(filename);
        lines = f.readlines();
        f.close();
        for i in lines:
            result = self.rcRegex.search(i);
            if result:
                k = result.group(1);
                v = result.group(2);
                if k in self.rcOptions:
                    self.__dict__[k] = eval(v);

        if not self.cache:
            print("{0}: {1} doesn't define cache. Exiting.".format(self.appName, self.configFileName));
            sys.exit(1);
        if not self.mirror:
            print("{0}: {1} doesn't define mirror. Exiting.".format(self.appName, self.configFileName));
            sys.exit(1);

        # We want ROOT + "/etc/setup" and cd(ROOT) to work:
        # necessitates two different forms, prefix and absolute
        if(self.cygwinPlatform):
            self.setRoot("/");
        else:
            self.setRoot(self.ROOT);
        self.ROOT = None;
        self.pm = PathMapper(self.prefixRoot, self.cygwinPlatform);
        self.config = self.pm.mapPath("/etc/setup");
        self.cache = self.pm.mapPath(self.cache);
        self.downloadDir = self.cache + '/' + urllib.quote(self.mirror, '').lower();
        self.installedDb = self.config + '/installed.db';

        # It might seem odd that we don't map these paths: we need
        # to retain unmapped forms since under DOS we invoke Cygwin bash to
        # run these scripts unless flagged not to
        self.postInstallDir = "/etc/postinstall";
        self.postRemoveDir = "/etc/postremove";
        self.preremove_dir = "/etc/preremove";

        self.setup_ini = self.pm.mapPath(self.setup_ini);
        self.dosBinDir = self.pm.mountRoot + "/bin";
        self.dosBash = self.pm.mountRoot + "bin/bash";
        self.dosLn = self.pm.mountRoot + "bin/ln";
        return 0;

    def isBarredPackage(self, package):
        barred = [];
        # add user barred package
        barred.extend(self.barred.split());
        # add force barred package
        barred.extend(self._forceBarred);

        # store current package name
        curr_pkgname = self.pkgName;

        # get barred package requires
        depbarred = [];
        for self.pkgName in barred:
            try:
                depbarred.extend(self.getRequires());
            except SystemExit:
                pass;

        barred.extend(depbarred);

        # set current package name
        self.pkgName = curr_pkgname;

        return (not self.noBarred) and package in barred;

class AppConflictError(CygAptError):
    def __init__(self, *args):
        CygAptError.__init__(self, *args);

class SetupIniError(CygAptError):
    def __init__(self, *args):
        CygAptError.__init__(self, *args);
