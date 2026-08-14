#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""
# ruff: noqa: SIM114 Combine `if` branches using logical `or` operator help: Combine `if` branches (Ruff SIM114)


# --- pyLnLib modules
from pyLnLib.logger    import get_logger
from pyLnLib.files      import scan_directory
from pyLnLib.varie      import menu_select_from_list


# --- project modules
from .init.initialize_program import initialize_program
from .epubs.calibre import initialize_calibre
from .epubs.epubs import extract_text

logger = get_logger()




def main():
    ctx = initialize_program()
    args=ctx.args

    if args.choice == 'duplicated':
        logger.info(ctx.calibre.get_duplicate_report())

    elif args.choice == 'search':
        ...

    elif args.choice == 'extract':
        if args.calibre:
            _choice, library = menu_select_from_list(ctx.config.calibre_config.folders)
            ctx.calibre = initialize_calibre(library)
        else: # ---> args.epubs
            _choice, library = menu_select_from_list(ctx.config.epubs_config.folders)

        if isinstance(library, str):
            library=[library]
        for source_dir in library:
            file_list = scan_directory(root_dir=source_dir, pattern='*.epub')
            nfiles=len(file_list)
            logger.info(file_list)

            for index, file in enumerate(file_list):
                if file.stem in ctx.config.files_to_skip:
                    logger.warning(f"Skipping {file.stem}")
                    continue
                extract_text(epub_path=file, export_dir=ctx.config.main_folder, index=f"{index:04}/{nfiles:04}")

    elif ctx.args.choice == 'extract_from_calibre':
        calibre_folders = ctx.config.calibre
        print(calibre_folders.to_dict())
        breakpoint()

    # sys.exit("temporary exit")

if __name__ == "__main__":
    main()
