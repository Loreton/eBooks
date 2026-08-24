# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/calibre/__init__


import sys; sys.dont_write_bytecode=True


from .epub_process      import extract_text, copy_new
from .calibre_process    import start_calibre, authors_from_authors, authors_from_ebooks, library_to_text
from .clean_filename    import clean_filename

__all__ = [
    "start_calibre",
    "extract_text",
    "copy_new",
    "authors_from_authors",
    "authors_from_ebooks",
    "clean_filename",
    "library_to_text",
]
