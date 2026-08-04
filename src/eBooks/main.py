#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""

import sys
from pathlib import Path


# --- pyLnLib modules
# from eBooks.calibre.test01 import test01_main
# from pyLnLib.git.pyproject_class import PyProjectManager
# from pyLnLib.context   import ctx, lnContext
# from pyLnLib.files     import get_yaml_engine, scan_directory
# from pyLnLib.lndict    import lnDict
from pyLnLib.logger    import get_logger
from pyLnLib.epub      import EpubProcessor
# from pyLnLib.system import start_signal_handler
# from pyLnLib.calibre import test_calibre, CalibreMetadataReader


# --- project modules
from .core.initialize_program import initialize_program, foo_debug


sys.dont_write_bytecode = True
logger = get_logger()






def save_text_file(text: str, output_dir: Path, filename: str) -> None:
    file_path = output_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


def process_epub(epub_path: str|Path, export_dir: Path | None = None, index: str|None=None) -> None:
    book = EpubProcessor(epub_path)
    author = book.author
    # filename = book.filename
    index=f"{index} - "  if index is not None else ''

    logger.info("%sprocessing: %s/%s", index, book.author, book.filename.name)
    # justxtract
    if export_dir:
        if author:
            output_dir = Path(export_dir) / author
            saved_filename = book.export_text(filename=output_dir / f"{book.filename.stem}.txt", replace=False, unique=False)
            logger.debug("saved:      \"%s\"", saved_filename)
        return


    logger.info("filename:   %s", book.filename)
    logger.info("title:      %s", book.title)
    logger.info("author:     %s", book.author)
    logger.info("language:   %s", book.language)
    logger.info("identifier: %s", book.identifier)
    logger.info("sections:   %s", len(book.get_sections()))
    # Salva il report degli autori e dei conflitti
        # book._save_conflict_report(output_dir)



def main():
    ctx = initialize_program()
    foo_debug()
    args = ctx.args
    if args.extract:
        # breakpoint()
        for source_dir in ctx.config.dirs.source_top_dir:
            file_list = scan_directory(root_dir=source_dir, pattern='*.epub')
            nfiles=len(file_list)
            logger.info(file_list)
            for index, file in enumerate(file_list):
                if file.stem in ctx.config.files_to_skip:
                    logger.warning(f"Skipping {file.stem}")
                    continue
                process_epub(epub_path=file, export_dir=ctx.config.dirs.extract_dir, index=f"{index:04}/{nfiles:04}")


    '''
    #### - processor initializzation
    logger.info("🚀 Avvio processamento ebook...")
    processor = EbookProcessor(decode_type='lxml', normalize_text=True)
    # Directory di esempio
    root_dir = Path(ctx.config.dirs.top_dir)  # Cambia con la tua directory
    output_dir = Path(ctx.config.dirs.output_dir)  # Directory di output

    if not root_dir.exists():
        logger.error(f"Directory non trovata: {root_dir}")
        return

    # Processa tutti gli EPUB nella directory, organizzando per autore
    logger.info("🚀 Avvio processamento ebook...")

    _results = processor.process_directory(
        root_dir,
        output_dir,
        organize_by_author=True,
        skip_duplicates=True
    )

    # Mostra statistiche sugli autori
    author_stats = processor.get_author_statistics()
    print("\n" + "=" * 60)
    print("📚 STATISTICHE AUTORI")
    print("=" * 60)
    print(f"Autori unici trovati: {author_stats['total_unique_authors']}")

    if author_stats['authors']:
        print("\nAutori:")
        for author in author_stats['authors'][:10]:  # Mostra solo primi 10
            variants = author_stats['variants'][author]
            if len(variants) > 1:
                print(f"  - {author} (varianti: {len(variants)})")
            else:
                print(f"  - {author}")

        if len(author_stats['authors']) > 10:
            print(f"  ... e altri {len(author_stats['authors']) - 10} autori")

    # Mostra statistiche conflitti
    stats = processor.get_statistics()
    conflicts = stats['conflicts']

    print("\n" + "=" * 60)
    print("⚠️  STATISTICHE CONFLITTI")
    print("=" * 60)
    print(f"File salvati: {conflicts['total_files']}")
    if conflicts['total_conflicts'] > 0:
        print(f"Conflitti risolti: {conflicts['total_conflicts']}")
        print(f"Rapporto conflitti: {conflicts['conflict_ratio']:.2%}")
    else:
        print("Nessun conflitto rilevato ✅")

    # Cerca un testo specifico
    search_term = input("\n🔍 Inserisci testo da cercare (o premi Invio per saltare): ").strip()
    if search_term:
        search_results = processor.search_in_directory(root_dir, search_term)
        print(f"\n🔍 Trovate {len(search_results)} occorrenze di '{search_term}'")

        if search_results:
            print("\nPrime 5 occorrenze:")
            for i, result in enumerate(search_results[:5], 1):
                print(f"\n{i}. Libro: {result['title']}")
                print(f"   Autori: {', '.join(result['authors'])}")
                print(f"   Contesto: ...{result['context']}...")

    # Mostra statistiche complete
    print("\n" + "=" * 60)
    print("📊 STATISTICHE COMPLETE")
    print("=" * 60)
    print(f"File processati: {stats['files_processed']}")
    print(f"Timestamp: {stats['timestamp']}")

    if output_dir.exists():
        print(f"\n📁 Output salvato in: {output_dir.absolute()}")
        print(f"   - Report autori: {output_dir / '_AUTHORS_REPORT.txt'}")
        if conflicts['total_conflicts'] > 0:
            print(f"   - Report conflitti: {output_dir / '_CONFLICT_REPORT.txt'}")

    print("\n✅ Processamento completato!")

    '''

if __name__ == "__main__":
    main()
