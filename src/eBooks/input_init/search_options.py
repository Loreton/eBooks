# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/parse_input/authors.py
# src/eBooks/parse_input/authors.py

import sys
from types import SimpleNamespace
from pathlib import Path

from pyLnLib.context import ctx
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

from .common_options    import common_options

C=get_colors()
logger=get_logger()

# -----------------------------
def check_dir(path):
    p = Path(path)
    if (p).is_dir():
        return str(p.resolve())
    else:
        logger.error(f"""path: {p} doesn't exists! """)
        sys.exit(1)




def _searchingFlags(v:SimpleNamespace, parser):
    flags = parser.add_argument_group(f'{C.white}Searching flags{C.reset}')
    flags.add_argument('--boundary',  action='store_true', default=False, required=False,
            help=f'{C.cyan}full words instead of partial strings {v.default}')

    flags.add_argument('--ignore-case',  action='store_true', default=False, required=False,
            help=f'{C.cyan}case insensitive {v.default}')

    flags.add_argument('--normalize-text',  action='store_true', default=False, required=False,
            help=f'{C.cyan}normalize text {v.default}')

    flags.add_argument('--context-length',  type=int, default=0, metavar='', required=False,
            help=f'{C.cyan}text-len of extra Text before and after the searched string {v.default}')

    # wd_required = True if '--near' in sys.argv else False
    flags.add_argument('--max-words-between',  type=int, metavar='', default=0, required=False,
            help=f'{C.cyan}max distance between words {v.default_color}(default 0 (no-limits)){C.reset}')


    flags.add_argument('--any-order',     action='store_true', default=False, help=f'{C.cyan}any order of words (otherwise is sequentiaal){C.reset}')
    flags.add_argument('--show-source-text', action='store_true', default=False, help=f'{C.cyan}print text used as source text {C.reset}')


def _operatorsFlags(v:SimpleNamespace, parser):
    operation = parser.add_argument_group(f'{C.white}Operators Group (mandatory) {C.reset}')
    # operators_group = operation.add_mutually_exclusive_group(required=True)
    # operators_group.add_argument('--terms',   action='store_true', default=False, help=f'{C.cyan}search for a single term{C.reset}')
    # operators_group.add_argument('--and',     action='store_true', dest="and_arg", default=False, help=f'{C.cyan}and between words{C.reset}')
    # operators_group.add_argument('--or',      action='store_true', dest="or_arg", default=False, help=f'{C.cyan}or several words{C.reset}')
    # operators_group.add_argument('--replace',     action='store_true', default=False, help=f'{C.cyan}replace string{C.reset}')
    # operators_group.add_argument('--single',     action='store_true', default=False, help=f'{C.cyan}find all occurrences of a single string{C.reset}')

def _mandatory(v:SimpleNamespace, parser):
    group = parser.add_argument_group(f'{C.cyanH}Mandatory options {C.white}(mandatory) {C.reset}')
    # operation = parser.add_argument_group(f'{C.white}Operators Group (mandatory) {C.reset}')
    group.add_argument('--top-dir',  required=True, metavar='', default=None, type=check_dir,
                help=f'{C.cyan}specify source txt files top directory {v.default}')

    group.add_argument('--terms',  type=str, nargs='*', metavar='', default=0, required=True,
            help=f'{C.cyan}terms to search for {v.default_color}(default 0 (no-limits)){C.reset}')

    exclusive_group = group.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('--and',     action='store_true', dest="and_arg", default=False, help=f'{C.cyan}and between words{C.reset}')
    exclusive_group.add_argument('--or',      action='store_true', dest="or_arg", default=False, help=f'{C.cyan}or several words{C.reset}')
    # operators_group.add_argument('--terms',   action='store_true', default=False, help=f'{C.cyan}search for a single term{C.reset}')
    # operators_group.add_argument('--replace',     action='store_true', default=False, help=f'{C.cyan}replace string{C.reset}')
    # operators_group.add_argument('--single',     action='store_true', default=False, help=f'{C.cyan}find all occurrences of a single string{C.reset}')

    # group = subp.add_argument_group(f'{C.cyanH}Operators Group {C.white}(mandatory) {C.reset}')



def search(v:SimpleNamespace, parser):
    """
        Scan di epub in una dir/subdirs,
        per estrarre text
    """
    func_name=ctx.get_function_name()
    subp = parser.add_parser(name=func_name, help=f"{C.cyan}{func_name} process directory for text in txt files{C.reset}")
    # subp.add_argument('--terms',    action='store_true', help=f'{C.cyan}replace existing files {v.default}')


    # exclusive_group=subp.add_mutually_exclusive_group(required=True)
    # exclusive_group.add_argument('--authors-from-ebooks',  action='store_true', help=f'{C.cyan}get authors from ebook in calibre library metadata {v.default}')
    # exclusive_group.add_argument('--extract-text',    action='store_true', help=f'{C.cyan}extract text from epub files {v.default}')


    # _operatorsFlags(v=v, parser=subp)
    _mandatory(v=v, parser=subp)
    _searchingFlags(v=v, parser=subp)
    common_options(v=v, parser=subp, func_name=func_name)
