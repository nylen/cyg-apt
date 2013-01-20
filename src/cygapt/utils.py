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
import os;
import re;
import shutil;
import sys;
import urlparse;

from error import CygAptError;
from url_opener import CygAptURLopener;

def cygpath(path):
    p = os.popen("cygpath \"{0}\"".format(path));
    dospath = p.read().strip();
    p.close();
    return dospath;

def parse_rc(cyg_apt_rc):
    # Currently main only needs to know if we alway call the update command
    # before other commands
    f = open(cyg_apt_rc);
    lines = f.readlines();
    f.close();
    rc_regex = re.compile("^\s*(\w+)\s*=\s*(.*)\s*$");
    always_update = False;
    for i in lines:
        result = rc_regex.search(i);
        if result:
            k = result.group(1);
            v = result.group(2);
            if k == "always_update":
                always_update = eval(v);

    if always_update in [True, 'True', 'true', 'Yes', 'yes']:
        always_update = True;
    else:
        always_update = False;

    return always_update;

def prsort(lst):
    lst.sort();
    lst.reverse();
    return lst;

def rename(src, dest):
    if os.path.exists(dest):
        os.remove(dest);
    os.rename(src, dest);

def rmtree(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            rmtree_helper(path);
            shutil.rmtree(path);
        else:
            os.chmod(path, 0o777);
            os.remove(path);

def rmtree_helper(path):
    if os.path.isdir:
        files = os.listdir(path);
        for x in files:
            fullpath = os.path.join(path, x);
            os.chmod(fullpath, 0o777);
            if os.path.isdir(fullpath):
                rmtree_helper(fullpath);

def uri_get(directory, uri, verbose=False):
    up = urlparse.urlparse(uri);
    scriptname = os.path.basename(sys.argv[0]);

    if up.scheme == "file":
        shutil.copy(uri[7:], directory);
        if verbose:
            print("cp {0} {1}".format(uri[7:], directory));
    elif up.scheme == "http" or up.scheme == "ftp":
        url_base = os.path.basename(up.path);
        old_cwd = os.getcwd();
        os.chdir(directory);
        if verbose:
            print("\r{0}: downloading: {1}".format(scriptname, uri));
        try:
            opener = CygAptURLopener(verbose);
            opener.retrieve\
                (uri, url_base + ".tmp", reporthook=opener.dlProgress);
        except IOError:
            opener.setErrorCode(1);
        finally:
            opener.close();
        if (opener.getErrorCode() == 200):
            rename(url_base + ".tmp", url_base);
        else:
            if os.path.exists(url_base + ".tmp"):
                os.remove(url_base + ".tmp");
            os.chdir(old_cwd);
            raise CygAptError("{0} unreached URL {1}\n"\
                              "".format(opener.getErrorCode(),
                                        uri));
        os.chdir(old_cwd);
    else:
        raise CygAptError("bad URL {0}".format(uri));
