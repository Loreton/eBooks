
#
import os
from pathlib import Path
import shutil
import re


# --- pyLnLib modules
from pyLnLib.context    import ctx, pVars as pv
from pyLnLib.logger    import get_logger
from pyLnLib.files import get_unique_filename
from pyLnLib.epub      import EpubProcessor, get_epub_processor, manage_epub_processor
from pyLnLib.files      import scan_directory
# from pyLnLib.epub      import AuthorRegistry

logger = get_logger()

def clean_filename(text: str) -> str:
    """
    Es: filename = "Mate: edizione italiana (Bride Vol. 2).epub"
    Rimuove tutto dal primo ':', '(', '[' o '-' fino alla fine della stringa
    Come funziona la regex r"(s*[:([-].*)":
        s*: ignora eventuali spazi prima del separatore.
        [:([-]: individua il punto di inizio del taglio (due punti :, parentesi tonda (, parentesi quadra [, o trattino -).
        .*: seleziona tutto il resto della stringa fino alla fine.
        "": sostituisce tutta la parte selezionata con una stringa vuota, lasciando solo il titolo principale.
    """


# Rimuove tutto dal primo ':', '(', '[' o '-' fino alla fine della stringa
    cleaned_text = re.sub(r"\s*[:\(\[-].*", "", text)
    cleaned_text = re.sub(r"s*[:([-].*", "", text)
    return cleaned_text.strip()


#==========================================
# - main_folder/
# -     author/
# -         text/
# -         epubs/
#==========================================
def extract_text(epub_path: str|Path, main_folder: Path | None = None, index: str|None=None) -> None:
    book = EpubProcessor(epub_path)
    author = book.author
    index=f"{index} - "  if index is not None else ''

    logger.info("%sprocessing: %s/%s", index, book.author, book.filename.name)
    # justxtract
    if main_folder:
        if author:
            output_dir = Path(main_folder) / author / "text"
            saved_filename = book.export_text(filename=output_dir / f"{book.filename.stem}.txt", replace=False, unique=False)
            logger.debug("saved:      \"%s\"", saved_filename)
        return


    logger.info("filename:   %s", book.filename)
    logger.info("title:      %s", book.title)
    logger.info("author:     %s", book.author)
    logger.info("language:   %s", book.language)
    logger.info("identifier: %s", book.identifier)
    logger.info("sections:   %s", len(book.get_sections()))

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

            rel_output_filename=Path("epubs") / author / f"{cleaned_title}.epub"
            logger.info("\twill be copied as: \n%s", rel_output_filename)
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


def init_epubs():
    ...
