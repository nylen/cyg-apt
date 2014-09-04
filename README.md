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

Type `cyg-apt --help` or `man cyg-apt` for see all commands and options.


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
