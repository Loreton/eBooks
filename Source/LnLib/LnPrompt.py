#!/usr/bin/python
# -*- coding: utf-8 -*-

# updated by ...: Loreto Notarantonio
# Version ......: 28-04-2020 09.32.31
import sys


def prompt(msg='', validKeys='ENTER', exitKeys='x'):
    # msg = "{0} [{1}] - ({2} to exit) ==> ".format(msg, validKeys, exitKeys)
    if not msg:
        msg='Enter to continue....'

    if validKeys=='ENTER':
        msg = "{msg} - ({exitKeys} to exit) ==> ".format(**locals())
    else:
        msg = "{msg} [{validKeys}] - ({exitKeys} to exit) ==> ".format(**locals())

    if isinstance(validKeys, (range)):
        _keys = []
        for i in validKeys:
            _keys.append(i)
        validKeys = '|'.join([str(x) for x in _keys])

    validKeys = validKeys.split('|')

    exitKeys = exitKeys.split('|')
    while True:
        choice      = input(msg).strip()
        choiceUPP   = choice.upper()
        
        if choice in exitKeys: # diamo priorità all'uscita
            print("Exiting on user request new.")
            sys.exit(1)
        
        if choice == '':    
            if "ENTER" in exitKeys:
                sys.exit()
            if "ENTER" in validKeys:
                return ''
            else:
                print('\n... please enter something\n')

        elif "ENTER" in validKeys:
            return choice

        elif choice in validKeys:
            break

        else:
            print('\n... try again\n')

    return choice

def prompt_prev(msg='', validKeys='ENTER', exitKeys='x'):
    # msg = "{0} [{1}] - ({2} to exit) ==> ".format(msg, validKeys, exitKeys)
    if not msg:
        msg='Continue....'
    msg = "{msg} [{validKeys}] - ({exitKeys} to exit) ==> ".format(**locals())
    validKeys = validKeys.split('|')
    exitKeys = exitKeys.split('|')
    while True:
        choice      = input(msg).strip()
        choiceUPP   = choice.upper()
        if choice == '':    # diamo priorità alla exit
            if "ENTER" in exitKeys:
                sys.exit()
            elif "ENTER" in validKeys:
                return ''
            else:
                print('\n... please enter something\n')

        elif choice in exitKeys:
            print("Exiting on user request new.")
            sys.exit(1)

        elif choice in validKeys:
            break

        else:
            print('\n... try again\n')

    return choice


