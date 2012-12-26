cyg-apt
=======

A Cygwin command line package management tool.
Allows you to install and remove packages on the command line, 
and provides other package management functions. 
It has a command syntax similar to apt-get and dpkg.

It's a fork of svn repository http://code.google.com/p/cyg-apt/

REQUIREMENTS
------------

* A base Cygwin installation.
* Cygwin `gnupg` package, under Utilities
* Cygwin Python, under Python. Currently this package is at Python 2.6.
  Python 3.0 is not currently  supported.

BUILDING
--------

* $ `make`

INSTALL
-------

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

The original cyg-apt was written by Jan Nieuwenhuizen. Additional development by Christopher Cormie. Questions and feedback to cjcormie@gmail.com.