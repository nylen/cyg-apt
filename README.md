cyg-apt
=======

A Cygwin command line package manager.

Like `apt-get`, `cyg-apt` allows you to install and remove packages on the Cygwin command line, and provides other package management functions.

This project is a fork of http://code.google.com/p/cyg-apt/ with extensive improvements by [@alquerci](https://github.com/alquerci), [@nylen](https://github.com/nylen), and others.

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

cyg-apt is similar to apt-get.
You can install, use it and remove packages from the Cygwin command prompt:

    $ cyg-apt install gdb
    ...
    $ gdb
    (gdb)
    $ cyg-apt remove gdb

Type `cyg-apt --help` or `man cyg-apt` for see all commands and options.


Acknowledgments
---------------

The original cyg-apt was written by Jan Nieuwenhuizen <janneke@gnu.org>.

For a list of authors, please see the `AUTHORS` files.
