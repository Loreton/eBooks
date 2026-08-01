#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""

import sys
from pathlib import Path


# --- pyLnLib modules
from pyLnLib.git.pyproject_class import PyProjectManager
from pyLnLib.context   import ctx, lnContext
from pyLnLib.files     import get_yaml_engine, scan_directory
from pyLnLib.lndict    import lnDict
from pyLnLib.logger    import get_logger

# --- project modules
from eBooks.ebook_processor import EbookProcessor
from eBooks.core import parseInput

sys.dont_write_bytecode = True
logger = get_logger()

def check_zed() -> None:
    if 'debugpy' in sys.modules:
        import os
        print(os.environ.get("ZED_APP_PATH"))
        print(os.environ.get("ZED_ENVIRONMENT"))
        print(os.environ.get("ZED_TERM"))
        print(os.environ.get("TERM_PROGRAM"))



def initialize_program() -> lnContext:
    # 1. initialize context
    pyproject = PyProjectManager(Path.cwd())
    appl_version = pyproject.get_version()
    ctx.initialize(project_name="eBooks", project_temp_dir=f"/tmp/ebooks-{appl_version}", version=appl_version)


    #### 3. read  project configuration file
    config_file = ctx.project_config_dir / "authors.yaml"
    yaml_engine=get_yaml_engine(search_paths=[ctx.project_config_dir], recursive=True)
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))

    #### 4. insert configuration data into context
    ctx.config.update(config_data)
    return ctx



def main():
    initialize_program()
    args=parseInput()
    #### 2. logger initializzation
    logger.initialize(name="eBooks", logging_dir=ctx.project_log_dir, console_logger_level=args.console_log_level)


    breakpoint()
    if args.extract:
        file_list = scan_directory(root_dir="/home/loreto/filu/ln-eBooks/new_books", pattern='*.epub')
        logger.info(file_list)
        # for file in file_list:
        #     export_dir = Path(file).parent / "export"
            # test_01(epub_path=file, export_dir=export_dir)


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
