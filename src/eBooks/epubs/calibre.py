# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/epubs/calibre.py

from pathlib import Path
import os
import shutil


from pyLnLib.calibre import CalibreMetadataReader
from pyLnLib.epub import author_registry
from pyLnLib.context import pVars as pv
from pyLnLib import get_emoji
from pyLnLib.logger import get_logger
from pyLnLib.files import get_unique_filename


from .clean_filename import clean_filename

E=get_emoji()
logger=get_logger()

# ============================================================
# inizializza calibre con la libreria passata
# ============================================================
def initialize_calibre(library: str|Path) -> CalibreMetadataReader:
    reader = CalibreMetadataReader(library)

    # ===== 1. Indici caricati all'avvio =====
    logger.info("📊 Libreria:")
    logger.info(f"\tTotale libri:      {reader.count:-5}")
    logger.info(f"\tTotale autori:     {len(reader.authors):-5}")
    logger.info(f"\tDuplicati trovati: {reader.duplicate_count:-5}")

    logger.info(f"""📊 Libreria:\n
                Totale libri:      {reader.count:-5}\n
                Totale autori:     {len(reader.authors):-5}\n
                Duplicati trovati: {reader.duplicate_count:-5}\n
                """)

    # for author, book_ids in reader.authors.items():
    #     logger.info(f"{E.arrow_right} {author}: {len(book_ids)} libri")
    return reader


def showAuthors(library_path: Path):
    pv.calibre = initialize_calibre(library_path)

    authors_ln = pv.calibre.get_authors_ln()
    wrong_authors = []
    for index, (author, book_ids) in enumerate(authors_ln.items()):
        logger.info(f"{E.arrow_right}  {index:03d}: {author:<30} - {len(book_ids):3} libri - {book_ids} ")
        # logger.info(f"{E.arrow_right}  {index:03d}: {author:<30} ({len(book_ids):3} libri) {book_ids:<30} ")

        author=pv.author_registry.format(author, canonical=False)
        '''
        if '|' in author:
            if pv.args.update_authors: # author corretto di calibre "Cognome| nome""
                author=pv.author_registry.format(author, canonical=False)

        else:
            if len(author.split()) > 1: # non c'è il carattere "|"dè  più di una word
                wrong_authors.append((author, book_ids))
        '''


    # per i nomi di autori non corretti
    # stampiamo il relativo libro
    for index, (author, book_ids) in enumerate(wrong_authors):
        logger.warning(f"  {index:03d}: {author:<30} ({len(book_ids)} libri)")
        for book_id in book_ids:
            book = pv.calibre.get_book(book_id)
            logger.warning(f"    {book_id:03d}: %s", book)
    logger.notify("Autori trovati: " + str(len(authors_ln)))




#==========================================
# - copy new epub_files to my target epub_main_path
# -     text/
# -         author/
# -     epubs/
# -         author/
#==========================================
def processCalibreLibrary(library_path: Path, target_path: Path) -> None:
    pv.calibre = initialize_calibre(library_path)

    authors = pv.calibre.get_authors()
    for index, author in enumerate(authors):
        logger.debug(f"{E.arrow_right}  {index:03d}: {author}")

    authors_ln = pv.calibre.get_authors_ln()
    wrong_authors = []
    for index, (author, book_ids) in enumerate(authors_ln.items()):
        logger.info(f"{E.arrow_right}  {index:03d}: {author:<30} ({len(book_ids)} libri)")
        if not '|' in author and len(author.split()) > 0:
            wrong_authors.append(f"  {index:03d}: {author:<30} ({len(book_ids)} libri)")

    for author in wrong_authors:
        logger.warning(author)
    # logger.warning(f"  {index:03d}: {author:<30} ({len(book_ids)} libri)")
    import sys; sys.exit("Autori trovati: " + str(len(authors)))
    # ----------------------------------------------------
    # - moving to target dir per lavorare con il relative_paths
    # ----------------------------------------------------
    os.chdir(target_path)

    # ----------------------------------------------------
    # - Itera sulla list libri
    # - inserisce nel book l'indice di lista del libro
    # ----------------------------------------------------
    nfiles = pv.calibre.count
    for index, id in enumerate(pv.calibre.ids[pv.args.start_id:]):
        print()

        logger.info(f"id: {id}")
        book = pv.calibre.get_book(id)
        authors = book.get('authors')
        authors=' '.join(authors) # per ora faccio il join anche se più di uno
        logger.info(f"book: {book}")
        logger.info(f"Autori: {authors}")
        source_epub = book.file_path # type: ignore
        author=pv.author_registry.format(authors, canonical=False) # type: ignore
        # breakpoint()
        # author = [ pv.author_registry.format(author, canonical=False) for author in book["authors"] ]
        inx=f"{index:03d}/{nfiles:03d}"
        logger.info("%s - processing:\n%s/%s", inx, author, source_epub.name) # type: ignore

        if author:
            cleaned_title = clean_filename(text=book.title) # type: ignore
            logger.info("\tcleaned_title: %s", cleaned_title)
            rel_output_filename=Path(author) / f"{cleaned_title}.epub"
            rel_output_filename.parent.mkdir(parents=True, exist_ok=True)

            target_filename = get_unique_filename(rel_output_filename)

            if target_filename is None:
                """file esiste già, ha lo stesso size e lo stesso SHA256 - non facciamo nulla"""
                continue


            elif target_filename == rel_output_filename:
                """file non esiste"""
                logger.info("\tcopying as: \n%s", rel_output_filename)
                shutil.copy2(source_epub, target_filename)
                continue

            else:
                """ file exists, change output_directory to put duplicated"""
                # breakpoint()
                logger.info("\talready exists! %s", rel_output_filename)
                rel_output_filename=rel_output_filename.parent / "duplicated" / f"{cleaned_title}.epub"
                rel_output_filename.parent.mkdir(parents=True, exist_ok=True)
                target_filename = get_unique_filename(rel_output_filename, start_index=1)
                if target_filename is None:
                    logger.info("\talready exists on duplicated!")
                else:
                    logger.info("\tcopying as: \n%s", rel_output_filename)
                    shutil.copy2(book.file_path, target_filename) # type: ignore

        else:
            logger.error("\tno author found!")
