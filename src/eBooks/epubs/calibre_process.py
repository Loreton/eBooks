# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/epubs/calibre.py

from pathlib import Path
import os
import shutil


from pyLnLib.context import pVars as pv
from pyLnLib.epub import CalibreMetadataReader, EpubProcessor
from pyLnLib import get_emoji, lnDict
from pyLnLib.logger import get_logger
from pyLnLib.files import get_unique_filename
from pyLnLib.system import clean_doc
from pyLnLib.varie      import menu_select_from_list

from .clean_filename import clean_filename

E=get_emoji()
logger=get_logger()



# ============================================================
# inizializza calibre con la libreria passata
# ============================================================
def start_calibre(libraries: list) -> CalibreMetadataReader:
    _choice, library = menu_select_from_list(libraries)
    reader = CalibreMetadataReader(Path(library))

    # ===== 1. Indici caricati all'avvio =====
    logger.info(clean_doc("""Libreria:\n
                Totale libri:      %s\n
                Totale autori:     %s\n
                Duplicati trovati: %s\n
                """), reader.count, len(reader.authors), reader.duplicate_count)


    return reader


#============================================================
# - lavora con la lista degli autori e basta.
# - Può essere utile per verificare author_registry.format()
# - e per caricare gli autori nello yaml
#============================================================
def authors_from_authors(reader: CalibreMetadataReader):
    authors_ln = reader.get_authors_ln()
    for index, (author, book_ids) in enumerate(authors_ln.items()):
        logger.info(f"{index:03d}: {author:<30} - {len(book_ids):3} libri - {book_ids} ")

        author=pv.author_registry.format(author, canonical=False)

        logger.info("\tnormalized: %s", author)


#============================================================
# - Esplora tutti i libri e mostra/carica nello yaml gli autori
# - Per ogni libro potrei avere più di un autore.
# - La stessa cosa di showAuthors ma con più dettagli del libro.
#============================================================
def authors_from_ebooks(reader: CalibreMetadataReader):
    IDs = reader.get_all_ids()

    for book_id in IDs:
        book: lnDict= reader.get_book(book_id)
        authors: list = book.authors
        logger.warning(f"  {book_id:03d}: {authors} - {book.title}")
        authors = pv.author_registry.format(authors, canonical=True)
        logger.info(f"  {authors = }")






#==========================================
# - copy new epub_files to my target epub_main_path
# -     text/
# -         author/
# -     epubs/
# -         author/
#==========================================
def library_to_text(reader: CalibreMetadataReader, target_path: Path) -> None:
    authors_ln = reader.get_authors_ln()
    n_authors = len(authors_ln)
    # ----------------------------------------------------
    # - moving to target dir per lavorare con il relative_paths
    # ----------------------------------------------------
    os.chdir(target_path)

    for index, (author, book_ids) in enumerate(authors_ln.items()):
        print()
        author_name=pv.author_registry.format(author, canonical=False, registry_update=True)
        if not author_name:
            logger.warning(f"{index:03d}: {author:<30} - {len(book_ids):3} libri - {book_ids} ")
            logger.warning(f"Author not found in registry: {author}")
            continue
        else:
            author_name = author_name[0]
        dest_author_path = Path(author_name)
        dest_author_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"{index:03d}/{n_authors:<3}: {author_name:<30} - {len(book_ids):3} libri - {book_ids} ")

        # - per l'author in questione vediamo i libri
        for id in book_ids:
            book = reader.get_book(id)
            logger.info("\tepub title: %s", book.title)
            cleaned_title = clean_filename(text=book.title)
            logger.info("\ttext title: %s", cleaned_title)

            rel_output_filename=dest_author_path / f"{cleaned_title}.txt"
            # - creiamo l'istanza EpubProcess per il file epub
            # - ed il metodo to_text() per convertire il file epub in testo
            epub_obj = EpubProcessor(book.file_path)
            epub_obj.to_text(txt_filename=rel_output_filename, replace=False, force_log=False)






#==========================================
# - copy new epub_files to my target epub_main_path
# -     text/
# -         author/
# -     epubs/
# -         author/
#==========================================
def epub_to_text_OK0(reader: CalibreMetadataReader, target_path: Path) -> None:
    authors_ln = reader.get_authors_ln()
    # ----------------------------------------------------
    # - moving to target dir per lavorare con il relative_paths
    # ----------------------------------------------------
    os.chdir(target_path)

    for index, (author, book_ids) in enumerate(authors_ln.items()):
        print()
        author_name=pv.author_registry.format(author, canonical=False)[0]
        dest_author_path = Path(author_name)
        dest_author_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"{index:03d}: {author_name:<30} - {len(book_ids):3} libri - {book_ids} ")

        # - per l'author in questione vediamo i libri
        for id in book_ids:
            book = reader.get_book(id)
            logger.info("\tepub title: %s", book.title)
            cleaned_title = clean_filename(text=book.title)
            logger.info("\ttext title: %s", cleaned_title)

            # - creiamo l'istanza EpubProcess per il file epub
            source_epub = book.file_path
            epub_obj = EpubProcessor(source_epub)

            rel_output_filename=dest_author_path / f"{cleaned_title}.txt"
            target_filename = get_unique_filename(rel_output_filename)


            if target_filename:
                """file non esiste"""
                if not epub_obj.to_text(txt_filename=target_filename, replace=False):
                    logger.info("\tfile already exists!")
                continue
            else:
                """file esiste già, ha lo stesso size e lo stesso SHA256 - non facciamo nulla"""
                logger.info("\tfile already exists!")
                continue

            # else:
            #     """ file exists, change output_directory to duplicated to mantains more copies of the same book ????"""
            #     logger.info("\talready exists! %s", rel_output_filename)
            #     rel_output_filename=rel_output_filename.parent / "duplicated" / f"{cleaned_title}.epub"
            #     rel_output_filename.parent.mkdir(parents=True, exist_ok=True)
            #     target_filename = get_unique_filename(rel_output_filename, start_index=1)
            #     if target_filename is None:
            #         logger.info("\talready exists on duplicated!")
            #     else:
            #         logger.info("\tcopying as: \n%s", rel_output_filename)
            #         shutil.copy2(book.file_path, target_filename) # type: ignore
