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
* `python` 2.6+, <3.0
* `python-argparse` 1.2+


Build requirements
------------------

* `make` 3.80+
* `git` 1.7+


Install instructions
--------------------

Briefly the following commands should build, test and install this package.
 * $ `make`
 * $ `make test`
 * $ `make install`

See the [INSTALL][0] file for more detailed instructions.


HELP
----

* $ `cyg-apt --help`
* $ `man cyg-apt`

TODO
----

* Add cygport support
* Add travis test
* Add missing tests

ACKNOWLEDGMENTS
---------------

The original cyg-apt was written by Jan Nieuwenhuizen.  Additional development
by Christopher Cormie (cjcormie@gmail.com), James Nylen (jnylen@gmail.com), and
Alexandre Quercia (alquerci@email.com).

[0]: INSTALL.md