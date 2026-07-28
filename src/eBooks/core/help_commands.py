#!/usr/bin/env python3
#
# updated by ...: Loreto Notarantonio
# Date .........: 05-07-2026 14.43.32
#

import sys; sys.dont_write_bytecode = True



### - project modules
from pyLnLib import get_colors
C=get_colors()

###################################################
# ---- git command list ----
###################################################
def helpCommands():
    ob='{'
    cb='}'
    _dollar='$'
    varBR=f'{ob}BR{cb}'
    varoldname=f'{ob}oldName{cb}'
    varnewname=f'{ob}newName{cb}'

    commands = f'''
        {C.blue}--------- Comandi utili --------------------------{C.green}
        git checkout other_branch filename                       ### --- copy file from another branch

        {C.blue}--- TAGs{C.green}
        git tag -a "D2026-02-28T16.41" -m "Tag note"


        {C.blue}--- clone specific tag {C.green}
        git clone -b [tag_name] [repository_url]

        {C.blue}--- CREATE new Branch (solo se non è stato fatto il commit){C.green}
        BR='devel' && git checkout -b ${varBR} && git push -u gitHub ${varBR}

        {C.blue}--- CREATE a new branch from tagxxx{C.green}
        git checkout -b nuovo-branch-dal-tag v1.0.2

        {C.blue}--- DELETE branch (-D -> --delete --force){C.green}
        BR='old_branch' && git branch -d ${varBR} && git push gitHub --delete ${varBR}

        {C.blue}--- RENAME branch{C.green}
        oldName='name'; newName='name';git checkout main && git branch -m ${varoldname} ${varnewname} && git push gitHub :${varoldname} ${varnewname}

        {C.blue}--- CREATE directory for specific BRANCH{C.green}
        git worktree add ../pressControl-devel01 devel01

        {C.blue}--- MOVE branch (changes to a new one){C.green}
        BR='newBranch' && git checkout -b ${varBR} && git add --all && git commit -a -m 'starting new branch'
        {C.blue}--- return to previos BRANCH (se necessario{C.green}
        BR='prevBranch' && git checkout ${varBR} && git restore . && git clean -fd

        # Rimuovere il file dalla storia git
        git filter-branch --tree-filter 'rm -f .pio/build/esp32_littleFS/src/main.cpp.o' HEAD
        # Forzare il push (ATTENZIONE: modifica la storia!)
        git push origin main --force-with-lease


        {C.blue}--- Muoversi nei commit e Tags{C.green}
        git tag -n                               [show tags and message]
        git tag -l -n9                           [show tags and message]
        git log --oneline                        [show all commits and messages]
        git checkout V.1.3.2                     [checkout to specific Tag]
        git checkout 7a2b3c4                     [checkout to specific commit]
        git checkout main                        [Tornare all'ultima versione]




        --------------------------------------------------
    '''
    return commands
