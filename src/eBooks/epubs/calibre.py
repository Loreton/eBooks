# /home/loreto/filu/Programming/gitREPO/eBooks/src/eBooks/epubs/calibre.py

from pyLnLib.calibre import CalibreMetadataReader
from pyLnLib import ctx, get_emoji
from pyLnLib.logger import get_logger


E=get_emoji()
logger=get_logger()

# ============================================================
# inizializza calibre con la libreria passata
# ============================================================
def initialize_calibre(library: str) -> CalibreMetadataReader:
    reader = CalibreMetadataReader(library)

    # ===== 1. Indici caricati all'avvio =====
    logger.info("📊 Libreria:")
    logger.info(f"\tTotale libri:      {reader.count:-5}")
    logger.info(f"\tTotale autori:     {len(reader.authors):-5}")
    logger.info(f"\tDuplicati trovati: {reader.duplicate_count:-5}")

    logger.info(f"""📊 Libreria:\n
                Totale libri:      {reader.count:-5}\n
                Totale autori:     {len(reader.authors):-5}\n
                Duplicati trovati: {reader.duplicate_count:-5}\n
                """)
    return reader
