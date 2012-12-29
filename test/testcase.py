"""
"""

import unittest
import os
import tempfile

class TestCase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self._var_tmpdir = tempfile.mkdtemp()
        self._var_old_cwd = os.getcwd()
        os.chdir(self._var_tmpdir)
        self._var_exename = "cyg-apt"
        self._var_mirror = "http://cygwin.xl-mirror.nl/"
        self._var_old_env = os.environ
        
        # unix tree
        self._dir_mtroot = self._var_tmpdir + "/"
        self._dir_tmp = os.path.join(self._dir_mtroot, "tmp")
        self._dir_prefix = os.path.join(self._dir_mtroot, "usr")
        self._dir_sysconf = os.path.join(self._dir_mtroot, "etc")
        self._dir_localstate = os.path.join(self._dir_mtroot, "var")
        self._dir_home = os.path.join(self._dir_mtroot, "home")
        self._dir_libexec = os.path.join(self._dir_prefix, "lib")
        self._dir_data = os.path.join(self._dir_prefix, "share")
        self._dir_man = os.path.join(self._dir_data, "man")
        self._dir_info = os.path.join(self._dir_data, "info")
        # bulld unix tree
        os.mkdir(self._dir_tmp)
        os.mkdir(self._dir_prefix)
        os.mkdir(self._dir_sysconf)
        os.mkdir(self._dir_localstate)
        os.mkdir(self._dir_home)
        os.mkdir(self._dir_libexec)
        os.mkdir(self._dir_data)
        os.mkdir(self._dir_man)
        os.mkdir(self._dir_info)
        
        # exe tree
        self._dir_confsetup = os.path.join(self._dir_sysconf, "setup")
        self._dir_user = os.path.join(self._dir_home, "user")
        self._dir_execache = os.path.join(self._dir_localstate, "cache",
                                          self._var_exename)
        self._dir_exedata = os.path.join(self._dir_data, self._var_exename)
        # build exe tree
        os.mkdir(self._dir_confsetup)
        os.mkdir(self._dir_user)
        os.makedirs(self._dir_execache)
        os.mkdir(self._dir_exedata)
        
        # exe files
        self._file_cygwin_sig   = os.path.join(self._dir_exedata,
                                               "cygwin.sig")
        self._file_installed_db = os.path.join(self._dir_confsetup,
                                               "installed.db")
        self._file_setup_ini    = os.path.join(self._dir_confsetup,
                                               "setup.ini")
        self._file_setup_rc     = os.path.join(self._dir_confsetup,
                                               "setup.rc")
        self._file_user_config  = os.path.join(self._dir_user,
                                               "." + self._var_exename)
        
        open(self._file_setup_rc, "wb").write(r"""
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
""".format(self._dir_execache, self._var_mirror, "\t"))
                
        os.environ['TMP'] = self._dir_tmp
        os.environ['HOME'] = self._dir_user
        

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
