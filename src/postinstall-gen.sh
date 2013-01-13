#!/bin/bash

if [ -z "$ID_PREFIX" ];
then
    ID_PREFIX="usr";
fi;

if [ -z "$ID_EXEC" ];
then
    ID_EXEC="$ID_PREFIX/bin";
fi;

if [ -z "$ID_DATA" ];
then
    ID_DATA="$ID_PREFIX/share";
fi;

if [ -z "$EXENAME" ];
then
    EXENAME="cyg-apt";
fi;

if [ -z "$GPG_CYGWIN_PUBKEY" ];
then
    GPG_CYGWIN_PUBKEY="cygwin.sig";
fi;

echo "#!/bin/bash
# Add Cygwin's public key to the gpg keyring
/usr/bin/gpg --import --no-secmem-warning \"$ID_ROOT/$ID_DATA/$EXENAME/$GPG_CYGWIN_PUBKEY\"

# Initialize $EXEC
\"$ID_ROOT/$ID_EXEC/$EXENAME\" setup
";

exit 0;