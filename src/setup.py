#!/usr/bin/env python
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

from distutils.core import setup;
import os;

realpathfile = os.path.realpath(os.path.dirname(__file__));
realpathcwd = os.path.realpath(os.getcwd());

if realpathfile != realpathcwd:
    os.chdir(realpathfile);

try:
    version = os.environ['VERSION'];
except KeyError:
    version = "1.1.0rc1";

try:
    pkgname = os.environ['PYPKG'];
except KeyError:
    pkgname = "cygapt";

f = open("../README.md");
long_description = f.read();
f.close();

setup(
    name=pkgname,
    packages=[
        'cygapt',
        'cygapt.process',
        'cygapt.test',
        'cygapt.test.case',
        'cygapt.test.case.py2',
        'cygapt.test.case.py2.minor6',
    ],
    package_data={pkgname: [
        'LICENSE',
        'test/fixtures/utils/*',
    ]},
    version=version,
    description="A Cygwin command line package management tool.",
    long_description=long_description,
    license="GPL-3.0",
    url="https://github.com/nylen/cyg-apt",
    author="Jan Nieuwenhuizen, Chris Cormie, James Nylen, Alexandre Quercia",
    author_email="cjcormie@gmail.com, janneke@gnu.org, jnylen@gmail.com, alquerci@email.com",
    maintainer="Alexandre Quercia",
    maintainer_email="alquerci@email.com",
    platforms="cygwin",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License, Version 3',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
);

os.chdir(realpathcwd);
