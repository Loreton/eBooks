# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/calibre/__init__
# .py
from .epubs      import extract_text, copy_new
from .calibre    import initialize_calibre, processCalibreLibrary, showAuthors
from .clean_filename    import clean_filename

__all__ = [
    "initialize_calibre",
    "extract_text",
    "copy_new",
    "processCalibreLibrary",
    "clean_filename",
    "showAuthors",
]
