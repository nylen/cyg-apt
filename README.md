cyg-apt
=======

A Cygwin command line package manager.

Like `apt-get`, `cyg-apt` allows you to install and remove packages on the Cygwin command line, and provides other package management functions.

This project is a fork of http://code.google.com/p/cyg-apt/ with extensive improvements and lots of bugfixes by [@alquerci](https://github.com/alquerci), [@nylen](https://github.com/nylen), and others.

Requirements
------------

* `cygwin` 1.7+
* `gnupg` 1.4+
* `python` 2.6+, &lt;3.0
* `python-argparse` 1.2+
* `xz` (should be installed with Cygwin by default)


Build requirements
------------------

* `make` 3.80+
* `git` 1.7+


Install instructions
--------------------

Briefly the following commands should build, test and install this package.

    $ make
    $ make test
    $ make install

See the [`INSTALL.md`](INSTALL.md) file for more detailed instructions.


Usage
-----

`cyg-apt` is similar to `apt-get`.  You can use it to install and remove packages (and more) from the Cygwin command prompt:

    $ cyg-apt install gdb
    ...
    $ gdb
    (gdb)
    $ cyg-apt remove gdb

Type `cyg-apt --help` or `man cyg-apt` to see all commands and options:

```
Usage: cyg-apt [OPTION]... COMMAND [PACKAGE]...

  Commands:
    setup    : create cyg-apt configuration file, it overwrite with -f option
    update   : fetch current package database from mirror
    ball     : print tarball name
    download : download package (only, do not install)
    filelist : list files installed by given packages
    find     : find package containing file
    help     : this help message
    install  : download and install packages with dependencies
    list     : list installed packages
    checksum : check digest of cached package against database
    missing  : print missing dependencies for package
    new      : list new (upgradable) packages in distribution
    purge    : uninstall packages and delete from cache
    remove   : uninstall packages
    requires : print requires: for package
    search   : search all package descriptions for string
    show     : print package description
    source   : download source package
    upgrade  : all installed packages
    url      : print tarball url
    version  : print installed version

  Options:
    -d, --download       download only
    -h, --help           show brief usage
    -m, --mirror=URL     use mirror
    -t, --dist=NAME      set dist name (curr, test, prev)
    -x, --no-deps        ignore dependencies
    -s, --regexp         search as regex pattern
    -f, --nobarred       add/remove packages cyg-apt depends on
    -X, --no-verify      do not verify setup.ini signatures
    -y, --nopostinstall  do not run postinstall scripts
    -z, --nopostremove   do not run preremove/postremove scripts
    -q, --quiet          loggable output - no progress indicator
```


Contributing
------------

Cyg-apt is an open source, community-driven project. All code contributions -
including those of people having commit access - must go through a pull request
and be approved by a core developer before being merged. This is to ensure
proper review of all the code.

If you would like to help, take a look at the
[list of issues](https://github.com/nylen/cyg-apt/issues).

See the [`CONTRIBUTING.md`](CONTRIBUTING.md) file for more detailed instructions.


Acknowledgments
---------------

The original cyg-apt was written by Jan Nieuwenhuizen <janneke@gnu.org>.

For a list of authors, please see the `AUTHORS` files.
