import os
""" A useful set of utility classes and functions."""
import subprocess


def popen_ext(cmd, echo=0):
    if echo:
        print "\n" + cmd
    ret = popen(cmd)
    if echo:
        print ret[0],
        print ret[1],
    return ret


def popen(cmd):
    spl = cmd.split()
    ret = subprocess.Popen(spl,\
        stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return ret


class path:
    def __init__(self, path):
        self.path = path
        self._basename = os.path.basename(path)

    def recursive_items(self, walk_path):
        local_entries = os.listdir(walk_path)
        if walk_path == ".":
            prefix = ""
        elif walk_path[-1] == '/':
            prefix = walk_path
        else:
            prefix = walk_path + "/"            
        entries = [prefix + x for x in local_entries]
        #pdb.set_trace()
        dirs = [x for x in entries if os.path.isdir(x)]
        for d in dirs:
            entries += self.recursive_items(d)
        return entries
    
    def files(self):
        entries = self.recursive_items(self.path)
        f = [x for x in entries if os.path.isfile(x)]
        return f
        
    def dirs(self):
        entries = self.recursive_items(self.path)
        f = [x for x in entries if os.path.isdir(x)]
        return f
        
    def basename(self):
        return self._basename

def main():    
    print "Smoketest path class."
    p = path(".")
    files = p.files()
    dirs = p.dirs()
    print "\nFiles in ./"
    for f in files:
        print f
    print "\nDirs in ./"
    for d in dirs:
        print d


if __name__ == "__main__":
    main()
    
