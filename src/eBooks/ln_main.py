#!/usr/bin/env python3
# ln_main.py
#
#
from pathlib import Path

# pyLnLib modules
from pyLnLib.logger import init_logger
from pyLnLib.files import scan_directory


# this program modules
from eBooks import EpubProcessor





def save_text_file(text: str, output_dir: Path, filename: str) -> None:
    file_path = output_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


def process_epub(epub_path: str|Path, output_dir: Path | None = None) -> None:
    book = EpubProcessor(epub_path)
    book.process_epub(output_dir=output_dir)
    # Salva il report degli autori e dei conflitti
    if output_dir:
        book.save_text_file()
        book._save_conflict_report(output_dir)





def test_01(epub_path: str|Path, export_dir: Path | None = None) -> None:
    epub_path = Path(epub_path)
    book = EpubProcessor(epub_path)
    logger.info("filename:   %s", book.filename)
    logger.info("title:      %s", book.get_title())
    logger.info("author:     %s", book.get_author())
    logger.info("language:   %s", book.get_language())
    logger.info("identifier: %s", book.get_identifier())
    logger.info("sections:   %s", len(book.get_sections()))

    if export_dir is not None:
        filename = Path(export_dir) / str(book.get_author()) / epub_path.with_suffix('.txt').name
        # book.export_text(output_dir=export_dir, filename=epub_path.with_suffix('.txt').name)
        _ = book.export_text(filename=filename)
        logger.info('exported to: "%s"', filename)




if __name__ == "__main__":
    logger = init_logger()
    f_scan=False
    f_export=True

    if f_scan:
        file_list = scan_directory(root_dir="/home/loreto/filu/ln-eBooks/new_books", pattern='*.epub')
        logger.info(file_list)
        for file in file_list:
            test_01(file, f_export=f_export)
    else:
        epub_file="/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub"
        export_dir = Path(epub_file).parent / "export"
        test_01(epub_path=epub_file, export_dir=export_dir)
