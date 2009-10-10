#!python
import pdb
import argparse
import os
import re
import sys
import string
from utilpack import path
from subprocess import Popen
from subprocess import PIPE


def popen(cmd):
    spl = cmd.split()
    return Popen(spl, stdout=PIPE).communicate()[0]
    
def debug (s):
    s

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

def error (msg):
    print sys.argv[0] + ": " + msg
    


def find_line(inifile, target_package, section, filename):
    ini = file(inifile).readlines()
    tpmarkerlen= len(target_package) + 2
    ln = 0
    found = False
    for l in ini:        
        if l[0:tpmarkerlen] == "@ " + target_package:
            found = True
            break
        ln = ln + 1
    
    if not found:
        error("urg")
        return None
    
    endln = len(ini)
    while ln < endln:
        #print ini[ln]
        if section in ini[ln]:
            return ln, ini[ln]
        ln += 1
    raise("urg")
             
                

 
def gen_diff(diff_filename, packagename, linenum, oldline,\
    filename, basename, section):
    # Generate the md5
    md5 = popen("md5sum " + filename).split()[0]
    
    # Generate the length
    len = str(os.stat(filename).st_size)
    
    # Generate the new line
    #install: release-2/testpkg/testpkg-0.0.1-0.tar.bz 3140 fbbe05f50b9273be640c312857f70619
    newline = section + ": " + "release-2/" + packagename + "/" + basename + " " + len + " " + md5 + "\n"
    
    # Use the old and new lines to create a diff
#19916c19916
#< install: release-2/testpkg/testpkg-0.0.1-0.tar.bz 3140 fbbe05f50b9273be640c312857f70619
#---
#> install: release-2/testpkg/testpkg-0.0.1-0.tar.bz 3140 69906b3bc3a249056201c398cb928bef


    # Add one: we're zerobase internally but diff is 1 based linenumbers
    diff = [0,0,0,0]
    diff[0] = str(linenum + 1) + "c" + str(linenum + 1) + "\n"
    diff[1] = "< " + oldline
    diff[2] = "---\n"
    diff[3] = "> " + newline
    # Return the diff
    return diff
    
def main():
    global dists
    parser =  argparse.ArgumentParser(description = " Fixes md5sum in setup-2.ini to match newly built package. It is an error for given files not to exist in the .ini under that package."\
    "Example usage: " + sys.argv[0] + " testpkg test-pkg-0.0.1-0-src.tar.bz test-pkg-0.0.1-0.tar.bz"
    
    )
    
    parser.add_argument("inifile",\
        help="The setup.ini to patch.", metavar="INI")

    parser.add_argument("package",\
        help="The package name to fix the md5sums for.", metavar="PKG")

    parser.add_argument("files",\
        help="The package files to fix.", nargs = "*", metavar="FILES")

    options = parser.parse_args()
    target_package  = options.package
    target_files = []
    for f in options.files:
        target_files.append(f)

    
    # Yeah I know this looks wrong but that's globals for you
    get_setup_ini(options.inifile)
    inifile = options.inifile
    
    pkgs = dists["curr"]
    namekeys = pkgs.keys()
    
    if target_package not in namekeys:
        error(target_package + " is not in " + inifile)
        return 1
    
    sections = ["install", "source"]
    
    for f in target_files:
        basename = path(f).basename()
        found_section = 0
        for s in sections:
            if basename in pkgs[target_package][s]:
                found_section = s
                break
        if not found_section:
            error(basename + " is not in install: or source: of " +\
            target_package + "in " + inifile )
            return 1
            
#def gen_diff(diff_filename, packagename, linenum, oldline,\
#    filename, basename, section):
            
    for f in target_files:
        basename = path(f).basename()
#def find_line(inifile, target_package, section, filename):  
        (linenum, line) = find_line(inifile, target_package,\
        found_section, basename)
        diff_filename = basename + ".diff"
        diff = gen_diff(diff_filename, target_package, linenum, line,\
        f, basename, found_section)
        df = file(diff_filename, "w")
        df.writelines(diff)
        df.close()
    
    
    
    #selected = []
    #for package in dists["curr"].keys():
    #     if "Base" in dists["curr"][package]["category"]:
    #         selected.append(package)
    #selected.sort()
    #for i in selected:
    #    print i
    
    



if __name__ == "__main__":
    main()
    
