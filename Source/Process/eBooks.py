#! /usr/bin/env python3
# updated by ...: Loreto Notarantonio
# Date .........: 28-09-2025 18.24.58
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
    def get_first_item(value):
        if value:
            if isinstance(value, (list, tuple)):
                value = get_first_item(value[0])
        else:
            value = "Sconosciuto"
        return value


    try:
        titles = book.get_metadata('DC', 'title')
        title = get_first_item(titles)

        creators = book.get_metadata('DC', 'creator')
        authors = get_first_item(creators)

    except Exception as e:
        ...
        # Aumentiamo la verbosità dell'errore per il debug
        # logger.error("Errore durante l'estrazione dei metadati con EbookLib: %s",  e)

    return title, authors


##############################################################
# read epub book, return clean text and save it to fileout
##############################################################
# @function_executing_time
def read_epub(epub_file: str, out_dir: str=None):
    ebook = {}

    decode_type = 'html.parser'
    decode_type = 'lxml'
    if decode_type == 'lxml':
        import warnings
        warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)

    try:
        book = epub.read_epub(epub_file)
    except Exception as e:
        logger.error("Errore durante l'apertura del file: %s - %s", epub_file,  e)
        return {}

    ebook["title"], ebook["authors"] = extractMetadata(book)

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            raw_content = item.content
            decoded_content = raw_content.decode('utf-8', errors='ignore')
            soup = bs4.BeautifulSoup(decoded_content, decode_type)

            ### --- INIZIO MODIFICA PER NORMALIZZAZIONE TESTO ***
            # Estrai il testo e poi normalizzalo ulteriormente
            intermediate_clean_text = soup.get_text(separator=' ', strip=True)

            # Rimuovi i salti di riga e i ritorni a capo per trattare tutto come una singola riga di testo
            # e sostituisci eventuali spazi multipli con un singolo spazio
            clean_text = re.sub(r'\s+', ' ', intermediate_clean_text).strip()
            ### --- FINE MODIFICA PER NORMALIZZAZIONE TESTO ***

            ### --- la prima word dovrebbe essere il numero della parte
            part_name, *_rest = clean_text.split(' ', 1)
            if part_name in ["title"]:
                continue
            # print(part_name)
            ebook[part_name] = _rest


    if out_dir:
        # print(ebook["title"])
        # print(ebook["authors"])
        # import pdb; pdb.set_trace() # by Loreto
        title = ebook["title"].replace(' ', '_') if ebook["title"] else ""
        main_author = ebook["authors"][0].replace(' ', '_') if ebook["authors"] else ""
        fileout=f'{out_dir}/{title}_{main_author}.txt'
        if False:
            with open(fileout, 'w', encoding='utf-8') as fout:
                for key, value in ebook.items():
                    logger.debug("writing key: %s", key)

                    fout.write(key)
                    fout.write(':\n')
                    if isinstance(value, list):
                        fout.write(', '.join(value))
                    else:
                        fout.write(value)
                    fout.write('\n\n')

        logger.debug("%s_%s.txt has been written", title, main_author)

    return ebook


##############################################################
# read epub book, return clean text and save it to fileout
##############################################################
# @function_executing_time
def process_epub(book, title: str, authors: str, out_dir: str=None):
    ebook = {}
    # ebook["title"] = title.replace(' ', '_')
    # ebook["authors"] = authors.replace(' ', '_')
    ebook["title"] = title
    ebook["authors"] = authors

    decode_type = 'html.parser'
    decode_type = 'lxml'
    if decode_type == 'lxml':
        import warnings
        warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            raw_content = item.content
            decoded_content = raw_content.decode('utf-8', errors='ignore')
            soup = bs4.BeautifulSoup(decoded_content, decode_type)

            ### --- INIZIO MODIFICA PER NORMALIZZAZIONE TESTO ***
            # Estrai il testo e poi normalizzalo ulteriormente
            intermediate_clean_text = soup.get_text(separator=' ', strip=True)

            # Rimuovi i salti di riga e i ritorni a capo per trattare tutto come una singola riga di testo
            # e sostituisci eventuali spazi multipli con un singolo spazio
            clean_text = re.sub(r'\s+', ' ', intermediate_clean_text).strip()
            ### --- FINE MODIFICA PER NORMALIZZAZIONE TESTO ***

            ### --- la prima word dovrebbe essere il numero della parte
            part_name, *_rest = clean_text.split(' ', 1)
            if part_name in ["title"]:
                continue
            # print(part_name)
            ebook[part_name] = _rest


    if out_dir:
        fileout=f'{out_dir}/{title}_{authors}.txt'
        if False:
            with open(fileout, 'w', encoding='utf-8') as fout:
                for key, value in ebook.items():
                    logger.debug("writing key: %s", key)

                    fout.write(key)
                    fout.write(':\n')
                    if isinstance(value, list):
                        fout.write(', '.join(value))
                    else:
                        fout.write(value)
                    fout.write('\n\n')

        # logger.debug("%s_%s.txt has been written", title, authors)
        logger.debug("%s_%s.txt has been written", ebook["title"], ebook["authors"])

    return ebook


##############################################################
# read epub book, return clean text and save it to fileout
##############################################################
# @function_executing_time
def read_epub_01(epub_file: str, fileout: str=None):
    ebook = {}

    decode_type = 'html.parser'
    decode_type = 'lxml'
    if decode_type == 'lxml':
        import warnings
        warnings.filterwarnings("ignore", category=bs4.XMLParsedAsHTMLWarning)

    try:
        book = epub.read_epub(epub_file)
        ebook["title"], ebook["authors"] = extractMetadata(book)

        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    raw_content = item.content
                    decoded_content = raw_content.decode('utf-8', errors='ignore')
                    soup = bs4.BeautifulSoup(decoded_content, decode_type)

                    ### --- INIZIO MODIFICA PER NORMALIZZAZIONE TESTO ***
                    # Estrai il testo e poi normalizzalo ulteriormente
                    intermediate_clean_text = soup.get_text(separator=' ', strip=True)

                    # Rimuovi i salti di riga e i ritorni a capo per trattare tutto come una singola riga di testo
                    # e sostituisci eventuali spazi multipli con un singolo spazio
                    clean_text = re.sub(r'\s+', ' ', intermediate_clean_text).strip()
                    ### --- FINE MODIFICA PER NORMALIZZAZIONE TESTO ***

                except Exception as e:
                    print(f"Errore nella lettura o elaborazione del contenuto dell'elemento in '{epub_file}': {e}")
                    # break

                finally:
                    ### --- la prima word dovrebbe essere il numero della parte
                    part_name, _rest = clean_text.split(' ', 1)
                    ebook[part_name] = _rest
                    print(part_name)

    except Exception as e:
        # Aumentiamo la verbosità dell'errore per il debug
        print(f"Errore durante l'apertura di '{epub_file}' con EbookLib: {e}")

    if fileout:
        with open(fileout, 'w', encoding='utf-8') as fout:
            for key, value in ebook.items():
                logger.info("writing key: %s", key)

                fout.write(key)
                fout.write(':\n')
                if isinstance(value, list):
                    fout.write(', '.join(value))
                else:
                    fout.write(value)
                fout.write('\n\n')

    return ebook



# ######################################################
# # get list of files recursive
# ######################################################
def fileList(root_path, folder='', pattern='*.*'):
    root_path=Path(root_path)
    root_path=root_path / folder
    file_list=list(root_path.glob(f'**/{pattern}'))

    return file_list



def process(gVars):
    global gv, logger
    gv = gVars
    logger = gv.logger
    args   = gv.args

    ebookRootDir=Path(args.dir_name).resolve()


    files=fileList(ebookRootDir, pattern='*.epub')

    index=0
    # for filepath in files[0:3]:
    for filepath in files:
        file = Path(filepath)
        index += 1
        # fileOut = f"{args.out_dir}/{filepath.stem.replace(' ', '_')}.txt"

        logger.info("[%s] - processing book: %s", index, file.name)
        try:
            book = epub.read_epub(filepath)
        except Exception as e:
            logger.error("Errore durante l'apertura del file: %s - %s", filepath,  e)
            continue

        data = book.get_metadata('DC', 'title') ### --- return list
        title = [c[0].replace("(Italian Edition)", '') for c in data]
        title = ' - '.join(title)
        if title == "Il verdetto":
            import pdb; pdb.set_trace() # by Loreto
        creators = book.get_metadata('DC', 'creator') ### --- return list
        authors = [c[0] for c in creators if c[0]]
        author = ' - '.join(authors) if authors else 'Sconosciuto'
        print(title)
        print(author)

        continue

        title, authors = extractMetadata(book)
        logger.info("      title:  %s", title)
        logger.info("      author: %s", authors)
        ebook = process_epub(book=book, title=title, authors=authors, out_dir=args.out_dir)


