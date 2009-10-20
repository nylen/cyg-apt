#!python
import pdb
import argparse
import os
import re
import sys
from pdb import set_trace as stra

    
def main():
    parser =  argparse.ArgumentParser(description = "Creates a .bat to reset cmd shell to default environment from a dump from a clean shell.")
    parser.add_argument("env_dump_file",\
        help="Environment dump from clean shell.", metavar="ENVDUMP")
    parser.add_argument("reset_bat_file",\
        help="Filename for reset batch file.", metavar="BATFILEOUT")
    parser.add_argument("-f", "--overwrite", dest="overwrite",
                  help="overwrite the output .bat if it exists", default=False, action="store_true")
    options = parser.parse_args()
    env_dump_file = options.env_dump_file
    reset_bat_file = options.reset_bat_file
    overwrite = options.overwrite
    
    ed = file(options.env_dump_file)
    bat = ["@ECHO OFF\n"]
    for l in ed.readlines():
        if "=" in l:
            bat.append("SET " + l)
    if not overwrite and os.path.exists(reset_bat_file):
        print reset_bat_file + " exists, not overwriting. Exit."
        sys.exit(1)
    bf = file(reset_bat_file,"w")
    bf.writelines(bat)
            




if __name__ == "__main__":
    main()
    
