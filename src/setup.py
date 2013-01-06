#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os

realpathfile = os.path.realpath(os.path.dirname(__file__))
realpathcwd = os.path.realpath(os.getcwd())

if realpathfile != realpathcwd:
    os.chdir(realpathfile)

try:
    version = os.environ['VERSION']
except KeyError:
    version = "1.1.0"

try:
    pkgname = os.environ['PYPKG']
except KeyError:
    pkgname = "cygapt"

long_description = open("../README.md").read()

setup(name=pkgname,
      packages=[pkgname],
      version=version,
      description="A Cygwin command line package management tool.",
      long_description=long_description,
      license="GNU GPLv3",
      url="https://github.com/alquerci/cyg-apt",
      author="Jan Nieuwenhuizen, Chris Cormie, James Nylen",
      author_email="cjcormie@gmail.com, janneke@gnu.org, jnylen@gmail.com",
      maintainer="Alexandre Quercia",
      maintainer_email="alquerci@email.com",
      platforms="cygwin",
      classifiers=[
          'Development Status :: 1 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License, Version 3',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          ],
      )

os.chdir(realpathcwd)
