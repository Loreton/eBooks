
#
from pathlib import Path
import shutil


# --- pyLnLib modules
from pyLnLib.context    import ctx
from pyLnLib.logger    import get_logger
from pyLnLib.files import unique_filename
from pyLnLib.epub      import EpubProcessor, get_epub_processor, manage_epub_processor
from pyLnLib.files      import scan_directory

logger = get_logger()



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
def copy_new(epubs_path: Path, target_path: Path, multiple_copies: bool=False) -> None:
    file_list = scan_directory(root_dir=epubs_path, pattern='*.epub')
    nfiles=len(file_list)
    logger.info(file_list)

    # Itera sui processori validi
    index = 0
    for book in manage_epub_processor(file_list):
        # Processa il libro
        index += 1
        inx=f"{index:03d}/{nfiles:03d}"

        author = book.author
        print()
        logger.info("%s - processing:\n%s/%s", inx, book.author, book.filename.name)


        if author:
            output_filename = target_path / "epubs" / author / book.title
            output_filename.parent.mkdir(parents=True, exist_ok=True)
            if multiple_copies:
                output_filename = unique_filename(output_filename) # assicuriamocie che non ricopra filesistenti
            else:
                if output_filename.exists():
                    logger.info("\talready exists!")
                    continue

            shutil.copy2(file, output_filename)

            logger.info("filename:   %s", book.filename)
            logger.info("title:      %s", book.title)
            logger.info("author:     %s", book.author)
            logger.info("language:   %s", book.language)
            logger.info("identifier: %s", book.identifier)
            logger.info("sections:   %s", len(book.get_sections()))

        else:
            logger.warning("no author:  %s", book.filename)

#==========================================
# - copy new epub_files to my target epub_main_path
# -     text/
# -         author/
# -     epubs/
# -         author/
#==========================================
def copy_new2(epubs_path: Path, target_path: Path, multiple_copies: bool=False) -> None:
    file_list = scan_directory(root_dir=epubs_path, pattern='*.epub')
    nfiles=len(file_list)
    logger.info(file_list)

    for index, file in enumerate(file_list):
        if file.stem in ctx.config.files_to_skip:
            logger.warning(f"Skipping {file.stem}")
            continue

        inx=f"{index:03d}/{nfiles:03d}"
        # book = EpubProcessor(file)


        book = get_epub_processor(file)
        if book is None:
            continue

        author = book.author
        print()
        logger.info("%s - processing:\n%s/%s", inx, book.author, book.filename.name)


        if author:
            output_filename = target_path / "epubs" / author / book.title
            output_filename.parent.mkdir(parents=True, exist_ok=True)
            if multiple_copies:
                output_filename = unique_filename(output_filename) # assicuriamocie che non ricopra filesistenti
            else:
                if output_filename.exists():
                    logger.info("\talready exists!")
                    continue

            shutil.copy2(file, output_filename)

            logger.info("filename:   %s", book.filename)
            logger.info("title:      %s", book.title)
            logger.info("author:     %s", book.author)
            logger.info("language:   %s", book.language)
            logger.info("identifier: %s", book.identifier)
            logger.info("sections:   %s", len(book.get_sections()))

        else:
            logger.warning("no author:  %s", book.filename)

def init_epubs():
    ...
