# ebook_processor/models.py
"""
Data models for the ebook processor
"""

from dataclasses import dataclass, field


@dataclass
class EbookMetadata:
    """Data class per i metadati dell'ebook"""
    title: str = "Sconosciuto"
    authors: list[str] = field(default_factory=lambda: ["Sconosciuto"])
    language: str = "Sconosciuto"
    publisher: str = "Sconosciuto"
    publication_date: str = "Sconosciuto"

    def to_dict(self) -> dict[str, any]:
        """Converte i metadati in un dizionario"""
        return {
            'title': self.title,
            'authors': self.authors,
            'language': self.language,
            'publisher': self.publisher,
            'publication_date': self.publication_date
        }

    @classmethod
    def from_dict(cls, data: dict[str, any]) -> EbookMetadata:  # type: ignore
        """Crea un oggetto EbookMetadata da un dizionario"""
        return cls(
            title=data.get('title', 'Sconosciuto'),
            authors=data.get('authors', ['Sconosciuto']),
            language=data.get('language', 'Sconosciuto'),
            publisher=data.get('publisher', 'Sconosciuto'),
            publication_date=data.get('publication_date', 'Sconosciuto')
        )
