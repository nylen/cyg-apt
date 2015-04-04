News
====

* 2.0.0 ()

  * Removed the `setup_ini` configuration field

    Before:

    The `setup.ini` database is located at the following paths:

      - `<cachedir>/<mirror>/<arch>/setup.ini`

      - according to the value of the `setup_ini` configuration field,
          with the default one `/etc/setup/setup.ini`

    After:

    The `setup.ini` database is only located at the following path:

      - `<cachedir>/<mirror>/<arch>/setup.ini`

  * Removed the `md5` command, use `checksum` instead.

* 1.2.0 ()

  * Added `checksum` command.
