#
# ruff: noqa: SIM113 - Use `enumerate()` for index variable `index` in `for` loop (Ruff SIM113)
from multiprocessing.reduction import register
import os
from pathlib import Path
import shutil
import re


# --- pyLnLib modules
from pyLnLib.context    import pVars as pv
from pyLnLib.logger    import get_logger
from pyLnLib.files import get_unique_filename
from pyLnLib.epub      import EpubProcessor,  manage_epub_processor
from pyLnLib.files      import scan_directory
from pyLnLib.varie      import menu_select_from_list



from .clean_filename import clean_filename
logger = get_logger()







#==========================================
# - main_folder/
# -     author/
# -         text/
# -         epubs/
#==========================================
# def extract_text(epub_path: str|Path, main_folder: Path | None = None, index: str|None=None) -> None:
def extract_text(epubs_top_dir: Path, target_path: Path, replace: bool = False) -> None:
    file_list = scan_directory(root_dir=epubs_top_dir, pattern='*.epub')
    nfiles=len(file_list)
    logger.debug(file_list)

    os.chdir(target_path)

    for index, book in enumerate(manage_epub_processor(book_files=file_list), 1): # type: ignore
        print()
        if book.author.startswith("Colleen"):
            pass

        # non aggiorniamo il registry perché sugli epub sciolti potrebberossercirrori nei nomi autori
        author_name=pv.author_registry.format(book.author, canonical=False, registry_update=False)[0]
        print()
        dest_author_path = Path(author_name)
        dest_author_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"{index:03d}/{nfiles:03d}: -{author_name}-")

        logger.info("\tepub title: %s", book.title)
        cleaned_title = clean_filename(text=book.title)
        logger.info("\ttext title: %s", cleaned_title)

        rel_output_filename=dest_author_path / f"{cleaned_title}.txt"
        # - creiamo l'istanza EpubProcess per il file epub
        # - ed il metodo to_text() per convertire il file epub in testo
        epub_obj = EpubProcessor(book.file_path)
        epub_obj.to_text(txt_filename=rel_output_filename, replace=replace, force_log=False)





















#==========================================
# - copy new epub_files to my target epub_main_path
# -     text/
# -         author/
# -     epubs/
# -         author/
#==========================================
def copy_new(epubs_path: Path, target_path: Path) -> None:
    file_list = scan_directory(root_dir=epubs_path, pattern='*.epub')
    nfiles=len(file_list)
    logger.debug(file_list)

    # ----------------------------------------------------
    # - moving to target dir per lavorare con il relative_paths
    # ----------------------------------------------------
    os.chdir(target_path)

    # ----------------------------------------------------
    # - Itera sulla list libri
    # - inserisce nel book l'indice di lista del libro
    # ----------------------------------------------------
    for book in manage_epub_processor(book_files=file_list): # type: ignore
        print()
        source_epub = book.filename
        inx=f"{book.index:03d}/{nfiles:03d}"

        # - trasforma il nome dell'autore in formato 'Surname Name'

        logger.info("%s - processing:\n%s/%s", inx, book.author, source_epub.name)

        author=pv.author_registry.format(book.author, canonical=False)
        if author:
            cleaned_title = clean_filename(text=str(book.title))
            logger.info("\tcleaned_title: %s", cleaned_title)

            rel_output_filename=Path(author) / f"{cleaned_title}.epub"
            # logger.info("\twill be copied as: \n%s", rel_output_filename)
            rel_output_filename.parent.mkdir(parents=True, exist_ok=True)

            target_filename = get_unique_filename(rel_output_filename)

            if target_filename is None:
                """file esiste già, ha lo stesso size e lo stesso SHA256 - non facciamo nulla"""
                continue


            elif target_filename == rel_output_filename:
                """file non esiste"""
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
                    shutil.copy2(book.filename, target_filename)

            # logger.info("filename:   %s", book.filename)
            # logger.info("title:      %s", book.title)
            # logger.info("author:     %s", book.author)
            # logger.info("language:   %s", book.language)
            # logger.info("identifier: %s", book.identifier)
            # logger.info("sections:   %s", len(book.get_sections()))

        else:
            logger.error("\tno author found!")
