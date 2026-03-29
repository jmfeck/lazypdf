from __future__ import annotations

from typing import TYPE_CHECKING

from lazypdf.utils import validate_pages

if TYPE_CHECKING:
    from lazypdf.core import PDFFile


class PagesMixin:
    """Mixin for page-level operations: split, extract, remove, reorder."""

    def extract_pages(self: PDFFile, pages: list[int]) -> PDFFile:
        """Keep only the specified pages (1-indexed). Returns self for chaining.

        Args:
            pages: List of 1-indexed page numbers to keep.
        """
        validate_pages(pages, len(self._doc))
        indices = sorted(set(p - 1 for p in pages))
        self._doc.select(indices)
        return self

    def remove_pages(self: PDFFile, pages: list[int]) -> PDFFile:
        """Remove the specified pages (1-indexed). Returns self for chaining.

        Args:
            pages: List of 1-indexed page numbers to remove.
        """
        validate_pages(pages, len(self._doc))
        to_remove = set(p - 1 for p in pages)
        keep = [i for i in range(len(self._doc)) if i not in to_remove]
        if not keep:
            raise ValueError("Cannot remove all pages from a PDF.")
        self._doc.select(keep)
        return self

    def reorder(self: PDFFile, order: list[int]) -> PDFFile:
        """Reorder pages according to the given sequence (1-indexed).

        Args:
            order: New page order as 1-indexed page numbers. Pages can be
                   repeated (to duplicate) or omitted (to remove).
        """
        validate_pages(order, len(self._doc))
        indices = [p - 1 for p in order]
        self._doc.select(indices)
        return self

    def reverse(self: PDFFile) -> PDFFile:
        """Reverse the page order."""
        indices = list(range(len(self._doc) - 1, -1, -1))
        self._doc.select(indices)
        return self

    def split(self: PDFFile, output_dir: str, *, every: int = 1) -> list[str]:
        """Split the PDF into multiple files. Terminal operation.

        Args:
            output_dir: Directory to write the split files into.
            every: Number of pages per output file. Defaults to 1 (one page per file).

        Returns:
            List of output file paths.
        """
        import os

        import pymupdf

        if every < 1:
            raise ValueError(f"'every' must be >= 1, got {every}.")

        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        paths: list[str] = []
        total = len(self._doc)

        for start in range(0, total, every):
            end = min(start + every, total)
            out_doc = pymupdf.open()
            out_doc.insert_pdf(self._doc, from_page=start, to_page=end - 1)
            out_path = os.path.join(output_dir, f"{base}_{start + 1}-{end}.pdf")
            out_doc.save(out_path)
            out_doc.close()
            paths.append(out_path)

        return paths

    def split_at(self: PDFFile, output_dir: str, *, at: list[int]) -> list[str]:
        """Split the PDF at specific page boundaries. Terminal operation.

        Args:
            output_dir: Directory to write the split files into.
            at: List of 1-indexed page numbers where splits occur.
                E.g. at=[3, 7] on a 10-page PDF yields: pages 1-2, 3-6, 7-10.

        Returns:
            List of output file paths.
        """
        import os

        import pymupdf

        total = len(self._doc)
        validate_pages(at, total)

        os.makedirs(output_dir, exist_ok=True)
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]

        boundaries = sorted(set([0] + [p - 1 for p in at] + [total]))
        paths: list[str] = []

        for i in range(len(boundaries) - 1):
            start, end = boundaries[i], boundaries[i + 1]
            out_doc = pymupdf.open()
            out_doc.insert_pdf(self._doc, from_page=start, to_page=end - 1)
            out_path = os.path.join(output_dir, f"{base}_{start + 1}-{end}.pdf")
            out_doc.save(out_path)
            out_doc.close()
            paths.append(out_path)

        return paths
