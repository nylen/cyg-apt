#!/usr/bin/sh
# Add Cygwin's public key to the gpg keyring
gpg --import --no-secmem-warning cygwin.sig
cp -f cyg-apt /usr/bin/
cyg-apt setup