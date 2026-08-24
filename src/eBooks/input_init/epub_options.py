# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/parse_input/authors.py
# src/eBooks/parse_input/authors.py

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



def epubs(v:SimpleNamespace, parser):
    """
        Scan di epub in una dir/subdirs,
        per estrarre text
    """
    func_name=ctx.get_function_name()
    subp = parser.add_parser(name=func_name, help=f"{C.cyan}{func_name} process directory with epub files{C.reset}")
    subp.add_argument('--replace',    action='store_true', help=f'{C.cyan}replace existing files {v.default}')

    subp.add_argument('--top-dir',  required=True, metavar='', default=None, type=check_dir,
                help=f'{C.cyan}specify source epubs top directory {v.default}')

    exclusive_group=subp.add_mutually_exclusive_group(required=True)
    exclusive_group.add_argument('--authors-from-ebooks',  action='store_true', help=f'{C.cyan}get authors from ebook in calibre library metadata {v.default}')
    exclusive_group.add_argument('--extract-text',    action='store_true', help=f'{C.cyan}extract text from epub files {v.default}')
    common_options(v=v, parser=subp, func_name=func_name)
