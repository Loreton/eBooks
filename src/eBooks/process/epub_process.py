#
# ruff: noqa: SIM113 - Use `enumerate()` for index variable `index` in `for` loop (Ruff SIM113)

import os
from pathlib import Path
import shutil
from datetime import datetime


# --- pyLnLib modules
from pyLnLib.context    import pVars as pv
from pyLnLib.logger    import get_logger
from pyLnLib.files import get_unique_filename
from pyLnLib.epub      import EpubManager
from pyLnLib.files      import scan_directory
from pyLnLib.varie import keyboardPrompt, select_from_list



from .clean_filename import clean_filename
logger = get_logger()







#==========================================
# - main_folder/
# -     author/
# -         text/
# -         epubs/
#==========================================
def extract_text(epubs_top_dir: Path, target_path: Path, replace: bool = False) -> None:
    file_list = scan_directory(root_dir=epubs_top_dir, pattern='*.epub')
    nfiles=len(file_list)
    logger.debug(file_list)

    os.chdir(target_path)
    # file_list=['/home/loreto/.aMule/Copied/Verity - Hoover, Colleen.epub']
    # file_list=['/home/loreto/filu/ln-eBooks/lnExtracted/epubs/Bluebook/TREDICESIMA STORIA, lA.epub']

    for index, epub_path in enumerate(file_list, 1):
        # logger.info("working on file: %s", epub_path)
        try:
            with EpubManager(epub_path) as book:
                print()
                logger.info(f"{index:03d}/{nfiles:03d}:\n{book.source_path}")
                # non aggiorniamo il registry perché sugli epub sciolti potrebbero esserci errori nei nomi autori
                author_name=pv.author_registry.format(book.author, canonical=True, registry_update=False)
                if not author_name:
                    continue

                author_name = author_name[0]
                cleaned_title = clean_filename(text=book.title)


                logger.info(f"\torig. author %s", book.author)
                logger.info(f"\tnew   author %s", author_name)
                logger.info(f"\torig. title  %s", book.title)
                logger.info(f"\tnew   title  %s", cleaned_title)


                # dest_author_path = Path(author_name)
                # dest_author_path.mkdir(parents=True, exist_ok=True)


                # logger.info("\tepub title: %s", book.title)

                # rel_output_filename=dest_author_path / f"{cleaned_title}.txt"
                # - creiamo l'istanza EpubProcess per il file epub
                # - ed il metodo to_text() per convertire il file epub in testo
                # epub_obj = EpubManager(book.file_path)
                # epub_obj.to_text(txt_filename=rel_output_filename, replace=replace, force_log=False)
        except Exception as e:
            logger.error("%s", e, show_stack=True)
            breakpoint()


def select_author(book) -> str:
    # non aggiorniamo il registry perché sugli epub sciolti potrebbero esserci errori nei nomi autori
    authors=pv.author_registry.format(book.author, canonical=True, registry_update=False)
    author_name=' & '.join(authors)
    cleaned_title = clean_filename(text=book.title)

    authors_choice=[
        book.author,
        author_name,
    ]
    default=1
    author = select_from_list(data=authors_choice,
                            text_msg="please select author name or [ENTER.default/new/skip]: ",
                            extra_validKeys=["ENTER", "new", "skip"],
                            default=default+1) # l'indice partirà da 1, quindi default+1 per selezionare il secondo elemento della lista

    if author == "new":
        author=""
        l_choice = keyboardPrompt(text_msg="please enter custom author name: ", validKeys=[])
        if l_choice != ["ENTER"]:
            author = l_choice[0]

    elif author == "skip":
        author = ""

    # elif author == "ENTER":
    #     author = authors_choice[default]

    logger.info(f"author: {author}")
    return author



def select_title(book) -> str:
    cleaned_title = clean_filename(text=book.title)
    title_choice = [
        book.title,
        cleaned_title,
    ]
    default=1
    title = select_from_list(data=title_choice,
                            text_msg="please select title or [ENTER.default/new/skip]: ",
                            extra_validKeys=["ENTER", "new", "skip"],
                            default=default+1) # l'indice partirà da 1, quindi default+1 per selezionare il secondo elemento della lista

    if title == "new":
        title=""
        l_choice = keyboardPrompt(text_msg="please enter custom title name: ", validKeys=[])
        if l_choice != ["ENTER"]:
            title = l_choice[0]

    elif title == "skip":
        title = ""

    elif title == "ENTER":
        title = title_choice[default]

    logger.info(f"title: {title}")
    return title

#==========================================
# - cerchiamo di aggiornare authors title
#==========================================
def update_metadata(epubs_top_dir: Path, target_path: Path|str, replace: bool = False) -> None:
    target_path = Path(target_path)
    file_list = scan_directory(root_dir=epubs_top_dir, pattern='*.epub')
    nfiles=len(file_list)
    logger.debug(file_list)

    # file_list=['/home/loreto/filu/ln-eBooks/lnCollection/new/March, Meghan/Billionaire#02 - Miele.epub']
    os.chdir(target_path)

    for index, epub_path in enumerate(file_list, 1):
        with EpubManager(epub_path) as book:
            modified_by = book.get_custom_metadata(key="modified_by")
            modified_date = book.get_custom_metadata(key="modified_date")
            if modified_by and modified_by == 'Loreto':
                logger.notify("already processed by: %s on %s", modified_by, modified_date)
                continue

            print()
            logger.info(f"{index:03d}/{nfiles:03d}:\n{book.source_path}")
            # non aggiorniamo il registry perché sugli epub sciolti potrebbero esserci errori nei nomi autori
            author_name=pv.author_registry.format(book.author, canonical=True, registry_update=False)
            if not author_name:
                continue

            author_name = author_name[0]
            new_title = clean_filename(text=book.title)

            chnged_by = book.get_custom_metadata("changed_by")
            logger.info("\torig. author %s", book.author)
            logger.info("\tnew   author %s", author_name)
            logger.info("\torig. title  %s", book.title)
            logger.info("\tnew   title  %s", new_title)
            f_save: bool = False

            if author_name != book.author:
                author_name = select_author(book)
                if not author_name:
                    continue
                # aggiornameto dei metadati....
                book.set_author(new_author=author_name)
                f_save = True
                # logger.info("\tchanged author  %s", book.author)

            if new_title != book.title:
                new_title = select_title(book)
                if not new_title:
                    continue
                # aggiornameto dei metadati....
                book.set_title(new_title=new_title)
                f_save = True
                # logger.info("\tchanged title  %s", book.title)



            if f_save:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                book.set_custom_metadata(key="modified_by", value="Loreto")
                book.set_custom_metadata(key="modified_date", value=now)
                book.set_custom_metadata(key='processed_by', value='EpubManager v2.0')

                # 5. Salva in nuovo file
                output_file = target_path / author_name / f"{new_title}.epub"
                path_for_duplicated=output_file.parent / "duplicated"
                target_file=get_unique_filename(filename=output_file, path_for_duplicated=path_for_duplicated)
                if target_file:
                    logger.info(f"Saving...: %s", target_file)
                    book.save(target_file)
                else:
                    logger.warning("file already exists: %s", target_file)

        # except Exception as e:
        #     logger.error("%s", e, show_stack=True)
        #     breakpoint()






















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
