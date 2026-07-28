#!/usr/bin/env python3
# ebook_processor/main.py
"""
Example usage of the EbookProcessor
"""

import sys
sys.dont_write_bytecode = True

from pathlib import Path


# from pyLnLib import init_logger
from pyLnLib.git.pyproject_class import PyProjectManager

# from pyLnLib.context   import ctx, get_project_vars
from pyLnLib.context_V2   import init_context
from pyLnLib.logger    import init_logger
from pyLnLib.files     import get_yaml_engine
from pyLnLib.lndict    import lnDict


from eBooks.ebook_processor import EbookProcessor




def initialize_program() -> lnDict:
    if 'debugpy' in sys.modules:
        import os
        print(os.environ.get("ZED_APP_PATH"))
        print(os.environ.get("ZED_ENVIRONMENT"))
        print(os.environ.get("ZED_TERM"))
        print(os.environ.get("TERM_PROGRAM"))

    pyproject = PyProjectManager(Path.cwd())
    appl_version = pyproject.get_version()
    # ctx.project_name = f"eBooks-{ctx.version}"
    ctx = init_context(name=f"eBooks-{appl_version}", tmp_dir=f"/tmp/ebooks-{appl_version}", version=appl_version)
    #### 2. read static project_list file
    yaml_engine=get_yaml_engine(search_paths=[ctx.config_dir], recursive=True)
    config_file = ctx.config_dir / "authors.yaml"
    config_data: lnDict = lnDict(yaml_engine.load(str(config_file)))

    # pv: lnDict=get_project_vars()
    ctx.config = config_data
    return ctx




def main():
    """Funzione main per testare la classe"""
    ctx = initialize_program()

    #### - logger initializzation
    logger = init_logger(logger_name=ctx.name, logging_dir=ctx.log_dir)

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


if __name__ == "__main__":
    main()
