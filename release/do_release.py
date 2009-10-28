#!python
import pdb
import argparse
import os
import re
import sys
import shutil
from pdb import set_trace as stra

def rmtree_helper(path):
    if os.path.isdir:
        files = os.listdir(path)
        for x in files:
            fullpath = os.path.join(path, x)
            os.chmod(fullpath, 0777)
            if os.path.isdir(fullpath):
                rmtree_helper(fullpath)


def rmtree(path):
    if os.path.exists(path):
        if os.path.isdir(path):
            rmtree_helper(path)
            shutil.rmtree(path)
        else:
            os.chmod(path, 0777)
            os.remove(path)
            
def main():
    parser =  argparse.ArgumentParser(description = "Performs the cyg-apt release build.")
    parser.add_argument("rel",\
        help="The release number", metavar="REL")
    parser.add_argument("-f", "--force", dest="force",
                  help="overwrite if release already exisits", default=False, action="store_true")
    options = parser.parse_args()
    rel = options.rel
    reldir = "cyg-apt-" + rel
    relfn = reldir + ".tar.bz2"
    force = options.force
    if os.path.exists(reldir):
        if force:
            print "Nuking: " + reldir
            rmtree(reldir)
        else:
            print reldir + " exists. Use -f to overwrite. exiting."
            sys.exit(1)
        
        
    
    os.makedirs(reldir)
    shutil.copy("../cyg-apt",reldir)
    shutil.copy("README.txt", reldir)
    print "tar -jcf " + relfn + " " + reldir
    os.system("tar -jcf " + relfn + " " + reldir)
    print "tar -tvf " + relfn
    os.system("tar -tvf " + relfn)



if __name__ == "__main__":
    main()
    
