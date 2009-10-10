#!/usr/bin/python
import pdb
import argparse
import os
import re
import sys
from subprocess import Popen
from subprocess import PIPE


def popen(cmd):
    return Popen(cmd, stdout=PIPE).communicate()[0]

    
def main():
    parser =  argparse.ArgumentParser(description =\
        "Creates md5.sum file for a dir in that dir")
    parser.add_argument("src",\
        help="Concatenate md5sum output for all files in SRC", metavar="SRC")
    parser.add_argument("md5_file", nargs="?",\
        help="Filename for md5.sum output.", metavar="MD5FILE", default="md5.sum")
    parser.add_argument("-f", "--overwrite",
                  action="store_true", dest="overwrite", default=False,
                  help="If the output file exists, overwrite it. Otherwise error exit.")
    parser.add_argument("-i", "--ignore", dest="ignore", default=["md5.sum"], nargs="*", help="ignore these files")
    

    options = parser.parse_args()
    if not os.path.isdir(options.src):
        parser.print_usage()
        return 1
        
    wd = os.getcwd()
    os.chdir(options.src)
    files = os.listdir(".")
    out = []
    for f in files:
        if f in options.ignore:
            print sys.argv[0] + ": Ignoring " + f
            continue
        md5 = popen(["md5sum", f])
        md5 = md5.replace("*","")
        out.append(md5)
    out.sort()
    os.chdir(wd)
   
    if os.path.exists(options.md5_file) and options.overwrite is False:
        print options.md5_file + " already exists, not overwriting."
        return 1
    outfile = file(options.md5_file, "w")
    outfile.writelines(out)
    

    return 0



if __name__ == "__main__":
    main()
    
