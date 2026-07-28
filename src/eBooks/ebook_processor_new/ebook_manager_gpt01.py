from curses import meta
from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import epub, ITEM_DOCUMENT


class EpubProcessor:
    """Simple EPUB reader."""

    def __init__(self, filename: str | Path):
        self._filename = Path(filename)

        if not self._filename.is_file():
            raise FileNotFoundError(self._filename)

        self._book = epub.read_epub(str(self._filename))

    def __str__(self) -> str:
        author = self.get_author() or "Unknown"
        title = self.get_title() or self.filename.name
        return f"{author} - {title}"


    # ==================================================================
    # Properties
    # ==================================================================

    @property
    def filename(self) -> Path:
        """Return EPUB filename."""
        return self._filename

    # ==================================================================
    # Public methods
    # ==================================================================

    def get_metadata(self) -> dict:
        """Return the raw metadata dictionary."""
        return self._book.metadata

    def get_text(self) -> str:
        """Return the plain text of the ebook."""

        parts = []

        for item in self._book.get_items():
            if item.get_type() != ITEM_DOCUMENT:
                continue

            soup = BeautifulSoup(
                item.get_body_content(),
                "html.parser"
            )

            text = soup.get_text(separator=" ", strip=True)

            if text:
                parts.append(text)

        return "\n\n".join(parts)

    def get_title(self) -> str | None:
        return self._get_dc("title")

    def get_author(self) -> str | None:
        return self._get_dc("creator")

    def get_language(self) -> str | None:
        return self._get_dc("language")

    def get_publisher(self) -> str | None:
        return self._get_dc("publisher")

    def get_date(self) -> str | None:
        return self._get_dc("date")

    def get_identifier(self) -> str | None:
        return self._get_dc("identifier")

    def get_description(self) -> str | None:
        return self._get_dc("description")

    def get_subject(self) -> str | None:
        return self._get_dc("subject")

    # ==================================================================
    # Private methods
    # ==================================================================

    def _get_dc(self, key: str) -> str | None:
        """Return a Dublin Core metadata value."""

        values = self._book.get_metadata("DC", key)

        if not values:
            return None

        return values[0][0]


book = EpubProcessor("/home/loreto/filu/ln-eBooks/new_books/single_test_book/Raine Miller - Nudo D'autore (2014).epub")

print(book.filename)
print(book.get_title())
print(book.get_author())
print(book.get_language())
print(book.get_identifier())

text = book.get_text()
metadata = book.get_metadata()
print(metadata)
print(text)
