cyg-apt
=======

A Cygwin command line package management tool that allows you to install and
remove packages on the command line, and provides other package management
functions.  It has a command syntax similar to `apt-get` and `dpkg`.

The project's original SVN repository is here:
http://code.google.com/p/cyg-apt/

REQUIREMENTS
------------

* A Cygwin base installation v1.7+
* `gnupg` v1.4+, under `Utils` category
* `python` v2.6+, <3.0, under `Python` category
* `python-argparse` v1.2+, under `Python` category
* `make` v3.82+, under `Devel` category

BUILDING
--------

* $ `make`

INSTALL
-------

* $ `make test`
* $ `make install`

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
