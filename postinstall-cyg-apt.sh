#!/usr/bin/sh
# Add Cygwin's public key to the gpg keyring
gpg --import --no-secmem-warning /usr/share/cyg-apt/cygwin.sig
cyg-apt setup