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
from pdb import set_trace as st


def popen(cmd):
    spl = cmd.split()
    return Popen(spl, stdout=PIPE).communicate()[0]
    
    
def error (msg):
    print sys.argv[0] + ": " + msg
    


def find_line(inifile, packagename, section, option):
    ini = file(inifile).readlines()
    tpmarkerlen= len(packagename) + 2
    ln = 0
    found = False
    for l in ini:        
        if l[0:tpmarkerlen] == "@ " + packagename:
            found = True
            break
        ln = ln + 1
    
    if not found:
        error("urg")
        return None
        
    endln = len(ini)
    if section != "curr":
        found = False
        while ln < endln:
            if ini[ln].strip() == "":
                raise(sys.argv[0] + ": out of section! Exiting.")
            if "[" + section + "]" in ini[ln]:
                found = True
                break
            ln += 1
            
    if not found:
        error("urg")
        return None    

    while ln < endln:
        if ini[ln].strip() == "":
            raise(sys.argv[0] + ": Failed to find option! Exiting.")     
        if option in ini[ln]:       
            return ln, ini[ln]
        ln += 1
    raise("urg")
             
 
def gen_md5_diff\
    (packagename,\
    option,\
    linenum,\
    oldline,\
    tarfile):

    md5 = popen("md5sum " + tarfile).split()[0]
    len = str(os.stat(tarfile).st_size)
    basename = os.path.basename(tarfile)

    #install: release-2/testpkg/testpkg-0.0.1-0.tar.bz 3140 fbbe05f50b9273be640c312857f70619

    newline = option + ": " + "release-2/" + packagename + "/" + basename + " " + len + " " + md5 + "\n"

    # Add one: sometimes patch/diff seems 1 based not zero based
    diff = [0,0,0,0]
    diff[0] = str(linenum + 1) + "c" + str(linenum + 1) + "\n"
    diff[1] = "< " + oldline
    diff[2] = "---\n"
    diff[3] = "> " + newline
    
    # Return the diff
    return diff
    

def gen_version_diff\
    (packagename,\
    option,\
    linenum,\
    oldline,\
    version):

    newline = option + ": " + version + "\n"

    # Add one: sometimes patch/diff seems 1 based not zero based
    diff = [0,0,0,0]
    diff[0] = str(linenum + 1) + "c" + str(linenum + 1) + "\n"
    diff[1] = "< " + oldline
    diff[2] = "---\n"
    diff[3] = "> " + newline
    
    # Return the diff
    return diff
    
    
def gen_file_version_diff\
    (packagename,\
    option,\
    linenum,\
    oldline,\
    field_input):


    newline = oldline.replace(field_input[1], field_input[2])
    #install: release-2/testpkg/testpkg-0.0.1-0.tar.bz 3140 fbbe05f50b9273be640c312857f70619

    # Add one: sometimes patch/diff seems 1 based not zero based
    diff = [0,0,0,0]
    diff[0] = str(linenum + 1) + "c" + str(linenum + 1) + "\n"
    diff[1] = "< " + oldline
    diff[2] = "---\n"
    diff[3] = "> " + newline
    
    # Return the diff
    return diff
     

def main():
    global dists
    parser =  argparse.ArgumentParser(description = "Generates a diff to change a field of a given package in setup-2.ini. It is an error for given files not to exist in the .ini under that package."\
    "Example usage: " + sys.argv[0] +\
    "setup-2.ini testpkg install md5 --field_input=test-pkg-0.0.1-0.tar.bz"
    )
    
    parser.add_argument("ini",\
        help="The setup.ini to patch.", metavar="INI")

    parser.add_argument("package",\
        help="The package name to edit.", metavar="PKG")
    
    parser.add_argument("--section", dest="section",\
        help = "Section, curr if not given.", metavar="SEC", nargs="?",\
        default="curr")

    parser.add_argument("option",\
        help="The option to edit.", metavar="option")
        
    parser.add_argument("field",\
        help="The field of the option to edit.", metavar="FIELD", nargs="?")

    parser.add_argument("--field-input", dest="field_input",\
        help="The data to generate the replacement field with.", metavar="FIELD-INPUT", nargs="+")
        
    options = parser.parse_args()
    ini = options.ini
    packagename  = options.package
    section = options.section
    option = options.option
    field = options.field
    field_input = options.field_input
    diff_filename = os.path.basename(ini) + ".diff"
    
    (linenum, line) = find_line(ini, packagename, section, option)
      
    if (option == "install" or option == "source") and field == "md5":
        diff = gen_md5_diff\
        (\
            packagename,\
            option,\
            linenum,\
            line,\
            field_input[0]
        )

    elif option == "version":
        diff = gen_version_diff\
        (\
            packagename,\
            option,\
            linenum,\
            line,\
            field_input[0]
        )
    elif (option == "install" and field == "tarver"):
        diff = gen_file_version_diff\
        (\
            packagename,\
            option,\
            linenum,\
            line,\
            field_input
        )
    else:
        raise "urg"
    
    
    df = file(diff_filename, "w")
    df.writelines(diff)
    df.close()

if __name__ == "__main__":
    main()
    
