#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""

import sys
# from pathlib import Path


# --- pyLnLib modules
from pyLnLib.logger    import get_logger
# from pyLnLib.epub      import EpubProcessor
from pyLnLib.files      import scan_directory


# --- project modules
from .init.initialize_program import initialize_program
# from .calibre.calibre import show_duplicated_books

logger = get_logger()




# ruff: noqa: SIM114 Combine `if` branches using logical `or` operator help: Combine `if` branches (Ruff SIM114)
def main():
    ctx = initialize_program()

    # reader = CalibreMetadataReader(calibre_path)

    # ===== 1. Indici caricati all'avvio =====
    logger.info("📊 Libreria:")
    logger.info(f"\tTotale libri:      {ctx.calibre.count}")
    logger.info(f"\tTotale autori:     {len(ctx.calibre.authors)}")
    logger.info(f"\tDuplicati trovati: {ctx.calibre.duplicate_count}")


    if ctx.args.choice == 'duplicated':
        logger.info(ctx.calibre.get_duplicate_report())

    elif ctx.args.choice == 'no-path':
        _data=show_duplicated_books(reader=ctx.calibre)

    elif ctx.args.choice == 'search':
        ...

    elif ctx.args.choice == 'extract':
        for source_dir in ctx.config.dirs.source_top_dir:
            file_list = scan_directory(root_dir=source_dir, pattern='*.epub')
            nfiles=len(file_list)
            logger.info(file_list)
            for index, file in enumerate(file_list):
                if file.stem in ctx.config.files_to_skip:
                    logger.warning(f"Skipping {file.stem}")
                    continue
                process_epub(epub_path=file, export_dir=ctx.config.dirs.extract_dir, index=f"{index:04}/{nfiles:04}")


    # sys.exit("temporary exit")

if __name__ == "__main__":
    main()
