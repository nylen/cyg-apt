#!/usr/bin/python
import pdb
import argparse
import os
import re
import sys
import __main__
from utilpack import path


#.cyg-apt
#ROOT="/."
#MKNETREL="/."
#NETREL="/."
#mirror="http://wanda/~chrisc/"
#cache="/e/home/application_data/cygwin_1_7/"
#setup_ini="/./etc/setup/setup-2.ini"
#distname="curr"

    
def main():
    parser =  argparse.ArgumentParser(description = "Remove a package from the package cache.")
    parser.add_argument("pkg",\
        help="The package to remove", metavar="PKG")

    options = parser.parse_args()
    
    config = file(".cyg-apt").readlines()
    cache_tag = "cache"
    cache_tag_size = len(cache_tag)
    for l in config:
        k, v = l.split ('=', 2)
        __main__.__dict__[k] = eval (v)
    
    c = path(cache)
    cache_files = c.files()
    for f in cache_files:
        if options.pkg in f:
            #print f
            os.system("rm " + f)
    
    



if __name__ == "__main__":
    main()
    
