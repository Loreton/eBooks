from pathlib import Path
from typing import Any
import bs4
import ebooklib
from ebooklib import epub


class EpubProcessor:

    def __init__(self, file_path: str | Path) -> None:
        """Inizializza il processore verificando l'esistenza del file EPUB."""
        self.file_path = Path(file_path)

        if not self.file_path.is_file():
            raise FileNotFoundError(
                f"Il file specificato non esiste: {self.file_path}"
            )

        if self.file_path.suffix.lower() != ".epub":
            raise ValueError(
                f"Il file deve avere estensione .epub: {self.file_path}"
            )

        # Carichiamo il libro
        self.book = epub.read_epub(
            str(self.file_path), options={"ignore_ncx": True}
        )

    def extract_metadata(self) -> dict[str, list[tuple[str, dict[str, Any]]]]:
        """Estrae tutti i metadati presenti nel file EPUB.

        Restituisce un dizionario formattato dove ogni chiave corrisponde al
        namespace/nome del metadato (es. 'DC/title', 'DC/creator').
        """
        return self.book.metadata

    def get_title(self) -> str:
        """Restituisce il titolo del libro o una stringa vuota se non trovato."""
        titles = self.book.get_metadata("DC", "title")
        if titles:
            # titles è una lista di tuple: (valore, dizionario_attributi)
            return titles[0][0]
        return ""

    def get_author(self) -> str:
        """Restituisce l'autore (creator) principale o una stringa vuota."""
        authors = self.book.get_metadata("DC", "creator")
        if authors:
            return authors[0][0]
        return ""

    def extract_text(self, separator: str = "\n\n") -> str:
        """Estrae l'intero testo visibile del libro unendo i vari capitoli HTML.

        :param separator: Stringa usata per separare i vari capitoli del testo.
        """
        text_parts: list[str] = []

        # Sccorriamo solo gli elementi di tipo testo (HTML/XHTML)
        for item in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content()
            if not content:
                continue

            # Usiamo BeautifulSoup per rimuovere i tag HTML e recuperare il testo pulito
            soup = bs4.BeautifulSoup(content, "html.parser")

            # get_text con strip=True rimuove gli spazi vuoti superflui
            cleaned_text = soup.get_text(separator=" ", strip=True)

            if cleaned_text:
                text_parts.append(cleaned_text)

        return separator.join(text_parts)



if __name__ == "__main__":
    epub_file = Path("/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub")

    try:
        processor = EpubProcessor(epub_file)

        print(f"Titolo: {processor.get_title()}")
        print(f"Autore: {processor.get_author()}")

        # Estrazione metadati grezzi
        metadata = processor.extract_metadata()
        breakpoint()

        # Estrazione del testo completo
        text = processor.extract_text()
        print(f"\nLunghezza testo estratto: {len(text)} caratteri")
        print("\nAnteprima primi 300 caratteri:")
        print(text[:300])

    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")
