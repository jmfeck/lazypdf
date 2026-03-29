from __future__ import annotations

from typing import TYPE_CHECKING

from lazypdf.utils import resolve_pages

if TYPE_CHECKING:
    from lazypdf.core import PDFFile


class SecurityMixin:
    """Mixin for PDF security operations: encrypt, decrypt, redact."""

    def encrypt(
        self: PDFFile,
        user_password: str,
        *,
        owner_password: str | None = None,
        permissions: int = 4095,
    ) -> PDFFile:
        """Add password protection to the PDF.

        Args:
            user_password: Password required to open the PDF.
            owner_password: Password for full access. Defaults to user_password.
            permissions: Permission flags bitmask. Default allows all except printing/copying restrictions.
        """
        import pymupdf

        if owner_password is None:
            owner_password = user_password
        self._encryption = {
            "user_pw": user_password,
            "owner_pw": owner_password,
            "perm": permissions,
            "encrypt": pymupdf.PDF_ENCRYPT_AES_256,
        }
        return self

    def decrypt(self: PDFFile, password: str) -> PDFFile:
        """Remove password protection from the PDF.

        Args:
            password: The password to unlock the PDF.
        """
        if self._doc.is_encrypted:
            if not self._doc.authenticate(password):
                raise ValueError("Incorrect password.")
        return self

    def redact(
        self: PDFFile,
        text: str,
        *,
        pages: list[int] | None = None,
        fill: tuple[float, float, float] = (0, 0, 0),
    ) -> PDFFile:
        """Permanently redact (black out) all occurrences of the given text.

        The redaction is applied immediately. Save with .to_pdf() to persist.

        Args:
            text: Text to search for and redact (case-sensitive, exact match).
            pages: Optional list of 1-indexed page numbers. If None, applies to all.
            fill: RGB fill color for the redaction rectangle (0-1 range).
        """
        target = resolve_pages(pages, len(self._doc))
        for i in target:
            page = self._doc[i]
            hits = page.search_for(text)
            for rect in hits:
                page.add_redact_annot(rect, fill=fill)
            page.apply_redactions()
        return self
