#!/usr/bin/python
# -*- coding: utf-8 -*-

# updated by ...: Loreto Notarantonio
# Version ......: 03-05-2020 09.16.05
import sys
# import Ln
# from . import LnColor
def set_prompt(Color):
    global C
    C=Color()

def prompt(msg='', validKeys='ENTER', exitKeys='x', displayValidKeys=False):
    # msg = "{0} [{1}] - ({2} to exit) ==> ".format(msg, validKeys, exitKeys)
    if not msg:
        msg='Enter to continue....'

    if validKeys or not displayValidKeys:
        msg = "     {msg} - ({exitKeys} to exit) ==> ".format(**locals())
    else:
        msg = "     {msg} [{validKeys}] - ({exitKeys} to exit) ==> ".format(**locals())


    msg=C.whiteH(text=msg, get=True)
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




