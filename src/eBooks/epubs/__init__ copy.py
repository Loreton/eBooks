# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/calibre/__init__
# .py
from .epubs      import extract_text, copy_new
from .calibre    import start_calibre, authors_from_authors, authors_from_ebooks
from .clean_filename    import clean_filename

__all__ = [
    "start_calibre",
    "extract_text",
    "copy_new",
    "authors_from_authors",
    "authors_from_ebooks",
    "clean_filename",
]
