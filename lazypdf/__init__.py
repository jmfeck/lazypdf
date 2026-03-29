"""lazypdf - A pandas-like wrapper for PDF operations.

Read a PDF, transform it, export to another format. That's it.

    import lazypdf as lz

    lz.read("input.pdf").rotate(90).compress().to_pdf("output.pdf")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lazypdf.core import PDFFile

__version__ = "0.1.0"

__all__ = [
    "read",
    "read_pdf",
    "read_images",
    "read_jpg",
    "read_png",
    "read_html",
    "read_docx",
    "read_xlsx",
    "read_pptx",
    "read_csv",
    "merge",
    "from_bytes",
]

# Lazy imports to keep `import lazypdf` fast.
# The heavy dependencies (pymupdf, etc.) are only loaded when needed.


def read(path: str) -> PDFFile:
    """Read a PDF file and return a PDFFile for chaining operations.

    Args:
        path: Path to the PDF file.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    doc = pymupdf.open(path)
    return PDFFile(doc, path=path)


def read_pdf(path: str) -> PDFFile:
    """Alias for read()."""
    return read(path)


def read_images(*paths: str, page_size: str = "a4") -> PDFFile:
    """Create a PDF from one or more image files.

    Args:
        paths: One or more paths to image files (jpg, png, etc.).
        page_size: Page size name ('a4', 'letter', etc.) or 'fit' to match image size.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    doc = pymupdf.open()

    page_sizes = {
        "a4": pymupdf.paper_rect("a4"),
        "a3": pymupdf.paper_rect("a3"),
        "letter": pymupdf.paper_rect("letter"),
        "legal": pymupdf.paper_rect("legal"),
    }

    for img_path in paths:
        img_doc = pymupdf.open(img_path)
        try:
            img_rect = img_doc[0].rect

            if page_size == "fit":
                rect = img_rect
            else:
                rect = page_sizes.get(page_size.lower(), pymupdf.paper_rect("a4"))

            page = doc.new_page(width=rect.width, height=rect.height)

            # Scale image to fit page while preserving aspect ratio
            scale_x = rect.width / img_rect.width
            scale_y = rect.height / img_rect.height
            scale = min(scale_x, scale_y)
            new_w = img_rect.width * scale
            new_h = img_rect.height * scale
            x_offset = (rect.width - new_w) / 2
            y_offset = (rect.height - new_h) / 2
            target_rect = pymupdf.Rect(x_offset, y_offset, x_offset + new_w, y_offset + new_h)

            page.insert_image(target_rect, filename=img_path)
        finally:
            img_doc.close()

    return PDFFile(doc)


def read_jpg(*paths: str, page_size: str = "a4") -> PDFFile:
    """Create a PDF from JPEG images. Alias for read_images()."""
    return read_images(*paths, page_size=page_size)


def read_png(*paths: str, page_size: str = "a4") -> PDFFile:
    """Create a PDF from PNG images. Alias for read_images()."""
    return read_images(*paths, page_size=page_size)


def read_html(path_or_url: str) -> PDFFile:
    """Create a PDF from an HTML file or URL.

    Requires WeasyPrint: pip install weasyprint

    Args:
        path_or_url: Path to an HTML file or a URL.

    Returns:
        A PDFFile instance.
    """
    try:
        from weasyprint import HTML
    except ImportError:
        raise ImportError("HTML to PDF requires WeasyPrint. Install with: pip install weasyprint") from None

    import pymupdf

    from lazypdf.core import PDFFile

    if path_or_url.startswith(("http://", "https://")):
        pdf_bytes = HTML(url=path_or_url).write_pdf()
    else:
        pdf_bytes = HTML(filename=path_or_url).write_pdf()
    doc = pymupdf.open("pdf", pdf_bytes)
    return PDFFile(doc)


def _msoffice_to_pdf(path: str, app: str) -> bytes:
    """Convert a file to PDF using Microsoft Office via COM automation (Windows only)."""
    import os
    import tempfile

    try:
        import pythoncom
        import win32com.client
    except ImportError:
        raise ImportError("pywin32 is required for MS Office conversion. Install with: pip install pywin32") from None

    abs_path = os.path.abspath(path)
    tmp_dir = tempfile.mkdtemp()
    base = os.path.splitext(os.path.basename(path))[0]
    pdf_path = os.path.join(tmp_dir, f"{base}.pdf")

    pythoncom.CoInitialize()
    office = None
    try:
        if app == "word":
            office = win32com.client.DispatchEx("Word.Application")
            office.Visible = False
            doc = office.Documents.Open(abs_path)
            doc.SaveAs(pdf_path, FileFormat=17)  # 17 = wdFormatPDF
            doc.Close()
        elif app == "excel":
            office = win32com.client.DispatchEx("Excel.Application")
            office.Visible = False
            office.DisplayAlerts = False
            wb = office.Workbooks.Open(abs_path)
            wb.ExportAsFixedFormat(0, pdf_path)  # 0 = xlTypePDF
            wb.Close(False)
        elif app == "powerpoint":
            office = win32com.client.DispatchEx("PowerPoint.Application")
            prs = office.Presentations.Open(abs_path, WithWindow=False)
            prs.SaveAs(pdf_path, FileFormat=32)  # 32 = ppSaveAsPDF
            prs.Close()
        else:
            raise ValueError(f"Unknown Office app: {app}")

        with open(pdf_path, "rb") as f:
            return f.read()
    finally:
        if office is not None:
            try:
                office.Quit()
            except Exception:
                pass
            del office
        import gc

        gc.collect()
        pythoncom.CoUninitialize()

        import shutil

        shutil.rmtree(tmp_dir, ignore_errors=True)


def _libreoffice_to_pdf(path: str) -> bytes:
    """Convert a file to PDF using LibreOffice in headless mode."""
    import shutil
    import subprocess
    import tempfile

    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise RuntimeError(
            "LibreOffice not found. Install it from https://www.libreoffice.org/ "
            "and make sure 'soffice' is on your PATH."
        )

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir", tmp, path],
            check=True,
            capture_output=True,
        )
        import os

        base = os.path.splitext(os.path.basename(path))[0]
        pdf_path = os.path.join(tmp, f"{base}.pdf")
        with open(pdf_path, "rb") as f:
            return f.read()


_OFFICE_APP_MAP = {
    ".doc": "word",
    ".docx": "word",
    ".odt": "word",
    ".rtf": "word",
    ".xls": "excel",
    ".xlsx": "excel",
    ".ods": "excel",
    ".csv": "excel",
    ".ppt": "powerpoint",
    ".pptx": "powerpoint",
    ".odp": "powerpoint",
}


def _office_to_pdf(path: str) -> bytes:
    """Convert an Office file to PDF. Tries MS Office first, then LibreOffice."""
    import os
    import sys

    ext = os.path.splitext(path)[1].lower()
    app = _OFFICE_APP_MAP.get(ext)
    if app is None:
        supported = sorted(_OFFICE_APP_MAP.keys())
        raise ValueError(f"Unsupported file extension: '{ext}'. Supported: {supported}")

    # Try MS Office (Windows only)
    if sys.platform == "win32":
        try:
            return _msoffice_to_pdf(path, app)
        except ImportError:
            # pywin32 not installed, fall through to LibreOffice
            pass

    # Fallback to LibreOffice
    import shutil

    if shutil.which("soffice") or shutil.which("libreoffice"):
        return _libreoffice_to_pdf(path)

    raise RuntimeError(
        "No Office suite found. Install one of:\n"
        "  - Microsoft Office (Windows, detected automatically via pywin32)\n"
        "  - LibreOffice (any OS, https://www.libreoffice.org/)\n"
        "and make sure it's available on your PATH."
    )


def read_docx(path: str) -> PDFFile:
    """Read a Word document (.docx/.doc) and convert it to a PDFFile.

    Requires Microsoft Office (Windows) or LibreOffice.

    Args:
        path: Path to the Word document.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    pdf_bytes = _office_to_pdf(path)
    doc = pymupdf.open("pdf", pdf_bytes)
    return PDFFile(doc, path=path)


def read_xlsx(path: str) -> PDFFile:
    """Read an Excel spreadsheet (.xlsx/.xls) and convert it to a PDFFile.

    Requires Microsoft Office (Windows) or LibreOffice.

    Args:
        path: Path to the Excel file.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    pdf_bytes = _office_to_pdf(path)
    doc = pymupdf.open("pdf", pdf_bytes)
    return PDFFile(doc, path=path)


def read_pptx(path: str) -> PDFFile:
    """Read a PowerPoint presentation (.pptx/.ppt) and convert it to a PDFFile.

    Requires Microsoft Office (Windows) or LibreOffice.

    Args:
        path: Path to the PowerPoint file.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    pdf_bytes = _office_to_pdf(path)
    doc = pymupdf.open("pdf", pdf_bytes)
    return PDFFile(doc, path=path)


def read_csv(path: str) -> PDFFile:
    """Read a CSV file and convert it to a PDFFile.

    Requires Microsoft Office (Windows) or LibreOffice.

    Args:
        path: Path to the CSV file.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    pdf_bytes = _office_to_pdf(path)
    doc = pymupdf.open("pdf", pdf_bytes)
    return PDFFile(doc, path=path)


def merge(*inputs: str | list[str]) -> PDFFile:
    """Merge multiple PDF files into one.

    Args:
        inputs: Two or more PDF file paths, or a single list of paths.

    Returns:
        A PDFFile with all documents merged in order.
    """
    paths: list[str] = []
    for item in inputs:
        if isinstance(item, list):
            paths.extend(item)
        else:
            paths.append(item)

    if len(paths) < 2:
        raise ValueError("merge() requires at least 2 PDF paths.")

    pdf = read(paths[0])
    pdf.merge(*paths[1:])
    return pdf


def from_bytes(data: bytes) -> PDFFile:
    """Create a PDFFile from raw PDF bytes.

    Args:
        data: Raw PDF file content as bytes.

    Returns:
        A PDFFile instance.
    """
    import pymupdf

    from lazypdf.core import PDFFile

    doc = pymupdf.open("pdf", data)
    return PDFFile(doc)
