# updated by ...: Loreto Notarantonio
import sys
from types import SimpleNamespace
import argparse


# - loreto pyLnLib
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger


# - project modules
from .calibre_options    import calibre
from .epub_options       import epubs
from .search_options     import search



C=get_colors()
logger=get_logger()


##############################################################
# - Parse Input
##############################################################
def parseInput() -> argparse.Namespace:
    # global v
    v=SimpleNamespace(
        default_color=C.yellow,
        metavar_optional=f'{C.white}<optional>{C.reset}',
        metavar_mandatory=f'{C.white}<mandatory>{C.reset}',
        # extra_description=f'{C.white}arguments description{C.reset}',
        extra_description=None,
    )
    v.default=f'{v.default_color}(default: %(default)s){C.reset}\n\n'



    # -----------------------------
    print('\n'*2)
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(description='devices management')
    # parser.add_argument('--version', action='version', version=version)



    # ===================================
    # - Main positional arguments
    # -    choice conterrà l'argomento posizionale
    # ===================================
    positional_arguments = ["calibre", "epubs", "search"]
    for item in positional_arguments:
        if sys.argv[1].startswith(item[:3]):
            sys.argv[1] = item
            break

    pos_parser = parser.add_subparsers(dest='choice',required=True, title=f'{C.white}choices - required positional arguments{C.reset}')

    calibre(v=v, parser=pos_parser)
    epubs(v=v, parser=pos_parser)
    search(v=v, parser=pos_parser)




    args = parser.parse_args()



    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)

    if args.show_log_function_name:
        logger.show_function_name(True)
    return  args
