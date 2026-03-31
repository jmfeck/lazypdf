from __future__ import annotations

from typing import TYPE_CHECKING

from lazypdf.utils import resolve_pages, validate_pages

if TYPE_CHECKING:
    from lazypdf.core import PDFFile


class TextMixin:
    """Mixin for text and table extraction."""

    def extract_text(
        self: PDFFile,
        *,
        pages: list[int] | None = None,
        sep: str = "\n",
        engine: str = "text",
        page_separator: str | None = None,
    ) -> str:
        """Extract all text from the PDF.

        Args:
            pages: Optional list of 1-indexed page numbers. If None, extracts from all.
            sep: Separator between pages (used when ``page_separator`` is ``None``).
            engine: Extraction engine. ``"text"`` = text layer only (default),
                ``"ocr"`` = force OCR on all pages, ``"auto"`` = try text first,
                fallback to OCR per page.
            page_separator: Separator inserted between pages. ``{n}`` is replaced
                with the 1-indexed page number. ``None`` uses *sep* instead.

        Returns:
            Extracted text as a single string.
        """
        valid_engines = {"text", "ocr", "auto"}
        if engine not in valid_engines:
            raise ValueError(f"Unknown engine '{engine}'. Options: {sorted(valid_engines)}")

        if engine in ("ocr", "auto"):
            try:
                import pytesseract  # noqa: F401
            except ImportError:
                raise ImportError(
                    f"engine='{engine}' requires pytesseract. Install with: pip install lazypdf[ocr]"
                ) from None

        target = resolve_pages(pages, len(self._doc))
        parts: list[str] = []

        for i in target:
            page = self._doc[i]

            if engine == "text":
                text = page.get_text()
            elif engine == "ocr":
                text = self._ocr_page(page)
            else:  # auto
                text = page.get_text()
                if not text.strip():
                    text = self._ocr_page(page)

            parts.append(text)

        if page_separator is not None:
            result_parts: list[str] = []
            for idx, (page_idx, text) in enumerate(zip(target, parts)):
                separator = page_separator.replace("{n}", str(page_idx + 1))
                result_parts.append(separator)
                result_parts.append(text)
            return "".join(result_parts)

        return sep.join(parts)

    @staticmethod
    def _ocr_page(page) -> str:
        """Run OCR on a single page and return the extracted text."""
        import pytesseract

        from io import BytesIO

        from PIL import Image

        pix = page.get_pixmap(dpi=300)
        img = Image.open(BytesIO(pix.tobytes("png")))
        return pytesseract.image_to_string(img)

    def extract_tables(
        self: PDFFile,
        *,
        pages: list[int] | None = None,
        flavor: str = "lattice",
    ) -> list[list[list[str]]]:
        """Extract tables from the PDF.

        Uses *camelot-py* when ``flavor`` is specified for fine-grained control,
        falling back to *pdfplumber* as the underlying engine.

        Args:
            pages: Optional list of 1-indexed page numbers. If None, extracts from all.
            flavor: Table detection strategy. ``"lattice"`` for tables with visible
                borders, ``"stream"`` for borderless tables.

        Returns:
            List of tables, where each table is a list of rows (list of cell strings).
        """
        valid_flavors = {"lattice", "stream"}
        if flavor not in valid_flavors:
            raise ValueError(f"Unknown flavor '{flavor}'. Options: {sorted(valid_flavors)}")

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

        table_settings = {}
        if flavor == "stream":
            table_settings = {
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
            }

        tables = []
        with pdfplumber.open(BytesIO(data)) as plumber:
            target_pages = pages or list(range(1, len(plumber.pages) + 1))
            for pnum in target_pages:
                page = plumber.pages[pnum - 1]
                for table in page.extract_tables(table_settings=table_settings):
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
