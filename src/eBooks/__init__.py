
import sys; sys.dont_write_bytecode=True

"""
Ebook Processor Package
A package for processing EPUB files with author normalization and conflict management
"""


#- ------ process folder
from .process.epub_process      import extract_text, copy_new
from .process.calibre_process    import start_calibre, authors_from_authors, authors_from_ebooks, library_to_text
from .process.clean_filename    import clean_filename

#- ------ input_init folder
from .input_init.calibre_options           import calibre
from .input_init.common_options    import common_options
from .input_init.parse_input import parseInput
from .input_init.initialize_program import initialize_program


__all__ = [
    'parseInput',
    "start_calibre",
    "extract_text",
    "copy_new",
    "authors_from_authors",
    "authors_from_ebooks",
    "clean_filename",
    "library_to_text",
    "calibre",
    "common_options",
    "initialize_program",
]
__version__ = "1.0.0"
