from __future__ import annotations

import pymupdf

from lazypdf._converters import ConvertersMixin
from lazypdf._operations import OperationsMixin
from lazypdf._pages import PagesMixin
from lazypdf._security import SecurityMixin
from lazypdf._text import TextMixin


class PDFFile(PagesMixin, OperationsMixin, SecurityMixin, TextMixin, ConvertersMixin):
    """A pandas-like wrapper around a PDF document.

    Supports method chaining for transformations and terminal export methods.

    Example::

        import lazypdf as lz

        lz.read("input.pdf").rotate(90).compress().to_pdf("output.pdf")
    """

    def __init__(self, doc: pymupdf.Document, path: str | None = None) -> None:
        self._doc = doc
        self.path = path
        self._save_opts: dict = {}
        self._encryption: dict = {}

    def __repr__(self) -> str:
        pages = len(self._doc)
        name = self.path or "<memory>"
        return f"<PDFFile '{name}' ({pages} pages)>"

    def __len__(self) -> int:
        return len(self._doc)

    def __enter__(self) -> PDFFile:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying PDF document and release resources."""
        doc = getattr(self, "_doc", None)
        if doc is not None and not doc.is_closed:
            doc.close()

    def copy(self) -> PDFFile:
        """Create an independent copy of this PDFFile."""
        data = self._doc.tobytes()
        new_doc = pymupdf.open("pdf", data)
        return PDFFile(new_doc, path=self.path)
