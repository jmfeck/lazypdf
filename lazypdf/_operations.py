from __future__ import annotations

from typing import TYPE_CHECKING

from lazypdf.utils import resolve_pages

if TYPE_CHECKING:
    from lazypdf.core import PDFFile


class OperationsMixin:
    """Mixin for PDF transformation operations."""

    def merge(self: PDFFile, *others: str | PDFFile | list[str | PDFFile]) -> PDFFile:
        """Append one or more PDFs to this document.

        Args:
            others: File paths, PDFFile instances, or lists of either.
        """
        import pymupdf

        flat: list[str | PDFFile] = []
        for item in others:
            if isinstance(item, list):
                flat.extend(item)
            else:
                flat.append(item)

        for other in flat:
            if isinstance(other, str):
                other_doc = pymupdf.open(other)
                self._doc.insert_pdf(other_doc)
                other_doc.close()
            else:
                self._doc.insert_pdf(other._doc)
        return self

    def rotate(self: PDFFile, degrees: int, *, pages: list[int] | None = None) -> PDFFile:
        """Rotate pages by the given angle.

        Args:
            degrees: Rotation angle (must be a multiple of 90).
            pages: Optional list of 1-indexed page numbers. If None, rotates all pages.
        """
        if degrees % 90 != 0:
            raise ValueError("Rotation must be a multiple of 90 degrees.")
        target = resolve_pages(pages, len(self._doc))
        for i in target:
            self._doc[i].set_rotation((self._doc[i].rotation + degrees) % 360)
        return self

    def crop(
        self: PDFFile,
        left: float = 0,
        top: float = 0,
        right: float = 0,
        bottom: float = 0,
        *,
        pages: list[int] | None = None,
    ) -> PDFFile:
        """Crop pages by adjusting margins (in points, 72 pts = 1 inch).

        Args:
            left: Points to trim from the left. Must be >= 0.
            top: Points to trim from the top. Must be >= 0.
            right: Points to trim from the right. Must be >= 0.
            bottom: Points to trim from the bottom. Must be >= 0.
            pages: Optional list of 1-indexed page numbers. If None, crops all pages.
        """
        import pymupdf

        for val, name in [(left, "left"), (top, "top"), (right, "right"), (bottom, "bottom")]:
            if val < 0:
                raise ValueError(f"'{name}' must be >= 0, got {val}.")

        target = resolve_pages(pages, len(self._doc))
        for i in target:
            page = self._doc[i]
            rect = page.rect
            new_rect = pymupdf.Rect(rect.x0 + left, rect.y0 + top, rect.x1 - right, rect.y1 - bottom)
            if new_rect.is_empty:
                raise ValueError(f"Crop values exceed page dimensions on page {i + 1}.")
            page.set_cropbox(new_rect)
        return self

    def compress(
        self: PDFFile,
        *,
        img_quality: int | None = None,
        compression_level: int = 5,
    ) -> PDFFile:
        """Compress the PDF to reduce file size.

        Applies deflate compression to streams, images and fonts, and removes
        unused/duplicate objects.

        Args:
            img_quality: Quality level for image recompression (1-100).
                ``None`` skips image recompression.
            compression_level: Deflate compression level for content streams (1-9).
        """
        import pymupdf

        if img_quality is not None and not (1 <= img_quality <= 100):
            raise ValueError(f"img_quality must be between 1 and 100, got {img_quality}.")
        if not (1 <= compression_level <= 9):
            raise ValueError(f"compression_level must be between 1 and 9, got {compression_level}.")

        self._save_opts["deflate"] = True
        self._save_opts["deflate_images"] = True
        self._save_opts["deflate_fonts"] = True
        self._save_opts["garbage"] = 4
        self._save_opts["clean"] = True

        if img_quality is not None:
            # Recompress images at the given quality by re-saving through pymupdf
            for page_idx in range(len(self._doc)):
                page = self._doc[page_idx]
                images = page.get_images(full=True)
                for img_info in images:
                    xref = img_info[0]
                    try:
                        pix = pymupdf.Pixmap(self._doc, xref)
                    except Exception:
                        continue
                    if pix.n > 4:
                        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
                    img_bytes = pix.tobytes("jpeg", jpg_quality=img_quality)
                    self._doc.update_stream(xref, img_bytes)

        return self

    def add_watermark(
        self: PDFFile,
        text: str,
        *,
        fontsize: float = 60,
        color: tuple[float, float, float] = (0.75, 0.75, 0.75),
        opacity: float = 0.3,
        angle: float = -45,
        pages: list[int] | None = None,
    ) -> PDFFile:
        """Add a text watermark to pages.

        Args:
            text: Watermark text.
            fontsize: Font size in points.
            color: RGB color tuple (0-1 range).
            opacity: Opacity from 0 (invisible) to 1 (opaque).
            angle: Rotation angle in degrees.
            pages: Optional list of 1-indexed page numbers. If None, applies to all pages.
        """
        import pymupdf

        if not text:
            raise ValueError("Watermark text cannot be empty.")

        target = resolve_pages(pages, len(self._doc))
        for i in target:
            page = self._doc[i]
            rect = page.rect
            cx, cy = rect.width / 2, rect.height / 2
            tw = pymupdf.TextWriter(page.rect, opacity=opacity, color=color)
            font = pymupdf.Font("helv")
            text_width = font.text_length(text, fontsize=fontsize)
            tw.append(pymupdf.Point(cx - text_width / 2, cy), text, font=font, fontsize=fontsize)
            tw.write_text(page, morph=(pymupdf.Point(cx, cy), pymupdf.Matrix(angle)))
        return self

    def add_image_watermark(
        self: PDFFile,
        image_path: str,
        *,
        opacity: float = 0.5,
        overlay: bool = False,
        pages: list[int] | None = None,
    ) -> PDFFile:
        """Add an image watermark to pages.

        Args:
            image_path: Path to the watermark image (PNG, JPG, etc.).
            opacity: Opacity from 0 (invisible) to 1 (opaque).
            overlay: If True, place on top of content. If False, behind content (background).
            pages: Optional list of 1-indexed page numbers. If None, applies to all pages.
        """
        import tempfile

        from PIL import Image

        img = Image.open(image_path).convert("RGBA")
        alpha = img.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        img.putalpha(alpha)

        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp_path = tmp.name
        img.save(tmp_path, "PNG")
        tmp.close()

        try:
            target = resolve_pages(pages, len(self._doc))
            for i in target:
                page = self._doc[i]
                page.insert_image(
                    page.rect,
                    filename=tmp_path,
                    overlay=overlay,
                    keep_proportion=True,
                )
        finally:
            import os

            os.unlink(tmp_path)

        return self

    def add_page_numbers(
        self: PDFFile,
        *,
        position: str = "bottom-center",
        fontsize: float = 12,
        margin: float = 36,
        fmt: str = "{n}",
        start: int = 1,
        pages: list[int] | None = None,
    ) -> PDFFile:
        """Add page numbers to the PDF.

        Args:
            position: One of 'bottom-left', 'bottom-center', 'bottom-right',
                      'top-left', 'top-center', 'top-right'.
            fontsize: Font size in points.
            margin: Distance from page edge in points.
            fmt: Format string. {n} = page number, {total} = total pages.
            start: Starting page number.
            pages: Optional list of 1-indexed page numbers. If None, applies to all.
        """
        import pymupdf

        valid_positions = {"bottom-left", "bottom-center", "bottom-right", "top-left", "top-center", "top-right"}
        if position not in valid_positions:
            raise ValueError(f"Invalid position '{position}'. Must be one of: {sorted(valid_positions)}")

        total = len(self._doc)
        target = resolve_pages(pages, total)

        for idx in target:
            page = self._doc[idx]
            rect = page.rect
            num_text = fmt.format(n=idx + start, total=total)

            if "top" in position:
                y = margin
            else:
                y = rect.height - margin

            if "left" in position:
                x = margin
                align = 0
            elif "right" in position:
                x = rect.width - margin
                align = 2
            else:
                x = rect.width / 2
                align = 1

            font = pymupdf.Font("helv")
            tw = font.text_length(num_text, fontsize=fontsize)

            if align == 1:
                x -= tw / 2
            elif align == 2:
                x -= tw

            page.insert_text(pymupdf.Point(x, y), num_text, fontsize=fontsize, fontname="helv")
        return self

    def resize(
        self: PDFFile,
        size: str = "a4",
        *,
        pages: list[int] | None = None,
    ) -> PDFFile:
        """Resize pages to a standard paper size, preserving content aspect ratio.

        Args:
            size: Target size name ('a4', 'a3', 'letter', 'legal').
            pages: Optional list of 1-indexed page numbers. If None, resizes all.
        """
        import pymupdf

        sizes = {
            "a4": pymupdf.paper_rect("a4"),
            "a3": pymupdf.paper_rect("a3"),
            "letter": pymupdf.paper_rect("letter"),
            "legal": pymupdf.paper_rect("legal"),
        }
        target_rect = sizes.get(size.lower())
        if target_rect is None:
            raise ValueError(f"Unknown size '{size}'. Supported: {sorted(sizes.keys())}")

        target_indices = resolve_pages(pages, len(self._doc))

        new_doc = pymupdf.open()
        for i in range(len(self._doc)):
            if i in target_indices or (pages is None):
                src_page = self._doc[i]
                src_rect = src_page.rect
                new_page = new_doc.new_page(width=target_rect.width, height=target_rect.height)

                scale_x = target_rect.width / src_rect.width
                scale_y = target_rect.height / src_rect.height
                scale = min(scale_x, scale_y)
                new_w = src_rect.width * scale
                new_h = src_rect.height * scale
                x_off = (target_rect.width - new_w) / 2
                y_off = (target_rect.height - new_h) / 2
                dest_rect = pymupdf.Rect(x_off, y_off, x_off + new_w, y_off + new_h)

                new_page.show_pdf_page(dest_rect, self._doc, i)
            else:
                new_doc.insert_pdf(self._doc, from_page=i, to_page=i)

        self._doc.close()
        self._doc = new_doc
        return self

    def flatten(self: PDFFile, *, dpi: int = 72, pages: list[int] | None = None) -> PDFFile:
        """Flatten pages by rasterizing them to images.

        Burns all annotations, form fields, and layers into a flat image per page.

        Args:
            dpi: Resolution for rasterization. Higher = better quality but larger file.
            pages: Optional list of 1-indexed page numbers. If None, flattens all.
        """
        import pymupdf

        target_set = set(resolve_pages(pages, len(self._doc)))

        new_doc = pymupdf.open()
        for i in range(len(self._doc)):
            if i in target_set:
                page = self._doc[i]
                pix = page.get_pixmap(dpi=dpi)
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                new_page.insert_image(new_page.rect, pixmap=pix)
            else:
                new_doc.insert_pdf(self._doc, from_page=i, to_page=i)

        self._doc.close()
        self._doc = new_doc
        return self

    def repair(self: PDFFile, *, engine: str = "auto") -> PDFFile:
        """Attempt to repair a corrupted PDF.

        Args:
            engine: Repair engine. ``"pymupdf"`` (built-in), ``"pikepdf"``
                (strong at object stream corruption), or ``"auto"`` (tries
                each engine in order, returns first success).
        """
        valid_engines = {"pymupdf", "pikepdf", "auto"}
        if engine not in valid_engines:
            raise ValueError(f"Unknown engine '{engine}'. Options: {sorted(valid_engines)}")

        if engine == "pymupdf":
            return self._repair_pymupdf()
        elif engine == "pikepdf":
            return self._repair_pikepdf()
        else:  # auto
            try:
                return self._repair_pymupdf()
            except Exception:
                pass
            try:
                return self._repair_pikepdf()
            except ImportError:
                raise
            except Exception:
                raise

    def _repair_pymupdf(self: PDFFile) -> PDFFile:
        """Repair using PyMuPDF (re-save with garbage collection)."""
        import pymupdf

        data = self._doc.tobytes(garbage=4, deflate=True, clean=True)
        self._doc.close()
        self._doc = pymupdf.open("pdf", data)
        return self

    def _repair_pikepdf(self: PDFFile) -> PDFFile:
        """Repair using pikepdf."""
        try:
            import pikepdf
        except ImportError:
            raise ImportError(
                "engine='pikepdf' requires pikepdf. Install with: pip install lazypdf[repair]"
            ) from None

        import pymupdf
        from io import BytesIO

        raw = self._doc.tobytes()
        buf = BytesIO()
        with pikepdf.open(BytesIO(raw)) as pdf:
            pdf.save(buf, linearize=True)

        self._doc.close()
        self._doc = pymupdf.open("pdf", buf.getvalue())
        return self

    def ocr(self: PDFFile, *, language: str = "eng", pages: list[int] | None = None) -> PDFFile:
        """Apply OCR to make scanned pages searchable (requires Tesseract installed).

        Args:
            language: Tesseract language code (e.g. 'eng', 'por', 'deu').
            pages: Optional list of 1-indexed page numbers. If None, applies to all.
        """
        try:
            import pytesseract
        except ImportError:
            raise ImportError("OCR requires pytesseract. Install with: pip install lazypdf[ocr]") from None

        import pymupdf

        target = resolve_pages(pages, len(self._doc))

        for i in target:
            page = self._doc[i]
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")

            from io import BytesIO

            from PIL import Image

            img = Image.open(BytesIO(img_data))
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=language, extension="pdf")

            ocr_doc = pymupdf.open("pdf", pdf_bytes)
            if len(ocr_doc) > 0:
                ocr_page = ocr_doc[0]
                text_dict = ocr_page.get_text("dict")
                for block in text_dict.get("blocks", []):
                    if block.get("type") == 0:
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                page.insert_text(
                                    pymupdf.Point(span["origin"][0], span["origin"][1]),
                                    span["text"],
                                    fontsize=span["size"],
                                    render_mode=3,
                                )
            ocr_doc.close()

        return self
