#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 26-09-2025 11.34.05
#

import sys; sys.dont_write_bytecode=True
import os
import re

from pathlib import Path

from html.parser import HTMLParser
import ebooklib
from   ebooklib import epub
import bs4 ### --- BeautifulSoup



### -------------------
### --- Loreto Modules
### -------------------
from functionExecutionTime import function_executing_time
import LnRegex







# #######################################################
# # book = epub.read_epub(percorso_file_epub)
# #######################################################
def extractMetadata(book):
    try:
        titles = book.get_metadata('DC', 'title')
        if titles:
            title = titles[0][0]

        creators = book.get_metadata('DC', 'creator')
        if creators:
            authors = [c[0] for c in creators]
        else:
            authors = ["Sconosciuto"]

    except Exception as e:
        ...
        # Aumentiamo la verbosità dell'errore per il debug
        # print(f"Errore durante l'estrazione dei metadati con EbookLib da '{percorso_file_epub}': {e}")

    return title, authors



##############################################################
# read epub book, return clean text and save it to fileout
##############################################################
# @function_executing_time
def read_epub(gVars: dict, epub_file: str, fileout: str=None):
    global gv
    gv=gVars

    content = ""

    decode_type = 'html.parser'
    decode_type = 'lxml'
    if decode_type == 'lxml':
        import warnings
        warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)


    try:
        book = epub.read_epub(epub_file)

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    raw_content = item.content
                    decoded_content = raw_content.decode('utf-8', errors='ignore')
                    soup = bs4.BeautifulSoup(decoded_content, decode_type)

                    # *** INIZIO MODIFICA PER NORMALIZZAZIONE TESTO ***
                    # Estrai il testo e poi normalizzalo ulteriormente
                    intermediate_clean_text = soup.get_text(separator=' ', strip=True)

                    # Rimuovi i salti di riga e i ritorni a capo per trattare tutto come una singola riga di testo
                    # e sostituisci eventuali spazi multipli con un singolo spazio
                    clean_text = re.sub(r'\s+', ' ', intermediate_clean_text).strip()
                    # *** FINE MODIFICA PER NORMALIZZAZIONE TESTO ***

                    content += clean_text + '\n'

                except Exception as e:
                    print(f"Errore nella lettura o elaborazione del contenuto dell'elemento in '{epub_file}': {e}")

    except Exception as e:
        # Aumentiamo la verbosità dell'errore per il debug
        print(f"Errore durante l'apertura di '{epub_file}' con EbookLib: {e}")

    if fileout:
        with open(fileout, 'w', encoding='utf-8') as fout:
            fout.write(content)

    return content




def process(gVars):
    global gv, logger
    gv = gVars
    logger = gv.logger
    args   = gv.args

    ebookRootDir=Path(args.dir_name).resolve()
    search_string=args.search


    files=fileList(ebookRootDir, pattern=f'*{args.extension}')
    # for file in files[0:3]:
    search_strings = " ".join(gv.args["search"])

    for filepath in files:
        file = Path(filepath)
        fileOut = f"{args.out_dir}/{filepath.stem.replace(' ', '_')}.txt"

        logger.info("reading book: %s", file.name)

        # clean_text = eBooks.read_epub(gVars=gv, epub_file=filepath, fileout=fileOut)

        # lnTimeIt(fStart=True)
        # text_split(clean_text)
        # lnTimeIt("fine dello splitting del eBook", fStart=False, fPause=False)



        # logger.info("searching string: %s", search_strings)
        # wordsFound = eBooks.searchString(source_string=clean_text, search_string=search_strings, exact_match=True, word_distance=5)
        # lnTimeIt(fStart=False)
        # for item in wordsFound:
        #     # logger.notify(item)
        #     print(item)
        #     print()

