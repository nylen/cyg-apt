#!/usr/bin/sh

echo "Uncomment this line in setup.sh, replacing the given server with a URL to
 a server you have scp access to. Alternatively you might want to move this
line to your .bashrc"
echo "#export CYGAPT_TESTMIRROR=chrisc@wanda:~/public_html"
#export CYGAPT_TESTMIRROR=chrisc@wanda:~/public_html

echo "Install Python module used by test-cyg-apt.py"
python tools/utilpack/setup.py install