#!/bin/bash

if [ -z "$PREFIX" ];
then
    PREFIX="/usr";
fi;

if [ -z "$EXEC" ];
then
    EXEC="cyg-apt";
fi;

if [ -z "$GPG_CYGWIN_PUBKEY" ];
then
    GPG_CYGWIN_PUBKEY="cygwin.sig";
fi;

echo "#!/bin/bash
# Add Cygwin's public key to the gpg keyring
gpg --import --no-secmem-warning \"$PREFIX/share/$EXEC/$GPG_CYGWIN_PUBKEY\"

# Initialize $EXEC
cyg-apt setup
";

exit 0;