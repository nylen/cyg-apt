#!/usr/bin/sh

cd "$(dirname "$0")"

# Add Cygwin's public key to the gpg keyring
gpg --import --no-secmem-warning cygwin.sig

# Copy cyg-apt
cp -vf cyg-apt /usr/local/bin/

# Initialize cyg-apt
./cyg-apt setup
