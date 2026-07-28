# ebook_processor/__init__.py
"""
Ebook Processor Package
A package for processing EPUB files with author normalization and conflict management
"""

from .models import EbookMetadata
from .author_normalizer import AuthorNormalizer
from .conflict_manager import FileConflictManager
from .filename_cleaner import FilenameCleaner
from .ebook_processor import EbookProcessor

__version__ = "1.0.0"
__all__ = [
    'EbookMetadata',
    'AuthorNormalizer',
    'FileConflictManager',
    'FilenameCleaner',
    'EbookProcessor'
]
