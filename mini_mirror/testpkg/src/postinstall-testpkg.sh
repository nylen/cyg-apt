#!/bin/sh
# Postinstall script for testpkg.

/usr/bin/mkdir -p /usr/share/doc/testpkg
/usr/bin/echo "Hello from the testpkg postinstall script." > /usr/share/doc/testpkg/README
