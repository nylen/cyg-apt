#!/bin/bash
######################## BEGIN LICENSE BLOCK ########################
# This file is part of the cygapt package.
#
# Copyright (C) 2002-2009 Jan Nieuwenhuizen  <janneke@gnu.org>
#               2002-2009 Chris Cormie       <cjcormie@gmail.com>
#                    2012 James Nylen        <jnylen@gmail.com>
#               2012-2014 Alexandre Quercia  <alquerci@email.com>
#
# For the full copyright and license information, please view the
# LICENSE file that was distributed with this source code.
######################### END LICENSE BLOCK #########################
#
# bash completion support for cyg-apt.
#


##
# Sets all available packages in $_cyg_apt_all_packages
##
_cyg_apt_set_all_packages()
{
    if [ -z "${_cyg_apt_all_packages}" ] ; then
        _cyg_apt_all_packages="$("${COMP_WORDS[0]}" search . -s | cut -d " " -f 1)";
    fi;
    return 0;
}

_cyg_apt()
{
    local cur prev cmds long_opts dist_opts mirrors;
    COMPREPLY=();
    cur="${COMP_WORDS[COMP_CWORD]}";
    prev="${COMP_WORDS[COMP_CWORD-1]}";
    cmds="
setup
update
ball
download
filelist
find
help
install
list
md5
missing
new
purge
remove
requires
search
show
source
upgrade
url
version
";
    long_opts="
--quiet
--download
--mirror
--dist
--no-deps
--regexp
--force
--no-verify
--nopostinstall
--nopostremove
--help
";
    dist_opts="
curr
test
prev
";
    mirrors="
ftp://ftp.is.co.za/mirrors/cygwin/
http://mirrors.163.com/cygwin/
ftp://ftp.iitm.ac.in/cygwin/
http://mirror.internode.on.net/pub/cygwin/
ftp://mirror.csclub.uwaterloo.ca/cygwin/
http://cygwin.mirror.rafal.ca/
http://cygwin.uib.no/
ftp://ftp.heanet.ie/pub/cygwin/
http://cygwin.osuosl.org/
ftp://lug.mtu.edu/cygwin/
";

    case "${COMP_CWORD}" in
        1 )
            COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") );
            return 0;
            ;;
        * )
            case "$prev" in
                --dist|-t )
                    # list available distribution
                    COMPREPLY=( $(compgen -W "${dist_opts}" -- "${cur}") );
                    return 0;
                    ;;
                --mirror|-m )
                    # list some mirrors
                    COMPREPLY=( $(compgen -W "${mirrors}" -- "${cur}") );
                    return 0;
                    ;;
                * )
                    ;;
            esac;

            if [[ "$cur" == -* ]] ; then
                COMPREPLY=( $(compgen -W "${long_opts}" -- "${cur}") );
                return 0;
            fi

            case "${COMP_WORDS[1]}" in
                ball|requires|show|download|md5|purge|search|source|url|filelist|install|missing|remove|version )
                    _cyg_apt_set_all_packages;
                    COMPREPLY=( $(compgen -W "${_cyg_apt_all_packages}" -- "${cur}") );
                    return 0;
                    ;;
                * )
                    ;;
            esac;
        ;;
    esac;

    return 0;
}

complete -F _cyg_apt cyg-apt;
