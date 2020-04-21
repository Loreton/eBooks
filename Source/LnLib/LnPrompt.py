#!/usr/bin/python
# -*- coding: utf-8 -*-

# updated by ...: Loreto Notarantonio
# Version ......: 21-04-2020 15.54.55
import sys


def prompt(msg='', validKeys='ENTER', exitKeys='x'):
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


