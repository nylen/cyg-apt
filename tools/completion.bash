#!/bin/bash
#
# bash completion support for cyf-apt.
#
_cyg_apt()
{
    local cur prev opts cmds long_opts dist_opts must_package must_file
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    cmds="setup update ball download filelist find help install list md5 missing new purge remove requires search show source upgrade url version"
    long_opts="--quiet --download --help --mirror --dist --no-deps --regexp --force --nobarred --no-verify --nopostinstall --nopostremove"
    dist_opts="curr test prev"
    must_package="ball requires show download md5 purge search source url file list install missing remove version"
    must_file="find"
    
    if [[ $COMP_CWORD -eq 1 ]] ; then
        COMPREPLY=( $(compgen -W "${cmds}" -- ${cur}) )
        return 0
    fi
    
    if [[ $COMP_CWORD -eq 2 ]] ; then
        if [[ `echo "$must_package" | grep -Ec "${prev}"` == 1 ]] ; then
            if [[ -z $cyg_apt_packages ]] ; then
                packList=`cyg-apt search . | cut -d " " -f 1`
                for rpack in $packList
                do
                    cyg_apt_packages="$cyg_apt_packages $rpack"
                done
                cyg_apt_packages="$cyg_apt_packages cygwin "
                unset rpack packList
            fi
            COMPREPLY=( $(compgen -W "${cyg_apt_packages}" -- ${cur}) )
            return 0
        elif [[ `echo "$must_file" | grep -Ec "${prev}"` == 1 ]] ; then
            COMPREPLY=( $(compgen -W "`ls`" -- ${cur}) )
            return 0
        elif [[ ${cur} == -* ]] ; then
            COMPREPLY=( $(compgen -W "${long_opts}" -- ${cur}) )
            return 0
        fi
    fi
    
    if [[ $COMP_CWORD -eq 3 ]] && [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "${long_opts}" -- ${cur}) )
        return 0
    fi
    
    if [[ ${prev} == "--dist" ]] || [[ ${prev} == "-t" ]] ; then
        COMPREPLY=( $(compgen -W "${dist_opts}" -- ${cur}) )
        return 0
    fi
}
complete -F _cyg_apt cyg-apt
