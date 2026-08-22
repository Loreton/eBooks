# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/parse_input/authors.py
# src/eBooks/parse_input/authors.py

import argparse
from types import SimpleNamespace

from pyLnLib.context import ctx
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

from .common_options    import common_options

C=get_colors()
logger=get_logger()


def extract_text(v:SimpleNamespace, parser):
    """
        Ricerca tutti gli autodi della libreria di calibre,
        li estrae, li normalizza li salva nel file authors.yaml
    """
    func_name=ctx.get_function_name()
    subp = parser.add_parser(name=func_name, help=f"{C.cyan}{func_name} show all authors theid IDs{C.reset}")
    # group = subp.add_argument_group(f'{C.white}{func_name} flags{C.reset}', v.extra_description)
    # group.add_argument('--update-authors',    action='store_true', help=f'{C.cyan}update authors in authors.yaml {v.default}')
    # excl_group=group.add_mutually_exclusive_group(required=True)
    # excl_group.add_argument('--from-authors',  action='store_true', help=f'{C.cyan}use files in calibre folders as source files  {v.default}')
    # excl_group.add_argument('--from-ebooks',    action='store_true', help=f'{C.cyan}use files in epub folders as source files {v.default}')
    common_options(v=v, parser=subp, func_name=func_name)
