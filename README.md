cyg-apt
=======

A Cygwin command line package management tool that allows you to install and
remove packages on the command line, and provides other package management
functions.  It has a command syntax similar to `apt-get` and `dpkg`.

The project's original SVN repository is here:
http://code.google.com/p/cyg-apt/

Requirements
------------

* `cygwin` 1.7+
* `gnupg` 1.4+
* `python` 2.6+, &lt;3.0
* `python-argparse` 1.2+


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

See the [`INSTALL.md`](blob/master/INSTALL.md) file for more detailed instructions.


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
