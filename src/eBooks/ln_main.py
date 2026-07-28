#!/usr/bin/env python3
# ln_main.py
#
#
from pathlib import Path

# pyLnLib modules
from pyLnLib.logger import init_logger
from pyLnLib.files import scan_directory


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


def test_01(epub_path: str|Path):
    book = EpubProcessor(epub_path)
    print(book.filename)
    print(book.get_title())
    print(book.get_author())
    print(book.get_language())
    print(book.get_identifier())

    metadata = book.get_metadata()
    print(metadata)
    text = book.get_text()
    print(text)


def test_02(epub_path: str|Path):
    epub_path = Path(epub_path)
    book = EpubProcessor(epub_path)
    print(book.filename)
    print(book.get_title())
    print(book.get_author())
    print(book.get_language())
    print(book.get_identifier())

    print(len(book.get_sections()))
    book.export_text(epub_path.with_suffix('.txt'))

    # print(book.get_title())
    # print(book.get_author())
    # print(book.get_language())
    # print(book.get_identifier())

    # metadata = book.get_metadata()
    # print(metadata)
    # text = book.get_text()
    # print(text)


if __name__ == "__main__":
    logger = init_logger()
    f_scan=False
    # test_01()
    # test_02(file)
    if f_scan:
        file_list = scan_directory(root_dir="/home/loreto/filu/ln-eBooks/new_books", pattern='*.epub')
        logger.info(file_list)
        for file in file_list:
            test_02(file)
    else:
        epub_file="/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub"
        test_02(epub_path=epub_file)
