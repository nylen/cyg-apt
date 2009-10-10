#!/usr/bin/python
import pdb
import argparse
import os
import re
import sys
from utilpack import path


def hasfiles(to_check, ignore):
    p = path(to_check)
    fl = p.files()
    found = []
    for f in fl:
       if ignore not in f:
           found.append(f)
    if found:
        print sys.argv[0] + ": files exist"        
        for f in found:
            print f
    
def main():
    parser =  argparse.ArgumentParser(description = "Checks a directory recursively for any files, returns true if any files exist.")
    parser.add_argument("to_check",\
        help="Directory to check for files", metavar="DIR")
    parser.add_argument("ignore",\
        help="Ignore any path containing this string.", metavar="DIR", default="svn", nargs="?")

    #pdb.set_trace()
    options = parser.parse_args()
    hasfiles(options.to_check, options.ignore)

    
    
if __name__ == "__main__":
    main()
    
