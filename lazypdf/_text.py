from __future__ import annotations

from typing import TYPE_CHECKING

from lazypdf.utils import resolve_pages, validate_pages

if TYPE_CHECKING:
    from lazypdf.core import PDFFile


class TextMixin:
    """Mixin for text and table extraction."""

    def extract_text(self: PDFFile, *, pages: list[int] | None = None, sep: str = "\n") -> str:
        """Extract all text from the PDF.

        Args:
            pages: Optional list of 1-indexed page numbers. If None, extracts from all.
            sep: Separator between pages.

        Returns:
            Extracted text as a single string.
        """
        target = resolve_pages(pages, len(self._doc))
        parts = [self._doc[i].get_text() for i in target]
        return sep.join(parts)

    def extract_tables(self: PDFFile, *, pages: list[int] | None = None) -> list[list[list[str]]]:
        """Extract tables from the PDF using pdfplumber.

        Args:
            pages: Optional list of 1-indexed page numbers. If None, extracts from all.

        Returns:
            List of tables, where each table is a list of rows (list of cell strings).
        """
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "Table extraction requires pdfplumber. Install with: pip install lazypdf[tables]"
            ) from None

        if pages is not None:
            validate_pages(pages, len(self._doc))

        data = self._doc.tobytes()
        from io import BytesIO

        tables = []
        with pdfplumber.open(BytesIO(data)) as plumber:
            target_pages = pages or list(range(1, len(plumber.pages) + 1))
            for pnum in target_pages:
                page = plumber.pages[pnum - 1]
                for table in page.extract_tables():
                    tables.append(table)
        return tables

    @property
    def metadata(self: PDFFile) -> dict:
        """Return the PDF metadata dictionary."""
        return dict(self._doc.metadata)

    @property
    def page_count(self: PDFFile) -> int:
        """Return the number of pages."""
        return len(self._doc)

    def page_sizes(self: PDFFile) -> list[tuple[float, float]]:
        """Return a list of (width, height) tuples for each page in points."""
        return [(self._doc[i].rect.width, self._doc[i].rect.height) for i in range(len(self._doc))]

    def extract_images(
        self: PDFFile,
        output_dir: str,
        *,
        pages: list[int] | None = None,
    ) -> list[str]:
        """Extract all embedded images from the PDF and save them to disk.

        Args:
            output_dir: Directory to write the extracted images.
            pages: Optional list of 1-indexed page numbers. If None, extracts from all.

        Returns:
            List of output file paths.
        """
        import os

        import pymupdf

        os.makedirs(output_dir, exist_ok=True)
        target = resolve_pages(pages, len(self._doc))
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        paths: list[str] = []
        seen_xrefs: set[int] = set()

        for i in target:
            page = self._doc[i]
            images = page.get_images(full=True)
            for img_idx, img_info in enumerate(images):
                xref = img_info[0]
                if xref in seen_xrefs:
                    continue
                seen_xrefs.add(xref)

                try:
                    pix = pymupdf.Pixmap(self._doc, xref)
                except Exception:
                    continue

                if pix.n > 4:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

                ext = "png" if pix.alpha else "jpg"
                out_path = os.path.join(output_dir, f"{base}_p{i + 1}_img{img_idx + 1}.{ext}")
                pix.save(out_path)
                paths.append(out_path)

        return paths
