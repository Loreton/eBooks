# updated by ...: Loreto Notarantonio
import sys
from types import SimpleNamespace
import argparse
from pathlib import Path
# from pyLnLib.context import ctx
from pyLnLib.colors import get_colors
from pyLnLib.logger import get_logger

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



# -- add common options to specific parser
def common_options(parser, name: str):
    logger_levels: list[str]=logger.get_log_levels()

    _extra_descr=f'{C.white}arguments description{C.reset}'
    extra_descr= None
    group=parser.add_argument_group(f'{C.white}common arguments{C.reset}', extra_descr)

    group.add_argument('--show-log-function-name',action='store_true', help=f'{C.green}show function on log line {v.default}')
    group.add_argument( "--console-log-level",
                            # metavar=f'{C.yellowH}<optional>{C.reset}',
                            metavar='',
                            type=str.lower,
                            required=False,
                            default='info',
                            choices=logger_levels,
                            nargs="?", # just one entry
                            help=f"""{C.cyan}set logger console level:
                                    {logger_levels} {v.default} """.replace('  ', '')
                        )

    # common_flags = parser.add_argument_group(f'{C.white}execution flags{C.reset}')
    # if parser_name in ['no_path']:
    # group.add_argument('--force-trace',   action='store_true', help=f'{C.green}force trace    level on log {v.default}')
    # group.add_argument('--force-notify',  action='store_true', help=f'{C.green}force notify   level on log {v.default}')
    group.add_argument('--go',            action='store_true', help=f'{C.green}specify if command must be executed. {v.default}')
    group.add_argument('--display-args',  action='store_true', help=f'{C.green}Display arguments {v.default}')




# ==================
# define group for duplicated
# ==================
def duplicated(parser, name: str):
    subp   = parser.add_parser(name=name, help=f"{C.cyan}visualizza tutti i libri che sono duplicati{C.reset}")
    # _extra_descr=f'{C.white}arguments description{C.reset}'
    # extra_descr= None
    # group=excel_parser.add_argument_group(f'{C.white}{name} group {C.reset}', extra_descr)

    # exclusive_group.add_argument('--print', action='store_true', help=f'{C.cyan}print all files {v.default}')
    # exclusive_group.add_argument('--prompt', action='store_true', help=f'{C.cyan}prompt for each file to allow delection{v.default}')
    common_options(parser=subp, name=name)




# ==================
# define group for extract
# ==================
def extract(parser, name: str):
    subp = parser.add_parser(name=name, help=f"{C.cyan}{name} extract full textfrom ebook and save them as .txt in extraction_top_dir{C.reset}")
    group = subp.add_argument_group(f'{C.white}{name} flags{C.reset}', v.extra_description)

    group.add_argument('--source-epubs',  required=False, metavar='', default=None, type=check_dir,
                help=f'{C.cyan}specify source epubs top directory {v.default}')

    excl_group=group.add_mutually_exclusive_group(required=True)
    excl_group.add_argument('--calibre',  action='store_true', help=f'{C.cyan}use files in calibre folders as source files  {v.default}')
    excl_group.add_argument('--epubs',    action='store_true', help=f'{C.cyan}use files in epub folders as source files {v.default}')


    common_options(parser=subp, name=name)

# ==================
# define group for rename
# ==================
def rename(parser, name: str):
    subp = parser.add_parser(name=name, help=f"{C.cyan}rename epu bile using auhtor - title{C.reset}")
    group = subp.add_argument_group(f'{C.white}Searching flags{C.reset}')
    # group.add_argument('--calibre',         action='store_true', help=f'{C.cyan}use calibre files and not epub single files {v.default}')
    # this_parser.add_argument('--calibre', action='store_true', help=f'{C.cyan}export text from calibre epub files {v.default}')
    # this_parser.add_argument('--extraction-top-dir',  required=False, metavar='', default=ctx.config.dirs.extract_dir, type=str,
    #             help=f'{C.cyan}specify root directory {v.default}')
    common_options(parser=subp, name=name)

# ==================
# define group for search menu
# ==================
def search(parser, name: str):
    subp = parser.add_parser(name=name, help=f"{C.cyan}{name} for specific string/words{C.reset}")
    group = subp.add_argument_group(f'{C.white}Searching flags{C.reset}')
    group.add_argument('--calibre',         action='store_true', help=f'{C.cyan}use calibre files and not epub single files {v.default}')
    group.add_argument('--terms',           type=str, nargs='*', metavar='', default=[], required=True, help=f'{C.cyan}terms to search for {v.default}')
    group.add_argument('--boundary',        action='store_true', help=f'{C.cyan}full words instead of partial strings {v.default}')
    group.add_argument('--ignore-case',     action='store_true', help=f'{C.cyan}case insensitive {v.default}')
    group.add_argument('--normalize-text',  action='store_true', help=f'{C.cyan}normalize text {v.default}')
    group.add_argument('--and',             action='store_true', dest="and_arg", help=f'{C.cyan}and between words (default OR){v.default}')
    group.add_argument('--context-length',  type=int, metavar='', default=0, help=f'{C.cyan}text-len of extra Text before and after the searched string {v.default}')
    group.add_argument('--max-words-between',type=int, metavar='', default=None,  help=f'{C.cyan}max distance between words 0=adiacent {v.default}')

    # wd_required = True if '--near' in sys.argv else False


    common_options(parser=subp, name=name)





##############################################################
# - Parse Input
##############################################################
def parseInput() -> argparse.Namespace:
    global v
    v=SimpleNamespace(
        default_color=C.yellow,
        metavar_optional=f'{C.white}<optional>{C.reset}',
        metavar_mandatory=f'{C.white}<mandatory>{C.reset}',
        # extra_description=f'{C.white}arguments description{C.reset}',
        extra_description=None,
    )
    v.default=f'{v.default_color}(default: %(default)s){C.reset}\n\n'



    # -----------------------------
    import argparse
    if len(sys.argv) == 1:
        sys.argv.append('-h')

    parser = argparse.ArgumentParser(description='devices management')
    # parser.add_argument('--version', action='version', version=version)



    # ===================================
    # - Main positional arguments
    # -    choice conterrà l'argomento posizionale
    # ===================================
    positional_arguments = ["rename", "extract", "search", "duplicated"]
    for item in positional_arguments:
        if sys.argv[1].startswith(item[:3]):
            sys.argv[1] = item
            break

    pos_parser     = parser.add_subparsers(dest='choice',required=True, title=f'{C.white}choices - required positional arguments{C.reset}')
    duplicated(parser=pos_parser, name='duplicated')
    rename(parser=pos_parser, name="rename")
    extract(parser=pos_parser, name="extract")
    search(parser=pos_parser, name="search")


    # - common options for all subparsers
    # common_options(subparsers=subparsers)




    args = parser.parse_args()
    if args.display_args:
        import json
        json_data = json.dumps(vars(args), indent=4, sort_keys=True)
        print('input arguments: {json_data}'.format(**locals()))
        sys.exit(0)

    if args.show_log_function_name:
        logger.show_function_name(True)
    return  args
