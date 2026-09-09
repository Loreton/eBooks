#
# ruff: noqa: SIM113 - Use `enumerate()` for index variable `index` in `for` loop (Ruff SIM113)

# import os
# from pathlib import Path
# import shutil


# --- pyLnLib modules
# from pyLnLib.context    import pVars as pv
from pyLnLib.lndict        import lnDict
from pyLnLib        import get_colors
from pyLnLib.logger    import get_logger
from pyLnLib.files      import scan_directory
from pyLnLib import regex, processContext
from pyLnLib.context import pVars as pv
from pyLnLib.varie.keyboard_prompt import keyboardPrompt
from pyLnLib.epub      import EpubManager

# from .clean_filename import clean_filename
logger = get_logger()
C=get_colors()




def printOccurrences(occurrencies: list, words_list: list):
    items = processContext(occurrencies)
    n_items=len(items)
    logger.info("found occurrencies: %s", n_items)

    if n_items > 0:
        data=items[0].pop("source_data")  # - il text sorgente lo trovo nella prima occurrency.
        logger.info("searching words:\n%s", words_list)
        for index, item in enumerate(items):
            print()
            if not item.valid:
                continue
            logger.debug("item: %s", item)
            content = data[item.context_start:item.context_end]
            for word in words_list:
                content = regex.replace(content, word, f"{C.yellowH}{word}{C.reset}", ignore_case=True)

            # epub_file=filename.with_suffix(".epub")
            # logger.info("file:\n'%s' ...", str(epub_file).replace("text", "epubs"))
            print(f"{C.yellowH}content[{index-1}/{n_items}] - indexes of occurrencies: {sorted(item.index)}:")
            print(f"{C.reset}... {content} ...")

    else:
        logger.info("non trovate")
    logger.info("found occurrencies: %s", len(items))


def logOccurrences(occurrencies: list, words_list: list):
    items = processContext(occurrencies)
    n_items=len(items)
    logger.info("found occurrencies: %s", n_items)

    if n_items > 0:
        data=items[0].pop("source_data")  # - il text sorgente lo trovo nella prima occurrency.
        logger.info("searching words:\n%s", words_list)
        for index, item in enumerate(items):
            print()
            if not item.valid:
                continue
            logger.debug("item: %s", item)
            content = data[item.context_start:item.context_end]
            for word in words_list:
                content = regex.replace(content, word, f"{C.yellowH}{word}{C.reset}", ignore_case=True)

            # epub_file=filename.with_suffix(".epub")
            # logger.info("file:\n'%s' ...", str(epub_file).replace("text", "epubs"))
            logger.info("content[%s/%s] - indexes of occurrencies: %s:\n%s ...", index+1, n_items, sorted(item.index), content)

    else:
        logger.info("non trovate")
    logger.info("found occurrencies: %s", len(items))




####################################################
#
####################################################
def OR_search():
    args = pv.args
    file_list = scan_directory(root_dir=args.top_dir, pattern='*.epub')

    nfiles=len(file_list)
    logger.debug(file_list)

    for index, epub_path in enumerate(file_list, 1):
        with EpubManager(epub_path) as book:
            print("\n"*3)
            logger.info("*"*90)
            logger.info(f"* {C.white}{index:03d}/{nfiles:03d}: {C.cyan}{book.epub_path}")
            logger.info("*"*90)
            full_metadata = book.metadata.to_dict()
            calibre = full_metadata.calibre

            logger.info(f"  Titolo:  {book.title}")
            logger.info(f"  Autori:  {book.authors}")
            logger.info(f"  Calibre:  {calibre}")
            # logger.info(f"  Dizionario completo: {book.metadata.to_dict()}")
            output_temp_file = "/tmp/book_temp.txt"
            content = book.to_text(output_file=output_temp_file)
            # logger.info("file content:\n%s", content[:1000])

            occurrencies = regex.or_search( source_data=content,
                                            words_list=args.terms,
                                            normalize_text=args.normalize_text,
                                            ignore_case=args.ignore_case,
                                            context_length=args.context_length,
                                            boundary=args.boundary)
            printOccurrences(occurrencies=occurrencies, words_list=args.terms)
            logger.info("output file: %s", output_temp_file)


        keyboardPrompt(text_msg="press 'c' to continue", validKeys=["c"],exitKeys=["ENTER"])
        logger.info("*"*60)

####################################################
# - Cerca in epub files
# - consideriamo che sono epubs salvati da Calibre in modo
# - da avere anche i metadata di Calibre incorporati
####################################################
def AND_search():
    args = pv.args
    file_list = scan_directory(root_dir=args.top_dir, pattern='*.epub')

    nfiles=len(file_list)
    logger.debug(file_list)

    for index, epub_path in enumerate(file_list, 1):
        with EpubManager(epub_path) as book:
            logger.info(f"{C.white}{index:03d}/{nfiles:03d}: {C.cyan}{book.epub_path}")
            full_metadata = book.metadata.to_dict()
            calibre = full_metadata.calibre
            # logger.info("calibre metadata: %s", calibre)


            content = book.to_text()
            # logger.info("file content:\n%s", content[:1000])

            logger.info("\tauthor: %s", book.authors)
            logger.info("\ttitle:  %s", book.title)

            occurrencies = regex.and_search( source_data=content,
                                            words_list=args.terms,
                                            normalize_text=args.normalize_text,
                                            ignore_case=args.ignore_case,
                                            context_length=args.context_length,
                                            boundary=args.boundary)
            printOccurrences(occurrencies=occurrencies, words_list=args.terms)

        keyboardPrompt(text_msg="press 'ENTER' to continue", validKeys=["ENTER"])
        print("\n\n")




    # for index, book in enumerate(file_list, 1):
    #     # logger.info(f"{index:03d}/{nfiles:03d}: {C.white}{book.parent.name}/{book.name}")
    #     # breakpoint()
    #     logger.info(f"{index:03d}/{nfiles:03d}: {C.white}{book}")
    #     file_content = book.read_text()
    #     occurrencies = regex.and_search( source_data=file_content,
    #                                     words_list=args.terms,
    #                                     normalize_text=args.normalize_text,
    #                                     ignore_case=args.ignore_case,
    #                                     context_length=args.context_length,
    #                                     boundary=args.boundary)
    #     printOccurrences(occurrencies=occurrencies, words_list=args.terms)
    #     keyboardPrompt(text_msg="press 'ENTER' to continue", validKeys=["ENTER"])

####################################################
#
####################################################
def AND_search_txt():
    args = pv.args
    file_list = scan_directory(root_dir=args.top_dir, pattern='*.txt')
    nfiles=len(file_list)
    logger.debug(file_list)

    for index, book in enumerate(file_list, 1):
        # logger.info(f"{index:03d}/{nfiles:03d}: {C.white}{book.parent.name}/{book.name}")
        # breakpoint()
        logger.info(f"{index:03d}/{nfiles:03d}: {C.white}{book}")
        file_content = book.read_text()
        occurrencies = regex.and_search( source_data=file_content,
                                        words_list=args.terms,
                                        normalize_text=args.normalize_text,
                                        ignore_case=args.ignore_case,
                                        context_length=args.context_length,
                                        boundary=args.boundary)
        printOccurrences(occurrencies=occurrencies, words_list=args.terms)
        keyboardPrompt(text_msg="press 'ENTER' to continue", validKeys=["ENTER"])
