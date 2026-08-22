"""
Ebook Processor Package
A package for processing EPUB files with author normalization and conflict management
"""

if False:
    from .ebook_processor.models import EbookMetadata
    from .ebook_processor.author_normalizer import AuthorNormalizer
    from .ebook_processor.conflict_manager import FileConflictManager
    from .ebook_processor.filename_cleaner import FilenameCleaner
    from .ebook_processor import EbookProcessor

    __all__ = [
        'EbookMetadata',
        'AuthorNormalizer',
        'FileConflictManager',
        'FilenameCleaner',
    ]

else:
    # from .ebook_processor_new.ln_ebook_manager_v02 import EpubProcessor
    # from .ebook_processor_new.ebook_manager_deepseek01 import EpubProcessor
    # from .ebook_processor_new.ebook_manager_gemini01 import EpubProcessor
    # from .ebook_processor_new.ebook_manager_gpt01 import EpubProcessor
    # from .input.parse_input import parseInput
    from .input import parseInput
    # from .core.ln_ebook_manager import EpubProcessor

    __all__ = [
        # 'EpubProcessor',
        'parseInput',
    ]
__version__ = "1.0.0"
