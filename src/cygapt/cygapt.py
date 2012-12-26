"""
  cyg-apt - a Cygwin package manager.
  
  (c) 2002--2009 Chris Cormie         Jan Nieuwenhuizen
                 <cjcormie@gmail.com> <janneke@gnu.org> 
  (c) 2012       James Nylen
                 <jnylen@gmail.com>
  
  License: GNU GPL
"""

import gzip
import hashlib
import io
import os
import re
import shutil
import string
import sys
import tarfile
import urllib

import utils as cautils
from error import CygAptError
from path_mapper import PathMapper

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
        self.installed_db_magic = 'INSTALLED.DB 2\n'
        self.INSTALL = 'install'
        self.rc_options = ['ROOT', 'mirror', 'cache', 'setup_ini', 'distname', 'barred']
        self.distnames = ('curr', 'test', 'prev')
        self.rc_regex = re.compile("^\s*(\w+)\s*=\s*(.*)\s*$")

        # Default behaviours
        self.regex_search = False
        self.nobarred = False
        self.nopostinstall = False
        self.nopostremove = False

        # Init
        self.sn = main_scriptname
        self.packagename = main_packagename
        self.files = main_files
        self.cygwin_p = main_cygwin_p
        self.download_p = main_download_p
        self.downloads = main_downloads
        self.nodeps_p = main_nodeps_p
        self.regex_search = main_regex_search
        self.nobarred = main_nobarred
        self.nopostinstall = main_nopostinstall
        self.nopostremove = main_nopostremove
        self.dists = main_dists
        self.installed = main_installed
        self.cyg_apt_rc = main_cyg_apt_rc
        self.verbose = main_verbose

        # Read in our configuration
        self.get_rc(open(self.cyg_apt_rc))

        # Now we have a path mapper, check setup.exe is not running
        self.check_for_setup_exe()

        # DOS specific
        if not self.cygwin_p:
            self.can_use_ln = os.path.exists(self.PREFIX_ROOT + "/bin/ln.exe")
        else:
            self.can_use_ln = True

        # Overrides to the .rc
        if (main_mirror):
            self.mirror = main_mirror
            self.downloads = self.cache + '/' + urllib.quote(self.mirror, '').lower()

        if (main_distname):
            self.distname = main_distname

        if not (os.path.isfile(self.installed_db) or os.path.isfile(self.setup_ini)):
            sys.stderr.write('\n')
            sys.stderr.write('error: \"%s\" no such file\n' % self.installed_db)
            sys.stderr.write('error: run cyg-apt setup?\n' % vars())
            sys.exit(2)
        else:
            self.get_setup_ini()
            self.get_installed()

    def check_for_setup_exe(self):
        # It's far from bulletpoof, but it's surprisingly hard to detect 
        # setup.exe running since it doesn't lock any files.
        psout = os.popen(self.pm.map_path("/usr/bin/ps -W")).readlines()
        for l in psout:
            if "setup.exe" in l or "setup-1.7.exe" in l:
                raise AppConflictError("%s: Please close setup.exe while "\
                    "running cyg-apt. Exiting." % self.sn)

    def version_to_string(self, t):
        def try_itoa(x):
            if type(x) == int:
                return "%d" % x
            return x
        return '%s-%s' % (string.join(list(map(try_itoa, t[:-1])), '.'),
                  t[-1])

    def string_to_version(self, s):
        s = re.sub('([^0-9][^0-9]*)', ' \\1 ', s)
        s = re.sub('[ _.-][ _.-]*', ' ', s)
        def try_atoi(x):
            if re.match('^[0-9]*$', x):
                return string.atoi(x)
            return x
        return tuple(map(try_atoi, (string.split(s, ' '))))

    def split_ball(self, p):
        m = re.match('^(.*)-([0-9].*-[0-9]+)(.tar.bz2)?$', p)
        if not m:
            print('split_ball: ' + p)
            return (p[:2], (0, 0))
        t = (m.group(1), self.string_to_version(m.group(2)))
        return t

    def join_ball(self, t):
        return t[0] + '-' + self.version_to_string(t[1])

    def debug(self, s):
        s

    def help(self,):
        """this help message"""
        if len(self.files) < 2:
            self.usage()
            sys.exit()
        print(self.__dict__[self.packagename].__doc__)

    def get_setup_ini(self):
        if self.dists:
            return
        self.dists = {'test': {}, 'curr': {}, 'prev' : {}}
        chunks = string.split(open(self.setup_ini).read(), '\n\n@ ')
        for i in chunks[1:]:
            lines = string.split(i, '\n')
            name = string.strip(lines[0])
            self.debug('package: ' + name)
            packages = self.dists['curr']
            records = {'sdesc': name}
            j = 1
            while j < len(lines) and string.strip(lines[j]):
                self.debug('raw: ' + lines[j])
                if lines[j][0] == '#':
                    j = j + 1
                    continue
                elif lines[j][0] == '[':
                    self.debug('dist: ' + lines[j][1:5])
                    packages[name] = records.copy()
                    packages = self.dists[lines[j][1:5]]
                    j = j + 1
                    continue

                try:
                    key, value = list(map(string.strip,
                          string.split(lines[j], ': ', 1)))
                except:
                    print(lines[j])
                    raise
                if value.find('"') != -1 and value.find('"', value.find('"') + 1) == -1:
                    while 1:
                        j = j + 1
                        value += '\n' + lines[j]
                        if lines[j].find('"') != -1:
                            break
                records[key] = value
                j = j + 1
            packages[name] = records

    def get_url(self):
        if self.packagename not in self.dists[self.distname] \
           or self.INSTALL not in self.dists[self.distname][self.packagename]:
            self.no_package()
            install = 0
            for d in self.distnames:
                if self.packagename in self.dists[d] \
                   and self.INSTALL in self.dists[d][self.packagename]:
                    install = self.dists[d][self.packagename][self.INSTALL]
                    sys.stderr.write("warning: using [%s]\n" % d)
                    break
            if not install:
                raise SetupIniError(str(self.packagename) + " is not in " + self.setup_ini)
        else:
            install = self.dists[self.distname][self.packagename][self.INSTALL]
        filename, size, md5 = string.split(install)
        return filename, md5

    def url(self):
        """print tarball url"""
        if not self.packagename:
            raise CygAptError("url command requires a package name")
        print(self.mirror + "/" + self.get_url()[0])

    def get_ball(self):
        url, md5 = self.get_url()
        return '%s/%s' % (self.downloads, url)

    def ball(self):
        """print tarball name"""
        print(self.get_ball())

    def do_download(self):
        url, md5 = self.get_url()
        directory = '%s/%s' % (self.downloads, os.path.split(url)[0])
        if not os.path.exists(self.get_ball()) or not self.check_md5():
            if not os.path.exists(directory):
                os.makedirs(directory)
            status = cautils.uri_get(directory, '%s/%s' % (self.mirror, url))
            if status:
                sys.stderr.write("\n%s: didn't find %s "\
                    "on mirror %s: possible mismatch between setup.ini and "\
                    "mirror requiring %s update?"\
                    % (self.sn, self.packagename, self.mirror, \
                    self.sn))
                sys.exit(1)
                    

    def download(self):
        """download package (only, do not install)"""
        self.do_download()
        self.ball()
        self.md5()

    def no_package(self):
        sys.stderr.write \
        ("%s: %s is not on mirror %s in [%s]\n" % (self.sn, self.packagename, \
            self.mirror, self.distname))

    # return an array contents all dependencies of self.packagename
    def get_requires(self):
        # Looking for dependencies on curr not prev or test
        dist = self.dists["curr"]
        if self.packagename not in self.dists[self.distname]:
            self.no_package()
            sys.exit(1)
        if self.nodeps_p:
            return []
        reqs = {self.packagename:0}
        if self.INSTALL == 'source' \
            and 'external-source' in dist[self.packagename]:
            reqs[dist[self.packagename]['external-source']] = 0
        n = 0
        while len(reqs) > n:
            n = len(reqs)
            for i in list(reqs.keys()):
                if i not in dist:
                    sys.stderr.write("error: %s not in [%s]\n" \
                        % (i, self.distname))
                    if i != self.packagename:
                        del reqs[i]
                    continue
                reqs[i] = '0'
                p = dist[i]
                if 'requires' not in p:
                    continue
                update_list = [(x, 0) for x in string.split(p['requires'])]
                reqs.update(update_list)
        # Delete the ask package it is not require by it self (joke)
        reqs.pop(self.packagename)
        rlist = list(reqs.keys())
        rlist.sort()
        return rlist

    def requires(self):
        """print requires: for package"""
        reqs = self.get_requires()
        if len(reqs) == 0:
            print('No dependencies for package %s' % self.packagename)
        else:
            print(string.join(reqs, '\n'))

    def get_installed(self):
        if self.installed:
            return self.installed
        self.installed = {0:{}}
        for i in open(self.installed_db).readlines()[1:]:
            name, ball, status = string.split(i)
            self.installed[int(status)][name] = ball
        return self.installed

    def write_installed(self):
        file_db = open(self.installed_db, 'w')
        file_db.write(self.installed_db_magic)
        file_db.writelines(['%s %s 0\n' % (x, self.installed[0][x]) for x in list(self.installed[0].keys())])
        if file_db.close():
            raise IOError

    def get_field(self, field, default=''):
        for d in (self.distname,) + self.distnames:
            if self.packagename in self.dists[d] \
               and field in self.dists[d][self.packagename]:
                return self.dists[d][self.packagename][field]
        return default

    def psort(self, lst):
        lst.sort()
        return lst
        

    def preverse(self, lst):
        lst.reverse()
        return lst

    def list(self):
        """list installed packages"""
        print("--- Installed packages ---")
        for self.packagename in self.psort(list(self.installed[0].keys())):
            ins = self.get_installed_version()
            new = 0
            if self.packagename in self.dists[self.distname] \
               and self.INSTALL in self.dists[self.distname][self.packagename]:
                new = self.get_version()
            s = '%-19s %-15s' % (self.packagename, self.version_to_string(ins))
            if new and new != ins:
                s += '(%s)' % self.version_to_string(new)
            print(s)

    def filelist(self):
        """list files installed by given packages"""
        if not self.packagename:
            print >> sys.stderr, \
            ("%s: no package name given. Exiting.\n" % self.sn)
        else:
            print(string.join(self.get_filelist(), '\n'))

    def postinstall(self):
        self.run_all(self.postinstall_dir)

    def postremove(self):
        if len(self.files[1:]) == 0:
            print >> sys.stderr, \
            ("%s: must specify package to run postremove. Exiting." % \
                self.sn)
        else:
            for self.packagename in self.files[1:]:
                self.preremove_sh = self.preremove_dir + "/" + self.packagename + ".sh"
                self.postremove_sh = self.postremove_dir + "/" + self.packagename + ".sh"
                self.run_script(self.preremove_sh)
                self.run_script(self.postremove_sh)

    def get_version(self):
        if self.packagename not in self.dists[self.distname] \
           or self.INSTALL not in self.dists[self.distname][self.packagename]:
            self.no_package()
            return (0, 0)
        package = self.dists[self.distname][self.packagename]
        if 'ver' not in package:
            filename = string.split(package[self.INSTALL])[0]
            ball = os.path.split(filename)[1]
            package['ver'] = self.split_ball(ball)[1]
        return package['ver']

    def get_installed_version(self):
        return self.split_ball(self.installed[0][self.packagename])[1]

    def version(self):
        """print installed version"""
        if self.packagename:
            if self.packagename not in self.installed[0]:
                raise CygAptError(self.packagename + " is not installed")
            print(self.version_to_string(self.get_installed_version()))
        else:
            for self.packagename in self.psort(list(self.installed[0].keys())):
                if self.packagename not in self.installed[0]:
                    self.distname = 'installed'
                    self.no_package()
                    sys.exit(1)
                print('%-20s%-12s' % (self.packagename,
                         self.version_to_string(self.get_installed_version())))

    def get_new(self):
        lst = []
        for self.packagename in list(self.installed[0].keys()):
            new = self.get_version()
            ins = self.get_installed_version()
            if new > ins:
                self.debug(" %s > %s" % (new, ins))
                lst.append(self.packagename)
        return lst

    def new(self):
        """list new (upgradable) packages in distribution"""
        for self.packagename in self.psort(self.get_new()):
            print('%-20s%-12s' % (self.packagename,
                          self.version_to_string(self.get_version())))

    def get_md5(self):
        url, md5 = self.get_url()
        f = file("%s/%s" % (self.downloads, url), "rb").read()
        m = hashlib.md5()
        m.update(f)
        digest = m.hexdigest()
        return digest

    def check_md5(self):
        return self.get_url()[1] == self.get_md5()

    def md5(self):
        """check md5 sum of cached package against database"""
        if not os.path.exists(self.get_ball()):
            sys.stderr.write("%s: %s not installed. Exiting.\n"\
                % (os.path.basename(sys.argv[0]), self.packagename))
            return 1
        url, md5 = self.get_url()
        ball = os.path.basename(url)
        print('%s  %s' % (md5, ball))
        actual_md5 = self.get_md5()
        print('%s  %s' % (actual_md5, ball))
        if actual_md5 != md5:
            raise CygAptError("md5sum of cached package doesn't match md5 in setup.ini from mirror")

    def search(self):
        """search all package descriptions for string"""
        if not self.packagename:
            raise CygAptError("search command requires a string to search for")
        if not self.regex_search:
            regexp = re.escape(self.packagename)
        else:
            regexp = self.packagename
        packages = []
        keys = []
        if self.distname in self.dists:
            keys = list(self.dists[self.distname].keys())
        else:
            for i in list(self.dists.keys()):
                for j in list(self.dists[i].keys()):
                    if not j in keys:
                        keys.append(j)
        for i in keys:
            self.packagename = i
            if not regexp or re.search(regexp, i) \
               or re.search(regexp, self.get_field('sdesc')) \
               or re.search(regexp, self.get_field('ldesc')):
                if self.distname in self.dists:
                    if self.INSTALL in self.dists[self.distname][i]:
                        packages.append(i)
                else:
                    packages.append(i)
        for self.packagename in self.psort(packages):
            s = self.packagename
            d = self.get_field('sdesc') 
            if d:
                s += ' - %s' % d[1:-1]
            print(s)

    def show(self):
        """print package description"""
        s = self.packagename
        d = self.get_field('sdesc') 
        if d:
            s += ' - %s' % d[1:-1]
        ldesc = self.get_field('ldesc')
        if ldesc != "":
            print(s + "\n")
            print(ldesc)
        else:
            print("%s: not found in setup.ini: %s" % (self.sn, s))

    # return an array with all packages that must to be install
    def get_missing(self):
        reqs = self.get_requires()
        missingreqs = []  # List of missing package on requires list
        for i in reqs:
            if i not in self.installed[0]:
                missingreqs.append(i)
        if self.packagename not in self.installed[0]:
            missingreqs.append(self.packagename)
        if missingreqs and self.packagename not in missingreqs:
            sys.stderr.write('warning: missing packages: %s\n' % string.join(missingreqs))
        elif self.packagename in self.installed[0]:  # Check version
            ins = self.get_installed_version()
            new = self.get_version()
            if ins >= new:
                sys.stderr.write('%s is already the newest version\n' % self.packagename)
                # missingreqs.remove(self.packagename)
            elif self.packagename not in missingreqs:
                missingreqs.append(self.packagename)
        return missingreqs

    def missing(self):
        """print missing dependencies for package"""
        missing = self.get_missing()
        if len(missing) > 0:
            print(string.join(missing, '\n'))
        else:
            print("All dependent packages for %s installed" % self.packagename)

    def run_script(self, file_name, optional=True):
        if os.path.isfile(self.pm.map_path(file_name)):      
            sys.stderr.write('running: %(file_name)s\n' % vars())
            if self.cygwin_p:
                os.system("sh " + file_name)
                shutil.move(file_name, file_name + ".done")
            else:
                os.system(self.dos_bash + " --login -c " + file_name)
                mapped = self.pm.map_path(file_name)
                shutil.move(mapped, mapped + ".done")
        else:
            if not optional:
                sys.stderr.write("%s: WARNING couldn't find %s.\n"\
                    % (self.sn, file_name))

    def run_all(self, dirname):
        if os.path.isdir(dirname):
            lst = [x for x in os.listdir(dirname) if x[-3:] == '.sh']
            for i in lst:
                self.run_script('%s/%s' % (dirname, i))

    def do_install_external(self, tf):
        # Currently we use a temporary directory and extractall() then copy:
        # this is very slow. The Python documentation warns more sophisticated
        # approaches have pitfalls without specifying what they are.
        members = tf.getmembers()
        tempdir = os.path.basename(tf.name) + "-tmp"
        tempdir = tempdir.replace(".tar.bz2", "")
        if os.path.exists(tempdir):
            print >> sys.stderr, \
            ("%s: tmpdir %s exists, won't overwrite.\nInstall "\
            "of %s failed. exiting." % self.sn, tempdir, self.packagename)
            sys.exit(1)
        try:
            tf.extractall(tempdir)
            for m in members:
                if m.isdir():
                    path = self.pm.map_path("/" + m.name)
                    if not os.path.exists(path):
                        os.makedirs(path, m.mode)
            for m in members:
                if m.isdir():
                    path = self.pm.map_path("/" + m.name)
                    if not os.path.exists(path):
                        os.makedirs(path, m.mode)
                else:
                    path = self.pm.map_path("/" + m.name)
                    dirname = os.path.dirname(path)
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    if os.path.exists(path):
                        os.chmod(path, 0o777)
                        os.remove(path)
                    # Windows extract() is robust but can't form Cygwin links
                    # (It produces copies instead: bulky and bugbait.)
                    # Convert to links if possible -- depends on coreutils being installed
                    if m.issym() and self.can_use_ln:
                        link_filename = "/" + m.name
                        link_target = m.linkname
                        os.system(self.dos_ln + " -s " + link_target + " " + link_filename)
                    elif m.islnk() and self.can_use_ln:
                        # Hard link -- expect these to be very rare
                        link_filename = "/" + m.name
                        link_target = m.linkname
                        mapped_target = self.pm.map_path("/" + m.linkname)
                        # Must ensure target exists before forming hard link
                        if not os.path.exists(mapped_target):
                            shutil.move(tempdir + "/" + link_target, mapped_target)
                        os.system(self.dos_ln + " /" + link_target + " " + link_filename) 
                        
                    else:
                        shutil.move(tempdir + "/" + m.name, path)
        finally:
            cautils.rmtree(tempdir)

    def do_install(self):
        ball = self.get_ball()
        if tarfile.is_tarfile(ball):
            tf = tarfile.open(ball)
            if self.cygwin_p:
                tf.extractall(self.ABSOLUTE_ROOT)
            else:
                self.do_install_external(tf)
            # Force slash to the end of each directories
            members = tf.getmembers()
            lst = []
            for m in members:
                if m.isdir() and not m.name.endswith("/"):
                    lst.append(m.name + "/")
                else:
                    lst.append(m.name)
        else:
            print >> sys.stderr, \
            ("%s: bad tarball %s. Install failed." % self.sn, ball)
            return
        self.write_filelist(lst)
        self.installed[0][self.packagename] = os.path.basename(ball)
        self.write_installed()

    def get_filelist(self):
        filelist_file = "%s/%s.lst.gz" % (self.config, self.packagename)
        if not os.path.exists(filelist_file):
            if self.packagename not in self.installed[0]:
                raise CygAptError(self.packagename + " is not installed")
            else:
                raise CygAptError(self.packagename + " is installed, but " + \
                    filelist_file + " is missing")
        lst = gzip.GzipFile(filelist_file).readlines()
        lst = [x.strip() for x in lst]
        return lst

    def touch(self, fname, times=None):
        f = file(fname, 'a')
        os.utime(fname, times)
        f.close()

    def write_filelist(self, lst):
        gz_filename = '%s/%s.lst.gz' % (self.config, self.packagename)
        lst_cr = [x + "\n" for x in lst]

        # create iostring and write in gzip
        lst_io = io.StringIO()
        lst_io_gz = gzip.GzipFile(fileobj=lst_io, mode='wb')
        lst_io_gz.writelines(lst_cr)
        lst_io_gz.close()

        # save it in the file
        lst_gz = open(gz_filename, 'wb')
        lst_gz.write(lst_io.getvalue())
        lst_gz.close()
        lst_io.close()

        stat_struct = os.stat(self.setup_ini)
        atime = stat_struct[7]
        mtime = stat_struct[8]
        self.touch(gz_filename, (atime, mtime))

    def remove_filelist(self):
        lst_name = '%s/%s.lst.gz' % (self.config, self.packagename)
        if os.path.exists(lst_name):
            os.remove(lst_name)
        else:
            sys.stderr.write('%S: warning %s no such file\n' % \
                 (sys.argv[0], lst_name))

    def uninstall_want_file_removed(self, filename, noremoves, nowarns):
        # Returns true if the path from the tarball should result in a file # removal operation, false if not.
        if not os.path.exists(filename) and not os.path.islink(filename):
            if filename not in nowarns:
                sys.stderr.write('warning: %s no such file\n' % filename)
            return False
        elif not os.path.isdir(filename) and filename not in noremoves:
            return True

    def do_uninstall(self):
        postremove_sh = self.postremove_dir + "/" + self.packagename + ".sh"
        postinstall_sh = self.postinstall_dir + "/" + self.packagename + ".sh"
        preremove_sh = self.preremove_dir + "/" + self.packagename + ".sh"

        postinstall_done = self.postinstall_dir + "/" + self.packagename + ".sh.done"
        suppression_msg = \
            "%s: postremove suppressed: \"%s postremove %s\" to complete." % \
            (self.sn, self.sn, self.packagename)

        lst = self.get_filelist()
        expect_preremove = preremove_sh[1:] in lst
        expect_postremove = postremove_sh[1:] in lst

        if not self.nopostremove:
            if expect_preremove:
                self.run_script(preremove_sh, optional=False)
        else:
            print >> sys.stderr, ("%s" % suppression_msg)

        # We don't expect these to be present: they are executed 
        # and moved to $(packagename).sh.done
        nowarns = []
        nowarns.append(self.pm.map_path(postinstall_sh))
        nowarns.append(self.pm.map_path(preremove_sh))

        noremoves = []
        if self.nopostremove:
            noremoves.append(self.pm.map_path(preremove_sh))
        noremoves.append(self.pm.map_path(postremove_sh))

        # remove files
        for i in lst:
            filename = self.pm.map_path("/" + i)
            if os.path.isdir(filename):
                continue
            if (self.uninstall_want_file_removed(filename, noremoves, nowarns)):
                if os.path.exists(filename):
                    if self.cygwin_p:
                        os.chmod(filename, 0o777)
                    if os.remove(filename):
                        raise IOError
                else:
                    if os.path.islink(filename):
                        os.remove(filename)
                    else:
                        print("%s: warning: expected to remove %s but it was"\
                            " not there." % (self.sn, filename))
        if not self.nopostremove:
            if expect_postremove:
                self.run_script(postremove_sh, optional=False)
            if os.path.isfile(self.pm.map_path(postremove_sh)):
                if os.remove(self.pm.map_path(postremove_sh)):
                    raise IOError

        # We don't remove empty directories: the problem is are we sure no other
        # package is depending on them.

        # setup.exe removes the filelist when a package is uninstalled: we try to be
        # as much like setup.exe as possible
        self.remove_filelist()

        # Clean up the postintall script: it's been moved to .done
        if os.path.isfile(self.pm.map_path(postinstall_done)):
            os.remove(self.pm.map_path(postinstall_done))

        # update installed[]
        del(self.installed[0][self.packagename])
        self.write_installed()

    def remove(self):
        """uninstall packages"""
        barred = []
        for self.packagename in self.files[1:]:
            if self.packagename not in self.installed[0]:
                sys.stderr.write('warning: %s not installed\n' % self.packagename)
                continue
            if self.is_barred_package(self.packagename):
                barred.append(self.packagename)
                continue
            sys.stderr.write('uninstalling %s %s\n' \
                      % (self.packagename,
                         self.version_to_string(self.get_installed_version())))
            self.do_uninstall()
        self.barred_warn_if_need(barred, "removing")

    def purge(self):
        """uninstall packages and delete from cache"""
        barred = []

        for self.packagename in self.files[1:]:
            try:
                if self.packagename in self.installed[0]:
                    if self.is_barred_package(self.packagename):
                        barred.append(self.packagename)
                        continue
                    sys.stderr.write('uninstalling %s %s\n' \
                        % (self.packagename,
                        self.version_to_string(self.get_installed_version())))
                    self.do_uninstall()
                scripts = [self.postinstall_dir + "/%s.sh.done", \
                    self.preremove_dir + "/%s.sh.done", \
                    self.postremove_dir + "/%s.sh.done"]
                scripts = [s % self.packagename for s in scripts]
                scripts = [self.pm.map_path(s) for s in scripts]
                for s in scripts:
                    if os.path.exists(s):
                        os.remove(s)
                ball = self.get_ball()
                if os.path.exists(ball):
                    print("%s: removing %s" % (self.sn, ball))
                    os.remove(ball)
            except SetupIniError as xxx_todo_changeme1:
                (err) = xxx_todo_changeme1
                sys.stderr.write(self.sn + ": " + err.msg + \
                    " exiting.\n")
                sys.exit(1)
        self.barred_warn_if_need(barred, "purging")

    def barred_warn_if_need(self, barred, command):
        num_barred = len(barred)
        if num_barred > 0:
            if num_barred == 1:
                this_these = "this package"
            else:
                this_these = "these packages"
            barredstr = " " + string.join(barred, ", ")
            print >> sys.stderr, (self.sn + ": NOT " + command + \
                barredstr + ": " + self.sn + " is dependent on " + \
                this_these + " under Cygwin.")
            if not self.cygwin_p:
                print >> sys.stderr, \
                ("Use -f to override but proceed with caution.")

    def install(self):
        """download and install packages with dependencies"""
        suppression_msg = \
            "%s: postinstall suppressed: \"%s postinstall\" to complete." % \
            (self.sn, self.sn)
        missing = {}
        barred = []
        for self.packagename in self.files[1:]:
            missing.update(dict([(x, 0) for x in self.get_missing()]))

        if len(missing) > 1:
            sys.stderr.write('to install: \n')
            sys.stderr.write('    %s' % string.join(list(missing.keys())))
            sys.stderr.write('\n')

        for self.packagename in list(missing.keys()):
            if not self.get_url():
                del missing[self.packagename]

        for self.packagename in list(missing.keys()):
            if self.is_barred_package(self.packagename):
                barred.append(self.packagename)
                del missing[self.packagename]

        for self.packagename in list(missing.keys()):
            self.download()
        if self.download_p:
            sys.exit(0)
        for self.packagename in list(missing.keys()):
            if self.packagename in self.installed[0]:
                sys.stderr.write('preparing to replace %s %s\n' \
                    % (self.packagename, self.version_to_string(self.get_installed_version())))
                self.do_uninstall()
            sys.stderr.write('installing %s %s\n' \
                  % (self.packagename, self.version_to_string(self.get_version())))
            self.do_install()
            
        if self.nopostinstall:
            print >> sys.stderr, ("%s" % suppression_msg)
        else:
            self.postinstall()

        self.barred_warn_if_need(barred, "installing")

        # TODO: do somethings when installation fail
        self.check(missing)


    def check(self, checklist=[]):
        """show installed version of PACKAGE and verify integrity
                (or for all installed packages if none specified)
        """

        if len(checklist) == 0:
            checklist = self.files[1:]

        options = "-c "
        if self.verbose:
            options += '-v '

        pkg_lst = string.join(checklist)
        command = ''
        if not self.cygwin_p:
            command += self.dos_bash + ' --login -c '
            command += "'"
        command += 'cygcheck '
        command += options
        command += pkg_lst
        if not self.cygwin_p:
            command += "'"

        outputlines = os.popen(command).readlines()

        unformat = ''
        start = False
        incomplete = []
        for res in outputlines:
            try:
                res_split = res.split()
                package, version, status = res_split
            except ValueError:
                if len(res_split) > 0:
                    unformat += res
                continue

            if package == 'Package' and \
               version == 'Version' and \
                status == 'Status':
                start = True
                unformat = ''
            elif not start:
                continue

            if start and status == 'Incomplete':
                print(res[:-2])
                print(unformat)
                unformat = ''
                incomplete.append(package)
            else:
                print(res[:-2])
                unformat = ''

        return incomplete

    def upgrade(self):
        """all installed packages"""
        self.files[1:] = self.get_new()
        self.install()

    def printerr(self, err):
        print("%s: %s" % self.sn, err)

    def do_unpack(self):
        ball = self.get_ball()
        basename = os.path.basename(ball)
        self.packagename = re.sub('(-src)*\.tar\.(bz2|gz)', '', basename)
        if os.path.exists(self.packagename):
            self.printerr(self.packagename + " already exists. Not overwriting.\n")
            return 1
        os.mkdir(self.packagename)
        if tarfile.is_tarfile(ball):
            tf = tarfile.open(ball)
            tf.extractall(self.packagename)
        else:
            print >> sys.stderr, \
            ("%s: bad source tarball %s, exiting.\n%s: SOURCE UNPACK FAILED"\
             % self.sn, ball, self.sn)
            sys.exit(1)
        if not os.path.exists(self.packagename):
            raise IOError
        print(self.packagename)

    def source(self):
        """download source package"""
        self.INSTALL = 'source'
        for self.packagename in self.files[1:]:
            self.download()
            self.do_unpack()
        sys.exit(0)

    def find(self):
        """find package containing file"""
        if self.regex_search:
            file_to_find = self.packagename
        else:
            file_to_find = re.escape(self.packagename)
        hits = []
        for self.packagename in self.psort(list(self.installed[0].keys())):
            filenames_file = "%s/%s.lst.gz" % (self.config, self.packagename)
            if not os.path.exists(filenames_file):
                continue
            files = self.get_filelist()
            for i in files:
                if re.search(file_to_find, '/%s' % i):
                    hits.append('%s: /%s' % (self.packagename, i))
        print((string.join(hits, '\n')))

    def set_root(self, root):
        if len(root) < 1 or root[-1] != "/":
            print("%s: ROOT must end in a slash. Exiting." % self.sn)
            sys.exit(1)
        self.PREFIX_ROOT = root[:-1]
        self.ABSOLUTE_ROOT = root

    def get_rc(self, h):
        for i in h.readlines():
            result = self.rc_regex.search(i)
            if result:
                k = result.group(1)
                v = result.group(2)
                if k in self.rc_options:
                    self.__dict__[k] = eval(v)
        h.close()
        if not self.cache:
            print("%s: %s doesn't define cache. Exiting." % (self.sn, self.cyg_apt_rc))
            sys.exit(1)
        if not self.mirror:
            print("%s: %s doesn't define mirror. Exiting." % (self.sn, self.cyg_apt_rc))
            sys.exit(1)

        # We want ROOT + "/etc/setup" and cd(ROOT) to work: 
        # necessitates two different forms, prefix and absolute
        if(self.cygwin_p):
            self.set_root("/")
        else:
            self.set_root(self.ROOT)
        self.ROOT = None
        self.pm = PathMapper(self.PREFIX_ROOT, self.cygwin_p)
        self.config = self.pm.map_path("/etc/setup")
        self.cache = self.pm.map_path(self.cache)
        self.downloads = self.cache + '/' + urllib.quote(self.mirror, '').lower()
        self.installed_db = self.config + '/installed.db'

        # It might seem odd that we don't map these paths: we need
        # to retain unmapped forms since under DOS we invoke Cygwin bash to
        # run these scripts unless flagged not to
        self.postinstall_dir = "/etc/postinstall"
        self.postremove_dir = "/etc/postremove"
        self.preremove_dir = "/etc/preremove"
        
        self.setup_ini = self.pm.map_path(self.setup_ini)
        self.dos_bin_dir = self.pm.mountroot + "/bin"
        self.dos_bash = self.pm.mountroot + "bin/bash"
        self.dos_ln = self.pm.mountroot + "bin/ln"
        return 0

    def is_barred_package(self, package):
        return (not self.nobarred) and package in self.barred

class AppConflictError(CygAptError):
    def __init__(self, *args):
        CygAptError.__init__(self, *args)

class SetupIniError(CygAptError):
    def __init__(self, *args):
        CygAptError.__init__(self, *args)
