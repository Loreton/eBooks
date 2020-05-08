#!/usr/bin/python3
# Progamma per testare regex
#
# updated by ...: Loreto Notarantonio
# Version ......: 08-05-2020 15.06.44
#

import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap
import pdb
import re

from subprocess import call

def prompt(msg='', validKeys='ENTER', exitKeys='x', displayValidKeys=False):
    # msg = "{0} [{1}] - ({2} to exit) ==> ".format(msg, validKeys, exitKeys)
    if not msg:
        msg='Enter to continue....'

    # pdb.set_trace()
    if validKeys and not displayValidKeys:
        msg = "     {msg} - ({exitKeys} to exit) ==> ".format(**locals())
    else:
        msg = "     {msg} [{validKeys}] - ({exitKeys} to exit) ==> ".format(**locals())


    # msg=C.whiteH(text=msg, get=True)
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

def menu_data():
    menu={}
    for i in range(1, 100+1):
        menu[i] = 'Menu numero {i:3}'.format(**locals())
        print(menu[i])

    return menu


def display(data, start, end):
    for index in range(start, end):
        print('     {}: {}'.format(index, data[index]))


def main(data, step=10, return_on_fw=False):
    if not hasattr(main, 'start'): # static variable
        main.start=1
    bottom = len(data)+1
    top=1
    _from=main.start
    while True:
        # - set range to display menu
        _ = call('clear' if os.name =='posix' else 'cls')
        print('\n'*2)
        if _from>=bottom: _from=bottom-step
        if _from<=top: _from=top
        _to = _from+step
        if _to>=bottom: _to=bottom

        display(data, _from, _to)
        _keys = ['f', 'b', '-']
        for i in range(_from, _to): _keys.append(i)
        validKeys = '|'.join([str(x) for x in _keys])
        choice = prompt(msg='scegli', validKeys=validKeys, displayValidKeys=True)
        if   choice=='f': _from+=step
        elif choice =='b': _from-=step
        else:
            if return_on_fw:
                main.start=_from # remember for next call
            break

        if _from>=bottom and return_on_fw:
            main.start=_from # remember for next call
            break

    return choice


if __name__ == "__main__":
    choice=main(s=10)
    print(choice)