#
# ruff: noqa: SIM113 - Use `enumerate()` for index variable `index` in `for` loop (Ruff SIM113)

import os
from pathlib import Path
import shutil


# --- pyLnLib modules
# from pyLnLib.context    import pVars as pv
from pyLnLib.lndict        import lnDict
from pyLnLib        import get_colors
from pyLnLib.logger    import get_logger
from pyLnLib.files      import scan_directory
from pyLnLib import regex, processContext
from pyLnLib.context import pVars as pv


# from .clean_filename import clean_filename
logger = get_logger()
C=get_colors()




def printOccurrences(occurrencies: list, words_list: list, filename: Path):
    source_data=filename.read_text()
    items = processContext(occurrencies, source_data=source_data)
    logger.info("found occurrencies: %s", len(items))

    if len(items) > 0:
        logger.info("searching words:\n%s", words_list)
        for item in items:
            print()
            if not item.valid:
                continue
            logger.debug("item: %s", item)
            content = item.context
            for word in words_list:
                content = regex.replace(content, word, f"{C.yellowH}{word}{C.reset}", ignore_case=True)

            epub_file=filename.with_suffix(".epub")
            logger.info("file:\n'%s' ...", str(epub_file).replace("text", "epubs"))
            logger.info("content:\n%s ...", content)

    else:
        logger.info("non trovate")
    logger.info("found occurrencies: %s", len(items))



def printOccurrences_prev(occurrencies: list, words_list: list):
    # from pprint import pprint
    logger.info("found occurrencies: %s", len(occurrencies))
    if len(occurrencies) > 0:
        logger.info("words to find: \n%s", words_list)
        for item in occurrencies:
            logger.info("item: %s", item)
            content = item.context
            '''
            content = (
                content[:item.match_start]
                + C.yellowH
                + content[item.match_start:item.match_end]
                + C.reset
                + content[item.match_end:]
            )
            '''
            for word in words_list:
                content = regex.replace(content, word, f"{C.yellowH}{word}{C.reset}", ignore_case=True)

            # per evitare di scrivere troppo
            limit = max(item.context_length, 600)
            limit = min(limit, len(content))
            content = content[:limit]
            logger.info("content[:%s]: %s ...", limit, content)
            # breakpoint()

    else:
        logger.info("non trovate")
    logger.info("found occurrencies: %s", len(occurrencies))




####################################################
#
####################################################
def OR_terms(data: str):
    args = pv.args
    file_list = scan_directory(root_dir=args.top_dir, pattern='*.txt')
    nfiles=len(file_list)
    logger.debug(file_list)

    for index, book in enumerate(file_list[:10], 1):
        logger.info(f"{index:03d}/{nfiles:03d}: {C.white}{book.parent.name}/{book.name}")
        file_content = book.read_text()
        occurrencies = regex.or_search( source_data=file_content,
                                        words_list=args.terms,
                                        normalize_text=args.normalize_text,
                                        ignore_case=args.ignore_case,
                                        context_length=args.context_length,
                                        boundary=args.boundary)
        printOccurrences(occurrencies=occurrencies, words_list=args.terms, filename=book)
