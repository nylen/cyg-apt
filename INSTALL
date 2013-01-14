Installation Instructions
*************************

Copyright (C) 1994-1996, 1999-2002, 2004-2012 Free Software Foundation,
Inc.

   Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without warranty of any kind.

Basic Installation
==================

   Briefly, the shell commands `make; make install` should
build, and install this package.

   The simplest way to compile this package is:

  1. `cd` to the directory containing the package's source code and type
     `make package` to compile the package.

  2. Optionally, type `make test` to run any self-tests that come with
     the package, generally using the just-built uninstalled binaries.

  3. Type `make install` to install the programs and any data files and
     documentation.  When installing into a prefix owned by root, it is
     recommended that the package be configured and built as a regular
     user, and only the `make install` phase executed with root
     privileges.

  4. Optionally, type `make installtest` to repeat any self-tests, but
     this time using the binaries in their final installed location.
     This target does not install anything.  Running this target as a
     regular user, particularly if the prior `make install` required
     root privileges, verifies that the installation completed
     correctly.

  5. You can remove the program binaries and object files from the
     source code directory by typing `make clean`. To also remove all
     genereted fils type `make mrproper`.

Installation Names
==================

   By default, `make install` installs the package's commands under
`/usr/bin`, share files under `/usr/share`, etc.
