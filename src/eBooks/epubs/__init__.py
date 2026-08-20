# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/calibre/__init__
# .py
from .epubs      import extract_text, copy_new
from .calibre    import start_calibre, processCalibreLibrary, loadAuthors_from_books, loadAuthors
from .clean_filename    import clean_filename

__all__ = [
    "start_calibre",
    "extract_text",
    "copy_new",
    "processCalibreLibrary",
    "clean_filename",
    "loadAuthors",
]
