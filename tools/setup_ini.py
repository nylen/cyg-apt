#!python
import pdb
import argparse
import os
import re
import sys
import string

def debug (s):
    s

"""
This is just cut-and-paste code from cyg-apt for parsing setup.ini
"""

dists = 0
def get_setup_ini (setup_ini_filename):
    global dists
    if dists:
        return
    dists = {'test': {}, 'curr': {}, 'prev' : {}}
    chunks = string.split (open (setup_ini_filename).read (), '\n\n@ ')
    for i in chunks[1:]:
        lines = string.split (i, '\n')
        name = string.strip (lines[0])
        debug ('package: ' + name)
        packages = dists['curr']
        records = {'sdesc': name}
        j = 1
        while j < len (lines) and string.strip (lines[j]):
            debug ('raw: ' + lines[j])
            if lines[j][0] == '#':
                j = j + 1
                continue
            elif lines[j][0] == '[':
                debug ('dist: ' + lines[j][1:5])
                packages[name] = records.copy ()
                packages = dists[lines[j][1:5]]
                j = j + 1
                continue

            try:
                key, value = map (string.strip,
                      string.split (lines[j], ': ', 1))
            except:
                print lines[j]
                raise 'URG'
            if value[0] == '"' and value.find ('"', 1) == -1:
                while 1:
                    j = j + 1
                    value += '\n' + lines[j]
                    if lines[j].find ('"') != -1:
                        break
            records[key] = value
            j = j + 1
        packages[name] = records

    
def main():
    parser =  argparse.ArgumentParser(description = "Typical usage goes here.")
    parser.add_argument("setup_ini_filename",\
        help="The Cygwin setup.ini file", metavar="INI")

    options = parser.parse_args()
    setup_ini = get_setup_ini(options.setup_ini_filename)
    selected = []
    for package in dists["curr"].keys():
         if "Base" in dists["curr"][package]["category"]:
             selected.append(package)
    selected.sort()
    for i in selected:
        print i
    
    



if __name__ == "__main__":
    main()
    
