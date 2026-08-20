# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/parse_input/authors.py
# src/eBooks/parse_input/authors.py

import argparse
from types import SimpleNamespace

from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

from .common_options    import common_options

C=get_colors()
logger=get_logger()

# ==================
# mostra gli autori per capire se sono corretti "Cognome | Nome"
# ==================
def authors_from_authors(v:SimpleNamespace, parser, name: str):
    subp = parser.add_parser(name=name, help=f"{C.cyan}{name} show all authors theid IDs{C.reset}")
    group = subp.add_argument_group(f'{C.white}{name} flags{C.reset}', v.extra_description)
    group.add_argument('--update-authors',    action='store_true', help=f'{C.cyan}update authors in authors.yaml {v.default}')
    excl_group=group.add_mutually_exclusive_group(required=True)
    excl_group.add_argument('--calibre',  action='store_true', help=f'{C.cyan}use files in calibre folders as source files  {v.default}')
    excl_group.add_argument('--epubs',    action='store_true', help=f'{C.cyan}use files in epub folders as source files {v.default}')
    common_options(v=v, parser=subp, name=name)



def authors_from_ebook(v:SimpleNamespace, parser, name: str):
    subp = parser.add_parser(name=name, help=f"{C.cyan}{name} show all authors theid IDs{C.reset}")
    group = subp.add_argument_group(f'{C.white}{name} flags{C.reset}', v.extra_description)
    group.add_argument('--update-authors',    action='store_true', help=f'{C.cyan}update authors in authors.yaml {v.default}')
    excl_group=group.add_mutually_exclusive_group(required=True)
    excl_group.add_argument('--calibre',  action='store_true', help=f'{C.cyan}use files in calibre folders as source files  {v.default}')
    excl_group.add_argument('--epubs',    action='store_true', help=f'{C.cyan}use files in epub folders as source files {v.default}')
    common_options(v=v, parser=subp, name=name)

def authors_calibre(v:SimpleNamespace, parser, name: str):
    subp = parser.add_parser(name=name, help=f"{C.cyan}{name} show all authors theid IDs{C.reset}")
    group = subp.add_argument_group(f'{C.white}{name} flags{C.reset}', v.extra_description)
    group.add_argument('--update-authors',    action='store_true', help=f'{C.cyan}update authors in authors.yaml {v.default}')
    excl_group=group.add_mutually_exclusive_group(required=True)
    excl_group.add_argument('--from-authors',  action='store_true', help=f'{C.cyan}use files in calibre folders as source files  {v.default}')
    excl_group.add_argument('--from-ebooks',    action='store_true', help=f'{C.cyan}use files in epub folders as source files {v.default}')
    common_options(v=v, parser=subp, name=name)
