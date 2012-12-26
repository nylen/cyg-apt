#!/bin/bash

if [ -z "$ID_DATA" ];
then
    ID_DATA="usr/share";
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
gpg --import --no-secmem-warning \"$ID_ROOT/$ID_DATA/$EXENAME/$GPG_CYGWIN_PUBKEY\"

# Initialize $EXEC
$EXENAME setup
";

exit 0;