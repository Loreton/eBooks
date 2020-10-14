#!/usr/bin/python3
# Progamma per testare regex
#
# updated by ...: Loreto Notarantonio
# Version ......: 11-10-2020 18.03.18
#

import sys; sys.dont_write_bytecode = True
import os
from dotmap import DotMap
import pdb
import re

from subprocess import call
from types import SimpleNamespace

"""
    inp_list=[
                [title1, tags]
                [title2, tags]
                [title..n, tags]
        ]
    menu_entries=[
        {1 { title: title, tags: tags }}
        {2 { title: title, tags: tags }}
        {3 { title: title, tags: tags }}
        ]
"""

from subprocess import call
def Menu(inp_list, choice_dict):

    """ create menu entries """
    menu_list=[]
    menu_list.append({0: 'dummy'}) # menu start from 1
    for index, inp_item in enumerate(inp_list, start=1):
        item=SimpleNamespace()
        item.index=index
        item.title, item.tags = inp_item
        menu_item={index: item.__dict__}
        menu_list.append(menu_item)
    # for item in inp_list: print(item)
    # for item in menu_list: print(item)

    tot_item=len(menu_list)
    _from=1
    menu_entries=10
    while True:
        _ = call('clear' if os.name =='posix' else 'cls')
        print('\n'*2)

        """ display items (menu_entries) """
        if _from>=tot_item: _from=tot_item-menu_entries
        if _from<1: _from=1
        _to = _from+menu_entries
        if _to>=tot_item: _to=tot_item

        for index in range(_from, _to):
            item=menu_list[index][index]
            print(f"    [{index:02}]: {item['title']} - {item['tags']}")

        msg='s[earch] - u[pdate] - d[elete] n[ext] p[prev] - q[uit]'
        choice = input(msg).strip().lower()

        if choice=='n':
            _from+=menu_entries
        elif choice=='p':
            _from-=menu_entries
        elif int(choice) in range(_from, _to):
            print(choice)
            prompt()
        elif choice in choice_dict.keys():
            choice_dict[choice]()



def search():
    print('search')
    prompt()
def update():
    print('update')
    prompt()
def delete():
    print('delete')
    prompt()
def quit():
    sys.exit()


if __name__ == "__main__":
    inp_list=[]
    for index in range(0, 100):
        item=[f'title_{index:02}', f'tags_{index:02}']
        inp_list.append(item)
    # for item in inp_list:  print(item)
    choice_dict = {
        's': search,
        'u': update,
        'd': delete,
        'q': quit
    }

    choice=Menu(inp_list, choice_dict)
